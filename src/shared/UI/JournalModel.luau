-- What the Quest Journal shows (docs/ui/JournalScreen.md, ARCHITECTURE §4.7, D12),
-- as plain data the window draws: the book tab's quests from the QuestView remote
-- and the trophy tab's progression snapshot, both turned into the same "entry"
-- shape (a list row plus its detail page).
--
--   entry = { id, icon, title, subtitle, status?, illustration, heading,
--             description, objectives = {{icon, title, description, count?,
--             needed?, done}}, rewardsTitle, rewards = {{icon, amount, label}},
--             claim? = {enabled, label}, place? }
--
-- Every word and number comes from the data: quests have one objective, and pay
-- Coins, Gems and an XP boost only.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local EconomyRules = require(ReplicatedStorage.Shared.Economy.EconomyRules)
local HudModel = require(ReplicatedStorage.Shared.UI.HudModel)

local JournalModel = {}

-- The side tabs, top to bottom. "party" opens the Party window instead of a page.
JournalModel.TABS = { "quests", "progress", "map", "party" }
-- Flat glyph ids (drawn "ink:<id>", the selected tab "white:<id>" in leather).
JournalModel.TAB_ICONS = { quests = "book", progress = "trophy", map = "map_pin", party = "people" }

-- Per quest action: the row icon, the detail illustration, the row's line, and
-- the objective's title and description (what the server counts).
JournalModel.ACTIONS = {
	Harvest = {
		icon = "logs",
		illustration = "logs",
		line = "Gather resources.",
		objective = "Gather Resources",
		hint = "Chop trees and mine rocks around the island.",
	},
	Extract = {
		icon = "portal",
		illustration = "portal",
		line = "Leave the island alive.",
		objective = "Extract",
		hint = "Reach an extraction point and get out.",
	},
	Craft = {
		icon = "hammer",
		illustration = "anvil_hammer",
		line = "Make items at a bench.",
		objective = "Craft Items",
		hint = "Every item you craft counts.",
	},
	Enemy = {
		icon = "paw",
		illustration = "paw",
		line = "Hunt island creatures.",
		objective = "Defeat Creatures",
		hint = "Defeat hostile creatures on the island.",
	},
	Cache = {
		icon = "chest",
		illustration = "treasure",
		line = "Find supply caches.",
		objective = "Open Caches",
		hint = "Open supply caches around the island.",
	},
	Boss = {
		icon = "tusk",
		illustration = "tusk",
		line = "Bring down a boss.",
		objective = "Defeat a Boss",
		hint = "Help defeat a boss summoned on the island.",
	},
	Guardian = {
		icon = "totem",
		illustration = "totem",
		line = "Face the Guardian.",
		objective = "Defeat the Guardian",
		hint = "The Guardian fights in the Shattered Keep's courtyard.",
	},
}
local DEFAULT_ACTION = {
	icon = "scroll",
	illustration = "scroll",
	line = "A task on the island.",
	objective = "Complete the Task",
	hint = "",
}

-- The map place a quest points at (IslandMap pin ids), when it has one.
JournalModel.PLACES = { Guardian = "KeepTower" }

-- Mastery track icons for the trophy tab.
JournalModel.TRACK_ICONS = {
	Mining = "pickaxe",
	Woodcutting = "hatchet",
	Farming = "berry_bush",
	Crafting = "anvil_hammer",
	PvP = "spear",
}

-- Groups in list order: daily quests first (they reset), then main quests.
-- Each quest entry carries its group as `tag` ("Daily" | "Main"), drawn small
-- on its row, so the grouping reads without headers pushing the rows down.
JournalModel.GROUPS = {
	{ id = "Daily", title = "Daily Quests" },
	{ id = "Once", title = "Main Quests" },
}

-- Claim refusals in plain words; other codes go through Ui.Reasons.
JournalModel.CLAIM_REASONS = {
	AlreadyClaimed = "This reward was already claimed.",
	NotFinished = "Finish the quest first.",
	UnknownQuest = "That quest no longer exists.",
	BadRequest = "That quest no longer exists.",
}

function JournalModel.Action(action: string?)
	return JournalModel.ACTIONS[action or ""] or DEFAULT_ACTION
end

-- "claimed" | "ready" (finished, reward waiting) | "open".
function JournalModel.Status(quest): string
	if quest.claimed then
		return "claimed"
	elseif (quest.count or 0) >= (quest.needed or 1) then
		return "ready"
	end
	return "open"
end

-- Seconds until the next UTC midnight (daily quests reset then).
function JournalModel.SecondsToReset(now: number): number
	local left = 86400 - (math.floor(now) % 86400)
	return if left <= 0 then 86400 else left
end

-- "5h 12m", "12m", "under a minute".
function JournalModel.Duration(seconds: number): string
	seconds = math.max(0, math.floor(seconds))
	local hours = seconds // 3600
	local minutes = (seconds % 3600) // 60
	if hours > 0 then
		return ("%dh %dm"):format(hours, minutes)
	elseif minutes > 0 then
		return ("%dm"):format(minutes)
	end
	return "under a minute"
end

-- "x250", "x1,000".
function JournalModel.Amount(n: number): string
	return "x" .. HudModel.Thousands(n)
end

-- The reward tiles of a quest: Coins, Gems, XP Boost (what ClaimQuest pays).
function JournalModel.Rewards(quest)
	local list = {}
	if (quest.coins or 0) > 0 then
		table.insert(list, { icon = "coin", amount = JournalModel.Amount(quest.coins), label = "Coins" })
	end
	if (quest.gems or 0) > 0 then
		table.insert(list, { icon = "gem", amount = JournalModel.Amount(quest.gems), label = "Gems" })
	end
	if quest.booster then
		local minutes = EconomyRules.BOOSTER_SECONDS // 60
		table.insert(list, { icon = "lightning", amount = ("%dm"):format(minutes), label = "XP Boost" })
	end
	return list
end

-- The quests of each group, in catalog order: {{id, title, quests}}; empty
-- groups are left out.
function JournalModel.Groups(quests)
	local groups = {}
	for _, group in JournalModel.GROUPS do
		local members = {}
		for _, quest in quests or {} do
			local repeats = if quest.repeats == "Daily" then "Daily" else "Once"
			if repeats == group.id then
				table.insert(members, quest)
			end
		end
		if #members > 0 then
			table.insert(groups, { id = group.id, title = group.title, quests = members })
		end
	end
	return groups
end

-- QUEST PROGRESS: quests finished (or claimed) out of all listed, and its fraction.
function JournalModel.Progress(quests): (number, number, number)
	local done, total = 0, 0
	for _, quest in quests or {} do
		total += 1
		if JournalModel.Status(quest) ~= "open" then
			done += 1
		end
	end
	return done, total, if total > 0 then done / total else 0
end

-- CLAIM: enabled only for a finished, unclaimed quest with no claim on its way.
function JournalModel.Claim(quest, claiming: boolean?)
	local status = JournalModel.Status(quest)
	return {
		enabled = status == "ready" and not claiming,
		busy = claiming == true and status == "ready",
		label = if status == "claimed" then "Claimed" else "Claim",
	}
end

-- The detail page's two lines under the quest's name.
function JournalModel.Description(quest, now: number): string
	local tier = quest.tier or "Normal"
	if quest.repeats == "Daily" then
		return ("A daily quest (%s). Progress resets at midnight UTC, in %s."):format(
			tier,
			JournalModel.Duration(JournalModel.SecondsToReset(now))
		)
	end
	return ("A main quest (%s). It pays its reward once."):format(tier)
end

-- One quest as a list entry with its detail page.
function JournalModel.QuestEntry(quest, now: number, claiming: boolean?)
	local action = JournalModel.Action(quest.action)
	local needed = math.max(1, quest.needed or 1)
	local count = math.clamp(quest.count or 0, 0, needed)
	return {
		id = quest.id,
		icon = action.icon,
		title = quest.name or quest.id,
		subtitle = action.line,
		tag = if quest.repeats == "Daily" then "Daily" else "Main",
		status = JournalModel.Status(quest),
		illustration = action.illustration,
		heading = quest.name or quest.id,
		description = JournalModel.Description(quest, now),
		objectives = {
			{
				icon = action.icon,
				title = action.objective,
				description = action.hint,
				count = count,
				needed = needed,
				done = count >= needed,
			},
		},
		rewardsTitle = "Rewards",
		rewards = JournalModel.Rewards(quest),
		claim = JournalModel.Claim(quest, claiming),
		place = JournalModel.PLACES[quest.action or ""],
	}
end

-- The book tab: groups of entries ({id, entries}, daily first) and the footer.
function JournalModel.QuestPage(quests, now: number, claimingId: string?)
	local groups = {}
	for _, group in JournalModel.Groups(quests) do
		local entries = {}
		for _, quest in group.quests do
			table.insert(entries, JournalModel.QuestEntry(quest, now, claimingId == quest.id))
		end
		table.insert(groups, { id = group.id, entries = entries })
	end
	local done, total, fraction = JournalModel.Progress(quests)
	return {
		groups = groups,
		footer = {
			label = "Quest Progress",
			fraction = fraction,
			text = if quests == nil then "" else ("%d / %d Completed"):format(done, total),
		},
		empty = if quests == nil then "Loading your quests…" else "No quests right now.",
	}
end

-- "Timberhand at level 5" → "Timberhand", 5.
function JournalModel.ParseMilestone(text: string?): (string?, number?)
	if type(text) ~= "string" then
		return nil, nil
	end
	local title, level = string.match(text, "^(.-) at level (%d+)$")
	if title then
		return title, tonumber(level)
	end
	return text, nil
end

-- The trophy tab (D12): a read-only view of the progression snapshot
-- (ProgressionController.View(): level, XP, masteries, titles, rebirth).
function JournalModel.ProgressPage(view)
	if type(view) ~= "table" then
		return {
			groups = {},
			footer = { label = "Level", fraction = 0, text = "" },
			empty = "Your progress is still loading.",
		}
	end
	local level = view.level or 0
	local rebirth = view.rebirth or {}
	local maxed = view.xpToNext == nil
	local entries = {}
	table.insert(entries, {
		id = "Level",
		icon = "star",
		title = ("Level %d"):format(level),
		subtitle = if maxed then "Max level" else ("%d / %d XP"):format(view.xp or 0, view.xpToNext),
		illustration = "trophy",
		heading = ("Level %d"):format(level),
		description = ("Every verified action earns XP. Rebirths: %d. Perk tokens: %d."):format(
			rebirth.count or 0,
			rebirth.tokens or 0
		),
		objectives = {
			if maxed
				then {
					icon = "star",
					title = "Max Level",
					description = "Rebirth in the Progress window to keep climbing.",
					done = true,
				}
				else {
					icon = "star",
					title = ("Reach Level %d"):format(level + 1),
					description = "Gather, craft, fight and extract to earn XP.",
					count = view.xp or 0,
					needed = view.xpToNext,
					done = false,
				},
		},
		rewardsTitle = "Rewards",
		rewards = {},
	})
	for _, mastery in view.masteries or {} do
		local mastered = mastery.nextXp == nil
		local title, at = JournalModel.ParseMilestone(mastery.nextReward)
		local rewards = {}
		if title then
			table.insert(rewards, {
				icon = "crown",
				amount = if at then ("Lv %d"):format(at) else "",
				label = title,
			})
		end
		table.insert(entries, {
			id = "Mastery" .. tostring(mastery.track),
			icon = JournalModel.TRACK_ICONS[mastery.track] or "star",
			title = tostring(mastery.track),
			subtitle = ("Mastery %d / 10"):format(mastery.level or 0),
			illustration = JournalModel.TRACK_ICONS[mastery.track] or "trophy",
			heading = ("%s Mastery"):format(tostring(mastery.track)),
			description = ("Level %d of 10. It grows with every verified %s action."):format(
				mastery.level or 0,
				string.lower(tostring(mastery.track))
			),
			objectives = {
				if mastered
					then {
						icon = JournalModel.TRACK_ICONS[mastery.track] or "star",
						title = "Mastered",
						description = "This track is at its highest level.",
						done = true,
					}
					else {
						icon = JournalModel.TRACK_ICONS[mastery.track] or "star",
						title = ("Reach Mastery %d"):format((mastery.level or 0) + 1),
						description = ("Keep at %s to raise it."):format(string.lower(tostring(mastery.track))),
						count = mastery.xp or 0,
						needed = mastery.nextXp,
						done = false,
					},
			},
			rewardsTitle = "Next Title",
			rewards = rewards,
		})
	end
	local titles = view.titles or {}
	local titleRows = {}
	for _, name in titles do
		table.insert(titleRows, { icon = "crown", title = tostring(name), description = "Earned.", done = true })
	end
	if #titleRows == 0 then
		table.insert(titleRows, {
			icon = "crown",
			title = "No Titles Yet",
			description = "Mastery milestones award them.",
			done = false,
		})
	end
	table.insert(entries, {
		id = "Titles",
		icon = "crown",
		title = "Titles",
		subtitle = ("%d earned"):format(#titles),
		illustration = "crown",
		heading = "Titles",
		description = "Titles you have earned. Your best one shows on your name plate in the lobby.",
		objectives = titleRows,
		rewardsTitle = "Rewards",
		rewards = {},
	})
	return {
		groups = { { id = "Progress", entries = entries } },
		footer = {
			label = ("Level %d"):format(level),
			fraction = if maxed then 1 else HudModel.XpFraction(view.xp or 0, view.xpToNext),
			text = if maxed then "Max level" else ("%d / %d XP"):format(view.xp or 0, view.xpToNext),
		},
		empty = "Your progress is still loading.",
	}
end

-- The entry with `id` in a page, or nil.
function JournalModel.Find(page, id: string?)
	if id == nil then
		return nil
	end
	for _, group in page.groups do
		for _, entry in group.entries do
			if entry.id == id then
				return entry
			end
		end
	end
	return nil
end

-- The first entry of a page, or nil.
function JournalModel.First(page)
	for _, group in page.groups do
		if group.entries[1] then
			return group.entries[1]
		end
	end
	return nil
end

-- The id of the first quest waiting to be claimed, or nil.
function JournalModel.FirstReady(quests): string?
	for _, quest in quests or {} do
		if JournalModel.Status(quest) == "ready" then
			return quest.id
		end
	end
	return nil
end

return JournalModel
