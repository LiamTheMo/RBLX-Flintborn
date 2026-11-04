-- Pure progression rules over a profile (GDD §33, §37, Q52–54, Q69–89, Q150–153).
-- General XP and mastery XP apply to the profile the moment they are earned and are
-- never taken back by death (Q70). Each run tracks the XP it earned so a Center
-- extraction can add an equal bonus once (Q69); portable runes never do (Q158).
-- Rebirth resets the general level only (Q82).

local PerkCatalog = require(script.Parent.PerkCatalog)

local ProgressionRules = {}

function ProgressionRules.PerkCost(perkId: string, rank: number): number?
	local perk = PerkCatalog.Get(perkId)
	return perk and perk.costs[rank + 1] or nil
end

return ProgressionRules
