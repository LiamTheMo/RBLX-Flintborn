-- The painted island map (art/ui/map/island.png, uploaded as pm_map_island) inside
-- a clipped frame: zoom in and out, pins for places with a name plate on the
-- chosen one, and an optional live marker. The Journal's map panel and the world
-- Map screen use it. The image covers MAP_SPAN studs centred on the island with
-- −Z (north) up, the span render_island.py paints.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local PoiCatalog = require(ReplicatedStorage.Shared.World.PoiCatalog)
local Layout = require(script.Parent.Layout)
local Parchment = require(script.Parent.Parchment)
local Widgets = require(script.Parent.Widgets)

local IslandMap = {}
IslandMap.__index = IslandMap

IslandMap.MAP_SPAN = 4400
IslandMap.ZOOMS = { 1, 1.5, 2.25, 3.4 }
IslandMap.PIN = 50

-- Landmarks big enough to find your way by; the rest stay off the map so it
-- does not crowd.
IslandMap.LANDMARKS = {
	KeepTower = true,
	FrostpeakSummit = true,
	FallenTemple = true,
	EmberhollowMouth = true,
	TimberwatchTower = true,
	OldLighthouse = true,
}

-- Places shown as pins: the safe camps and the main landmarks.
function IslandMap.Places(): { { id: string, name: string, x: number, z: number } }
	local places = {}
	for _, camp in PoiCatalog.SafeZones do
		table.insert(places, { id = camp.id, name = camp.name, x = camp.x, z = camp.z })
	end
	for _, landmark in PoiCatalog.Landmarks do
		if IslandMap.LANDMARKS[landmark.id] then
			table.insert(places, { id = landmark.id, name = landmark.name, x = landmark.x, z = landmark.z })
		end
	end
	return places
end

-- World X/Z → a 0–1 position on the map image.
function IslandMap.ToMap(x: number, z: number): (number, number)
	return 0.5 + x / IslandMap.MAP_SPAN, 0.5 + z / IslandMap.MAP_SPAN
end

-- `r` = {x, y, w, h} of the visible map in the parent's pixels. opts: zoomButtons
-- ({in, out} rects in the parent), places (default IslandMap.Places()).
function IslandMap.new(parent: Instance, r, opts)
	opts = opts or {}
	local self = setmetatable({}, IslandMap)
	self.size = { r[3], r[4] }
	self.zoomIndex = 1
	self.focus = { 0.5, 0.5 }
	local clip = Widgets.Make("Frame", {
		Name = "Map",
		BackgroundColor3 = Layout.Color("paper"),
		BackgroundTransparency = 1,
		ClipsDescendants = true,
		Position = UDim2.fromOffset(r[1], r[2]),
		Size = UDim2.fromOffset(r[3], r[4]),
		ZIndex = 3,
	}, parent)
	self.clip = clip
	-- The square image fills the frame's longer side at zoom 1.
	local side = math.max(r[3], r[4])
	self.side = side
	local canvas = Widgets.Make("Frame", {
		Name = "Canvas",
		BackgroundTransparency = 1,
		Size = UDim2.fromOffset(side, side),
		ZIndex = 3,
	}, clip)
	self.canvas = canvas
	Widgets.Sprite("pm_map_island", { Name = "Island", Size = UDim2.fromScale(1, 1), ZIndex = 3 }, canvas)
	self.pins = {}
	for _, place in opts.places or IslandMap.Places() do
		local u, v = IslandMap.ToMap(place.x, place.z)
		local pin = Widgets.Make("Frame", {
			Name = place.id,
			AnchorPoint = Vector2.new(0.5, 1),
			BackgroundTransparency = 1,
			Position = UDim2.fromScale(u, v),
			Size = UDim2.fromOffset(IslandMap.PIN, IslandMap.PIN * 1.05),
			ZIndex = 5,
		}, canvas)
		Widgets.Sprite("pm_map_pin", { Name = "Art", Size = UDim2.fromScale(1, 1), ZIndex = 5 }, pin)
		local press = Parchment.Pressable(pin, nil, function()
			self:Select(if self.selected == place.id then nil else place.id)
		end)
		press.ZIndex = 6
		self.pins[place.id] = { frame = pin, place = place }
	end
	-- The name plate for the chosen pin.
	self.label = Widgets.Make("Frame", {
		Name = "Label",
		AnchorPoint = Vector2.new(0.12, 0),
		BackgroundTransparency = 1,
		Size = UDim2.fromOffset(196, 70),
		Visible = false,
		ZIndex = 7,
	}, canvas)
	Widgets.Sprite("pm_map_label", { Name = "Art", Size = UDim2.fromScale(1, 1), ZIndex = 7 }, self.label)
	self.labelText = Parchment.Text("", { 34, 8, 150, 36 }, self.label, {
		size = 22,
		align = "Center",
		scaled = true,
		z = 8,
	})
	-- The player's own position (world Map), hidden until SetMarker.
	self.marker = Widgets.Make("Frame", {
		Name = "You",
		AnchorPoint = Vector2.new(0.5, 0.5),
		BackgroundColor3 = Layout.Color("cream"),
		BorderSizePixel = 0,
		Size = UDim2.fromOffset(16, 16),
		Visible = false,
		ZIndex = 9,
	}, canvas)
	Widgets.Make("UICorner", { CornerRadius = UDim.new(0.5, 0) }, self.marker)
	Widgets.Make("UIStroke", { Color = Layout.Color("leather"), Thickness = 3 }, self.marker)
	if opts.zoomButtons then
		self.zoomIn = Parchment.Button("pm_button_zoom_in", opts.zoomButtons[1], parent, function()
			self:Zoom(1)
		end, { name = "ZoomIn", z = 8 })
		self.zoomOut = Parchment.Button("pm_button_zoom_out", opts.zoomButtons[2], parent, function()
			self:Zoom(-1)
		end, { name = "ZoomOut", z = 8 })
	end
	self:_place()
	return self
end

-- Positions the canvas so `focus` sits in the middle (kept inside the image).
function IslandMap:_place()
	local zoom = IslandMap.ZOOMS[self.zoomIndex]
	local side = self.side * zoom
	local w, h = self.size[1], self.size[2]
	local x = math.clamp(w / 2 - self.focus[1] * side, w - side, 0)
	local y = math.clamp(h / 2 - self.focus[2] * side, h - side, 0)
	self.canvas.Size = UDim2.fromOffset(side, side)
	self.canvas.Position = UDim2.fromOffset(x, y)
	if self.zoomIn then
		self.zoomIn.SetEnabled(self.zoomIndex < #IslandMap.ZOOMS)
		self.zoomOut.SetEnabled(self.zoomIndex > 1)
	end
end

function IslandMap:Zoom(step: number)
	self.zoomIndex = math.clamp(self.zoomIndex + step, 1, #IslandMap.ZOOMS)
	self:_place()
end

-- Centres the map on world X/Z.
function IslandMap:Focus(x: number, z: number)
	local u, v = IslandMap.ToMap(x, z)
	self.focus = { u, v }
	self:_place()
end

-- Shows the name plate on pin `id` (nil hides it).
function IslandMap:Select(id: string?)
	self.selected = id
	local entry = id and self.pins[id]
	self.label.Visible = entry ~= nil
	if entry then
		local u, v = IslandMap.ToMap(entry.place.x, entry.place.z)
		self.label.Position = UDim2.new(u, 0, v, -6)
		self.labelText.Text = entry.place.name
	end
end

-- The live marker at world X/Z, or hidden when nil.
function IslandMap:SetMarker(x: number?, z: number?)
	self.marker.Visible = x ~= nil and z ~= nil
	if x and z then
		local u, v = IslandMap.ToMap(x, z)
		self.marker.Position = UDim2.fromScale(u, v)
	end
end

return IslandMap
