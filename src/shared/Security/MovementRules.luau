-- Server movement sanity (GDD §24, §21.4). Horizontal travel between two server
-- samples may not exceed the speed the server currently allows the player (walk,
-- sprint or a downed crawl, as set on their Humanoid) with a generous
-- allowance for latency. The latency allowance is a budget: overruns spend it
-- and slower samples refill it, so it cannot be claimed every sample for a
-- sustained speed-up. A move far beyond the limit is a teleport and is pulled
-- back at once; smaller overruns get STRIKES chances first. Over a longer window
-- (WINDOW_SECONDS) the distance must also stay near the allowed pace, so a small
-- steady speed-up inside the per-sample tolerance is caught too.
--
-- Vertically (JudgeAir): nobody swims or climbs, so a player off the ground may
-- rise no higher than a jump above where they last stood, and may not stay up
-- for long without falling (fly and hover hacks). Falls are free.

local Geometry = require(script.Parent.Parent.Core.Geometry)
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
-- (it already includes sprint, hunger and water modifiers), or the crawl
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

-- True when a client-owned `live` position is horizontally within `slack` studs of
-- the last server-validated one (nil: untracked, so nothing to compare). A client
-- that teleports, acts and teleports back between two samples fails this.
function MovementRules.NearValidated(live: Vector3, validated: Vector3?, slack: number): boolean
	return validated == nil or Geometry.FlatDistance(validated, live) <= slack
end

-- Studs a client-owned point may be from the last validated position: what the
-- allowed speed covers in `elapsed` seconds since that position was taken, plus
-- a little latency, capped at `cap`. The longer since the last good sample, the
-- more slack (an overrun sample leaves the validated position behind).
MovementRules.SLACK_PAD = 2
function MovementRules.Slack(allowedSpeed: number, elapsed: number, cap: number): number
	return math.min(cap, allowedSpeed * elapsed * MovementRules.TOLERANCE + MovementRules.SLACK_PAD)
end

-- Sustained pace: the flat distance over the last WINDOW_SECONDS may exceed what
-- the allowed speed covered by WINDOW_TOLERANCE plus WINDOW_PAD studs (latency
-- when sprint starts or stops, and a lag spike's backlog arriving at once:
-- about a second and a half of walking). A steady speed-up of about 18% or more
-- is over. `window` is a list of {dt, distance, allowed} samples, oldest first.
MovementRules.WINDOW_SECONDS = 8
MovementRules.WINDOW_TOLERANCE = 1.08
MovementRules.WINDOW_PAD = 12
function MovementRules.PushWindow(window, dt: number, distance: number, allowed: number)
	table.insert(window, { dt = dt, distance = distance, allowed = allowed })
	local total = 0
	for index = #window, 1, -1 do
		total += window[index].dt
		if total > MovementRules.WINDOW_SECONDS then
			for _ = 1, index - 1 do
				table.remove(window, 1)
			end
			break
		end
	end
end

function MovementRules.WindowOver(window): boolean
	local seconds, travelled, budget = 0, 0, 0
	for _, entry in window do
		seconds += entry.dt
		travelled += entry.distance
		budget += entry.allowed * entry.dt
	end
	-- Only a (nearly) full window judges: a short one is the per-sample check's job.
	if seconds < MovementRules.WINDOW_SECONDS * 0.9 then
		return false
	end
	return travelled > budget * MovementRules.WINDOW_TOLERANCE + MovementRules.WINDOW_PAD
end

-- Air time. `air` is {groundY, since?, startY?}: the height the player last stood
-- at, and when and at what height they left the ground. Off the ground they may
-- rise at most `jumpHeight` + RISE_MARGIN above groundY, and after HOVER_SECONDS
-- they must have dropped HOVER_DROP studs below where they left it.
-- Returns "Ok" | "Fly" (and updates `air`).
MovementRules.RISE_MARGIN = 3
MovementRules.HOVER_SECONDS = 1.5
MovementRules.HOVER_DROP = 4
function MovementRules.JudgeAir(air, supported: boolean, y: number, jumpHeight: number, now: number): string
	if supported then
		air.groundY, air.since, air.startY = y, nil, nil
		return "Ok"
	end
	if air.since == nil then
		air.since, air.startY = now, y
	end
	if y - air.groundY > math.max(jumpHeight, 0) + MovementRules.RISE_MARGIN then
		return "Fly"
	end
	if now - air.since >= MovementRules.HOVER_SECONDS and air.startY - y < MovementRules.HOVER_DROP then
		return "Fly"
	end
	return "Ok"
end

-- True for a move so far over the limit that it can only be a teleport ("blink").
function MovementRules.Blink(from: Vector3, to: Vector3, dt: number, maxSpeed: number): boolean
	return Geometry.FlatDistance(from, to) > MovementRules.Limit(dt, maxSpeed) * MovementRules.BLINK_FACTOR
end

-- Judges one sample against the latency budget `slack` (start at ALLOWANCE).
-- Returns "Ok" | "Over" | "Blink" and the budget to carry into the next sample.
function MovementRules.Judge(slack: number, from: Vector3, to: Vector3, dt: number, maxSpeed: number): (string, number)
	if MovementRules.Blink(from, to, dt, maxSpeed) then
		return "Blink", slack
	end
	local remaining = math.min(
		MovementRules.ALLOWANCE,
		slack + maxSpeed * dt * MovementRules.TOLERANCE - Geometry.FlatDistance(from, to)
	)
	if remaining < 0 then
		return "Over", slack
	end
	return "Ok", remaining
end

return MovementRules
