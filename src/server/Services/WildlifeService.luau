-- Roaming wildlife (GDD §54, owner decisions 2026-10-28). Keeps each map zone's
-- few small groups of regular creatures filled from its spawn table
-- (WildlifeRules), placed in their habitat by IslandLayout.RandomPointIn. A killed
-- or despawned group's slot refills about three minutes later, never within
-- PLAYER_CLEARANCE of a player or inside a safe zone. A hard cap bounds the
-- island's creatures; when it is full, a group nobody has been near for a while
-- is despawned to make room. NpcService drives the bodies. Until the map provides
-- RandomPointIn nothing spawns. World place only.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local WildlifeRules = require(ReplicatedStorage.Shared.Enemies.WildlifeRules)
local NpcService = require(script.Parent.NpcService)
local SafeZoneService = require(script.Parent.SafeZoneService)

local WildlifeService = {}

-- slot = {zone, readyAt, group?}; group = {slot, members = {npc -> true}, size, lastNear}.
local slots = {}
local owners = {}
local alive = 0
local rng = Random.new()
local layout = nil

local function now(): number
	return os.clock()
end

-- The world layout, if it is there and loads (it lands with the map work).
local function loadLayout()
	local world = ReplicatedStorage.Shared:FindFirstChild("World")
	local module = world and world:FindFirstChild("IslandLayout")
	if module == nil then
		return nil
	end
	local ok, result = pcall(require, module)
	return if ok and type(result) == "table" then result else nil
end

local function randomPoint(zoneId: string, habitat: string?): Vector3?
	if layout == nil or type(layout.RandomPointIn) ~= "function" then
		return nil
	end
	local ok, point = pcall(layout.RandomPointIn, zoneId, rng, habitat)
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
	for _, name in { "EventEnemies", "WorldEvents", "Bosses", "GuardianArena", "Arrows" } do
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
	local hit = workspace:Raycast(position + Vector3.new(0, 30, 0), Vector3.new(0, -80, 0), params)
	return if hit and hit.Material ~= Enum.Material.Water then hit.Position else position
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

-- A spot for a group in `zoneId`'s `habitat`, away from players and safe zones.
local function place(zoneId: string, habitat: string?): Vector3?
	local players = playerPositions()
	for _ = 1, WildlifeRules.PLACEMENT_ATTEMPTS do
		local point = randomPoint(zoneId, habitat)
		if point and WildlifeRules.ClearOfPlayers(point, players) and not SafeZoneService.Contains(point) then
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
	local center = place(slot.zone, entry.habitat)
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
	layout = loadLayout()
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
		while true do
			task.wait(WildlifeRules.TICK_SECONDS)
			WildlifeService.Tick()
		end
	end)
end

return WildlifeService
