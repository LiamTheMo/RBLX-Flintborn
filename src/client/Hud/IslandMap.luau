-- The painted island map (art/ui/map/island.png, the kit role map.island) inside
-- a clipped frame: zoom in and out, drag to pan, pins for places with a name
-- plate on the chosen one, and an optional live marker. Drawn from the UI kit
-- (pins, plate, zoom buttons, marker); the Journal's map tab, the world Map and
-- the Play window use it. The image covers MAP_SPAN studs centred on the island
-- with −Z (north) up, the span render_island.py paints (it refuses to run if the
-- two differ). It shows the generated island; an authored world would need its
-- own painting.

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local KitModel = require(ReplicatedStorage.Shared.UI.KitModel)
local PoiCatalog = require(ReplicatedStorage.Shared.World.PoiCatalog)
local Kit = require(script.Parent.Kit)

local IslandMap = {}
IslandMap.__index = IslandMap

IslandMap.MAP_SPAN = 4400
-- Zoom levels. The map draws the 1,000 px painting where it is shown small (the
-- Journal) and its 2,040 px copy where it is magnified (map.island's `hi`
-- tiles, once uploaded), which stays at or under 1x at zoom 1 on the world map
-- even at 1440p.
IslandMap.ZOOMS = { 1, 1.5, 2.2, 3 }
-- The zoom factor of one mouse wheel notch.
IslandMap.WHEEL_STEP = 1.2
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

-- Player markers (kit dot roles, design px): you, and your tribe mates.
IslandMap.YOU_DOT = "dot.yellow"
IslandMap.MATE_DOT = "dot.green"
IslandMap.YOU_SIZE = 26
IslandMap.MATE_SIZE = 22

-- The map rotation (degrees, east = 0, clockwise) of a world look direction:
-- the map has +X to the right and +Z down.
function IslandMap.Heading(look: Vector3): number
	return math.deg(math.atan2(look.Z, look.X))
end

-- A player marker, "o>": the kit's painted dot (`dot`, a dot role) on a paper
-- disc with an ink point at its east edge, in a `size` design px box centred on
-- the Position. It points east; its Rotation is the heading (IslandMap.Heading).
function IslandMap.Arrow(parent: Instance, name: string, dot: string, size: number, z: number): Frame
	local holder = Kit.Core.Make("Frame", {
		Name = name,
		AnchorPoint = Vector2.new(0.5, 0.5),
		BackgroundTransparency = 1,
		Size = UDim2.fromOffset(size, size),
		ZIndex = z,
	}, parent) :: Frame
	-- The point: an ink square turned 45° behind the disc, so only its tip shows.
	Kit.Core.Make("Frame", {
		Name = "Point",
		AnchorPoint = Vector2.new(0.5, 0.5),
		BackgroundColor3 = Kit.Tokens.Color("ink"),
		BorderSizePixel = 0,
		Position = UDim2.fromScale(0.82, 0.5),
		Rotation = 45,
		Size = UDim2.fromScale(0.5, 0.5),
		ZIndex = z,
	}, holder)
	-- A paper disc with an ink rim under the dot keeps it readable on the painting.
	local backing = Kit.Core.Make("Frame", {
		Name = "Backing",
		AnchorPoint = Vector2.new(0.5, 0.5),
		BackgroundColor3 = Kit.Tokens.Color("paper"),
		BorderSizePixel = 0,
		Position = UDim2.fromScale(0.5, 0.5),
		Size = UDim2.fromScale(0.78, 0.78),
		ZIndex = z + 1,
	}, holder)
	Kit.Core.Make("UICorner", { CornerRadius = UDim.new(0.5, 0) }, backing)
	Kit.Core.Make("UIStroke", { Color = Kit.Tokens.Color("ink"), Thickness = 1.5 }, backing)
	local d = math.round(size * 0.7)
	local disc = Kit.Core.Make("Frame", {
		Name = "Dot",
		AnchorPoint = Vector2.new(0.5, 0.5),
		BackgroundTransparency = 1,
		Position = UDim2.fromScale(0.5, 0.5),
		Size = UDim2.fromOffset(d, d),
		ZIndex = z + 2,
	}, holder)
	Kit.Art.Plate(disc, dot, d, d, { z = z + 2 })
	return holder
end

-- `r` = {x, y, w, h} of the visible map in the parent's pixels. opts: zoomButtons
-- ({in, out} rects in the parent), places (default IslandMap.Places()), zIndex
-- (default 3), fit (the whole island at zoom 1).
function IslandMap.new(parent: Instance, r, opts)
	opts = opts or {}
	local self = setmetatable({}, IslandMap)
	self.maid = KitModel.Maid()
	self.size = { r[3], r[4] }
	-- 1 shows the whole image across the frame; up to the last of ZOOMS.
	self.zoom = 1
	self.focus = { 0.5, 0.5 }
	local z = opts.zIndex or 3
	local clip = Kit.Core.Make("Frame", {
		Name = "Map",
		BackgroundTransparency = 1,
		ClipsDescendants = true,
		Position = UDim2.fromOffset(r[1], r[2]),
		Size = UDim2.fromOffset(r[3], r[4]),
		ZIndex = z,
	}, parent)
	self.maid:Give(clip)
	self.clip = clip
	-- The square image fills the frame's longer side at zoom 1, or with `fit` its
	-- shorter side, so the whole island shows.
	local side = if opts.fit then math.min(r[3], r[4]) else math.max(r[3], r[4])
	self.side = side
	local canvas = Kit.Core.Make("Frame", {
		Name = "Canvas",
		BackgroundTransparency = 1,
		Size = UDim2.fromOffset(side, side),
		ZIndex = z,
	}, clip)
	self.canvas = canvas
	local island = Kit.Picture.new(canvas, { name = "Island", size = { side, side }, role = "map.island", zIndex = z })
	-- It follows the canvas as it zooms.
	island.root.Size = UDim2.fromScale(1, 1)
	self.maid:Give(island)
	self.pins = {}
	for _, place in opts.places or IslandMap.Places() do
		self:_pin(place, z)
	end
	-- The name plate for the chosen pin.
	self.label = Kit.Core.Make("Frame", {
		Name = "Label",
		AnchorPoint = Vector2.new(0.12, 0),
		BackgroundTransparency = 1,
		Size = UDim2.fromOffset(196, 56),
		Visible = false,
		ZIndex = z + 4,
	}, canvas)
	Kit.Art.Plate(self.label, "panel.plaque", 196, 56, { z = z + 4 })
	self.labelText = Kit.Text.new(self.label, {
		name = "Name",
		rect = { 16, 4, 164, 46 },
		text = "",
		role = "rowTitle",
		align = "Center",
		scaled = true,
		zIndex = z + 5,
	}).root
	-- The player's own position (world Map), hidden until SetMarker.
	self.marker = IslandMap.Arrow(canvas, "You", IslandMap.YOU_DOT, IslandMap.YOU_SIZE, z + 6)
	self.marker.Visible = false
	self.mates = {}
	self.z = z
	-- The drag pad first, so the zoom buttons (drawn later and higher) take
	-- presses over it.
	self:_drag(clip)
	if opts.zoomButtons then
		self.zoomIn = Kit.IconButton.new(parent, {
			name = "ZoomIn",
			rect = opts.zoomButtons[1],
			-- Above the map and its drag pad (z + 1), so they stay tappable.
			variant = "plus",
			zIndex = z + 8,
			onPress = function()
				self:Zoom(1)
			end,
		})
		self.zoomOut = Kit.IconButton.new(parent, {
			name = "ZoomOut",
			rect = opts.zoomButtons[2],
			variant = "minus",
			zIndex = z + 8,
			onPress = function()
				self:Zoom(-1)
			end,
		})
		self.maid:Give(self.zoomIn)
		self.maid:Give(self.zoomOut)
	end
	self:_place()
	return self
end

-- A pressable pin for `place`: tap to show its name, tap again to hide it.
function IslandMap:_pin(place, z: number)
	local u, v = IslandMap.ToMap(place.x, place.z)
	local w, h = IslandMap.PIN, math.floor(IslandMap.PIN * 1.12)
	local base = Kit.Core.Root(self.canvas, "MapPin", "map.pin", {
		name = place.id,
		size = { w, h },
		position = UDim2.fromScale(u, v),
		anchorPoint = Vector2.new(0.5, 1),
		zIndex = z + 2,
	}, w, h)
	Kit.Art.Icon(base.visual, "map_pin", { 0, 0, w, h }, { z = z + 2, name = "Art" })
	local control = Kit.Interact.attach(base, {
		pad = IslandMap.PIN_PAD,
		hoverScale = true,
		onPress = function()
			if self.selected == place.id then
				self:Select(nil)
			else
				self:Select(place.id)
				-- Zoomed in, the map follows the chosen pin.
				if self.zoom > 1 then
					self:Focus(place.x, place.z)
				end
			end
		end,
	})
	self.maid:Give(base.maid)
	self.pins[place.id] = { frame = base.root, place = place, control = control }
end

-- Positions the canvas so `focus` sits in the middle (kept inside the image),
-- and keeps `focus` on what is actually shown.
function IslandMap:_place()
	local side = self.side * self.zoom
	local w, h = self.size[1], self.size[2]
	-- An image narrower than the frame is centred; a wider one pans, kept inside.
	local function offset(span: number, focus: number): number
		if side <= span then
			return (span - side) / 2
		end
		return math.clamp(span / 2 - focus * side, span - side, 0)
	end
	local x = offset(w, self.focus[1])
	local y = offset(h, self.focus[2])
	self.focus = { (w / 2 - x) / side, (h / 2 - y) / side }
	self.canvas.Size = UDim2.fromOffset(side, side)
	self.canvas.Position = UDim2.fromOffset(x, y)
	if self.zoomIn then
		self.zoomIn:SetEnabled(self.zoom < IslandMap.ZOOMS[#IslandMap.ZOOMS])
		self.zoomOut:SetEnabled(self.zoom > 1)
	end
end

-- Multiplies the zoom by `factor` (kept between 1 and the last of ZOOMS) and
-- keeps the map under screen point `point` where it is: the wheel at the mouse,
-- a pinch at the fingers' midpoint.
function IslandMap:ZoomAt(factor: number, point: Vector2)
	local zoom = math.clamp(self.zoom * factor, 1, IslandMap.ZOOMS[#IslandMap.ZOOMS])
	local canvas, clip = self.canvas.AbsoluteSize, self.clip.AbsoluteSize
	if zoom == self.zoom or canvas.X <= 0 or clip.X <= 0 then
		return
	end
	-- The image fraction under the point, and the point in the frame's design px.
	local f = (point - self.canvas.AbsolutePosition) / canvas
	local p = (point - self.clip.AbsolutePosition) * (self.size[1] / clip.X)
	local side = self.side * zoom
	self.zoom = zoom
	self.focus = { f.X + (self.size[1] / 2 - p.X) / side, f.Y + (self.size[2] / 2 - p.Y) / side }
	self:_place()
end

-- Dragging the map (mouse or finger) pans it while zoomed in.
function IslandMap:_drag(clip: Frame)
	local drag = Kit.Core.Make("TextButton", {
		Name = "Drag",
		Text = "",
		AutoButtonColor = false,
		BackgroundTransparency = 1,
		Selectable = false,
		Size = UDim2.fromScale(1, 1),
		ZIndex = clip.ZIndex + 1,
	}, clip) :: TextButton
	local active: InputObject? = nil
	local last: Vector3? = nil
	-- Fingers on the map: one pans, two pinch to zoom about their midpoint.
	local touches: { [InputObject]: Vector2 } = {}
	local pinch: number? = nil
	local function fingers(): { Vector2 }
		local list = {}
		for _, at in touches do
			table.insert(list, at)
		end
		return list
	end
	self.maid:Give(drag.InputBegan:Connect(function(input: InputObject)
		local kind = input.UserInputType
		if kind == Enum.UserInputType.Touch then
			touches[input] = Vector2.new(input.Position.X, input.Position.Y)
			local list = fingers()
			if #list == 2 then
				active, last = nil, nil
				pinch = (list[1] - list[2]).Magnitude
			end
		end
		if kind == Enum.UserInputType.MouseButton1 or (kind == Enum.UserInputType.Touch and pinch == nil) then
			active, last = input, input.Position
		end
		if kind == Enum.UserInputType.MouseButton1 or kind == Enum.UserInputType.Touch then
			-- Whoever follows a moving marker leaves the map alone from now on.
			self.panned = true
		end
	end))
	self.maid:Give(drag.InputChanged:Connect(function(input: InputObject)
		if input.UserInputType == Enum.UserInputType.MouseWheel then
			self.panned = true
			self:ZoomAt(IslandMap.WHEEL_STEP ^ input.Position.Z, Vector2.new(input.Position.X, input.Position.Y))
		end
	end))
	self.maid:Give(UserInputService.InputChanged:Connect(function(input: InputObject)
		if touches[input] then
			touches[input] = Vector2.new(input.Position.X, input.Position.Y)
			local list = fingers()
			if pinch and #list == 2 then
				local distance = (list[1] - list[2]).Magnitude
				if pinch > 0 and distance > 0 then
					self:ZoomAt(distance / pinch, (list[1] + list[2]) / 2)
				end
				pinch = distance
				return
			end
		end
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
		local side = self.side * self.zoom * math.max(scale, 0.01)
		self.focus = {
			math.clamp(self.focus[1] - delta.X / side, 0, 1),
			math.clamp(self.focus[2] - delta.Y / side, 0, 1),
		}
		self:_place()
	end))
	self.maid:Give(UserInputService.InputEnded:Connect(function(input: InputObject)
		if touches[input] then
			touches[input] = nil
			local list = fingers()
			if pinch and #list == 1 then
				-- The finger left after a pinch carries on panning.
				pinch = nil
				for touch in touches do
					active, last = touch, touch.Position
				end
				return
			end
			pinch = nil
		end
		if input == active or input.UserInputType == Enum.UserInputType.MouseButton1 then
			active, last = nil, nil
		end
	end))
end

-- The zoom buttons: the next level of ZOOMS in (`step` > 0) or out from here.
function IslandMap:Zoom(step: number)
	local levels = IslandMap.ZOOMS
	local zoom = if step > 0 then levels[#levels] else 1
	for index = 1, #levels do
		local level = if step > 0 then levels[index] else levels[#levels + 1 - index]
		if (step > 0 and level > self.zoom + 0.01) or (step < 0 and level < self.zoom - 0.01) then
			zoom = level
			break
		end
	end
	self.zoom = zoom
	self:_place()
end

-- Centres the map on world X/Z.
function IslandMap:Focus(x: number, z: number)
	local u, v = IslandMap.ToMap(x, z)
	self.focus = { u, v }
	self:_place()
end

-- Shows the name plate on pin `id` (nil hides it); the pin draws selected.
function IslandMap:Select(id: string?)
	self.selected = id
	for pinId, pin in self.pins do
		pin.control:SetSelected(pinId == id)
	end
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
-- each a small dot in its colour with its name beside it. Replaces the last set.
function IslandMap:SetMarkers(markers)
	for _, old in self.extra or {} do
		old:Destroy()
	end
	self.extra = {}
	for _, entry in markers do
		local u, v = IslandMap.ToMap(entry.x, entry.z)
		local holder = Kit.Core.Make("Frame", {
			Name = entry.id,
			AnchorPoint = Vector2.new(0, 0.5),
			BackgroundTransparency = 1,
			Position = UDim2.new(u, -13, v, 0),
			Size = UDim2.fromOffset(200, 28),
			ZIndex = 8,
		}, self.canvas)
		local dot = Kit.Core.Make("Frame", {
			Name = "Mark",
			BackgroundTransparency = 1,
			Position = UDim2.fromOffset(2, 3),
			Size = UDim2.fromOffset(22, 22),
			ZIndex = 8,
		}, holder)
		Kit.Art.Plate(dot, "dot.yellow", 22, 22, { z = 8, tint = entry.color })
		-- Names over the painting: the Kit's paper outline keeps them readable.
		Kit.Text.new(holder, {
			name = "Name",
			rect = { 30, 0, 170, 28 },
			text = entry.name,
			role = "hudSmall",
			outline = true,
			outlineThickness = 2,
			zIndex = 8,
		})
		table.insert(self.extra, holder)
	end
end

-- Your marker at world X/Z facing `heading` (IslandMap.Heading), or hidden when nil.
function IslandMap:SetMarker(x: number?, z: number?, heading: number?)
	self.marker.Visible = x ~= nil and z ~= nil
	if x and z then
		local u, v = IslandMap.ToMap(x, z)
		self.marker.Position = UDim2.fromScale(u, v)
		self.marker.Rotation = heading or 0
	end
end

-- Tribe mates' markers with their names: {{userId, name, x, z, heading}}.
-- Replaces the last set.
function IslandMap:SetMates(mates)
	local seen = {}
	for _, mate in mates do
		local entry = self.mates[mate.userId]
		if entry == nil then
			local arrow = IslandMap.Arrow(self.canvas, "Mate", IslandMap.MATE_DOT, IslandMap.MATE_SIZE, self.z + 5)
			local label = Kit.Text.new(self.canvas, {
				name = "MateName",
				rect = { 0, 0, 170, 28 },
				text = mate.name,
				role = "hudSmall",
				outline = true,
				outlineThickness = 2,
				zIndex = self.z + 5,
			}).root
			label.AnchorPoint = Vector2.new(0, 0.5)
			entry = { arrow = arrow, label = label }
			self.mates[mate.userId] = entry
		end
		seen[mate.userId] = true
		local u, v = IslandMap.ToMap(mate.x, mate.z)
		entry.arrow.Position = UDim2.fromScale(u, v)
		entry.arrow.Rotation = mate.heading or 0
		entry.label.Position = UDim2.new(u, IslandMap.MATE_SIZE + 4, v, 0)
		entry.label.Text = mate.name
	end
	for userId, entry in self.mates do
		if not seen[userId] then
			entry.arrow:Destroy()
			entry.label:Destroy()
			self.mates[userId] = nil
		end
	end
end

function IslandMap:Destroy()
	for _, old in self.extra or {} do
		old:Destroy()
	end
	self.extra = {}
	self:SetMates({})
	self.maid:Clean()
end

return IslandMap
