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
-- World place only. The pieces of the build live in Server/WorldBuild: BuildKit
-- (shared state and helpers), IslandTerrain, Landmarks, SafeCamp and Scenery.

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerStorage = game:GetService("ServerStorage")

local BiomeCatalog = require(ReplicatedStorage.Shared.World.BiomeCatalog)
local IslandLayout = require(script.Parent.Parent.Rules.World.IslandLayout)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local PoiCatalog = require(ReplicatedStorage.Shared.World.PoiCatalog)
local WorldState = require(ReplicatedStorage.Shared.World.WorldState)
local BuildKit = require(script.Parent.Parent.WorldBuild.BuildKit)
local IslandTerrain = require(script.Parent.Parent.WorldBuild.IslandTerrain)
local Landmarks = require(script.Parent.Parent.WorldBuild.Landmarks)
local SafeCamp = require(script.Parent.Parent.WorldBuild.SafeCamp)
local Scenery = require(script.Parent.Parent.WorldBuild.Scenery)

local WorldBuildService = {}

WorldBuildService.MAP_NAME = WorldState.MAP_NAME
-- Bump when the generated layout changes, so islands saved into a place rebuild.
WorldBuildService.LAYOUT_VERSION = 4
-- Terrain is written in square chunks (16 × 16 voxel columns).
WorldBuildService.CHUNK = 64
WorldBuildService.OCEAN_TILE = 1024
-- Seconds of work between yields.
WorldBuildService.YIELD_SECONDS = 0.05
-- The invisible offshore wall (IslandTerrain): one segment per this many degrees.
WorldBuildService.BOUNDARY_STEP_DEGREES = 1
WorldBuildService.BOUNDARY_HEIGHT = 120
-- Each zone's scenery draws from Random.new(SCENERY_SEED + its place in
-- BiomeCatalog.ZONE_IDS).
WorldBuildService.SCENERY_SEED = 5417

-- The build pieces read the tunables above from here as they run.
local state = BuildKit.state
state.service = WorldBuildService

local anchor = BuildKit.anchor
local groundAt = BuildKit.groundAt

local function generate()
	local started = os.clock()
	state.lastYield = started
	local folder = Instance.new("Folder")
	state.folder = folder
	folder.Name = WorldBuildService.MAP_NAME
	folder:SetAttribute("GeneratedLayout", WorldBuildService.LAYOUT_VERSION)
	folder.Parent = workspace
	-- A Studio baseplate would cut through the island; it only exists at runtime here.
	local baseplate = workspace:FindFirstChild("Baseplate")
	if baseplate then
		baseplate:Destroy()
	end
	IslandTerrain.Build()
	IslandTerrain.Boundary()
	for _, entry in PoiCatalog.Landmarks do
		Landmarks.Build(entry)
	end
	for _, entry in PoiCatalog.Portals do
		anchor(entry.name, groundAt(entry.x, entry.z), "PortalSite", {
			Kind = entry.kind,
			ZoneRadius = entry.zoneRadius,
			Hidden = entry.hidden == true,
		})
	end
	for _, entry in PoiCatalog.SafeZones do
		SafeCamp.Build(entry)
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
	local sceneryCount = Scenery.Build()
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
	workspace:SetAttribute(WorldState.MAP_RADIUS_ATTRIBUTE, BiomeCatalog.MAP_RADIUS)
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
