-- Rebirth perks (GDD §37, Q86–88): permanently active, some with several ranks,
-- no loadout slots. Each rank's value is additive. Costs are tokens per rank.

local PerkCatalog = {}

PerkCatalog.Perks = {
	Scholar = {
		name = "Scholar",
		description = "+5% XP per rank",
		stat = "Xp",
		value = 0.05,
		costs = { 1, 2, 3, 4, 5 },
	},
	Fortune = {
		name = "Fortune",
		description = "+2% rare-drop luck per rank",
		stat = "Luck",
		value = 0.02,
		costs = { 2, 3, 4 },
	},
	Bounty = {
		name = "Bounty",
		description = "+3% gathered drop quantity per rank",
		stat = "DropQuantity",
		value = 0.03,
		costs = { 1, 2, 3, 4, 5 },
	},
	Tidewalker = {
		name = "Tidewalker",
		description = "+10% movement speed in water per rank",
		stat = "SwimSpeed",
		value = 0.1,
		costs = { 1, 2 },
	},
}

PerkCatalog.ORDER = { "Scholar", "Fortune", "Bounty", "Tidewalker" }

function PerkCatalog.Get(perkId: any)
	return type(perkId) == "string" and PerkCatalog.Perks[perkId] or nil
end

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
