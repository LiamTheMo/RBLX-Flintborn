-- Settings (GDD §25, §11, §46): UI scale, colour-blind palette, reduced motion,
-- subtitles for alert sounds, replaying the tutorial, and keyboard controls. The
-- Settings key (O by default) or the ⚙ button opens it; choices save to the
-- profile and apply everywhere at once. To rebind, click an action and press the
-- new key (Esc cancels); a key another action uses swaps with it.

local ContextActionService = game:GetService("ContextActionService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local Rarity = require(ReplicatedStorage.Shared.Items.Rarity)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Keybinds = require(ReplicatedStorage.Shared.Settings.Keybinds)
local Binds = require(script.Parent.Parent.Ui.Binds)
local Theme = require(script.Parent.Parent.Ui.Theme)

local SettingsController = {}

local player = Players.LocalPlayer
local playerGui = player:WaitForChild("PlayerGui")
local ui = {}
local defaultRarity = table.clone(Rarity.Colors)
-- The action waiting for its new key, and a note shown under Controls.
local capturing = nil
local controlsNote = ""

local CAPTURE_ACTION = "FlintbornKeyCapture"

local make = Theme.Make

-- Small screens (phones are about 360 px tall) shrink the whole UI so fixed-size
-- panels and their close buttons stay on-screen; the user's choice multiplies it.
SettingsController.DESIGN_HEIGHT = 600

local function viewportFactor(): number
	local camera = workspace.CurrentCamera
	if camera == nil or camera.ViewportSize.Y <= 1 then
		return 1
	end
	return math.min(1, camera.ViewportSize.Y / SettingsController.DESIGN_HEIGHT)
end

-- Roblox's own touch controls (thumbstick, jump and action buttons) live in
-- PlayerGui too; they size themselves for the screen and must not shrink. The
-- in-world HUD fits itself to the screen and applies UiScale on its own.
local UNSCALED = { TouchGui = true, FlintbornHud = true, FlintbornHudOverlay = true }

local function applyScale()
	local scale = (player:GetAttribute("UiScale") or 1) * viewportFactor()
	for _, gui in playerGui:GetChildren() do
		if gui:IsA("ScreenGui") and not UNSCALED[gui.Name] then
			local uiScale = gui:FindFirstChild("FlintbornScale") or make("UIScale", { Name = "FlintbornScale" }, gui)
			uiScale.Scale = scale
		end
	end
end

local function applyPalette()
	local palette = if player:GetAttribute("ColourBlind") then Theme.ColourBlindRarity else defaultRarity
	for name, color in palette do
		Rarity.Colors[name] = color
	end
end

local function save(changes)
	local settings = {
		uiScale = player:GetAttribute("UiScale") or 1,
		colourBlindMode = player:GetAttribute("ColourBlind") == true,
		reducedMotion = player:GetAttribute("ReducedMotion") == true,
		subtitles = player:GetAttribute("Subtitles") ~= false,
	}
	for key, value in changes do
		settings[key] = value
	end
	Remotes.Get("SaveSettings"):FireServer(settings)
end

local render

local function stopCapture()
	capturing = nil
	ContextActionService:UnbindAction(CAPTURE_ACTION)
end

local function saveKeys(overrides)
	Remotes.Get("SaveKeybinds"):FireServer(overrides)
end

-- Waits for the next key for action `id`. Bound above every game action and sunk,
-- so pressing (say) Tab here rebinds instead of opening the backpack.
local function startCapture(id: string)
	stopCapture()
	capturing = id
	controlsNote = ""
	ContextActionService:BindActionAtPriority(CAPTURE_ACTION, function(_, state, input)
		if state ~= Enum.UserInputState.Begin then
			return Enum.ContextActionResult.Sink
		end
		local key = input.KeyCode.Name
		if input.KeyCode == Enum.KeyCode.Escape then
			controlsNote = ""
		elseif Keybinds.IsAllowed(key) then
			local overrides = Keybinds.Assign(Binds.Overrides(), id, key)
			if overrides then
				saveKeys(overrides)
				controlsNote = ("%s → %s"):format(Keybinds.Get(id).label, Keybinds.Display(key))
			end
		else
			controlsNote = ("%s is reserved (movement, chat or menus)."):format(Keybinds.Display(key))
		end
		stopCapture()
		render()
		return Enum.ContextActionResult.Sink
	end, false, Enum.ContextActionPriority.High.Value + 100, Enum.UserInputType.Keyboard)
	render()
end

function render()
	for _, child in ui.list:GetChildren() do
		if not child:IsA("UIListLayout") then
			child:Destroy()
		end
	end
	local order = 0
	local function nextOrder(): number
		order += 1
		return order
	end
	local function row(text: string, onClick, height: number?)
		local b = make("TextButton", {
			Text = text,
			Size = UDim2.new(1, -8, 0, height or Theme.TOUCH_TARGET),
			BackgroundColor3 = Theme.Colors.Button,
			TextColor3 = Theme.Colors.Text,
			Font = Theme.Fonts.Bold,
			TextSize = Theme.TextSize.Body,
			LayoutOrder = nextOrder(),
		}, ui.list)
		make("UICorner", { CornerRadius = UDim.new(0, 6) }, b)
		b.Activated:Connect(function()
			onClick()
			task.delay(0.3, render)
		end)
		return b
	end
	local function heading(text: string)
		make("TextLabel", {
			Text = text,
			Size = UDim2.new(1, -8, 0, 22),
			BackgroundTransparency = 1,
			TextXAlignment = Enum.TextXAlignment.Left,
			TextWrapped = true,
			TextColor3 = Theme.Colors.Heading,
			Font = Theme.Fonts.Bold,
			TextSize = Theme.TextSize.Heading,
			LayoutOrder = nextOrder(),
		}, ui.list)
	end
	local scale = player:GetAttribute("UiScale") or 1
	row(("UI scale: %.1f×  (tap to cycle)"):format(scale), function()
		local nextScale = scale + 0.1
		save({ uiScale = if nextScale > 1.4 + 1e-6 then 0.8 else nextScale })
	end)
	local function toggle(label: string, attribute: string, key: string, default: boolean)
		local value = player:GetAttribute(attribute)
		if value == nil then
			value = default
		end
		row(("%s: %s"):format(label, if value then "ON" else "OFF"), function()
			save({ [key] = not value })
		end)
	end
	toggle("Colour-blind palette", "ColourBlind", "colourBlindMode", false)
	toggle("Reduced motion", "ReducedMotion", "reducedMotion", false)
	toggle("Subtitles for alert sounds", "Subtitles", "subtitles", true)
	row("Replay the tutorial", function()
		pcall(function()
			Remotes.Get("TutorialAction"):InvokeServer("Replay")
		end)
	end)
	-- Keyboard controls: only meaningful with a keyboard attached.
	if not UserInputService.KeyboardEnabled then
		return
	end
	heading("Controls — click an action, then press a key")
	if controlsNote ~= "" then
		heading(controlsNote)
	end
	local keys = Binds.Map()
	for _, action in Keybinds.Actions do
		local text = if capturing == action.id
			then ("%s: press a key… (Esc cancels)"):format(action.label)
			else ("%s: %s"):format(action.label, Keybinds.Display(keys[action.id]))
		local b = row(text, function()
			startCapture(action.id)
		end, 30)
		b.TextXAlignment = Enum.TextXAlignment.Left
		b.TextSize = Theme.TextSize.Small
		make("UIPadding", { PaddingLeft = UDim.new(0, 8) }, b)
	end
	row("Reset controls to defaults", function()
		stopCapture()
		controlsNote = "Controls reset to defaults."
		saveKeys({})
	end)
end

local function build()
	local gui = make("ScreenGui", { Name = "Settings", ResetOnSpawn = false, DisplayOrder = 20 }, playerGui)
	ui.panel = make("Frame", {
		AnchorPoint = Vector2.new(0.5, 0.5),
		Position = UDim2.fromScale(0.5, 0.5),
		Size = UDim2.fromOffset(380, 440),
		BackgroundColor3 = Theme.Colors.Panel,
		Active = true,
		Visible = false,
	}, gui)
	make("UICorner", { CornerRadius = UDim.new(0, 8) }, ui.panel)
	make("TextLabel", {
		Text = "Settings",
		Position = UDim2.fromOffset(12, 6),
		Size = UDim2.new(1, -50, 0, 26),
		BackgroundTransparency = 1,
		TextXAlignment = Enum.TextXAlignment.Left,
		TextColor3 = Theme.Colors.Heading,
		Font = Theme.Fonts.Title,
		TextSize = Theme.TextSize.Title,
	}, ui.panel)
	local close = make("TextButton", {
		Text = "✕",
		AnchorPoint = Vector2.new(1, 0),
		Position = UDim2.new(1, -6, 0, 6),
		Size = UDim2.fromOffset(32, 28),
		BackgroundColor3 = Theme.Colors.ButtonDisabled,
		TextColor3 = Theme.Colors.Text,
		Font = Theme.Fonts.Bold,
		TextSize = 14,
	}, ui.panel)
	close.Activated:Connect(function()
		ui.panel.Visible = false
		stopCapture()
	end)
	-- Scrolls: the controls list is longer than the panel.
	ui.list = make("ScrollingFrame", {
		Position = UDim2.fromOffset(12, 40),
		Size = UDim2.new(1, -24, 1, -50),
		BackgroundTransparency = 1,
		BorderSizePixel = 0,
		ScrollBarThickness = 6,
		CanvasSize = UDim2.new(),
		AutomaticCanvasSize = Enum.AutomaticSize.Y,
		ScrollingDirection = Enum.ScrollingDirection.Y,
	}, ui.panel)
	make("UIListLayout", { Padding = UDim.new(0, 6), SortOrder = Enum.SortOrder.LayoutOrder }, ui.list)
	-- A small always-visible button, so touch players can reach settings too.
	local open = make("TextButton", {
		Text = "⚙",
		AnchorPoint = Vector2.new(1, 1),
		Position = UDim2.new(1, -12, 1, -12),
		Size = UDim2.fromOffset(Theme.TOUCH_TARGET, Theme.TOUCH_TARGET),
		BackgroundColor3 = Theme.Colors.Panel,
		BackgroundTransparency = 0.2,
		TextColor3 = Theme.Colors.Heading,
		Font = Theme.Fonts.Bold,
		TextSize = 22,
	}, gui)
	make("UICorner", { CornerRadius = UDim.new(0.5, 0) }, open)
	open.Activated:Connect(function()
		SettingsController.Toggle()
	end)
end

-- Opens or closes this panel (keys, and the on-screen navigation bar).
function SettingsController.Toggle()
	ui.panel.Visible = not ui.panel.Visible
	stopCapture()
	if ui.panel.Visible then
		render()
	end
end

function SettingsController.Start()
	build()
	applyScale()
	applyPalette()
	playerGui.ChildAdded:Connect(function(child)
		if child:IsA("ScreenGui") then
			task.defer(applyScale)
		end
	end)
	player:GetAttributeChangedSignal("UiScale"):Connect(applyScale)
	local viewportConnection = nil
	local function watchCamera()
		if viewportConnection then
			viewportConnection:Disconnect()
			viewportConnection = nil
		end
		local camera = workspace.CurrentCamera
		if camera then
			viewportConnection = camera:GetPropertyChangedSignal("ViewportSize"):Connect(applyScale)
		end
		applyScale()
	end
	workspace:GetPropertyChangedSignal("CurrentCamera"):Connect(watchCamera)
	watchCamera()
	player:GetAttributeChangedSignal("ColourBlind"):Connect(applyPalette)
	Binds.Changed:Connect(function()
		if ui.panel.Visible then
			render()
		end
	end)
	Binds.Bind("Settings", function(_, state)
		if state == Enum.UserInputState.Begin then
			SettingsController.Toggle()
		end
		return Enum.ContextActionResult.Pass
	end)
end

return SettingsController
