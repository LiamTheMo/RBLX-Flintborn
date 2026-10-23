local Server = game:GetService("ServerScriptService").Server
local Shared = game:GetService("ReplicatedStorage").Shared
local OperationJournal = require(Server.Infrastructure.OperationJournal)
local ExtractionRules = require(Shared.Extraction.ExtractionRules)
local VaultRules = require(Shared.Extraction.VaultRules)
local ProfileSchema = require(Shared.Data.ProfileSchema)

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
		{ catalogId = "Arrow", quantity = 20 },
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

test("manual vault deposits are refused, never deleted, when full", function()
	local profile = ProfileSchema.Default(0)
	profile.lobbyBackpack.slots = { sword("a"), { catalogId = "Stone", quantity = 300 } }
	profile.vault.materials.Stone = 800
	local ok, reason = VaultRules.Deposit(profile, 2)
	expect(not ok and reason == "VaultStackFull", "800 + 300 would exceed 1,000")
	expectEq(profile.lobbyBackpack.slots[2].quantity, 300, "nothing lost")
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

test("withdrawals move vault items and materials into the lobby backpack", function()
	local profile = ProfileSchema.Default(0)
	profile.vault.items = { sword("a") }
	profile.vault.materials.Iron = 40
	expect(VaultRules.WithdrawItem(profile, 1), "withdraw sword")
	expectEq(#profile.vault.items, 0, "vault emptied")
	expect(VaultRules.WithdrawMaterial(profile, "Iron", 15), "withdraw iron")
	expectEq(profile.vault.materials.Iron, 25, "25 left")
	expect(not VaultRules.WithdrawMaterial(profile, "Iron", 99), "cannot overdraw")
	expect(not VaultRules.WithdrawMaterial(profile, "Iron", 1.5), "whole numbers only")
	expect(VaultRules.WithdrawMaterial(profile, "Iron", 25), "withdraw the rest")
	expectEq(profile.vault.materials.Iron, nil, "empty stack removed")
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
	for i = 1, ExtractionRules.RECEIPT_RETENTION + 5 do
		ExtractionRules.Settle(profile, {}, "Fixed", "r" .. i, i)
	end
	local count = 0
	for _ in profile.receipts.extraction do
		count += 1
	end
	expectEq(count, ExtractionRules.RECEIPT_RETENTION, "trimmed")
	expectEq(profile.receipts.extraction.r1, nil, "oldest dropped")
	expect(profile.receipts.extraction["r" .. (ExtractionRules.RECEIPT_RETENTION + 5)] ~= nil, "newest kept")
end)
