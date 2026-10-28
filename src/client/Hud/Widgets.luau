-- Builders for HUD pieces drawn from the UI art sheets (art/ui/sprites). With an
-- uploaded id a sprite is an ImageLabel (9-sliced when the manifest gives slice
-- insets); without one it falls back to a styled Frame in the same place: dark
-- fill #1E1E1E, rope-brown #8A5A2E stroke, rounded corners, and a text glyph for
-- icons. So the HUD reads clearly before any upload.

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")

local HudModel = require(ReplicatedStorage.Shared.UI.HudModel)
local UiAssets = require(ReplicatedStorage.Shared.UI.UiAssets)
local Layout = require(script.Parent.Layout)
local SpriteLoader = require(script.Parent.SpriteLoader)

local Widgets = {}

-- Text stand-ins for icons that are not uploaded yet.
Widgets.GLYPHS = {
	icon_heart = { "♥", "health" },
	icon_lightning = { "⚡", "food" },
	icon_meat = { "🍖", "body" },
	icon_star_gold = { "★", "gold" },
	icon_sound_on = { "🔊", "cyan" },
	icon_waypoint = { "◆", "gold" },
	icon_storm = { "🌀", "cyan" },
	icon_mountain = { "▲", "text" },
	icon_tower = { "♜", "text" },
	icon_run = { "🏃", "text" },
	compass_marker = { "▼", "text" },
}

-- Fallback colours for bar fills.
Widgets.FILL_COLORS = {
	fill_red = "health",
	fill_green = "stamina",
	fill_yellow = "food",
	fill_orange_striped = "xp",
	fill_blue = "cyan",
	fill_track = "track",
}

local function apply(object: Instance, props)
	if props then
		for key, value in props do
			(object :: any)[key] = value
		end
	end
	return object
end

function Widgets.Make(className: string, props, parent: Instance?)
	local object = Instance.new(className)
	apply(object, props)
	object.Parent = parent
	return object
end

local function targetSize(props): (number, number)
	local size = props and props.Size
	if typeof(size) == "UDim2" then
		return size.X.Offset, size.Y.Offset
	end
	return 0, 0
end

-- Parchment-kit stand-ins: words for icons, warm paper or leather plates for the
-- rest, so the lobby reads before its art is uploaded.
Widgets.PARCHMENT_GLYPHS = {
	pm_icon_crown = { "♛", "leather" },
	pm_icon_add_friend = { "+", "ink" },
	pm_button_add_friend = { "+", "ink" },
	pm_button_x = { "✕", "ink" },
	pm_button_check = { "✓", "ink" },
	pm_lobby_gear = { "⚙", "ink" },
}

-- Coins and Gems plates: a coloured mark at the left where the art has its coin
-- or gem, so the two read apart before upload.
Widgets.PARCHMENT_BADGES = {
	pm_lobby_coins = { "●", "gold" },
	pm_lobby_gems = { "◆", "cyan" },
}

local function parchmentFallback(name: string, props, parent: Instance?)
	local frame = Widgets.Make("Frame", { Name = name, BorderSizePixel = 0 }, parent)
	local leather = name == "pm_lobby_enter" or string.find(name, "^pm_button_leather") ~= nil
	if name == "pm_fill_xp" then
		frame.BackgroundColor3 = Layout.Color("xp")
		Widgets.Make("UICorner", { CornerRadius = UDim.new(0.5, 0) }, frame)
		return apply(frame, props)
	end
	frame.BackgroundColor3 = Layout.Color(if leather then "leather" else "paper")
	Widgets.Make("UICorner", { CornerRadius = UDim.new(0, 8) }, frame)
	Widgets.Make("UIStroke", { Color = Layout.Color("paperEdge"), Thickness = 2 }, frame)
	local badge = Widgets.PARCHMENT_BADGES[name]
	if badge then
		local mark = Widgets.Make("TextLabel", {
			Name = "Badge",
			BackgroundTransparency = 1,
			Position = UDim2.new(0, 10, 0.15, 0),
			Size = UDim2.fromScale(0.3, 0.7),
			Text = badge[1],
			TextColor3 = Layout.Color(badge[2]),
			TextScaled = true,
			Font = Enum.Font.GothamBold,
			ZIndex = (props and props.ZIndex or 1) + 1,
		}, frame)
		Widgets.Make("UITextSizeConstraint", { MaxTextSize = 40 }, mark)
	end
	local glyph = Widgets.PARCHMENT_GLYPHS[name]
	if glyph then
		if string.sub(name, 1, 8) == "pm_icon_" then
			frame.BackgroundTransparency = 1
			frame:FindFirstChildOfClass("UIStroke"):Destroy()
		end
		local mark = Widgets.Make("TextLabel", {
			Name = "Glyph",
			BackgroundTransparency = 1,
			Size = UDim2.fromScale(1, 1),
			Text = glyph[1],
			TextColor3 = Layout.Color(glyph[2]),
			TextScaled = true,
			Font = Enum.Font.GothamBold,
			ZIndex = (props and props.ZIndex or 1) + 1,
		}, frame)
		Widgets.Make("UITextSizeConstraint", { MaxTextSize = 40 }, mark)
	end
	return apply(frame, props)
end

local function fallback(name: string, props, parent: Instance?)
	if string.sub(name, 1, 3) == "pm_" then
		return parchmentFallback(name, props, parent)
	end
	local glyph = Widgets.GLYPHS[name]
	if glyph or string.sub(name, 1, 5) == "icon_" then
		local label = Widgets.Make("TextLabel", {
			Name = name,
			BackgroundTransparency = 1,
			Text = glyph and glyph[1] or "•",
			TextColor3 = Layout.Color(glyph and glyph[2] or "text"),
			TextScaled = true,
			Font = Enum.Font.GothamBold,
		}, parent)
		return apply(label, props)
	end
	local frame = Widgets.Make("Frame", { Name = name, BorderSizePixel = 0 }, parent)
	local fillKey = Widgets.FILL_COLORS[name]
	if fillKey then
		frame.BackgroundColor3 = Layout.Color(fillKey)
		Widgets.Make("UICorner", { CornerRadius = UDim.new(0.5, 0) }, frame)
	elseif name == "keycap" then
		frame.BackgroundColor3 = Layout.Color("body")
		Widgets.Make("UICorner", { CornerRadius = UDim.new(0, 8) }, frame)
	elseif name == "frame_slot_selected" then
		frame.BackgroundTransparency = 1
		Widgets.Make("UICorner", { CornerRadius = UDim.new(0, 10) }, frame)
		Widgets.Make("UIStroke", { Color = Layout.Color("selected"), Thickness = 3 }, frame)
	elseif string.sub(name, -7) == "_hollow" then
		-- Open rope frames (over a portrait or a fill): stroke only.
		frame.BackgroundTransparency = 1
		Widgets.Make("UICorner", { CornerRadius = UDim.new(0, 8) }, frame)
		Widgets.Make("UIStroke", { Color = Layout.Color("fallbackStroke"), Thickness = 3 }, frame)
	else
		-- Filled rope frames, panels, pills and slot overlays: dark fill, rope edge.
		frame.BackgroundColor3 = Layout.Color("fallbackFill")
		frame.BackgroundTransparency = if string.sub(name, 1, 6) == "panel_" then 0.15 else 0.05
		Widgets.Make("UICorner", { CornerRadius = UDim.new(0, 8) }, frame)
		if string.sub(name, 1, 6) ~= "panel_" then
			Widgets.Make("UIStroke", { Color = Layout.Color("fallbackStroke"), Thickness = 2 }, frame)
		end
	end
	return apply(frame, props)
end

-- An image from the art sheets by sprite name, or its styled fallback.
-- `sliceScale` overrides the automatic 9-slice corner scale (layout "sliceScale").
function Widgets.Sprite(name: string, props, parent: Instance?, sliceScale: number?): GuiObject
	local id = UiAssets.image(name)
	if id == nil then
		return fallback(name, props, parent)
	end
	local image = Widgets.Make("ImageLabel", { Name = name, BackgroundTransparency = 1, Image = id }, parent)
	SpriteLoader.Track(image)
	local center = UiAssets.sliceCenter(name)
	local sprite = UiAssets.sprite(name)
	if center and sprite then
		image.ScaleType = Enum.ScaleType.Slice
		image.SliceCenter = center
		local width, height = targetSize(props)
		if sliceScale then
			image.SliceScale = sliceScale
		elseif width > 0 and height > 0 then
			image.SliceScale = HudModel.SliceScale(sprite.w, sprite.h, width, height)
		end
	elseif string.sub(name, 1, 5) == "fill_" then
		image.ScaleType = Enum.ScaleType.Stretch
	else
		image.ScaleType = Enum.ScaleType.Fit
	end
	return apply(image, props)
end

-- A frame sprite whose visible rails land on `rect` [x, y, w, h]: the sprite's
-- rope sits a few pixels inside its own bounds, so it is drawn larger by `outset`
-- [left, top, right, bottom] (the layout's frameOutset unless given).
function Widgets.Frame(name: string, rect, parent: Instance, sliceScale: number?, outset)
	local layout = Layout.Get()
	local pad = outset or layout.frameOutset or { 0, 0, 0, 0 }
	local width, height = rect[3] + pad[1] + pad[3], rect[4] + pad[2] + pad[4]
	local frame = Widgets.Sprite(name, {
		Name = "Frame",
		Position = UDim2.fromOffset(rect[1] - pad[1], rect[2] - pad[2]),
		Size = UDim2.fromOffset(width, height),
		ZIndex = 3,
	}, parent, sliceScale)
	return frame
end

-- A panel: a translucent rounded fill (cfg.fill, cfg.fillTransparency) under a
-- rope frame sprite (cfg.frame) whose rails sit on the panel's own rectangle.
function Widgets.Panel(cfg, props, parent: Instance?): Frame
	local holder = Widgets.Make("Frame", { BackgroundTransparency = 1 }, parent)
	apply(holder, props)
	local size = props.Size
	local width, height = size.X.Offset, size.Y.Offset
	if cfg.fill then
		local inset = cfg.fillInset or 3
		local fill = Widgets.Make("Frame", {
			Name = "Fill",
			BackgroundColor3 = Layout.Color(cfg.fill),
			BackgroundTransparency = cfg.fillTransparency or 0,
			BorderSizePixel = 0,
			Position = UDim2.fromOffset(inset, inset),
			Size = UDim2.new(1, -inset * 2, 1, -inset * 2),
			ZIndex = 1,
		}, holder)
		Widgets.Make("UICorner", { CornerRadius = UDim.new(0, 8) }, fill)
	end
	if cfg.frame then
		Widgets.Frame(cfg.frame, { 0, 0, width, height }, holder, cfg.sliceScale, cfg.frameOutset)
	end
	return holder :: Frame
end

-- A solid rounded bar fill in a layout colour with a soft top highlight. The
-- gradient carries the colour over a white background: a UIGradient multiplies
-- the background, so a coloured one would come out darker and oversaturated.
function Widgets.Fill(colorKey: string, props, parent: Instance?): Frame
	local color = Layout.Color(colorKey)
	local fill = Widgets.Make("Frame", {
		Name = "Fill",
		BackgroundColor3 = Color3.new(1, 1, 1),
		BorderSizePixel = 0,
	}, parent)
	Widgets.Make("UICorner", { CornerRadius = UDim.new(0.5, 0) }, fill)
	Widgets.Make("UIGradient", {
		Rotation = 90,
		Color = ColorSequence.new({
			ColorSequenceKeypoint.new(0, color:Lerp(Color3.new(1, 1, 1), 0.25)),
			ColorSequenceKeypoint.new(0.45, color),
			ColorSequenceKeypoint.new(1, color:Lerp(Color3.new(0, 0, 0), 0.12)),
		}),
	}, fill)
	return apply(fill, props) :: Frame
end

-- A text label in the layout's fonts and colours. `entry` holds font, textSize, color.
function Widgets.Text(entry, props, parent: Instance?): TextLabel
	local label = Widgets.Make("TextLabel", {
		BackgroundTransparency = 1,
		Font = Layout.Font(entry.font),
		TextSize = entry.textSize or 14,
		TextColor3 = Layout.Color(entry.color),
		TextStrokeColor3 = Color3.new(0, 0, 0),
		TextStrokeTransparency = 0.65,
		TextXAlignment = Enum.TextXAlignment.Left,
		TextTruncate = Enum.TextTruncate.AtEnd,
		ZIndex = 4,
	}, parent)
	local face = Layout.FontFace(entry.font)
	if face then
		label.FontFace = face
	end
	return apply(label, props) :: TextLabel
end

-- A bar: a track (a sprite, or a rounded colour with `trackColor`) and a fill
-- whose width Widgets.SetBar sets. cfg = {rect, inset?, maxWidth?, track?,
-- trackColor?, fillColor}. Returns {root, fill, maxWidth, height, inset}.
function Widgets.Bar(cfg, parent)
	local rect = cfg.rect
	local inset = cfg.inset or 0
	local root = Widgets.Make("Frame", {
		Name = "Bar",
		BackgroundTransparency = 1,
		Position = Layout.Position(rect),
		Size = Layout.Size(rect),
		ZIndex = 4,
	}, parent)
	if cfg.track then
		Widgets.Sprite(cfg.track, { Name = "Track", Size = Layout.Size(rect), ZIndex = 4 }, root)
	elseif cfg.trackColor then
		local track = Widgets.Make("Frame", {
			Name = "Track",
			BackgroundColor3 = Layout.Color(cfg.trackColor),
			BorderSizePixel = 0,
			Size = UDim2.fromScale(1, 1),
			ZIndex = 4,
		}, root)
		Widgets.Make("UICorner", { CornerRadius = UDim.new(0.5, 0) }, track)
	end
	local fillHeight = rect[4] - inset * 2
	local maxWidth = cfg.maxWidth or (rect[3] - inset * 2)
	local fillProps = {
		Name = "Fill",
		Position = UDim2.fromOffset(cfg.insetX or inset, inset),
		Size = UDim2.fromOffset(maxWidth, fillHeight),
		ZIndex = 5,
	}
	-- A sprite fill (9-sliced art, corners at their natural size) or a colour fill.
	local fill = if cfg.fill
		then Widgets.Sprite(cfg.fill, fillProps, root, 1)
		else Widgets.Fill(cfg.fillColor, fillProps, root)
	-- A sprite fill narrower than its two end caps would fold over itself, so it
	-- hides below that width.
	local sprite = cfg.fill and UiAssets.sprite(cfg.fill)
	local slice = sprite and sprite.slice
	local minWidth = if type(slice) == "table" and #slice == 4 then slice[1] + slice[3] else 1
	return { root = root, fill = fill, maxWidth = maxWidth, height = fillHeight, inset = inset, minWidth = minWidth }
end

-- The selected-slot highlight: the sheet's glowing cyan slot frame (cfg.sprite)
-- drawn over the slot's own frame at the same size, untinted so the glow stays
-- bright. Hidden until the slot is selected.
function Widgets.SelectionRing(cfg, slotSize, parent: Instance): GuiObject
	local rect = { 0, 0, slotSize[1], slotSize[2] }
	local ring = Widgets.Frame(cfg.sprite, rect, parent, cfg.sliceScale, cfg.frameOutset)
	ring.Name = "Selected"
	ring.Visible = false
	if ring:IsA("ImageLabel") then
		ring.ImageColor3 = Color3.new(1, 1, 1)
	end
	return ring
end

-- A small white map pin (circle head, pointed foot, dark centre) in `size`.
function Widgets.Pin(color: Color3, props, parent: Instance?): Frame
	local pin = Widgets.Make("Frame", { Name = "Pin", BackgroundTransparency = 1 }, parent)
	apply(pin, props)
	local foot = Widgets.Make("Frame", {
		AnchorPoint = Vector2.new(0.5, 0.5),
		BackgroundColor3 = color,
		BorderSizePixel = 0,
		Position = UDim2.fromScale(0.5, 0.58),
		Rotation = 45,
		Size = UDim2.fromScale(0.5, 0.36),
		ZIndex = 4,
	}, pin)
	Widgets.Make("UIAspectRatioConstraint", { AspectRatio = 1 }, foot)
	local head = Widgets.Make("Frame", {
		BackgroundColor3 = color,
		BorderSizePixel = 0,
		Size = UDim2.fromScale(1, 0.7),
		ZIndex = 5,
	}, pin)
	Widgets.Make("UICorner", { CornerRadius = UDim.new(0.5, 0) }, head)
	Widgets.Make("UIAspectRatioConstraint", { AspectRatio = 1 }, head)
	local dot = Widgets.Make("Frame", {
		AnchorPoint = Vector2.new(0.5, 0.5),
		BackgroundColor3 = Layout.Color("outline"),
		BorderSizePixel = 0,
		Position = UDim2.fromScale(0.5, 0.5),
		Size = UDim2.fromScale(0.36, 0.36),
		ZIndex = 6,
	}, head)
	Widgets.Make("UICorner", { CornerRadius = UDim.new(0.5, 0) }, dot)
	return pin :: Frame
end

Widgets.BAR_TWEEN = TweenInfo.new(0.25, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)

-- Sets a bar's fill (0–1), easing smoothly unless `instant` (reduced motion, first draw).
function Widgets.SetBar(bar, fraction: number, instant: boolean?)
	fraction = HudModel.Clamp01(fraction)
	if bar.fraction == fraction and not instant then
		return
	end
	bar.fraction = fraction
	local width = bar.maxWidth * fraction
	local goal = UDim2.fromOffset(width, bar.height)
	if bar.tween then
		bar.tween:Cancel()
		bar.tween = nil
	end
	if instant then
		bar.fill.Size = goal
		bar.fill.Visible = width >= (bar.minWidth or 1)
		return
	end
	-- Ease all the way to empty, then hide the rounded sliver that would remain.
	bar.fill.Visible = true
	local tween = TweenService:Create(bar.fill, Widgets.BAR_TWEEN, { Size = goal })
	bar.tween = tween
	tween.Completed:Connect(function(state)
		if state == Enum.PlaybackState.Completed and bar.tween == tween then
			bar.fill.Visible = width >= (bar.minWidth or 1)
		end
	end)
	tween:Play()
end

return Widgets
