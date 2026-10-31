-- Progress and stat bars (sheets 05, 08, 18, 19, 20):
--   fill  "xp" / "yellow", "health" / "red", "stamina" / "green",
--         "food" / "orange", "blue" — the 9-sliced fills of sheets 18 and 19
--   frame "track" dark XP track (M01, M07), "none" the fill alone,
--         "well" paper frame with a dark well, "thin" the quest-row frame,
--         "stat" a framed icon tile (sheets 08, 20) beside the paper bar
--         frame, with the value centred in the bar (cream, ink outline) so it
--         reads over the fill and the empty well alike
-- :Set(fraction) eases the fill (bar motion token; at once with reduced motion).
-- Bars always show the real fraction (D20).
--
--   local xp = Kit.Bar.new(card, { rect = { 96, 46, 160, 14 }, fill = "xp" })
--   xp:Set(450 / 750)
--   Kit.Bar.new(hud, { rect = { 0, 0, 315, 65 }, fill = "health", frame = "stat", icon = "heart", text = "85" })

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local HudModel = require(ReplicatedStorage.Shared.UI.HudModel)
local KitModel = require(ReplicatedStorage.Shared.UI.KitModel)
local Art = require(script.Parent.Art)
local Core = require(script.Parent.Core)
local Motion = require(script.Parent.Motion)

local Bar = {}
Bar.__index = Bar

Bar.FILLS = {
	xp = "yellow",
	yellow = "yellow",
	health = "red",
	red = "red",
	stamina = "green",
	green = "green",
	food = "orange",
	orange = "orange",
	blue = "blue",
}

-- Frame art and its well (the fill's area) in the sprite's own px:
-- {role, left, top, right, bottom}.
Bar.FRAMES = {
	track = { "bar.track", 3, 3, 3, 3 },
	well = { "bar.frame", 24, 15, 23, 16 },
	thin = { "bar.frameThin", 10, 9, 10, 8 },
	stat = { "bar.frame", 24, 15, 23, 16 },
}
-- The stat frame: the icon tile is as wide as the bar is tall, then this gap,
-- then the bar frame to the right edge; the icon fills this share of the tile.
Bar.STAT_GAP = 4
Bar.STAT_ICON = 0.7
-- The value's text size as a share of the well's height.
Bar.STAT_TEXT = 0.6

-- props: rect | size, fill, frame ("track"), icon (stat frame), text (value
-- text over the bar: the stat frame's in cream with an ink outline, else in
-- textColor, default ink), textSize (stat frame), value (0-1), zIndex, name.
function Bar.new(parent: Instance, props)
	local fillKey = Bar.FILLS[props.fill or "xp"] or "yellow"
	local fillRole = "bar.fill." .. fillKey
	local frameKey = props.frame or "track"
	local frame = Bar.FRAMES[frameKey]
	local w, h = Core.Size(props, 300, 28)
	local base = Core.Root(parent, "Bar", fillRole, props, w, h)
	base.root:SetAttribute("KitFrame", frameKey)
	local self = setmetatable({ root = base.root, base = base, w = w, h = h, fraction = -1 }, Bar)
	local well = { 0, 0, w, h }
	if frame then
		-- The frame's rect: the whole bar, or (stat) right of the icon tile.
		local fx = 0
		if frameKey == "stat" then
			local tile = Core.Make("Frame", {
				Name = "IconTile",
				BackgroundTransparency = 1,
				Size = UDim2.fromOffset(h, h),
				ZIndex = base.z,
			}, base.visual)
			Art.Plate(tile, "bar.statTile", h, h, { z = base.z })
			if props.icon then
				local box = math.floor(h * Bar.STAT_ICON)
				self.icon = Art.Icon(base.visual, props.icon, { (h - box) / 2, (h - box) / 2, box, box }, {
					z = base.z + 3,
					name = "StatIcon",
				})
			end
			fx = h + Bar.STAT_GAP
		end
		local fw = w - fx
		local holder = Core.Make("Frame", {
			Name = "Frame",
			BackgroundTransparency = 1,
			Position = UDim2.fromOffset(fx, 0),
			Size = UDim2.fromOffset(fw, h),
			ZIndex = base.z,
		}, base.visual)
		local sprite = Art.ROLES[frame[1]].sprite
		local nw, nh = Art.SizeOf(sprite)
		local k = HudModel.SliceScale(nw or fw, nh or h, fw, h)
		Art.Plate(holder, frame[1], fw, h, { z = base.z })
		-- The well is measured from the sprite's corner; the plate is drawn
		-- outset so its visible edge sits on the rect.
		local out = Art.Outset(frame[1], sprite, fw, h)
		local l, t = frame[2] * k - out[1], frame[3] * k - out[2]
		local r, b = frame[4] * k - out[3], frame[5] * k - out[4]
		well = {
			fx + math.floor(l + 0.5),
			math.floor(t + 0.5),
			fw - math.floor(l + r + 0.5),
			h - math.floor(t + b + 0.5),
		}
		if frameKey == "stat" then
			-- The value sits in the bar, over the fill and the empty well.
			self.label = Core.Label(base.visual, {
				name = "Value",
				text = props.text or "",
				role = "value",
				size = props.textSize or math.floor(well[4] * Bar.STAT_TEXT),
				color = "cream",
				outline = "ink",
				outlineThickness = 2,
				align = "Center",
				scaled = true,
				rect = { well[1] + 6, well[2], well[3] - 12, well[4] },
				z = base.z + 3,
			})
		end
	end
	self.well = well
	local fillSprite = Art.ROLES[fillRole].sprite
	local _, fh = Art.SizeOf(fillSprite)
	local fillScale = well[4] / (fh or well[4])
	self.minWidth = 24 * fillScale
	-- The fill is a clipping frame as wide as the value over a sliced plate
	-- never narrower than its two end caps: a low value (under about a fifth)
	-- shows a short clipped stub instead of vanishing.
	self.fill = Core.Make("Frame", {
		Name = "Fill",
		BackgroundTransparency = 1,
		ClipsDescendants = true,
		Position = UDim2.fromOffset(well[1], well[2]),
		Size = UDim2.fromOffset(well[3], well[4]),
		ZIndex = base.z + 1,
	}, base.visual)
	self.fillPlate = Core.Make("Frame", {
		Name = "Plate",
		BackgroundTransparency = 1,
		Size = UDim2.fromOffset(well[3], well[4]),
		ZIndex = base.z + 1,
	}, self.fill)
	-- Built at the full well size, so the fill's caps scale with the bar's height.
	Art.Plate(self.fillPlate, fillRole, well[3], well[4], { z = base.z + 1 })
	if props.text and frameKey ~= "stat" then
		self.label = Core.Label(base.visual, {
			name = "Value",
			text = props.text,
			role = "hudSmall",
			color = props.textColor or "ink",
			align = "Center",
			scaled = true,
			rect = { 0, 0, w, h },
			z = base.z + 3,
		})
	end
	self:Set(props.value or 0, true)
	return self
end

-- Sets the fill to `fraction` (0-1), easing unless `instant`.
function Bar:Set(fraction: number, instant: boolean?)
	fraction = HudModel.Clamp01(fraction)
	if fraction == self.fraction and not instant then
		return
	end
	self.fraction = fraction
	self.root:SetAttribute("KitValue", fraction)
	local width = KitModel.FillWidth(fraction, self.well[3], self.minWidth)
	local visible = fraction > 0
	local goal = { Size = UDim2.fromOffset(width, self.well[4]) }
	local plateGoal = { Size = UDim2.fromOffset(math.max(width, self.minWidth), self.well[4]) }
	if instant then
		Motion.Set(self.fill, goal)
		Motion.Set(self.fillPlate, plateGoal)
		self.fill.Visible = visible
		return
	end
	self.fill.Visible = true
	Motion.Play(self.fillPlate, "bar", plateGoal)
	Motion.Play(self.fill, "bar", goal, function()
		self.fill.Visible = visible
	end)
end

function Bar:SetText(text: string)
	if self.label then
		self.label.Text = text
	end
end

function Bar:Destroy()
	self.base.maid:Clean()
end

return Bar
