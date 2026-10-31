-- The protected world menu through the real WorldMenuController, its session
-- states set as the server sets them and its remotes mocked:
--
--   1 loading (Play disabled)    2 ready              3 Play pressed: the request
--   fails, the reason shows      4 game-update notice 5 Play hover
--   6 entering the world: the menu closes and the at-risk toast shows
--
--   python3 art/ui/capture/capture.py world_menu

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local W, H = 1672, 941
workspace.CurrentCamera.ViewportSize = Vector2.new(W, H)
workspace:SetAttribute("FlintbornPlaceRole", "World")
local folder = Instance.new("Folder")
folder.Name = "FlintbornRemotes"
folder.Parent = ReplicatedStorage
local calls = {}
local answers = { RequestPlay = { false, "NotReady" }, ReturnToLobby = { true } }
for name in answers do
	local remote = Instance.new("RemoteFunction")
	remote.Name = name
	remote.Parent = folder
	remote.InvokeServer = function()
		table.insert(calls, name)
		return table.unpack(answers[name])
	end
end

local player = Players.LocalPlayer
local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local Theme = require(Client.Ui.Theme)
local WorldMenuController = require(Client.Controllers.WorldMenuController)
local gui = player.PlayerGui
local BG = { background = "art/reference/lobby_map.png" }

local function check(cond, msg)
	print((cond and "  ok " or "  FAIL ") .. msg)
	if not cond then
		__failed = true
	end
end

player:SetAttribute("SessionState", "StagingLoading")
WorldMenuController.Start()
Theme.TopStack().Position = UDim2.new(0.5, 0, 0, 126)
local menu = gui:FindFirstChild("WorldMenu")
local play = menu:FindFirstChild("Play", true)
check(menu.Enabled, "the menu shows while loading")
check(play:GetAttribute("KitState") == "disabled", "Play is disabled while loading")
__dump(gui, W, H, BG)

player:SetAttribute("SessionState", "WorldMainMenuReady")
check(play:GetAttribute("KitState") == "normal", "Play unlocks when the server is ready")
__dump(gui, W, H, BG)

play:FindFirstChild("Hit").Activated:Fire()
check(calls[1] == "RequestPlay", "Play asks the server")
check(string.find(menu:FindFirstChild("Error", true).Text, "You are still safe") ~= nil, "a refusal says you are safe")
__dump(gui, W, H, BG)

player:SetAttribute("MaintenanceNotice", true)
check(string.find(menu:FindFirstChild("Error", true).Text, "Game update") ~= nil, "the game-update notice shows")
__dump(gui, W, H, BG)

play:SetAttribute("DebugState", "hover")
__dump(gui, W, H, BG)
play:SetAttribute("DebugState", "")

player:SetAttribute("SessionState", "ActiveRun")
check(not menu.Enabled, "the menu closes in the run")
check(gui:FindFirstChild("Transition", true).Visible, "the at-risk warning shows")
__dump(gui, W, H, BG)

print(__failed and "SCENE FAILED" or "SCENE OK")
if __failed then
	error("world menu failed")
end
