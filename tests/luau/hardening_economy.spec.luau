-- Economy hardening: codes, purchases, Center doubling, rebirth credit, trade
-- reconciliation and limits, PvP credit, tutorial skips and shop pricing.
local Server = game:GetService("ServerScriptService").Server
local Shared = game:GetService("ReplicatedStorage").Shared
local EconomyRules = require(Shared.Economy.EconomyRules)
local ExtractionRules = require(Shared.Extraction.ExtractionRules)
local OfferCatalog = require(Shared.Economy.OfferCatalog)
local OperationJournal = require(Server.Infrastructure.OperationJournal)
local ProfileSchema = require(Shared.Data.ProfileSchema)
local ProgressionRules = require(Shared.Progression.ProgressionRules)
local ShopCatalog = require(Shared.Economy.ShopCatalog)
local TradeRules = require(Shared.Economy.TradeRules)
local TutorialSteps = require(Shared.Tutorial.TutorialSteps)

local DAY = 86400 * 20000

local function sword(id, overrides)
	local item = { instanceId = id, catalogId = "IronSword", ownerId = 1, location = "LobbyBackpack", qualityRoll = 0 }
	for key, value in overrides or {} do
		item[key] = value
	end
	return item
end

local function strict(apply)
	return function(working)
		local ok, reason = apply(working)
		if not ok then
			error(reason, 0)
		end
		return reason
	end
end

local function flushJournal(profile)
	for index = 1, OperationJournal.RETENTION + 5 do
		OperationJournal.Run(profile, "filler:" .. index, "Filler", index, function() end)
	end
end

local function fang(id, overrides)
	local item = { instanceId = id, catalogId = "GuardianFang", ownerId = 1, guardianEncounterId = "enc-" .. id }
	for key, value in overrides or {} do
		item[key] = value
	end
	return item
end

test("a code redeems once ever, even after the journal forgets it", function()
	local profile = ProfileSchema.Default(0)
	local redeem = strict(function(working)
		return EconomyRules.RedeemCode(working, "FLINTBORN-LAUNCH", { gems = 25 }, 1)
	end)
	OperationJournal.Run(profile, "code:FLINTBORN-LAUNCH", "CodeRedeem", 1, redeem)
	flushJournal(profile)
	expectEq(OperationJournal.Get(profile, "code:FLINTBORN-LAUNCH"), nil, "journal trimmed")
	local ok, reason = pcall(OperationJournal.Run, profile, "code:FLINTBORN-LAUNCH", "CodeRedeem", 9, redeem)
	expect(not ok and reason == "AlreadyRedeemed", "the permanent record refuses it")
	expectEq(profile.currency.gems, 25, "25 Gems once")
end)

test("a respec code with nothing to respec fails and grants no Gems", function()
	local profile = ProfileSchema.Default(0)
	local ok, reason = EconomyRules.RedeemCode(profile, "FLINTBORN-RESPEC", { respec = true }, 1)
	expect(not ok and reason == "NothingToRespec", "nothing to refund")
	expectEq(profile.currency.gems, 0, "no Gem fallback for codes")
	expectEq(profile.currency.redeemedCodes["FLINTBORN-RESPEC"], nil, "still usable later")
	profile.rebirth.ownedPerks = { Scholar = 1 }
	expect(EconomyRules.RedeemCode(profile, "FLINTBORN-RESPEC", { respec = true }, 2), "refunds perks")
	expectEq(profile.rebirth.tokens, 1, "token back")
	expect(profile.currency.redeemedCodes["FLINTBORN-RESPEC"], "now used")
end)

test("a purchase retried after the journal trims never grants twice", function()
	local profile = ProfileSchema.Default(0)
	local function fulfil(working)
		return EconomyRules.FulfilPurchase(working, "P1", OfferCatalog.ById.GemPack, 0, 1)
	end
	OperationJournal.Run(profile, "purchase:P1", "Purchase", 1, fulfil)
	flushJournal(profile)
	local _, applied = OperationJournal.Run(profile, "purchase:P1", "Purchase", 9, fulfil)
	expect(applied, "the journal no longer remembers it")
	expectEq(profile.currency.gems, 100, "the entitlement record still grants once")
	expectEq(profile.currency.purchaseEntitlements.P1.offer, "GemPack", "entitlement kept")
end)

test("every extracted material banks into the vault, special ones included", function()
	local profile = ProfileSchema.Default(0)
	ProgressionRules.StartRun(profile, "run1")
	local receipt = ExtractionRules.Settle(profile, {
		{ catalogId = "AncientEmber", quantity = 1 },
		{ catalogId = "Stone", quantity = 30 },
	}, "Center", "r1", 1)
	expectEq(profile.vault.materials.AncientEmber, 2, "Ancient Ember is vaulted and doubled")
	expectEq(profile.vault.materials.Stone, 60, "gathered Stone doubled")
	expectEq(#profile.lobbyBackpack.slots, 0, "no material lands in the lobby backpack")
	expectEq(receipt.vaulted.AncientEmber, 2, "the receipt lists it as vaulted")
end)

test("the vault's material capacity, not the backpack, decides what is deleted", function()
	local profile = ProfileSchema.Default(0)
	for i = 1, 50 do
		table.insert(profile.lobbyBackpack.slots, { instanceId = "s" .. i, catalogId = "StoneSpear" })
	end
	profile.vault.materials.Stone = 990
	local receipt = ExtractionRules.Settle(profile, {
		{ catalogId = "Stone", quantity = 30 },
		{ catalogId = "AncientEmber", quantity = 3 },
		{ instanceId = "late", catalogId = "StoneSpear" },
	}, "Center", "r1", 1)
	expectEq(profile.vault.materials.Stone, 1000, "Stone fills the vault stack")
	expectEq(receipt.vaulted.Stone, 10, "10 of 60 fit")
	expectEq(receipt.deleted.Stone, 50, "the rest is deleted and listed")
	expectEq(profile.vault.materials.AncientEmber, 6, "a full backpack never deletes materials")
	expectEq(receipt.deleted.StoneSpear, 1, "gear still overflows the 50-slot backpack")
end)

test("a Guardian Legendary counts toward rebirth on its first extraction only", function()
	local profile = ProfileSchema.Default(0)
	ExtractionRules.Settle(profile, { fang("g1") }, "Fixed", "r1", 1)
	expectEq(profile.rebirth.legendariesSinceRebirth, 1, "first extraction counts")
	local stored = profile.lobbyBackpack.slots[1]
	expect(stored.rebirthCredited, "the stored copy is marked")
	-- Redeploy and extract the same Fang again, or receive it in a trade.
	ExtractionRules.Settle(profile, { ProfileSchema.DeepCopy(stored) }, "Fixed", "r2", 2)
	local other = ProfileSchema.Default(0)
	ExtractionRules.Settle(other, { ProfileSchema.DeepCopy(stored) }, "Fixed", "r3", 3)
	ExtractionRules.Settle(other, { { instanceId = "x", catalogId = "GuardianFang", ownerId = 2 } }, "Fixed", "r4", 4)
	expectEq(profile.rebirth.legendariesSinceRebirth, 1, "re-extraction never counts again")
	expectEq(other.rebirth.legendariesSinceRebirth, 0, "traded or unattributed Fangs never count")
end)

test("Permanent items still land past 50 backpack slots on extraction", function()
	local profile = ProfileSchema.Default(0)
	for index = 1, 50 do
		table.insert(profile.lobbyBackpack.slots, sword("f" .. index))
	end
	ProgressionRules.StartRun(profile, "run1")
	local receipt =
		ExtractionRules.Settle(profile, { sword("p1", { permanent = true }), sword("n1") }, "Center", "r1", 1)
	expectEq(#profile.lobbyBackpack.slots, 51, "Permanent kept, ordinary deleted")
	expectEq(profile.lobbyBackpack.slots[51].instanceId, "p1", "the Permanent item")
	expectEq(receipt.deleted.IronSword, 1, "the ordinary sword is listed as deleted")
end)

local function settled(server)
	local a, b = ProfileSchema.Default(0), ProfileSchema.Default(0)
	a.progression.level, b.progression.level = 12, 12
	a.lobbyBackpack.slots = { sword("s1") }
	b.lobbyBackpack.slots = { { catalogId = "AncientEmber", quantity = 3 } }
	local bStored = ProfileSchema.DeepCopy(b)
	TradeRules.Settle("t1", { profile = a, userId = 1, offer = { items = { 1 } } }, {
		profile = b,
		userId = 2,
		offer = { items = { 1 } },
	}, DAY)
	a.trades.pending.t1.server = server
	return a, b, bStored
end

test("reconcile waits while the counterpart's settling server may still save", function()
	local a, _, bStored = settled("S")
	bStored.sessionLease = { jobId = "S", expiresAt = DAY + 300 }
	expectEq(TradeRules.Reconcile(a, "t1", bStored, DAY + 10), "Deferred", "B is live on S")
	expect(a.trades.pending.t1 ~= nil, "nothing changed yet")
	expectEq(TradeRules.Reconcile(a, "t1", bStored, DAY + 400), "RolledBack", "lease expired: never saved")
	expectEq(a.lobbyBackpack.slots[1].instanceId, "s1", "A has the sword back")
end)

test("a counterpart reloaded on another server never saved the trade: roll back", function()
	local a, _, bStored = settled("S")
	bStored.sessionLease = { jobId = "X", expiresAt = DAY + 300 }
	expectEq(TradeRules.Reconcile(a, "t1", bStored, DAY + 10), "RolledBack", "X loaded B without it")
end)

test("reconcile settles only on a pending or Settled counterpart record", function()
	local a, b = settled("S")
	b.sessionLease = { jobId = "S", expiresAt = DAY + 300 }
	expectEq(TradeRules.Reconcile(a, "t1", b, DAY + 1), "Settled", "B saved it pending")
	local a2, b2 = settled("S")
	TradeRules.Finalize(b2, "t1", DAY)
	expectEq(TradeRules.Reconcile(a2, "t1", b2, DAY + 1), "Settled", "B finalised it")
	local a3, _, b3 = settled("S")
	b3.sessionLease = { jobId = "S", expiresAt = DAY + 300 }
	b3.trades.history.t1 = { outcome = "RolledBack", at = DAY }
	expectEq(TradeRules.Reconcile(a3, "t1", b3, DAY + 1), "RolledBack", "B rolled back: so does A")
end)

test("a rollback claws received items back from the vault too", function()
	local a, _, bStored = settled("S")
	-- A deposited what it received before the rollback.
	local ember = table.remove(a.lobbyBackpack.slots, 1)
	a.vault.materials.AncientEmber = ember.quantity + 4
	expectEq(TradeRules.Reconcile(a, "t1", bStored, DAY + 1), "RolledBack", "B never saved")
	expectEq(a.vault.materials.AncientEmber, 4, "only the received 3 are taken back")
	local b = ProfileSchema.Default(0)
	b.progression.level = 12
	local giver = ProfileSchema.Default(0)
	giver.lobbyBackpack.slots = { sword("s9") }
	TradeRules.Settle("t9", { profile = b, userId = 2, offer = { items = {} } }, {
		profile = giver,
		userId = 1,
		offer = { items = { 1 } },
	}, DAY)
	table.insert(b.vault.items, table.remove(b.lobbyBackpack.slots, 1))
	TradeRules.Reconcile(b, "t9", ProfileSchema.Default(0), DAY + 1)
	expectEq(#b.vault.items, 0, "the vaulted sword is clawed back")
end)

test("a pending trade blocks new offers and history keeps 500 trades", function()
	local a = settled("S")
	local ok, reason = TradeRules.ValidateOffer(a, { items = {} }, DAY)
	expect(not ok and reason == "TradePending", "no chained trades on an unconfirmed one")
	expect(TradeRules.HISTORY >= 500, "long history for reconciliation")
end)

test("receiving Gems needs level 10 and is capped per UTC day", function()
	local receiver = ProfileSchema.Default(0)
	local ok, reason = TradeRules.ValidateReceive(receiver, 100, DAY)
	expect(not ok and reason == "PartnerGemLevel", "level 10 to receive")
	receiver.progression.level = 10
	expect(TradeRules.ValidateReceive(receiver, 2000, DAY), "up to the cap after the fee")
	local sender = ProfileSchema.Default(0)
	sender.progression.level, sender.currency.gems = 12, 2000
	TradeRules.Settle("g1", { profile = sender, userId = 1, offer = { items = {}, gems = 2000 } }, {
		profile = receiver,
		userId = 3,
		offer = { items = {} },
	}, DAY)
	expectEq(receiver.currency.gemsReceivedToday, 1900, "received after the fee")
	ok, reason = TradeRules.ValidateReceive(receiver, 200, DAY + 60)
	expect(not ok and reason == "PartnerGemDailyLimit", "a second sender cannot exceed the cap")
	expect(TradeRules.ValidateReceive(receiver, 200, DAY + 86400), "the next UTC day resets it")
end)

test("PvP credit persists per victim and stays bounded", function()
	local profile = ProfileSchema.Default(0)
	expect(ProgressionRules.CreditPvp(profile, 42, 1000, 1800), "first kill")
	expect(not ProgressionRules.CreditPvp(profile, 42, 2000, 1800), "same victim inside the window")
	local reloaded = ProfileSchema.DeepCopy(profile)
	expect(not ProgressionRules.CreditPvp(reloaded, 42, 2500, 1800), "a new server still remembers")
	expect(ProgressionRules.CreditPvp(reloaded, 42, 2801, 1800), "after the window")
	for victim = 1, 80 do
		ProgressionRules.CreditPvp(reloaded, 1000 + victim, 3000 + victim, 1800)
	end
	local count = 0
	for _ in reloaded.progression.pvpCredits do
		count += 1
	end
	expect(count <= ProgressionRules.PVP_CREDIT_MEMORY, "bounded map")
end)

test("a tutorial skip blocks rewards even after a replay", function()
	local state = ProfileSchema.Default(0).tutorial
	local extract = TutorialSteps.Steps[TutorialSteps.Index.Extract]
	TutorialSteps.Advance(state, "RunStarted", 1)
	expect(TutorialSteps.Skip(state), "skipped")
	TutorialSteps.Replay(state)
	expect(not state.skipped, "the replay runs")
	expect(not TutorialSteps.ClaimReward(state, extract), "but never pays a skipper")
end)

test("no shop entry is dominated by another for the same item", function()
	for _, entry in ShopCatalog.Stock do
		for _, rival in ShopCatalog.Stock do
			if rival ~= entry and entry.catalogId and rival.catalogId == entry.catalogId then
				local dominated = rival.quantity >= entry.quantity and rival.price <= entry.price
				expect(not dominated, entry.id .. " is dominated by " .. rival.id)
			end
		end
	end
end)
