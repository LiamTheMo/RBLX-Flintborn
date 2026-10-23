-- Server-authoritative combat (GDD §5.1, §5.5, §21.1, §21.5). Clients send attack
-- intent (aim direction, draw time) with increasing sequence numbers; the server
-- picks targets from its own positions, enforces cadence, reach, arc, line of
-- sight, risk state, friendly fire and safe zones, and applies damage through
-- armor EHP. Nobody inside a safe zone deals damage to anything (§3.2). Arrows
-- leave from the head, and draw time is capped at what the server saw. World only.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local ArmorRules = require(ReplicatedStorage.Shared.Combat.ArmorRules)
local DamageRules = require(ReplicatedStorage.Shared.Combat.DamageRules)
local GameConstants = require(ReplicatedStorage.Shared.GameConstants)
local ModifierRules = require(ReplicatedStorage.Shared.Progression.ModifierRules)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local SessionStates = require(ReplicatedStorage.Shared.Admission.SessionStates)
local Signal = require(ReplicatedStorage.Shared.Core.Signal)
local WeaponCatalog = require(ReplicatedStorage.Shared.Combat.WeaponCatalog)
local BuildingService = require(script.Parent.BuildingService)
local DownedService = require(script.Parent.DownedService)
local InventoryService = require(script.Parent.InventoryService)
local ModifierService = require(script.Parent.ModifierService)
local NpcService = require(script.Parent.NpcService)
local ProjectileService = require(script.Parent.ProjectileService)
local SafeZoneService = require(script.Parent.SafeZoneService)
local WorldAdmissionService = require(script.Parent.WorldAdmissionService)

local CombatService = {}

-- Fires (attacker, targetPlayer, rawDamage, newHealth) after damage is applied.
CombatService.Damaged = Signal.new()
-- Fires (targetPlayer) whenever a player takes damage from anything.
CombatService.Hurt = Signal.new()

local lastAttack = {}
local lastSequence = {}
-- When each player's run began: the first draw cannot predate it.
local runStartedAt = {}

local function rootOf(player: Player)
	local character = player.Character
	return character and character:FindFirstChild("HumanoidRootPart")
end

local function aliveHumanoid(player: Player): Humanoid?
	local humanoid = player.Character and player.Character:FindFirstChildOfClass("Humanoid")
	return humanoid and humanoid.Health > 0 and humanoid or nil
end

local function actor(player: Player)
	local root = rootOf(player)
	return {
		state = WorldAdmissionService.GetState(player),
		tribeId = player:GetAttribute("TribeId"),
		inSafeZone = root ~= nil and SafeZoneService.Contains(root.Position),
	}
end

-- Applies armor-reduced damage, routing tribe members into the downed state.
-- Returns the target's new health.
local function applyDamage(target: Player, humanoid: Humanoid, rawDamage: number): number
	CombatService.Hurt:Fire(target)
	if DownedService.IsDowned(target) then
		-- Finishing a downed player is allowed at any time, even mid-revive (Q68).
		DownedService.DamageDowned(target, rawDamage)
		return humanoid.Health
	end
	local factor = ArmorRules.Factor(InventoryService.ArmorPieces(target))
	local newHealth = GameConstants.ApplyDamage(humanoid.Health, factor, rawDamage)
	if newHealth <= 0 and DownedService.TryDown(target) then
		-- Tribe members go down instead of dying (GDD §5.3).
		return humanoid.Health
	end
	humanoid.Health = newHealth
	return newHealth
end

-- Applies raw damage from `attacker` to `target` if the rules allow it.
-- Returns true when damage was applied.
function CombatService.ApplyHit(attacker: Player, target: Player, rawDamage: number): boolean
	if attacker == target then
		return false
	end
	local humanoid = aliveHumanoid(target)
	if humanoid == nil or DownedService.IsDowned(attacker) then
		return false
	end
	if not DamageRules.CanDamage(actor(attacker), actor(target)) then
		return false
	end
	-- PvP mastery combat perk, bounded at +5% (Q76).
	rawDamage = ModifierRules.Raw(rawDamage, ModifierService.Get(attacker, "PvpDamage"))
	local newHealth = applyDamage(target, humanoid, rawDamage)
	Remotes.Get("CombatFeedback"):FireClient(attacker, "Hit", math.round(rawDamage))
	Remotes.Get("CombatFeedback"):FireClient(target, "Hurt", math.round(rawDamage))
	CombatService.Damaged:Fire(attacker, target, rawDamage, newHealth)
	return true
end

-- Damage from the world (traps, event creatures) under the same safety rules as player hits: only
-- at-risk players outside safe zones can be hurt.
function CombatService.ApplyEnvironmentHit(target: Player, rawDamage: number): boolean
	local humanoid = aliveHumanoid(target)
	local victim = actor(target)
	if humanoid == nil or not SessionStates.IsAtRisk(victim.state) or victim.inSafeZone then
		return false
	end
	applyDamage(target, humanoid, rawDamage)
	Remotes.Get("CombatFeedback"):FireClient(target, "Hurt", math.round(rawDamage))
	return true
end

-- Accepts each client sequence number once and only in increasing order.
local function acceptSequence(player: Player, sequence: any): boolean
	if type(sequence) ~= "number" or sequence % 1 ~= 0 then
		return false
	end
	if lastSequence[player] and sequence <= lastSequence[player] then
		return false
	end
	lastSequence[player] = sequence
	return true
end

local function validDirection(direction: any): Vector3?
	if typeof(direction) ~= "Vector3" or direction.Magnitude < 0.5 or direction.Magnitude ~= direction.Magnitude then
		return nil
	end
	return direction.Unit
end

local function readyToAttack(player: Player, cooldown: number): boolean
	local now = os.clock()
	if not DamageRules.CooldownReady(lastAttack[player], now, cooldown) then
		return false
	end
	lastAttack[player] = now
	return true
end

-- Everything a line-of-sight ray ignores: characters never block a swing.
local function characters()
	local list = {}
	for _, other in Players:GetPlayers() do
		if other.Character then
			table.insert(list, other.Character)
		end
	end
	return list
end

-- True when nothing solid (structures, ground, terrain) lies between `from` and
-- `to`, other than `target` itself.
local function clearLine(from: Vector3, to: Vector3, ignore, target: Instance?): boolean
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	params.FilterDescendantsInstances = ignore
	params.RespectCanCollide = true
	params.IgnoreWater = true
	local hit = workspace:Raycast(from, to - from, params)
	return hit == nil or (target ~= nil and (hit.Instance == target or hit.Instance:IsDescendantOf(target)))
end

local function inSafeZone(player: Player): boolean
	local root = rootOf(player)
	return root ~= nil and SafeZoneService.Contains(root.Position)
end

local function melee(player: Player, sequence: any, direction: any)
	local aim = validDirection(direction)
	local root = rootOf(player)
	local head = player.Character and player.Character:FindFirstChild("Head")
	if not acceptSequence(player, sequence) or aim == nil or root == nil or head == nil then
		return
	end
	if aliveHumanoid(player) == nil or not WorldAdmissionService.IsAtRisk(player) or inSafeZone(player) then
		return
	end
	local equipped = InventoryService.Equipped(player)
	local profile = WeaponCatalog.For(equipped and equipped.catalogId)
	if profile.kind ~= "Melee" or DownedService.IsDowned(player) or not readyToAttack(player, profile.cooldown) then
		return
	end
	local ignore = characters()
	local function canSee(part: BasePart): boolean
		return clearLine(head.Position, part.Position, ignore, part)
	end
	local flatAim = Vector3.new(aim.X, 0, aim.Z)
	local attacker = actor(player)
	local best, bestDistance = nil, math.huge
	for _, other in Players:GetPlayers() do
		local otherRoot = other ~= player and rootOf(other)
		if otherRoot then
			local offset = otherRoot.Position - root.Position
			local distance = offset.Magnitude
			-- Only targets this swing could actually hurt compete, so an untouchable
			-- tribe-mate in front never absorbs a hit meant for an enemy.
			if
				distance < bestDistance
				and DamageRules.WithinReach(distance, profile.reach)
				and DamageRules.WithinArc(flatAim, Vector3.new(offset.X, 0, offset.Z), profile.arc)
				and DamageRules.CanDamage(attacker, actor(other))
				and canSee(otherRoot)
			then
				best, bestDistance = other, distance
			end
		end
	end
	local damage = DamageRules.MeleeDamage(profile, equipped and equipped.qualityRoll)
	if best then
		CombatService.ApplyHit(player, best, damage)
	elseif not NpcService.Hit(root.Position, flatAim, profile.reach, damage, player, canSee) then
		-- Raiding: the same swing damages another tribe's structures (GDD Q38).
		BuildingService.Hit(player, root.Position, flatAim, profile.reach, damage, canSee)
	end
end

local function shoot(player: Player, sequence: any, drawSeconds: any, direction: any)
	local aim = validDirection(direction)
	local character = player.Character
	local head = character and character:FindFirstChild("Head")
	if not acceptSequence(player, sequence) or aim == nil or head == nil or aliveHumanoid(player) == nil then
		return
	end
	if type(drawSeconds) ~= "number" or drawSeconds ~= drawSeconds or not WorldAdmissionService.IsAtRisk(player) then
		return
	end
	if inSafeZone(player) then
		return
	end
	local equipped = InventoryService.Equipped(player)
	local profile = WeaponCatalog.For(equipped and equipped.catalogId)
	local previous = lastAttack[player] or runStartedAt[player]
	if profile.kind ~= "Bow" or DownedService.IsDowned(player) or not readyToAttack(player, profile.cooldown) then
		return
	end
	-- Each shot consumes one crafted arrow (GDD Q28).
	if not InventoryService.RemoveAll(player, { Arrow = 1 }) then
		InventoryService.Notify(player, "You have no arrows.")
		return
	end
	local damage = DamageRules.ArrowDamage(profile, "Arrow", equipped.qualityRoll)
	-- The draw cannot have lasted longer than the server saw since the last attack.
	local draw = DamageRules.ObservedDraw(drawSeconds, previous, lastAttack[player])
	-- Launched from the head itself, so an arrow can never start beyond a wall.
	ProjectileService.Fire(head.Position, aim * DamageRules.ArrowSpeed(draw), character, function(result)
		local model = result.Instance:FindFirstAncestorOfClass("Model")
		local target = model and Players:GetPlayerFromCharacter(model)
		if target then
			CombatService.ApplyHit(player, target, damage)
		else
			NpcService.HitPart(result.Instance, damage, player)
		end
	end)
end

function CombatService.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	Remotes.Listen("Attack", melee)
	Remotes.Listen("Shoot", shoot)
	-- Event creatures hurt players through the same safety rules as PvP.
	NpcService.DamagePlayer = CombatService.ApplyEnvironmentHit
	WorldAdmissionService.RunStarted:Connect(function(player)
		runStartedAt[player] = os.clock()
	end)
	Players.PlayerRemoving:Connect(function(player)
		lastAttack[player] = nil
		lastSequence[player] = nil
		runStartedAt[player] = nil
	end)
end

return CombatService
