-- What happens to carried items when an at-risk player dies or leaves (GDD §29,
-- Q156–157). Ordinary items go into ONE lootable body for exactly 600 s; owned
-- Permanent items never enter a body and go back to their owner's lobby backpack.

local GameConstants = require(script.Parent.Parent.GameConstants)

local DeathRules = {}

DeathRules.BODY_SECONDS = GameConstants.CORPSE_SECONDS

-- Splits carried items into (bodyItems, keptItems).
function DeathRules.Split(items)
	local body, kept = {}, {}
	for _, item in items do
		if item.permanent then
			table.insert(kept, item)
		else
			table.insert(body, item)
		end
	end
	return body, kept
end

function DeathRules.IsExpired(createdAt: number, now: number): boolean
	return now - createdAt >= DeathRules.BODY_SECONDS
end

-- Takes one entry out of a body's contents. Returns the entry or nil.
function DeathRules.Take(contents, index: number)
	if type(index) ~= "number" or index % 1 ~= 0 or contents[index] == nil then
		return nil
	end
	return table.remove(contents, index)
end

return DeathRules
