-- Settings (GDD §25, §11): UI scale, colour-blind palette, reduced motion,
-- subtitles for alert sounds, and replaying the tutorial. O (or the Settings
-- button) opens it; choices save to the profile and apply everywhere at once.

local ContextActionService = game:GetService("ContextActionService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Rarity = require(ReplicatedStorage.Shared.Items.Rarity)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Theme = require(script.Parent.Parent.Ui.Theme)

local SettingsController = {}

local player = Players.LocalPlayer
local playerGui = player:WaitForChild("PlayerGui")
local ui = {}
local defaultRarity = table.clone(Rarity.Colors)

local make = Theme.Make

local function applyScale()
	local scale = player:GetAttribute("UiScale") or 1
	for _, gui in playerGui:GetChildren() do
		if gui:IsA("ScreenGui") then
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

local function render()
	for _, child in ui.list:GetChildren() do
		if not child:IsA("UIListLayout") then
			child:Destroy()
		end
	end
	local function row(text: string, onClick)
		local b = make("TextButton", {
			Text = text,
			Size = UDim2.new(1, 0, 0, Theme.TOUCH_TARGET),
			BackgroundColor3 = Theme.Colors.Button,
			TextColor3 = Theme.Colors.Text,
			Font = Theme.Fonts.Bold,
			TextSize = Theme.TextSize.Body,
		}, ui.list)
		make("UICorner", { CornerRadius = UDim.new(0, 6) }, b)
		b.Activated:Connect(function()
			onClick()
			task.delay(0.3, render)
		end)
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
end

local function build()
	local gui = make("ScreenGui", { Name = "Settings", ResetOnSpawn = false, DisplayOrder = 20 }, playerGui)
	ui.panel = make("Frame", {
		AnchorPoint = Vector2.new(0.5, 0.5),
		Position = UDim2.fromScale(0.5, 0.5),
		Size = UDim2.fromOffset(360, 330),
		BackgroundColor3 = Theme.Colors.Panel,
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
	end)
	ui.list = make("Frame", {
		Position = UDim2.fromOffset(12, 40),
		Size = UDim2.new(1, -24, 1, -50),
		BackgroundTransparency = 1,
	}, ui.panel)
	make("UIListLayout", { Padding = UDim.new(0, 6) }, ui.list)
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
		ui.panel.Visible = not ui.panel.Visible
		if ui.panel.Visible then
			render()
		end
	end)
end

-- Opens or closes this panel (keys, and the on-screen navigation bar).
function SettingsController.Toggle()
	ui.panel.Visible = not ui.panel.Visible
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
	player:GetAttributeChangedSignal("ColourBlind"):Connect(applyPalette)
	ContextActionService:BindAction("FlintbornSettings", function(_, state)
		if state == Enum.UserInputState.Begin then
			SettingsController.Toggle()
		end
		return Enum.ContextActionResult.Pass
	end, false, Enum.KeyCode.O)
end

return SettingsController
