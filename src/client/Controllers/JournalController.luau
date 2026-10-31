-- The Quest Journal (GDD §10.1, §25; docs/ui/JournalScreen.md): quests with their
-- progress and rewards, a read-only view of progression, and the painted island
-- map (Hud/Screens/JournalWindow). The lobby's Quests tile opens it.
--
-- Quests come from the QuestView remote when the Journal opens, and again
-- whenever the server publishes progress (ProgressionChanged follows every
-- verified action and every claim) and at the daily reset; nothing polls. CLAIM
-- pays a finished quest through QuestClaim. The trophy tab draws
-- ProgressionController's snapshot; the party tab opens the Party window.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local JournalModel = require(ReplicatedStorage.Shared.UI.JournalModel)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Kit = require(script.Parent.Parent.Hud.Kit)
local JournalWindow = require(script.Parent.Parent.Hud.Screens.JournalWindow)
local Reasons = require(script.Parent.Parent.Ui.Reasons)

local JournalController = {}

-- Seconds after midnight UTC before the daily quests are fetched again.
JournalController.RESET_MARGIN = 2

local player = Players.LocalPlayer
local window = nil
local quests = nil
local progress = nil
local claiming: string? = nil
-- Bumped on every open and close, so replies and timers from an earlier
-- opening drop out.
local session = 0
local fetching = false
local fetchAgain = false

local function invoke(name: string, ...)
	local ok, a, b = pcall(function(...)
		return Remotes.Get(name):InvokeServer(...)
	end, ...)
	if not ok then
		return nil, "Request failed"
	end
	return a, b
end

local function now(): number
	local ok, t = pcall(function()
		return workspace:GetServerTimeNow()
	end)
	return if ok and type(t) == "number" and t > 0 then t else os.time()
end

-- The progression controller, when it is in this build (read only).
local function progression()
	local module = script.Parent:FindFirstChild("ProgressionController")
	if module == nil then
		return nil
	end
	local ok, controller = pcall(require, module)
	return if ok and type(controller) == "table" then controller else nil
end

-- The Party window's controller (lobby only), required when the party tab is
-- pressed so the two controllers never require each other while loading.
local function partyController()
	local module = script.Parent:FindFirstChild("PartyController")
	if module == nil then
		return nil
	end
	local ok, controller = pcall(require, module)
	if ok and type(controller) == "table" and type(controller.Open) == "function" then
		return controller
	end
	return nil
end

local function drawQuests()
	if window then
		window:SetPage("quests", JournalModel.QuestPage(quests, now(), claiming))
	end
end

local function drawProgress()
	if window then
		window:SetPage("progress", JournalModel.ProgressPage(progress))
	end
end

-- Fetches the quests; a request made while one is on its way runs after it.
local function refresh()
	if fetching then
		fetchAgain = true
		return
	end
	fetching = true
	repeat
		fetchAgain = false
		local token = session
		local list = invoke("QuestView")
		if token == session and type(list) == "table" then
			quests = list
			drawQuests()
		end
	until not fetchAgain or not JournalController.IsOpen()
	fetching = false
end

-- While open, the daily line ("Resets in …") stays true: redraw at each whole
-- hour and fetch again just after midnight UTC, when daily quests reset.
local function scheduleClock(token: number)
	local t = now()
	local toReset = JournalModel.SecondsToReset(t)
	local toHour = 3600 - (math.floor(t) % 3600)
	local wait = math.min(toReset + JournalController.RESET_MARGIN, toHour)
	task.delay(wait, function()
		if token ~= session then
			return
		end
		if toReset <= toHour then
			task.spawn(refresh)
		else
			drawQuests()
		end
		scheduleClock(token)
	end)
end

local function claim(questId: string)
	if claiming then
		return
	end
	local quest = nil
	for _, entry in quests or {} do
		if entry.id == questId then
			quest = entry
		end
	end
	if quest == nil or JournalModel.Status(quest) ~= "ready" then
		return
	end
	claiming = questId
	drawQuests()
	local ok, reason = invoke("QuestClaim", questId)
	-- Always released, even if the Journal closed meanwhile.
	claiming = nil
	if ok then
		quest.claimed = true
		Kit.Toast.Show({ kind = "quest", title = "Reward Claimed", text = quest.name })
	else
		Kit.Toast.Show({
			kind = "warn",
			title = "Not Claimed",
			text = JournalModel.CLAIM_REASONS[reason] or Reasons.Text(reason),
		})
	end
	drawQuests()
	refresh()
end

local function onOpened()
	session += 1
	local token = session
	local controller = progression()
	if progress == nil and controller and type(controller.View) == "function" then
		progress = controller.View()
	end
	drawQuests()
	drawProgress()
	scheduleClock(token)
	task.spawn(refresh)
	if progress == nil then
		task.spawn(function()
			local snapshot = invoke("ProgressionSnapshot")
			if token == session and type(snapshot) == "table" and progress == nil then
				progress = snapshot
				drawProgress()
			end
		end)
	end
end

function JournalController.IsOpen(): boolean
	return window ~= nil and window.screen:IsOpen()
end

-- Opens the Journal on `tab` ("quests" | "progress" | "map"; default: the tab it
-- showed last). Opening it again only switches the tab.
function JournalController.Open(tab: string?)
	if window == nil then
		return
	end
	if tab and tab ~= "party" then
		window:SelectTab(tab)
	end
	if not window.screen:IsOpen() then
		window.screen:Open(Kit.Input.IsGamepad())
	end
end

function JournalController.Close()
	if window then
		window.screen:Close()
	end
end

function JournalController.Toggle()
	if JournalController.IsOpen() then
		JournalController.Close()
	else
		JournalController.Open()
	end
end

-- The window the controller draws (scenes and verifiers).
function JournalController.Window()
	return window
end

function JournalController.Start()
	window = JournalWindow.new(player:WaitForChild("PlayerGui"), {
		onClaim = function(questId: string)
			task.spawn(claim, questId)
		end,
		onParty = function()
			local party = partyController()
			if party == nil then
				return
			end
			local ok, err = pcall(party.Open)
			if not ok then
				warn("[Journal] the Party window did not open: " .. tostring(err))
			end
		end,
	})
	window:SetPartyAvailable(PlaceConfig.IsLobby() and script.Parent:FindFirstChild("PartyController") ~= nil)
	window.screen:Watch()
	window.screen.Opened:Connect(onOpened)
	window.screen.Closed:Connect(function()
		session += 1
	end)
	-- Every verified action and every claim publishes progress: the trophy tab
	-- redraws and, while open, the quests are fetched again.
	Remotes.Get("ProgressionChanged").OnClientEvent:Connect(function(snapshot)
		if type(snapshot) == "table" then
			progress = snapshot
			drawProgress()
		end
		if JournalController.IsOpen() then
			task.spawn(refresh)
		end
	end)
end

return JournalController
