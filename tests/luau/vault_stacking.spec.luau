-- Identical items stack (Q128): a vault deposit, a move to the end of the lobby
-- backpack and a return to the lobby top up the stack of their type instead of
-- adding a second one, and profiles saved with split stacks merge on load.
local Shared = game:GetService("ReplicatedStorage").Shared
local Server = game:GetService("ServerScriptService").Server
local InventoryRules = require(Shared.Inventory.InventoryRules)
local ItemCatalog = require(Shared.Items.ItemCatalog)
local VaultRules = require(Server.Rules.Extraction.VaultRules)
local LobbyLoadoutRules = require(Server.Rules.Inventory.LobbyLoadoutRules)
local ProfileSchema = require(Server.Rules.Data.ProfileSchema)

local MEDICINE = "BasicMedicine"

local function sword(id)
	return { instanceId = id, catalogId = "StoneSword", ownerId = 1, location = "LobbyBackpack", qualityRoll = 0 }
end

local function medicine(quantity)
	return { catalogId = MEDICINE, quantity = quantity }
end

local function quantities(list)
	local out = {}
	for _, item in list do
		table.insert(out, (item.instanceId or item.catalogId) .. "=" .. tostring(item.quantity or 1))
	end
	return table.concat(out, ",")
end

test("the stack cap these specs lean on", function()
	expectEq(ItemCatalog.StackCap(MEDICINE), 50, "medicine stacks to 50")
end)

test("depositing a consumable the vault already holds tops up that stack", function()
	local profile = ProfileSchema.Default(0)
	profile.lobbyBackpack.slots = { medicine(2) }
	expect(VaultRules.Deposit(profile, 1), "first deposit")
	profile.lobbyBackpack.slots = { medicine(2) }
	expect(VaultRules.Deposit(profile, 1), "second deposit")
	expectEq(quantities(profile.vault.items), "BasicMedicine=4", "one stack of 4")
	expectEq(#profile.lobbyBackpack.slots, 0, "the backpack slot is gone")

	-- Part of a stack joins it too, and the rest stays in the backpack.
	profile.lobbyBackpack.slots = { medicine(6) }
	expect(VaultRules.Deposit(profile, 1, 0, nil, 4), "deposit 4 of 6")
	expectEq(quantities(profile.vault.items), "BasicMedicine=8", "one stack of 8")
	expectEq(quantities(profile.lobbyBackpack.slots), "BasicMedicine=2", "2 stay")
end)

test("a deposit past the cap fills the stack and starts one more", function()
	local profile = ProfileSchema.Default(0)
	profile.vault.items = { medicine(48) }
	profile.lobbyBackpack.slots = { medicine(5) }
	expect(VaultRules.Deposit(profile, 1), "deposit 5")
	expectEq(quantities(profile.vault.items), "BasicMedicine=50,BasicMedicine=3", "50 and 3")
end)

test("a full vault still takes a stack its own stack has room for, and nothing else", function()
	local profile = ProfileSchema.Default(0)
	profile.vault.items = { medicine(10) }
	for index = 2, VaultRules.ItemCapacity(profile) do
		table.insert(profile.vault.items, sword("v" .. index))
	end
	profile.lobbyBackpack.slots = { medicine(5), medicine(45), sword("b") }
	expect(VaultRules.Deposit(profile, 1), "5 merge into the 10")
	expectEq(profile.vault.items[1].quantity, 15, "15 vaulted")
	local ok, reason = VaultRules.Deposit(profile, 1)
	expect(not ok and reason == "VaultFull", "45 more would need a slot")
	expectEq(profile.vault.items[1].quantity, 15, "nothing moved")
	expectEq(quantities(profile.lobbyBackpack.slots), "BasicMedicine=45,b=1", "the backpack is unchanged")
	ok, reason = VaultRules.Deposit(profile, 2)
	expect(not ok and reason == "VaultFull", "a unique item needs a slot")
end)

test("moving a hotbar stack to the end of the backpack joins the stack there", function()
	local profile = ProfileSchema.Default(0)
	profile.lobbyBackpack.hotbar = { ["1"] = medicine(3) }
	profile.lobbyBackpack.armor = {}
	profile.lobbyBackpack.slots = { medicine(2) }
	for index = 2, LobbyLoadoutRules.BACKPACK_SLOTS do
		table.insert(profile.lobbyBackpack.slots, sword("s" .. index))
	end
	expect(LobbyLoadoutRules.Move(profile, "hotbar", 1, "backpack", nil), "merges into a full backpack")
	expectEq(profile.lobbyBackpack.slots[1].quantity, 5, "one stack of 5")
	expectEq(#profile.lobbyBackpack.slots, LobbyLoadoutRules.BACKPACK_SLOTS, "no new slot")
	expectEq(LobbyLoadoutRules.HotbarAt(profile, 1), nil, "the hotbar slot is empty")

	profile.lobbyBackpack.hotbar = { ["1"] = sword("h") }
	local ok, reason = LobbyLoadoutRules.Move(profile, "hotbar", 1, "backpack", nil)
	expect(not ok and reason == "BackpackFull", "a unique item needs a free slot")
end)

test("an item coming back to the lobby joins the stack of its type", function()
	local profile = ProfileSchema.Default(0)
	profile.lobbyBackpack.hotbar = { ["1"] = sword("h") }
	profile.lobbyBackpack.armor = {}
	profile.lobbyBackpack.slots = { medicine(2) }
	-- Its hotbar slot is taken, so it goes to the backpack.
	local returned = medicine(3)
	returned.loadoutSlot = "hotbar:1"
	LobbyLoadoutRules.Return(profile, returned)
	expectEq(quantities(profile.lobbyBackpack.slots), "BasicMedicine=5", "one stack of 5")
end)

test("Land moves carried units with the units they belong to", function()
	local slots = { { catalogId = "Stone", quantity = 10, carried = 4 } }
	InventoryRules.Land(slots, { catalogId = "Stone", quantity = 6, carried = 6 })
	expectEq(#slots, 1, "one stack")
	expectEq(slots[1].quantity, 16, "16 stone")
	expectEq(InventoryRules.Carried(slots[1]), 10, "4 + 6 carried")
end)

test("profiles saved with split stacks merge on load, unique items untouched", function()
	local data = ProfileSchema.Default(0)
	data.vault.items = { medicine(2), sword("a"), medicine(2), { catalogId = "Sunberry", quantity = 5 }, medicine(2) }
	data.lobbyBackpack.slots = {
		{ catalogId = "Sunberry", quantity = 5 },
		sword("b"),
		{ catalogId = "Sunberry", quantity = 5 },
	}
	local profile = assert(ProfileSchema.Migrate(data, 0))
	expectEq(quantities(profile.vault.items), "BasicMedicine=6,a=1,Sunberry=5", "vault merged in order")
	expectEq(quantities(profile.lobbyBackpack.slots), "Sunberry=10,b=1", "backpack merged")
	local again = assert(ProfileSchema.Migrate(profile, 0))
	expectEq(quantities(again.vault.items), "BasicMedicine=6,a=1,Sunberry=5", "loading again changes nothing")
end)
