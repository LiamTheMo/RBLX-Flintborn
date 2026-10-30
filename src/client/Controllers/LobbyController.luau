-- Lobby screen: Deploy with a list of every item that will enter the run (GDD Q155),
-- and the party panel for invites (GDD Q161c). Lobby place only. Everything the
-- server needs is sent as intent through remotes; the server decides.
--
-- With the lobby HUD (HudMode.ReplacesLobby) this keeps the logic and the HUD and
-- the Party and Play windows draw it: Deploy(), PartyAction() and its wrappers
-- (Invite, Accept, Decline, Leave, SetReady), PartyView(), IsReady(), IsInvited(),
-- Preview(), Invitable(), Status(), Changed and PartyChanged. Otherwise it also
-- builds its own panel.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local PartyRules = require(ReplicatedStorage.Shared.Admission.PartyRules)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Signal = require(ReplicatedStorage.Shared.Core.Signal)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local HudMode = require(script.Parent.Parent.Hud.HudMode)
local Reasons = require(script.Parent.Parent.Ui.Reasons)

local LobbyController = {}

-- Fires (what) when "party", "preview" or "status" changes.
LobbyController.Changed = Signal.new()
-- Fires (view) with each new party view from the server (see PartyView).
LobbyController.PartyChanged = Signal.new()

local player = Players.LocalPlayer
local partyView = { party = nil, invites = {}, ready = false, maxSize = PartyRules.MAX_SIZE }
-- The deploy preview: {catalogId, quantity, permanent}[] once read, or nil.
local previewItems = nil
local statusText = "You are safe in the lobby."
local deploying = false
local ui = {}

local function make(className: string, props, parent)
	local instance = Instance.new(className)
	for key, value in props do
		instance[key] = value
	end
	instance.Parent = parent
	return instance
end

local function button(text: string, parent, onClick)
	local b = make("TextButton", {
		Text = text,
		Size = UDim2.new(1, 0, 0, 36),
		BackgroundColor3 = Color3.fromRGB(92, 64, 40),
		TextColor3 = Color3.fromRGB(245, 236, 222),
		Font = Enum.Font.GothamBold,
		TextSize = 16,
		AutoButtonColor = true,
	}, parent)
	make("UICorner", { CornerRadius = UDim.new(0, 6) }, b)
	b.Activated:Connect(onClick)
	return b
end

local function label(text: string, parent, height: number?)
	return make("TextLabel", {
		Text = text,
		Size = UDim2.new(1, 0, 0, height or 22),
		BackgroundTransparency = 1,
		TextColor3 = Color3.fromRGB(240, 232, 220),
		TextXAlignment = Enum.TextXAlignment.Left,
		TextWrapped = true,
		Font = Enum.Font.Gotham,
		TextSize = 14,
	}, parent)
end

local function clear(container)
	for _, child in container:GetChildren() do
		if not child:IsA("UIListLayout") then
			child:Destroy()
		end
	end
end

local function setStatus(text: string)
	statusText = text
	if ui.status then
		ui.status.Text = text
	end
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
	if not ui.preview then
		return
	end
	clear(ui.preview)
	if not ok or type(items) ~= "table" then
		label("Could not read your backpack yet.", ui.preview)
		return
	end
	if #items == 0 then
		label("Nothing in your backpack will enter the run.", ui.preview)
	else
		label("⚠ These items go with you; all but ★ Permanent ones can be lost:", ui.preview)
		for _, item in items do
			local def = ItemCatalog.Get(item.catalogId)
			local name = def and def.name or tostring(item.catalogId)
			label(
				(item.permanent and "★ " or "• ") .. name .. (item.quantity and (" ×" .. item.quantity) or ""),
				ui.preview
			)
		end
	end
	label("Items in your vault always stay safe. Materials you bring never get the Center ×2.", ui.preview)
end

-- Coalesces refresh requests: one fetch at a time, never on the caller's thread,
-- with one more pass if something changed while a fetch was in flight.
local previewBusy, previewAgain = false, false
local function requestPreview()
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
	if not ui.party then
		return
	end
	clear(ui.party)
	local party = partyView.party
	if party then
		label("Your party (" .. #party.members .. "/" .. PartyRules.MAX_SIZE .. "):", ui.party)
		for _, member in party.members do
			label((member.userId == party.leader and "★ " or "• ") .. member.name, ui.party)
		end
		button("Leave party", ui.party, function()
			partyAction("leave")
		end)
	else
		label("You are not in a party.", ui.party)
	end
	for _, invite in partyView.invites do
		label("Invite from " .. invite.from, ui.party)
		button("Accept", ui.party, function()
			partyAction("accept", invite.partyId)
		end)
		button("Decline", ui.party, function()
			partyAction("decline", invite.partyId)
		end)
	end
	for _, other in invitable() do
		button("Invite " .. other.DisplayName, ui.party, function()
			partyAction("invite", other.UserId)
		end)
	end
end

local function deploy()
	if deploying then
		return
	end
	deploying = true
	setStatus("Deploying…")
	if ui.deploy then
		ui.deploy.Active = false
	end
	local ok, success, reason = pcall(function()
		return Remotes.Get("Deploy"):InvokeServer()
	end)
	deploying = false
	if ui.deploy then
		ui.deploy.Active = true
	end
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

-- "invite" + userId, "accept"/"decline" + partyId, "leave", or "ready" + bool.
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

-- Sets your own advisory ready flag (works without a party). The view updates
-- when the server confirms. Yields.
function LobbyController.SetReady(ready: boolean): (boolean, string?)
	return partyAction("ready", ready == true)
end

-- {
--   party = nil | {id, leader, createdAt (server os.time, or nil), members =
--     {{userId, name, ready}}, invited = {userId} (the leader's pending invites;
--     empty for other members)},
--   invites = {{partyId, from}} (invites waiting for you),
--   ready = boolean (yours, also when solo),
--   maxSize = 8,
-- }
function LobbyController.PartyView()
	return partyView
end

-- Whether `userId` (default: you) is ready. Only you and your party's members
-- are known; anyone else reads false.
function LobbyController.IsReady(userId: number?): boolean
	if userId == nil or userId == player.UserId then
		return partyView.ready == true
	end
	local party = partyView.party
	for _, member in party and party.members or {} do
		if member.userId == userId then
			return member.ready == true
		end
	end
	return false
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

local function build()
	local gui = make("ScreenGui", { Name = "Lobby", ResetOnSpawn = false }, player:WaitForChild("PlayerGui"))
	-- Left of the navigation bar (140 px on the right edge), below the wallet and
	-- code box, and never taller than the screen so Deploy stays on-screen.
	local panel = make("Frame", {
		AnchorPoint = Vector2.new(1, 1),
		Position = UDim2.new(1, -164, 1, -12),
		Size = UDim2.new(0, 300, 1, -100),
		BackgroundColor3 = Color3.fromRGB(28, 24, 20),
		BackgroundTransparency = 0.1,
		Active = true,
	}, gui)
	make("UICorner", { CornerRadius = UDim.new(0, 8) }, panel)
	make("UISizeConstraint", { MaxSize = Vector2.new(300, 460) }, panel)
	make("UIPadding", {
		PaddingTop = UDim.new(0, 12),
		PaddingBottom = UDim.new(0, 12),
		PaddingLeft = UDim.new(0, 12),
		PaddingRight = UDim.new(0, 12),
	}, panel)
	local scroll = make("ScrollingFrame", {
		Size = UDim2.fromScale(1, 1),
		BackgroundTransparency = 1,
		AutomaticCanvasSize = Enum.AutomaticSize.Y,
		CanvasSize = UDim2.new(),
		ScrollBarThickness = 6,
	}, panel)
	make("UIListLayout", { Padding = UDim.new(0, 6), SortOrder = Enum.SortOrder.LayoutOrder }, scroll)

	make("TextLabel", {
		Text = "FLINTBORN",
		Size = UDim2.new(1, 0, 0, 32),
		BackgroundTransparency = 1,
		TextColor3 = Color3.fromRGB(255, 214, 150),
		Font = Enum.Font.GothamBlack,
		TextSize = 24,
		LayoutOrder = 1,
	}, scroll)
	ui.deploy = button("Deploy", scroll, deploy)
	ui.deploy.LayoutOrder = 2
	ui.status = label("You are safe in the lobby.", scroll, 36)
	ui.status.LayoutOrder = 3
	ui.preview = make("Frame", {
		Size = UDim2.new(1, 0, 0, 0),
		AutomaticSize = Enum.AutomaticSize.Y,
		BackgroundTransparency = 1,
		LayoutOrder = 4,
	}, scroll)
	make("UIListLayout", { Padding = UDim.new(0, 2) }, ui.preview)
	ui.party = make("Frame", {
		Size = UDim2.new(1, 0, 0, 0),
		AutomaticSize = Enum.AutomaticSize.Y,
		BackgroundTransparency = 1,
		LayoutOrder = 5,
	}, scroll)
	make("UIListLayout", { Padding = UDim.new(0, 4) }, ui.party)
end

-- Builds the older lobby panel after the lobby HUD failed to start, so Deploy and
-- the party stay reachable.
function LobbyController.BuildFallback()
	if ui.status == nil and PlaceConfig.IsLobby() then
		build()
		ui.status.Text = statusText
		refreshParty()
		requestPreview()
	end
end

function LobbyController.Start()
	if not PlaceConfig.IsLobby() then
		return
	end
	if not HudMode.ReplacesLobby() then
		build()
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
	-- Never block later controllers' Start on a server round trip. The profile may
	-- still be loading now, and every vault, shop or trade change marks a save, so
	-- the save status changing is the cue to re-read; a slow timer backs it up.
	requestPreview()
	player:GetAttributeChangedSignal("SaveStatus"):Connect(requestPreview)
	task.spawn(function()
		while true do
			task.wait(LobbyController.PREVIEW_REFRESH_SECONDS)
			requestPreview()
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
