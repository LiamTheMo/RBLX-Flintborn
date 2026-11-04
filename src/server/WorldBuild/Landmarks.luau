-- The island's placeholder landmark structures (WorldBuildService), one builder
-- per PoiCatalog landmark style.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local BiomeCatalog = require(ReplicatedStorage.Shared.World.BiomeCatalog)
local IslandLayout = require(script.Parent.Parent.Rules.World.IslandLayout)
local BuildKit = require(script.Parent.BuildKit)

local Landmarks = {}

local block = BuildKit.block
local decor = BuildKit.decor
local groundAt = BuildKit.groundAt
local model = BuildKit.model
local STONE = BuildKit.STONE
local DARK_STONE = BuildKit.DARK_STONE
local WOOD = BuildKit.WOOD

local TOWER_ROOF = Color3.fromRGB(80, 56, 36)
local LIGHT_STONE = Color3.fromRGB(176, 170, 156)
local MERLON_STONE = Color3.fromRGB(112, 108, 116)
local MERLON_SPACING = 10
local MERLON_HEIGHT = 4

local function glow(parent, position: Vector3, color: Color3, range: number)
	local crystal = block(
		parent,
		"EmberCrystal",
		CFrame.new(position) * CFrame.Angles(0, math.rad(position.X % 90), math.rad(15)),
		Vector3.new(4, 10, 4),
		color,
		Enum.Material.Neon
	)
	crystal.CanCollide = false
	local light = Instance.new("PointLight")
	light.Color = color
	light.Range = range
	light.Brightness = 2
	light.Parent = crystal
	return crystal
end

-- A wall from a to b on the ground at `y`, with an optional gap in the middle.
local function wall(parent, a: Vector3, b: Vector3, height: number, gap: number?)
	local span = b - a
	local length = span.Magnitude
	local direction = span / length
	local pieces = if gap then { { 0, (length - gap) / 2 }, { (length + gap) / 2, length } } else { { 0, length } }
	for _, piece in pieces do
		local from, to = piece[1], piece[2]
		local mid = a + direction * ((from + to) / 2)
		local frame =
			CFrame.lookAt(mid + Vector3.new(0, height / 2, 0), mid + Vector3.new(0, height / 2, 0) + direction)
		block(parent, "Wall", frame, Vector3.new(6, height, to - from), DARK_STONE, Enum.Material.Slate)
		-- Battlements: a merlon every MERLON_SPACING studs along the top.
		local span = to - from
		local merlons = math.max(1, math.floor(span / MERLON_SPACING))
		for index = 1, merlons do
			local along = -span / 2 + (index - 0.5) * span / merlons
			block(
				parent,
				"Battlement",
				frame * CFrame.new(0, height / 2 + MERLON_HEIGHT / 2, along),
				Vector3.new(6.6, MERLON_HEIGHT, 5),
				MERLON_STONE,
				Enum.Material.Slate
			)
		end
	end
end

-- Column pairs (by index around the temple ring) that kept their lintel.
local TEMPLE_ARCHITRAVES = { { 1, 2 }, { 4, 5 }, { 7, 8 }, { 10, 11 } }

-- A tower's flat top (`width` studs square): a slab overhanging by a stud with a
-- merlon on each corner.
local function towerTop(parent, centre: Vector3, width: number)
	block(
		parent,
		"TowerCap",
		CFrame.new(centre + Vector3.new(0, 1.5, 0)),
		Vector3.new(width + 2, 3, width + 2),
		DARK_STONE,
		Enum.Material.Slate
	)
	for _, corner in { { -1, -1 }, { 1, -1 }, { -1, 1 }, { 1, 1 } } do
		block(
			parent,
			"Battlement",
			CFrame.new(
				centre + Vector3.new(corner[1] * (width / 2 - 1), 3 + MERLON_HEIGHT / 2, corner[2] * (width / 2 - 1))
			),
			Vector3.new(4, MERLON_HEIGHT, 4),
			MERLON_STONE,
			Enum.Material.Slate
		)
	end
end

-- A dark opening or slit set flush on a wall: decoration, never an obstacle.
local function opening(parent, name: string, cframe: CFrame, size: Vector3)
	return decor(parent, name, cframe, size, Color3.fromRGB(28, 26, 32), Enum.Material.Slate)
end

-- Heights of the broken keep tower's four corner stumps (studs above its top).
local KEEP_CROWN = { 10, 6, 12, 4 }

-- The Keep's walled courtyard (the Guardian's arena) with corner towers, gates on
-- the south (toward the ramp) and the north, and the broken keep tower behind it.
local function keep(entry)
	local keepModel = model(entry.name, { Landmark = entry.name })
	local court = IslandLayout.Courtyard
	local y = IslandLayout.KEEP_HEIGHT
	local x0, x1 = court.x - court.halfX, court.x + court.halfX
	local z0, z1 = court.z - court.halfZ, court.z + court.halfZ
	wall(keepModel, Vector3.new(x0, y, z1), Vector3.new(x1, y, z1), 22, 34)
	wall(keepModel, Vector3.new(x0, y, z0), Vector3.new(x1, y, z0), 22, 20)
	wall(keepModel, Vector3.new(x0, y, z0), Vector3.new(x0, y, z1), 18)
	wall(keepModel, Vector3.new(x1, y, z0), Vector3.new(x1, y, z1), 18)
	for _, corner in { { x0, z0 }, { x1, z0 }, { x0, z1 }, { x1, z1 } } do
		block(
			keepModel,
			"Tower",
			CFrame.new(corner[1], y + 18, corner[2]),
			Vector3.new(14, 36, 14),
			DARK_STONE,
			Enum.Material.Slate
		)
		towerTop(keepModel, Vector3.new(corner[1], y + 36, corner[2]), 14)
	end
	local base = groundAt(entry.x, entry.z)
	block(
		keepModel,
		"KeepTower",
		CFrame.new(base + Vector3.new(0, 35, 0)),
		Vector3.new(30, 70, 30),
		STONE,
		Enum.Material.Cobblestone
	)
	-- A broken crown of uneven corner stumps, buttresses at the foot, and the gate
	-- and slit windows on the face that looks over the courtyard (south).
	for index, corner in { { -1, -1 }, { 1, -1 }, { -1, 1 }, { 1, 1 } } do
		local stump = KEEP_CROWN[index]
		block(
			keepModel,
			"Crown",
			CFrame.new(base + Vector3.new(corner[1] * 10.5, 70 + stump / 2, corner[2] * 10.5)),
			Vector3.new(9, stump, 9),
			STONE,
			Enum.Material.Cobblestone
		)
		block(
			keepModel,
			"Buttress",
			CFrame.new(base + Vector3.new(corner[1] * 17, 8, corner[2] * 17)),
			Vector3.new(6, 16, 6),
			STONE,
			Enum.Material.Cobblestone
		)
	end
	opening(keepModel, "Gate", CFrame.new(base + Vector3.new(0, 7, 15.3)), Vector3.new(9, 14, 1))
	for _, slit in { { -8, 32 }, { 8, 32 }, { -8, 52 }, { 8, 52 } } do
		opening(keepModel, "Window", CFrame.new(base + Vector3.new(slit[1], slit[2], 15.3)), Vector3.new(2, 7, 1))
	end
	-- Fallen stones along the tower's east face, clear of the north gate.
	for index = 1, 3 do
		block(
			keepModel,
			"Rubble",
			CFrame.new(base + Vector3.new(21 + (index % 2) * 3, 3, (index - 2) * 9))
				* CFrame.Angles(math.rad(index * 23), math.rad(index * 41), 0),
			Vector3.new(8, 6, 7),
			STONE,
			Enum.Material.Cobblestone
		)
	end
end

-- Broken columns, a fallen roof slab and an altar on the temple mound.
local function temple(entry)
	local templeModel = model(entry.name, { Landmark = entry.name })
	local mound = IslandLayout.TempleMound
	local y = mound.height
	local columns = {}
	for index = 1, 12 do
		local angle = math.rad(index * 30)
		local height = if index % 3 == 0 then 8 else 22 + (index % 2) * 8
		local at = Vector3.new(mound.x + math.cos(angle) * 52, y, mound.z + math.sin(angle) * 52)
		columns[index] = { at = at, height = height }
		block(
			templeModel,
			"Column",
			CFrame.new(at + Vector3.new(0, height / 2, 0)),
			Vector3.new(6, height, 6),
			STONE,
			Enum.Material.Limestone
		)
		-- Every standing column keeps its capital.
		if height > 10 then
			block(
				templeModel,
				"Capital",
				CFrame.new(at + Vector3.new(0, height + 1, 0)),
				Vector3.new(8, 2, 8),
				LIGHT_STONE,
				Enum.Material.Limestone
			)
		end
	end
	-- Architraves still span the pairs of tall columns that stood side by side,
	-- resting on the shorter capital.
	for _, pair in TEMPLE_ARCHITRAVES do
		local a, b = columns[pair[1]], columns[pair[2]]
		local mid = (a.at + b.at) / 2 + Vector3.new(0, math.min(a.height, b.height) + 3.5, 0)
		block(
			templeModel,
			"Architrave",
			CFrame.lookAt(mid, mid + (b.at - a.at)),
			Vector3.new(5, 3, (b.at - a.at).Magnitude),
			LIGHT_STONE,
			Enum.Material.Limestone
		)
	end
	-- Two worn steps around the altar.
	block(
		templeModel,
		"AltarStep",
		CFrame.new(mound.x, y + 0.5, mound.z),
		Vector3.new(22, 1, 17),
		LIGHT_STONE,
		Enum.Material.Limestone
	)
	block(
		templeModel,
		"AltarStep",
		CFrame.new(mound.x, y + 1.5, mound.z),
		Vector3.new(16, 1, 12),
		STONE,
		Enum.Material.Limestone
	)
	block(
		templeModel,
		"FallenColumn",
		CFrame.new(mound.x + 20, y + 3, mound.z + 30) * CFrame.Angles(0, math.rad(35), math.rad(90)),
		Vector3.new(6, 26, 6),
		STONE,
		Enum.Material.Limestone
	)
	block(
		templeModel,
		"RoofSlab",
		CFrame.new(mound.x - 24, y + 4, mound.z - 18) * CFrame.Angles(math.rad(12), math.rad(20), 0),
		Vector3.new(36, 3, 22),
		STONE,
		Enum.Material.Limestone
	)
	block(
		templeModel,
		"Altar",
		CFrame.new(mound.x, y + 2.5, mound.z),
		Vector3.new(10, 5, 6),
		DARK_STONE,
		Enum.Material.Slate
	)
end

local function tower(entry)
	local towerModel = model(entry.name, { Landmark = entry.name })
	local base = groundAt(entry.x, entry.z)
	for _, corner in { { -7, -7 }, { 7, -7 }, { -7, 7 }, { 7, 7 } } do
		block(
			towerModel,
			"Leg",
			CFrame.new(base + Vector3.new(corner[1], 20, corner[2])),
			Vector3.new(2, 40, 2),
			WOOD,
			Enum.Material.Wood
		)
	end
	block(
		towerModel,
		"Platform",
		CFrame.new(base + Vector3.new(0, 40, 0)),
		Vector3.new(18, 1.5, 18),
		WOOD,
		Enum.Material.WoodPlanks
	)
	block(
		towerModel,
		"Roof",
		CFrame.new(base + Vector3.new(0, 50, 0)),
		Vector3.new(20, 1.5, 20),
		TOWER_ROOF,
		Enum.Material.WoodPlanks
	)
	-- Rails round the lookout, posts up to the roof and a stepped, tapering roof.
	for _, side in { -1, 1 } do
		block(
			towerModel,
			"Rail",
			CFrame.new(base + Vector3.new(0, 42, side * 8.75)),
			Vector3.new(18, 2.5, 0.5),
			WOOD,
			Enum.Material.Wood
		)
		block(
			towerModel,
			"Rail",
			CFrame.new(base + Vector3.new(side * 8.75, 42, 0)),
			Vector3.new(0.5, 2.5, 18),
			WOOD,
			Enum.Material.Wood
		)
	end
	for _, corner in { { -8.5, -8.5 }, { 8.5, -8.5 }, { -8.5, 8.5 }, { 8.5, 8.5 } } do
		block(
			towerModel,
			"RoofPost",
			CFrame.new(base + Vector3.new(corner[1], 45, corner[2])),
			Vector3.new(1.2, 8.5, 1.2),
			WOOD,
			Enum.Material.Wood
		)
	end
	for step = 1, 3 do
		local width = 20 - step * 5
		block(
			towerModel,
			"RoofStep",
			CFrame.new(base + Vector3.new(0, 50.75 + step * 1.5 - 0.75, 0)),
			Vector3.new(width, 1.5, width),
			if step % 2 == 0 then TOWER_ROOF else TOWER_ROOF:Lerp(Color3.new(1, 1, 1), 0.2),
			Enum.Material.WoodPlanks
		)
	end
end

-- Basalt pillars and a lintel framing the tunnel, and glowing crystals inside.
local function caveMouth(entry)
	local caveModel = model(entry.name, { Landmark = entry.name })
	local cave = BiomeCatalog.Zones.EmberhollowCaves
	local room, tunnel = cave.interior, cave.tunnel
	-- The gateway stands where the tunnel's open trench meets the ground outside.
	local mouthZ = tunnel.toZ - 20
	local floor = room.floor
	local tunnelHeight = tunnel.ceiling - floor
	for _, side in { -1, 1 } do
		block(
			caveModel,
			"MouthPillar",
			CFrame.new(tunnel.x + side * (tunnel.halfWidth + 3), floor + tunnelHeight / 2, mouthZ),
			Vector3.new(6, tunnelHeight, 6),
			Color3.fromRGB(46, 32, 30),
			Enum.Material.Basalt
		)
	end
	block(
		caveModel,
		"Lintel",
		CFrame.new(tunnel.x, tunnel.ceiling + 2, mouthZ),
		Vector3.new(tunnel.halfWidth * 2 + 12, 4, 6),
		Color3.fromRGB(46, 32, 30),
		Enum.Material.Basalt
	)
	local ember = Color3.fromRGB(255, 120, 40)
	glow(caveModel, Vector3.new(tunnel.x, floor + 5, tunnel.fromZ + 40), ember, 40)
	for index = 0, 9 do
		local along = (index % 5) / 4
		local side = if index < 5 then -1 else 1
		local x = room.x - room.halfX + 30 + along * (room.halfX * 2 - 60)
		glow(caveModel, Vector3.new(x, floor + 5, room.z + side * (room.halfZ - 6)), ember, 60)
	end
	for _, side in { -1, 1 } do
		glow(caveModel, Vector3.new(room.x + side * (room.halfX - 6), floor + 5, room.z), ember, 60)
	end
end

local function peak(entry)
	local peakModel = model(entry.name, { Landmark = entry.name })
	local base = groundAt(entry.x, entry.z)
	for index = 1, 3 do
		block(
			peakModel,
			"Cairn",
			CFrame.new(base + Vector3.new(0, index * 2.5 - 1, 0)) * CFrame.Angles(0, math.rad(index * 37), 0),
			Vector3.new(8 - index * 2, 2.5, 8 - index * 2),
			STONE,
			Enum.Material.Slate
		)
	end
	block(
		peakModel,
		"Pole",
		CFrame.new(base + Vector3.new(0, 14, 0)),
		Vector3.new(0.6, 20, 0.6),
		WOOD,
		Enum.Material.Wood
	)
	block(
		peakModel,
		"Banner",
		CFrame.new(base + Vector3.new(2.6, 21, 0)),
		Vector3.new(5, 3, 0.2),
		Color3.fromRGB(190, 40, 40),
		Enum.Material.Fabric
	)
end

-- A plank bridge across the river at the landmark.
local function bridge(entry)
	local bridgeModel = model(entry.name, { Landmark = entry.name })
	local river = IslandLayout.RiverAt(entry.x, entry.z)
	if river == nil then
		return
	end
	local points = river.river.points
	local nearest, along = nil, math.huge
	for index = 2, #points do
		local mid = (points[index] + points[index - 1]) / 2
		local distance = (Vector3.new(entry.x, 0, entry.z) - mid).Magnitude
		if distance < along then
			nearest, along = index, distance
		end
	end
	local direction = (points[nearest] - points[nearest - 1]).Unit
	local across = Vector3.new(-direction.Z, 0, direction.X)
	local center = Vector3.new(entry.x, river.surface + 3, entry.z)
	local length = river.halfWidth * 2 + 24
	block(
		bridgeModel,
		"Deck",
		CFrame.lookAt(center, center + across),
		Vector3.new(10, 1.2, length),
		WOOD,
		Enum.Material.WoodPlanks
	)
	for _, side in { -1, 1 } do
		local rail = center + direction * (side * 4.6) + Vector3.new(0, 2, 0)
		block(
			bridgeModel,
			"Rail",
			CFrame.lookAt(rail, rail + across),
			Vector3.new(0.6, 0.6, length),
			WOOD,
			Enum.Material.Wood
		)
	end
end

local function lighthouse(entry)
	local lighthouseModel = model(entry.name, { Landmark = entry.name })
	local base = groundAt(entry.x, entry.z)
	local shaft = block(
		lighthouseModel,
		"Tower",
		CFrame.new(base + Vector3.new(0, 22, 0)) * CFrame.Angles(0, 0, math.rad(90)),
		Vector3.new(48, 14, 14),
		Color3.fromRGB(214, 206, 192),
		Enum.Material.Cobblestone
	)
	shaft.Shape = Enum.PartType.Cylinder
	-- Two red bands round the shaft, a gallery under the lamp and a stepped cap over it.
	for _, bandY in { 10, 30 } do
		local band = decor(
			lighthouseModel,
			"Band",
			CFrame.new(base + Vector3.new(0, bandY, 0)) * CFrame.Angles(0, 0, math.rad(90)),
			Vector3.new(6, 14.6, 14.6),
			Color3.fromRGB(190, 60, 50),
			Enum.Material.SmoothPlastic
		)
		band.Shape = Enum.PartType.Cylinder
	end
	block(
		lighthouseModel,
		"Gallery",
		CFrame.new(base + Vector3.new(0, 46.6, 0)),
		Vector3.new(13, 1.2, 13),
		DARK_STONE,
		Enum.Material.Slate
	)
	local lamp = glow(lighthouseModel, base + Vector3.new(0, 48, 0), Color3.fromRGB(255, 230, 160), 80)
	lamp.Size = Vector3.new(6, 6, 6)
	block(
		lighthouseModel,
		"Cap",
		CFrame.new(base + Vector3.new(0, 52.75, 0)),
		Vector3.new(9, 1.5, 9),
		Color3.fromRGB(190, 60, 50),
		Enum.Material.SmoothPlastic
	)
	block(
		lighthouseModel,
		"Cap",
		CFrame.new(base + Vector3.new(0, 54.5, 0)),
		Vector3.new(4.5, 2, 4.5),
		Color3.fromRGB(190, 60, 50),
		Enum.Material.SmoothPlastic
	)
end

local function roots(entry)
	local rootsModel = model(entry.name, { Landmark = entry.name })
	local base = groundAt(entry.x, entry.z)
	for index = 1, 5 do
		block(
			rootsModel,
			"Root",
			CFrame.new(base + Vector3.new(0, 18, 0)) * CFrame.Angles(0, math.rad(index * 72), math.rad(35)),
			Vector3.new(8, 50, 8),
			Color3.fromRGB(96, 68, 44),
			Enum.Material.Wood
		)
	end
	block(
		rootsModel,
		"Trunk",
		CFrame.new(base + Vector3.new(0, 45, 0)),
		Vector3.new(18, 90, 18),
		Color3.fromRGB(86, 60, 40),
		Enum.Material.Wood
	)
end

local function monoliths(entry)
	local monolithModel = model(entry.name, { Landmark = entry.name })
	for index = 1, 3 do
		local x, z = entry.x + (index - 2) * 18, entry.z
		block(
			monolithModel,
			"Monolith",
			CFrame.new(groundAt(x, z) + Vector3.new(0, 28, 0)) * CFrame.Angles(0, math.rad(index * 20), 0),
			Vector3.new(8, 60, 3),
			Color3.fromRGB(34, 32, 40),
			Enum.Material.Slate
		)
	end
end

local LANDMARKS = {
	Keep = keep,
	Temple = temple,
	Tower = tower,
	CaveMouth = caveMouth,
	Peak = peak,
	Bridge = bridge,
	Lighthouse = lighthouse,
	Roots = roots,
	Monoliths = monoliths,
}

-- Builds the landmark for `entry` (a PoiCatalog landmark); styles without a
-- builder are skipped.
function Landmarks.Build(entry)
	local build = LANDMARKS[entry.style]
	if build then
		build(entry)
	end
end

return Landmarks
