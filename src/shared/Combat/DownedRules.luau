-- Downed and revive (GDD §5.3, §21.2, Q68, Q136, Q159). A tribe member at 0 HP goes
-- down with a separate 20-HP pool that armor still protects, and a 60 s bleed-out
-- that only runs while nobody is reviving. Anyone may revive; only one reviver at a
-- time; 10 continuous seconds; damage to the reviver does not stop it. A cancelled
-- revive resumes the timer from where it paused and restarts revive progress.

local GameConstants = require(script.Parent.Parent.GameConstants)

local DownedRules = {}

DownedRules.REVIVE_RANGE = 8
DownedRules.CRAWL_SPEED = 2

export type State = {
	downedHealth: number,
	remaining: number,
	reviverId: number?,
	reviveProgress: number,
}

function DownedRules.New(): State
	return {
		downedHealth = GameConstants.DOWNED_HEALTH,
		remaining = GameConstants.BLEED_OUT_SECONDS,
		reviverId = nil,
		reviveProgress = 0,
	}
end

-- Starts a revive. Refused while someone else is already reviving.
function DownedRules.StartRevive(state: State, reviverId: number): boolean
	if state.reviverId ~= nil and state.reviverId ~= reviverId then
		return false
	end
	state.reviverId = reviverId
	return true
end

-- Stops a revive (cancel, out of range, reviver down). Progress restarts next time.
function DownedRules.StopRevive(state: State, reviverId: number?)
	if reviverId == nil or state.reviverId == reviverId then
		state.reviverId = nil
		state.reviveProgress = 0
	end
end

-- Advances time. Returns "Revived", "BledOut" or nil.
function DownedRules.Step(state: State, dt: number): string?
	if state.reviverId ~= nil then
		state.reviveProgress += dt
		if state.reviveProgress >= GameConstants.REVIVE_SECONDS - 1e-9 then
			return "Revived"
		end
		return nil
	end
	state.remaining = math.max(0, state.remaining - dt)
	if state.remaining <= 1e-9 then
		return "BledOut"
	end
	return nil
end

-- Armor-scaled damage to the downed pool. Returns true when it kills.
function DownedRules.Damage(state: State, armorFactor: number, rawDamage: number): boolean
	state.downedHealth = GameConstants.ApplyDamage(state.downedHealth, armorFactor, rawDamage)
	return state.downedHealth <= 0
end

-- Health after a successful revive: 10% of max EHP back as actual HP (Q136).
function DownedRules.RevivedHealth(maxHealth: number, armorFactor: number): number
	return GameConstants.RevivedHealth(maxHealth, armorFactor)
end

return DownedRules
