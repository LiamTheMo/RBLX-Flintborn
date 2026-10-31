-- Top-centre compass on the kit's paper plaque (Kit.Panel "plaque"): heading
-- letters in the kit's ink type and ink tick rules (Kit.Divider) that scroll
-- with the camera's yaw, a fixed leather arrow (Kit.Icon) at the centre, and
-- the waypoint icons of known points of interest (Kit.Icon) under the plaque.
-- HudModel does the projection; this only places things.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local HudModel = require(ReplicatedStorage.Shared.UI.HudModel)
local Kit = require(script.Parent.Kit)
local Layout = require(script.Parent.Layout)

local Compass = {}
Compass.__index = Compass

-- Letters fade out over the outer part of the strip and are gone before the
-- strip's edge would cut them.
Compass.FADE_FROM = 0.7

function Compass.new(parent: Instance, layout)
	local cfg = Layout.Section(layout, "compass")
	-- Letter sizes as drawn (body text grows on phones, Kit.Core.TextBoost).
	local boost = Kit.Core.TextBoost("hudSmall")
	local self = setmetatable({
		cfg = cfg,
		marks = {},
		waypoints = {},
		letterSize = cfg.letter.size * boost,
		cardinalSize = cfg.letter.cardinalSize * boost,
		widths = {},
	}, Compass)
	self.root = Instance.new("Frame")
	self.root.Name = "Compass"
	self.root.BackgroundTransparency = 1
	Layout.Place(self.root, cfg)
	self.root.Parent = parent
	self.panel = Kit.Panel.new(self.root, {
		name = "Plaque",
		rect = { 0, 0, cfg.size[1], cfg.size[2] },
		variant = "plaque",
		pad = 0,
	})
	self.track = Instance.new("Frame")
	self.track.Name = "Track"
	self.track.BackgroundTransparency = 1
	self.track.ClipsDescendants = true
	self.track.Position = Layout.Position(cfg.track)
	self.track.Size = Layout.Size(cfg.track)
	self.track.ZIndex = 8
	self.track.Parent = self.root
	self.centre = cfg.track[3] / 2
	self.pixelsPerDegree = self.centre / cfg.halfSpan
	local count = math.floor(cfg.halfSpan * 2 / cfg.minorStep) + 2
	for index = 1, count do
		local notch = Kit.Divider.new(self.track, {
			name = "Notch" .. index,
			rect = { 0, cfg.minorTick.y, 2, cfg.minorTick.h },
			variant = "ink",
			anchorPoint = Vector2.new(0.5, 0),
			zIndex = 8,
		})
		local letter = Kit.Text.new(self.track, {
			name = "Letter" .. index,
			rect = { 0, cfg.letter.y, 44, cfg.letter.h },
			text = "",
			role = "hudSmall",
			textSize = cfg.letter.size,
			align = "Center",
			anchorPoint = Vector2.new(0.5, 0),
			zIndex = 9,
		})
		self.marks[index] = { notch = notch.root, letter = letter.root }
	end
	self.marker = Kit.Icon.new(self.root, {
		name = "Marker",
		rect = cfg.marker,
		icon = "arrow_down",
		tint = "leather",
		zIndex = 10,
	})
	self.waypointRow = Instance.new("Frame")
	self.waypointRow.Name = "Waypoints"
	self.waypointRow.BackgroundTransparency = 1
	self.waypointRow.Position = UDim2.fromOffset(cfg.track[1], cfg.waypoints.y)
	self.waypointRow.Size = UDim2.fromOffset(cfg.track[3], cfg.waypoints.size)
	self.waypointRow.Parent = self.root
	return self
end

-- Replaces the waypoint set: array of {id, icon, size?}. Positions come in Update.
function Compass:SetWaypoints(list)
	local keep = {}
	for _, waypoint in list do
		keep[waypoint.id] = true
		if self.waypoints[waypoint.id] == nil then
			local size = waypoint.size or self.cfg.waypoints.size
			local icon = Kit.Icon.new(self.waypointRow, {
				name = "Waypoint",
				rect = { 0, 0, size, size },
				icon = waypoint.icon,
				anchorPoint = Vector2.new(0.5, 1),
				zIndex = 6,
			})
			icon.root.Visible = false
			self.waypoints[waypoint.id] = icon
		end
	end
	for id, icon in self.waypoints do
		if not keep[id] then
			icon:Destroy()
			self.waypoints[id] = nil
		end
	end
end

-- Half a letter's drawn width (measured once per label and size).
function Compass:_halfWidth(label: string, size: number): number
	local key = label .. "@" .. size
	local width = self.widths[key]
	if width == nil then
		width = Kit.Text.Width(label, "hudSmall", size / Kit.Core.TextBoost("hudSmall"))
		self.widths[key] = width
	end
	return width / 2
end

-- heading: camera degrees clockwise from north. bearings: {[waypointId] = degrees}.
function Compass:Update(heading: number, bearings)
	local cfg = self.cfg
	local marks = HudModel.CompassMarks(heading, cfg.halfSpan, cfg.minorStep, cfg.minorLimit)
	for index, slot in self.marks do
		local mark = marks[index]
		slot.notch.Visible = mark ~= nil
		slot.letter.Visible = mark ~= nil and mark.label ~= nil
		if mark then
			local x = self.centre + mark.offset * self.pixelsPerDegree
			local tick = if mark.major then cfg.majorTick else cfg.minorTick
			slot.notch.Position = UDim2.fromOffset(x, tick.y)
			slot.notch.Size = UDim2.fromOffset(2, tick.h)
			if mark.label then
				local cardinal = #mark.label == 1
				local size = if cardinal then self.cardinalSize else self.letterSize
				-- The letter fades towards the edge and is hidden before the
				-- strip's edge would cut it (no half letters such as "SI").
				local room = self.centre - self:_halfWidth(mark.label, size) - 2
				local edge = math.abs(x - self.centre) / math.max(room, 1)
				local fade = math.clamp((edge - Compass.FADE_FROM) / (1 - Compass.FADE_FROM), 0, 1)
				slot.letter.Visible = edge < 1
				slot.letter.Text = mark.label
				slot.letter.TextSize = size
				slot.letter.Position = UDim2.fromOffset(x, cfg.letter.y - (if cardinal then cfg.letter.raise else 0))
				slot.letter.TextTransparency = fade * 0.85
			end
		end
	end
	for id, icon in self.waypoints do
		local bearing = bearings[id]
		local offset = bearing and HudModel.CompassOffset(heading, bearing, cfg.halfSpan)
		icon.root.Visible = offset ~= nil
		if offset then
			icon.root.Position = UDim2.fromOffset(self.centre + offset * self.pixelsPerDegree, cfg.waypoints.size)
		end
	end
end

return Compass
