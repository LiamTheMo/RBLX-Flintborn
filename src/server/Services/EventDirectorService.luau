-- The world event director (GDD §7, Q42–48, Q111–112, Q140–143). About every five
-- minutes each category rolls on its own; whatever triggers is placed at a random
-- valid spot in its biome — on the map's ground (never on a base or a player),
-- kept apart from other event footprints, extraction auras, safe zones, the
-- Guardian arena and totem-covered bases, and inside the server's budget —
-- announced to everyone, and cleaned up when claimed or expired.
-- Rare nodes pay out once and never regrow; generated ruins are never claimable.
-- The Guardian keeps its own schedule (v0.12). Every event is a gameplay part (the
-- prompt, hitbox or wall) dressed with placeholder props (PropModels) that live
-- under the event's model, so finishing the event removes them all. World place only.

local CollectionService = game:GetService("CollectionService")
local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local EventCatalog = require(ReplicatedStorage.Shared.Events.EventCatalog)
local EventRules = require(ReplicatedStorage.Shared.Events.EventRules)
local ModelBuilder = require(ReplicatedStorage.Shared.Visuals.ModelBuilder)
local NodeCatalog = require(ReplicatedStorage.Shared.Resources.NodeCatalog)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local PropModels = require(ReplicatedStorage.Shared.Visuals.PropModels)
local Rarity = require(ReplicatedStorage.Shared.Items.Rarity)
local Recipe = require(ReplicatedStorage.Shared.Visuals.Recipe)
local WorldState = require(ReplicatedStorage.Shared.World.WorldState)
local AnnouncementService = require(script.Parent.AnnouncementService)
local BossService = require(script.Parent.BossService)
local BuildingService = require(script.Parent.BuildingService)
local CacheService = require(script.Parent.CacheService)
local DropService = require(script.Parent.DropService)
local ExtractionService = require(script.Parent.ExtractionService)
local GuardianService = require(script.Parent.GuardianService)
local InventoryService = require(script.Parent.InventoryService)
local MeteorService = require(script.Parent.MeteorService)
local ModifierService = require(script.Parent.ModifierService)
local NpcService = require(script.Parent.NpcService)
local ProgressionService = require(script.Parent.ProgressionService)
local SafeZoneService = require(script.Parent.SafeZoneService)

local EventDirectorService = {}

EventDirectorService.DEFAULT_MAP_RADIUS = 1000
EventDirectorService.PLACEMENT_ATTEMPTS = 10
-- Studio ticks faster so events can be tried without waiting five minutes.
EventDirectorService.STUDIO_TICK_SECONDS = 45
EventDirectorService.NODE_HARVEST_SECONDS = 3
EventDirectorService.GENERATED_TAG = "GeneratedStructure"
-- Extra distance kept from totem cover so events never land in a base.
EventDirectorService.TOTEM_MARGIN = 20

-- Spawn counts by category and rarity, for analytics in v0.17 (§7.5).
EventDirectorService.Stats = {}

local events = {}
local folder = nil
local rng = Random.new()

local function now(): number
	return workspace:GetServerTimeNow()
end

local function activeFootprints()
	local list = {}
	for _, event in events do
		table.insert(list, { position = event.position, radius = event.entry.footprint })
	end
	return list
end

-- Map ground only: structures, bodies, bosses and other events are see-through.
local function groundParams()
	local ignore = { folder }
	for _, name in { BuildingService.FOLDER_NAME, "EventEnemies", "Bosses", "GuardianArena", "Arrows" } do
		local other = workspace:FindFirstChild(name)
		if other then
			table.insert(ignore, other)
		end
	end
	for _, player in Players:GetPlayers() do
		if player.Character then
			table.insert(ignore, player.Character)
		end
	end
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	params.FilterDescendantsInstances = ignore
	params.RespectCanCollide = true
	return params
end

-- The ground under (x, z), cast down from `fromY` (default: above the whole map;
-- lower to find a cave floor under the hill).
local function groundAt(x: number, z: number, fromY: number?): Vector3?
	local params = groundParams()
	local top = fromY or 1000
	local hit = workspace:Raycast(Vector3.new(x, top, z), Vector3.new(0, -(top + 1000), 0), params)
	if hit and hit.Material ~= Enum.Material.Water and hit.Position.Y > -50 then
		return hit.Position
	end
	return nil
end

-- Places an event must keep out of: extraction auras, safe zones, the Guardian
-- arena and totem-covered bases.
local function keepOut()
	local zones = ExtractionService.Auras()
	for _, zone in SafeZoneService.Circles() do
		table.insert(zones, zone)
	end
	local arena = GuardianService.ArenaCenter()
	if arena then
		table.insert(zones, { center = arena, radius = GuardianService.ARENA_RADIUS })
	end
	for _, totem in BuildingService.Totems() do
		table.insert(zones, { center = totem.position, radius = totem.radius + EventDirectorService.TOTEM_MARGIN })
	end
	return zones
end

-- A random spot in the entry's zone, habitat or tier that keeps clear of other
-- footprints. On the generated island EventRules.PlacePoint already returns
-- ground (the cave floor for cave events, which a raycast from above would miss);
-- an authored map falls back to a distance band and a raycast.
local function place(entry): Vector3?
	local mapRadius = workspace:GetAttribute("FlintbornMapRadius") or EventDirectorService.DEFAULT_MAP_RADIUS
	local generated = WorldState.IsGenerated()
	local footprints = activeFootprints()
	local zones = keepOut()
	for _ = 1, EventDirectorService.PLACEMENT_ATTEMPTS do
		local position
		if generated then
			position = EventRules.PlacePoint(entry, rng)
		else
			local angle = rng:NextNumber(0, math.pi * 2)
			local distance = EventRules.BiomeDistance(entry.biome, rng) * mapRadius
			position = groundAt(math.cos(angle) * distance, math.sin(angle) * distance)
		end
		if
			position
			and EventRules.Separated(position, entry.footprint, footprints)
			and EventRules.ClearOf(position, entry.footprint, zones)
		then
			return position
		end
	end
	return nil
end

local function finish(event)
	if events[event.id] ~= event then
		return
	end
	events[event.id] = nil
	for npc in event.npcs do
		NpcService.Despawn(npc)
	end
	if event.boss then
		-- Event and structure bosses leave with their event (Q46).
		BossService.Despawn(event.boss, "EventEnded")
	end
	event.model:Destroy()
	AnnouncementService.End(event.id)
end

local function spill(loot, position: Vector3, luck: number?)
	for _, item in EventRules.RollLoot(loot, rng, luck) do
		DropService.Spawn(item, position + Vector3.new(rng:NextNumber(-3, 3), 0, rng:NextNumber(-3, 3)))
	end
end

-- The hitbox of each node look: size, whether it blocks walking, and the prompt's action.
local NODE_LOOKS = {
	Ore = { size = Vector3.new(6, 5, 6), solid = true, action = "Mine" },
	Plant = { size = Vector3.new(4, 4, 4), solid = false, action = "Harvest" },
	Pile = { size = Vector3.new(4, 3, 4), solid = true, action = "Search" },
}

-- The accent colour props are lit in for an event's rarity.
local function accentOf(entry)
	return Recipe.Rgb(Rarity.Colors[entry.rarity] or Color3.new(1, 1, 1))
end

-- A one-time rare node: harvested once, never regrows (Q112). Plant nodes are
-- gathered by hand; ore nodes need a pickaxe of at least `minRank` (GDD §51). The
-- plain hitbox part carries the prompt and is drawn by PropModels (an ore cluster,
-- a glowing plant, or for `pile` a heap of rubble to search); it takes its props
-- with it when claimed.
local function spawnNode(event, loot, position: Vector3, minRank: number?, onClaimed, pile: boolean?)
	local isOre = minRank ~= nil
	local lookName = if pile then "Pile" elseif isOre then "Ore" else "Plant"
	local look = NODE_LOOKS[lookName]
	local part = Instance.new("Part")
	part.Name = event.entry.name
	part.Anchored = true
	part.Shape = if lookName == "Plant" then Enum.PartType.Ball else Enum.PartType.Block
	part.Size = look.size
	part.Transparency = 1
	part.CanCollide = look.solid
	part.CFrame = CFrame.new(position + Vector3.new(0, part.Size.Y / 2, 0))
	part.Parent = event.model
	local recipe = if pile
		then PropModels.LootPile
		elseif isOre then PropModels.OreNode(accentOf(event.entry))
		else PropModels.PlantNode(PropModels.PlantVariant(event.entry.id), accentOf(event.entry))
	ModelBuilder.Decorate(part, recipe)
	local prompt = Instance.new("ProximityPrompt")
	prompt.ActionText = look.action
	prompt.ObjectText = if isOre
		then ("%s · %s · %s+"):format(event.entry.name, event.entry.rarity, NodeCatalog.PickaxeName(minRank))
		else ("%s · %s"):format(event.entry.name, event.entry.rarity)
	prompt.HoldDuration = EventDirectorService.NODE_HARVEST_SECONDS
	prompt.MaxActivationDistance = 8
	prompt.RequiresLineOfSight = false
	prompt.Parent = part
	local function notice(player: Player): string?
		return if isOre then NodeCatalog.PickaxeNotice(InventoryService.EquippedTool(player), minRank) else nil
	end
	-- Say so as the hold starts rather than after it.
	prompt.PromptButtonHoldBegan:Connect(function(player)
		local message = notice(player)
		if message then
			InventoryService.Notify(player, message)
		end
	end)
	local site = {}
	prompt.Triggered:Connect(function(player)
		if not CacheService.CanInteract(player, part, 10) or notice(player) then
			return
		end
		if EventRules.Claim(site) then
			part:Destroy()
			spill(loot, position, ModifierService.Sum(player, "Luck"))
			ProgressionService.GrantXp(player, "RareNode", event.entry.name)
			onClaimed()
		end
	end)
end

-- One event's creatures share a group, so Neutral members defend the others
-- (protective boars around the Iron-Tusk Boar, GDD §54).
local function spawnGroup(event, group, center: Vector3)
	local pack = NpcService.NewGroup()
	for _, member in group do
		for _ = 1, member.count do
			local offset = Vector3.new(rng:NextNumber(-8, 8), 0, rng:NextNumber(-8, 8))
			-- Cast from just above the event centre, so a cave event's creatures
			-- stand on the cave floor rather than the hill above it.
			local position = groundAt(center.X + offset.X, center.Z + offset.Z, center.Y + 20) or center
			local npc = NpcService.Spawn(member.enemy, position, member.elite, event.id, pack)
			event.npcs[npc] = true
		end
	end
end

-- Generated raidable structures (Q47): never claimable by players. The gameplay
-- is a ring of walls with a doorway (tagged GeneratedStructure, Generated); each
-- wall is drawn by its style (Ruin stone stays visible and is broken up, the Fort's
-- palisade and the Camp's hide fence are drawn over an invisible part), and the
-- style's dressing and gate stand inside and at the doorway.
local function spawnStructure(event, position: Vector3)
	local entry = event.entry
	local style = entry.style
	local ring = PropModels.RING
	local material = if style == "Ruin" then Enum.Material.Cobblestone else Enum.Material.WoodPlanks
	for index = 1, ring.segments do
		-- Leave a doorway gap so the inside is reachable without breaking walls.
		if PropModels.HasWall(style, index) then
			local angle = (index / ring.segments) * math.pi * 2
			local wall = Instance.new("Part")
			wall.Name = "GeneratedWall"
			wall.Anchored = true
			wall.Material = material
			wall.Color = if style == "Ruin" then Color3.fromRGB(120, 116, 108) else Color3.fromRGB(110, 80, 50)
			local height = if style == "Ruin"
				then rng:NextNumber(PropModels.RUIN_HEIGHT[1], PropModels.RUIN_HEIGHT[2])
				else ring.height
			wall.Size = Vector3.new(ring.width, height, ring.thickness)
			local at = position
				+ Vector3.new(math.cos(angle) * ring.radius, wall.Size.Y / 2, math.sin(angle) * ring.radius)
			wall.CFrame = CFrame.lookAt(at, Vector3.new(position.X, at.Y, position.Z))
			wall:SetAttribute("Generated", true)
			CollectionService:AddTag(wall, EventDirectorService.GENERATED_TAG)
			wall.Parent = event.model
			local look = PropModels.Wall(style, height)
			if not look.hostVisible then
				wall.Transparency = 1
			end
			ModelBuilder.Decorate(wall, look)
		end
	end
	local base = position - Vector3.new(0, PropModels.STRUCTURE_SINK, 0)
	ModelBuilder.Build(PropModels.Structure[style], CFrame.new(base), { name = "Dressing", parent = event.model })
	local doorX, doorZ = PropModels.RingPoint(ring.doorway)
	local door = base + Vector3.new(doorX, 0, doorZ)
	ModelBuilder.Build(
		PropModels.Gate[style],
		CFrame.lookAt(door, Vector3.new(position.X, door.Y, position.Z)),
		{ name = "Gate", parent = event.model }
	)
	if entry.cache then
		CacheService.Spawn(EventCatalog.Get(entry.cache), position, event.model, function() end)
	end
	if entry.loot then
		spawnNode(event, entry.loot, position, nil, function() end, true)
	end
	if entry.defenders then
		spawnGroup(event, entry.defenders, position)
	end
	if entry.boss then
		event.boss = BossService.Spawn(entry.boss, position + Vector3.new(0, 0, 6), {
			source = "Structure",
			structureGone = function()
				return events[event.id] ~= event
			end,
		})
	end
end

-- Spawns what `event` is made of, by kind. False for a kind it does not know.
local function populate(event, done): boolean
	local entry, position, model = event.entry, event.position, event.model
	-- A failure while building (or an unknown kind) takes the half-made event down
	-- again instead of leaving a silent, unannounced one behind.
	local built, result = pcall(populate, event, done)
	if not built or result ~= true then
		warn(
			("[EventDirector] Could not build %s: %s"):format(
				entry.name,
				if built then "unknown kind" else tostring(result)
			)
		)
		finish(event)
		return false
	end
	local kind = entry.kind
	AnnouncementService.Announce({
		id = event.id,
		name = entry.name,
		rarity = entry.rarity,
		category = entry.category,
		kind = kind,
		position = position,
		radius = entry.footprint,
		endsAt = event.endsAt,
	})
	task.delay(entry.lifetime, done)
	local key = entry.category .. ":" .. entry.rarity
	EventDirectorService.Stats[key] = (EventDirectorService.Stats[key] or 0) + 1
	return true
end

-- One director tick: every category rolls independently (Q141), and so does every
-- rare type within it; each result is placed in turn (rarest first), so later ones
-- see the footprints and budget the earlier ones took.
function EventDirectorService.Tick()
	for _, entry in EventRules.RollTick(EventCatalog.Entries, EventCatalog.Categories, rng) do
		-- One bad event must never stop the director's loop.
		local ok, started = pcall(start, entry)
		if not ok then
			warn(("[EventDirector] %s failed to start: %s"):format(entry.name, tostring(started)))
		elseif not started then
			warn(("[EventDirector] Skipped %s: no valid place or over budget"):format(entry.name))
		end
	end
end

function EventDirectorService.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	folder = Instance.new("Folder")
	folder.Name = "WorldEvents"
	folder.Parent = workspace
	-- An NPC event ends once its whole group is dead.
	NpcService.Died:Connect(function(npc)
		local event = npc.eventId and events[npc.eventId]
		if event then
			event.npcs[npc] = nil
			if event.entry.kind == EventCatalog.Kinds.Npc and next(event.npcs) == nil then
				finish(event)
			end
		end
	end)
	task.spawn(function()
		-- Events are placed on the map's ground, so the map must be in place first.
		WorldState.WaitUntilReady()
		while true do
			local seconds = workspace:GetAttribute("FlintbornEventSeconds")
				or (if RunService:IsStudio() then EventDirectorService.STUDIO_TICK_SECONDS else EventRules.TICK_SECONDS)
			task.wait(seconds)
			EventDirectorService.Tick()
		end
	end)
end

return EventDirectorService
