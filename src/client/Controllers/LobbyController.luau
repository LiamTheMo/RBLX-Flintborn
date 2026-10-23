-- Lobby screen: Deploy with a list of every item that will enter the run (GDD Q155),
-- and the party panel for invites (GDD Q161c). Lobby place only. Everything the
-- server needs is sent as intent through remotes; the server decides.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)

local LobbyController = {}

local player = Players.LocalPlayer
local partyView = { party = nil, invites = {} }
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
	ui.status.Text = text
end

local function refreshPreview()
	local ok, items = pcall(function()
		return Remotes.Get("DeployPreview"):InvokeServer()
	end)
	clear(ui.preview)
	if not ok then
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
	label("Items in your vault always stay safe.", ui.preview)
end

local function partyAction(action: string, argument)
	local ok, success, reason = pcall(function()
		return Remotes.Get("PartyAction"):InvokeServer(action, argument)
	end)
	if not ok or not success then
		setStatus("Party: " .. tostring(reason or "request failed"))
	end
end

local function refreshParty()
	clear(ui.party)
	local party = partyView.party
	if party then
		label("Your party (" .. #party.members .. "/8):", ui.party)
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
	local canInvite = party == nil or party.leader == player.UserId
	if canInvite then
		for _, other in Players:GetPlayers() do
			local inParty = false
			if party then
				for _, member in party.members do
					inParty = inParty or member.userId == other.UserId
				end
			end
			if other ~= player and not inParty then
				button("Invite " .. other.DisplayName, ui.party, function()
					partyAction("invite", other.UserId)
				end)
			end
		end
	end
end

local function deploy()
	setStatus("Deploying…")
	ui.deploy.Active = false
	local ok, success, reason = pcall(function()
		return Remotes.Get("Deploy"):InvokeServer()
	end)
	ui.deploy.Active = true
	if ok and success then
		setStatus("Travelling to a world…")
	else
		setStatus("Deploy failed: " .. tostring(reason or success) .. ". Nothing was lost.")
		refreshPreview()
	end
end

local function build()
	local gui = make("ScreenGui", { Name = "Lobby", ResetOnSpawn = false }, player:WaitForChild("PlayerGui"))
	local panel = make("Frame", {
		AnchorPoint = Vector2.new(1, 0.5),
		Position = UDim2.new(1, -16, 0.5, 0),
		Size = UDim2.fromOffset(300, 460),
		BackgroundColor3 = Color3.fromRGB(28, 24, 20),
		BackgroundTransparency = 0.1,
	}, gui)
	make("UICorner", { CornerRadius = UDim.new(0, 8) }, panel)
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

function LobbyController.Start()
	if not PlaceConfig.IsLobby() then
		return
	end
	build()
	refreshPreview()
	refreshParty()
	Remotes.Get("PartyChanged").OnClientEvent:Connect(function(view)
		partyView = view
		refreshParty()
	end)
	local function notice()
		if player:GetAttribute("MaintenanceNotice") then
			setStatus("Game update: your items were saved and return on your next Play.")
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
