-- Lobby screen: Deploy with a list of every item that will enter the run (GDD Q155),
-- and the party panel for invites (GDD Q161c). Lobby place only. Everything the
-- server needs is sent as intent through remotes; the server decides.
--
-- This keeps the logic; the lobby HUD and the Party and Play windows draw it:
-- Deploy(), PartyAction() and its wrappers (Invite, Accept, Decline, Leave),
-- PartyView(), IsInvited(), Preview(), Invitable(), Status(), Changed and
-- PartyChanged.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local PartyRules = require(ReplicatedStorage.Shared.Admission.PartyRules)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Signal = require(ReplicatedStorage.Shared.Core.Signal)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Reasons = require(script.Parent.Parent.Ui.Reasons)

local LobbyController = {}

-- Fires (what) when "party", "preview" or "status" changes.
LobbyController.Changed = Signal.new()
-- Fires (view) with each new party view from the server (see PartyView).
LobbyController.PartyChanged = Signal.new()

local player = Players.LocalPlayer
local partyView = { party = nil, invites = {}, maxSize = PartyRules.MAX_SIZE }
-- The deploy preview: {catalogId, quantity, permanent}[] once read, or nil.
local previewItems = nil
local statusText = "You are safe in the lobby."
local deploying = false

local function setStatus(text: string)
	statusText = text
	LobbyController.Changed:Fire("status")
end

local function refreshPreview()
	local ok, items = pcall(function()
		return Remotes.Get("DeployPreview"):InvokeServer()
	end)
	-- A guarded remote answers `false, reason` when rate-limited or not loaded.
	if ok and type(items) == "table" then
		previewItems = items
		LobbyController.Changed:Fire("preview")
	end
end

-- Coalesces refresh requests: one fetch at a time, never on the caller's thread,
-- with one more pass if something changed while a fetch was in flight.
local previewBusy, previewAgain = false, false
-- When the preview was last asked for (os.clock): the backup timer re-reads it
-- only once that is PREVIEW_REFRESH_SECONDS old.
local previewAskedAt = -math.huge

local function requestPreview()
	previewAskedAt = os.clock()
	if previewBusy then
		previewAgain = true
		return
	end
	previewBusy = true
	task.spawn(function()
		repeat
			previewAgain = false
			refreshPreview()
		until not previewAgain
		previewBusy = false
	end)
end

LobbyController.PREVIEW_REFRESH_SECONDS = 30
-- Tries for the party view on start (PartyAction "view").
LobbyController.VIEW_ATTEMPTS = 3
LobbyController.MAINTENANCE_TEXT = "Game update: your items were saved and return on your next Play."

-- Returns (success, reason?) as the server answered.
local function partyAction(action: string, argument): (boolean, string?)
	local ok, success, reason = pcall(function()
		return Remotes.Get("PartyAction"):InvokeServer(action, argument)
	end)
	if not ok or not success then
		reason = if ok then reason else nil
		setStatus("Party: " .. Reasons.Text(reason or "request failed"))
		return false, if type(reason) == "string" then reason else "RequestFailed"
	end
	return true, nil
end

-- Players in this lobby server you may invite: everyone outside your party, when
-- you lead it or have none.
local function invitable(): { Player }
	local party = partyView.party
	if party ~= nil and party.leader ~= player.UserId then
		return {}
	end
	local list = {}
	for _, other in Players:GetPlayers() do
		local inParty = false
		if party then
			for _, member in party.members do
				inParty = inParty or member.userId == other.UserId
			end
		end
		if other ~= player and not inParty then
			table.insert(list, other)
		end
	end
	return list
end

local function refreshParty()
	LobbyController.Changed:Fire("party")
end

local function deploy()
	if deploying then
		return
	end
	deploying = true
	setStatus("Deploying…")
	local ok, success, reason = pcall(function()
		return Remotes.Get("Deploy"):InvokeServer()
	end)
	deploying = false
	if ok and success then
		setStatus("Travelling to a world…")
	else
		setStatus("Deploy failed: " .. Reasons.Text(reason or success) .. ". Nothing was lost.")
		requestPreview()
	end
end

-- Asks the server to deploy (the party leader takes the whole party). Yields.
-- Progress and failures are reported through Status() and Changed("status").
function LobbyController.Deploy()
	deploy()
end

function LobbyController.IsDeploying(): boolean
	return deploying
end

-- "invite" + userId, "accept"/"decline" + partyId, or "leave".
-- Yields; returns (success, reason?). A failure also shows in Status().
function LobbyController.PartyAction(action: string, argument: any?): (boolean, string?)
	return partyAction(action, argument)
end

function LobbyController.Invite(userId: number): (boolean, string?)
	return partyAction("invite", userId)
end

function LobbyController.Accept(partyId: string): (boolean, string?)
	return partyAction("accept", partyId)
end

function LobbyController.Decline(partyId: string): (boolean, string?)
	return partyAction("decline", partyId)
end

function LobbyController.Leave(): (boolean, string?)
	return partyAction("leave")
end

-- {
--   party = nil | {id, leader, createdAt (server os.time, or nil), members =
--     {{userId, name}}, invited = {userId} (the leader's pending invites;
--     empty for other members)},
--   invites = {{partyId, from, fromUserId}} (invites waiting for you; from is
--     the inviting leader's display name),
--   maxSize = 8,
-- }
function LobbyController.PartyView()
	return partyView
end

-- True while your party has an unanswered invite out to `userId` (leader only).
function LobbyController.IsInvited(userId: number): boolean
	local party = partyView.party
	return party ~= nil and table.find(party.invited or {}, userId) ~= nil
end

function LobbyController.Invitable(): { Player }
	return invitable()
end

-- The items that will enter the run ({catalogId, quantity, permanent}[]), or nil
-- until the first read; RefreshPreview() asks again.
function LobbyController.Preview()
	return previewItems
end

function LobbyController.RefreshPreview()
	requestPreview()
end

-- Reads the deploy preview now (yields) and returns it, or nil when the server
-- could not answer; the lobby HUD asks this when Enter is pressed (GDD Q155).
function LobbyController.FetchPreview()
	local ok, items = pcall(function()
		return Remotes.Get("DeployPreview"):InvokeServer()
	end)
	if ok and type(items) == "table" then
		previewItems = items
		LobbyController.Changed:Fire("preview")
		return items
	end
	return nil
end

function LobbyController.Status(): string
	return statusText
end

function LobbyController.Start()
	if not PlaceConfig.IsLobby() then
		return
	end
	Remotes.Get("PartyChanged").OnClientEvent:Connect(function(view)
		if type(view) ~= "table" then
			return
		end
		partyView = view
		partyView.invites = partyView.invites or {}
		partyView.maxSize = partyView.maxSize or PartyRules.MAX_SIZE
		LobbyController.PartyChanged:Fire(partyView)
		refreshParty()
	end)
	refreshParty()
	-- Ask for the party view now that the listener is connected: the one the
	-- server sent on join may have arrived first. Quiet (no status line), and
	-- retried a few times if the server is busy or still starting.
	task.spawn(function()
		for attempt = 1, LobbyController.VIEW_ATTEMPTS do
			local ok, success = pcall(function()
				return Remotes.Get("PartyAction"):InvokeServer("view")
			end)
			if ok and success then
				return
			end
			task.wait(attempt)
		end
	end)
	-- Never block later controllers' Start on a server round trip. The profile may
	-- still be loading now, and every vault, shop or trade change marks a save, so
	-- the save status changing is the cue to re-read; a slow timer backs it up,
	-- asking only when no other read has happened for PREVIEW_REFRESH_SECONDS
	-- (so the preview is never older than that, without extra round trips).
	requestPreview()
	player:GetAttributeChangedSignal("SaveStatus"):Connect(requestPreview)
	task.spawn(function()
		while true do
			local due = previewAskedAt + LobbyController.PREVIEW_REFRESH_SECONDS - os.clock()
			if due > 0 then
				task.wait(due)
			else
				requestPreview()
			end
		end
	end)
	local function notice()
		if player:GetAttribute("MaintenanceNotice") then
			setStatus(LobbyController.MAINTENANCE_TEXT)
		end
	end
	player:GetAttributeChangedSignal("MaintenanceNotice"):Connect(notice)
	notice()
	Players.PlayerAdded:Connect(refreshParty)
	Players.PlayerRemoving:Connect(function()
		task.defer(refreshParty)
	end)
end

return LobbyController
