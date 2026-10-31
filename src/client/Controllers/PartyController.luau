-- The Party window (docs/ui/PartyScreen.md, ARCHITECTURE §4.4): lobby only.
-- Builds Hud/Screens/PartyWindow on first open and feeds it from the real
-- party system: LobbyController's party view (PartyChanged), the players in
-- this server and their Level attributes. Every action goes to the server
-- through LobbyController (PartyAction: invite, accept, decline, leave,
-- ready), which validates it; the window only shows what the server answered.
--
-- Contract (ARCHITECTURE §4.9): Open(section?), Toggle(), IsOpen().
--   section "invite" starts gamepad selection on the invite list (the HUD's
--   add-player button), nil on your Ready toggle.
--
-- Nothing polls: the window redraws on PartyChanged, players joining or
-- leaving, a Level change, a search, or an answer to a request. The only timer
-- is the "Created" clock, which ticks once a minute while the window is open.
--
-- This is the one place that sends ready toggles and invite answers and keeps
-- their pending state (the HUD and the Play window call SetReady / Answer and
-- read ReadyPending / ShownReady / AnswerBusy; Changed fires when it moves).
-- A refusal is reported once: here as a toast (or by the caller when it asks
-- for `quiet`), while Reporting() tells the HUD not to toast the same
-- LobbyController status line again.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local SocialService = game:GetService("SocialService")

local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Signal = require(ReplicatedStorage.Shared.Core.Signal)
local PartyModel = require(ReplicatedStorage.Shared.UI.PartyModel)
local LobbyController = require(script.Parent.LobbyController)
local Hud = script.Parent.Parent.Hud
local Kit = require(Hud.Kit)
local PartyWindow = require(Hud.Screens.PartyWindow)

local PartyController = {}

-- Fires when a ready toggle or an invite answer starts or ends.
PartyController.Changed = Signal.new()

PartyController.CLOCK_SECONDS = 60
-- A ready request whose view never arrives stops waiting after this long.
PartyController.READY_TIMEOUT = 8

local player = Players.LocalPlayer
local window = nil
local started = false
local query = ""
-- Requests on their way to the server.
local pendingInvites: { [number]: boolean } = {}
local busyInvites: { [string]: boolean } = {}
local readyPending: boolean? = nil
local readyToken = 0
local leaveBusy = false
-- Requests in flight whose refusal this module reports itself.
local reporting = 0
local friendsAllowed = false
local friendsChecked = false
local clockToken = 0
local levelWatch: { [Player]: RBXScriptConnection } = {}

local function now(): number
	return workspace:GetServerTimeNow()
end

-- Each player's Level attribute, where it is set.
local function levels(): { [number]: number }
	local map = {}
	for _, other in Players:GetPlayers() do
		local level = other:GetAttribute("Level")
		if type(level) == "number" then
			map[other.UserId] = level
		end
	end
	return map
end

local function candidates(): { PartyModel.Candidate }
	local list = {}
	for _, other in LobbyController.Invitable() do
		table.insert(list, { userId = other.UserId, name = other.DisplayName, userName = other.Name })
	end
	return list
end

local function data()
	local view = LobbyController.PartyView()
	return PartyModel.WindowData(view, { userId = player.UserId, name = player.DisplayName }, candidates(), {
		query = query,
		now = now(),
		levels = levels(),
		pendingInvites = pendingInvites,
		busyInvites = busyInvites,
		readyPending = readyPending,
		leaveBusy = leaveBusy,
		friends = friendsAllowed,
	})
end

local function refresh()
	if window and window:IsOpen() then
		window:SetData(data())
	end
end

local function failed(reason: string?)
	Kit.Toast.Show({ kind = "warn", title = "Party", text = PartyModel.ReasonText(reason) })
end

-- Runs a LobbyController party request (yields) while Reporting() is true.
local function request(fn, ...): (boolean, string?)
	reporting += 1
	local ok, okOrErr, reason = pcall(fn, ...)
	reporting -= 1
	if not ok then
		return false, "RequestFailed"
	end
	return okOrErr, reason
end

local function changed()
	refresh()
	PartyController.Changed:Fire()
end

local function invite(userId: number)
	if pendingInvites[userId] then
		return
	end
	pendingInvites[userId] = true
	refresh()
	task.spawn(function()
		local ok, reason = request(LobbyController.Invite, userId)
		pendingInvites[userId] = nil
		if not ok then
			failed(reason)
		end
		refresh()
	end)
end

local function answer(partyId: string, accept: boolean)
	if busyInvites[partyId] then
		return
	end
	busyInvites[partyId] = true
	changed()
	task.spawn(function()
		local ok, reason = request(if accept then LobbyController.Accept else LobbyController.Decline, partyId)
		busyInvites[partyId] = nil
		if not ok then
			failed(reason)
		end
		changed()
	end)
end

-- Asks for your ready flag; `onFailed(reason)` replaces the toast (the Play
-- window shows refusals under its map instead).
local function setReady(ready: boolean, onFailed: ((string?) -> ())?)
	if readyPending ~= nil then
		return
	end
	readyPending = ready
	readyToken += 1
	local token = readyToken
	changed()
	task.spawn(function()
		local ok, reason = request(LobbyController.SetReady, ready)
		if token ~= readyToken then
			return
		end
		if not ok then
			readyPending = nil
			if onFailed then
				onFailed(reason)
			else
				failed(reason)
			end
		elseif PartyModel.ReadySettled(LobbyController.PartyView(), readyPending) then
			readyPending = nil
		end
		changed()
	end)
	-- The server's view normally lands before the answer; never wait forever.
	task.delay(PartyController.READY_TIMEOUT, function()
		if token == readyToken and readyPending ~= nil then
			readyPending = nil
			changed()
		end
	end)
end

local function leave()
	if leaveBusy then
		return
	end
	Kit.ConfirmDialog.Show({
		title = "Leave the party?",
		text = "You will play solo until someone invites you again.",
		confirmLabel = "Leave",
		danger = true,
		onConfirm = function()
			leaveBusy = true
			refresh()
			task.spawn(function()
				local ok, reason = request(LobbyController.Leave)
				leaveBusy = false
				if not ok then
					failed(reason)
				end
				refresh()
			end)
		end,
	})
end

local function inviteFriends()
	pcall(function()
		SocialService:PromptGameInvite(player)
	end)
end

-- Whether this player may send Roblox game invites (checked once; yields).
local function checkFriends()
	if friendsChecked then
		return
	end
	friendsChecked = true
	task.spawn(function()
		local ok, allowed = pcall(function()
			return SocialService:CanSendGameInviteAsync(player)
		end)
		friendsAllowed = ok and allowed == true
		if friendsAllowed then
			refresh()
		end
	end)
end

-- The "Created" value, once a minute while open.
local function startClock()
	clockToken += 1
	local token = clockToken
	local function tick()
		if token ~= clockToken or window == nil or not window:IsOpen() then
			return
		end
		local party = LobbyController.PartyView().party
		window:SetCreated(PartyModel.RelativeTime(party and party.createdAt, now()))
		task.delay(PartyController.CLOCK_SECONDS, tick)
	end
	task.delay(PartyController.CLOCK_SECONDS, tick)
end

local function ensureWindow()
	if window == nil then
		window = PartyWindow.new({
			onInvite = invite,
			onAccept = function(partyId)
				answer(partyId, true)
			end,
			onDecline = function(partyId)
				answer(partyId, false)
			end,
			onLeave = leave,
			onReady = function(ready: boolean)
				setReady(ready)
			end,
			onInviteFriends = inviteFriends,
			onSearch = function(text)
				query = text
				refresh()
			end,
			onClosed = function()
				clockToken += 1
			end,
			parent = player:FindFirstChildOfClass("PlayerGui"),
		})
	end
	return window
end

local function onView(view)
	if readyPending ~= nil and PartyModel.ReadySettled(view, readyPending) then
		readyPending = nil
		changed()
		return
	end
	refresh()
end

local function watchLevel(other: Player)
	if levelWatch[other] == nil then
		levelWatch[other] = other:GetAttributeChangedSignal("Level"):Connect(refresh)
	end
end

-- Sets your advisory ready flag through the server (one request at a time;
-- the HUD, the Party window and the Play window share it). `onFailed(reason)`
-- reports a refusal instead of the toast.
function PartyController.SetReady(ready: boolean, onFailed: ((string?) -> ())?)
	setReady(ready, onFailed)
end

-- Accepts or declines an invite (one answer per invite at a time).
function PartyController.Answer(partyId: string, accept: boolean)
	answer(partyId, accept)
end

-- The ready value on its way to the server, or nil.
function PartyController.ReadyPending(): boolean?
	return readyPending
end

-- Your ready flag as the screens show it: the asked value while it is on its
-- way, else the server's.
function PartyController.ShownReady(): boolean
	if readyPending ~= nil then
		return readyPending
	end
	return LobbyController.IsReady()
end

-- The invites whose answer is on its way ({[partyId] = true}).
function PartyController.AnswerBusy(): { [string]: boolean }
	return busyInvites
end

-- True while a party request this module reports on is in flight (the HUD
-- skips the LobbyController status toast for it).
function PartyController.Reporting(): boolean
	return reporting > 0
end

-- Opens the Party window (lobby only). `section` "invite" puts gamepad
-- selection on the invite list.
function PartyController.Open(section: string?)
	if not PlaceConfig.IsLobby() then
		return
	end
	PartyController.Start()
	local w = ensureWindow()
	checkFriends()
	local wasOpen = w:IsOpen()
	-- Drawn before it opens, so the section's control exists to select.
	w:SetData(data())
	w:Open(section, Kit.Input.IsGamepad())
	if not wasOpen then
		startClock()
	end
end

function PartyController.Close()
	if window then
		window:Close()
	end
end

function PartyController.Toggle()
	if PartyController.IsOpen() then
		PartyController.Close()
	else
		PartyController.Open()
	end
end

function PartyController.IsOpen(): boolean
	return window ~= nil and window:IsOpen()
end

-- The window object, for capture scenes and verifiers (nil until first open).
function PartyController.Window()
	return window
end

function PartyController.Start()
	if started or not PlaceConfig.IsLobby() then
		return
	end
	started = true
	LobbyController.PartyChanged:Connect(onView)
	for _, other in Players:GetPlayers() do
		watchLevel(other)
	end
	Players.PlayerAdded:Connect(function(other)
		watchLevel(other)
		refresh()
	end)
	Players.PlayerRemoving:Connect(function(other)
		local connection = levelWatch[other]
		if connection then
			connection:Disconnect()
			levelWatch[other] = nil
		end
		pendingInvites[other.UserId] = nil
		-- LobbyController's own list drops them after this event.
		task.defer(refresh)
	end)
end

return PartyController
