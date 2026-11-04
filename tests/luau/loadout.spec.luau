-- The lobby loadout (backpack, hotbar, worn armour) and how it carries into a run:
-- LobbyLoadoutRules, TransitRules with placed items, InventoryRules.FromLoadout and
-- taking worn armour off into a chosen run slot (drag and drop).

local Shared = game:GetService("ReplicatedStorage").Shared
local Server = game:GetService("ServerScriptService").Server
local InventoryRules = require(Server.Rules.Inventory.InventoryRules)
local LobbyLoadoutRules = require(Server.Rules.Inventory.LobbyLoadoutRules)
local ProfileSchema = require(Server.Rules.Data.ProfileSchema)
local TransitRules = require(Server.Rules.Admission.TransitRules)

local function unique(catalogId: string, id: string)
	return { catalogId = catalogId, instanceId = id, location = "LobbyBackpack" }
end

test("worn armour comes off into a chosen run slot, or swaps with a piece for that slot", function()
	local inventory = InventoryRules.New()
	inventory.armor.Chest = unique("HideChest", "c1")
	inventory.hotbar[1] = unique("StoneAxe", "a1")
	inventory.hotbar[2] = unique("IronChest", "c2")
	expect(not InventoryRules.UnequipArmorTo(inventory, "Chest", "hotbar", 1), "not onto an axe")
	expect(not InventoryRules.UnequipArmorTo(inventory, "Chest", "backpack", 99), "not off the backpack")
	expect(InventoryRules.UnequipArmorTo(inventory, "Chest", "hotbar", 2), "swaps with another chest piece")
	expectEq(inventory.armor.Chest.instanceId, "c2", "the iron chest is worn")
	expectEq(inventory.hotbar[2].instanceId, "c1", "the hide chest is on the hotbar")
	expect(InventoryRules.UnequipArmorTo(inventory, "Chest", "backpack", 5), "onto an empty slot")
	expectEq(inventory.armor.Chest, nil, "nothing worn")
	expectEq(inventory.backpack[5].instanceId, "c2", "in backpack slot 5")
	expect(not InventoryRules.UnequipArmorTo(inventory, "Chest", "backpack", 6), "nothing left to take off")
end)

test("a deployed loadout starts the run with the same hotbar and worn armour", function()
	local inventory, leftovers = InventoryRules.FromLoadout({
		{ catalogId = "Wood", quantity = 40 },
		unique("StonePickaxe", "p1"),
		{ catalogId = "StoneAxe", instanceId = "a1", loadoutSlot = "hotbar:3" },
		{ catalogId = "HideChest", instanceId = "c1", loadoutSlot = "armor:Chest" },
		-- A bad place (head armour tagged for the chest) falls back to the backpack.
		{ catalogId = "HideHead", instanceId = "h1", loadoutSlot = "armor:Chest" },
		{ catalogId = "StoneSpear", instanceId = "s1", loadoutSlot = "hotbar:3" },
	})
	expectEq(#leftovers, 0, "everything fits")
	expectEq(inventory.hotbar[3].instanceId, "a1", "the axe keeps hotbar slot 3")
	expectEq(inventory.hotbar[3].loadoutSlot, nil, "tags are removed")
	expectEq(inventory.armor.Chest.instanceId, "c1", "the chest piece is worn")
	expectEq(inventory.hotbar[1], nil, "backpack items do not jump onto the hotbar")
	local inBackpack = {}
	for _, entry in inventory.backpack do
		inBackpack[entry.instanceId or entry.catalogId] = true
	end
	expect(inBackpack.Wood and inBackpack.p1 and inBackpack.h1 and inBackpack.s1, "the rest is in the backpack")
	local place, key = InventoryRules.LoadoutPlace("hotbar:7")
	expect(place == nil and key == nil, "hotbar slots stop at six")
end)

test("an old profile's first arrangement puts its tools on the lobby hotbar", function()
	local profile = ProfileSchema.Default(0)
	profile.lobbyBackpack.slots = {
		unique("StoneAxe", "a1"),
		{ catalogId = "Wood", quantity = 40 },
		unique("StoneSpear", "s1"),
		unique("HideChest", "c1"),
	}
	expect(not LobbyLoadoutRules.Arranged(profile), "not arranged yet")
	LobbyLoadoutRules.Arrange(profile)
	expect(LobbyLoadoutRules.Arranged(profile), "arranged")
	expectEq(LobbyLoadoutRules.HotbarAt(profile, 1).instanceId, "a1", "the axe on slot 1")
	expectEq(LobbyLoadoutRules.HotbarAt(profile, 2).instanceId, "s1", "the spear on slot 2")
	expectEq(#profile.lobbyBackpack.slots, 2, "wood and the chest piece stay in the backpack")
	profile.lobbyBackpack.slots[1] = unique("StonePickaxe", "p1")
	LobbyLoadoutRules.Arrange(profile)
	expectEq(LobbyLoadoutRules.HotbarAt(profile, 3), nil, "it happens once only")
end)

test("moves between the lobby backpack, hotbar and worn armour", function()
	local profile = ProfileSchema.Default(0)
	profile.lobbyBackpack.slots = {
		unique("StoneAxe", "a1"),
		unique("HideChest", "c1"),
		{ catalogId = "Wood", quantity = 40 },
		unique("IronChest", "c2"),
	}
	local move = function(...)
		return LobbyLoadoutRules.Move(profile, ...)
	end
	expect(move("backpack", 1, "hotbar", 2), "the axe onto hotbar slot 2")
	expectEq(LobbyLoadoutRules.HotbarAt(profile, 2).instanceId, "a1", "on the hotbar")
	expectEq(#profile.lobbyBackpack.slots, 3, "out of the backpack: it takes no backpack slot")
	local ok, reason = move("backpack", 1, "armor", "Head")
	expect(not ok and reason == "WrongArmorSlot", "a chest piece is not worn on the head")
	expect(move("backpack", 1, "armor", "Chest"), "worn on the chest")
	expectEq(LobbyLoadoutRules.ArmorAt(profile, "Chest").instanceId, "c1", "worn")
	ok, reason = move("armor", "Chest", "backpack", 1)
	expect(not ok and reason == "SlotTaken", "the wood can't be worn in its place")
	expect(move("armor", "Chest", "backpack", 2), "swaps with the iron chest in the backpack")
	expectEq(LobbyLoadoutRules.ArmorAt(profile, "Chest").instanceId, "c2", "iron worn now")
	expectEq(profile.lobbyBackpack.slots[2].instanceId, "c1", "hide back in its backpack slot")
	expect(move("hotbar", 2, "hotbar", 5), "hotbar slots swap")
	expectEq(LobbyLoadoutRules.HotbarAt(profile, 5).instanceId, "a1", "moved to slot 5")
	expect(move("backpack", 1, "backpack", 2), "backpack slots swap")
	expectEq(profile.lobbyBackpack.slots[1].instanceId, "c1", "swapped")
	ok, reason = move("hotbar", 1, "backpack", nil)
	expect(not ok and reason == "Empty", "nothing in hotbar slot 1")
	ok, reason = move("hotbar", 9, "backpack", nil)
	expect(not ok and reason == "BadRequest", "no hotbar slot 9")
	for index = #profile.lobbyBackpack.slots + 1, LobbyLoadoutRules.BACKPACK_SLOTS do
		profile.lobbyBackpack.slots[index] = { catalogId = "Stone", quantity = index }
	end
	ok, reason = move("hotbar", 5, "backpack", nil)
	expect(not ok and reason == "BackpackFull", "a full backpack has no free slot for it")
	expect(move("hotbar", 5, "backpack", 3), "but it can still swap with a backpack item")
end)

test("Deploy carries the hotbar and worn armour; a rollback puts each back", function()
	local profile = ProfileSchema.Default(0)
	profile.lobbyBackpack.slots = { { catalogId = "Wood", quantity = 40 }, unique("StoneAxe", "a1") }
	LobbyLoadoutRules.Arrange(profile)
	profile.lobbyBackpack.armor.Chest = unique("HideChest", "c1")
	TransitRules.Reserve(profile, "res-1", 10)
	expectEq(#profile.transit.items, 3, "backpack, hotbar and armour all deploy")
	expectEq(LobbyLoadoutRules.HotbarAt(profile, 1), nil, "the hotbar is emptied")
	local tags = {}
	for _, item in profile.transit.items do
		if item.loadoutSlot then
			tags[item.loadoutSlot] = item.instanceId
		end
	end
	expect(tags["hotbar:1"] == "a1" and tags["armor:Chest"] == "c1", "each tagged with its place")
	expectEq(TransitRules.Rollback(profile), 3, "all returned")
	expectEq(LobbyLoadoutRules.HotbarAt(profile, 1).instanceId, "a1", "the axe back on slot 1")
	expectEq(LobbyLoadoutRules.ArmorAt(profile, "Chest").instanceId, "c1", "the chest worn again")
	expectEq(LobbyLoadoutRules.HotbarAt(profile, 1).loadoutSlot, nil, "untagged")
	expectEq(#profile.lobbyBackpack.slots, 1, "only the wood in the backpack")
end)
