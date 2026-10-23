-- Deterministic modifier stacking (GDD §33.3, Q78). Every buff or perk is either
-- additive or multiplicative: final = floor(base × (1 + Σadditive) × Πmultiplicative).

local ModifierRules = {}

ModifierRules.Additive = "Additive"
ModifierRules.Multiplicative = "Multiplicative"

-- The unrounded value; `modifiers` is a list of {op, value}.
function ModifierRules.Raw(base: number, modifiers): number
	local additive, multiplicative = 0, 1
	for _, modifier in modifiers do
		if modifier.op == ModifierRules.Multiplicative then
			multiplicative *= modifier.value
		else
			additive += modifier.value
		end
	end
	return base * (1 + additive) * multiplicative
end

function ModifierRules.Final(base: number, modifiers): number
	-- The epsilon keeps 100 × 1.1 × 1.2 at 132 rather than 131.99999.
	return math.floor(ModifierRules.Raw(base, modifiers) + 1e-9)
end

-- Small yields keep their expected value: the fractional part pays out by chance,
-- so +10% on a 3-item hit still averages 3.3 instead of always rounding to 3.
function ModifierRules.RollYield(base: number, modifiers, rng): number
	local raw = ModifierRules.Raw(base, modifiers)
	local whole = math.floor(raw + 1e-9)
	return whole + (if rng:NextNumber() < raw - whole then 1 else 0)
end

-- Sums one stat across modifier lists of {stat, op, value}, capped if given.
function ModifierRules.Collect(sources, stat: string)
	local list = {}
	for _, modifier in sources do
		if modifier.stat == stat then
			table.insert(list, modifier)
		end
	end
	return list
end

return ModifierRules
