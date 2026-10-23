-- Shared UI theme and helpers (GDD §11, §25). One palette, type scale and builder
-- for new screens; rarity always shows its name with its colour. Accessibility
-- choices replicate as player attributes (SettingsService): UiScale, ColourBlind,
-- ReducedMotion and Subtitles.

local Players = game:GetService("Players")

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
