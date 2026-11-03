-- The island's smooth Terrain (WorldBuildService): the open ocean, the island in
-- chunks of voxel columns, Emberhollow's cave, and the invisible offshore wall.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local BiomeCatalog = require(ReplicatedStorage.Shared.World.BiomeCatalog)
local IslandLayout = require(ReplicatedStorage.Shared.World.IslandLayout)
local BuildKit = require(script.Parent.BuildKit)

local IslandTerrain = {}

local state = BuildKit.state
local breathe = BuildKit.breathe
local part = BuildKit.part

local VOXEL = 4

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
	local tile = state.service.OCEAN_TILE
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
	local size = state.service.CHUNK
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
local function boundary()
	local wall = Instance.new("Folder")
	wall.Name = "Boundary"
	wall.Parent = state.folder
	local points = IslandLayout.BoundaryPoints(state.service.BOUNDARY_STEP_DEGREES)
	local height = state.service.BOUNDARY_HEIGHT
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
	local size = state.service.CHUNK
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

IslandTerrain.Build = buildTerrain
IslandTerrain.Boundary = boundary

return IslandTerrain
