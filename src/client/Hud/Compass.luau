-- Top-centre compass strip: heading letters and ticks that scroll with the
-- camera's yaw, a fixed centre marker, and a row of waypoint icons below for known
-- points of interest. HudModel does the projection; this only places things.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local HudModel = require(ReplicatedStorage.Shared.UI.HudModel)
local Layout = require(script.Parent.Layout)
local Widgets = require(script.Parent.Widgets)

local Compass = {}
Compass.__index = Compass

-- Letters fade out over the outer part of the strip.
Compass.FADE_FROM = 0.8

function Compass.new(parent: Instance, layout)
	local cfg = layout.compass
	local self = setmetatable({ cfg = cfg, marks = {}, waypoints = {} }, Compass)
	self.root = Widgets.Panel(cfg, {
		Name = "Compass",
		Size = UDim2.fromOffset(cfg.size[1], cfg.size[2]),
	}, parent)
	Layout.Place(self.root, cfg)
	-- Gold end triangles, as on the compass art.
	local triangles = cfg.triangles
	for _, centre in triangles.centres do
		Widgets.Make("TextLabel", {
			Name = "EndTriangle",
			AnchorPoint = Vector2.new(0.5, 0.5),
			BackgroundTransparency = 1,
			Position = UDim2.fromOffset(centre[1], centre[2]),
			Size = UDim2.fromOffset(triangles.size[1], triangles.size[2]),
			Text = "▲",
			TextColor3 = Layout.Color(triangles.color),
			TextScaled = true,
			TextStrokeColor3 = Layout.Color("outline"),
			TextStrokeTransparency = 0.3,
			Font = Enum.Font.GothamBold,
			ZIndex = 4,
		}, self.root)
	end
	self.track = Widgets.Make("Frame", {
		Name = "Track",
		BackgroundTransparency = 1,
		ClipsDescendants = true,
		Position = Layout.Position(cfg.track),
		Size = Layout.Size(cfg.track),
		ZIndex = 2,
	}, self.root)
	self.centre = cfg.track[3] / 2
	self.pixelsPerDegree = self.centre / cfg.halfSpan
	local count = math.floor(cfg.halfSpan * 2 / cfg.minorStep) + 2
	for index = 1, count do
		local notch = Widgets.Make("Frame", {
			Name = "Notch" .. index,
			AnchorPoint = Vector2.new(0.5, 0),
			BackgroundColor3 = Layout.Color("body"),
			BackgroundTransparency = 0.3,
			BorderSizePixel = 0,
			Size = UDim2.fromOffset(2, cfg.minorTick.h),
			ZIndex = 3,
		}, self.track)
		local letter = Widgets.Text(cfg.letter, {
			Name = "Letter" .. index,
			AnchorPoint = Vector2.new(0.5, 0),
			Size = UDim2.fromOffset(44, cfg.letter.h),
			TextXAlignment = Enum.TextXAlignment.Center,
			TextTruncate = Enum.TextTruncate.None,
		}, self.track)
		self.marks[index] = { notch = notch, letter = letter }
	end
	Widgets.Sprite(cfg.marker.sprite, {
		Name = "Marker",
		Position = Layout.Position(cfg.marker.rect),
		Size = Layout.Size(cfg.marker.rect),
		ZIndex = 6,
	}, self.root)
	self.waypointRow = Widgets.Make("Frame", {
		Name = "Waypoints",
		BackgroundTransparency = 1,
		Position = UDim2.fromOffset(cfg.track[1], cfg.waypoints.y),
		Size = UDim2.fromOffset(cfg.track[3], cfg.waypoints.size),
		ZIndex = 2,
	}, self.root)
	return self
end

-- Replaces the waypoint set: array of {id, icon, label?}. Positions come in Update.
function Compass:SetWaypoints(list)
	local keep = {}
	for _, waypoint in list do
		keep[waypoint.id] = true
		if self.waypoints[waypoint.id] == nil then
			local size = waypoint.size or self.cfg.waypoints.size
			local icon = Widgets.Sprite(waypoint.icon, {
				Name = "Waypoint",
				AnchorPoint = Vector2.new(0.5, 1),
				Size = UDim2.fromOffset(size, size),
				ZIndex = 3,
			}, self.waypointRow)
			if icon:IsA("ImageLabel") then
				icon.ImageColor3 = Layout.Color(self.cfg.waypoints.tint)
			end
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
			local tickCfg = if mark.major then cfg.majorTick else cfg.minorTick
			slot.notch.Position = UDim2.fromOffset(x, tickCfg.y)
			slot.notch.Size = UDim2.fromOffset(2, tickCfg.h)
			if mark.label then
				local edge = math.abs(mark.offset) / cfg.halfSpan
				local fade = math.clamp((edge - Compass.FADE_FROM) / (1 - Compass.FADE_FROM), 0, 1)
				slot.letter.Text = mark.label
				local cardinal = mark.label == "N"
				local raise = if cardinal then cfg.letter.cardinalRaise else 0
				slot.letter.TextSize = if cardinal then cfg.letter.cardinalTextSize else cfg.letter.textSize
				slot.letter.Position = UDim2.fromOffset(x, cfg.letter.y - raise)
				slot.letter.TextTransparency = fade * 0.8
			end
		end
	end
	for id, icon in self.waypoints do
		local bearing = bearings[id]
		local offset = bearing and HudModel.CompassOffset(heading, bearing, cfg.halfSpan)
		icon.Visible = offset ~= nil
		if offset then
			icon.Position = UDim2.fromOffset(self.centre + offset * self.pixelsPerDegree, self.cfg.waypoints.size)
		end
	end
end

return Compass
