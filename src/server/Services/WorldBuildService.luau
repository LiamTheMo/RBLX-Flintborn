-- The Shattered Crater (GDD §3, Q22, Q33, Q57, Q160a). Uses an authored map when
-- the place has one (a "ShatteredCrater" model in Workspace or ServerStorage.Maps);
-- otherwise builds a blocky placeholder island at startup: beaches and woodland
-- (Outer Rim), jungle (Inner Ring), a volcanic ridge with route gaps around an open
-- caldera (Center Crater), landmarks, and every gameplay POI as tagged parts so the
-- other services read the map without coordinates. Runs in Init, before any
-- service's Start reads the world. World place only.

local CollectionService = game:GetService("CollectionService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerStorage = game:GetService("ServerStorage")

local BiomeCatalog = require(ReplicatedStorage.Shared.World.BiomeCatalog)
local IslandLayout = require(ReplicatedStorage.Shared.World.IslandLayout)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local PoiCatalog = require(ReplicatedStorage.Shared.World.PoiCatalog)

local WorldBuildService = {}

WorldBuildService.MAP_NAME = "ShatteredCrater"

local folder = nil

local function part(props, tags)
	local instance = Instance.new("Part")
	instance.Anchored = true
	instance.TopSurface = Enum.SurfaceType.Smooth
	instance.BottomSurface = Enum.SurfaceType.Smooth
	for key, value in props do
		instance[key] = value
	end
	for _, tag in tags or {} do
		CollectionService:AddTag(instance, tag)
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

local function groundAt(position: Vector3): Vector3
	return Vector3.new(position.X, IslandLayout.HeightAt(position.X, position.Z), position.Z)
end

local function terrainTiles()
	local tile = IslandLayout.TILE
	local limit = BiomeCatalog.MAP_RADIUS + tile
	for x = -limit, limit, tile do
		for z = -limit, limit, tile do
			local distance = math.sqrt(x * x + z * z)
			if distance <= BiomeCatalog.MAP_RADIUS + tile / 2 then
				local height = IslandLayout.HeightAt(x, z)
				local biome = BiomeCatalog.Biomes[BiomeCatalog.BiomeAt(distance) or "Beach"]
				local onRidge = math.abs(distance - IslandLayout.RIDGE_RADIUS) < IslandLayout.RIDGE_WIDTH
					and height > 30
				part({
					Name = "Ground",
					Size = Vector3.new(tile, height + 24, tile),
					CFrame = CFrame.new(x, (height - 24) / 2, z),
					Color = if onRidge then Color3.fromRGB(58, 40, 36) else biome.color,
					Material = if onRidge then Enum.Material.Basalt else Enum.Material[biome.material],
				})
			end
		end
	end
	-- The sea around the island.
	workspace.Terrain:FillBlock(CFrame.new(0, -9, 0), Vector3.new(3600, 18, 3600), Enum.Material.Water)
end

local function landmark(entry)
	local base = groundAt(PoiCatalog.Position(entry))
	local model = Instance.new("Model")
	model.Name = entry.name
	model:SetAttribute("Landmark", entry.name)
	model.Parent = folder
	local tags = { "GeneratedStructure" }
	if entry.style == "Roots" then
		for index = 1, 5 do
			local angle = index * 72
			part({
				Name = "Root",
				Size = Vector3.new(8, 50, 8),
				CFrame = CFrame.new(base + Vector3.new(0, 18, 0)) * CFrame.Angles(0, math.rad(angle), math.rad(35)),
				Color = Color3.fromRGB(96, 68, 44),
				Material = Enum.Material.Wood,
				Parent = model,
			}, tags)
		end
		part({
			Name = "Trunk",
			Size = Vector3.new(18, 90, 18),
			CFrame = CFrame.new(base + Vector3.new(0, 45, 0)),
			Color = Color3.fromRGB(86, 60, 40),
			Material = Enum.Material.Wood,
			Parent = model,
		}, tags)
	elseif entry.style == "Ruins" then
		for index = 1, 8 do
			local angle = math.rad(index * 45)
			local height = 10 + (index % 3) * 8
			part({
				Name = "Pillar",
				Size = Vector3.new(5, height, 5),
				CFrame = CFrame.new(base + Vector3.new(math.cos(angle) * 22, height / 2, math.sin(angle) * 22)),
				Color = Color3.fromRGB(150, 146, 136),
				Material = Enum.Material.Cobblestone,
				Parent = model,
			}, tags)
		end
	elseif entry.style == "Monoliths" then
		for index = 1, 3 do
			part({
				Name = "Monolith",
				Size = Vector3.new(8, 60, 3),
				CFrame = CFrame.new(base + Vector3.new((index - 2) * 18, 30, 0))
					* CFrame.Angles(0, math.rad(index * 20), 0),
				Color = Color3.fromRGB(34, 32, 40),
				Material = Enum.Material.Slate,
				Parent = model,
			}, tags)
		end
	elseif entry.style == "Jade" then
		for index = 1, 4 do
			part({
				Name = "JadeSpire",
				Size = Vector3.new(6, 24 + index * 6, 6),
				CFrame = CFrame.new(base + Vector3.new(index * 7 - 17, 12 + index * 3, 0)),
				Color = Color3.fromRGB(80, 200, 140),
				Material = Enum.Material.Glass,
				Parent = model,
			}, tags)
		end
	else
		-- The volcanic ridge is shaped by the terrain; jagged rocks crown it.
		for index = 1, 24 do
			local angle = math.rad(index * 15 + 7)
			local at = Vector3.new(math.cos(angle), 0, math.sin(angle)) * IslandLayout.RIDGE_RADIUS
			if IslandLayout.HeightAt(at.X, at.Z) > 30 then
				part({
					Name = "RidgeRock",
					Size = Vector3.new(10, 18, 10),
					CFrame = CFrame.new(groundAt(at) + Vector3.new(0, 6, 0)) * CFrame.Angles(0, angle, math.rad(12)),
					Color = Color3.fromRGB(46, 32, 30),
					Material = Enum.Material.Basalt,
					Parent = model,
				}, tags)
			end
		end
	end
end

local function safeCamp(entry)
	local center = groundAt(PoiCatalog.Position(entry))
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
		part({
			Name = "CampPost",
			Size = Vector3.new(1.5, 8, 1.5),
			CFrame = CFrame.new(
				center + Vector3.new(math.cos(angle) * entry.radius, 4, math.sin(angle) * entry.radius)
			),
			Color = if index % 2 == 0 then Color3.fromRGB(240, 240, 240) else Color3.fromRGB(40, 110, 220),
			Material = Enum.Material.SmoothPlastic,
		}, { "GeneratedStructure" })
	end
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
	folder = Instance.new("Folder")
	folder.Name = WorldBuildService.MAP_NAME
	folder.Parent = workspace
	-- A Studio baseplate would cut through the island; it only exists at runtime here.
	local baseplate = workspace:FindFirstChild("Baseplate")
	if baseplate then
		baseplate:Destroy()
	end
	terrainTiles()
	for _, entry in PoiCatalog.Landmarks do
		landmark(entry)
	end
	for _, entry in PoiCatalog.Portals do
		anchor(entry.name, groundAt(PoiCatalog.Position(entry)), "PortalSite", {
			Kind = entry.kind,
			ZoneRadius = entry.zoneRadius,
			Hidden = entry.hidden == true,
		})
	end
	for _, entry in PoiCatalog.SafeZones do
		safeCamp(entry)
	end
	for _, entry in PoiCatalog.RitualSites do
		anchor(entry.name, groundAt(PoiCatalog.Position(entry)), "RitualSite")
	end
	anchor("Guardian Arena", groundAt(PoiCatalog.Position(PoiCatalog.GuardianArena)), "GuardianArena")
	for index, entry in PoiCatalog.SpawnCandidates() do
		anchor("Spawn" .. index, groundAt(PoiCatalog.Position(entry)) + Vector3.new(0, 1, 0), "SpawnCandidate")
	end
end

function WorldBuildService.Init()
	if not PlaceConfig.IsWorld() then
		return
	end
	local authored = workspace:FindFirstChild(WorldBuildService.MAP_NAME)
	local stored = ServerStorage:FindFirstChild("Maps")
		and ServerStorage.Maps:FindFirstChild(WorldBuildService.MAP_NAME)
	if authored == nil and stored then
		stored:Clone().Parent = workspace
		authored = workspace:FindFirstChild(WorldBuildService.MAP_NAME)
	end
	if authored == nil then
		if workspace:GetAttribute("FlintbornGenerateIsland") == false then
			return
		end
		generate()
	end
	workspace:SetAttribute("FlintbornIsland", true)
	workspace:SetAttribute("FlintbornMapRadius", BiomeCatalog.MAP_RADIUS)
end

return WorldBuildService
