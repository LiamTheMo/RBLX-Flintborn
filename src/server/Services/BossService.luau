-- Shared boss lifecycle (GDD §8, Q45–48, Q147). A boss starts from its authored
-- baseline times a scaling multiplier snapshotted at spawn from the active
-- population's level and gear. It hunts contesting players near its home with
-- three attack patterns — Slam (melee), Bolt (slow projectile) and Quake
-- (telegraphed area) — and resets by its source's rule when nobody contests it.
-- A hit from beyond aggro range provokes it: it stays leashed but answers the
-- attacker with Bolts and Quakes (AggroRules). Players in safe zones are never
-- targeted. Everyone who damaged it is in boss.contributors. It walks on the
-- ground like other enemies. Loot spills on death as physical, contested drops.
-- World place only.
--
-- A boss is an anchored, invisible hitbox Part (`boss.npc.body`, the part
-- weapons hit and the boss bar reads) with its placeholder model welded on
-- (CreatureModels). A shielded boss also wears a translucent bubble. The hitbox
-- rests on the ground and turns to face its target.

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local AggroRules = require(ReplicatedStorage.Shared.Enemies.AggroRules)
local BossCatalog = require(ReplicatedStorage.Shared.Bosses.BossCatalog)
local BossRules = require(ReplicatedStorage.Shared.Bosses.BossRules)
local BossScaling = require(ReplicatedStorage.Shared.Bosses.BossScaling)
local Characters = require(ReplicatedStorage.Shared.World.Characters)
local CreatureModels = require(ReplicatedStorage.Shared.Visuals.CreatureModels)
local EventRules = require(ReplicatedStorage.Shared.Events.EventRules)
local ModelBuilder = require(ReplicatedStorage.Shared.Visuals.ModelBuilder)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Signal = require(ReplicatedStorage.Shared.Core.Signal)
local WorldState = require(ReplicatedStorage.Shared.World.WorldState)
local DropService = require(script.Parent.DropService)
local InventoryService = require(script.Parent.InventoryService)
local ModifierService = require(script.Parent.ModifierService)
local NpcService = require(script.Parent.NpcService)
local ProfileService = require(script.Parent.ProfileService)
local WorldAdmissionService = require(script.Parent.WorldAdmissionService)

local BossService = {}

-- Fires (boss) when a boss is defeated (participation XP, telemetry).
BossService.Defeated = Signal.new()

BossService.STEP_SECONDS = 0.2
BossService.ATTACK_SECONDS = 2.5
BossService.AGGRO = 70
BossService.LEASH = 110
BossService.CONTEST_RADIUS = 120
BossService.BOLT_SPEED = 35
BossService.BOLT_RADIUS = 4
BossService.QUAKE_RADIUS = 12
BossService.QUAKE_WARNING = 1.5
-- A bolt flies at least this far, and far enough to reach a provoking attacker.
BossService.BOLT_MIN_RANGE = BossService.BOLT_SPEED * 3

local bosses = {}
local folder = nil
local rng = Random.new()

-- Living, at-risk, standing players outside safe zones (§3.2).
local canTarget = NpcService.CanTarget

-- Level and gear of every at-risk player right now (frozen by the caller).
local function population()
	local entries = {}
	for _, player in Players:GetPlayers() do
		if WorldAdmissionService.IsAtRisk(player) then
			local profile = ProfileService.GetProfile(player)
			table.insert(entries, {
				level = profile and profile.progression.level or 1,
				gearScore = BossScaling.GearScore(InventoryService.Items(player)),
			})
		end
	end
	return entries
end

-- Puts the shield bubble on a shielded boss and takes it off when it drops.
local function showShield(boss)
	local shielded = boss.npc.invulnerable == true
	if shielded and boss.shield == nil then
		boss.shield = ModelBuilder.Decorate(boss.npc.body, CreatureModels.Shield())[1]
	elseif not shielded and boss.shield then
		boss.shield:Destroy()
		boss.shield = nil
	end
end

local function publish(boss)
	local body = boss.npc.body
	showShield(boss)
	body:SetAttribute("HP", math.max(0, math.ceil(boss.npc.health)))
	body:SetAttribute("MaxHP", boss.npc.maxHealth)
	body:SetAttribute("Phase", boss.phase)
	body:SetAttribute("Shielded", boss.npc.invulnerable == true)
end

function BossService.SetPhase(boss, phase: string)
	boss.phase = phase
	publish(boss)
end

function BossService.SetShielded(boss, shielded: boolean)
	boss.npc.invulnerable = shielded
	publish(boss)
end

local function hurtNear(position: Vector3, radius: number, damage: number)
	for _, player in Players:GetPlayers() do
		local root = Characters.RootOf(player)
		if root and canTarget(player) and (root.Position - position).Magnitude <= radius then
			NpcService.DamagePlayer(player, damage)
		end
	end
end

local function bolt(boss, targetPosition: Vector3)
	local origin = boss.npc.body.Position
	local direction = (targetPosition - origin)
	if direction.Magnitude < 1 then
		return
	end
	local range = math.max(BossService.BOLT_MIN_RANGE, direction.Magnitude + BossService.BOLT_RADIUS * 2)
	direction = direction.Unit
	local orb = Instance.new("Part")
	orb.Name = "BossBolt"
	orb.Shape = Enum.PartType.Ball
	orb.Anchored = true
	orb.CanCollide = false
	orb.CanQuery = false
	orb.Material = Enum.Material.Neon
	orb.Color = boss.npc.body.Color
	orb.Size = Vector3.new(2.5, 2.5, 2.5)
	orb.CFrame = CFrame.new(origin)
	orb.Parent = folder
	local travelled, damage = 0, boss.damage * 0.8
	local connection
	local function stop()
		connection:Disconnect()
		orb:Destroy()
	end
	connection = RunService.Heartbeat:Connect(function(dt)
		travelled += BossService.BOLT_SPEED * dt
		if travelled > range then
			stop()
			return
		end
		local position = origin + direction * travelled
		orb.CFrame = CFrame.new(position)
		for _, player in Players:GetPlayers() do
			local root = Characters.RootOf(player)
			if root and canTarget(player) and (root.Position - position).Magnitude <= BossService.BOLT_RADIUS then
				-- A slow bolt hits the first player it reaches, once.
				NpcService.DamagePlayer(player, damage)
				stop()
				return
			end
		end
	end)
end

local function quake(boss, targetPosition: Vector3)
	local warning = Instance.new("Part")
	warning.Name = "QuakeWarning"
	warning.Shape = Enum.PartType.Cylinder
	warning.Anchored = true
	warning.CanCollide = false
	warning.CanQuery = false
	warning.Material = Enum.Material.Neon
	warning.Color = Color3.fromRGB(230, 60, 40)
	warning.Transparency = 0.5
	warning.Size = Vector3.new(0.3, BossService.QUAKE_RADIUS * 2, BossService.QUAKE_RADIUS * 2)
	warning.CFrame = CFrame.new(targetPosition) * CFrame.Angles(0, 0, math.rad(90))
	warning.Parent = folder
	local damage = boss.damage * 1.2
	task.delay(BossService.QUAKE_WARNING, function()
		warning:Destroy()
		if bosses[boss.id] then
			hurtNear(targetPosition, BossService.QUAKE_RADIUS, damage)
		end
	end)
end

local function attack(boss, target: Player, distance: number)
	local root = Characters.RootOf(target)
	if root == nil then
		return
	end
	local options = {}
	for _, name in boss.def.attacks do
		if name ~= "Slam" or distance <= boss.reach then
			table.insert(options, name)
		end
	end
	if #options == 0 then
		return
	end
	local choice = options[rng:NextInteger(1, #options)]
	if choice == "Slam" then
		hurtNear(boss.npc.body.Position, boss.reach, boss.damage)
	elseif choice == "Bolt" then
		bolt(boss, root.Position)
	else
		quake(boss, root.Position - Vector3.new(0, 2.5, 0))
	end
end

-- Removes a boss without loot (reset, or its event or hold ended).
function BossService.Despawn(boss, reason: string?)
	if bosses[boss.id] == nil then
		return
	end
	bosses[boss.id] = nil
	NpcService.Despawn(boss.npc)
	if boss.options.onEnded then
		boss.options.onEnded(boss, reason or "Despawned")
	end
end

function BossService.Heal(boss)
	boss.npc.health = boss.npc.maxHealth
	publish(boss)
end

-- Spawns a boss. options = {source, shielded?, onDamaged(boss, before, after)?,
-- onEnded(boss, reason)?, expired()?, structureGone()?}. Returns the boss.
function BossService.Spawn(bossId: string, position: Vector3, options)
	local def = BossCatalog.Get(bossId)
	assert(def, "Unknown boss " .. tostring(bossId))
	local snapshot = BossScaling.Snapshot(population())
	-- The hitbox: invisible, never blocks anyone, but arrows and rays still find it.
	local body = Instance.new("Part")
	body.Name = def.name
	body.Anchored = true
	body.CanCollide = false
	body.CanQuery = true
	body.CanTouch = false
	body.Transparency = 1
	body.Size = def.size
	-- The bolts take their colour from it.
	body.Color = def.color
	body.CFrame = CFrame.new(position + Vector3.new(0, def.size.Y / 2, 0))
	ModelBuilder.Decorate(body, CreatureModels.ForBoss(bossId))
	body:SetAttribute("BossName", def.name)
	body:SetAttribute("Source", def.source)
	body:SetAttribute("Scaling", snapshot.multiplier)
	body.Parent = folder
	local health = def.health * snapshot.multiplier
	local boss = {
		id = HttpService:GenerateGUID(false),
		def = def,
		source = options.source or def.source,
		home = position,
		damage = def.damage * snapshot.multiplier,
		reach = def.reach,
		multiplier = snapshot.multiplier,
		lastAttack = 0,
		lastContested = os.clock(),
		phase = "Fight",
		options = options,
		-- Player -> damage dealt, for everyone who damaged it (participation credit).
		contributors = {},
	}
	boss.npc = NpcService.Register({
		body = body,
		name = def.name,
		home = position,
		health = health,
		maxHealth = health,
		invulnerable = options.shielded == true,
		onDamaged = function(npc, amount, attacker)
			boss.lastContested = os.clock()
			if attacker then
				boss.contributors[attacker] = (boss.contributors[attacker] or 0) + amount
			end
			if options.onDamaged then
				options.onDamaged(boss, npc.health + amount, npc.health)
			end
			publish(boss)
		end,
		onKilled = function()
			if bosses[boss.id] == nil then
				return
			end
			bosses[boss.id] = nil
			local at = body.Position - Vector3.new(0, def.size.Y / 2, 0)
			-- The top damage dealer's luck raises the chance rows (GDD §51).
			local top = BossService.TopContributor(boss)
			local luck = if top then ModifierService.Sum(top, "Luck") else 0
			for _, item in EventRules.RollLoot(def.loot, rng, luck) do
				DropService.Spawn(item, at + Vector3.new(rng:NextNumber(-5, 5), 0, rng:NextNumber(-5, 5)))
			end
			BossService.Defeated:Fire(boss)
			if options.onEnded then
				options.onEnded(boss, "Defeated")
			end
		end,
	})
	body:SetAttribute("EncounterId", boss.id)
	bosses[boss.id] = boss
	publish(boss)
	return boss
end

local function groundParams()
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	local ignore = { folder }
	-- Only the map is ground: never climb onto pillars, walls, bases or other bodies.
	for _, name in { "EventEnemies", "Arrows", "GuardianArena", "WorldEvents", "PlayerStructures", "ResourceNodes" } do
		local other = workspace:FindFirstChild(name)
		if other then
			table.insert(ignore, other)
		end
	end
	-- Solid island scenery (trunks, boulders, logs) is queryable but never ground.
	local scenery = WorldState.Scenery()
	if scenery then
		table.insert(ignore, scenery)
	end
	for _, player in Players:GetPlayers() do
		if player.Character then
			table.insert(ignore, player.Character)
		end
	end
	params.FilterDescendantsInstances = ignore
	params.RespectCanCollide = true
	return params
end

-- Bosses follow the terrain like other enemies.
local function groundAt(position: Vector3, params): Vector3
	local hit = workspace:Raycast(position + Vector3.new(0, 20, 0), Vector3.new(0, -60, 0), params)
	return if hit then hit.Position else position
end

local function step(dt: number)
	local now = os.clock()
	local params = groundParams()
	for _, boss in bosses do
		local body = boss.npc.body
		local position = body.Position
		-- Where the hitbox stands: its bottom, on the ground.
		local feet = position - Vector3.new(0, body.Size.Y / 2, 0)
		local target, best = nil, BossService.AGGRO
		for _, player in Players:GetPlayers() do
			local root = Characters.RootOf(player)
			if root and canTarget(player) then
				local distance = (root.Position - position).Magnitude
				if distance <= BossService.CONTEST_RADIUS then
					boss.lastContested = now
				end
				if distance < best and (root.Position - boss.home).Magnitude <= BossService.LEASH then
					target, best = player, distance
				end
			end
		end
		if target == nil then
			-- Hit from beyond aggro range: answer the attacker from the arena.
			local provoker, provokerRoot = NpcService.Provoker(boss.npc, BossService.LEASH, now)
			if provoker then
				target, best = provoker, (provokerRoot.Position - position).Magnitude
			end
		end
		local action = BossRules.ResetAction(boss.source, {
			idleSeconds = now - boss.lastContested,
			eventExpired = boss.options.expired and boss.options.expired() or false,
			structureGone = boss.options.structureGone and boss.options.structureGone() or false,
		})
		if action == "Despawn" then
			BossService.Despawn(boss, "Reset")
			continue
		elseif action == "Heal" and boss.npc.health < boss.npc.maxHealth then
			BossService.Heal(boss)
		end
		-- Bosses never leave their leash, even to chase a provoking archer.
		local goal = AggroRules.ClampToLeash(
			boss.home,
			if target then Characters.RootOf(target).Position else boss.home,
			BossService.LEASH
		)
		local flat = Vector3.new(goal.X - position.X, 0, goal.Z - position.Z)
		if target and now - boss.lastAttack >= BossService.ATTACK_SECONDS then
			boss.lastAttack = now
			attack(boss, target, best)
		end
		if flat.Magnitude > (if target then boss.reach * 0.8 else 2) then
			local move = flat.Unit * math.min(boss.def.speed * dt, flat.Magnitude)
			-- Cast from the feet, which is also where it stays if the map ends here.
			local standing = groundAt(feet + move, params) + Vector3.new(0, body.Size.Y / 2, 0)
			body.CFrame = CFrame.lookAt(standing, standing + flat.Unit)
		elseif target and flat.Magnitude > 0.1 then
			-- Within reach it still turns to face whom it fights.
			body.CFrame = CFrame.lookAt(position, position + flat.Unit)
		end
	end
end

-- The player still in the server who dealt the boss the most damage, or nil.
function BossService.TopContributor(boss): Player?
	local best, bestDamage = nil, 0
	for player, damage in boss.contributors do
		if player.Parent and damage > bestDamage then
			best, bestDamage = player, damage
		end
	end
	return best
end

function BossService.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	folder = Instance.new("Folder")
	folder.Name = "Bosses"
	folder.Parent = workspace
	Players.PlayerRemoving:Connect(function(player)
		for _, boss in bosses do
			boss.contributors[player] = nil
		end
	end)
	local elapsed = 0
	RunService.Heartbeat:Connect(function(dt)
		elapsed += dt
		if elapsed >= BossService.STEP_SECONDS then
			step(elapsed)
			elapsed = 0
		end
	end)
end

return BossService
