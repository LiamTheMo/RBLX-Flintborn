-- Quests (GDD §10.1, Q90–92, Q117, Q121). Coin bands are confirmed: easy 250,
-- normal 1,000, hard 3,000. Gem grants sit around 25. Daily quests reset each UTC
-- day; one-time quests pay once. Objectives count verified actions (the XP action
-- keys) or extractions. The roster is a placeholder.

local QuestCatalog = {}

QuestCatalog.BANDS = { Easy = 250, Normal = 1000, Hard = 3000 }

QuestCatalog.Quests = {
	{
		id = "DailyGather",
		name = "Gather 100 times",
		tier = "Easy",
		action = "Harvest",
		count = 100,
		repeats = "Daily",
	},
	{ id = "DailyExtract", name = "Extract once", tier = "Easy", action = "Extract", count = 1, repeats = "Daily" },
	{ id = "DailyCraft", name = "Craft 15 items", tier = "Easy", action = "Craft", count = 15, repeats = "Daily" },
	{
		id = "DailyHunter",
		name = "Defeat 10 creatures",
		tier = "Normal",
		action = "Enemy",
		count = 10,
		repeats = "Daily",
	},
	{
		id = "DailyCaches",
		name = "Open 2 caches",
		tier = "Normal",
		action = "Cache",
		count = 2,
		repeats = "Daily",
		gems = 25,
	},
	{
		id = "DailyExtractions",
		name = "Extract 3 times",
		tier = "Normal",
		action = "Extract",
		count = 3,
		repeats = "Daily",
		booster = true,
	},
	{
		id = "DailyBoss",
		name = "Defeat a boss",
		tier = "Hard",
		action = "Boss",
		count = 1,
		repeats = "Daily",
		gems = 25,
	},
	{
		id = "FirstGuardian",
		name = "Defeat the Guardian",
		tier = "Hard",
		action = "Guardian",
		count = 1,
		repeats = "Once",
		gems = 50,
	},
}

QuestCatalog.ById = {}
for _, quest in QuestCatalog.Quests do
	assert(QuestCatalog.BANDS[quest.tier], "Unknown quest tier " .. quest.tier)
	quest.coins = QuestCatalog.BANDS[quest.tier]
	QuestCatalog.ById[quest.id] = quest
end

function QuestCatalog.Get(questId: any)
	return type(questId) == "string" and QuestCatalog.ById[questId] or nil
end

-- The period a quest's progress belongs to: the UTC day, or "once".
function QuestCatalog.Period(quest, now: number): string
	return if quest.repeats == "Daily" then tostring(now // 86400) else "once"
end

return QuestCatalog
