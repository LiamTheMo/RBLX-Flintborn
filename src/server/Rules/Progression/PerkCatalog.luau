-- Server half of Shared.Progression.PerkCatalog: what only the server uses. Everything in
-- ReplicatedStorage is downloaded to every player, so the shared module keeps
-- only what clients need; this one clones it and adds the rest, and server code
-- requires this module.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local SharedPerkCatalog = require(ReplicatedStorage.Shared.Progression.PerkCatalog)

local PerkCatalog = table.clone(SharedPerkCatalog)

-- Modifiers granted by owned ranks: {stat, op, value}.
function PerkCatalog.Modifiers(ownedPerks)
	local modifiers = {}
	for perkId, rank in ownedPerks do
		local perk = PerkCatalog.Get(perkId)
		if perk and rank > 0 then
			table.insert(modifiers, { stat = perk.stat, op = "Additive", value = perk.value * rank })
		end
	end
	return modifiers
end

return PerkCatalog
