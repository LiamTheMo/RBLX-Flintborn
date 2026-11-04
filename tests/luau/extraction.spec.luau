local Server = game:GetService("ServerScriptService").Server
local Shared = game:GetService("ReplicatedStorage").Shared
local OperationJournal = require(Server.Infrastructure.OperationJournal)
local ExtractionRules = require(Server.Rules.Extraction.ExtractionRules)
local VaultRules = require(Server.Rules.Extraction.VaultRules)
local ProfileSchema = require(Server.Rules.Data.ProfileSchema)
local Receipts = require(Server.Rules.Data.Receipts)
local CrashRecoveryRules = require(Server.Rules.Recovery.CrashRecoveryRules)

local function sword(id)
	return { instanceId = id, catalogId = "StoneSword", ownerId = 1, location = "Carried", qualityRoll = 0 }
end

-- A material stack carrying `carried` of its units in from the lobby (GDD §53).
local function stack(catalogId, quantity, carried)
	return { catalogId = catalogId, quantity = quantity, carried = carried }
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
	-- A late arrival inside the zone at zero qualifies; an early leaver does not.
	local center = Vector3.new(100, 10, 100)
	expect(ExtractionRules.InZone(Vector3.new(104, 12, 98), center, 12), "arrived late, inside at zero")
	expect(not ExtractionRules.InZone(Vector3.new(140, 10, 100), center, 12), "left before zero")
	expect(not ExtractionRules.InZone(Vector3.new(100, 60, 100), center, 12), "far above the zone")
end)

test("materials auto-bank, unique gear goes to the lobby backpack, and only the fixed Center portal doubles", function()
	expectEq(ExtractionRules.FIXED_SECONDS, 120, "fixed exits take 120 s")
	expectEq(ExtractionRules.PORTABLE_SECONDS, 30, "runes take 30 s")
	expectEq(ExtractionRules.Multiplier("Center"), 2, "center doubles")
	expectEq(ExtractionRules.Multiplier("Fixed"), 1, "ordinary portal")
	expectEq(ExtractionRules.Multiplier("Portable"), 1, "runes never double, even at the center")
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

test("carried-in materials never double at the Center; only what was gathered does", function()
	local profile = ProfileSchema.Default(0)
	-- 100 Wood brought in merged with 60 gathered into one stack of 160.
	local receipt = ExtractionRules.Settle(profile, { stack("Wood", 160, 100), sword("s1") }, "Center", "r1", 5)
	expectEq(profile.vault.materials.Wood, 220, "100 + 60 × 2")
	expectEq(receipt.vaulted.Wood, 220, "the receipt lists 220")
	expectEq(receipt.carriedIn.Wood, 100, "and the 100 it did not double")
	-- Carried units count across stacks, whoever extracts them.
	local mixed = ProfileSchema.Default(0)
	ExtractionRules.Settle(
		mixed,
		{ stack("Stone", 25, 25), stack("Wood", 10), stack("Stone", 45, 25) },
		"Center",
		"r1",
		5
	)
	expectEq(mixed.vault.materials.Stone, 90, "50 once + 20 gathered × 2")
	expectEq(mixed.vault.materials.Wood, 20, "a material with no carried units doubles in full")
	-- Carrying 100 in and extracting 40 doubles nothing; a malformed tag never counts more than the stack.
	local odd = ProfileSchema.Default(0)
	ExtractionRules.Settle(
		odd,
		{ stack("Wood", 40, 40), stack("Stone", 10, -4), stack("Wood", 10, 99) },
		"Center",
		"r2",
		5
	)
	expectEq(odd.vault.materials.Wood, 50, "all-carried stacks settle once, carried capped at the quantity")
	expectEq(odd.vault.materials.Stone, 20, "a negative tag counts as none")
	-- Other extractions settle carried-in and gathered materials alike.
	for _, kind in { "Fixed", "Portable" } do
		local plain = ProfileSchema.Default(0)
		local plainReceipt = ExtractionRules.Settle(plain, { stack("Wood", 160, 100) }, kind, "r1", 5)
		expectEq(plain.vault.materials.Wood, 160, kind .. " settles 160")
		expectEq(plainReceipt.carriedIn, nil, kind .. " lists nothing as skipped")
	end
	expectEq(ExtractionRules.MaterialYield(160, 100, 1), 160, "×1 never changes a total")
end)

test("a Play loadout and a crash checkpoint keep each stack's carried units", function()
	local profile = ProfileSchema.Default(0)
	CrashRecoveryRules.BeginRun(profile, "run-1", "job-1", { stack("Wood", 100, 100), sword("s1") }, 0)
	expectEq(profile.progression.currentRun.loadout[1].carried, 100, "the loadout keeps the tag")
	expectEq(profile.progression.currentRun.carriedIn, nil, "nothing is recorded on the run itself")
	local reloaded = ProfileSchema.Migrate(ProfileSchema.DeepCopy(profile), 0)
	expectEq(reloaded.progression.currentRun.loadout[1].carried, 100, "and so does a reload")
	local checkpoint = CrashRecoveryRules.Checkpoint("run-1", "job-1", { stack("Wood", 130, 100) }, {}, 0)
	expectEq(checkpoint.items[1].carried, 100, "a checkpoint keeps the tag")
	-- Restored into the lobby, the stack is lobby material again: the next Play
	-- tags whatever it takes afresh.
	CrashRecoveryRules.Restore(reloaded, checkpoint, 10)
	local restored = reloaded.lobbyBackpack.slots[#reloaded.lobbyBackpack.slots]
	expectEq(restored.quantity, 130, "all 130 Wood restored")
	expectEq(restored.carried, nil, "without a run tag")
end)

test("settlement overflow is deleted and listed: 1,000 per vault stack, 50 lobby backpack slots", function()
	local profile = ProfileSchema.Default(0)
	local receipt = ExtractionRules.Settle(profile, { { catalogId = "Wood", quantity = 600 } }, "Center", "r1", 5)
	expectEq(profile.vault.materials.Wood, 1000, "1,000 stored")
	expectEq(receipt.deleted.Wood, 200, "200 deleted")
	expectEq(receipt.vaulted.Wood, 1000, "1,000 banked")
	local items = {}
	for i = 1, 55 do
		table.insert(items, sword("s" .. i))
	end
	receipt = ExtractionRules.Settle(profile, items, "Fixed", "r2", 5)
	expectEq(#profile.lobbyBackpack.slots, 50, "50 kept")
	expectEq(receipt.deleted.StoneSword, 5, "5 deleted")
end)

test("manual item deposits are refused, never deleted, when full", function()
	local profile = ProfileSchema.Default(0)
	profile.lobbyBackpack.slots = { sword("a"), { catalogId = "Stone", quantity = 300 } }
	expect(VaultRules.Deposit(profile, 2, 5), "a material stack deposits")
	expectEq(#profile.vault.items, 0, "no material stack in the item slots")
	expectEq(profile.vault.materials.Stone, 300, "it banks as a material")
	expect(VaultRules.Deposit(profile, 1), "sword deposited")
	expectEq(profile.vault.items[1].location, "Vault", "now vaulted")
	for i = 2, 25 do
		table.insert(profile.vault.items, sword("v" .. i))
	end
	profile.lobbyBackpack.slots = { sword("b") }
	local ok, reason = VaultRules.Deposit(profile, 1)
	expect(not ok and reason == "VaultFull", "25 slots is full")
	expectEq(VaultRules.ItemCapacity(profile), 25, "25 starting slots")
end)

test("vault items and material stacks withdraw into the lobby backpack (GDD §53)", function()
	local profile = ProfileSchema.Default(0)
	profile.vault.items = { sword("a") }
	profile.vault.materials.IronBar = 40
	expect(VaultRules.WithdrawItem(profile, 1), "withdraw sword")
	expectEq(#profile.vault.items, 0, "vault emptied")

	expect(VaultRules.WithdrawMaterial(profile, "IronBar", 15), "withdraw 15 bars")
	expectEq(profile.vault.materials.IronBar, 25, "25 stay vaulted")
	expect(VaultRules.WithdrawMaterial(profile, "IronBar", 10), "withdraw 10 more")
	local bars = 0
	for _, slot in profile.lobbyBackpack.slots do
		if slot.catalogId == "IronBar" then
			bars += slot.quantity
		end
	end
	expectEq(bars, 25, "one backpack stack holds both withdrawals")
	local ok, reason = VaultRules.WithdrawMaterial(profile, "IronBar", 16)
	expect(not ok and reason == "NotEnough", "never more than the vault holds")
	expectEq(profile.vault.materials.IronBar, 15, "a refused withdrawal changes nothing")
	expect(not VaultRules.WithdrawMaterial(profile, "IronBar", 0), "zero is refused")
	expect(not VaultRules.WithdrawMaterial(profile, "IronBar", 1.5), "fractions are refused")
	expect(VaultRules.WithdrawMaterial(profile, "IronBar", 15), "the rest of the stack")
	expectEq(profile.vault.materials.IronBar, nil, "an emptied stack leaves the vault")

	-- A full backpack (50 other slots) refuses a new material stack, all or nothing.
	local full = ProfileSchema.Default(0)
	for i = 1, 50 do
		table.insert(full.lobbyBackpack.slots, sword("f" .. i))
	end
	full.vault.materials.Wood = 10
	ok, reason = VaultRules.WithdrawMaterial(full, "Wood", 10)
	expect(not ok and reason == "BackpackFull", "no room")
	expectEq(full.vault.materials.Wood, 10, "nothing moved")
	expectEq(#full.lobbyBackpack.slots, 50, "backpack unchanged")
end)

test("backpack materials stay put until deposited; a confirmed deposit past capacity deletes the rest", function()
	local profile = ProfileSchema.Default(0)
	profile.vault.materials.Stone = 800
	profile.lobbyBackpack.slots = {
		{ catalogId = "Stone", quantity = 300 },
		sword("a"),
		{ catalogId = "AncientEmber", quantity = 2 },
	}
	expectEq(VaultRules.BankMaterials, nil, "nothing banks the backpack automatically any more")
	expectEq(#profile.lobbyBackpack.slots, 3, "materials wait in the backpack")
	expectEq(VaultRules.DepositLoss(profile, 1), 100, "100 of the 300 Stone would be lost")
	local ok, reason = VaultRules.Deposit(profile, 1, 76)
	expect(not ok and reason == VaultRules.WOULD_OVERFLOW, "refused until confirmed: " .. tostring(reason))
	expectEq(profile.vault.materials.Stone, 800, "a refused deposit changes nothing")
	expectEq(#profile.lobbyBackpack.slots, 3, "the Stone stays in the backpack")
	expectEq(profile.vault.lastOverflow, nil, "and nothing is deleted")
	local wrong = VaultRules.Deposit(profile, 1, 77, { catalogId = "Wood", loss = 100 })
	expect(not wrong, "a confirmation for another material is refused")
	local less = VaultRules.Deposit(profile, 1, 77, { catalogId = "Stone", loss = 50 })
	expect(not less, "a confirmation for a smaller loss than now is refused")
	expectEq(profile.vault.materials.Stone, 800, "neither changed anything")
	expect(
		VaultRules.Deposit(profile, 1, 77, { catalogId = "Stone", loss = 100 }),
		"Stone deposits once the loss is confirmed"
	)
	expectEq(profile.vault.materials.Stone, 1000, "Stone fills its vault capacity")
	expectEq(profile.vault.lastOverflow.at, 77, "the loss is recorded")
	expectEq(profile.vault.lastOverflow.deleted.Stone, 100, "800 + 300 leaves 100 deleted")
	expectEq(#profile.lobbyBackpack.slots, 2, "the stack left the backpack")
	expect(VaultRules.Deposit(profile, 2, 78), "special materials deposit too")
	expectEq(profile.vault.materials.AncientEmber, 2, "Ancient Ember banked")
	expectEq(profile.vault.lastOverflow.at, 77, "a deposit with no loss keeps the last notice")
end)

test("a deposit can store part of a backpack stack; the client's amount is checked", function()
	local profile = ProfileSchema.Default(0)
	profile.vault.materials.Stone = 990
	profile.lobbyBackpack.slots = {
		{ catalogId = "Stone", quantity = 300 },
		sword("a"),
		{ catalogId = "Redberry", quantity = 9 },
	}
	for _, bad in { 0, -1, 301, 2.5, 0 / 0, math.huge, "5", true } do
		local ok, reason = VaultRules.Deposit(profile, 1, 1, nil, bad)
		expect(not ok and reason == "BadQuantity", "refused amount " .. tostring(bad))
	end
	expectEq(profile.vault.materials.Stone, 990, "refused amounts change nothing")
	expectEq(VaultRules.DepositLoss(profile, 1, 10), 0, "10 more fit")
	expectEq(VaultRules.DepositLoss(profile, 1, 30), 20, "30 would lose 20")
	expect(VaultRules.Deposit(profile, 1, 1, nil, 10), "store 10 of the 300 Stone")
	expectEq(profile.vault.materials.Stone, 1000, "10 banked")
	expectEq(profile.lobbyBackpack.slots[1].quantity, 290, "290 stay in the backpack slot")
	local ok, reason = VaultRules.Deposit(profile, 1, 2, nil, 5)
	expect(not ok and reason == VaultRules.WOULD_OVERFLOW, "a full material still asks first")
	expect(not VaultRules.Deposit(profile, 2, 2, nil, 2), "a unique item stores only as one")
	expect(VaultRules.Deposit(profile, 3, 3, nil, 4), "store 4 of 9 berries")
	expectEq(profile.lobbyBackpack.slots[3].quantity, 5, "5 berries stay")
	local stored = profile.vault.items[#profile.vault.items]
	expectEq(stored.catalogId, "Redberry", "the part goes in as its own vault entry")
	expectEq(stored.quantity, 4, "with the amount stored")
	expect(VaultRules.Deposit(profile, 3, 4, nil, 5), "the rest stores too")
	expectEq(#profile.lobbyBackpack.slots, 2, "an emptied slot leaves the backpack")
	expect(VaultRules.Deposit(profile, 2, 5, nil, nil), "nil stores the whole slot")
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
