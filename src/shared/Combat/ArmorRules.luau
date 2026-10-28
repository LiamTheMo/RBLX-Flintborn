-- Additive piece-based armor (GDD §21.5, §51, Q132). A full matching set has its
-- tier's factor (confirmed Hide ×1.2 and Iron ×2.0; Bone ×1.5, Copper ×1.8, then
-- ×1.25 per metal above Iron); each piece adds its share of that set's increment,
-- and pieces add rather than multiply. The per-piece split and how quality rolls
-- apply are starting placeholders.

local GameConstants = require(script.Parent.Parent.GameConstants)
local Tiers = require(script.Parent.Parent.Items.Tiers)

local ArmorRules = {}

ArmorRules.PIECE_SHARE = { Head = 0.25, Chest = 0.45, Legs = 0.30 }

-- Increment one piece adds above the unarmored factor of 1.
function ArmorRules.PieceIncrement(tier: string, slot: string, qualityRoll: number?): number
	local ladder = Tiers.Get(tier)
	local setFactor = ladder and Tiers.ArmorFactor(ladder)
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
