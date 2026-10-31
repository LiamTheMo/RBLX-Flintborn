-- The Quest Journal window (Hud/Screens/JournalWindow) at 1672 × 941 over the
-- lobby mockup, placed where 07_quest_journal.png has it, with quests shaped
-- like the QuestView remote's (the real catalog) and a progression snapshot.
-- One page per state:
--   1 book tab: the first quest chosen (under way), as the mockup
--   2 a finished quest chosen: CLAIM enabled; row hover / pressed, CLAIM hover
--   3 a claimed quest: CLAIMED (disabled); row focus (gamepad)
--   4 a claim on its way: CLAIM busy
--   5 trophy tab: progression (level, masteries, titles), a mastery chosen
--   6 trophy tab: titles chosen (several rows, scrolling objectives)
--   7 map pin tab: the island map with the Guardian's place
--   8 empty and loading states; side tabs hover / pressed / disabled (party)
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Hud = game:GetService("StarterPlayer").StarterPlayerScripts.Client.Hud
local Kit = require(Hud.Kit)
local JournalWindow = require(Hud.Screens.JournalWindow)
local JournalModel = require(ReplicatedStorage.Shared.UI.JournalModel)
local QuestCatalog = require(ReplicatedStorage.Shared.Economy.QuestCatalog)

local W, H = 1672, 941
local BACKGROUND = "art/reference/ui/lobby/01_hud.png"
-- 5 h 12 m before midnight UTC.
local NOW = 20000 * 86400 - (5 * 3600 + 12 * 60)

local missing = Kit.Art.Missing()
assert(#missing == 0, "roles without a manifest sprite: " .. table.concat(missing, ", "))

-- The catalog with some progress: one finished, one claimed, the rest under way.
local PROGRESS = {
	DailyGather = { 12, false },
	DailyExtract = { 1, true },
	DailyCraft = { 15, false },
	DailyHunter = { 3, false },
	DailyCaches = { 0, false },
	DailyExtractions = { 1, false },
	DailyBoss = { 0, false },
	FirstGuardian = { 0, false },
}
local function questView()
	local list = {}
	for _, quest in QuestCatalog.Quests do
		local p = PROGRESS[quest.id]
		table.insert(list, {
			id = quest.id,
			name = quest.name,
			tier = quest.tier,
			coins = quest.coins,
			gems = quest.gems,
			booster = quest.booster,
			count = p[1],
			needed = quest.count,
			claimed = p[2],
			repeats = quest.repeats,
			action = quest.action,
		})
	end
	return list
end

local SNAPSHOT = {
	level = 12,
	xp = 450,
	xpToNext = 750,
	masteries = {
		{ track = "Mining", level = 3, xp = 120, nextXp = 300, nextReward = "Stonebreaker at level 5" },
		{ track = "Woodcutting", level = 5, xp = 520, nextXp = 800, nextReward = "Master Woodcutter at level 10" },
		{ track = "Farming", level = 0, xp = 4, nextXp = 25, nextReward = "Green Thumb at level 5" },
		{ track = "Crafting", level = 2, xp = 80, nextXp = 150, nextReward = "Artisan at level 5" },
		{ track = "PvP", level = 10, xp = 3200, nextXp = nil, nextReward = nil },
	},
	titles = { "Duelist", "Timberhand", "Warlord" },
	rebirth = { count = 0, tokens = 0 },
	premium = false,
	boosterUntil = 0,
}

local window = JournalWindow.new(nil, {})
local screen = window.screen
local quests = questView()
window:SetPage("quests", JournalModel.QuestPage(quests, NOW))
window:SetPage("progress", JournalModel.ProgressPage(SNAPSHOT))
window:SetPartyAvailable(true)
screen:Open()
-- Where the mockup has the frame: left 300, top 150 (the screen is 50 px wider
-- each side for the tabs).
screen.holder.Position = UDim2.fromOffset(300 - JournalWindow.MARGIN + JournalWindow.SIZE[1] / 2, 150 + 688 / 2)
screen.scale.Scale = 1

local function dump()
	__dump(Players.LocalPlayer.PlayerGui, W, H, { background = BACKGROUND })
end

local function force(component, state)
	component.root:SetAttribute("DebugState", state)
end

-- 1: as the mockup.
dump()

-- 2: a finished quest, CLAIM enabled; hover and press on rows, CLAIM hover.
window:Select("DailyCraft")
force(window.rows.DailyExtract, "hover")
force(window.rows.DailyHunter, "pressed")
force(window.claim, "hover")
dump()
force(window.rows.DailyExtract, "")
force(window.rows.DailyHunter, "")
force(window.claim, "")

-- 3: a claimed quest; gamepad focus on a row.
window:Select("DailyExtract")
force(window.rows.DailyCaches, "focused")
dump()

-- 4: a claim on its way.
window:SetPage("quests", JournalModel.QuestPage(quests, NOW, "DailyCraft"))
window:Select("DailyCraft")
dump()

-- 5: trophy tab, a mastery chosen.
window:SelectTab("progress")
window:Select("MasteryWoodcutting")
dump()

-- 6: trophy tab, titles.
window:Select("Titles")
dump()

-- 7: map tab with the Guardian's place.
window:SelectTab("quests")
window:Select("FirstGuardian")
window:SelectTab("map")
dump()

-- 8: loading quests; tabs hover / pressed; party unavailable.
window:SetPage("quests", JournalModel.QuestPage(nil, NOW))
window:SelectTab("quests")
window:SetPartyAvailable(false)
force(window.tabs.progress, "hover")
force(window.tabs.map, "pressed")
dump()
