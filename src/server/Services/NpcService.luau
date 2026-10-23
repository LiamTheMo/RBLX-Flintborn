-- Event creatures and camp defenders (GDD §7.3, Q44). Simple server-driven
-- enemies: idle near home, chase at-risk players who come within aggro range,
-- give up past the leash and walk home. Their attacks go through the same combat
-- validation as PvP (injected by CombatService), and they drop physical,
-- contested loot when killed. World place only.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local DamageRules = require(ReplicatedStorage.Shared.Combat.DamageRules)
local EnemyCatalog = require(ReplicatedStorage.Shared.Enemies.EnemyCatalog)
local EventRules = require(ReplicatedStorage.Shared.Events.EventRules)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Signal = require(ReplicatedStorage.Shared.Core.Signal)
local DownedService = require(script.Parent.DownedService)
local DropService = require(script.Parent.DropService)
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

local function groundParams()
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	local ignore = { folder }
	for _, player in Players:GetPlayers() do
		if player.Character then
			table.insert(ignore, player.Character)
		end
	end
	params.FilterDescendantsInstances = ignore
	return params
end

local function groundAt(position: Vector3, params): Vector3
	local hit = workspace:Raycast(position + Vector3.new(0, 20, 0), Vector3.new(0, -60, 0), params)
	return if hit then hit.Position else position
end

local function label(npc)
	npc.text.Text = ("%s\n%d / %d"):format(npc.name, math.ceil(npc.health), npc.maxHealth)
end

function NpcService.Count(): number
	local count = 0
	for _ in npcs do
		count += 1
	end
	return count
end

-- Spawns one enemy standing at `position`. Returns its record.
function NpcService.Spawn(enemyId: string, position: Vector3, elite: boolean?, eventId: string?)
	local def = EnemyCatalog.Get(enemyId)
	assert(def, "Unknown enemy " .. tostring(enemyId))
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
	text.TextColor3 = if elite then Color3.fromRGB(255, 200, 90) else Color3.fromRGB(255, 235, 220)
	text.TextStrokeTransparency = 0.3
	text.Font = Enum.Font.GothamBold
	text.TextSize = 13
	text.Parent = billboard
	local health = def.health * (if elite then EnemyCatalog.ELITE.health else 1)
	local npc = {
		def = def,
		name = (if elite then "Alpha " else "") .. def.name,
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
	body.CFrame = CFrame.new(position + Vector3.new(0, body.Size.Y / 2, 0))
	body.Parent = folder
	npcs[npc] = true
	byPart[body] = npc
	label(npc)
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
	for _, item in EventRules.RollLoot(npc.def.drops, rng) do
		DropService.Spawn(item, position)
	end
	NpcService.Died:Fire(npc)
end

function NpcService.Damage(npc, amount: number)
	if not npcs[npc] or amount <= 0 then
		return
	end
	npc.health -= amount
	if npc.health <= 0 then
		kill(npc)
	else
		label(npc)
	end
end

-- Melee against enemies, called by CombatService before structures.
function NpcService.Hit(origin: Vector3, aim: Vector3, reach: number, rawDamage: number): boolean
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
		then
			best, bestDistance = npc, distance
		end
	end
	if best then
		NpcService.Damage(best, rawDamage)
		return true
	end
	return false
end

-- Arrow hits: true when `part` belongs to an enemy.
function NpcService.HitPart(part: Instance, rawDamage: number): boolean
	local npc = byPart[part]
	if npc then
		NpcService.Damage(npc, rawDamage)
		return true
	end
	return false
end

local function canTarget(player: Player): boolean
	local humanoid = player.Character and player.Character:FindFirstChildOfClass("Humanoid")
	return humanoid ~= nil
		and humanoid.Health > 0
		and WorldAdmissionService.IsAtRisk(player)
		and not DownedService.IsDowned(player)
end

local function step(dt: number)
	local params = groundParams()
	local now = os.clock()
	for npc in npcs do
		local position = npc.body.Position
		local target, targetRoot, best = nil, nil, EnemyCatalog.AGGRO
		for _, player in Players:GetPlayers() do
			local root = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
			if root and canTarget(player) and (root.Position - npc.home).Magnitude <= EnemyCatalog.LEASH then
				local distance = (root.Position - position).Magnitude
				if distance < best then
					target, targetRoot, best = player, root, distance
				end
			end
		end
		local goal = if targetRoot then targetRoot.Position else npc.home
		local flat = Vector3.new(goal.X - position.X, 0, goal.Z - position.Z)
		local reach = npc.def.reach + npc.body.Size.Z / 2
		if target and best <= reach then
			if now - npc.lastAttack >= npc.def.cooldown then
				npc.lastAttack = now
				NpcService.DamagePlayer(target, npc.damage)
			end
		elseif flat.Magnitude > 1 then
			local move = flat.Unit * math.min(npc.def.speed * dt, flat.Magnitude)
			local ground = groundAt(position + move, params)
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
