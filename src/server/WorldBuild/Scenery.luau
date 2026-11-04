-- The island's decorative scenery (WorldBuildService; SceneryModels).

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local BiomeCatalog = require(ReplicatedStorage.Shared.World.BiomeCatalog)
local IslandLayout = require(script.Parent.Parent.Rules.World.IslandLayout)
local ModelBuilder = require(script.Parent.Parent.Rules.Visuals.ModelBuilder)
local SceneryModels = require(script.Parent.Parent.Rules.Visuals.SceneryModels)
local WorldState = require(ReplicatedStorage.Shared.World.WorldState)
local BuildKit = require(script.Parent.BuildKit)

local Scenery = {}

local state = BuildKit.state
local breathe = BuildKit.breathe

-- Decorative extras (SceneryModels): deterministic and never harvestable. Only
-- trunks, boulders and logs (SceneryModels.SOLID_PARTS) collide, and they stay
-- queryable so building placement and floor detection see them; canopies, tufts and
-- the rest are walk-through and unqueryable. They sit in the map's scenery folder
-- (WorldState.SCENERY_FOLDER), which the services' ground rays exclude. Each zone
-- draws from Random.new(WorldBuildService.SCENERY_SEED + its place in
-- BiomeCatalog.ZONE_IDS).

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
	parent.Parent = state.folder
	for index, zoneId in BiomeCatalog.ZONE_IDS do
		local zone = SceneryModels.Zones[zoneId]
		if zone then
			local rng = Random.new(state.service.SCENERY_SEED + index)
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

-- Scatters the scenery into the map folder; returns the tally of models and parts.
function Scenery.Build()
	sceneryCount = { models = 0, parts = 0 }
	scenery()
	return sceneryCount
end

return Scenery
