-- The Play window (ARCHITECTURE §4.5, docs/ui/PlayScreen.md): how players deploy
-- from the lobby. It replaces the lobby's old Enter button, its server dropdown
-- (there is no server choice, D7) and the deploy check that went with them.
--
-- PLAY reads the deploy preview fresh and, when anything goes with you (or the
-- party is not all ready), lists it in a Kit.ConfirmDialog before deploying (GDD
-- Q155); with nothing to point out it deploys straight away. Solo players and
-- party leaders press PLAY; other members get a Ready toggle instead, since only
-- the leader deploys (D16) and Ready is advisory (D3). Everything goes through
-- LobbyController (Deploy, FetchPreview) and PartyController (SetReady, which
-- owns the pending ready state for every screen); the server decides.
--
-- Contract (§4.9): Open(), Toggle(), IsOpen(). Lobby place only, with the lobby
-- HUD in charge (HudMode.ReplacesLobby); otherwise LobbyController's own panel
-- deploys.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local SessionStates = require(ReplicatedStorage.Shared.Admission.SessionStates)
local PlayModel = require(ReplicatedStorage.Shared.UI.PlayModel)
local LobbyController = require(script.Parent.LobbyController)
local PartyController = require(script.Parent.PartyController)
local Hud = script.Parent.Parent.Hud
local HudMode = require(Hud.HudMode)
local Kit = require(Hud.Kit)
local PlayWindow = require(Hud.Screens.PlayWindow)

local PlayController = {}

-- How long a status message stays under the map.
PlayController.STATUS_SECONDS = 6
-- The deploy check's size; long item lists scroll.
PlayController.DIALOG_SIZE = { 600, 470 }

local player = Players.LocalPlayer
local started = false
local window = nil
local dialog = nil
-- A message showing under the map (nil: the idle line) and its token.
local statusText: string? = nil
local statusToken = 0
-- Reading the preview for PLAY (a ready toggle in flight is PartyController's).
local entering = false
-- The role the window was last drawn for: a new role drops the last message.
local shownRole: string? = nil
-- Level attribute watchers for the party's players, by userId.
local levelWatch: { [number]: RBXScriptConnection } = {}

local function me()
	return { userId = player.UserId, name = player.DisplayName }
end

local function role(): string
	return PlayModel.Role(LobbyController.PartyView(), player.UserId)
end

local function playerOf(userId: number): Player?
	return Players:GetPlayerByUserId(userId)
end

local function levelOf(userId: number): number?
	local other = playerOf(userId)
	local level = other and other:GetAttribute("Level")
	return if type(level) == "number" then level else nil
end

-- After a successful deploy the server holds the player for the teleport.
local function travelling(): boolean
	return player:GetAttribute("SessionState") == SessionStates.TeleportPending
end

-- The line under the map between messages: the game-update notice while it
-- applies, or a member's reminder that the leader starts the run.
local function idleLine(): string?
	if player:GetAttribute("MaintenanceNotice") then
		return LobbyController.MAINTENANCE_TEXT
	end
	if role() == "member" then
		return if PartyController.ShownReady() then PlayModel.MEMBER_READY_CAPTION else PlayModel.MEMBER_CAPTION
	end
	return nil
end

local function refreshStatus()
	if window then
		window:SetStatus(statusText or idleLine())
	end
end

local function showStatus(text: string)
	statusToken += 1
	local token = statusToken
	statusText = text
	refreshStatus()
	task.delay(PlayController.STATUS_SECONDS, function()
		if token == statusToken and not LobbyController.IsDeploying() then
			statusText = nil
			refreshStatus()
		end
	end)
end

local function refreshButton()
	if window == nil then
		return
	end
	local deploying = LobbyController.IsDeploying()
	local current = role()
	if current ~= shownRole then
		shownRole = current
		statusText = nil
		statusToken += 1
	end
	window:SetMode(current, PartyController.ShownReady())
	window:SetBusy(entering or PartyController.ReadyPending() ~= nil or deploying)
	-- Once the server is teleporting the player there is nothing left to press.
	window:SetEnabled(not (travelling() and not deploying and not entering))
end

local function watchLevels(rows)
	local wanted = {}
	for _, row in rows do
		wanted[row.userId] = true
	end
	for userId, connection in levelWatch do
		if not wanted[userId] then
			connection:Disconnect()
			levelWatch[userId] = nil
		end
	end
	for userId in wanted do
		local other = playerOf(userId)
		if levelWatch[userId] == nil and other then
			levelWatch[userId] = other:GetAttributeChangedSignal("Level"):Connect(function()
				PlayController.RefreshParty()
			end)
		end
	end
end

-- Party rows: leader first, each with the player's Level attribute (set by
-- ProgressionService.Publish) and, in a party, their ready dot.
function PlayController.RefreshParty()
	if window == nil then
		return
	end
	local view = LobbyController.PartyView()
	local rows = PlayModel.Members(view, me())
	for _, row in rows do
		row.level = levelOf(row.userId)
	end
	watchLevels(rows)
	window:SetParty(rows, view.party ~= nil)
end

-- The run hotbar and the detail rows from the latest deploy preview.
local function refreshLoadout()
	if window == nil then
		return
	end
	local preview = LobbyController.Preview()
	local hotbar, more = PlayModel.LoadoutHotbar(preview)
	window:SetLoadout(hotbar, more)
	local rows = PlayModel.WorldRows()
	table.insert(rows, PlayModel.CarryingRow(preview))
	window:SetDetails(rows)
end

local function refreshAll()
	PlayController.RefreshParty()
	refreshLoadout()
	refreshButton()
	refreshStatus()
end

local function closeDialog()
	if dialog then
		dialog.Close()
		dialog = nil
	end
end

local function deploy()
	closeDialog()
	if LobbyController.IsDeploying() then
		return
	end
	task.spawn(function()
		LobbyController.Deploy()
		refreshButton()
	end)
	refreshButton()
end

-- The deploy check's body: one line per item (scrolling when long), then the
-- notes (what can be lost, the vault, the ready count).
local function buildCheck(check)
	return function(body: Frame, w: number, h: number)
		local noteH = 0
		local notes = {}
		for _, note in check.notes do
			if note then
				table.insert(notes, note)
			end
		end
		local lineH = 22
		local function noteHeight(text: string): number
			local lines = math.ceil(Kit.Text.Width(text, "body") / (w - 8))
			return math.max(1, lines) * lineH + 4
		end
		for _, note in notes do
			noteH += noteHeight(note)
		end
		local listH = h - noteH - 8
		if #check.lines > 0 then
			local list = Kit.Scroll.new(body, {
				name = "Items",
				rect = { 0, 0, w, listH },
				gap = 2,
				padBottom = 4,
				contentHeight = #check.lines * (lineH + 2),
				zIndex = 7,
			})
			for index, line in check.lines do
				Kit.Text.new(list:Content(), {
					name = "Item" .. index,
					size = { w - 30, lineH },
					layoutOrder = index,
					text = line,
					role = "value",
					zIndex = 8,
				})
			end
		end
		local y = if #check.lines > 0 then listH + 8 else (h - noteH) / 2
		for index, note in notes do
			local nh = noteHeight(note)
			Kit.Text.new(body, {
				name = "Note" .. index,
				rect = { 0, y, w, nh },
				text = note,
				role = "body",
				align = "Center",
				wrap = true,
				zIndex = 7,
			})
			y += nh
		end
	end
end

local function showCheck(check)
	closeDialog()
	dialog = Kit.ConfirmDialog.Show({
		title = check.title,
		build = buildCheck(check),
		confirmLabel = check.confirmLabel,
		cancelLabel = "Cancel",
		size = PlayController.DIALOG_SIZE,
		onConfirm = function()
			dialog = nil
			deploy()
		end,
		onCancel = function()
			dialog = nil
		end,
	})
end

-- PLAY: read the preview fresh, then ask first or deploy (GDD Q155).
local function onPlay()
	if entering or LobbyController.IsDeploying() or role() == "member" then
		return
	end
	entering = true
	refreshButton()
	task.spawn(function()
		local items = LobbyController.FetchPreview()
		entering = false
		refreshButton()
		if window == nil or not window:IsOpen() then
			return
		end
		local ready, total = PlayModel.ReadyCounts(LobbyController.PartyView(), me())
		local check = PlayModel.DeployCheck(items, PlayModel.ReadyNote(ready, total), ready >= total)
		if check == nil then
			deploy()
		else
			showCheck(check)
		end
	end)
end

-- The member's Ready toggle; the view updates when the server confirms. A
-- refusal shows under the map (LobbyController's status line), not as a toast.
local function onReady()
	if PartyController.ReadyPending() ~= nil then
		return
	end
	PartyController.SetReady(not PartyController.ShownReady(), function() end)
end

local function build()
	window = PlayWindow.new({
		onPlay = onPlay,
		onReady = onReady,
		onClose = closeDialog,
	})
	window.screen:Watch()
end

-- Opens the Play window (the HUD's Play tile). A gamepad lands on PLAY.
function PlayController.Open()
	if not started then
		return
	end
	if window == nil then
		local ok, err = pcall(build)
		if not ok then
			warn("[Play] failed to build the Play window: " .. tostring(err))
			window = nil
			return
		end
	end
	refreshAll()
	window:Open(Kit.Input.IsGamepad())
	-- The backpack may have changed since the last read.
	LobbyController.RefreshPreview()
end

function PlayController.Toggle()
	if PlayController.IsOpen() then
		window:Close()
	else
		PlayController.Open()
	end
end

function PlayController.IsOpen(): boolean
	return window ~= nil and window:IsOpen()
end

-- The window object, for capture scenes and verifiers (nil until first opened).
function PlayController.Window()
	return window
end

function PlayController.Start()
	if not HudMode.ReplacesLobby() then
		return
	end
	started = true
	-- The shared ready state settles on the party view PartyController watches.
	PartyController.Start()
	LobbyController.Changed:Connect(function(what)
		if what == "party" then
			PlayController.RefreshParty()
			refreshButton()
			refreshStatus()
		elseif what == "preview" then
			refreshLoadout()
		elseif what == "status" then
			refreshButton()
			if window then
				showStatus(LobbyController.Status())
			end
		end
	end)
	-- A ready toggle starting or ending (from any screen).
	PartyController.Changed:Connect(function()
		refreshButton()
		refreshStatus()
	end)
	player:GetAttributeChangedSignal("MaintenanceNotice"):Connect(refreshStatus)
	player:GetAttributeChangedSignal("SessionState"):Connect(refreshButton)
end

return PlayController
