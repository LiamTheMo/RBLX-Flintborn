-- Server half of Shared.Combat.ArmorRules: what only the server uses. Everything in
-- ReplicatedStorage is downloaded to every player, so the shared module keeps
-- only what clients need; this one clones it and adds the rest, and server code
-- requires this module.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local GameConstants = require(ReplicatedStorage.Shared.GameConstants)
local SharedArmorRules = require(ReplicatedStorage.Shared.Combat.ArmorRules)

local ArmorRules = table.clone(SharedArmorRules)

-- Combined factor for worn pieces ({tier, slot, qualityRoll} each).
function ArmorRules.Factor(pieces): number
	local increments = {}
	for _, piece in pieces do
		table.insert(increments, ArmorRules.PieceIncrement(piece.tier, piece.slot, piece.qualityRoll))
	end
	return GameConstants.ArmorFactor(increments)
end

return ArmorRules
