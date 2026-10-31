-- The world overlays as the real controllers build them, driven by their own
-- remotes and attributes with sample data, over the island backdrop:
--
--   1 in a run: tutorial hint with key caps, downed (bleeding out), boss bar,
--     Horn of War, an event banner, two boosts (one ending soon), save status
--   2 revived / shielded / legacy lists: downed while revived, shielded boss,
--     the extraction and event lists, the boss cue plaque and a subtitle
--   3 body loot window        4 storage chest window
--   5 tribe window (leader)   6 tribe window (no tribe, an invite)
--   7 build palette           8 death summary      9 extraction protection
--
--   python3 art/ui/capture/capture.py world_overlays

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local W, H = 1672, 941
local BG = { background = "art/reference/lobby_map.png" }
workspace.CurrentCamera.ViewportSize = Vector2.new(W, H)
workspace:SetAttribute("FlintbornPlaceRole", "World")
-- Alert sounds are cleaned up by Debris in game.
game:GetService("Debris").AddItem = function() end
-- The event areas are world parts: a stand-in CFrame is enough for the capture.
local frameMeta = {}
frameMeta.__mul = function(a)
	return a
end
CFrame = {
	new = function()
		return setmetatable({}, frameMeta)
	end,
	Angles = function()
		return setmetatable({}, frameMeta)
	end,
}
local newInstance = Instance.new
Instance.new = function(className, parent)
	local made = newInstance(className, parent)
	if className == "Sound" then
		made.Play = function() end
	end
	return made
end

local folder = Instance.new("Folder")
folder.Name = "FlintbornRemotes"
folder.Parent = ReplicatedStorage
local events = {}
for _, name in
	{
		"Notice",
		"BossAlert",
		"ExtractionEvent",
		"ExtractionEnded",
		"EventAnnounced",
		"EventEnded",
		"TutorialChanged",
		"CorpseOpened",
		"DeathSummary",
		"ChestOpened",
		"TribeChanged",
	}
do
	local remote = Instance.new("RemoteEvent")
	remote.Name = name
	remote.Parent = folder
	events[name] = remote
end
for _, name in { "TutorialAction", "CorpseTake", "ChestTake", "ChestPut", "TribeAction", "Build", "BuildInfo" } do
	local remote = Instance.new("RemoteFunction")
	remote.Name = name
	remote.Parent = folder
	remote.InvokeServer = function()
		if name == "BuildInfo" then
			return { auras = {} }
		end
		return true
	end
end

local player = Players.LocalPlayer
player:SetAttribute("SessionState", "ActiveRun")
player:SetAttribute("Level", 12)
player.GetMouse = function()
	return { X = 0, Y = 0 }
end
local character = Instance.new("Model")
character.Name = "Character"
local rootPart = Instance.new("Part")
rootPart.Name = "HumanoidRootPart"
rootPart.Position = Vector3.new(0, 0, 0)
rootPart.Parent = character
character.Parent = workspace
player.Character = character
for index, name in { "ForestRanger", "Mira", "StoneSeeker" } do
	local other = Instance.new("Player")
	other.Name = name
	other.DisplayName = name
	other.UserId = index + 1
	other:SetAttribute("Level", 8 + index * 3)
	other.Parent = Players
end

local bosses = Instance.new("Folder")
bosses.Name = "Bosses"
bosses.Parent = workspace
local boss = Instance.new("Part")
boss.Name = "Guardian"
boss.Position = Vector3.new(40, 0, -60)
boss:SetAttribute("BossName", "Crater Guardian")
boss:SetAttribute("HP", 2140)
boss:SetAttribute("MaxHP", 3000)
boss:SetAttribute("Phase", "Pillars")
boss:SetAttribute("PillarsLeft", 2)
boss:SetAttribute("Shielded", true)
boss.Parent = bosses

local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local Controllers = Client.Controllers
local Theme = require(Client.Ui.Theme)
local HudMode = require(Client.Hud.HudMode)
local InventoryController = require(Controllers.InventoryController)
InventoryController.Snapshot.slots = {
	{ area = "hotbar", index = 1, catalogId = "StoneAxe", quantity = 1 },
	{ area = "hotbar", index = 2, catalogId = "Redberry", quantity = 5 },
	{ area = "backpack", index = 1, catalogId = "Wood", quantity = 24 },
	{ area = "backpack", index = 2, catalogId = "Stone", quantity = 3 },
	{ area = "backpack", index = 3, catalogId = "Fiber", quantity = 12 },
}

local started = {}
for _, name in
	{
		"SaveStatusController",
		"TutorialController",
		"DownedController",
		"BossUiController",
		"EventFeedController",
		"ExtractionController",
		"BoostHudController",
		"LootController",
		"StorageController",
		"TribeController",
		"BuildController",
	}
do
	local controller = require(Controllers[name])
	controller.Start()
	started[name] = controller
end
-- In game the world HUD puts the column under its compass.
local stack = Theme.TopStack()
stack.Position = UDim2.new(0.5, 0, 0, 126)

local gui = player.PlayerGui
local function find(name)
	return gui:FindFirstChild(name, true)
end
local function check(cond, msg)
	print((cond and "  ok " or "  FAIL ") .. msg)
	if not cond then
		__failed = true
	end
end

-- Page 1 ----------------------------------------------------------------------------
player:SetAttribute("SaveStatus", "Saved")
events.TutorialChanged.OnClientEvent:Fire({
	id = "Gather",
	index = 3,
	total = 11,
	title = "Gather",
	hint = "Walk up to a tree, rock or berry bush and press {Interact} to hit it. Hold {Sprint} to run.",
	ack = true,
})
player:SetAttribute("Downed", true)
player:SetAttribute("DownedHealth", 14)
player:SetAttribute("DownedRemaining", 24)
RunService.RenderStepped:Fire(0.016)
events.BossAlert.OnClientEvent:Fire({ kind = "Horn", spawnAt = 154 })
events.EventAnnounced.OnClientEvent:Fire({
	id = "e1",
	name = "Bloodroot Bloom",
	rarity = "Rare",
	category = "Vegetation",
	kind = "Bloom",
	position = Vector3.new(220, 0, -260),
	radius = 30,
	endsAt = 372,
}, false)
local BoostRules = require(ReplicatedStorage.Shared.Survival.BoostRules)
local xpAmount, xpUntil = BoostRules.Attributes("XP")
local luckAmount, luckUntil = BoostRules.Attributes("Luck")
player:SetAttribute(xpAmount, 0.25)
player:SetAttribute(xpUntil, 581)
player:SetAttribute(luckAmount, 0.15)
player:SetAttribute(luckUntil, 22)
RunService.Heartbeat:Fire(1)
-- The cue plaque belongs to page 2.
local cue = find("CueHolder")
if cue then
	for _, child in cue:GetChildren() do
		if child.Name == "Cue" then
			child.Visible = false
		end
	end
end
check(find("Downed").Visible, "the downed card shows")
check(find("BossBar").Visible and find("Horn").Visible, "the boss bar and the horn show")
check(find("EventBanner") ~= nil, "the event banner shows")
check(find("Tutorial").Visible, "the tutorial card shows")
check(find("BoostList").Visible, "the boosts show")
-- The alert caption belongs to page 2.
find("Caption").Visible = false
__dump(gui, W, H, BG)

-- Page 2 ----------------------------------------------------------------------------
player:SetAttribute("DownedReviver", "Mira")
player:SetAttribute("DownedReviveProgress", 6.5)
RunService.RenderStepped:Fire(0.016)
boss:SetAttribute("Shielded", false)
boss:SetAttribute("Phase", "Gauntlet")
events.BossAlert.OnClientEvent:Fire({ kind = "Spawned" })
events.BossAlert.OnClientEvent:Fire({ kind = "Phase" })
if cue then
	for _, child in cue:GetChildren() do
		child.Visible = true
	end
end
find("Tutorial").Visible = false
find("EventBanner"):Destroy()
HudMode.ReplacesLegacy = function()
	return false
end
events.ExtractionEvent.OnClientEvent:Fire({
	id = "x1",
	name = "North Portal",
	kind = "Edge",
	position = Vector3.new(0, 0, -300),
	radius = 20,
	endsAt = 84,
})
events.ExtractionEvent.OnClientEvent:Fire({
	id = "x2",
	name = "Center Portal",
	kind = "Center",
	position = Vector3.new(5, 0, 5),
	radius = 20,
	endsAt = 112,
})
RunService.Heartbeat:Fire(1)
events.EventAnnounced.OnClientEvent:Fire({
	id = "e2",
	name = "Iron Vein",
	rarity = "Epic",
	category = "Ore",
	kind = "Vein",
	position = Vector3.new(-300, 0, 40),
	radius = 20,
	endsAt = 95,
}, true)
find("BoostList").Visible = false
check(find("ExtractionList").Visible, "the legacy extraction list shows")
check(find("Events").Visible, "the legacy event list shows")
__dump(gui, W, H, BG)
-- The run's banners stay out of the window pages.
player:SetAttribute("Downed", false)
RunService.RenderStepped:Fire(0.016)
for _, name in { "BossBar", "Horn", "ExtractionList", "Events", "CueHolder", "Caption", "BoostList" } do
	local part = find(name)
	if part then
		part.Visible = false
	end
end

-- Page 3: loot --------------------------------------------------------------------------
events.CorpseOpened.OnClientEvent:Fire("body1", {
	{ index = 1, name = "Stone Axe", rarity = "Common" },
	{ index = 2, name = "Iron Ore", rarity = "Uncommon", quantity = 6 },
	{ index = 3, name = "Redberry", rarity = "Common", quantity = 4 },
	{ index = 4, name = "Basic Medicine", rarity = "Uncommon", quantity = 2 },
})
check(find("FlintbornLoot").Enabled, "the loot window opens")
__dump(gui, W, H, BG)

-- Page 4: storage ------------------------------------------------------------------------
events.ChestOpened.OnClientEvent:Fire("chest1", {
	{ index = 1, name = "Plank", rarity = "Common", quantity = 40 },
	{ index = 2, name = "Iron Bar", rarity = "Uncommon", quantity = 8 },
	{ index = 3, name = "Stone Spear", rarity = "Common", permanent = true },
})
check(find("FlintbornStorage").Enabled, "the storage window opens")
check(not find("FlintbornLoot").Enabled, "opening it closes the loot window")
__dump(gui, W, H, BG)

-- Page 5: tribe, as its leader -------------------------------------------------------------
started.TribeController.Toggle()
events.TribeChanged.OnClientEvent:Fire({
	tribe = {
		leader = player.UserId,
		members = {
			{ userId = player.UserId, name = player.Name },
			{ userId = 2, name = "ForestRanger" },
		},
		allies = { "t9" },
	},
	invites = {},
	others = { { tribeId = "t7", leader = "StoneSeeker", size = 3 } },
})
Players:GetPlayerByUserId(2):SetAttribute("TribeId", "t1")
events.TribeChanged.OnClientEvent:Fire({
	tribe = {
		leader = player.UserId,
		members = {
			{ userId = player.UserId, name = player.Name },
			{ userId = 2, name = "ForestRanger" },
		},
		allies = { "t9" },
	},
	invites = {},
	others = { { tribeId = "t7", leader = "StoneSeeker", size = 3 } },
})
check(find("FlintbornTribe").Enabled, "the tribe window opens")
__dump(gui, W, H, BG)

-- Page 6: no tribe, an invite --------------------------------------------------------------
events.TribeChanged.OnClientEvent:Fire({
	tribe = nil,
	invites = { { from = "Mira", tribeId = "t3" } },
	others = {},
})
__dump(gui, W, H, BG)
started.TribeController.Toggle()

-- Page 7: build palette ----------------------------------------------------------------------
started.BuildController.Toggle()
local palette = find("Palette")
check(palette and palette.Visible, "the build palette opens")
__dump(gui, W, H, BG)
started.BuildController.Toggle()

-- Page 8: death summary and extraction protection ---------------------------------------------
events.DeathSummary.OnClientEvent:Fire({ dropped = 5, kept = 2 })
check(find("Summary").Visible, "the death summary shows")
__dump(gui, W, H, BG)
find("Summary").Visible = false
player:SetAttribute("SessionState", "ExtractionProtected")
check(find("Protected").Visible, "the protection notice shows")
check(not find("FlintbornStorage").Enabled, "leaving the run closes the chest window")
__dump(gui, W, H, BG)

print(__failed and "SCENE FAILED" or "SCENE OK")
if __failed then
	error("world overlays failed")
end
