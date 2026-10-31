-- Drives PlayController headlessly through LobbyController with mocked remotes:
-- open the window as a party leader, press PLAY, the deploy check lists the
-- loadout, ENTER deploys (busy while the server answers), the server refuses with
-- a reason shown under the map; then a member's disabled PLAY (only the leader
-- starts the run, D24), the close button, and an open/close leak check.
--
--   1 opened as leader   2 deploy check   3 deploying (busy)   4 deploy failed
--   5 member: PLAY disabled
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
workspace:SetAttribute("FlintbornPlaceRole", "Lobby")
workspace.CurrentCamera.ViewportSize = Vector2.new(1672, 941)

local W, H = 1672, 941
local player = Players.LocalPlayer
player:SetAttribute("Level", 12)
player:SetAttribute("SessionState", "LobbySafe")
for id, info in { [2] = { "ForestRanger", 15 }, [3] = { "StoneSeeker", 9 } } do
	local other = Instance.new("Player")
	other.Name = info[1]
	other.DisplayName = info[1]
	other.UserId = id
	other:SetAttribute("Level", info[2])
	other.Parent = Players
end

local folder = Instance.new("Folder")
folder.Name = "FlintbornRemotes"
folder.Parent = ReplicatedStorage
local calls = {}
local deployThread = nil
local preview = {
	{ catalogId = "StoneAxe", permanent = true },
	{ catalogId = "StoneSpear" },
	{ catalogId = "BasicMedicine", quantity = 3 },
	{ catalogId = "Wood", quantity = 40 },
}
local handlers = {
	DeployPreview = function()
		table.insert(calls, { "DeployPreview" })
		return preview
	end,
	Deploy = function()
		table.insert(calls, { "Deploy" })
		-- Answer later: the scene resumes this thread with the server's reply.
		deployThread = coroutine.running()
		return coroutine.yield()
	end,
	PartyAction = function(action, argument)
		table.insert(calls, { "PartyAction", action, argument })
		return true
	end,
}
for name, fn in handlers do
	local remote = Instance.new("RemoteFunction")
	remote.Name = name
	remote.Parent = folder
	remote.InvokeServer = function(_, ...)
		return fn(...)
	end
end
local partyChanged = Instance.new("RemoteEvent")
partyChanged.Name = "PartyChanged"
partyChanged.Parent = folder

local function check(cond, msg)
	print((cond and "  ok " or "  FAIL ") .. msg)
	if not cond then
		__failed = true
	end
end
local function last(kind)
	for i = #calls, 1, -1 do
		if calls[i][1] == kind then
			return calls[i]
		end
	end
	return nil
end
local function count(kind)
	local n = 0
	for _, call in calls do
		if call[1] == kind then
			n += 1
		end
	end
	return n
end
local function dump()
	__dump(player.PlayerGui, W, H, { background = "art/reference/ui/lobby/01_hud.png" })
end
local function press(root)
	for _, d in root:GetDescendants() do
		if d.Name == "Hit" and d:IsA("TextButton") then
			d.Activated:Fire()
			return true
		end
	end
	return false
end
local function texts(root)
	local list = {}
	for _, d in root:GetDescendants() do
		if d:IsA("TextLabel") then
			table.insert(list, d.Text)
		end
	end
	return table.concat(list, "\n")
end

local function party(leader)
	local members = {}
	for _, entry in { { 1, "LiamTheMo" }, { 2, "ForestRanger" }, { 3, "StoneSeeker" } } do
		table.insert(members, { userId = entry[1], name = entry[2] })
	end
	return {
		party = { id = "p1", leader = leader, createdAt = 0, members = members, invited = {} },
		invites = {},
		maxSize = 8,
	}
end

local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local LobbyController = require(Client.Controllers.LobbyController)
local PlayController = require(Client.Controllers.PlayController)
local PlayModel = require(ReplicatedStorage.Shared.UI.PlayModel)
LobbyController.Start()
PlayController.Start()
partyChanged.OnClientEvent:Fire(party(1))

-- 1. Open as the leader.
check(not PlayController.IsOpen(), "closed before the tile is pressed")
PlayController.Open()
check(PlayController.IsOpen(), "Open() shows the window")
local window = PlayController.Window()
local gui = player.PlayerGui:FindFirstChild("FlintbornPlay")
check(gui ~= nil and gui.Enabled, "the window's gui is enabled")
check(window.play.root.Visible and window.readyButton == nil, "the leader gets PLAY, and there is no Ready")
check(window.play.root:GetAttribute("KitState") == "normal", "PLAY can be pressed")
check(gui:FindFirstChild("Ready", true) == nil and gui:FindFirstChild("NotReady", true) == nil, "no ready dots")
check(gui:FindFirstChild("Tag", true) == nil, "no Leader tag")
check(#window.partyList:Content():GetChildren() >= 3, "three party rows")
local shown = texts(gui)
check(string.find(shown, "ForestRanger", 1, true) ~= nil, "member names come from the party view")
check(string.find(shown, "LV. 15", 1, true) ~= nil, "levels come from each player's Level attribute")
check(string.find(shown, "4 items, 3 at risk", 1, true) ~= nil, "Carrying reads the deploy preview")
check(window.slots[1].item and window.slots[1].item.itemId == "StoneAxe", "slot 1 holds the axe, as the run packs it")
check(window.slots[4].item == nil, "wood goes to the run backpack, not the hotbar")
check(string.find(shown, "+1 more in your backpack", 1, true) ~= nil, "the leftover is counted")
dump()

-- 2. PLAY reads the preview fresh and asks first.
local reads = count("DeployPreview")
window.play.control:Activate()
check(count("DeployPreview") == reads + 1, "PLAY reads the preview again")
local dialogGui = player.PlayerGui:FindFirstChild("KitDialog")
check(dialogGui ~= nil and dialogGui.Enabled, "the deploy check opens")
local dialogText = dialogGui and texts(dialogGui) or ""
check(string.find(dialogText, "TAKE THESE INTO THE RUN?", 1, true) ~= nil, "titled as before")
check(string.find(dialogText, "Stone Axe", 1, true) ~= nil, "lists the items")
check(string.find(dialogText, "Wood ×40", 1, true) ~= nil, "with quantities")
check(string.find(string.lower(dialogText), "ready", 1, true) == nil, "no ready count in the check")
check(count("Deploy") == 0, "nothing deploys before ENTER")
dump()

-- 3. ENTER deploys; the button is busy while the server answers.
local confirm = nil
for _, d in dialogGui:GetDescendants() do
	if d.Name == "Confirm" and d:GetAttribute("KitComponent") == "Button" then
		confirm = d
	end
end
check(confirm ~= nil and press(confirm), "ENTER pressed")
check(count("Deploy") == 1, "Deploy called once")
check(window.play.root:GetAttribute("KitState") == "busy", "PLAY is busy while deploying")
check(string.find(texts(gui), "Deploying", 1, true) ~= nil, "the status line says so")
window.play.control:Activate()
check(count("Deploy") == 1 and count("DeployPreview") == reads + 1, "a second press does nothing")
dump()

-- 4. The server refuses: the reason shows and PLAY comes back.
check(deployThread ~= nil, "the deploy is waiting on the server")
coroutine.resume(deployThread, false, "WorldLoading")
check(not LobbyController.IsDeploying(), "deploy finished")
check(window.play.root:GetAttribute("KitState") == "normal", "PLAY is pressable again")
check(
	string.find(texts(gui), "Deploy failed: the island is still being built", 1, true) ~= nil,
	"the failure reason shows under the map"
)
dump()

-- 5. A member who does not lead sees PLAY disabled and the leader caption.
local actions = count("PartyAction")
partyChanged.OnClientEvent:Fire(party(2))
check(window.play.root.Visible, "members still see PLAY")
check(window.play.root:GetAttribute("KitState") == "disabled", "but disabled")
check(string.find(texts(gui), PlayModel.MEMBER_CAPTION, 1, true) ~= nil, "caption: the leader starts the run")
window.play.control:Activate()
check(count("Deploy") == 1 and count("DeployPreview") == reads + 1, "PLAY does nothing for members")
check(count("PartyAction") == actions, "and nothing is sent to the party")
dump()
partyChanged.OnClientEvent:Fire(party(1))
check(window.play.root:GetAttribute("KitState") == "normal", "leading again enables PLAY")

-- Close with the ✕, then Toggle; open and close 20 times without growing.
press(window.close.root)
check(not PlayController.IsOpen(), "the close button closes it")
PlayController.Toggle()
check(PlayController.IsOpen(), "Toggle opens it again")
PlayController.Toggle()
check(not PlayController.IsOpen(), "Toggle closes it")
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

PlayController.Open()
PlayController.Toggle()
local before, beforeConnections = leakCounts()
for _ = 1, 20 do
	PlayController.Open()
	PlayController.Toggle()
end
local after, afterConnections = leakCounts()
check(after == before, ("no instance growth over 20 open/close cycles (%d → %d)"):format(before, after))
check(
	afterConnections == beforeConnections,
	("no connection growth over 20 open/close cycles (%d → %d)"):format(beforeConnections, afterConnections)
)
if __failed then
	error("play_flow checks failed")
end
