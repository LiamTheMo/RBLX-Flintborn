-- Roaming wildlife (GDD §54, owner decisions 2026-10-28). Keeps each map zone's
-- few small groups of regular creatures filled from its spawn table
-- (WildlifeRules), placed in their habitat by IslandLayout.RandomPointIn. A killed
-- or despawned group's slot refills about three minutes later, never within
-- PLAYER_CLEARANCE of a player or inside a safe zone. A hard cap bounds the
-- island's creatures; when it is full, a group nobody has been near for a while
-- is despawned to make room. Hostile groups also keep clear of player spawn
-- points. NpcService drives the bodies. Wildlife needs the generated island's zones
-- (an authored map has none yet, so nothing spawns there) and waits for the map to
-- be built. World place only.

local CollectionService = game:GetService("CollectionService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local EnemyCatalog = require(ReplicatedStorage.Shared.Enemies.EnemyCatalog)
local IslandLayout = require(ReplicatedStorage.Shared.World.IslandLayout)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local WildlifeRules = require(ReplicatedStorage.Shared.Enemies.WildlifeRules)
local WorldState = require(ReplicatedStorage.Shared.World.WorldState)
local NpcService = require(script.Parent.NpcService)
local SafeZoneService = require(script.Parent.SafeZoneService)

local WildlifeService = {}

-- Hostile groups never start this close to a player spawn point.
WildlifeService.HOSTILE_SPAWN_CLEARANCE = 100
-- Creatures wade shallows and swim deeper water (as NpcService moves them).
WildlifeService.WADE_DEPTH = 4

-- slot = {zone, readyAt, group?}; group = {slot, members = {npc -> true}, size, lastNear}.
local slots = {}
local owners = {}
local alive = 0
local rng = Random.new()
local spawnPoints = {}

local function now(): number
	return os.clock()
end

local function randomPoint(zoneId: string, habitat: string?): Vector3?
	local ok, point = pcall(IslandLayout.RandomPointIn, zoneId, rng, habitat)
	return if ok and typeof(point) == "Vector3" then point else nil
end

local function playerPositions()
	local list = {}
	for _, player in Players:GetPlayers() do
		local root = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
		if root then
			table.insert(list, root.Position)
		end
	end
	return list
end

-- Map ground only: creatures, events, bosses and characters are see-through.
local function groundParams()
	local ignore = {}
	for _, name in { "EventEnemies", "WorldEvents", "Bosses", "GuardianArena", "Arrows", "ResourceNodes" } do
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

local function standingAt(position: Vector3, params): Vector3
	local hit = WorldState.Standing(position + Vector3.new(0, 30, 0), 80, params, WildlifeService.WADE_DEPTH)
	return if hit then hit.Position else position
end

local function despawn(group)
	for npc in group.members do
		owners[npc] = nil
		NpcService.Despawn(npc)
		alive -= 1
	end
	group.members = {}
	group.slot.group = nil
	group.slot.readyAt = now() + WildlifeRules.RESPAWN_SECONDS
end

-- Despawns far-from-everyone groups until `count` more creatures fit, if it can.
local function makeRoom(count: number): boolean
	while not WildlifeRules.HasRoom(alive, count) do
		local groups = {}
		for _, slot in slots do
			if slot.group then
				table.insert(groups, slot.group)
			end
		end
		local idle = WildlifeRules.MostIdle(groups, now())
		if idle == nil then
			return false
		end
		despawn(idle)
	end
	return true
end

-- A spot for a group in `zoneId`'s `habitat`, away from players and safe zones
-- (and, for Hostile creatures, from player spawn points).
local function place(zoneId: string, habitat: string?, hostile: boolean): Vector3?
	local players = playerPositions()
	for _ = 1, WildlifeRules.PLACEMENT_ATTEMPTS do
		local point = randomPoint(zoneId, habitat)
		if
			point
			and WildlifeRules.ClearOfPlayers(point, players)
			and not SafeZoneService.Contains(point)
			and (
				not hostile
				or WildlifeRules.ClearOfPlayers(point, spawnPoints, WildlifeService.HOSTILE_SPAWN_CLEARANCE)
			)
		then
			return point
		end
	end
	return nil
end

-- Fills one slot. False when there was no spot or no room under the cap.
local function fill(slot): boolean
	local zone = WildlifeRules.Zones[slot.zone]
	local entry = WildlifeRules.Pick(zone.spawns, rng)
	local size = WildlifeRules.GroupSize(entry, rng)
	local enemy = EnemyCatalog.Get(entry.enemy)
	local hostile = enemy ~= nil and enemy.behaviour == EnemyCatalog.Behaviours.Hostile
	local center = place(slot.zone, entry.habitat, hostile)
	if center == nil or not makeRoom(size) then
		return false
	end
	local params = groundParams()
	local herd = NpcService.NewGroup(true)
	local group = { slot = slot, members = {}, size = size, lastNear = now() }
	for _ = 1, size do
		local spread = WildlifeRules.GROUP_SPREAD
		local offset = Vector3.new(rng:NextNumber(-spread, spread), 0, rng:NextNumber(-spread, spread))
		local npc = NpcService.Spawn(entry.enemy, standingAt(center + offset, params), false, nil, herd)
		group.members[npc] = true
		owners[npc] = group
		alive += 1
	end
	slot.group = group
	return true
end

-- Remembers when someone was last near each group (far groups may make room).
local function watch()
	local players = playerPositions()
	local at = now()
	for _, slot in slots do
		local group = slot.group
		if group then
			local positions = {}
			for npc in group.members do
				table.insert(positions, npc.body.Position)
			end
			if WildlifeRules.AnyNear(positions, players, WildlifeRules.FAR_RADIUS) then
				group.lastNear = at
			end
		end
	end
end

function WildlifeService.Tick()
	watch()
	local at = now()
	for _, slot in slots do
		if slot.group == nil and at >= slot.readyAt and not fill(slot) then
			slot.readyAt = at + WildlifeRules.RETRY_SECONDS
		end
	end
end

-- Roaming creatures alive now.
function WildlifeService.Count(): number
	return alive
end

function WildlifeService.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	for _, zoneId in WildlifeRules.Slots() do
		table.insert(slots, { zone = zoneId, readyAt = 0 })
	end
	-- A group whose last member dies leaves its slot to refill later.
	NpcService.Died:Connect(function(npc)
		local group = owners[npc]
		if group == nil then
			return
		end
		owners[npc] = nil
		group.members[npc] = nil
		alive -= 1
		if next(group.members) == nil and group.slot.group == group then
			group.slot.group = nil
			group.slot.readyAt = now() + WildlifeRules.RESPAWN_SECONDS
		end
	end)
	task.spawn(function()
		WorldState.WaitUntilReady()
		if not WorldState.IsGenerated() then
			-- An authored map has no zone data for wildlife yet.
			return
		end
		for _, part in CollectionService:GetTagged("SpawnCandidate") do
			if part:IsA("BasePart") then
				table.insert(spawnPoints, part.Position)
			end
		end
		while true do
			task.wait(WildlifeRules.TICK_SECONDS)
			WildlifeService.Tick()
		end
	end)
end

return WildlifeService
