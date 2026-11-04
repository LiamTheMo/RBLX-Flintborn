-- Server half of Shared.Economy.QuestCatalog: what only the server uses. Everything in
-- ReplicatedStorage is downloaded to every player, so the shared module keeps
-- only what clients need; this one clones it and adds the rest, and server code
-- requires this module.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local SharedQuestCatalog = require(ReplicatedStorage.Shared.Economy.QuestCatalog)

local QuestCatalog = table.clone(SharedQuestCatalog)

function QuestCatalog.Get(questId: any)
	return type(questId) == "string" and QuestCatalog.ById[questId] or nil
end

-- The period a quest's progress belongs to: the UTC day, or "once".
function QuestCatalog.Period(quest, now: number): string
	return if quest.repeats == "Daily" then tostring(now // 86400) else "once"
end

return QuestCatalog
