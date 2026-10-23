-- Server movement sanity (GDD §24, §21.4). Horizontal travel between two server
-- samples may not exceed the speed the server currently allows the player (walk,
-- sprint, crouch or a downed crawl, as set on their Humanoid) with a generous
-- allowance for latency; vertical motion (falls, jumps) is ignored. The latency
-- allowance is a budget: overruns spend it and slower samples refill it, so it
-- cannot be claimed every sample for a sustained speed-up. A move far beyond the
-- limit is a teleport and is pulled back at once; smaller overruns get STRIKES
-- chances first.

local SurvivalRules = require(script.Parent.Parent.Survival.SurvivalRules)

local MovementRules = {}

-- Sustained speed may exceed the allowed speed by this factor. Bursts are covered
-- by the ALLOWANCE budget, so this stays below sprint / walk (1.5): moving at
-- sprint speed on a walk allowance is caught.
MovementRules.TOLERANCE = 1.25
MovementRules.ALLOWANCE = 6
MovementRules.CRAWL_SPEED = 2
-- Consecutive bad samples before the server pulls the player back.
MovementRules.STRIKES = 2
-- A single sample this many times over the limit is pulled back immediately.
MovementRules.BLINK_FACTOR = 3

-- The fastest legal speed with no server-set walk speed to go by.
function MovementRules.MaxSpeed(downed: boolean, swimBonus: number?): number
	if downed then
		return MovementRules.CRAWL_SPEED
	end
	return SurvivalRules.SPRINT_SPEED * (1 + (swimBonus or 0))
end

-- The speed the player is allowed right now: the server-set Humanoid walk speed
-- (it already includes sprint, crouch, hunger and swim modifiers), or the crawl
-- while downed. `previous` (last sample's allowance) covers the latency of a
-- change, e.g. stamina running out mid-sprint.
function MovementRules.AllowedSpeed(downed: boolean, walkSpeed: number?, previous: number?): number
	local current = if downed
		then MovementRules.CRAWL_SPEED
		elseif type(walkSpeed) == "number" and walkSpeed == walkSpeed then math.max(walkSpeed, 0)
		else MovementRules.MaxSpeed(false)
	return math.max(current, previous or 0)
end

-- Furthest horizontal distance allowed in `dt` seconds at `maxSpeed`.
function MovementRules.Limit(dt: number, maxSpeed: number): number
	return maxSpeed * dt * MovementRules.TOLERANCE + MovementRules.ALLOWANCE
end

local function horizontal(from: Vector3, to: Vector3): number
	local dx, dz = to.X - from.X, to.Z - from.Z
	return math.sqrt(dx * dx + dz * dz)
end

-- True when moving from `from` to `to` in `dt` seconds is physically plausible.
function MovementRules.Plausible(from: Vector3, to: Vector3, dt: number, maxSpeed: number): boolean
	return horizontal(from, to) <= MovementRules.Limit(dt, maxSpeed)
end

-- True for a move so far over the limit that it can only be a teleport ("blink").
function MovementRules.Blink(from: Vector3, to: Vector3, dt: number, maxSpeed: number): boolean
	return horizontal(from, to) > MovementRules.Limit(dt, maxSpeed) * MovementRules.BLINK_FACTOR
end

-- Judges one sample against the latency budget `slack` (start at ALLOWANCE).
-- Returns "Ok" | "Over" | "Blink" and the budget to carry into the next sample.
function MovementRules.Judge(slack: number, from: Vector3, to: Vector3, dt: number, maxSpeed: number): (string, number)
	if MovementRules.Blink(from, to, dt, maxSpeed) then
		return "Blink", slack
	end
	local remaining =
		math.min(MovementRules.ALLOWANCE, slack + maxSpeed * dt * MovementRules.TOLERANCE - horizontal(from, to))
	if remaining < 0 then
		return "Over", slack
	end
	return "Ok", remaining
end

return MovementRules
