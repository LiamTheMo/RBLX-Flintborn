-- The protected world main menu (GDD §31.3, §31.6). Shown on every world arrival
-- while the server loads; Play unlocks only when the server says the player is
-- ready, and the screen says plainly when items become at risk. World place only.

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local SessionStates = require(ReplicatedStorage.Shared.Admission.SessionStates)
local Theme = require(script.Parent.Parent.Ui.Theme)

local WorldMenuController = {}

local STATE_ATTRIBUTE = "SessionState"
local TRANSITION_SECONDS = 3

local player = Players.LocalPlayer
local ui = {}

local STATUS_TEXT = {
	StagingLoading = "Loading your data and the world…",
	WorldMainMenuReady = "Ready. Press Play to enter the world.",
	PlayRequested = "Entering the world…",
}

local function make(className: string, props, parent)
	local instance = Instance.new(className)
	for key, value in props do
		instance[key] = value
	end
	instance.Parent = parent
	return instance
end

local function refresh()
	local state = player:GetAttribute(STATE_ATTRIBUTE)
	ui.menu.Visible = SessionStates.ShowsWorldMenu(state)
	ui.status.Text = STATUS_TEXT[state] or ""
	if player:GetAttribute("MaintenanceNotice") then
		ui.error.Text = "Game update: your items were saved and return when you press Play."
	end
	local ready = state == SessionStates.WorldMainMenuReady
	ui.play.Active = ready
	ui.play.AutoButtonColor = ready
	ui.play.Text = ready and "PLAY" or "Loading…"
	ui.play.BackgroundTransparency = ready and 0 or 0.5
	if state == SessionStates.ActiveRun then
		ui.transition.Visible = true
		task.delay(TRANSITION_SECONDS, function()
			ui.transition.Visible = false
		end)
	end
end

local function play()
	if player:GetAttribute(STATE_ATTRIBUTE) ~= SessionStates.WorldMainMenuReady then
		return
	end
	local requestId = HttpService:GenerateGUID(false)
	ui.play.Active = false
	local ok, success, reason = pcall(function()
		return Remotes.Get("RequestPlay"):InvokeServer(requestId)
	end)
	if not ok or not success then
		ui.error.Text = "Could not enter the world ("
			.. tostring(reason or success)
			.. "). You are still safe — try again."
	else
		ui.error.Text = ""
	end
	refresh()
end

local function returnToLobby()
	ui.error.Text = "Returning to the lobby…"
	local ok, success, reason = pcall(function()
		return Remotes.Get("ReturnToLobby"):InvokeServer()
	end)
	if not ok or not success then
		ui.error.Text = "Could not return to the lobby (" .. tostring(reason or success) .. "). You are still safe."
	end
end

local function build()
	local gui = make("ScreenGui", {
		Name = "WorldMenu",
		ResetOnSpawn = false,
		IgnoreGuiInset = true,
		DisplayOrder = 20,
	}, player:WaitForChild("PlayerGui"))

	ui.menu = make("Frame", {
		Size = UDim2.fromScale(1, 1),
		BackgroundColor3 = Color3.fromRGB(18, 15, 12),
		Active = true,
	}, gui)
	local column = make("Frame", {
		AnchorPoint = Vector2.new(0.5, 0.5),
		Position = UDim2.fromScale(0.5, 0.5),
		Size = UDim2.fromOffset(420, 360),
		BackgroundTransparency = 1,
	}, ui.menu)
	make("UIListLayout", {
		Padding = UDim.new(0, 12),
		HorizontalAlignment = Enum.HorizontalAlignment.Center,
		SortOrder = Enum.SortOrder.LayoutOrder,
	}, column)
	make("TextLabel", {
		Text = "FLINTBORN",
		Size = UDim2.new(1, 0, 0, 56),
		BackgroundTransparency = 1,
		TextColor3 = Color3.fromRGB(255, 214, 150),
		Font = Enum.Font.GothamBlack,
		TextSize = 44,
		LayoutOrder = 1,
	}, column)
	make("TextLabel", {
		Text = "You are safe until you enter the world.",
		Size = UDim2.new(1, 0, 0, 24),
		BackgroundTransparency = 1,
		TextColor3 = Color3.fromRGB(200, 230, 200),
		Font = Enum.Font.GothamMedium,
		TextSize = 18,
		LayoutOrder = 2,
	}, column)
	ui.status = make("TextLabel", {
		Size = UDim2.new(1, 0, 0, 24),
		BackgroundTransparency = 1,
		TextColor3 = Color3.fromRGB(235, 228, 216),
		Font = Enum.Font.Gotham,
		TextSize = 16,
		LayoutOrder = 3,
	}, column)
	ui.play = make("TextButton", {
		Size = UDim2.fromOffset(260, 64),
		BackgroundColor3 = Color3.fromRGB(150, 84, 36),
		TextColor3 = Color3.fromRGB(255, 245, 230),
		Font = Enum.Font.GothamBlack,
		TextSize = 28,
		LayoutOrder = 4,
	}, column)
	make("UICorner", { CornerRadius = UDim.new(0, 10) }, ui.play)
	ui.play.Activated:Connect(play)
	local back = make("TextButton", {
		Text = "Return to lobby",
		Size = UDim2.fromOffset(260, 40),
		BackgroundColor3 = Color3.fromRGB(60, 52, 44),
		TextColor3 = Color3.fromRGB(235, 228, 216),
		Font = Enum.Font.GothamMedium,
		TextSize = 16,
		LayoutOrder = 5,
	}, column)
	make("UICorner", { CornerRadius = UDim.new(0, 8) }, back)
	back.Activated:Connect(returnToLobby)
	ui.error = make("TextLabel", {
		Text = "",
		Size = UDim2.new(1, 0, 0, 44),
		BackgroundTransparency = 1,
		TextColor3 = Color3.fromRGB(255, 190, 150),
		TextWrapped = true,
		Font = Enum.Font.Gotham,
		TextSize = 14,
		LayoutOrder = 6,
	}, column)

	-- In the shared top-centre column with the other banners.
	ui.transition = make("TextLabel", {
		Text = "⚠ Entering world — items are now at risk",
		Size = UDim2.fromOffset(460, 44),
		LayoutOrder = Theme.TopOrder.Transition,
		BackgroundColor3 = Color3.fromRGB(120, 40, 30),
		TextColor3 = Color3.fromRGB(255, 240, 230),
		Font = Enum.Font.GothamBold,
		TextSize = 18,
		Visible = false,
	}, Theme.TopStack())
	make("UICorner", { CornerRadius = UDim.new(0, 8) }, ui.transition)
end

function WorldMenuController.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	build()
	player:GetAttributeChangedSignal(STATE_ATTRIBUTE):Connect(refresh)
	player:GetAttributeChangedSignal("MaintenanceNotice"):Connect(refresh)
	refresh()
end

return WorldMenuController
