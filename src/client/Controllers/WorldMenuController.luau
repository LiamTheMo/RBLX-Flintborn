-- The protected world main menu (GDD §31.3, §31.6). Shown on every world arrival
-- while the server loads; Play unlocks only when the server says the player is
-- ready, and the screen says plainly when items become at risk. World place only.
-- A kit window (no close: the menu leaves only through Play or the lobby) over a
-- dark backdrop that hides the world while it loads; the warning when items
-- become at risk is a kit toast in the shared top-centre column.

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local SessionStates = require(ReplicatedStorage.Shared.Admission.SessionStates)
local Kit = require(script.Parent.Parent.Hud.Kit)
local Theme = require(script.Parent.Parent.Ui.Theme)
local Reasons = require(script.Parent.Parent.Ui.Reasons)

local WorldMenuController = {}

local STATE_ATTRIBUTE = "SessionState"
local TRANSITION_SECONDS = 3

WorldMenuController.SIZE = { 640, 500 }

local player = Players.LocalPlayer
local ui = {}

local STATUS_TEXT = {
	StagingLoading = "Loading your data and the world…",
	WorldMainMenuReady = "Ready. Press Play to enter the world.",
	PlayRequested = "Entering the world…",
}

local function setError(text: string)
	ui.error:SetText(text)
end

local function refresh()
	local state = player:GetAttribute(STATE_ATTRIBUTE)
	ui.gui.Enabled = SessionStates.ShowsWorldMenu(state)
	ui.status:SetText(STATUS_TEXT[state] or "")
	if player:GetAttribute("MaintenanceNotice") then
		setError("Game update: your items were saved and return when you press Play.")
	end
	local ready = state == SessionStates.WorldMainMenuReady
	if not ui.requesting then
		ui.play:SetBusy(false)
		ui.play:SetEnabled(ready)
	end
	ui.play:SetLabel(if ready then "Play" else "Loading…")
	if state == SessionStates.ActiveRun then
		ui.transition.root.Visible = true
		task.delay(TRANSITION_SECONDS, function()
			ui.transition.root.Visible = false
		end)
	end
end

local function play()
	if player:GetAttribute(STATE_ATTRIBUTE) ~= SessionStates.WorldMainMenuReady then
		return
	end
	if ui.requesting then
		return
	end
	local requestId = HttpService:GenerateGUID(false)
	ui.requesting = true
	ui.play:SetBusy(true)
	local ok, success, reason = pcall(function()
		return Remotes.Get("RequestPlay"):InvokeServer(requestId)
	end)
	ui.requesting = false
	if not ok or not success then
		setError(
			"Could not enter the world (" .. Reasons.Text(reason or success) .. "). You are still safe — try again."
		)
	else
		setError("")
	end
	refresh()
end

local function returnToLobby()
	setError("Returning to the lobby…")
	local ok, success, reason = pcall(function()
		return Remotes.Get("ReturnToLobby"):InvokeServer()
	end)
	if not ok or not success then
		setError("Could not return to the lobby (" .. tostring(reason or success) .. "). You are still safe.")
	end
end

local function build()
	local w, h = WorldMenuController.SIZE[1], WorldMenuController.SIZE[2]
	local gui = Theme.Make("ScreenGui", {
		Name = "WorldMenu",
		ResetOnSpawn = false,
		IgnoreGuiInset = true,
		DisplayOrder = Kit.Tokens.Order("window"),
		ZIndexBehavior = Enum.ZIndexBehavior.Sibling,
	}, player:WaitForChild("PlayerGui"))
	gui:SetAttribute("FitsItself", true)
	ui.gui = gui
	-- The backdrop: the kit's veil colour, solid, so the loading world stays hidden.
	Theme.Make("Frame", {
		Name = "Backdrop",
		Active = true,
		BackgroundColor3 = (Kit.Tokens.Veil()),
		BorderSizePixel = 0,
		Position = UDim2.fromOffset(-400, -400),
		Size = UDim2.new(1, 800, 1, 800),
		ZIndex = 0,
	}, gui)
	local holder = Theme.Make("Frame", {
		Name = "Holder",
		AnchorPoint = Vector2.new(0.5, 0.5),
		BackgroundTransparency = 1,
		Position = UDim2.fromScale(0.5, 0.5),
		Size = UDim2.fromOffset(w, h),
		ZIndex = 1,
	}, gui)
	ui.holder = holder
	local fit = Theme.Make("UIScale", { Name = "Fit" }, holder)
	local function apply()
		local size = gui.AbsoluteSize
		if size.X <= 0 or size.Y <= 0 then
			local camera = workspace.CurrentCamera
			if camera == nil then
				return
			end
			size = camera.ViewportSize
		end
		local k, centre =
			Kit.Scale.WindowFit(size.X, size.Y, Kit.Scale.WindowTop(gui), w, h, player:GetAttribute("UiScale"))
		fit.Scale = k
		holder.Position = UDim2.fromOffset(centre.X, centre.Y)
	end
	gui:GetPropertyChangedSignal("AbsoluteSize"):Connect(apply)
	player:GetAttributeChangedSignal("UiScale"):Connect(apply)
	apply()

	local window = Kit.Window.new(holder, {
		name = "Menu",
		rect = { 0, 0, w, h },
		title = "Flintborn",
		header = "centered",
		showClose = false,
	})
	local body = window:Body()
	local bw = window.bodyRect[3]
	Kit.Text.new(body, {
		name = "Safe",
		rect = { 0, 6, bw, 34 },
		text = "You are safe until you enter the world.",
		role = "itemTitle",
		textSize = 24,
		align = "Center",
		scaled = true,
	})
	ui.status = Kit.Text.new(body, {
		name = "Status",
		rect = { 0, 46, bw, 26 },
		text = "",
		role = "bodySoft",
		textSize = 18,
		align = "Center",
	})
	local buttonW = 340
	ui.play = Kit.Button.new(body, {
		name = "Play",
		rect = { (bw - buttonW) / 2, 96, buttonW, 76 },
		label = "Play",
		icon = "play",
		variant = "play",
		sizeClass = "l",
		onPress = play,
	})
	Kit.Button.new(body, {
		name = "ReturnToLobby",
		rect = { (bw - buttonW) / 2, 188, buttonW, 58 },
		label = "Return to lobby",
		variant = "secondary",
		textRole = "buttonS",
		textSize = 22,
		onPress = returnToLobby,
	})
	ui.error = Kit.Text.new(body, {
		name = "Error",
		rect = { 10, 262, bw - 20, 64 },
		text = "",
		role = "body",
		textSize = 16,
		color = "short",
		align = "Center",
		yAlign = "Top",
		wrap = true,
	})

	-- In the shared top-centre column with the other banners.
	ui.transition = Kit.Toast.new(Theme.TopStack(), {
		name = "Transition",
		size = { 520, 84 },
		layoutOrder = Theme.TopOrder.Transition,
		kind = "warn",
		icon = "warning",
		title = "Entering world",
		text = "Items are now at risk",
		visible = false,
		onClose = function()
			ui.transition.root.Visible = false
		end,
	})
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
