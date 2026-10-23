-- Additive piece-based armor (GDD §21.5, Q132). A full matching set has the
-- confirmed factor (Hide ×1.2, Wood ×1.5, Stone ×1.8, Iron ×2.0); each piece adds
-- its share of that set's increment, and pieces add rather than multiply. The
-- per-piece split and how quality rolls apply are starting placeholders.

local GameConstants = require(script.Parent.Parent.GameConstants)

local ArmorRules = {}

ArmorRules.PIECE_SHARE = { Head = 0.25, Chest = 0.45, Legs = 0.30 }

-- Increment one piece adds above the unarmored factor of 1.
function ArmorRules.PieceIncrement(tier: string, slot: string, qualityRoll: number?): number
	local setFactor = GameConstants.ARMOR_SET_FACTOR[tier]
	local share = ArmorRules.PIECE_SHARE[slot]
	if setFactor == nil or share == nil then
		return 0
	end
	return (setFactor - 1) * share * (1 + (qualityRoll or 0))
end

-- Combined factor for worn pieces ({tier, slot, qualityRoll} each).
function ArmorRules.Factor(pieces): number
	local increments = {}
	for _, piece in pieces do
		table.insert(increments, ArmorRules.PieceIncrement(piece.tier, piece.slot, piece.qualityRoll))
	end
	return GameConstants.ArmorFactor(increments)
end

return ArmorRules
