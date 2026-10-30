-- The painted island map (art/ui/map/island.png, uploaded as pm_map_island) inside
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
-- The 1,000 px painting stays sharp to about twice its size.
IslandMap.ZOOMS = { 1, 1.4, 2 }
IslandMap.PIN = 50
-- Extra touch room round a pin, in map pixels.
IslandMap.PIN_PAD = 12
-- The painting itself (the map is art, not a kit role).
IslandMap.IMAGE = "pm_map_island"

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
-- ({in, out} rects in the parent), places (default IslandMap.Places()), zIndex
-- (default 3).
function IslandMap.new(parent: Instance, r, opts)
	opts = opts or {}
	local self = setmetatable({}, IslandMap)
	self.maid = KitModel.Maid()
	self.size = { r[3], r[4] }
	self.zoomIndex = 1
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
	-- The square image fills the frame's longer side at zoom 1.
	local side = math.max(r[3], r[4])
	self.side = side
	local canvas = Kit.Core.Make("Frame", {
		Name = "Canvas",
		BackgroundTransparency = 1,
		Size = UDim2.fromOffset(side, side),
		ZIndex = z,
	}, clip)
	self.canvas = canvas
	Kit.Art.Sprite(IslandMap.IMAGE, side, side, canvas, {
		Name = "Island",
		Size = UDim2.fromScale(1, 1),
		ZIndex = z,
	})
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
	self.marker = Kit.Icon.new(canvas, {
		name = "You",
		size = { 36, 36 },
		icon = "compass_arrow",
		anchorPoint = Vector2.new(0.5, 0.5),
		visible = false,
		zIndex = z + 6,
	}).root
	if opts.zoomButtons then
		self.zoomIn = Kit.IconButton.new(parent, {
			name = "ZoomIn",
			rect = opts.zoomButtons[1],
			variant = "plus",
			zIndex = z + 5,
			onPress = function()
				self:Zoom(1)
			end,
		})
		self.zoomOut = Kit.IconButton.new(parent, {
			name = "ZoomOut",
			rect = opts.zoomButtons[2],
			variant = "minus",
			zIndex = z + 5,
			onPress = function()
				self:Zoom(-1)
			end,
		})
		self.maid:Give(self.zoomIn)
		self.maid:Give(self.zoomOut)
	end
	self:_drag(clip)
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
				if self.zoomIndex > 1 then
					self:Focus(place.x, place.z)
				end
			end
		end,
	})
	self.maid:Give(base.maid)
	self.pins[place.id] = { frame = base.root, place = place, control = control }
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
		self.zoomIn:SetEnabled(self.zoomIndex < #IslandMap.ZOOMS)
		self.zoomOut:SetEnabled(self.zoomIndex > 1)
	end
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
	self.maid:Give(drag.InputBegan:Connect(function(input: InputObject)
		local kind = input.UserInputType
		if kind == Enum.UserInputType.MouseButton1 or kind == Enum.UserInputType.Touch then
			active, last = input, input.Position
			-- Whoever follows a moving marker leaves the map alone meanwhile.
			self.dragging = true
		end
	end))
	self.maid:Give(UserInputService.InputChanged:Connect(function(input: InputObject)
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
	end))
	self.maid:Give(UserInputService.InputEnded:Connect(function(input: InputObject)
		if input == active or input.UserInputType == Enum.UserInputType.MouseButton1 then
			active, last = nil, nil
			self.dragging = false
		end
	end))
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
		local text = Kit.Text.new(holder, {
			name = "Name",
			rect = { 30, 0, 170, 28 },
			text = entry.name,
			role = "hudSmall",
			zIndex = 8,
		}).root
		text.TextStrokeColor3 = Kit.Tokens.Color("cream")
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

function IslandMap:Destroy()
	for _, old in self.extra or {} do
		old:Destroy()
	end
	self.extra = {}
	self.maid:Clean()
end

return IslandMap
