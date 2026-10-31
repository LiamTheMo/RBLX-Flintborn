-- Shared UI helpers (GDD §11, §25): accessibility options, the input check, the
-- shared top-centre banner column and alert subtitles. Screens take colours,
-- fonts and sizes from the UI kit's tokens (Hud/Kit, docs/ui/KIT.md); rarity
-- always shows its name with its colour. Accessibility choices replicate as
-- player attributes (SettingsService): UiScale, ColourBlind, ReducedMotion and
-- Subtitles.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local HudModel = require(ReplicatedStorage.Shared.UI.HudModel)
-- Only the kit's scale and tokens: the kit's components require this module.
local KitScale = require(script.Parent.Parent.Hud.Kit.Scale)
local KitTokens = require(script.Parent.Parent.Hud.Kit.Tokens)

local Theme = {}

-- Retired: the old dark palette, still read by NavController's legacy bar. New
-- UI uses the kit's tokens; delete these once nothing reads them.
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
-- stack instead of overlapping; hidden banners take no space. Banners are built
-- in the kit's design px (1672 × 941): the column carries the HUD's scale, and
-- its gui fits itself (Settings' UI scale is folded into that scale).
Theme.TopOrder = {
	Compass = 1,
	Transition = 2,
	Horn = 3,
	Downed = 4,
	Extraction = 5,
	BossBar = 6,
	EventBanner = 7,
	Receipt = 8,
	Toast = 10,
	Tutorial = 11,
}

-- The column's width in design px; banners are at most this wide.
Theme.TOP_WIDTH = 640

local topStack = nil

-- The least scale overlay cards get on a phone, so their body text stays near
-- the 9 px floor (the HUD formula gives about 0.37 at 844 × 390).
Theme.PHONE_MIN_SCALE = 0.6

-- The overlays' scale for a gui: the kit's HUD formula with the player's UI
-- scale; on phones (KitScale.IsSmallTouch) the kit's phone factor, but never
-- under PHONE_MIN_SCALE so notices stay readable.
function Theme.HudScale(gui: GuiBase2d): number
	local size = gui.AbsoluteSize
	if size.X <= 0 or size.Y <= 0 then
		local camera = workspace.CurrentCamera
		size = if camera then camera.ViewportSize else Vector2.new(1672, 941)
	end
	local ref = KitTokens.Data.reference
	local k = HudModel.HudScale(
		size.X,
		size.Y,
		ref.width,
		ref.height,
		KitTokens.Scale("hudMin"),
		KitTokens.Scale("hudMax"),
		Players.LocalPlayer:GetAttribute("UiScale")
	)
	if KitScale.IsSmallTouch(size.Y) then
		k = math.max(k * KitTokens.Scale("phoneHud"), Theme.PHONE_MIN_SCALE)
	end
	return k
end

-- Keeps `uiScale` at the HUD scale of `gui`. Returns a function that stops.
function Theme.FitHud(gui: ScreenGui, uiScale: UIScale): () -> ()
	gui:SetAttribute("FitsItself", true)
	local function apply()
		uiScale.Scale = Theme.HudScale(gui)
	end
	local connections = {
		gui:GetPropertyChangedSignal("AbsoluteSize"):Connect(apply),
		Players.LocalPlayer:GetAttributeChangedSignal("UiScale"):Connect(apply),
	}
	apply()
	return function()
		for _, connection in connections do
			connection:Disconnect()
		end
	end
end

-- A full-screen frame in `gui` in design px at Theme.HudScale (as KitScale.Hud
-- does for the HUD): regions placed inside it by scale and design-px offsets
-- keep to the screen's edges.
function Theme.HudRoot(gui: ScreenGui): Frame
	gui:SetAttribute("FitsItself", true)
	local root = Theme.Make("Frame", {
		Name = "Root",
		BackgroundTransparency = 1,
		Size = UDim2.fromScale(1, 1),
	}, gui)
	local uiScale = Theme.Make("UIScale", { Name = "Fit" }, root)
	local function apply()
		local k = Theme.HudScale(gui)
		uiScale.Scale = k
		root.Size = UDim2.fromScale(1 / k, 1 / k)
	end
	gui:GetPropertyChangedSignal("AbsoluteSize"):Connect(apply)
	Players.LocalPlayer:GetAttributeChangedSignal("UiScale"):Connect(apply)
	apply()
	return root
end

function Theme.TopStack()
	if topStack == nil then
		local gui = Theme.Make("ScreenGui", {
			Name = "TopStack",
			ResetOnSpawn = false,
			DisplayOrder = KitTokens.Order("topStack"),
			ZIndexBehavior = Enum.ZIndexBehavior.Sibling,
		}, Players.LocalPlayer:WaitForChild("PlayerGui"))
		topStack = Theme.Make("Frame", {
			Name = "Stack",
			AnchorPoint = Vector2.new(0.5, 0),
			Position = UDim2.new(0.5, 0, 0, 2),
			Size = UDim2.fromOffset(Theme.TOP_WIDTH, 0),
			AutomaticSize = Enum.AutomaticSize.Y,
			BackgroundTransparency = 1,
		}, gui)
		-- Scales about the column's top centre, so its position stays in screen px.
		Theme.FitHud(gui, Theme.Make("UIScale", { Name = "Fit" }, topStack))
		Theme.Make("UIListLayout", {
			Padding = UDim.new(0, KitTokens.Space("toastGap", 10)),
			HorizontalAlignment = Enum.HorizontalAlignment.Center,
			SortOrder = Enum.SortOrder.LayoutOrder,
		}, topStack)
	end
	return topStack
end

local subtitle = nil

-- Shows a caption for an alert sound when subtitles are on (§25.4 accessibility):
-- a kit tooltip box above the bottom bar, for four seconds.
function Theme.Subtitle(text: string)
	if Theme.Option("Subtitles") == false then
		return
	end
	-- Required here: the kit's components require this module.
	local Kit = require(script.Parent.Parent.Hud.Kit) :: any
	if subtitle == nil then
		local gui = Theme.Make("ScreenGui", {
			Name = "Subtitles",
			ResetOnSpawn = false,
			DisplayOrder = 50,
			ZIndexBehavior = Enum.ZIndexBehavior.Sibling,
		}, Players.LocalPlayer:WaitForChild("PlayerGui"))
		local holder = Theme.Make("Frame", {
			Name = "Caption",
			AnchorPoint = Vector2.new(0.5, 1),
			BackgroundTransparency = 1,
			Position = UDim2.new(0.5, 0, 1, -110),
			Size = UDim2.fromOffset(0, 0),
		}, gui)
		Theme.FitHud(gui, Theme.Make("UIScale", { Name = "Fit" }, holder))
		subtitle = { holder = holder, box = nil, text = nil }
	end
	local shown = "[" .. text .. "]"
	if subtitle.box then
		subtitle.box:Destroy()
	end
	local w, h = Kit.Tooltip.Measure(shown)
	subtitle.holder.Size = UDim2.fromOffset(w, h)
	subtitle.box =
		Kit.Tooltip.new(subtitle.holder, { name = "Box", rect = { 0, 0, w, h }, text = shown, tail = "none" })
	subtitle.text = shown
	subtitle.holder.Visible = true
	task.delay(4, function()
		if subtitle.text == shown then
			subtitle.holder.Visible = false
		end
	end)
end

return Theme
