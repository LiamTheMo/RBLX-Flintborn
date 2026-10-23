-- Server movement sanity (GDD §24, §21.4). Horizontal travel between two server
-- samples may not exceed the fastest legal speed (sprint, or a downed crawl) with
-- a generous allowance for latency; vertical motion (falls, jumps) is ignored.

local SurvivalRules = require(script.Parent.Parent.Survival.SurvivalRules)

local MovementRules = {}

MovementRules.TOLERANCE = 1.6
MovementRules.ALLOWANCE = 6
MovementRules.CRAWL_SPEED = 2
-- Consecutive bad samples before the server pulls the player back.
MovementRules.STRIKES = 2

function MovementRules.MaxSpeed(downed: boolean, swimBonus: number?): number
	if downed then
		return MovementRules.CRAWL_SPEED
	end
	return SurvivalRules.SPRINT_SPEED * (1 + (swimBonus or 0))
end

-- True when moving from `from` to `to` in `dt` seconds is physically plausible.
function MovementRules.Plausible(from: Vector3, to: Vector3, dt: number, maxSpeed: number): boolean
	local dx, dz = to.X - from.X, to.Z - from.Z
	local distance = math.sqrt(dx * dx + dz * dz)
	return distance <= maxSpeed * dt * MovementRules.TOLERANCE + MovementRules.ALLOWANCE
end

return MovementRules
