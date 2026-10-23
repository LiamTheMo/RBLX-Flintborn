-- Pure combat checks shared by the server and specs (GDD §5.1, §5.5, §21.1, §31.2,
-- Q160b). The server resolves every hit with these; clients never declare hits.

local SessionStates = require(script.Parent.Parent.Admission.SessionStates)
local WeaponCatalog = require(script.Parent.WeaponCatalog)

local DamageRules = {}

-- Small timing slack for network jitter on attack cadence.
DamageRules.COOLDOWN_TOLERANCE = 0.05
-- Extra reach allowed for latency between client and server positions.
DamageRules.REACH_ALLOWANCE = 2

function DamageRules.CooldownReady(lastAt: number?, now: number, cooldown: number): boolean
	return lastAt == nil or now - lastAt >= cooldown - DamageRules.COOLDOWN_TOLERANCE
end

-- Only at-risk players can be hurt; tribe members never hurt each other; nobody
-- deals or takes damage inside a safe zone.
function DamageRules.CanDamage(attacker, target): boolean
	if not SessionStates.IsAtRisk(attacker.state) or not SessionStates.IsAtRisk(target.state) then
		return false
	end
	if attacker.tribeId ~= nil and attacker.tribeId == target.tribeId then
		return false
	end
	if attacker.inSafeZone or target.inSafeZone then
		return false
	end
	return true
end

function DamageRules.WithinReach(distance: number, reach: number): boolean
	return distance <= reach + DamageRules.REACH_ALLOWANCE
end

-- True when `toTarget` lies within `arcDegrees` (full cone) of `facing`.
function DamageRules.WithinArc(facing, toTarget, arcDegrees: number): boolean
	local length = toTarget.Magnitude
	if length < 1e-6 then
		return true
	end
	local cosine = facing:Dot(toTarget / length) / math.max(facing.Magnitude, 1e-6)
	return cosine >= math.cos(math.rad(arcDegrees / 2))
end

-- Raw damage scaled by the item's quality roll.
function DamageRules.MeleeDamage(profile, qualityRoll: number?): number
	return profile.damage * (1 + (qualityRoll or 0))
end

-- Bow + arrow damage, independent of draw time (Q134).
function DamageRules.ArrowDamage(bowProfile, arrowId: string, qualityRoll: number?): number
	local arrow = WeaponCatalog.Arrows[arrowId]
	return (bowProfile.bowDamage + (arrow and arrow.damage or 0)) * (1 + (qualityRoll or 0))
end

-- Longer draws launch faster (farther), capped at a full draw.
function DamageRules.ArrowSpeed(drawSeconds: number): number
	local t = math.clamp(drawSeconds / WeaponCatalog.FULL_DRAW_SECONDS, 0, 1)
	return WeaponCatalog.MIN_ARROW_SPEED + (WeaponCatalog.MAX_ARROW_SPEED - WeaponCatalog.MIN_ARROW_SPEED) * t
end

-- The draw time to honour: the client's claim, capped at how long the server saw
-- since the previous attack (`previousAt`, nil before the first) at `now`.
function DamageRules.ObservedDraw(claimed: number, previousAt: number?, now: number): number
	local observed = if previousAt then now - previousAt else WeaponCatalog.FULL_DRAW_SECONDS
	return math.clamp(math.min(claimed, observed), 0, WeaponCatalog.FULL_DRAW_SECONDS)
end

-- When the current draw could have begun at the earliest: the later of the last
-- attack and the start of this run (an attack from an earlier run never counts).
function DamageRules.DrawStart(lastAttackAt: number?, runStartedAt: number?): number?
	if lastAttackAt == nil or (runStartedAt ~= nil and runStartedAt > lastAttackAt) then
		return runStartedAt
	end
	return lastAttackAt
end

return DamageRules
