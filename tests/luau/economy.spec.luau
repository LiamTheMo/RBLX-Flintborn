local Server = game:GetService("ServerScriptService").Server
local Shared = game:GetService("ReplicatedStorage").Shared
local EconomyRules = require(Shared.Economy.EconomyRules)
local ExtractionRules = require(Shared.Extraction.ExtractionRules)
local OfferCatalog = require(Shared.Economy.OfferCatalog)
local OperationJournal = require(Server.Infrastructure.OperationJournal)
local ProfileSchema = require(Shared.Data.ProfileSchema)
local QuestCatalog = require(Shared.Economy.QuestCatalog)
local ShopCatalog = require(Shared.Economy.ShopCatalog)
local TradeRules = require(Shared.Economy.TradeRules)
local VaultRules = require(Shared.Extraction.VaultRules)

local DAY = 86400 * 20000

local function sword(id, overrides)
	local item = { instanceId = id, catalogId = "IronSword", ownerId = 1, location = "LobbyBackpack", qualityRoll = 0 }
	for key, value in overrides or {} do
		item[key] = value
	end
	return item
end

test("quest bands are 250 / 1,000 / 3,000 Coins", function()
	expectEq(QuestCatalog.BANDS.Easy, 250, "easy")
	expectEq(QuestCatalog.BANDS.Normal, 1000, "normal")
	expectEq(QuestCatalog.BANDS.Hard, 3000, "hard")
	for _, quest in QuestCatalog.Quests do
		expectEq(quest.coins, QuestCatalog.BANDS[quest.tier], quest.id)
		expect((quest.gems or 25) <= 50, quest.id .. " gems around 25")
	end
end)

test("extracting grants zero Coins and zero Gems, even at the Center", function()
	local profile = ProfileSchema.Default(0)
	ExtractionRules.Settle(profile, { { catalogId = "Iron", quantity = 50 }, sword("s1") }, "Center", "r1", 1)
	expectEq(profile.currency.coins, 0, "no Coins")
	expectEq(profile.currency.gems, 0, "no Gems")
end)

test("each vault upgrade adds exactly 25 slots at the same Gem price", function()
	local profile = ProfileSchema.Default(0)
	profile.currency.gems = 5000
	local prices = {}
	for tier = 0, 3 do
		table.insert(prices, EconomyRules.VaultUpgradePrice(tier))
		local before = VaultRules.ItemCapacity(profile)
		expect(EconomyRules.BuyVaultTier(profile), "upgrade " .. tier)
		expectEq(VaultRules.ItemCapacity(profile) - before, 25, "+25")
	end
	expectEq(prices[1], prices[4], "same price every tier")
	expectEq(profile.currency.gems, 5000 - 4 * 500, "500 Gems each")
	profile.currency.gems = 0
	local ok, reason = EconomyRules.BuyVaultTier(profile)
	expect(not ok and reason == "NotEnoughGems", "cannot afford")
end)

test("quests pay once per day and count only their own action", function()
	local profile = ProfileSchema.Default(0)
	EconomyRules.RecordQuest(profile, "Extract", DAY)
	expect(EconomyRules.ClaimQuest(profile, "DailyExtract", DAY), "claimed")
	expectEq(profile.currency.coins, 250, "easy band")
	local ok, reason = EconomyRules.ClaimQuest(profile, "DailyExtract", DAY + 10)
	expect(not ok and reason == "AlreadyClaimed", "once a day")
	expect(not EconomyRules.ClaimQuest(profile, "DailyExtract", DAY + 86400), "next day needs new progress")
	for _ = 1, 3 do
		EconomyRules.RecordQuest(profile, "Extract", DAY)
	end
	expect(EconomyRules.ClaimQuest(profile, "DailyExtractions", DAY), "normal quest")
	expect(profile.boosters.xpUntil >= DAY + 1800, "earnable XP booster")
end)

test("shops sell into the lobby backpack and merchants buy at fixed prices", function()
	local profile = ProfileSchema.Default(0)
	profile.currency.coins = 300
	local id = 0
	local function newId()
		id += 1
		return "n" .. id
	end
	expect(EconomyRules.Buy(profile, "BasicPickaxe", newId, 7), "bought")
	expectEq(profile.currency.coins, 150, "150 Coins")
	expectEq(profile.lobbyBackpack.slots[1].ownerId, 7, "owned")
	local ok, reason = EconomyRules.Buy(profile, "TitleWanderer", newId, 7)
	expect(not ok and reason == "NotEnoughCoins", "too expensive")
	profile.vault.materials.Iron = 10
	local sold, coins = EconomyRules.Sell(profile, "vault", "Iron", 10, "sale:1", 1)
	expect(sold and coins == 80, "10 iron at 8")
	expectEq(profile.vault.materials.Iron, nil, "sold out")
	local value = ShopCatalog.SellValue("StoneSpear")
	expect(value ~= nil and value > 0, "crafted gear is worth 40% of its materials")
	local _, warning = EconomyRules.Quote({ catalogId = "AncientEmber", quantity = 1 })
	expect(warning ~= nil, "selling a Forge reagent warns")
	local permanent = EconomyRules.Quote({ catalogId = "IronSword", instanceId = "p", permanent = true })
	expectEq(permanent, nil, "Permanent items are not sold to merchants")
end)

test("trades reject Coins and raw materials and allow Gems, gear and Permanent items", function()
	local profile = ProfileSchema.Default(0)
	profile.progression.level = 12
	profile.currency.gems = 300
	profile.lobbyBackpack.slots = {
		sword("s1"),
		{ catalogId = "Stone", quantity = 50 },
		{ catalogId = "AncientEmber", quantity = 2 },
		sword("p1", { permanent = true }),
	}
	profile.vault.materials = { Stone = 50, AncientEmber = 2 }
	expect(not TradeRules.ValidateOffer(profile, { items = {}, coins = 100 }, DAY), "Coins never")
	local ok, reason = TradeRules.ValidateOffer(profile, { items = {}, materials = { Stone = 5 } }, DAY)
	expect(not ok and reason == "NotTradeable", "unflagged raw material")
	-- Materials trade only from the vault (GDD §45), never from the backpack.
	ok, reason = TradeRules.ValidateOffer(profile, { items = { 3 } }, DAY)
	expect(not ok and reason == "NotTradeable", "no backpack material offers")
	expect(
		TradeRules.ValidateOffer(profile, { items = { 1, 4 }, materials = { AncientEmber = 2 }, gems = 100 }, DAY),
		"gear, rare vault material, Permanent and Gems"
	)
	profile.progression.level = 5
	ok, reason = TradeRules.ValidateOffer(profile, { items = {}, gems = 10 }, DAY)
	expect(not ok and reason == "GemLevel", "Gem trades need level 10")
	expectEq(TradeRules.GemsAfterFee(100), 95, "5% fee")
end)

local function pair()
	local a, b = ProfileSchema.Default(0), ProfileSchema.Default(0)
	a.progression.level, b.progression.level = 12, 12
	a.lobbyBackpack.slots = { sword("s1", { ownerId = 1 }) }
	b.currency.gems = 200
	return a, b
end

test("a settled trade moves items and Gems once and finalises on both sides", function()
	local a, b = pair()
	TradeRules.Settle("t1", { profile = a, userId = 1, offer = { items = { 1 } } }, {
		profile = b,
		userId = 2,
		offer = { items = {}, gems = 200 },
	}, DAY)
	expectEq(#a.lobbyBackpack.slots, 0, "sword gone from A")
	expectEq(b.lobbyBackpack.slots[1].ownerId, 2, "B owns it")
	expectEq(a.currency.gems, 190, "200 Gems less the 5% fee")
	expectEq(TradeRules.Reconcile(a, "t1", b, DAY), "Settled", "B saved it too")
	expectEq(a.trades.pending.t1, nil, "pending cleared")
end)

test("a crash between the two writes rolls back the side that saved alone", function()
	local a, b = pair()
	local bBefore = ProfileSchema.DeepCopy(b)
	TradeRules.Settle("t2", { profile = a, userId = 1, offer = { items = { 1 } } }, {
		profile = b,
		userId = 2,
		offer = { items = {}, gems = 200 },
	}, DAY)
	-- A's write landed; B's did not, so B's stored profile is the old one.
	expectEq(TradeRules.Reconcile(a, "t2", bBefore, DAY), "RolledBack", "A undone")
	expectEq(a.lobbyBackpack.slots[1].instanceId, "s1", "A has the sword back")
	expectEq(a.currency.gems, 0, "A's received Gems removed")
	expectEq(bBefore.lobbyBackpack.slots[1], nil, "B never received it")
	expectEq(bBefore.currency.gems, 200, "B kept its Gems: one outcome, no duplication")
end)

test("every Robux offer has an earnable equivalent and sells no power", function()
	for _, offer in OfferCatalog.Offers do
		expect(type(offer.earnable) == "string" and #offer.earnable > 10, offer.id .. " earnable route")
		for _, key in OfferCatalog.FORBIDDEN_GRANTS do
			expectEq(offer.grant[key], nil, offer.id .. " grants no " .. key)
		end
	end
end)

test("purchase receipts are fulfilled exactly once", function()
	local profile = ProfileSchema.Default(0)
	local offer = OfferCatalog.ById.GemPack
	local function fulfil(working)
		return EconomyRules.Fulfil(working, offer, 1)
	end
	local _, applied = OperationJournal.Run(profile, "purchase:abc", "Purchase", 1, fulfil)
	expect(applied, "first delivery")
	_, applied = OperationJournal.Run(profile, "purchase:abc", "Purchase", 2, fulfil)
	expect(not applied, "a retried receipt is a no-op")
	expectEq(profile.currency.gems, 100, "100 Gems once")
end)

test("a perk respec refunds every spent token", function()
	local profile = ProfileSchema.Default(0)
	profile.rebirth.ownedPerks = { Scholar = 2, Tidewalker = 1 }
	expect(EconomyRules.Respec(profile), "respec")
	expectEq(profile.rebirth.tokens, 1 + 2 + 1, "all tokens back")
	expect(next(profile.rebirth.ownedPerks) == nil, "no perks left")
end)

test("trading a Permanent item moves its ownership ledger", function()
	local a, b = ProfileSchema.Default(0), ProfileSchema.Default(0)
	a.lobbyBackpack.slots = { sword("p1", { permanent = true, ownershipVersion = 1 }) }
	a.permanentItems.p1 = { catalogId = "IronSword" }
	TradeRules.Settle("t3", { profile = a, userId = 1, offer = { items = { 1 } } }, {
		profile = b,
		userId = 2,
		offer = { items = {} },
	}, DAY)
	expectEq(a.permanentItems.p1, nil, "the giver's claim ends")
	expectEq(b.permanentItems.p1.ownershipVersion, 2, "the receiver owns it")
	expect(b.lobbyBackpack.slots[1].permanent, "still Permanent")
end)
