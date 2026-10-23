local Shared = game:GetService("ReplicatedStorage").Shared
local DeathRules = require(Shared.Admission.DeathRules)
local ExtractionRules = require(Shared.Extraction.ExtractionRules)
local LevelCurve = require(Shared.Progression.LevelCurve)
local MasteryCatalog = require(Shared.Progression.MasteryCatalog)
local ModifierRules = require(Shared.Progression.ModifierRules)
local ProfileSchema = require(Shared.Data.ProfileSchema)
local ProgressionRules = require(Shared.Progression.ProgressionRules)

test("XP saves when earned and persists through death", function()
	local profile = ProfileSchema.Default(0)
	ProgressionRules.StartRun(profile, "run1")
	ProgressionRules.GrantXp(profile, 150)
	DeathRules.Split({ { catalogId = "Stone", quantity = 3 } })
	expectEq(profile.progression.level, 2, "100 XP reaches level 2")
	expectEq(profile.progression.xp, 50, "50 toward level 3")
	ProgressionRules.StartRun(profile, "run2")
	expectEq(profile.progression.level, 2, "a new run (after dying) keeps everything")
end)

test("the level curve follows 100 × n^1.5 and caps at 50", function()
	expectEq(LevelCurve.XpForLevel(1), 100, "level 1")
	expectEq(LevelCurve.XpForLevel(4), 800, "level 4")
	local level = LevelCurve.Add(1, 0, 10 ^ 9)
	expectEq(level, 50, "capped before rebirth")
end)

test("the Center bonus equals the run's XP once; runes never give it", function()
	local profile = ProfileSchema.Default(0)
	ProgressionRules.StartRun(profile, "run1")
	ProgressionRules.GrantXp(profile, 80)
	ProgressionRules.GrantMastery(profile, "Mining", 30)
	local receipt = ExtractionRules.Settle(profile, {}, "Center", "r1", 1)
	expectEq(receipt.runGeneralXPEarned, 80, "base run XP")
	expectEq(receipt.centerBonusGeneralXP, 80, "an equal bonus")
	expectEq(receipt.centerBonusMasteryXP, 30, "mastery XP doubled too")
	expectEq(profile.progression.masteryTracks.Mining.counters.actions, 30, "but never action counts")
	expectEq(profile.progression.masteryTracks.Mining.counters.xp, 60, "mastery XP 30 + 30")
	local again = ExtractionRules.Settle(profile, {}, "Center", "r2", 2)
	expectEq(again.centerBonusGeneralXP, 0, "never twice for one run, never for prior runs")

	local rune = ProfileSchema.Default(0)
	ProgressionRules.StartRun(rune, "run1")
	ProgressionRules.GrantXp(rune, 80)
	local runeReceipt = ExtractionRules.Settle(rune, {}, "Portable", "r1", 1)
	expectEq(runeReceipt.centerBonusGeneralXP, 0, "portable runes never double")
	expectEq(runeReceipt.runGeneralXPEarned, 80, "the run XP is still listed")
end)

test("exactly five mastery tracks, capped at 10", function()
	expectEq(#MasteryCatalog.TRACKS, 5, "five")
	local profile = ProfileSchema.Default(0)
	ProgressionRules.GrantMastery(profile, "Woodcutting", 100000)
	expectEq(profile.progression.masteryTracks.Woodcutting.level, 10, "cap 10")
	expectEq(ProgressionRules.GrantMastery(profile, "Fishing", 5), 0, "no sixth track")
	expect(profile.progression.titles["Master Woodcutter"], "milestone title granted")
end)

test("gathering yield reaches +10% at mastery 10", function()
	local buffs = MasteryCatalog.Buffs("Mining", 10)
	expectEq(ModifierRules.Final(100, buffs), 110, "+10%")
	expectEq(ModifierRules.Final(100, MasteryCatalog.Buffs("Farming", 3)), 103, "+1% per level")
	local pvp = ModifierRules.Collect(MasteryCatalog.Buffs("PvP", 10), "PvpDamage")
	expectEq(pvp[1].value, 0.05, "PvP combat perks capped at +5%")
end)

test("additive then multiplicative: base 100, +10% and ×1.2 gives 132", function()
	local modifiers = { { op = "Additive", value = 0.1 }, { op = "Multiplicative", value = 1.2 } }
	expectEq(ModifierRules.Final(100, modifiers), 132, "132")
	expectEq(
		ModifierRules.Final(100, { { op = "Additive", value = 0.25 }, { op = "Additive", value = 0.5 } }),
		175,
		"Premium +25% and a +50% booster add to +75%"
	)
end)

test("rebirth resets only the general level and keeps everything else", function()
	local profile = ProfileSchema.Default(0)
	profile.progression.level = 50
	profile.vault.materials.Iron = 500
	profile.permanentItems.p1 = { catalogId = "BasicPickaxe" }
	ProgressionRules.GrantMastery(profile, "Crafting", 500)
	profile.rebirth.ownedPerks.Scholar = 2
	local ok, reason = ProgressionRules.Rebirth(profile)
	expect(not ok and reason == "ChallengeIncomplete", "needs a Guardian Legendary extracted")
	ExtractionRules.Settle(
		profile,
		{ { instanceId = "g1", catalogId = "GuardianFang", ownerId = 1 } },
		"Fixed",
		"r1",
		1
	)
	expect(ProgressionRules.Rebirth(profile), "rebirth")
	expectEq(profile.progression.level, 1, "level reset")
	expectEq(profile.vault.materials.Iron, 500, "vault kept")
	expect(profile.permanentItems.p1 ~= nil, "Permanent items kept")
	expectEq(profile.progression.masteryTracks.Crafting.level, 5, "masteries kept")
	expectEq(profile.rebirth.ownedPerks.Scholar, 2, "perks kept")
	expectEq(profile.rebirth.tokens, 3, "3 tokens")
	expectEq(ProgressionRules.RequiredLegendaries(1), 2, "the next rebirth is harder")
	expectEq(ProgressionRules.TokensFor(3), 4, "+1 token every third rebirth")
end)

test("perk ranks spend tokens once and stop at the max rank", function()
	local profile = ProfileSchema.Default(0)
	profile.rebirth.tokens = 4
	expect(ProgressionRules.BuyPerk(profile, "Tidewalker"), "rank 1")
	expect(ProgressionRules.BuyPerk(profile, "Tidewalker"), "rank 2")
	local ok, reason = ProgressionRules.BuyPerk(profile, "Tidewalker")
	expect(not ok and reason == "MaxRank", "max rank")
	expectEq(profile.rebirth.tokens, 1, "1 + 2 spent")
	ok, reason = ProgressionRules.BuyPerk(profile, "Fortune")
	expect(not ok and reason == "NotEnoughTokens", "cannot overspend")
end)
