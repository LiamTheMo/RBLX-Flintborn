-- Berry and draught boosts (GDD §51, Q162, docs/ITEM_CATALOG.md §3): one timed
-- boost per kind that never weakens (only a stronger one takes over), XP that adds
-- to Premium and the paid booster, and luck that raises rare-drop chances only.
local Shared = game:GetService("ReplicatedStorage").Shared
local BoostRules = require(Shared.Survival.BoostRules)
local Consumables = require(Shared.Items.Consumables)
local EventRules = require(Shared.Events.EventRules)
local GameConstants = require(Shared.GameConstants)
local ItemCatalog = require(Shared.Items.ItemCatalog)
local ModifierRules = require(Shared.Progression.ModifierRules)
local PerkCatalog = require(Shared.Progression.PerkCatalog)

local catalog = Consumables.Catalog

-- An rng whose every roll is `roll`, so a chance check passes or fails on purpose.
local function fixedRng(roll)
	return {
		NextNumber = function()
			return roll
		end,
		NextInteger = function(_, low)
			return low
		end,
	}
end

test("every boost item carries a valid boost and is usable from the hotbar", function()
	for id, item in catalog do
		if item.kind == Consumables.Boost then
			expect(item.boost ~= nil, id .. " is a Boost item without a boost")
		end
		if item.boost ~= nil then
			expect(BoostRules.IsValid(item.boost), id .. " has a valid boost")
			expect(BoostRules.STATS[item.boost.kind] ~= nil, id .. " boosts a known stat")
		end
		local entry = ItemCatalog.Get(id)
		expect(entry ~= nil and entry.family == ItemCatalog.Families.Consumable, id .. " is a hotbar consumable")
	end
	expectEq(catalog.Sunberry.boost.kind, "XP", "Sunberry boosts XP")
	expectEq(catalog.Glimmerberry.boost.kind, "Luck", "Glimmerberry boosts luck")
	expectEq(catalog.Redberry.boost, nil, "Redberry has no boost")
	expectEq(catalog.Sweetberry.boost, nil, "Sweetberry has no boost")
end)

test("draughts beat raw berries and Strong draughts last longer", function()
	expect(catalog.SunberryDraught.boost.amount > catalog.Sunberry.boost.amount, "Sunberry Draught is stronger")
	expect(catalog.GlimmerDraught.boost.amount > catalog.Glimmerberry.boost.amount, "Glimmer Draught is stronger")
	expect(
		catalog.StrongSunberryDraught.boost.seconds > catalog.SunberryDraught.boost.seconds,
		"Strong Sunberry Draught lasts longer"
	)
	expect(
		catalog.StrongGlimmerDraught.boost.seconds > catalog.GlimmerDraught.boost.seconds,
		"Strong Glimmer Draught lasts longer"
	)
end)

test("bad boosts are rejected", function()
	expect(not BoostRules.IsValid(nil), "nil")
	expect(not BoostRules.IsValid({ kind = "Speed", amount = 0.1, seconds = 60 }), "unknown kind")
	expect(not BoostRules.IsValid({ kind = "XP", amount = -0.1, seconds = 60 }), "negative amount")
	expect(not BoostRules.IsValid({ kind = "XP", amount = 0.1, seconds = 0 }), "no duration")
	expect(not BoostRules.IsValid({ kind = "XP", amount = "lots", seconds = 60 }), "non-number amount")
end)

test("a running boost never weakens: only a stronger one takes over", function()
	local boosts = BoostRules.New()
	local first, started = BoostRules.Apply(boosts, catalog.Sunberry.boost, 0)
	expect(started, "nothing running, so the berry starts")
	expectEq(first.endsAt, 180, "a Sunberry lasts 3 minutes")

	local draught, upgraded = BoostRules.Apply(boosts, catalog.SunberryDraught.boost, 60)
	expect(upgraded, "a stronger draught takes over")
	expectNear(BoostRules.Amount(boosts, "XP", 61), 0.25, 1e-9, "the draught's strength, not the sum")
	expectEq(draught.endsAt, 660, "its own timer, from the drink")

	expect(not BoostRules.Takes(boosts, catalog.Sunberry.boost, 100), "a weaker berry would change nothing")
	local kept, weaker = BoostRules.Apply(boosts, catalog.Sunberry.boost, 100)
	expect(not weaker, "the weaker berry does not start")
	expectEq(kept, draught, "the draught keeps running")
	expectNear(BoostRules.Amount(boosts, "XP", 101), 0.25, 1e-9, "still +25%")
	expectEq(boosts.XP.endsAt, 660, "and its timer is untouched")

	local _, same = BoostRules.Apply(boosts, catalog.StrongSunberryDraught.boost, 500)
	expect(not same, "an equally strong draught changes nothing either")
	expectEq(boosts.XP.endsAt, 660, "the running boost stays static until it ends")

	local _, after = BoostRules.Apply(boosts, catalog.Sunberry.boost, 660)
	expect(after, "once it has run out, any boost starts again")
	expectNear(BoostRules.Amount(boosts, "XP", 661), 0.10, 1e-9, "the berry's own strength")
end)

test("XP and luck boosts run side by side", function()
	local boosts = BoostRules.New()
	BoostRules.Apply(boosts, catalog.SunberryDraught.boost, 0)
	BoostRules.Apply(boosts, catalog.GlimmerDraught.boost, 0)
	expectNear(BoostRules.Amount(boosts, "XP", 10), 0.25, 1e-9, "XP boost")
	expectNear(BoostRules.Amount(boosts, "Luck", 10), 0.15, 1e-9, "luck boost")
	local modifiers = BoostRules.Modifiers(boosts, 10)
	expectEq(#modifiers, 2, "one modifier per running boost")
	expectEq(ModifierRules.Collect(modifiers, "Xp")[1].value, 0.25, "XP feeds the Xp stat")
	expectEq(ModifierRules.Collect(modifiers, "Luck")[1].value, 0.15, "Luck feeds the Luck stat")
end)

test("boosts end on time and stop counting", function()
	local boosts = BoostRules.New()
	BoostRules.Apply(boosts, catalog.Glimmerberry.boost, 0)
	expectNear(BoostRules.Amount(boosts, "Luck", 179.9), 0.05, 1e-9, "still running just before the end")
	expectEq(BoostRules.Amount(boosts, "Luck", 180), 0, "over at 3 minutes")
	expectEq(#BoostRules.Modifiers(boosts, 180), 0, "no modifier once over")
	local _, started = BoostRules.Apply(boosts, catalog.Glimmerberry.boost, 200)
	expect(started, "an expired boost never blocks a new one")
	BoostRules.Prune(boosts, 400)
	expectEq(boosts.Luck, nil, "pruned after it ran out")
end)

test("Q162: a potion XP boost adds to Premium and the paid booster", function()
	local boosts = BoostRules.New()
	BoostRules.Apply(boosts, catalog.SunberryDraught.boost, 0)
	local sources = {
		{ stat = "Xp", op = "Additive", value = GameConstants.PREMIUM_XP_BONUS },
		{ stat = "Xp", op = "Additive", value = 0.5 },
	}
	for _, modifier in BoostRules.Modifiers(boosts, 1) do
		table.insert(sources, modifier)
	end
	local xp = ModifierRules.Collect(sources, "Xp")
	expectEq(#xp, 3, "the potion is counted exactly once")
	expectEq(ModifierRules.Final(100, xp), 200, "+25% Premium, +50% booster and +25% potion give +100%")
	expectEq(ModifierRules.Final(100, ModifierRules.Collect(BoostRules.Modifiers(boosts, 1), "Xp")), 125, "alone")
end)

test("luck sums the Fortune perk and a luck boost", function()
	local boosts = BoostRules.New()
	BoostRules.Apply(boosts, catalog.GlimmerDraught.boost, 0)
	local sources = PerkCatalog.Modifiers({ Fortune = 2 })
	for _, modifier in BoostRules.Modifiers(boosts, 1) do
		table.insert(sources, modifier)
	end
	local luck = 0
	for _, modifier in ModifierRules.Collect(sources, "Luck") do
		luck += modifier.value
	end
	expectNear(luck, 0.19, 1e-9, "+4% Fortune and +15% draught")
end)

test("luck raises rare-drop chances only and never above certain", function()
	local loot = { { "Common", 2, 2, 1 }, { "Rare", 1, 1, 0.2 } }
	local roll = fixedRng(0.21)
	local plain = EventRules.RollLoot(loot, roll, 0)
	expectEq(#plain, 1, "a 0.21 roll misses a 20% row without luck")
	expectEq(plain[1].catalogId, "Common", "the certain row still drops")
	local lucky = EventRules.RollLoot(loot, roll, catalog.GlimmerDraught.boost.amount)
	expectEq(#lucky, 2, "+15% luck makes the 20% row 23%, so 0.21 hits")
	expectEq(lucky[1].quantity, 2, "luck does not change quantities")

	local nearlyCertain = fixedRng(0.999999)
	expectEq(#EventRules.RollLoot({ { "Sure", 1, 1, 1 } }, nearlyCertain, 5), 1, "certain rows stay certain")
	local capped = EventRules.RollLoot({ { "Half", 1, 1, 0.5 } }, fixedRng(1), 5)
	expectEq(#capped, 0, "chance is capped at 1, never more")
end)

test("luck lifts the rare-drop rate by the expected amount over many rolls", function()
	local rng = Random.new(42)
	local loot = { { "Rare", 1, 1, 0.1 } }
	local plain, lucky = 0, 0
	local trials = 20000
	for _ = 1, trials do
		plain += #EventRules.RollLoot(loot, rng, 0)
		lucky += #EventRules.RollLoot(loot, rng, catalog.GlimmerDraught.boost.amount)
	end
	expectNear(plain / trials, 0.10, 0.01, "base 10% rate")
	expectNear(lucky / trials, 0.115, 0.01, "+15% luck gives about 11.5%")
end)

test("use toasts name the item and its effects", function()
	expectEq(BoostRules.UseText(catalog.SunberryDraught), "Sunberry Draught: +25% XP for 10:00", "draught toast")
	expectEq(
		BoostRules.UseText(catalog.Glimmerberry),
		"Glimmerberry: +5% food, +5% rare-drop chance for 3:00",
		"boost berry toast"
	)
	expectEq(BoostRules.UseText(catalog.Redberry), "Redberry: +10% food, heals 10 over 10 s", "Redberry toast")
	expectEq(BoostRules.UseText(catalog.HeartyTonic), "Hearty Tonic: +60% food", "Hearty Tonic toast")
	expectEq(
		BoostRules.UseText(catalog.Sunberry, { amount = 0.25, endsAt = 600 }),
		"Sunberry: +5% food, your +25% XP boost keeps running",
		"a berry eaten under a stronger boost still feeds and says the boost stays"
	)
end)

test("time left reads as minutes and seconds", function()
	expectEq(BoostRules.FormatTime(581), "9:41", "9:41")
	expectEq(BoostRules.FormatTime(0.2), "0:01", "partial seconds round up")
	expectEq(BoostRules.FormatTime(900), "15:00", "Strong draught")
	expectEq(BoostRules.FormatTime(-3), "0:00", "never negative")
	local amountName, untilName = BoostRules.Attributes("XP")
	expectEq(amountName, "BoostXP", "amount attribute")
	expectEq(untilName, "BoostXPUntil", "end-time attribute")
end)
