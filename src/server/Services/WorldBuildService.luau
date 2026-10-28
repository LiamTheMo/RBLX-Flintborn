-- The play-world island (GDD §3, §54, Q22, Q33, Q57, Q160a). Uses an authored map
-- when the place has one (a "ShatteredCrater" model in Workspace or
-- ServerStorage.Maps); otherwise builds the placeholder island at startup from
-- IslandLayout as smooth Terrain: a 6,144-stud ocean, the 4,096-stud island with
-- per-zone materials, Crater Lake and its river, the Emberhollow hill with an
-- enterable cave, and a few simple placeholder structures (the Keep's walled
-- courtyard, the Fallen Temple ruins, Timberwatch's tower, bridges, camps). Every
-- gameplay POI is a tagged part so the other services read the map without
-- coordinates. The build runs in the background from Init, yielding between
-- terrain chunks, so every other service starts at once (matchmaking keeps
-- reporting); services that read the map's terrain or tagged parts, and Play
-- admission, wait for WorldState's ready flag. A generated island saved into the
-- place (its folder carries the current GeneratedLayout version) is reused as is.
-- World place only.

local CollectionService = game:GetService("CollectionService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerStorage = game:GetService("ServerStorage")

local BiomeCatalog = require(ReplicatedStorage.Shared.World.BiomeCatalog)
local IslandLayout = require(ReplicatedStorage.Shared.World.IslandLayout)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local PoiCatalog = require(ReplicatedStorage.Shared.World.PoiCatalog)
local WorldState = require(ReplicatedStorage.Shared.World.WorldState)

local WorldBuildService = {}

WorldBuildService.MAP_NAME = "ShatteredCrater"
-- Bump when the generated layout changes, so islands saved into a place rebuild.
WorldBuildService.LAYOUT_VERSION = 2
-- Terrain is written in square chunks (16 × 16 voxel columns).
WorldBuildService.CHUNK = 64
WorldBuildService.OCEAN_TILE = 1024
-- Seconds of work between yields.
WorldBuildService.YIELD_SECONDS = 0.05

local VOXEL = 4
local folder = nil
local lastYield = 0

local function breathe()
	if os.clock() - lastYield >= WorldBuildService.YIELD_SECONDS then
		task.wait()
		lastYield = os.clock()
	end
end

local function part(props, tags)
	local instance = Instance.new(props.ClassName or "Part")
	instance.Anchored = true
	instance.TopSurface = Enum.SurfaceType.Smooth
	instance.BottomSurface = Enum.SurfaceType.Smooth
	for key, value in props do
		if key ~= "ClassName" then
			instance[key] = value
		end
	end
	for _, tag in tags or {} do
		CollectionService:AddTag(instance, tag)
		if tag == "GeneratedStructure" then
			-- Map ruins are never claimable (Q39); BuildingService marks tagged parts at
			-- Start, before this background build has made them.
			instance:SetAttribute("Generated", true)
		end
	end
	instance.Parent = props.Parent or folder
	return instance
end

-- An invisible anchor the gameplay services read by tag.
local function anchor(name: string, position: Vector3, tag: string, attributes)
	local marker = part({
		Name = name,
		Size = Vector3.new(2, 2, 2),
		CFrame = CFrame.new(position + Vector3.new(0, 1, 0)),
		Transparency = 1,
		CanCollide = false,
		CanQuery = false,
		CanTouch = false,
	}, { tag })
	for key, value in attributes or {} do
		marker:SetAttribute(key, value)
	end
	return marker
end

local function groundAt(x: number, z: number): Vector3
	return Vector3.new(x, IslandLayout.HeightAt(x, z), z)
end

-- Terrain ------------------------------------------------------------------------

local materialCache = {}
local function material(name: string): Enum.Material
	local value = materialCache[name]
	if value == nil then
		value = Enum.Material[name]
		materialCache[name] = value
	end
	return value
end

-- The open ocean out to the full 6,144 studs: a sand floor and water to sea level.
local function ocean(terrain: Terrain)
	local half = BiomeCatalog.WORLD_SIZE / 2
	local tile = WorldBuildService.OCEAN_TILE
	local floor = IslandLayout.SEA_FLOOR
	for x = -half, half - tile, tile do
		for z = -half, half - tile, tile do
			local center = Vector3.new(x + tile / 2, 0, z + tile / 2)
			terrain:FillBlock(
				CFrame.new(center + Vector3.new(0, floor - 4, 0)),
				Vector3.new(tile, 8, tile),
				Enum.Material.Sand
			)
			terrain:FillBlock(
				CFrame.new(center + Vector3.new(0, floor / 2, 0)),
				Vector3.new(tile, -floor, tile),
				Enum.Material.Water
			)
			breathe()
		end
	end
end

-- Surface material per lattice point (zone, height and steepness), worked out once.
local latticeMaterials = {}
local function latticeMaterial(ix: number, iz: number): Enum.Material
	local key = ix * 4096 + iz
	local cached = latticeMaterials[key]
	if cached then
		return cached
	end
	local step = IslandLayout.LATTICE
	local x, z = ix * step - IslandLayout.BUILD_HALF, iz * step - IslandLayout.BUILD_HALF
	local h = IslandLayout.LatticeHeight(ix, iz)
	local gx = IslandLayout.LatticeHeight(ix + 1, iz) - IslandLayout.LatticeHeight(ix - 1, iz)
	local gz = IslandLayout.LatticeHeight(ix, iz + 1) - IslandLayout.LatticeHeight(ix, iz - 1)
	local slope = math.sqrt(gx * gx + gz * gz) / (2 * step)
	cached = material(IslandLayout.SurfaceMaterial(BiomeCatalog.ZoneAt(x, z), x, z, h, slope))
	latticeMaterials[key] = cached
	return cached
end

-- One chunk: solid rock up to just under its lowest ground, then voxel columns with
-- fractional tops (smooth slopes), surface material and water up to the lake,
-- river or sea surface. Chunks entirely on the open sea floor are left to the ocean.
local function chunk(terrain: Terrain, cx: number, cz: number)
	local size = WorldBuildService.CHUNK
	local columns = size / VOXEL
	local half = IslandLayout.BUILD_HALF
	local step = IslandLayout.LATTICE
	local heights, waters, surfaces = table.create(columns * columns), table.create(columns * columns), {}
	local low, top, high = math.huge, -math.huge, -math.huge
	for i = 1, columns do
		for k = 1, columns do
			local x, z = cx + (i - 0.5) * VOXEL, cz + (k - 0.5) * VOXEL
			local h = IslandLayout.HeightAt(x, z)
			local w = IslandLayout.WaterLevelAt(x, z)
			local index = (i - 1) * columns + k
			heights[index], waters[index] = h, w
			surfaces[index] = latticeMaterial(math.round((x + half) / step), math.round((z + half) / step))
			low, top, high = math.min(low, h), math.max(top, h), math.max(high, h, w)
		end
	end
	if top <= IslandLayout.SEA_FLOOR + 0.5 then
		return
	end
	local bottom = VOXEL * math.floor((low - VOXEL) / VOXEL)
	local ceiling = VOXEL * math.ceil(high / VOXEL)
	local floor = IslandLayout.SEA_FLOOR - 8
	if bottom > floor then
		terrain:FillBlock(
			CFrame.new(cx + size / 2, (floor + bottom) / 2, cz + size / 2),
			Vector3.new(size, bottom - floor, size),
			Enum.Material.Rock
		)
	end
	local layers = (ceiling - bottom) / VOXEL
	local materials, occupancies = table.create(columns), table.create(columns)
	for i = 1, columns do
		local materialX, occupancyX = table.create(layers), table.create(layers)
		for j = 1, layers do
			local base = bottom + (j - 1) * VOXEL
			local materialY, occupancyY = table.create(columns), table.create(columns)
			for k = 1, columns do
				local index = (i - 1) * columns + k
				local h, w = heights[index], waters[index]
				local solid = math.clamp((h - base) / VOXEL, 0, 1)
				if solid > 0 then
					materialY[k] = if h - base <= 8 then surfaces[index] else Enum.Material.Rock
					occupancyY[k] = solid
				elseif w > base then
					materialY[k] = Enum.Material.Water
					occupancyY[k] = math.clamp((w - base) / VOXEL, 0, 1)
				else
					materialY[k] = Enum.Material.Air
					occupancyY[k] = 0
				end
			end
			materialX[j], occupancyX[j] = materialY, occupancyY
		end
		materials[i], occupancies[i] = materialX, occupancyX
	end
	local region = Region3.new(Vector3.new(cx, bottom, cz), Vector3.new(cx + size, ceiling, cz + size))
	terrain:WriteVoxels(region, VOXEL, materials, occupancies)
end

-- Emberhollow's interior (450 × 350) and its tunnel, hollowed out of the hill.
local function carveCave(terrain: Terrain)
	local cave = BiomeCatalog.Zones.EmberhollowCaves
	local room, tunnel = cave.interior, cave.tunnel
	local height = room.ceiling - room.floor
	terrain:FillBlock(
		CFrame.new(room.x, room.floor + height / 2, room.z),
		Vector3.new(room.halfX * 2, height, room.halfZ * 2),
		Enum.Material.Air
	)
	local length = tunnel.toZ - tunnel.fromZ
	local tunnelHeight = tunnel.ceiling - room.floor
	terrain:FillBlock(
		CFrame.new(tunnel.x, room.floor + tunnelHeight / 2, tunnel.fromZ + length / 2),
		Vector3.new(tunnel.halfWidth * 2, tunnelHeight, length),
		Enum.Material.Air
	)
	-- A basalt floor with cracked-lava seams.
	terrain:FillBlock(
		CFrame.new(room.x, room.floor - 2, room.z),
		Vector3.new(room.halfX * 2, 4, room.halfZ * 2),
		Enum.Material.Basalt
	)
	for index = 1, 5 do
		local x = room.x + (index - 3) * 80
		terrain:FillBlock(
			CFrame.new(x, room.floor - 2, room.z + (index % 2) * 60 - 30),
			Vector3.new(16, 4, 120),
			Enum.Material.CrackedLava
		)
	end
end

local function buildTerrain()
	local terrain = workspace.Terrain
	terrain:Clear()
	ocean(terrain)
	local half = IslandLayout.BUILD_HALF
	local size = WorldBuildService.CHUNK
	for cx = -half, half - size, size do
		for cz = -half, half - size, size do
			chunk(terrain, cx, cz)
			breathe()
		end
	end
	carveCave(terrain)
	-- Let the per-point materials go (the height lattice stays for gameplay).
	latticeMaterials = {}
end

-- Structures ---------------------------------------------------------------------

local STONE = Color3.fromRGB(150, 146, 136)
local DARK_STONE = Color3.fromRGB(92, 88, 96)
local WOOD = Color3.fromRGB(110, 78, 50)

local function model(name: string, attributes)
	local instance = Instance.new("Model")
	instance.Name = name
	for key, value in attributes or {} do
		instance:SetAttribute(key, value)
	end
	instance.Parent = folder
	return instance
end

local function block(parent, name: string, cframe: CFrame, size: Vector3, color: Color3, mat: Enum.Material)
	return part({
		Name = name,
		CFrame = cframe,
		Size = size,
		Color = color,
		Material = mat,
		Parent = parent,
	}, { "GeneratedStructure" })
end

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
		block(
			parent,
			"Wall",
			CFrame.lookAt(mid + Vector3.new(0, height / 2, 0), mid + Vector3.new(0, height / 2, 0) + direction),
			Vector3.new(6, height, to - from),
			DARK_STONE,
			Enum.Material.Slate
		)
	end
end

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
	for index = 1, 12 do
		local angle = math.rad(index * 30)
		local height = if index % 3 == 0 then 8 else 22 + (index % 2) * 8
		local at = Vector3.new(mound.x + math.cos(angle) * 52, y, mound.z + math.sin(angle) * 52)
		block(
			templeModel,
			"Column",
			CFrame.new(at + Vector3.new(0, height / 2, 0)),
			Vector3.new(6, height, 6),
			STONE,
			Enum.Material.Limestone
		)
	end
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
		Color3.fromRGB(80, 56, 36),
		Enum.Material.WoodPlanks
	)
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
	local lamp = glow(lighthouseModel, base + Vector3.new(0, 48, 0), Color3.fromRGB(255, 230, 160), 80)
	lamp.Size = Vector3.new(6, 6, 6)
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

local function safeCamp(entry)
	local center = groundAt(entry.x, entry.z)
	-- The server-side volume nobody can fight inside (SafeZoneService).
	local zone = part({
		Name = entry.name,
		Size = Vector3.new(entry.radius * 2, 40, entry.radius * 2),
		CFrame = CFrame.new(center + Vector3.new(0, 18, 0)),
		Transparency = 1,
		CanCollide = false,
		CanQuery = false,
		CanTouch = false,
	}, { "SafeZone" })
	zone:SetAttribute("SafeName", entry.name)
	-- A colour-blind-safe boundary: alternating white and blue posts.
	for index = 1, 16 do
		local angle = math.rad(index * 22.5)
		local x, z = entry.x + math.cos(angle) * entry.radius, entry.z + math.sin(angle) * entry.radius
		part({
			Name = "CampPost",
			Size = Vector3.new(1.5, 8, 1.5),
			CFrame = CFrame.new(groundAt(x, z) + Vector3.new(0, 3, 0)),
			Color = if index % 2 == 0 then Color3.fromRGB(240, 240, 240) else Color3.fromRGB(40, 110, 220),
			Material = Enum.Material.SmoothPlastic,
		}, { "GeneratedStructure" })
	end
	part({
		Name = "Tent",
		Size = Vector3.new(10, 6, 10),
		CFrame = CFrame.new(center + Vector3.new(-12, 2, -8)) * CFrame.Angles(0, math.rad(30), 0),
		Color = Color3.fromRGB(196, 170, 120),
		Material = Enum.Material.Fabric,
	}, { "GeneratedStructure" })
	local sign = part({
		Name = "CampSign",
		Size = Vector3.new(1, 1, 1),
		CFrame = CFrame.new(center + Vector3.new(0, 14, 0)),
		Transparency = 1,
		CanCollide = false,
	})
	local billboard = Instance.new("BillboardGui")
	billboard.Size = UDim2.fromOffset(220, 40)
	billboard.MaxDistance = 400
	billboard.Parent = sign
	local label = Instance.new("TextLabel")
	label.Size = UDim2.fromScale(1, 1)
	label.BackgroundTransparency = 1
	label.Text = "🛡 " .. entry.name .. " — safe camp"
	label.TextColor3 = Color3.fromRGB(220, 235, 255)
	label.TextStrokeTransparency = 0.2
	label.Font = Enum.Font.GothamBold
	label.TextSize = 16
	label.Parent = billboard
end

local function generate()
	local started = os.clock()
	lastYield = started
	folder = Instance.new("Folder")
	folder.Name = WorldBuildService.MAP_NAME
	folder:SetAttribute("GeneratedLayout", WorldBuildService.LAYOUT_VERSION)
	folder.Parent = workspace
	-- A Studio baseplate would cut through the island; it only exists at runtime here.
	local baseplate = workspace:FindFirstChild("Baseplate")
	if baseplate then
		baseplate:Destroy()
	end
	buildTerrain()
	for _, entry in PoiCatalog.Landmarks do
		local build = LANDMARKS[entry.style]
		if build then
			build(entry)
		end
	end
	for _, entry in PoiCatalog.Portals do
		anchor(entry.name, groundAt(entry.x, entry.z), "PortalSite", {
			Kind = entry.kind,
			ZoneRadius = entry.zoneRadius,
			Hidden = entry.hidden == true,
		})
	end
	for _, entry in PoiCatalog.SafeZones do
		safeCamp(entry)
	end
	for _, entry in PoiCatalog.RitualSites do
		anchor(entry.name, groundAt(entry.x, entry.z), "RitualSite", { SiteId = entry.id })
	end
	local arena = PoiCatalog.GuardianArena
	anchor("Guardian Arena", groundAt(arena.x, arena.z), "GuardianArena")
	for index, position in IslandLayout.SpawnCandidates() do
		anchor("Spawn" .. index, position + Vector3.new(0, 1, 0), "SpawnCandidate", {
			Zone = BiomeCatalog.ZoneAt(position.X, position.Z),
		})
	end
	print(("[WorldBuildService] Built the placeholder island in %.1f s"):format(os.clock() - started))
end

-- Builds the placeholder island now (yields). Also usable from Studio's command bar
-- to bake the island into the place, which later starts then reuse.
function WorldBuildService.Generate()
	local old = workspace:FindFirstChild(WorldBuildService.MAP_NAME)
	if old then
		old:Destroy()
	end
	generate()
end

local function publish(generated: boolean)
	if generated then
		-- Gameplay may trust IslandLayout's zones and heights on this map.
		workspace:SetAttribute(WorldState.GENERATED_ATTRIBUTE, true)
	end
	workspace:SetAttribute("FlintbornIsland", true)
	workspace:SetAttribute("FlintbornMapRadius", BiomeCatalog.MAP_RADIUS)
end

function WorldBuildService.Init()
	if not PlaceConfig.IsWorld() then
		return
	end
	local existing = workspace:FindFirstChild(WorldBuildService.MAP_NAME)
	local version = existing and existing:GetAttribute("GeneratedLayout")
	if version ~= nil then
		if version == WorldBuildService.LAYOUT_VERSION then
			-- A generated island saved into the place: nothing to build.
			publish(true)
			WorldState.MarkReady()
			return
		end
		-- An island saved from an older layout is rebuilt.
		existing:Destroy()
	end
	local authored = workspace:FindFirstChild(WorldBuildService.MAP_NAME)
	local stored = ServerStorage:FindFirstChild("Maps")
		and ServerStorage.Maps:FindFirstChild(WorldBuildService.MAP_NAME)
	if authored == nil and stored then
		stored:Clone().Parent = workspace
		authored = workspace:FindFirstChild(WorldBuildService.MAP_NAME)
	end
	if authored then
		publish(false)
		WorldState.MarkReady()
		return
	end
	if workspace:GetAttribute("FlintbornGenerateIsland") == false then
		WorldState.MarkReady()
		return
	end
	publish(true)
	task.spawn(function()
		local ok, err = pcall(generate)
		if not ok then
			warn("[WorldBuildService] Island build failed: " .. tostring(err))
		end
		WorldState.MarkReady()
	end)
end

return WorldBuildService
