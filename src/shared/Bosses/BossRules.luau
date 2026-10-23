-- Pure boss lifecycle rules (GDD §8, Q46, §12.2 invariant 8). The Guardian
-- returns 15–20 minutes after its previous encounter ends, announced 3 minutes
-- ahead. Its Legendary is released once per encounter at 25% HP. Each boss source
-- resets by its own rule.

local BossRules = {}

BossRules.GUARDIAN_MIN_SECONDS = 15 * 60
BossRules.GUARDIAN_MAX_SECONDS = 20 * 60
BossRules.HORN_SECONDS = 3 * 60
BossRules.LEGENDARY_FRACTION = 0.25

-- Idle limits per source before a reset (placeholders).
BossRules.IDLE = { Guardian = 120, Ritual = 60, Structure = 30, Event = math.huge }

-- When the next Guardian appears and when its Horn of War sounds.
function BossRules.GuardianSchedule(endedAt: number, rng)
	local spawnAt = endedAt + rng:NextInteger(BossRules.GUARDIAN_MIN_SECONDS, BossRules.GUARDIAN_MAX_SECONDS)
	return { hornAt = spawnAt - BossRules.HORN_SECONDS, spawnAt = spawnAt }
end

-- True on the hit that first takes the boss to 25% HP or below.
function BossRules.CrossesLegendary(before: number, after: number, maxHealth: number): boolean
	local threshold = maxHealth * BossRules.LEGENDARY_FRACTION
	return before > threshold and after <= threshold
end

-- Releases the Legendary once per encounter ID, however often 25% is crossed.
function BossRules.ReleaseLegendary(released, encounterId: string): boolean
	if released[encounterId] then
		return false
	end
	released[encounterId] = true
	return true
end

-- What happens to an idle or orphaned boss, by source (Q46):
-- "Despawn", "Heal" or nil (keep fighting).
function BossRules.ResetAction(source: string, state): string?
	if source == "Event" then
		return if state.eventExpired then "Despawn" else nil
	end
	if source == "Structure" then
		if state.structureGone then
			return "Despawn"
		end
		return if state.idleSeconds >= BossRules.IDLE.Structure then "Heal" else nil
	end
	-- The Guardian and ritual bosses leave once nobody contests them.
	return if state.idleSeconds >= (BossRules.IDLE[source] or math.huge) then "Despawn" else nil
end

return BossRules
