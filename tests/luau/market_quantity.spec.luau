-- Market quantities (docs/ui/ListWindows.md, Market): the Buy and Sell tabs pick
-- how many with a slider and a stepper, and the server takes that amount only
-- after its own checks. EconomyRules.Buy buys a validated number of one entry
-- all or nothing; EconomyRules.Sell sells part of a backpack stack; MaxBuy is the
-- limit the picker offers.

local Shared = game:GetService("ReplicatedStorage").Shared
local Server = game:GetService("ServerScriptService").Server
local EconomyRules = require(Shared.Economy.EconomyRules)
local GameConstants = require(Shared.GameConstants)
local ItemCatalog = require(Shared.Items.ItemCatalog)
local ProfileSchema = require(Server.Rules.Data.ProfileSchema)
local ShopCatalog = require(Shared.Economy.ShopCatalog)

local function ids()
	local n = 0
	return function()
		n += 1
		return "id" .. n
	end
end

local function rich(coins: number)
	local profile = ProfileSchema.Default(0)
	profile.currency.coins = coins
	return profile
end

local function count(profile, catalogId: string): number
	local total = 0
	for _, slot in profile.lobbyBackpack.slots do
		if slot.catalogId == catalogId then
			total += slot.quantity or 1
		end
	end
	return total
end

test("buying several packs costs each pack and lands as one stack; no quantity buys one", function()
	local profile = rich(1000)
	local ok = EconomyRules.Buy(profile, "RedberryPack", ids(), 7, 3)
	expect(ok, "three packs bought")
	expectEq(profile.currency.coins, 1000 - 3 * ShopCatalog.ById.RedberryPack.price, "paid for three")
	expectEq(count(profile, "Redberry"), 15, "three packs of five")
	expectEq(#profile.lobbyBackpack.slots, 1, "one stack")
	-- No quantity buys one, as before.
	local single = rich(500)
	expect(EconomyRules.Buy(single, "Bandage", ids(), 7), "one bought")
	expectEq(count(single, "BasicMedicine"), 1, "one medicine")
	expectEq(single.currency.coins, 450, "one price")
end)

test("buying several tools makes one item each, every one owned", function()
	local profile = rich(1000)
	expect(EconomyRules.Buy(profile, "StoneAxe", ids(), 7, 4), "four axes")
	expectEq(#profile.lobbyBackpack.slots, 4, "four slots")
	local seen = {}
	for _, slot in profile.lobbyBackpack.slots do
		expect(slot.instanceId ~= nil and not seen[slot.instanceId], "a unique id each")
		seen[slot.instanceId] = true
		expectEq(slot.ownerId, 7, "owned")
	end
	expectEq(profile.currency.coins, 1000 - 4 * 150, "paid 4 x 150")
end)

test("a client quantity that is not a whole number in range is refused and changes nothing", function()
	for _, bad in { 0, -2, 1.5, 0 / 0, math.huge, -math.huge, EconomyRules.MAX_BUY_QUANTITY + 1, "3", true, {} } do
		local profile = rich(1000000)
		local ok, reason = EconomyRules.Buy(profile, "RedberryPack", ids(), 7, bad)
		expect(not ok and reason == "BadQuantity", "refused: " .. tostring(bad))
		expectEq(profile.currency.coins, 1000000, "no Coins taken for " .. tostring(bad))
		expectEq(#profile.lobbyBackpack.slots, 0, "nothing added for " .. tostring(bad))
	end
end)

test("a title is bought once: a larger quantity is refused", function()
	local profile = rich(100000)
	local ok, reason = EconomyRules.Buy(profile, "TitleWanderer", ids(), 7, 2)
	expect(not ok and reason == "BadQuantity", "two titles refused")
	expect(EconomyRules.Buy(profile, "TitleWanderer", ids(), 7, 1), "one title")
	expectEq(EconomyRules.MaxBuy(profile, "TitleWanderer"), 0, "an owned title offers none")
end)

test("a purchase the Coins or the backpack cannot cover in full buys nothing", function()
	local poor = rich(100)
	local ok, reason = EconomyRules.Buy(poor, "RedberryPack", ids(), 7, 3)
	expect(not ok and reason == "NotEnoughCoins", "120 Coins needed")
	expectEq(poor.currency.coins, 100, "Coins kept")
	expectEq(#poor.lobbyBackpack.slots, 0, "no berries")
	local profile = rich(1000000)
	for i = 1, GameConstants.BACKPACK_SLOTS - 2 do
		profile.lobbyBackpack.slots[i] = { instanceId = "x" .. i, catalogId = "StoneSpear", qualityRoll = 0 }
	end
	ok, reason = EconomyRules.Buy(profile, "StoneAxe", ids(), 7, 3)
	expect(not ok and reason == "BackpackFull", "three axes need three free slots")
	expectEq(#profile.lobbyBackpack.slots, GameConstants.BACKPACK_SLOTS - 2, "no axe added")
	expectEq(profile.currency.coins, 1000000, "no Coins taken")
	expect(EconomyRules.Buy(profile, "StoneAxe", ids(), 7, 2), "two fit")
	-- A stack is capped (Q128): packs past the cap do not fit.
	local berries = rich(1000000)
	local cap = ItemCatalog.StackCap("Redberry")
	berries.lobbyBackpack.slots[1] = { catalogId = "Redberry", quantity = cap - 7 }
	ok, reason = EconomyRules.Buy(berries, "RedberryPack", ids(), 7, 2)
	expect(not ok and reason == "BackpackFull", "ten more berries pass the cap")
	expectEq(berries.lobbyBackpack.slots[1].quantity, cap - 7, "stack untouched")
	expect(EconomyRules.Buy(berries, "RedberryPack", ids(), 7, 1), "one pack fits")
end)

test("MaxBuy offers what the Coins, the backpack and the limit allow", function()
	local profile = rich(130)
	expectEq(EconomyRules.MaxBuy(profile, "RedberryPack"), 3, "130 Coins cover three 40-Coin packs")
	profile.currency.coins = 1000000
	expectEq(
		EconomyRules.MaxBuy(profile, "RedberryPack"),
		math.min(EconomyRules.MAX_BUY_QUANTITY, ItemCatalog.StackCap("Redberry") // 5),
		"the stack cap and the limit"
	)
	expectEq(EconomyRules.MaxBuy(profile, "StoneAxe"), EconomyRules.MAX_BUY_QUANTITY, "an empty backpack")
	for i = 1, GameConstants.BACKPACK_SLOTS - 1 do
		profile.lobbyBackpack.slots[i] = { instanceId = "x" .. i, catalogId = "StoneSpear", qualityRoll = 0 }
	end
	expectEq(EconomyRules.MaxBuy(profile, "StoneAxe"), 1, "one free slot")
	expectEq(EconomyRules.MaxBuy(profile, "Nope"), 0, "unknown stock")
	-- Whatever MaxBuy offers goes through, and one more does not.
	local fresh = rich(130)
	local max = EconomyRules.MaxBuy(fresh, "RedberryPack")
	expect(EconomyRules.Buy(fresh, "RedberryPack", ids(), 7, max), "the offered maximum buys")
	local ok = EconomyRules.Buy(fresh, "RedberryPack", ids(), 7, 1)
	expect(not ok, "and nothing past it")
end)

test("a backpack stack sells in part and the rest stays; no quantity sells the whole slot", function()
	local profile = rich(0)
	profile.lobbyBackpack.slots[1] = { catalogId = "Flint", quantity = 10 }
	local ok, coins = EconomyRules.Sell(profile, "backpack", 1, 4, "sale:a", 1)
	expect(ok and coins == 4 * ShopCatalog.SellValue("Flint"), "four flint sold")
	expectEq(profile.lobbyBackpack.slots[1].quantity, 6, "six left")
	expectEq(profile.currency.coins, coins, "paid")
	ok = EconomyRules.Sell(profile, "backpack", 1, 6, "sale:b", 1)
	expect(ok and #profile.lobbyBackpack.slots == 0, "selling the rest empties the slot")
	-- No quantity sells the whole slot, as before.
	profile.lobbyBackpack.slots[1] = { catalogId = "Flint", quantity = 10 }
	ok, coins = EconomyRules.Sell(profile, "backpack", 1, nil, "sale:all", 1)
	expect(ok and coins == 10 * ShopCatalog.SellValue("Flint"), "all ten")
	expectEq(#profile.lobbyBackpack.slots, 0, "slot gone")
end)

test("a backpack sale never sells more than the slot holds, nor odd amounts", function()
	for _, bad in { 11, 0, -1, 2.5, 0 / 0, math.huge, "4", false } do
		local profile = rich(0)
		profile.lobbyBackpack.slots[1] = { catalogId = "Flint", quantity = 10 }
		local ok, reason = EconomyRules.Sell(profile, "backpack", 1, bad, "sale:x", 1)
		expect(not ok and reason == "BadQuantity", "refused: " .. tostring(bad))
		expectEq(profile.lobbyBackpack.slots[1].quantity, 10, "stack kept for " .. tostring(bad))
		expectEq(profile.currency.coins, 0, "no Coins for " .. tostring(bad))
	end
	-- A unique item is one: 1 or nil sells it, more is refused.
	local profile = rich(0)
	profile.lobbyBackpack.slots[1] = { instanceId = "s", catalogId = "StoneSpear", qualityRoll = 0 }
	local ok, reason = EconomyRules.Sell(profile, "backpack", 1, 2, "sale:y", 1)
	expect(not ok and reason == "BadQuantity", "two of one spear refused")
	expect(EconomyRules.Sell(profile, "backpack", 1, 1, "sale:z", 1), "one spear sells")
end)

test("a backpack slot that changed since the client looked sells nothing", function()
	local profile = rich(0)
	profile.lobbyBackpack.slots[1] = { catalogId = "Wood", quantity = 10 }
	local ok, reason = EconomyRules.Sell(profile, "backpack", 1, 5, "sale:c", 1, "Flint")
	expect(not ok and reason == "SlotChanged", "the client asked for flint")
	expectEq(profile.lobbyBackpack.slots[1].quantity, 10, "wood kept")
	expect(EconomyRules.Sell(profile, "backpack", 1, 5, "sale:d", 1, "Wood"), "the matching slot sells")
end)

test("vault sales still refuse more than is stored", function()
	local profile = rich(0)
	profile.vault.materials.IronOre = 5
	local ok, reason = EconomyRules.Sell(profile, "vault", "IronOre", 6, "sale:e", 1)
	expect(not ok and reason == "NotEnough", "six of five")
	expectEq(profile.vault.materials.IronOre, 5, "kept")
	expect(EconomyRules.Sell(profile, "vault", "IronOre", 2, "sale:f", 1), "two of five")
	expectEq(profile.vault.materials.IronOre, 3, "three left")
end)
