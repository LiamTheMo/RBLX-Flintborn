-- Who an enemy or boss hunts (GDD §7.3, §8, Q44). Enemies notice players inside
-- their aggro range, but a hit from farther away provokes them too: for a while
-- after being damaged they hunt their attacker anywhere within the leash plus bow
-- range of home, so nothing can be killed risk-free from out of reach. Bosses stay
-- leashed to their arena and answer such attackers with ranged attacks.

local AggroRules = {}

-- How long one hit keeps an enemy hunting its attacker.
AggroRules.PROVOKE_SECONDS = 10
-- Effective bow range: attackers this far past the leash still provoke.
AggroRules.BOW_RANGE = 150

local function flatDistance(a: Vector3, b: Vector3): number
	local dx, dz = a.X - b.X, a.Z - b.Z
	return math.sqrt(dx * dx + dz * dz)
end

-- True while a hit at `provokedAt` still makes an enemy homed at `home` hunt an
-- attacker standing at `attackerPosition`.
function AggroRules.Provoked(
	provokedAt: number?,
	now: number,
	home: Vector3,
	attackerPosition: Vector3,
	leash: number
): boolean
	return provokedAt ~= nil
		and now - provokedAt <= AggroRules.PROVOKE_SECONDS
		and flatDistance(attackerPosition, home) <= leash + AggroRules.BOW_RANGE
end

-- `goal` pulled back (horizontally) to within `leash` of `home`.
function AggroRules.ClampToLeash(home: Vector3, goal: Vector3, leash: number): Vector3
	local offset = Vector3.new(goal.X - home.X, 0, goal.Z - home.Z)
	local distance = offset.Magnitude
	if distance <= leash then
		return goal
	end
	return Vector3.new(home.X + offset.X / distance * leash, goal.Y, home.Z + offset.Z / distance * leash)
end

return AggroRules
