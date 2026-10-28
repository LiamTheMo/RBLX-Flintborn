-- Who an enemy or boss hunts (GDD §7.3, §8, Q44, §54). Hostile enemies notice
-- players inside their aggro range, but a hit from farther away provokes them too:
-- for a while after being damaged they hunt their attacker anywhere within the
-- leash plus bow range of home, so nothing can be killed risk-free from out of
-- reach. Bosses stay leashed to their arena and answer such attackers with ranged
-- attacks. Neutral creatures (§54) only hunt players who hurt them or their group,
-- until they calm down; Passive ones never hunt and run from nearby players.

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

-- Neutral groups stay angry at an attacker this long after the group's last hit
-- from them, then calm down.
AggroRules.CALM_SECONDS = 20
-- Passive creatures run from players this close, farther once they have been hurt.
AggroRules.FLEE_RADIUS = 30
AggroRules.PANIC_RADIUS = 60
-- How far one flee step aims.
AggroRules.FLEE_STEP = 20
-- Idle creatures amble around home within this radius, at this share of their speed.
AggroRules.WANDER_RADIUS = 24
AggroRules.WANDER_SPEED = 0.35

-- A herd, pack or event group: who it is angry at (attacker -> time of last hit).
function AggroRules.NewGroup()
	return { angry = {} }
end

-- A hit (or a fight an alpha starts) makes the whole group angry at `attacker`.
function AggroRules.Anger(group, attacker: any, now: number)
	if group and attacker ~= nil then
		group.angry[attacker] = now
	end
end

-- True while `group` is still angry at `player`; forgets calmed-down grudges.
function AggroRules.AngryAt(group, player: any, now: number): boolean
	local at = group and group.angry[player]
	if at == nil then
		return false
	end
	if now - at > AggroRules.CALM_SECONDS then
		group.angry[player] = nil
		return false
	end
	return true
end

-- Whether a creature of `behaviour` may attack `player`: Hostile ones anyone they
-- notice, Neutral ones only while their group is angry at them, Passive never.
function AggroRules.Hunts(behaviour: string?, group, player: any, now: number): boolean
	if behaviour == "Passive" then
		return false
	elseif behaviour == "Neutral" then
		return AggroRules.AngryAt(group, player, now)
	end
	return true
end

-- Where a Passive creature at `position` runs from `threats` (positions), kept
-- within `leash` of home: straight away from them, or sideways when the leash
-- corners it. nil when nothing threatens it.
function AggroRules.FleeGoal(position: Vector3, threats, home: Vector3, leash: number): Vector3?
	local x, z = 0, 0
	for _, threat in threats do
		local dx, dz = position.X - threat.X, position.Z - threat.Z
		local distance = math.max(math.sqrt(dx * dx + dz * dz), 0.5)
		-- Closer threats push harder.
		x += dx / (distance * distance)
		z += dz / (distance * distance)
	end
	local length = math.sqrt(x * x + z * z)
	if #threats == 0 then
		return nil
	elseif length < 1e-6 then
		x, z, length = 1, 0, 1
	end
	x, z = x / length, z / length
	local best, bestGain = nil, -math.huge
	-- Away first, then the two sideways escapes; take the one that gets farthest.
	for _, direction in { { x, z }, { -z, x }, { z, -x } } do
		local goal = AggroRules.ClampToLeash(
			home,
			Vector3.new(
				position.X + direction[1] * AggroRules.FLEE_STEP,
				position.Y,
				position.Z + direction[2] * AggroRules.FLEE_STEP
			),
			leash
		)
		local gain = flatDistance(goal, position)
		if gain >= AggroRules.FLEE_STEP * 0.5 then
			return goal
		elseif gain > bestGain then
			best, bestGain = goal, gain
		end
	end
	return best
end

-- An idle creature's next amble: a spot near home, or a pause where it stands
-- (when it is already near home).
function AggroRules.WanderGoal(home: Vector3, position: Vector3, rng): Vector3
	if flatDistance(position, home) <= AggroRules.WANDER_RADIUS and rng:NextNumber() < 0.4 then
		return position
	end
	local angle = rng:NextNumber(0, math.pi * 2)
	local distance = rng:NextNumber(0, AggroRules.WANDER_RADIUS)
	return Vector3.new(home.X + math.cos(angle) * distance, home.Y, home.Z + math.sin(angle) * distance)
end

return AggroRules
