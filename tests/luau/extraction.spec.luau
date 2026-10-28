local Server = game:GetService("ServerScriptService").Server
local Shared = game:GetService("ReplicatedStorage").Shared
local OperationJournal = require(Server.Infrastructure.OperationJournal)
local ExtractionRules = require(Shared.Extraction.ExtractionRules)
local VaultRules = require(Shared.Extraction.VaultRules)
local ProfileSchema = require(Shared.Data.ProfileSchema)
local Receipts = require(Shared.Data.Receipts)

local function sword(id)
	return { instanceId = id, catalogId = "StoneSword", ownerId = 1, location = "Carried", qualityRoll = 0 }
end

test("only living, non-downed, at-risk players inside the zone at the deadline extract", function()
	local base = { alive = true, downed = false, atRisk = true, inZone = true }
	expect(ExtractionRules.Qualifies(base), "qualifies")
	for _, key in { "alive", "atRisk", "inZone" } do
		local candidate = table.clone(base)
		candidate[key] = false
		expect(not ExtractionRules.Qualifies(candidate), "not " .. key)
	end
	local downed = table.clone(base)
	downed.downed = true
	expect(not ExtractionRules.Qualifies(downed), "downed players do not extract")
	expect(ExtractionRules.InZone(Vector3.new(5, 0, 5), Vector3.new(0, 0, 0), 8), "inside the radius")
	expect(not ExtractionRules.InZone(Vector3.new(9, 0, 0), Vector3.new(0, 0, 0), 8), "outside")
end)

test("fixed exits take 120 s, runes 30 s, and only the fixed Center portal doubles", function()
	expectEq(ExtractionRules.FIXED_SECONDS, 120, "120 s")
	expectEq(ExtractionRules.PORTABLE_SECONDS, 30, "30 s")
	expectEq(ExtractionRules.Multiplier("Center"), 2, "center doubles")
	expectEq(ExtractionRules.Multiplier("Fixed"), 1, "ordinary portal")
	expectEq(ExtractionRules.Multiplier("Portable"), 1, "runes never double, even at the center")
end)

test("ordinary materials auto-bank and unique gear goes to the lobby backpack", function()
	local profile = ProfileSchema.Default(0)
	local receipt = ExtractionRules.Settle(profile, {
		{ catalogId = "Stone", quantity = 30 },
		sword("s1"),
		{ catalogId = "FlintArrow", quantity = 20 },
	}, "Fixed", "r1", 5)
	expectEq(profile.vault.materials.Stone, 30, "stone banked")
	expectEq(#profile.lobbyBackpack.slots, 2, "sword and arrows in the lobby backpack")
	expectEq(profile.lobbyBackpack.slots[1].location, "LobbyBackpack", "location updated")
	expectEq(receipt.vaulted.Stone, 30, "receipt lists the stone")
	expectEq(profile.receipts.extraction.r1, receipt, "receipt saved")
	expectEq(profile.metrics.extractions, 1, "counted")
end)

test("the Center doubles materials but never clones a sword", function()
	local profile = ProfileSchema.Default(0)
	ExtractionRules.Settle(profile, { { catalogId = "Stone", quantity = 30 }, sword("s1") }, "Center", "r1", 5)
	expectEq(profile.vault.materials.Stone, 60, "30 stone becomes 60")
	expectEq(#profile.lobbyBackpack.slots, 1, "one sword")
end)

test("anything over a vault stack's 1,000 is deleted and listed", function()
	local profile = ProfileSchema.Default(0)
	local receipt = ExtractionRules.Settle(profile, { { catalogId = "Wood", quantity = 600 } }, "Center", "r1", 5)
	expectEq(profile.vault.materials.Wood, 1000, "1,000 stored")
	expectEq(receipt.deleted.Wood, 200, "200 deleted")
	expectEq(receipt.vaulted.Wood, 1000, "1,000 banked")
end)

test("items beyond 50 lobby backpack slots are deleted", function()
	local profile = ProfileSchema.Default(0)
	local items = {}
	for i = 1, 55 do
		table.insert(items, sword("s" .. i))
	end
	local receipt = ExtractionRules.Settle(profile, items, "Fixed", "r1", 5)
	expectEq(#profile.lobbyBackpack.slots, 50, "50 kept")
	expectEq(receipt.deleted.StoneSword, 5, "5 deleted")
end)

test("manual item deposits are refused, never deleted, when full", function()
	local profile = ProfileSchema.Default(0)
	profile.lobbyBackpack.slots = { sword("a"), { catalogId = "Stone", quantity = 300 } }
	local ok, reason = VaultRules.Deposit(profile, 2)
	expect(not ok and reason == "MaterialsBankAutomatically", "a material never takes an item slot")
	expectEq(#profile.vault.items, 0, "no material stack in the item slots")
	expect(VaultRules.Deposit(profile, 1), "sword deposited")
	expectEq(profile.vault.items[1].location, "Vault", "now vaulted")
	for i = 2, 25 do
		table.insert(profile.vault.items, sword("v" .. i))
	end
	profile.lobbyBackpack.slots = { sword("b") }
	ok, reason = VaultRules.Deposit(profile, 1)
	expect(not ok and reason == "VaultFull", "25 slots is full")
	expectEq(VaultRules.ItemCapacity(profile), 25, "25 starting slots")
end)

test("withdrawals move vault items into the lobby backpack; materials stay vaulted", function()
	local profile = ProfileSchema.Default(0)
	profile.vault.items = { sword("a") }
	profile.vault.materials.IronBar = 40
	expect(VaultRules.WithdrawItem(profile, 1), "withdraw sword")
	expectEq(#profile.vault.items, 0, "vault emptied")
	expectEq(VaultRules.WithdrawMaterial, nil, "materials have no way back out of the vault")
	expectEq(profile.vault.materials.IronBar, 40, "iron bars untouched")
end)

test("backpack materials bank into the vault at once; overflow is deleted", function()
	local profile = ProfileSchema.Default(0)
	profile.vault.materials.Stone = 800
	profile.lobbyBackpack.slots = {
		{ catalogId = "Stone", quantity = 300 },
		sword("a"),
		{ catalogId = "AncientEmber", quantity = 2 },
		{ catalogId = "FlintArrow", quantity = 20 },
		{ catalogId = "Stone", quantity = 50 },
	}
	local deleted = VaultRules.BankMaterials(profile, 77)
	expectEq(profile.vault.materials.Stone, 1000, "Stone fills its vault capacity")
	expectEq(deleted.Stone, 150, "800 + 350 leaves 150 to delete")
	expectEq(profile.vault.materials.AncientEmber, 2, "special materials bank too")
	expectEq(#profile.lobbyBackpack.slots, 2, "only the sword and arrows stay")
	for _, item in profile.lobbyBackpack.slots do
		expect(
			item.catalogId == "StoneSword" or item.catalogId == "FlintArrow",
			"non-material kept: " .. item.catalogId
		)
	end
	expectEq(profile.vault.lastOverflow.at, 77, "the loss is recorded")
	expectEq(profile.vault.lastOverflow.deleted.Stone, 150, "with its amount")

	local again = VaultRules.BankMaterials(profile, 78)
	expectEq(next(again), nil, "nothing left to bank")
	expectEq(profile.vault.lastOverflow.at, 77, "a sweep with no loss keeps the last notice")
end)

test("replaying a settlement receipt never credits twice", function()
	local profile = ProfileSchema.Default(0)
	local items = { { catalogId = "Stone", quantity = 30 }, sword("s1") }
	local function settle(working)
		return ExtractionRules.Settle(working, items, "Center", "extract:e1", 5)
	end
	local _, applied = OperationJournal.Run(profile, "extract:e1", "Extraction", 5, settle)
	expect(applied, "first settlement applies")
	_, applied = OperationJournal.Run(profile, "extract:e1", "Extraction", 6, settle)
	expect(not applied, "the replay is a no-op")
	expectEq(profile.vault.materials.Stone, 60, "stone credited once")
	expectEq(#profile.lobbyBackpack.slots, 1, "one sword")
	expectEq(profile.metrics.extractions, 1, "one extraction counted")
end)

test("a settlement that fails part-way deletes and grants nothing", function()
	local profile = ProfileSchema.Default(0)
	profile.vault.materials.Stone = 10
	local ok = pcall(OperationJournal.Run, profile, "extract:e2", "Extraction", 5, function(working)
		ExtractionRules.Settle(working, { { catalogId = "Stone", quantity = 30 } }, "Fixed", "extract:e2", 5)
		error("DataStore unavailable")
	end)
	expect(not ok, "the failure surfaces")
	expectEq(profile.vault.materials.Stone, 10, "vault unchanged")
	expectEq(profile.receipts.extraction["extract:e2"], nil, "no receipt")
	expectEq(OperationJournal.Get(profile, "extract:e2"), nil, "can be retried later")
end)

test("a late arrival inside the zone at zero qualifies; an early leaver does not", function()
	local center = Vector3.new(100, 10, 100)
	expect(ExtractionRules.InZone(Vector3.new(104, 12, 98), center, 12), "arrived late, inside at zero")
	expect(not ExtractionRules.InZone(Vector3.new(140, 10, 100), center, 12), "left before zero")
	expect(not ExtractionRules.InZone(Vector3.new(100, 60, 100), center, 12), "far above the zone")
end)

test("only the newest receipts are kept", function()
	local profile = ProfileSchema.Default(0)
	for i = 1, Receipts.RETENTION + 5 do
		ExtractionRules.Settle(profile, {}, "Fixed", "r" .. i, i)
	end
	local count = 0
	for _ in profile.receipts.extraction do
		count += 1
	end
	expectEq(count, Receipts.RETENTION, "trimmed")
	expectEq(profile.receipts.extraction.r1, nil, "oldest dropped")
	expect(profile.receipts.extraction["r" .. (Receipts.RETENTION + 5)] ~= nil, "newest kept")
end)
