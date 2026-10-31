-- The play-world island (GDD §3, §54, Q22, Q33, Q57, Q160a). Uses an authored map
-- when the place has one (a "ShatteredCrater" model in Workspace or
-- ServerStorage.Maps); otherwise builds the placeholder island at startup from
-- IslandLayout as smooth Terrain: a 6,144-stud ocean, the 4,096-stud island with
-- per-zone materials, Crater Lake and its river, the Emberhollow hill with an
-- enterable cave, and a few simple placeholder structures (the Keep's walled and
-- battlemented courtyard, the Fallen Temple ruins, Timberwatch's tower, bridges,
-- camps with tents and fire pits), dressed with decorative scenery (forest clumps,
-- boulders, grass and fern tufts, fallen logs; SceneryModels) so the world reads as
-- a place. Scenery is never harvestable; only its trunks, boulders and logs collide or can be queried. Every gameplay POI
-- is a tagged part so the other services read the map without coordinates. The build runs in the background from Init, yielding between
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
local ModelBuilder = require(ReplicatedStorage.Shared.Visuals.ModelBuilder)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local PoiCatalog = require(ReplicatedStorage.Shared.World.PoiCatalog)
local SceneryModels = require(ReplicatedStorage.Shared.Visuals.SceneryModels)
local WorldState = require(ReplicatedStorage.Shared.World.WorldState)

local WorldBuildService = {}

WorldBuildService.MAP_NAME = WorldState.MAP_NAME
-- Bump when the generated layout changes, so islands saved into a place rebuild.
WorldBuildService.LAYOUT_VERSION = 4
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

-- The open ocean out to the full 6,144 studs: a sand floor and water to sea level
-- (its top voxel a quarter full, so the surface meets the shelf's knee-deep water).
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
			local level = IslandLayout.SEA_LEVEL
			terrain:FillBlock(
				CFrame.new(center + Vector3.new(0, (floor + level) / 2, 0)),
				Vector3.new(tile, level - floor, tile),
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
			-- Water only on knee-deep beds (and the open sea): see IslandLayout.
			local w = IslandLayout.WaterLevelAt(x, z) or -math.huge
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

-- The invisible wall a short way offshore: players wade the knee-deep shelf but
-- never walk out to the deep sea (GDD §55). Rays pass through it.
WorldBuildService.BOUNDARY_STEP_DEGREES = 1
WorldBuildService.BOUNDARY_HEIGHT = 120

local function boundary()
	local wall = Instance.new("Folder")
	wall.Name = "Boundary"
	wall.Parent = folder
	local points = IslandLayout.BoundaryPoints(WorldBuildService.BOUNDARY_STEP_DEGREES)
	local height = WorldBuildService.BOUNDARY_HEIGHT
	for index, a in points do
		local b = points[index % #points + 1]
		local mid = (a + b) / 2 + Vector3.new(0, height / 2 - 20, 0)
		part({
			Name = "Wall",
			Size = Vector3.new(4, height, (b - a).Magnitude + 4),
			CFrame = CFrame.lookAt(mid, mid + (b - a)),
			Transparency = 1,
			CanQuery = false,
			CanTouch = false,
			Parent = wall,
		})
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
local TOWER_ROOF = Color3.fromRGB(80, 56, 36)
local LIGHT_STONE = Color3.fromRGB(176, 170, 156)
local MERLON_STONE = Color3.fromRGB(112, 108, 116)
local MERLON_SPACING = 10
local MERLON_HEIGHT = 4

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

-- Pure decoration (a painted opening, a flame, a tent floor): no tag, no collision,
-- no query, so it never blocks building, rays or projectiles.
local function decor(parent, name: string, cframe: CFrame, size: Vector3, color: Color3, mat: Enum.Material)
	return part({
		Name = name,
		CFrame = cframe,
		Size = size,
		Color = color,
		Material = mat,
		CanCollide = false,
		CanQuery = false,
		CanTouch = false,
		Parent = parent,
	})
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

-- Camp props ------------------------------------------------------------------------

-- An open A-frame tent (two slanted cloth panels over a ridge pole) turned `yaw` degrees.
local TENT_PANEL = Vector3.new(6.4, 0.4, 9)

local function tent(parent, x: number, z: number, yaw: number, cloth: Color3)
	local frame = CFrame.new(groundAt(x, z)) * CFrame.Angles(0, math.rad(yaw), 0)
	for _, side in { -1, 1 } do
		block(
			parent,
			"Tent",
			frame * CFrame.new(side * 2.05, 2.45, 0) * CFrame.Angles(0, 0, math.rad(-side * 50)),
			TENT_PANEL,
			cloth,
			Enum.Material.Fabric
		)
	end
	block(parent, "TentPole", frame * CFrame.new(0, 4.95, 0), Vector3.new(0.5, 0.5, 10.4), WOOD, Enum.Material.Wood)
	decor(
		parent,
		"TentFloor",
		frame * CFrame.new(0, 0.15, 0),
		Vector3.new(8.4, 0.3, 9.4),
		Color3.fromRGB(110, 92, 70),
		Enum.Material.Fabric
	)
end

-- A ring of stones round three crossed logs and a glowing flame (lit: Neon + light).
local function firePit(parent, x: number, z: number)
	local at = groundAt(x, z)
	for index = 1, 8 do
		local angle = math.rad(index * 45)
		decor(
			parent,
			"FireStone",
			CFrame.new(at + Vector3.new(math.cos(angle) * 2.4, 0.4, math.sin(angle) * 2.4))
				* CFrame.Angles(0, -angle, 0),
			Vector3.new(1.2, 0.9, 1.6),
			if index % 2 == 0 then STONE else DARK_STONE,
			Enum.Material.Slate
		)
	end
	for index = 1, 3 do
		decor(
			parent,
			"FireLog",
			CFrame.new(at + Vector3.new(0, 0.5, 0)) * CFrame.Angles(0, math.rad(index * 60), math.rad(12)),
			Vector3.new(3.4, 0.7, 0.7),
			WOOD,
			Enum.Material.Wood
		)
	end
	local flame = decor(
		parent,
		"Flame",
		CFrame.new(at + Vector3.new(0, 1.6, 0)),
		Vector3.new(1.4, 2, 1.4),
		Color3.fromRGB(255, 150, 50),
		Enum.Material.Neon
	)
	local light = Instance.new("PointLight")
	light.Color = Color3.fromRGB(255, 160, 80)
	light.Range = 24
	light.Brightness = 1.5
	light.Parent = flame
end

-- A trader's stall: a counter under a red awning on four posts, with crates.
local function stall(parent, x: number, z: number, yaw: number)
	local frame = CFrame.new(groundAt(x, z)) * CFrame.Angles(0, math.rad(yaw), 0)
	block(parent, "Counter", frame * CFrame.new(0, 1.5, 0.8), Vector3.new(7, 3, 2), WOOD, Enum.Material.WoodPlanks)
	for _, post in { { -3.6, -2 }, { 3.6, -2 }, { -3.6, 2 }, { 3.6, 2 } } do
		block(
			parent,
			"StallPost",
			frame * CFrame.new(post[1], 3.6, post[2]),
			Vector3.new(0.5, 7.2, 0.5),
			WOOD,
			Enum.Material.Wood
		)
	end
	decor(
		parent,
		"Awning",
		frame * CFrame.new(0, 7.4, 0),
		Vector3.new(8.6, 0.4, 5.6),
		Color3.fromRGB(190, 60, 50),
		Enum.Material.Fabric
	)
	for index, crate in { { 5.6, 1.4 }, { 6.2, -1.2 } } do
		block(
			parent,
			"Crate",
			frame * CFrame.new(crate[1], 1.25, crate[2]) * CFrame.Angles(0, math.rad(index * 25), 0),
			Vector3.new(2.5, 2.5, 2.5),
			Color3.fromRGB(140, 104, 66),
			Enum.Material.WoodPlanks
		)
	end
end

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
	-- A small camp: two tents, a fire pit and a trader's stall.
	local props = model(entry.name .. " Props")
	tent(props, entry.x - 12, entry.z - 8, 30, Color3.fromRGB(196, 170, 120))
	tent(props, entry.x - 10, entry.z + 11, 70, Color3.fromRGB(158, 98, 84))
	firePit(props, entry.x + 8, entry.z + 9)
	stall(props, entry.x + 12, entry.z - 9, -25)
	local sign = part({
		Name = "CampSign",
		Size = Vector3.new(1, 1, 1),
		CFrame = CFrame.new(center + Vector3.new(0, 14, 0)),
		Transparency = 1,
		CanCollide = false,
		CanQuery = false,
		CanTouch = false,
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

-- Scenery -------------------------------------------------------------------------

-- Decorative extras (SceneryModels): deterministic and never harvestable. Only
-- trunks, boulders and logs (SceneryModels.SOLID_PARTS) collide, and they stay
-- queryable so building placement and floor detection see them; canopies, tufts and
-- the rest are walk-through and unqueryable. They sit in the map's scenery folder
-- (WorldState.SCENERY_FOLDER), which the services' ground rays exclude.
-- Each zone draws from Random.new(SCENERY_SEED + its place in BiomeCatalog.ZONE_IDS).
WorldBuildService.SCENERY_SEED = 5417
-- Extra studs kept clear round camps, structures, portals and the cave tunnel.
local SCENERY_MARGIN = 6
-- Studs kept clear round every player spawn point.
local SPAWN_CLEARANCE = 14
-- Steepest ground (rise per stud) a tree or a prop stands on.
local TREE_MAX_SLOPE = 0.55
local PROP_MAX_SLOPE = 1
-- Trunks in one clump keep this far apart (studs).
local TREE_SPACING = 7
-- Attempts to place one tree in its clump, and to find one prop spot.
local TREE_TRIES = 6
local PROP_TRIES = 4
-- The Keep island's causeway and ramp run south from the courtyard along the Keep's
-- centre line: scenery stays this far to either side of it (x) until CAUSEWAY_END
-- studs south of the Keep's centre (past the end of the land bridge).
local CAUSEWAY_HALF_WIDTH = 50
local CAUSEWAY_END = 740

local KEEP_SHAPE = BiomeCatalog.Zones.ShatteredKeep.shape
local FOOTPRINT = { { 1, 0 }, { -1, 0 }, { 0, 1 }, { 0, -1 } }

local function nearSpawn(x: number, z: number): boolean
	for _, spawn in IslandLayout.SpawnCandidates() do
		local dx, dz = x - spawn.X, z - spawn.Z
		if dx * dx + dz * dz < SPAWN_CLEARANCE * SPAWN_CLEARANCE then
			return true
		end
	end
	return false
end

local function onCauseway(x: number, z: number): boolean
	local court = IslandLayout.Courtyard
	return math.abs(x - KEEP_SHAPE.x) < CAUSEWAY_HALF_WIDTH
		and z > court.z + court.halfZ
		and z < KEEP_SHAPE.z + CAUSEWAY_END
end

-- Scenery may stand at (x, z) in `zoneId`: dry, off camps and structures, on
-- ground that is not a cliff, off the causeway and spawn points.
local function usable(zoneId: string, x: number, z: number, maxSlope: number): boolean
	return BiomeCatalog.ZoneAt(x, z) == zoneId
		and IslandLayout.IsDry(x, z)
		and not IslandLayout.KeepOut(x, z, SCENERY_MARGIN)
		and IslandLayout.SlopeAt(x, z) <= maxSlope
		and not onCauseway(x, z)
		and not nearSpawn(x, z)
end

-- The lowest ground under a footprint of `radius` studs, so a piece sits in its
-- slope rather than hovering on the downhill side.
local function footingAt(x: number, z: number, radius: number): number
	local low = IslandLayout.HeightAt(x, z)
	for _, offset in FOOTPRINT do
		low = math.min(low, IslandLayout.HeightAt(x + offset[1] * radius, z + offset[2] * radius))
	end
	return low
end

local sceneryCount = { models = 0, parts = 0 }

-- One model of `kind` at (x, z), turned and sized at random within its kind's range.
local function place(parent: Instance, kind: string, paletteId: string, rng: Random, x: number, z: number)
	local info = SceneryModels.Kinds[kind]
	local scale = rng:NextNumber(info.scale[1], info.scale[2])
	local recipe = SceneryModels.Get(kind, paletteId, rng:NextInteger(1, info.variants))
	local origin = CFrame.new(x, footingAt(x, z, info.radius * scale), z)
		* CFrame.Angles(0, rng:NextNumber(0, math.pi * 2), 0)
	local built = ModelBuilder.Build(recipe, origin, { name = kind, parent = parent, scale = Vector3.one * scale })
	for _, child in built:GetChildren() do
		if info.solid and SceneryModels.SOLID_PARTS[child.Name] then
			-- Trunks, boulders and logs block movement and are real obstacles for building
			-- and floor detection, so they stay queryable; the rest is decoration.
			child.CanCollide = true
			child.CanQuery = true
		elseif not info.solid then
			-- Hundreds of tiny tufts are not worth a shadow each.
			child.CastShadow = false
		end
	end
	sceneryCount.models += 1
	sceneryCount.parts += #recipe.parts
	breathe()
end

-- The first habitat in `habitats` that the zone offers (nil when none).
local function habitatIn(zoneId: string, habitats: { string }): string?
	for _, habitat in habitats do
		if BiomeCatalog.HasHabitat(zoneId, habitat) then
			return habitat
		end
	end
	return nil
end

-- A spot for one prop (a boulder, tuft or log) in `zoneId`, preferring `habitat`.
local function propSpot(zoneId: string, rng: Random, habitat: string?): (number?, number?)
	for _ = 1, PROP_TRIES do
		local point = IslandLayout.RandomPointIn(zoneId, rng, habitat)
		if point == nil and habitat then
			point = IslandLayout.RandomPointIn(zoneId, rng, nil)
		end
		if point and usable(zoneId, point.X, point.Z, PROP_MAX_SLOPE) then
			return point.X, point.Z
		end
	end
	return nil, nil
end

local function scatter(
	parent: Instance,
	zoneId: string,
	paletteId: string,
	rng: Random,
	kind: string,
	count: number,
	habitat: string?
)
	for _ = 1, count do
		local x, z = propSpot(zoneId, rng, habitat)
		if x and z then
			place(parent, kind, paletteId, rng, x, z)
		end
	end
end

-- Forest clumps: trees of one kind scattered round a centre in forest, kept apart.
local function clump(parent: Instance, zoneId: string, zone, kind: string, rng: Random, habitat: string?)
	local centre = IslandLayout.RandomPointIn(zoneId, rng, habitat)
	if centre == nil and habitat then
		centre = IslandLayout.RandomPointIn(zoneId, rng, nil)
	end
	if centre == nil then
		return
	end
	local trunks = {}
	for _ = 1, rng:NextInteger(zone.clumpSize[1], zone.clumpSize[2]) do
		for _ = 1, TREE_TRIES do
			local angle, reach = rng:NextNumber(0, math.pi * 2), zone.clumpRadius * math.sqrt(rng:NextNumber())
			local x, z = centre.X + math.cos(angle) * reach, centre.Z + math.sin(angle) * reach
			local crowded = false
			for _, other in trunks do
				if (x - other[1]) ^ 2 + (z - other[2]) ^ 2 < TREE_SPACING * TREE_SPACING then
					crowded = true
					break
				end
			end
			if not crowded and usable(zoneId, x, z, TREE_MAX_SLOPE) then
				table.insert(trunks, { x, z })
				place(parent, kind, zone.palette, rng, x, z)
				break
			end
		end
	end
end

local function scenery()
	local parent = Instance.new("Folder")
	parent.Name = WorldState.SCENERY_FOLDER
	parent.Parent = folder
	for index, zoneId in BiomeCatalog.ZONE_IDS do
		local zone = SceneryModels.Zones[zoneId]
		if zone then
			local rng = Random.new(WorldBuildService.SCENERY_SEED + index)
			local forest = habitatIn(zoneId, { "Forest", "Jungle" })
			for _, entry in zone.clumps do
				for _ = 1, entry[2] do
					clump(parent, zoneId, zone, entry[1], rng, forest)
				end
			end
			scatter(parent, zoneId, zone.palette, rng, "Boulder", zone.boulders, habitatIn(zoneId, { "Rocky" }))
			for _, cover in zone.groundcover do
				scatter(
					parent,
					zoneId,
					zone.palette,
					rng,
					cover[1],
					cover[2],
					habitatIn(zoneId, { "Meadow", "Grassland", "Clearing" })
				)
			end
			scatter(parent, zoneId, zone.palette, rng, "Log", zone.logs, forest)
		end
	end
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
	boundary()
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
	sceneryCount = { models = 0, parts = 0 }
	scenery()
	print(
		("[WorldBuildService] Built the placeholder island in %.1f s (%d scenery models, %d parts)"):format(
			os.clock() - started,
			sceneryCount.models,
			sceneryCount.parts
		)
	)
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
