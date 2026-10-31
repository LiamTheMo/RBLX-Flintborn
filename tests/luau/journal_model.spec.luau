local Shared = game:GetService("ReplicatedStorage").Shared
local JournalModel = require(Shared.UI.JournalModel)
local QuestCatalog = require(Shared.Economy.QuestCatalog)
local EconomyRules = require(Shared.Economy.EconomyRules)

local function quest(id, count, claimed)
	local entry = QuestCatalog.Get(id)
	return {
		id = entry.id,
		name = entry.name,
		tier = entry.tier,
		coins = entry.coins,
		gems = entry.gems,
		booster = entry.booster,
		count = count,
		needed = entry.count,
		claimed = claimed,
		repeats = entry.repeats,
		action = entry.action,
	}
end

test("status: open, ready when finished, claimed", function()
	expectEq(JournalModel.Status(quest("DailyGather", 12, false)), "open", "under way")
	expectEq(JournalModel.Status(quest("DailyGather", 100, false)), "ready", "finished")
	expectEq(JournalModel.Status(quest("DailyGather", 100, true)), "claimed", "claimed")
end)

test("claim is enabled only for a finished, unclaimed quest with no claim on its way", function()
	expect(not JournalModel.Claim(quest("DailyCraft", 3, false)).enabled, "unfinished")
	expect(JournalModel.Claim(quest("DailyCraft", 15, false)).enabled, "finished")
	local busy = JournalModel.Claim(quest("DailyCraft", 15, false), true)
	expect(not busy.enabled and busy.busy, "busy while claiming")
	local done = JournalModel.Claim(quest("DailyCraft", 15, true))
	expect(not done.enabled, "claimed is disabled")
	expectEq(done.label, "Claimed", "claimed label")
end)

test("rewards are only what ClaimQuest pays", function()
	local plain = JournalModel.Rewards(quest("DailyGather", 0, false))
	expectEq(#plain, 1, "coins only")
	expectEq(plain[1].label, "Coins", "coins label")
	expectEq(plain[1].amount, "x250", "coin amount")
	local gems = JournalModel.Rewards(quest("FirstGuardian", 0, false))
	expectEq(#gems, 2, "coins and gems")
	expectEq(gems[2].amount, "x50", "gem amount")
	local boost = JournalModel.Rewards(quest("DailyExtractions", 0, false))
	expectEq(boost[#boost].label, "XP Boost", "booster tile")
	expectEq(boost[#boost].amount, ("%dm"):format(EconomyRules.BOOSTER_SECONDS // 60), "booster length")
	expectEq(JournalModel.Rewards(quest("DailyBoss", 0, false))[1].amount, "x3,000", "thousands")
end)

test("groups: daily first, then main; progress is the real fraction", function()
	local list = {}
	for _, entry in QuestCatalog.Quests do
		table.insert(list, quest(entry.id, 0, false))
	end
	list[1].count = list[1].needed
	list[2].count, list[2].claimed = list[2].needed, true
	local groups = JournalModel.Groups(list)
	expectEq(groups[1].id, "Daily", "daily first")
	expectEq(groups[#groups].id, "Once", "main last")
	local done, total, fraction = JournalModel.Progress(list)
	expectEq(done, 2, "finished and claimed count")
	expectEq(total, #QuestCatalog.Quests, "all listed")
	expectNear(fraction, 2 / #QuestCatalog.Quests, 1e-9, "fraction")
	local page = JournalModel.QuestPage(list, 0)
	expectEq(page.footer.text, ("2 / %d Completed"):format(#QuestCatalog.Quests), "footer text")
	expectEq(JournalModel.QuestPage(nil, 0).footer.text, "", "no count while loading")
end)

test("a quest entry has one objective with its real count", function()
	local entry = JournalModel.QuestEntry(quest("DailyGather", 12, false), 0)
	expectEq(#entry.objectives, 1, "one objective")
	expectEq(entry.objectives[1].count, 12, "count")
	expectEq(entry.objectives[1].needed, 100, "needed")
	expect(not entry.objectives[1].done, "not done")
	expectEq(entry.icon, "logs", "icon by action")
	expectEq(JournalModel.QuestEntry(quest("FirstGuardian", 0, false), 0).place, "KeepTower", "guardian place")
	expectEq(JournalModel.QuestEntry(quest("DailyBoss", 0, false), 0).place, nil, "bosses have no fixed place")
end)

test("daily reset countdown", function()
	expectEq(JournalModel.SecondsToReset(86400 * 3), 86400, "at midnight")
	expectEq(JournalModel.SecondsToReset(86400 * 3 - 60), 60, "a minute before")
	expectEq(JournalModel.Duration(5 * 3600 + 12 * 60 + 30), "5h 12m", "hours and minutes")
	expectEq(JournalModel.Duration(30), "under a minute", "seconds")
end)

test("progress page reads the progression snapshot", function()
	expect(#JournalModel.ProgressPage(nil).groups == 0, "nothing while loading")
	local page = JournalModel.ProgressPage({
		level = 12,
		xp = 450,
		xpToNext = 750,
		masteries = {
			{ track = "Mining", level = 3, xp = 120, nextXp = 300, nextReward = "Stonebreaker at level 5" },
			{ track = "PvP", level = 10, xp = 3200 },
		},
		titles = { "Warlord" },
		rebirth = { count = 1, tokens = 2 },
	})
	expectNear(page.footer.fraction, 450 / 750, 1e-9, "level fraction")
	local mining = JournalModel.Find(page, "MasteryMining")
	expectEq(mining.objectives[1].count, 120, "mastery xp")
	expectEq(mining.rewards[1].label, "Stonebreaker", "next title")
	expectEq(mining.rewards[1].amount, "Lv 5", "title level")
	expect(JournalModel.Find(page, "MasteryPvP").objectives[1].done, "mastered")
	expectEq(JournalModel.Find(page, "Titles").objectives[1].title, "Warlord", "titles listed")
	expect(JournalModel.Find(page, "Level").claim == nil, "nothing to claim")
end)
