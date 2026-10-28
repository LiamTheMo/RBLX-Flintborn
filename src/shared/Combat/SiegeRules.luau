-- Siege items (GDD §6.3, §51; docs/ITEM_CATALOG.md §5). Optional raid
-- accelerators, never a requirement: ordinary weapons and tools still break every
-- tier. The Fire Bomb is thrown on a slow, visible arc and bursts in a small
-- radius; fire burns Wood ×3, Stone ×1 and every metal ×0.25 of the base burst.
-- The burst also scorches players (under the same PvP, tribe and safe-zone rules
-- as any hit, never the thrower) and creatures for a modest amount. A Breaching
-- Charge is set on an enemy wall or door the player is looking at and near, burns
-- an 8 s fuse and then deals one heavy flat blow to that piece only: enough to
-- break any Wood or Stone wall or door, and a large share of a metal one. Neither
-- works inside a safe zone; a charge also cannot be set in a no-build aura
-- (portals, the Guardian arena). Totems never protect against raids. All numbers
-- are starting placeholders.

local BuildRules = require(script.Parent.Parent.Building.BuildRules)
local DamageRules = require(script.Parent.DamageRules)
local ItemCatalog = require(script.Parent.Parent.Items.ItemCatalog)
local Tiers = require(script.Parent.Parent.Items.Tiers)

local SiegeRules = {}

SiegeRules.FIRE_BOMB = "FireBomb"
SiegeRules.BREACHING_CHARGE = "BreachingCharge"

-- Fire Bomb: at most one throw per second, launched from the head.
SiegeRules.THROW_COOLDOWN = 1
SiegeRules.THROW_SPEED = 70
-- Upward bias added to the aim so a level throw still arcs.
SiegeRules.THROW_LOFT = 0.2
-- Heavier than an arrow (ARROW_GRAVITY_SCALE 0.35): a short, readable lob.
SiegeRules.THROW_GRAVITY_SCALE = 0.6
SiegeRules.THROW_LIFETIME = 4
-- A burst farther than this from the thrower's validated position does nothing.
SiegeRules.THROW_MAX_RANGE = 60
SiegeRules.BURST_RADIUS = 6
SiegeRules.BURST_DAMAGE = 60
SiegeRules.FIRE_MULTIPLIERS = { Wood = 3, Stone = 1 }
SiegeRules.METAL_FIRE_MULTIPLIER = 0.25
-- Modest damage to players and creatures caught in the burst.
SiegeRules.BURST_PLAYER_DAMAGE = 20
SiegeRules.BURST_CREATURE_DAMAGE = 20

-- Breaching Charge: set within CHARGE_REACH of the head, at most once a second.
SiegeRules.CHARGE_REACH = 8
SiegeRules.CHARGE_COOLDOWN = 1
SiegeRules.FUSE_SECONDS = 8
-- Breaks every Wood/Stone wall (300/800 HP) and door; takes 72% of an Iron wall
-- (1,250 HP) and 30% of an Adamantine one (3,050 HP).
SiegeRules.BREACH_DAMAGE = 900
SiegeRules.BREACHABLE = { Wall = true, Door = true }

-- How far (horizontally) the head may be from the last validated position.
SiegeRules.VALIDATED_SLACK = 12

-- Player-facing text for every refusal reason.
SiegeRules.MESSAGES = {
	NotInRun = "You can't use that right now.",
	BadRequest = "Can't use that.",
	NotHeld = "Equip the item on your hotbar first.",
	NoItem = "You have none left.",
	TooSoon = "Wait a moment.",
	SafeZone = "Nothing can be raided inside a safe zone.",
	NoRaidZone = "Charges can't be set here.",
	NoTarget = "Aim at an enemy wall or door within reach.",
	NotBreachable = "Charges only go on walls and doors.",
	OwnStructure = "That's your own structure.",
	TooFar = "Get closer.",
	ChargeSet = ("Breaching Charge set: %d s fuse."):format(SiegeRules.FUSE_SECONDS),
	BombReady = "Fire Bomb ready: attack to throw it.",
	ChargeReady = "Aim at an enemy wall or door within reach, then attack to set the charge.",
}

-- "Thrown" or "Placed" for a siege item, otherwise nil.
function SiegeRules.Kind(catalogId: any): string?
	local item = ItemCatalog.Get(catalogId)
	return item and item.siege and item.siege.kind or nil
end

function SiegeRules.Message(reason: string?): string
	return reason and SiegeRules.MESSAGES[reason] or ("Can't do that (" .. tostring(reason) .. ").")
end

function SiegeRules.IsMetal(material: string?): boolean
	return material ~= nil and table.find(Tiers.Metals, material) ~= nil
end

-- Fire multiplier for a structure material (unknown materials burn as Stone).
function SiegeRules.FireMultiplier(material: string?): number
	if SiegeRules.IsMetal(material) then
		return SiegeRules.METAL_FIRE_MULTIPLIER
	end
	return material and SiegeRules.FIRE_MULTIPLIERS[material] or 1
end

-- Burst damage one Fire Bomb deals to a structure of `material`.
function SiegeRules.FireDamage(material: string?): number
	return SiegeRules.BURST_DAMAGE * SiegeRules.FireMultiplier(material)
end

-- Raw damage to hand BuildingService.Hit so a structure loses exactly `desired`:
-- Hit applies the held tool's match bonus (BuildRules.StructureDamage), which a
-- bomb or charge must not get.
function SiegeRules.RawFor(desired: number, toolKind: string?, material: string): number
	return desired / BuildRules.StructureDamage(1, toolKind, material)
end

-- Launch velocity for a throw along `aim` (a unit vector).
function SiegeRules.ThrowVelocity(aim: Vector3): Vector3
	local lofted = aim + Vector3.new(0, SiegeRules.THROW_LOFT, 0)
	return lofted / lofted.Magnitude * SiegeRules.THROW_SPEED
end

function SiegeRules.ThrowReady(lastAt: number?, now: number): boolean
	return DamageRules.CooldownReady(lastAt, now, SiegeRules.THROW_COOLDOWN)
end

function SiegeRules.ChargeReady(lastAt: number?, now: number): boolean
	return DamageRules.CooldownReady(lastAt, now, SiegeRules.CHARGE_COOLDOWN)
end

-- True when a burst at `impact` lies within range of the thrower's validated
-- position (nil when untracked: the projectile's own lifetime bounds it).
function SiegeRules.WithinRange(validated: Vector3?, impact: Vector3): boolean
	return validated == nil or (impact - validated).Magnitude <= SiegeRules.THROW_MAX_RANGE
end

-- True when a structure box (centre, half-size) is caught by a burst at `center`.
function SiegeRules.InBurst(center: Vector3, position: Vector3, half: Vector3): boolean
	local below = math.max(math.abs(center.Y - position.Y) - half.Y, 0)
	local beside = BuildRules.HorizontalDistance(center, position, half)
	return math.sqrt(beside * beside + below * below) <= SiegeRules.BURST_RADIUS
end

-- Why a charge cannot be set, or nil when it can. `target` describes what the
-- placer is looking at: {pieceId, ownedByPlacer, distance (head to the hit point),
-- validatedDistance (validated root to the hit point, nil when untracked),
-- inSafeZone (placer or piece), inNoBuildAura}; nil when the aim hit no structure.
function SiegeRules.ChargeRefusal(target): string?
	if target == nil then
		return "NoTarget"
	end
	if not SiegeRules.BREACHABLE[target.pieceId] then
		return "NotBreachable"
	end
	if target.ownedByPlacer then
		return "OwnStructure"
	end
	if target.distance > SiegeRules.CHARGE_REACH then
		return "TooFar"
	end
	if
		target.validatedDistance ~= nil
		and target.validatedDistance > SiegeRules.CHARGE_REACH + SiegeRules.VALIDATED_SLACK
	then
		return "TooFar"
	end
	if target.inSafeZone then
		return "SafeZone"
	end
	if target.inNoBuildAura then
		return "NoRaidZone"
	end
	return nil
end

-- Damage a detonating charge deals to its piece: flat, whatever the tier.
function SiegeRules.BreachDamage(): number
	return SiegeRules.BREACH_DAMAGE
end

-- Whole seconds left on a fuse, for the countdown above the charge.
function SiegeRules.FuseLabel(remaining: number): string
	return tostring(math.max(0, math.ceil(remaining)))
end

return SiegeRules
