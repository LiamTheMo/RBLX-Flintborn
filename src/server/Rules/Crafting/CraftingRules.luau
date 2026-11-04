-- Server half of Shared.Crafting.CraftingRules: what only the server uses. Everything in
-- ReplicatedStorage is downloaded to every player, so the shared module keeps
-- only what clients need; this one clones it and adds the rest, and server code
-- requires this module.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local SharedCraftingRules = require(ReplicatedStorage.Shared.Crafting.CraftingRules)

local CraftingRules = table.clone(SharedCraftingRules)

-- The refusal code for crafting away from `station` ("NeedsAnvil").
function CraftingRules.Refusal(station: string): string
	return "Needs" .. station
end

-- A recipe's inputs for `count` units.
function CraftingRules.BatchInputs(recipe, count: number)
	local inputs = {}
	for catalogId, amount in recipe.inputs do
		inputs[catalogId] = amount * count
	end
	return inputs
end

-- A new smelting job; `station` is the station part it is bound to.
function CraftingRules.NewJob(recipe, count: number, now: number, station: any, character: any)
	return {
		recipe = recipe,
		count = count,
		done = 0,
		unitEndsAt = now + recipe.seconds,
		station = station,
		character = character,
	}
end

-- Why a running job must stop, or nil. `check` holds what the server sees now:
-- atRisk (still in the run), sameCharacter, alive, downed, stationStanding and
-- distance (studs from the station).
function CraftingRules.Interruption(check): string?
	if not check.atRisk then
		return "NotInRun"
	end
	if not check.sameCharacter or not check.alive then
		return "Died"
	end
	if check.downed then
		return "Downed"
	end
	if not check.stationStanding then
		return "StationGone"
	end
	if type(check.distance) ~= "number" or check.distance > CraftingRules.STATION_RANGE then
		return "MovedAway"
	end
	return nil
end

-- True when the job's current unit is finished.
function CraftingRules.UnitDue(job, now: number): boolean
	return job.done < job.count and now >= job.unitEndsAt
end

-- Records one finished unit and starts the next. True when the job is complete.
function CraftingRules.Advance(job): boolean
	job.done += 1
	if job.done >= job.count then
		return true
	end
	job.unitEndsAt += job.recipe.seconds
	return false
end

-- True when the recipe passes the menu's filter: {category?, tier?, hereOnly?}.
function CraftingRules.Matches(recipe, filter, nearby): boolean
	if filter.category and CraftingRules.Category(recipe) ~= filter.category then
		return false
	end
	if filter.tier and CraftingRules.Tier(recipe) ~= filter.tier then
		return false
	end
	return not filter.hereOnly or CraftingRules.AvailableHere(recipe, nearby)
end

return CraftingRules
