-- The painted island map (art/ui/map/island.png, uploaded as pm_map_island) inside
-- a clipped frame: zoom in and out, drag to pan, pins for places with a name
-- plate on the chosen one, and an optional live marker. The Journal's map panel
-- uses it. The image covers MAP_SPAN studs centred on the island with −Z (north)
-- up, the span render_island.py paints (it refuses to run if the two differ). It
-- shows the generated island; an authored world would need its own painting.

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local PoiCatalog = require(ReplicatedStorage.Shared.World.PoiCatalog)
local Layout = require(script.Parent.Layout)
local Parchment = require(script.Parent.Parchment)
local Widgets = require(script.Parent.Widgets)

local IslandMap = {}
IslandMap.__index = IslandMap

IslandMap.MAP_SPAN = 4400
-- The 1,000 px painting stays sharp to about twice its size.
IslandMap.ZOOMS = { 1, 1.4, 2 }
IslandMap.PIN = 50
-- Extra touch room round a pin, in map pixels.
IslandMap.PIN_PAD = 12

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
			if self.selected == place.id then
				self:Select(nil)
			else
				self:Select(place.id)
				-- Zoomed in, the map follows the chosen pin.
				if self.zoomIndex > 1 then
					self:Focus(place.x, place.z)
				end
			end
		end, IslandMap.PIN_PAD)
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
	Widgets.Sprite(
		"pm_map_label",
		{ Name = "Art", Size = UDim2.fromScale(1, 1), ZIndex = 7 },
		self.label,
		Parchment.SliceFor("pm_map_label", { 0, 0, 196, 70 })
	)
	self.labelText = Parchment.Text("", { 28, 14, 140, 28 }, self.label, {
		size = 18,
		align = "Center",
		scaled = true,
		minSize = 10,
		z = 8,
	})
	-- The player's own position (world Map), hidden until SetMarker.
	self.marker = Widgets.Make("Frame", {
		Name = "You",
		AnchorPoint = Vector2.new(0.5, 0.5),
		BackgroundColor3 = Layout.Color("cream"),
		BorderSizePixel = 0,
		Size = UDim2.fromOffset(24, 24),
		Visible = false,
		ZIndex = 9,
	}, canvas)
	Widgets.Make("UICorner", { CornerRadius = UDim.new(0.5, 0) }, self.marker)
	Widgets.Make("UIStroke", { Color = Layout.Color("leather"), Thickness = 4 }, self.marker)
	if opts.zoomButtons then
		self.zoomIn = Parchment.Button("pm_button_zoom_in", opts.zoomButtons[1], parent, function()
			self:Zoom(1)
		end, { name = "ZoomIn", z = 8, pad = 6 })
		self.zoomOut = Parchment.Button("pm_button_zoom_out", opts.zoomButtons[2], parent, function()
			self:Zoom(-1)
		end, { name = "ZoomOut", z = 8, pad = 6 })
	end
	self:_drag(clip)
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

-- Dragging the map (mouse or finger) pans it while zoomed in.
function IslandMap:_drag(clip: Frame)
	local drag = Widgets.Make("TextButton", {
		Name = "Drag",
		Text = "",
		AutoButtonColor = false,
		BackgroundTransparency = 1,
		Selectable = false,
		Size = UDim2.fromScale(1, 1),
		ZIndex = 4,
	}, clip) :: TextButton
	local active: InputObject? = nil
	local last: Vector3? = nil
	drag.InputBegan:Connect(function(input: InputObject)
		local kind = input.UserInputType
		if kind == Enum.UserInputType.MouseButton1 or kind == Enum.UserInputType.Touch then
			active, last = input, input.Position
			-- Whoever follows a moving marker leaves the map alone meanwhile.
			self.dragging = true
		end
	end)
	UserInputService.InputChanged:Connect(function(input: InputObject)
		if active == nil or last == nil then
			return
		end
		local moved = input.UserInputType == Enum.UserInputType.MouseMovement
			or (input.UserInputType == Enum.UserInputType.Touch and input == active)
		if not moved then
			return
		end
		local delta = input.Position - last
		last = input.Position
		-- Screen pixels → map fractions at the current zoom and window scale.
		local scale = clip.AbsoluteSize.X / math.max(self.size[1], 1)
		local side = self.side * IslandMap.ZOOMS[self.zoomIndex] * math.max(scale, 0.01)
		self.focus = {
			math.clamp(self.focus[1] - delta.X / side, 0, 1),
			math.clamp(self.focus[2] - delta.Y / side, 0, 1),
		}
		self:_place()
	end)
	UserInputService.InputEnded:Connect(function(input: InputObject)
		if input == active or input.UserInputType == Enum.UserInputType.MouseButton1 then
			active, last = nil, nil
			self.dragging = false
		end
	end)
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
		-- The plate hangs below and right of the pin, or flips left near the
		-- east edge and above it near the south edge, so it stays on the map.
		local east, south = u > 0.72, v > 0.86
		self.label.AnchorPoint = Vector2.new(if east then 0.88 else 0.12, if south then 1 else 0)
		self.label.Position = UDim2.new(u, 0, v, if south then -IslandMap.PIN - 4 else -6)
		self.labelText.Text = entry.place.name
	end
end

-- Live markers (the world Map's portals and events): {{id, x, z, name, color}},
-- each a small tinted diamond with its name beside it. Replaces the last set.
function IslandMap:SetMarkers(markers)
	for _, old in self.extra or {} do
		old:Destroy()
	end
	self.extra = {}
	for _, entry in markers do
		local u, v = IslandMap.ToMap(entry.x, entry.z)
		local holder = Widgets.Make("Frame", {
			Name = entry.id,
			AnchorPoint = Vector2.new(0, 0.5),
			BackgroundTransparency = 1,
			Position = UDim2.new(u, -13, v, 0),
			Size = UDim2.fromOffset(200, 28),
			ZIndex = 8,
		}, self.canvas)
		Widgets.Sprite("pm_glyph_diamond", {
			Name = "Mark",
			ImageColor3 = entry.color or Layout.Color("ink"),
			Position = UDim2.fromOffset(0, 0),
			Size = UDim2.fromOffset(26, 28),
			ZIndex = 8,
		}, holder)
		local text = Parchment.Text(entry.name, { 30, 0, 170, 28 }, holder, { size = 18, z = 8, name = "Name" })
		text.TextStrokeColor3 = Layout.Color("cream")
		text.TextStrokeTransparency = 0.2
		table.insert(self.extra, holder)
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
