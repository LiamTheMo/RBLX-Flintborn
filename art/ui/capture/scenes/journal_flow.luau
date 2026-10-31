-- Drives the Quest Journal through JournalController headlessly with real
-- events: open, choose quests, claim (refused, then paid), progress published
-- by the server, the side tabs (trophy, map, party), close, and an open/close
-- leak check. Rows, tabs and CLAIM are pressed through their kit controls;
-- remotes are mocked as vault_flow does. Pages: after the paid claim (toast
-- showing), the map tab, the trophy tab.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
workspace:SetAttribute("FlintbornPlaceRole", "Lobby")

local W, H = 1672, 941
local folder = Instance.new("Folder")
folder.Name = "FlintbornRemotes"
folder.Parent = ReplicatedStorage

local quests = {
	{
		id = "DailyGather",
		name = "Gather 100 times",
		tier = "Easy",
		action = "Harvest",
		coins = 250,
		count = 10,
		needed = 100,
		claimed = false,
		repeats = "Daily",
	},
	{
		id = "DailyExtract",
		name = "Extract once",
		tier = "Easy",
		action = "Extract",
		coins = 250,
		count = 1,
		needed = 1,
		claimed = false,
		repeats = "Daily",
	},
	{
		id = "FirstGuardian",
		name = "Defeat the Guardian",
		tier = "Hard",
		action = "Guardian",
		coins = 3000,
		gems = 50,
		count = 0,
		needed = 1,
		claimed = false,
		repeats = "Once",
	},
}
local snapshot = {
	level = 12,
	xp = 450,
	xpToNext = 750,
	masteries = { { track = "Mining", level = 3, xp = 120, nextXp = 300, nextReward = "Stonebreaker at level 5" } },
	titles = {},
	rebirth = { count = 0, tokens = 0 },
	premium = false,
	boosterUntil = 0,
}
local views, claims = 0, {}
local claimReply = { false, "AlreadyClaimed" }
local handlers = {
	QuestView = function()
		views += 1
		-- A copy, as the network delivers.
		local copy = {}
		for _, q in quests do
			table.insert(copy, table.clone(q))
		end
		return copy
	end,
	QuestClaim = function(id)
		table.insert(claims, id)
		if claimReply[1] then
			for _, q in quests do
				if q.id == id then
					q.claimed = true
				end
			end
		end
		return claimReply[1], claimReply[2]
	end,
	ProgressionSnapshot = function()
		return snapshot
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
local progressionChanged = Instance.new("RemoteEvent")
progressionChanged.Name = "ProgressionChanged"
progressionChanged.Parent = folder

local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local JournalController = require(Client.Controllers.JournalController)
local JournalWindow = require(Client.Hud.Screens.JournalWindow)
local player = Players.LocalPlayer

local function check(cond, msg)
	print((cond and "  ok " or "  FAIL ") .. msg)
	if not cond then
		__failed = true
	end
end

local function press(component)
	component.control:Activate()
end

local function place(window)
	window.screen.holder.Position =
		UDim2.fromOffset(300 - JournalWindow.MARGIN + JournalWindow.SIZE[1] / 2, 150 + 688 / 2)
	window.screen.scale.Scale = 1
end

local function dump()
	__dump(player.PlayerGui, W, H, { background = "art/reference/ui/lobby/01_hud.png" })
end

JournalController.Start()
local window = JournalController.Window()
local gui = player.PlayerGui:FindFirstChild("FlintbornJournal")
check(gui ~= nil and not gui.Enabled, "built closed")
check(views == 0, "nothing fetched before opening")

-- Open: one fetch, rows listed, the first quest chosen.
JournalController.Toggle()
place(window)
check(gui.Enabled and JournalController.IsOpen(), "Toggle opens the journal")
check(views == 1, "quests fetched once on open (no polling)")
check(window.rows.DailyGather ~= nil and window.rows.FirstGuardian ~= nil, "quests listed")
check(window:Selected() == "DailyGather", "first quest chosen")
check(window.claim.control:State() == "disabled", "CLAIM disabled while under way")
press(window.claim)
check(#claims == 0, "an unfinished quest cannot be claimed")

-- A finished quest: CLAIM enabled; the server refuses once, then pays.
press(window.rows.DailyExtract)
check(window:Selected() == "DailyExtract", "row press chooses the quest")
check(window.claim.control:State() == "normal", "CLAIM enabled when finished")
press(window.claim)
check(#claims == 1 and claims[1] == "DailyExtract", "claim sends the quest id")
local toasts = player.PlayerGui:FindFirstChild("KitToasts")
check(toasts ~= nil and #toasts:GetDescendants() > 0, "a refusal shows a toast")
check(window.claim.control:State() == "normal", "a refused claim leaves CLAIM enabled")
claimReply = { true }
local before = views
press(window.claim)
check(#claims == 2, "second claim sent")
check(window.claim.control:State() == "disabled", "CLAIMED after paying")
check(string.upper(window.claim.text) == "CLAIMED", "label reads CLAIMED")
check(views > before, "quests fetched again after a claim")
check(window.rows.DailyExtract.root:FindFirstChild("Claimed", true) ~= nil, "claimed row carries a check")
dump()

-- The server publishes progress: quests fetched again, trophy page updated.
before = views
snapshot.level = 13
progressionChanged.OnClientEvent:Fire(snapshot)
check(views == before + 1, "ProgressionChanged refreshes quests while open")

-- Side tabs.
press(window.tabs.map)
check(window:Tab() == "map" and window.mapFrame.Visible, "map tab shows the island map")
check(not window.entriesFrame.Visible, "map hides the quest list")
press(window.tabs.quests)
press(window.rows.FirstGuardian)
press(window.tabs.map)
check(window.map.selected == "KeepTower", "map points at the Guardian's place")
dump()
press(window.tabs.progress)
check(window:Tab() == "progress", "trophy tab")
check(window.rows.Level ~= nil and window.rows.MasteryMining ~= nil, "progression rows listed")
check(not window.claim.root.Visible, "no CLAIM on the trophy tab")
check(window.footerText.root.Text == "450 / 750 XP", "level bar shows the real fraction")
dump()

-- Party tab opens the Party window through PartyController.Open.
local partyOpened = 0
local okParty, PartyController = pcall(require, Client.Controllers.PartyController)
if okParty and type(PartyController) == "table" then
	PartyController.Open = function()
		partyOpened += 1
	end
	check(window.partyTab.control:State() ~= "disabled", "party tab enabled in the lobby")
	press(window.partyTab)
	check(partyOpened == 1, "party tab calls PartyController.Open")
	check(window:Tab() == "progress", "party tab does not switch the page")
else
	print("  (PartyController missing: party tab stays disabled)")
	check(window.partyTab.control:State() == "disabled", "party tab disabled without a Party window")
end

-- Close, and Open(tab).
JournalController.Toggle()
check(not JournalController.IsOpen(), "Toggle closes")
before = views
progressionChanged.OnClientEvent:Fire(snapshot)
check(views == before, "no fetch while closed")
JournalController.Open("map")
check(JournalController.IsOpen() and window:Tab() == "map", "Open(tab) opens on that tab")
JournalController.Close()

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

-- Leak check: twenty opens and closes leave the same instance and connection counts.
JournalController.Open("quests")
JournalController.Close()
local base, baseConnections = leakCounts()
for _ = 1, 20 do
	JournalController.Open("quests")
	JournalController.Close()
end
local after, afterConnections = leakCounts()
check(after == base, ("no instance leak over 20 opens (%d → %d)"):format(base, after))
check(
	afterConnections == baseConnections,
	("no connection leak over 20 opens (%d → %d)"):format(baseConnections, afterConnections)
)

print(__failed and "FLOW FAILED" or "FLOW OK")
if __failed then
	error("journal flow failed")
end
