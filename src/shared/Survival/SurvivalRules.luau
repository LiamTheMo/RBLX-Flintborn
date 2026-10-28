-- Survival meters as pure step functions (GDD §4.3–4.5, §5.4, Q61–65, Q135, Q160).
-- Health, stamina and food only. Stamina and food are fractions in [0, 1]; health is
-- in HP. The server owns the state; clients only send movement intent and use
-- requests.

local GameConstants = require(script.Parent.Parent.GameConstants)

local SurvivalRules = {}

-- Starting movement speeds in studs/s (GDD leaves exact speeds Open).
SurvivalRules.WALK_SPEED = 16
SurvivalRules.SPRINT_SPEED = 24
SurvivalRules.CROUCH_SPEED = 8
-- Walking (or sprinting, or crouching) through knee-deep water is 30% slower
-- (GDD §55); the Tidewalker perk's bonus applies on top.
SurvivalRules.WATER_SPEED_MULTIPLIER = 0.7

-- Meter values this close to an end are snapped to it, so float drift from many
-- small ticks never leaves "almost empty" stamina that still allows a sprint.
local EPSILON = 1e-6

local function settle(value: number): number
	if value < EPSILON then
		return 0
	elseif value > 1 - EPSILON then
		return 1
	end
	return value
end

export type FoodHeal = { remaining: number, endsAt: number }
export type State = {
	stamina: number,
	food: number,
	sprintIntent: boolean,
	crouching: boolean,
	-- Set when a sprint empties the bar: no sprint until it is released or full.
	exhausted: boolean?,
	-- Seconds left before stamina may recover (reset by every sprinting step).
	regenDelay: number?,
	medicineLockUntil: number,
	foodHeals: { FoodHeal },
}

function SurvivalRules.NewState(): State
	return {
		stamina = 1,
		food = 1,
		sprintIntent = false,
		crouching = false,
		medicineLockUntil = 0,
		foodHeals = {},
	}
end

-- Sprinting only happens while the player wants to, is moving, is not crouching
-- and has stamina left. Only sprinting spends stamina (Q62). A sprint that empties
-- the bar stays stopped until sprint is released or the bar is full again, so a
-- held sprint does not restart on every sliver of recovered stamina.
function SurvivalRules.IsSprinting(state: State, moving: boolean): boolean
	return state.sprintIntent and moving and not state.crouching and state.stamina > 0 and not state.exhausted
end

-- Travel the server observes is judged over a whole window, so the uneven way
-- character positions arrive over the network averages out.
SurvivalRules.PACE_WINDOW_SECONDS = 1
-- Pace above this multiple of walking counts as sprinting: halfway from walking
-- (16) to sprinting (24), well clear of a walker's network jitter.
SurvivalRules.SPRINT_PACE = 1.25

export type Pace = { samples: { { distance: number, elapsed: number } }, allowed: number?, walkPace: number? }

function SurvivalRules.NewPace(): Pace
	return { samples = {}, allowed = nil, walkPace = nil }
end

-- The multiplier water puts on every movement speed (1 on dry ground).
function SurvivalRules.WaterFactor(inWater: boolean?, waterBonus: number?): number
	if not inWater then
		return 1
	end
	return SurvivalRules.WATER_SPEED_MULTIPLIER * (1 + (waterBonus or 0))
end

-- Plain walking pace right now, the yardstick for spotting unrequested sprints.
function SurvivalRules.WalkPace(inWater: boolean?, waterBonus: number?): number
	return SurvivalRules.WALK_SPEED * SurvivalRules.WaterFactor(inWater, waterBonus)
end

-- Feeds one server sample of horizontal travel (`distance` studs over `elapsed`
-- seconds) while the server allows `allowed` studs/s. A change of allowance (a
-- sprint released, a crouch) or of walking pace (stepping into or out of water)
-- restarts the window, so travel from just before it never counts. Returns true when a full window was clearly faster than walking
-- at `walkPace` (default WALK_SPEED): the player is sprinting whatever their
-- client claims (GDD §24).
function SurvivalRules.ObservePace(
	pace: Pace,
	distance: number,
	elapsed: number,
	allowed: number,
	walkPace: number?
): boolean
	if pace.allowed ~= allowed or pace.walkPace ~= walkPace then
		pace.allowed = allowed
		pace.walkPace = walkPace
		table.clear(pace.samples)
	end
	if elapsed <= 0 then
		return false
	end
	table.insert(pace.samples, { distance = distance, elapsed = elapsed })
	local window = SurvivalRules.PACE_WINDOW_SECONDS
	local total, travelled = 0, 0
	for _, sample in pace.samples do
		total += sample.elapsed
		travelled += sample.distance
	end
	while #pace.samples > 1 and total - pace.samples[1].elapsed >= window do
		local oldest = table.remove(pace.samples, 1)
		total -= oldest.elapsed
		travelled -= oldest.distance
	end
	if total < window then
		return false
	end
	return travelled / total > (walkPace or SurvivalRules.WALK_SPEED) * SurvivalRules.SPRINT_PACE
end

-- A full bar lasts 3 s of sprint; empty to full takes 5 s (Q62). Recovery waits
-- until 3 s after the last sprinting step (GDD §47). `observedSprint` drains it
-- for travel at sprint pace even without a sprint request.
function SurvivalRules.StepStamina(state: State, dt: number, moving: boolean, observedSprint: boolean?)
	if state.exhausted and (not state.sprintIntent or state.stamina >= 1) then
		state.exhausted = false
	end
	if SurvivalRules.IsSprinting(state, moving) or (observedSprint and state.stamina > 0) then
		-- PvP mastery's non-combat perk stretches the sprint (staminaDrainScale < 1).
		local drain = dt * (state.staminaDrainScale or 1) / GameConstants.SPRINT_SECONDS
		state.stamina = settle(math.max(0, state.stamina - drain))
		if state.stamina <= 0 then
			state.exhausted = true
		end
		state.regenDelay = GameConstants.STAMINA_REGEN_DELAY_SECONDS
	elseif (state.regenDelay or 0) > 0 then
		-- Any of this step left after the pause ends already recovers.
		local recover = math.max(0, dt - state.regenDelay)
		state.regenDelay = math.max(0, state.regenDelay - dt)
		state.stamina = settle(math.min(1, state.stamina + recover / GameConstants.STAMINA_RECOVERY_SECONDS))
	else
		state.stamina = settle(math.min(1, state.stamina + dt / GameConstants.STAMINA_RECOVERY_SECONDS))
	end
end

-- Full to empty in 60 minutes (Q63, changed in GDD §49). 0% adds nothing beyond the slow (Q160c).
function SurvivalRules.StepFood(state: State, dt: number)
	state.food = settle(math.max(0, state.food - dt / GameConstants.FOOD_DRAIN_SECONDS))
end

-- The server-set walk speed: walk, sprint or crouch, times the hunger slow and the
-- water slow (with the Tidewalker `waterBonus`).
function SurvivalRules.MoveSpeed(state: State, moving: boolean, inWater: boolean?, waterBonus: number?): number
	local speed = SurvivalRules.WALK_SPEED
	if state.crouching then
		speed = SurvivalRules.CROUCH_SPEED
	elseif SurvivalRules.IsSprinting(state, moving) then
		speed = SurvivalRules.SPRINT_SPEED
	end
	if GameConstants.IsFoodSlowed(state.food) then
		speed *= GameConstants.FOOD_SLOW_MULTIPLIER
	end
	return speed * SurvivalRules.WaterFactor(inWater, waterBonus)
end

function SurvivalRules.CanUseMedicine(state: State, now: number): boolean
	return now >= state.medicineLockUntil
end

-- Immediate heal capped at max HP, then the animation locks further medicine (Q64,
-- Q135). Returns the new health, or nil while locked (nothing is consumed).
function SurvivalRules.UseMedicine(state: State, item, health: number, maxHealth: number, now: number): number?
	if not SurvivalRules.CanUseMedicine(state, now) then
		return nil
	end
	state.medicineLockUntil = now + item.animationSeconds
	return math.min(maxHealth, health + item.heal)
end

-- Eating restores hunger at once and starts a 10 s heal. Heals stack (Q160d).
function SurvivalRules.Eat(state: State, item, now: number)
	state.food = math.min(1, state.food + (item.hunger or 0))
	if item.heal and item.heal > 0 then
		table.insert(state.foodHeals, {
			remaining = item.heal,
			endsAt = now + GameConstants.FOOD_HEAL_SECONDS,
		})
	end
end

-- Applies pending food healing for this tick. Each heal spreads what remains over
-- the time it has left, so a halved heal still ends on schedule. Returns HP healed.
function SurvivalRules.StepFoodHeals(state: State, now: number, dt: number): number
	local healed = 0
	for index = #state.foodHeals, 1, -1 do
		local heal = state.foodHeals[index]
		local timeLeft = heal.endsAt - now
		local amount = if timeLeft <= dt then heal.remaining else heal.remaining * (dt / timeLeft)
		heal.remaining -= amount
		healed += amount
		if heal.remaining <= 1e-9 or timeLeft <= dt then
			table.remove(state.foodHeals, index)
		end
	end
	return healed
end

-- A damaging hit halves every pending food heal and cancels any left at ≤10 HP (Q65).
-- Already-applied healing is never taken back.
function SurvivalRules.OnDamaged(state: State)
	for index = #state.foodHeals, 1, -1 do
		local heal = state.foodHeals[index]
		heal.remaining = GameConstants.FoodHealAfterHit(heal.remaining)
		if heal.remaining <= 0 then
			table.remove(state.foodHeals, index)
		end
	end
end

-- Downed players cannot heal (Q159f): pending food healing is cleared.
function SurvivalRules.OnDowned(state: State)
	table.clear(state.foodHeals)
end

function SurvivalRules.PendingFoodHealing(state: State): number
	local total = 0
	for _, heal in state.foodHeals do
		total += heal.remaining
	end
	return total
end

return SurvivalRules
