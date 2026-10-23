-- Shared UI theme and helpers (GDD §11, §25). One palette, type scale and builder
-- for new screens; rarity always shows its name with its colour. Accessibility
-- choices replicate as player attributes (SettingsService): UiScale, ColourBlind,
-- ReducedMotion and Subtitles.

local Players = game:GetService("Players")
local UserInputService = game:GetService("UserInputService")

local Theme = {}

Theme.Colors = {
	Panel = Color3.fromRGB(24, 20, 17),
	Card = Color3.fromRGB(38, 32, 27),
	Button = Color3.fromRGB(110, 70, 30),
	ButtonDisabled = Color3.fromRGB(50, 44, 38),
	Text = Color3.fromRGB(235, 226, 212),
	Heading = Color3.fromRGB(255, 214, 150),
	Good = Color3.fromRGB(160, 230, 160),
	Warn = Color3.fromRGB(255, 170, 120),
}

Theme.Fonts = { Body = Enum.Font.GothamMedium, Bold = Enum.Font.GothamBold, Title = Enum.Font.GothamBlack }
Theme.TextSize = { Small = 12, Body = 14, Heading = 16, Title = 20 }
-- Roblox mobile guidance: touch targets of at least 44 px.
Theme.TOUCH_TARGET = 44

-- A colour-blind-safe rarity palette (Okabe–Ito based), applied in place so every
-- screen reading Rarity.Colors follows the setting.
Theme.ColourBlindRarity = {
	Common = Color3.fromRGB(200, 200, 200),
	Uncommon = Color3.fromRGB(0, 158, 115),
	Rare = Color3.fromRGB(86, 180, 233),
	Epic = Color3.fromRGB(204, 121, 167),
	Legendary = Color3.fromRGB(230, 159, 0),
	Mythic = Color3.fromRGB(213, 94, 0),
	Secret = Color3.fromRGB(240, 228, 66),
	Exclusive = Color3.fromRGB(255, 255, 255),
}

function Theme.Make(className: string, props, parent)
	local instance = Instance.new(className)
	for key, value in props do
		instance[key] = value
	end
	instance.Parent = parent
	return instance
end

function Theme.Option(name: string): any
	return Players.LocalPlayer:GetAttribute(name)
end

function Theme.ReducedMotion(): boolean
	return Theme.Option("ReducedMotion") == true
end

-- True when the player is aiming with a mouse right now. Touchscreen laptops have
-- both a mouse and touch, so the last input decides, not the hardware list.
function Theme.UsingMouse(): boolean
	local last = UserInputService:GetLastInputType()
	if last == Enum.UserInputType.Touch or string.find(last.Name, "Gamepad") then
		return false
	end
	if string.find(last.Name, "Mouse") then
		return true
	end
	-- Keyboard (or nothing yet): fall back to the hardware.
	return UserInputService.MouseEnabled and (last == Enum.UserInputType.Keyboard or not UserInputService.TouchEnabled)
end

-- One shared top-centre column for banners from several controllers, so they
-- stack instead of overlapping; hidden banners take no space.
Theme.TopOrder = {
	Compass = 1,
	Transition = 2,
	Horn = 3,
	Downed = 4,
	Extraction = 5,
	BossBar = 6,
	EventBanner = 7,
	Receipt = 8,
	TradeInvite = 9,
	Toast = 10,
	Tutorial = 11,
}

local topStack = nil

function Theme.TopStack()
	if topStack == nil then
		local gui = Theme.Make(
			"ScreenGui",
			{ Name = "TopStack", ResetOnSpawn = false, DisplayOrder = 5 },
			Players.LocalPlayer:WaitForChild("PlayerGui")
		)
		topStack = Theme.Make("Frame", {
			Name = "Stack",
			AnchorPoint = Vector2.new(0.5, 0),
			Position = UDim2.new(0.5, 0, 0, 2),
			Size = UDim2.fromOffset(600, 0),
			AutomaticSize = Enum.AutomaticSize.Y,
			BackgroundTransparency = 1,
		}, gui)
		Theme.Make("UIListLayout", {
			Padding = UDim.new(0, 4),
			HorizontalAlignment = Enum.HorizontalAlignment.Center,
			SortOrder = Enum.SortOrder.LayoutOrder,
		}, topStack)
	end
	return topStack
end

local subtitle = nil

-- Shows a caption for an alert sound when subtitles are on (§25.4 accessibility).
function Theme.Subtitle(text: string)
	if Theme.Option("Subtitles") == false then
		return
	end
	if subtitle == nil then
		local gui = Theme.Make(
			"ScreenGui",
			{ Name = "Subtitles", ResetOnSpawn = false, DisplayOrder = 50 },
			Players.LocalPlayer:WaitForChild("PlayerGui")
		)
		subtitle = Theme.Make("TextLabel", {
			AnchorPoint = Vector2.new(0.5, 1),
			Position = UDim2.new(0.5, 0, 1, -110),
			Size = UDim2.fromOffset(520, 26),
			BackgroundColor3 = Color3.new(0, 0, 0),
			BackgroundTransparency = 0.35,
			TextColor3 = Color3.new(1, 1, 1),
			Font = Theme.Fonts.Bold,
			TextSize = Theme.TextSize.Body,
			Visible = false,
		}, gui)
		Theme.Make("UICorner", { CornerRadius = UDim.new(0, 6) }, subtitle)
	end
	local shown = "[" .. text .. "]"
	subtitle.Text = shown
	subtitle.Visible = true
	task.delay(4, function()
		if subtitle.Text == shown then
			subtitle.Visible = false
		end
	end)
end

return Theme
