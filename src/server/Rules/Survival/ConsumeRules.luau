-- Server half of Shared.Survival.ConsumeRules: what only the server uses. Everything in
-- ReplicatedStorage is downloaded to every player, so the shared module keeps
-- only what clients need; this one clones it and adds the rest, and server code
-- requires this module.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Consumables = require(ReplicatedStorage.Shared.Items.Consumables)
local GameConstants = require(ReplicatedStorage.Shared.GameConstants)
local SharedConsumeRules = require(ReplicatedStorage.Shared.Survival.ConsumeRules)

local ConsumeRules = table.clone(SharedConsumeRules)

-- Kinds applied when the use starts rather than when it ends: medicine heals at
-- once and its animation is the only cooldown, "not a pre-heal channel" (GDD
-- §4.5, §5.4, Q64). Remove Medicine here to heal at the end of the drink instead.
ConsumeRules.APPLY_AT_START = { [Consumables.Medicine] = true }

-- Seconds the use of `item` (a Consumables entry) takes.
function ConsumeRules.Duration(item): number
	if item.kind == Consumables.Medicine then
		return item.animationSeconds
	end
	return GameConstants.CONSUME_SECONDS[item.kind] or GameConstants.CONSUME_SECONDS.Food
end

-- True when `item` is applied as its use starts (medicine), false when it ends.
function ConsumeRules.AppliesAtStart(item): boolean
	return item ~= nil and ConsumeRules.APPLY_AT_START[item.kind] == true
end

-- A new use of `item` started at `now`: {requestId, catalogId, item, startedAt, endsAt}.
function ConsumeRules.Begin(requestId: string, catalogId: string, item, now: number)
	return {
		requestId = requestId,
		catalogId = catalogId,
		item = item,
		startedAt = now,
		endsAt = now + ConsumeRules.Duration(item),
	}
end

-- True once the use's animation has run its full time.
function ConsumeRules.Done(use, now: number): boolean
	return now >= use.endsAt
end

-- Why a running use of `catalogId` must stop, or nil to carry on. `view` is what
-- the server sees now: {present, alive, downed, held = the held catalog id}.
function ConsumeRules.Interruption(view, catalogId: string): string?
	if not view.present or not view.alive then
		return "NotInRun"
	elseif view.downed then
		return "Downed"
	elseif view.held ~= catalogId then
		return "Interrupted"
	end
	return nil
end

return ConsumeRules
