-- The world overlays on a phone held sideways (844 × 390, touch only): the
-- banner column, boosts and save status at the HUD's phone scale, the loot and
-- tribe windows fitted to the whole height, the build palette, and the world
-- menu. Real controllers, mocked remotes, sample data as in world_overlays.
--
--   1 run banners    2 loot window    3 tribe window    4 build palette
--   5 world menu (ready)
--
--   python3 art/ui/capture/capture.py world_overlays_phone

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")
local W, H = 844, 390
local BG = { background = "art/reference/lobby_map.png" }
workspace.CurrentCamera.ViewportSize = Vector2.new(W, H)
UserInputService.TouchEnabled = true
UserInputService.KeyboardEnabled = false
UserInputService.MouseEnabled = false
workspace:SetAttribute("FlintbornPlaceRole", "World")
game:GetService("Debris").AddItem = function() end

local folder = Instance.new("Folder")
folder.Name = "FlintbornRemotes"
folder.Parent = ReplicatedStorage
local events = {}
for _, name in { "TutorialChanged", "CorpseOpened", "DeathSummary", "TribeChanged" } do
	local remote = Instance.new("RemoteEvent")
	remote.Name = name
	remote.Parent = folder
	events[name] = remote
end
for _, name in { "TutorialAction", "CorpseTake", "TribeAction", "Build", "BuildInfo", "RequestPlay", "ReturnToLobby" } do
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
local other = Instance.new("Player")
other.Name = "Mira"
other.DisplayName = "Mira"
other.UserId = 2
other:SetAttribute("Level", 14)
other.Parent = Players

local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local Controllers = Client.Controllers
local Theme = require(Client.Ui.Theme)
local BoostRules = require(ReplicatedStorage.Shared.Survival.BoostRules)
local started = {}
for _, name in
	{
		"SaveStatusController",
		"TutorialController",
		"DownedController",
		"BoostHudController",
		"LootController",
		"TribeController",
		"BuildController",
		"WorldMenuController",
	}
do
	started[name] = require(Controllers[name])
	started[name].Start()
end
local stack = Theme.TopStack()
stack.Position = UDim2.new(0.5, 0, 0, 58)
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
check(
	Theme.HudScale(gui) == Theme.PHONE_MIN_SCALE,
	("overlays keep the phone floor (%.3f)"):format(Theme.HudScale(gui))
)
-- Shown for three seconds when the run starts (the world menu's toast).
find("Transition").Visible = false

player:SetAttribute("SaveStatus", "Saving")
events.TutorialChanged.OnClientEvent:Fire({
	id = "Gather",
	index = 3,
	total = 11,
	title = "Gather",
	hint = "Walk up to a tree and press {Interact} to hit it.",
	ack = true,
})
player:SetAttribute("Downed", true)
player:SetAttribute("DownedHealth", 14)
player:SetAttribute("DownedRemaining", 24)
RunService.RenderStepped:Fire(0.016)
local xpAmount, xpUntil = BoostRules.Attributes("XP")
player:SetAttribute(xpAmount, 0.25)
player:SetAttribute(xpUntil, 581)
RunService.Heartbeat:Fire(1)
__dump(gui, W, H, BG)

player:SetAttribute("Downed", false)
RunService.RenderStepped:Fire(0.016)
find("Tutorial").Visible = false
find("BoostList").Visible = false
events.CorpseOpened.OnClientEvent:Fire("body1", {
	{ index = 1, name = "Stone Axe", rarity = "Common" },
	{ index = 2, name = "Iron Ore", rarity = "Uncommon", quantity = 6 },
	{ index = 3, name = "Redberry", rarity = "Common", quantity = 4 },
})
__dump(gui, W, H, BG)

started.TribeController.Toggle()
events.TribeChanged.OnClientEvent:Fire({
	tribe = {
		leader = player.UserId,
		members = { { userId = player.UserId, name = player.Name } },
		allies = {},
	},
	invites = {},
	others = {},
})
check(find("FlintbornTribe").Enabled, "the tribe window opens")
__dump(gui, W, H, BG)
started.TribeController.Toggle()

started.BuildController.Toggle()
__dump(gui, W, H, BG)
started.BuildController.Toggle()

player:SetAttribute("SessionState", "WorldMainMenuReady")
check(find("WorldMenu").Enabled, "the world menu shows")
__dump(gui, W, H, BG)

print(__failed and "SCENE FAILED" or "SCENE OK")
if __failed then
	error("world overlays phone failed")
end
