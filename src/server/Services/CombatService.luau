-- Server-authoritative combat (GDD §5.1, §5.5, §21.1, §21.5). Clients send attack
-- intent (aim direction, draw time) with increasing sequence numbers; the server
-- picks targets from its own positions, enforces cadence, reach, arc, risk state,
-- friendly fire and safe zones, and applies damage through armor EHP. World only.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local ArmorRules = require(ReplicatedStorage.Shared.Combat.ArmorRules)
local DamageRules = require(ReplicatedStorage.Shared.Combat.DamageRules)
local GameConstants = require(ReplicatedStorage.Shared.GameConstants)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Signal = require(ReplicatedStorage.Shared.Core.Signal)
local WeaponCatalog = require(ReplicatedStorage.Shared.Combat.WeaponCatalog)
local InventoryService = require(script.Parent.InventoryService)
local ProjectileService = require(script.Parent.ProjectileService)
local SafeZoneService = require(script.Parent.SafeZoneService)
local WorldAdmissionService = require(script.Parent.WorldAdmissionService)

local CombatService = {}

-- Fires (attacker, targetPlayer, rawDamage, newHealth) after damage is applied.
CombatService.Damaged = Signal.new()

local lastAttack = {}
local lastSequence = {}

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

-- Applies raw damage from `attacker` to `target` if the rules allow it.
-- Returns true when damage was applied.
function CombatService.ApplyHit(attacker: Player, target: Player, rawDamage: number): boolean
	if attacker == target then
		return false
	end
	local humanoid = aliveHumanoid(target)
	if humanoid == nil or not DamageRules.CanDamage(actor(attacker), actor(target)) then
		return false
	end
	local factor = ArmorRules.Factor(InventoryService.ArmorPieces(target))
	local newHealth = GameConstants.ApplyDamage(humanoid.Health, factor, rawDamage)
	humanoid.Health = newHealth
	Remotes.Get("CombatFeedback"):FireClient(attacker, "Hit", math.round(rawDamage))
	Remotes.Get("CombatFeedback"):FireClient(target, "Hurt", math.round(rawDamage))
	CombatService.Damaged:Fire(attacker, target, rawDamage, newHealth)
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

local function melee(player: Player, sequence: any, direction: any)
	local aim = validDirection(direction)
	local root = rootOf(player)
	if not acceptSequence(player, sequence) or aim == nil or root == nil or aliveHumanoid(player) == nil then
		return
	end
	if not WorldAdmissionService.IsAtRisk(player) then
		return
	end
	local equipped = InventoryService.Equipped(player)
	local profile = WeaponCatalog.For(equipped and equipped.catalogId)
	if profile.kind ~= "Melee" or not readyToAttack(player, profile.cooldown) then
		return
	end
	local flatAim = Vector3.new(aim.X, 0, aim.Z)
	local best, bestDistance = nil, math.huge
	for _, other in Players:GetPlayers() do
		local otherRoot = other ~= player and rootOf(other)
		if otherRoot then
			local offset = otherRoot.Position - root.Position
			local distance = offset.Magnitude
			if
				distance < bestDistance
				and DamageRules.WithinReach(distance, profile.reach)
				and DamageRules.WithinArc(flatAim, Vector3.new(offset.X, 0, offset.Z), profile.arc)
			then
				best, bestDistance = other, distance
			end
		end
	end
	if best then
		CombatService.ApplyHit(player, best, DamageRules.MeleeDamage(profile, equipped and equipped.qualityRoll))
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
	local equipped = InventoryService.Equipped(player)
	local profile = WeaponCatalog.For(equipped and equipped.catalogId)
	if profile.kind ~= "Bow" or not readyToAttack(player, profile.cooldown) then
		return
	end
	-- Each shot consumes one crafted arrow (GDD Q28).
	if not InventoryService.RemoveAll(player, { Arrow = 1 }) then
		InventoryService.Notify(player, "You have no arrows.")
		return
	end
	local damage = DamageRules.ArrowDamage(profile, "Arrow", equipped.qualityRoll)
	local origin = head.Position + aim * 2
	ProjectileService.Fire(origin, aim * DamageRules.ArrowSpeed(drawSeconds), character, function(result)
		local model = result.Instance:FindFirstAncestorOfClass("Model")
		local target = model and Players:GetPlayerFromCharacter(model)
		if target then
			CombatService.ApplyHit(player, target, damage)
		end
	end)
end

function CombatService.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	Remotes.Get("Attack").OnServerEvent:Connect(melee)
	Remotes.Get("Shoot").OnServerEvent:Connect(shoot)
	Players.PlayerRemoving:Connect(function(player)
		lastAttack[player] = nil
		lastSequence[player] = nil
	end)
end

return CombatService
