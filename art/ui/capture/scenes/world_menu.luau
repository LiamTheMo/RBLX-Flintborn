-- The protected world menu through the real WorldMenuController, its session
-- states set as the server sets them and its remotes mocked:
--
--   1 loading (Play disabled)    2 ready              3 Play pressed: the request
--   fails, the reason shows      4 game-update notice 5 Play hover
--   6 entering the world: the menu closes and the at-risk toast shows
--   then a 20× open / close leak check (instances and connections)
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

-- Leak check: the menu shown and closed 20 times (back to the menu, into the
-- run) leaves the PlayerGui's instances and the live connections as they were.
-- Leak check counts: the PlayerGui's instances, and the live connections on
-- every instance still in the game (a destroyed one drops out with its
-- connections, as in Roblox) plus those on the shared Core.Signal objects.
local leakCounts
do
	local SignalMeta = getmetatable(Instance.new("Frame"):GetPropertyChangedSignal("Name"))
	local CoreSignal = require(game:GetService("ReplicatedStorage").Shared.Core.Signal)
	local coreLive = setmetatable({}, { __mode = "k" })
	local connect = CoreSignal.Connect
	CoreSignal.Connect = function(signal, fn)
		local connection = connect(signal, fn)
		coreLive[connection] = true
		return connection
	end
	local ROOTS = {
		"Players",
		"UserInputService",
		"GuiService",
		"RunService",
		"Lighting",
		"ReplicatedStorage",
		"StarterPlayer",
		"SoundService",
		"ContextActionService",
		"SocialService",
		"TweenService",
	}
	function leakCounts(): (number, number)
		local count = 0
		local seen = {}
		local function signals(map)
			for _, value in map or {} do
				if type(value) == "table" and getmetatable(value) == SignalMeta then
					count += #value.handlers
				end
			end
		end
		local function visit(instance)
			if instance == nil or seen[instance] then
				return
			end
			seen[instance] = true
			signals(rawget(instance, "__props"))
			signals(rawget(instance, "__changed"))
			signals(rawget(instance, "__attrChanged"))
			for _, child in rawget(instance, "__children") or {} do
				visit(child)
			end
		end
		visit(game)
		visit(workspace)
		visit(workspace.CurrentCamera)
		for _, name in ROOTS do
			visit(game:GetService(name))
		end
		local player = game:GetService("Players").LocalPlayer
		visit(player)
		for connection in coreLive do
			if connection.Connected then
				count += 1
			end
		end
		return #player.PlayerGui:GetDescendants(), count
	end
end

local function cycle()
	player:SetAttribute("SessionState", "WorldMainMenuReady")
	player:SetAttribute("SessionState", "ActiveRun")
end
cycle()
local instances, connections = leakCounts()
for _ = 1, 20 do
	cycle()
end
local instancesAfter, connectionsAfter = leakCounts()
check(instancesAfter == instances, ("open/close ×20 leaves %d descendants (%d)"):format(instances, instancesAfter))
check(
	connectionsAfter == connections,
	("open/close ×20 leaves %d connections (%d)"):format(connections, connectionsAfter)
)

print(__failed and "SCENE FAILED" or "SCENE OK")
if __failed then
	error("world menu failed")
end
