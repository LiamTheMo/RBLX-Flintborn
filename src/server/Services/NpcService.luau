-- Creatures: roaming wildlife, event creatures and camp defenders (GDD §7.3,
-- Q44, §54). Simple server-driven bodies that amble around home and act by their
-- kind's behaviour (AggroRules): Hostile ones chase at-risk players who come
-- within aggro range, give up past the leash and walk home, and a hit provokes
-- them into hunting their attacker even from bow range; Neutral ones fight back,
-- with their whole group, only at players who hurt the group, until they calm
-- down; Passive ones run from nearby players and never deal damage. Players in
-- safe zones are never targeted and cannot hurt them (§3.2). Their attacks go
-- through the same combat validation as PvP (injected by CombatService), and they
-- drop physical, contested loot when killed. Wildlife far from every player stands
-- still to save work. World place only.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local AggroRules = require(ReplicatedStorage.Shared.Enemies.AggroRules)
local DamageRules = require(ReplicatedStorage.Shared.Combat.DamageRules)
local EnemyCatalog = require(ReplicatedStorage.Shared.Enemies.EnemyCatalog)
local EventRules = require(ReplicatedStorage.Shared.Events.EventRules)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Signal = require(ReplicatedStorage.Shared.Core.Signal)
local WildlifeRules = require(ReplicatedStorage.Shared.Enemies.WildlifeRules)
local WorldState = require(ReplicatedStorage.Shared.World.WorldState)
local DownedService = require(script.Parent.DownedService)
local DropService = require(script.Parent.DropService)
local ModifierService = require(script.Parent.ModifierService)
local SafeZoneService = require(script.Parent.SafeZoneService)
local WorldAdmissionService = require(script.Parent.WorldAdmissionService)

local NpcService = {}

NpcService.STEP_SECONDS = 0.1
NpcService.HIT_ALLOWANCE = 2

-- Set by CombatService: (player, rawDamage) -> boolean, applying PvP safety rules.
NpcService.DamagePlayer = function(_player: Player, _rawDamage: number): boolean
	return false
end

-- Fires (npc) when an enemy dies; npc.eventId names its event.
NpcService.Died = Signal.new()

local npcs = {}
local byPart = {}
local folder = nil
local rng = Random.new()

-- Map ground only: creatures, characters and resource nodes are see-through, so
-- nobody stands on a tree or a rock node.
local function groundParams()
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	local ignore = { folder }
	local nodes = workspace:FindFirstChild("ResourceNodes")
	if nodes then
		table.insert(ignore, nodes)
	end
	for _, player in Players:GetPlayers() do
		if player.Character then
			table.insert(ignore, player.Character)
		end
	end
	params.FilterDescendantsInstances = ignore
	return params
end

-- Creatures walk on the bed of knee-deep water, 30% slower (GDD §55).
NpcService.WATER_SPEED_MULTIPLIER = 0.7

-- The ground under a spot and whether it is in water.
local function groundAt(position: Vector3, params): (Vector3, boolean)
	local hit, wet = WorldState.Standing(position + Vector3.new(0, 20, 0), 60, params)
	return if hit then hit.Position else position, wet
end

local function label(npc)
	if npc.text == nil then
		return
	end
	npc.text.Text = ("%s\n%d / %d"):format(npc.name, math.ceil(npc.health), npc.maxHealth)
end

-- Bodies counted against the event budget: roaming wildlife has its own cap
-- (WildlifeService).
function NpcService.Count(): number
	local count = 0
	for npc in npcs do
		if not npc.wildlife then
			count += 1
		end
	end
	return count
end

-- A herd, pack or event group whose members share Neutral anger (AggroRules).
-- `wildlife` marks roaming creatures (own cap, sleep far from players).
function NpcService.NewGroup(wildlife: boolean?)
	local group = AggroRules.NewGroup()
	group.wildlife = wildlife == true
	return group
end

-- Spawns one enemy standing at `position`, in `group` (a new one of its own when
-- omitted). `elite` makes it its event's alpha. Returns its record.
function NpcService.Spawn(enemyId: string, position: Vector3, elite: boolean?, eventId: string?, group)
	local def = EnemyCatalog.Get(enemyId)
	assert(def, "Unknown enemy " .. tostring(enemyId))
	group = group or NpcService.NewGroup()
	local scale = if elite then EnemyCatalog.ELITE.size else 1
	local body = Instance.new("Part")
	body.Name = def.name
	body.Anchored = true
	body.CanCollide = false
	body.Size = def.size * scale
	body.Color = def.color
	body.Material = if def.theme == "Elemental" then Enum.Material.Neon else Enum.Material.SmoothPlastic
	local billboard = Instance.new("BillboardGui")
	billboard.Size = UDim2.fromOffset(140, 36)
	billboard.StudsOffset = Vector3.new(0, body.Size.Y / 2 + 1.5, 0)
	billboard.MaxDistance = 120
	billboard.Parent = body
	local text = Instance.new("TextLabel")
	text.Size = UDim2.fromScale(1, 1)
	text.BackgroundTransparency = 1
	text.TextColor3 = if elite or def.elite then Color3.fromRGB(255, 200, 90) else Color3.fromRGB(255, 235, 220)
	text.TextStrokeTransparency = 0.3
	text.Font = Enum.Font.GothamBold
	text.TextSize = 13
	text.Parent = billboard
	local health = def.health * (if elite then EnemyCatalog.ELITE.health else 1)
	local npc = {
		def = def,
		name = (if elite then "Alpha " else "") .. def.name,
		-- Event elites are authored strong; both kinds carry the elite drops.
		elite = elite == true or def.elite == true,
		behaviour = def.behaviour or EnemyCatalog.Behaviours.Hostile,
		group = group,
		wildlife = group.wildlife,
		body = body,
		text = text,
		health = health,
		maxHealth = health,
		damage = def.damage * (if elite then EnemyCatalog.ELITE.damage else 1),
		home = position,
		lastAttack = 0,
		eventId = eventId,
	}
	body:SetAttribute("Enemy", enemyId)
	body:SetAttribute("Behaviour", npc.behaviour)
	body.CFrame = CFrame.new(position + Vector3.new(0, body.Size.Y / 2, 0))
	body.Parent = folder
	npcs[npc] = true
	byPart[body] = npc
	label(npc)
	return npc
end

-- Registers a body driven elsewhere (bosses, pillars) so weapons can hit it.
-- `npc` = {body, name, health, maxHealth, home?, invulnerable?,
-- onDamaged(npc, amount, attacker?)?, onKilled(npc)?}. NpcService never moves it.
function NpcService.Register(npc)
	npc.custom = true
	npcs[npc] = true
	byPart[npc.body] = npc
	return npc
end

-- Removes an enemy without loot (its event ended).
function NpcService.Despawn(npc)
	if npcs[npc] then
		npcs[npc] = nil
		byPart[npc.body] = nil
		npc.body:Destroy()
	end
end

local function kill(npc)
	local position = npc.body.Position - Vector3.new(0, npc.body.Size.Y / 2, 0)
	NpcService.Despawn(npc)
	-- The killer's luck raises the chance rows only (GDD §51); certain drops stay certain.
	local killer = npc.lastAttacker
	local luck = if killer and killer.Parent then ModifierService.Sum(killer, "Luck") else 0
	for _, item in EventRules.RollLoot(npc.def.drops, rng, luck) do
		DropService.Spawn(item, position)
	end
	-- Alphas also carry the elite materials (GDD §51).
	if npc.elite then
		for _, item in EventRules.RollLoot(EnemyCatalog.ELITE_DROPS, rng, luck) do
			DropService.Spawn(item, position)
		end
	end
	NpcService.Died:Fire(npc)
end

local function rootOf(player: Player)
	return player.Character and player.Character:FindFirstChild("HumanoidRootPart")
end

-- True when `player` stands inside a safe zone, where nobody deals damage.
local function inSafeZone(player: Player): boolean
	local root = rootOf(player)
	return root ~= nil and SafeZoneService.Contains(root.Position)
end

-- `attacker` (optional) is remembered for kill credit and provokes the enemy.
function NpcService.Damage(npc, amount: number, attacker: Player?)
	if not npcs[npc] or amount <= 0 or npc.invulnerable then
		return
	end
	if attacker then
		if inSafeZone(attacker) then
			return
		end
		npc.lastAttacker = attacker
		npc.provokedAt = os.clock()
		-- Neutral herds and packs turn on whoever hurt one of them.
		AggroRules.Anger(npc.group, attacker, npc.provokedAt)
	end
	npc.health -= amount
	if npc.custom then
		if npc.onDamaged then
			npc.onDamaged(npc, amount, attacker)
		end
		if npc.health <= 0 then
			NpcService.Despawn(npc)
			if npc.onKilled then
				npc.onKilled(npc)
			end
		end
		return
	end
	if npc.health <= 0 then
		kill(npc)
	else
		label(npc)
	end
end

-- Melee against enemies, called by CombatService before structures. `canSee(part)`
-- (optional) rejects enemies behind walls.
function NpcService.Hit(
	origin: Vector3,
	aim: Vector3,
	reach: number,
	rawDamage: number,
	attacker: Player?,
	canSee: ((BasePart) -> boolean)?
): boolean
	local best, bestDistance = nil, math.huge
	for npc in npcs do
		local offset = npc.body.Position - origin
		local flat = Vector3.new(offset.X, 0, offset.Z)
		local distance = math.max(flat.Magnitude - math.max(npc.body.Size.X, npc.body.Size.Z) / 2, 0)
		if
			distance < bestDistance
			and distance <= reach + NpcService.HIT_ALLOWANCE
			and math.abs(offset.Y) <= npc.body.Size.Y / 2 + 6
			and (distance < 1 or DamageRules.WithinArc(aim, flat, 120))
			and (canSee == nil or canSee(npc.body))
		then
			best, bestDistance = npc, distance
		end
	end
	if best then
		NpcService.Damage(best, rawDamage, attacker)
		return true
	end
	return false
end

-- Arrow hits: true when `part` belongs to an enemy.
function NpcService.HitPart(part: Instance, rawDamage: number, attacker: Player?): boolean
	local npc = byPart[part]
	if npc then
		NpcService.Damage(npc, rawDamage, attacker)
		return true
	end
	return false
end

-- Living, at-risk, standing players outside safe zones can be hunted.
function NpcService.CanTarget(player: Player): boolean
	local humanoid = player.Character and player.Character:FindFirstChildOfClass("Humanoid")
	return humanoid ~= nil
		and humanoid.Health > 0
		and WorldAdmissionService.IsAtRisk(player)
		and not DownedService.IsDowned(player)
		and not inSafeZone(player)
end
local canTarget = NpcService.CanTarget

-- The attacker a recent hit provoked `npc` into hunting, and their root, if any.
function NpcService.Provoker(npc, leash: number, now: number)
	local attacker = npc.lastAttacker
	local root = attacker and rootOf(attacker)
	if root and canTarget(attacker) and AggroRules.Provoked(npc.provokedAt, now, npc.home, root.Position, leash) then
		return attacker, root
	end
	return nil, nil
end

-- Whom a Hostile or Neutral creature goes after now, with their root and distance.
local function huntTarget(npc, position: Vector3, roots, now: number)
	local target, targetRoot, best = nil, nil, math.huge
	local neutral = npc.behaviour == EnemyCatalog.Behaviours.Neutral
	for player, root in roots do
		local distance = (root.Position - position).Magnitude
		local fromHome = (root.Position - npc.home).Magnitude
		local wanted
		if neutral then
			-- Fights back anywhere a hit could have come from, while still angry.
			wanted = fromHome <= EnemyCatalog.LEASH + AggroRules.BOW_RANGE
				and AggroRules.Hunts(npc.behaviour, npc.group, player, now)
		else
			wanted = distance <= EnemyCatalog.AGGRO and fromHome <= EnemyCatalog.LEASH
		end
		-- The cheap range tests first: canTarget scans every safe zone.
		if wanted and distance < best and canTarget(player) then
			target, targetRoot, best = player, root, distance
		end
	end
	if target == nil and not neutral then
		-- Hit from out of aggro range: go after the attacker.
		target, targetRoot = NpcService.Provoker(npc, EnemyCatalog.LEASH, now)
		best = if targetRoot then (targetRoot.Position - position).Magnitude else best
	end
	return target, targetRoot, best
end

-- What a Passive creature runs from: players close by (farther once hurt) and
-- whoever just shot it.
local function threats(npc, position: Vector3, roots, now: number)
	local hurt = npc.provokedAt ~= nil and now - npc.provokedAt <= AggroRules.PROVOKE_SECONDS
	local radius = if hurt then AggroRules.PANIC_RADIUS else AggroRules.FLEE_RADIUS
	local list = {}
	for player, root in roots do
		local humanoid = player.Character and player.Character:FindFirstChildOfClass("Humanoid")
		local alive = humanoid ~= nil and humanoid.Health > 0
		if alive and ((root.Position - position).Magnitude <= radius or (hurt and player == npc.lastAttacker)) then
			table.insert(list, root.Position)
		end
	end
	return list
end

local function wander(npc, position: Vector3, now: number): Vector3
	if npc.wanderGoal == nil or now >= npc.wanderUntil then
		npc.wanderGoal = AggroRules.WanderGoal(npc.home, position, rng)
		npc.wanderUntil = now + rng:NextNumber(4, 9)
	end
	return npc.wanderGoal
end

local function step(dt: number)
	local params = groundParams()
	local now = os.clock()
	local roots, rootPositions = {}, {}
	for _, player in Players:GetPlayers() do
		local root = rootOf(player)
		if root then
			roots[player] = root
			table.insert(rootPositions, root.Position)
		end
	end
	for npc in npcs do
		if npc.custom then
			continue
		end
		local position = npc.body.Position
		if npc.wildlife and not WildlifeRules.AnyNear({ position }, rootPositions, WildlifeRules.SLEEP_RADIUS) then
			continue
		end
		local target, targetRoot, best, goal = nil, nil, math.huge, nil
		if npc.behaviour == EnemyCatalog.Behaviours.Passive then
			goal = AggroRules.FleeGoal(position, threats(npc, position, roots, now), npc.home, EnemyCatalog.LEASH)
		else
			target, targetRoot, best = huntTarget(npc, position, roots, now)
			goal = if targetRoot then targetRoot.Position else nil
		end
		local speed = npc.def.speed
		if goal then
			npc.wanderGoal = nil
		else
			goal, speed = wander(npc, position, now), npc.def.speed * AggroRules.WANDER_SPEED
		end
		local flat = Vector3.new(goal.X - position.X, 0, goal.Z - position.Z)
		local reach = npc.def.reach + npc.body.Size.Z / 2
		if target and best <= reach then
			if now - npc.lastAttack >= npc.def.cooldown then
				npc.lastAttack = now
				NpcService.DamagePlayer(target, npc.damage)
				-- A Hostile member's fight is its group's: protective boars join their alpha.
				if npc.behaviour == EnemyCatalog.Behaviours.Hostile then
					AggroRules.Anger(npc.group, target, now)
				end
			end
		elseif flat.Magnitude > 1 then
			if npc.inWater then
				speed *= NpcService.WATER_SPEED_MULTIPLIER
			end
			local move = flat.Unit * math.min(speed * dt, flat.Magnitude)
			local ground, wet = groundAt(position + move, params)
			npc.inWater = wet
			npc.body.CFrame = CFrame.lookAt(
				ground + Vector3.new(0, npc.body.Size.Y / 2, 0),
				ground + Vector3.new(0, npc.body.Size.Y / 2, 0) + flat.Unit
			)
		end
	end
end

function NpcService.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	folder = Instance.new("Folder")
	folder.Name = "EventEnemies"
	folder.Parent = workspace
	-- Kill credit and provocation must not keep departed players alive.
	Players.PlayerRemoving:Connect(function(player)
		for npc in npcs do
			if npc.lastAttacker == player then
				npc.lastAttacker = nil
				npc.provokedAt = nil
			end
			if npc.group then
				npc.group.angry[player] = nil
			end
		end
	end)
	local elapsed = 0
	RunService.Heartbeat:Connect(function(dt)
		elapsed += dt
		if elapsed >= NpcService.STEP_SECONDS then
			step(elapsed)
			elapsed = 0
		end
	end)
end

return NpcService
