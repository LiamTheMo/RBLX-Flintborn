-- Permanent items (GDD §15, §17, Q8–13, Q109–110, Q156). A Permanent item is the
-- same unique instance with the same stats and quality roll, flagged `permanent`:
-- it survives its owner's death, transfers ownership when dropped and picked up
-- (or traded, v0.14), and is lost if left on the ground when the world resets.
-- Any gear converts; rarity alone grants nothing.

local ItemCatalog = require(script.Parent.ItemCatalog)

local PermanentRules = {}

-- Any weapon, tool or armor piece can become Permanent (GDD §51); the Forge prices
-- the conversion by tier.
local GEAR = { Weapon = true, Tool = true, Armor = true }

function PermanentRules.IsEligible(catalogId: string): boolean
	local def = ItemCatalog.Get(catalogId)
	return def ~= nil and GEAR[def.family] == true
end

return PermanentRules
