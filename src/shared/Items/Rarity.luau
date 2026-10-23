-- The eight ordered rarity tiers (GDD Q51). Rarity is fixed per item archetype and
-- never rolled (Q102). Colours are always shown alongside the tier name.

local GameConstants = require(script.Parent.Parent.GameConstants)

local Rarity = {}

Rarity.Order = GameConstants.RARITIES

Rarity.Colors = {
	Common = Color3.fromRGB(190, 190, 190),
	Uncommon = Color3.fromRGB(96, 192, 96),
	Rare = Color3.fromRGB(70, 140, 230),
	Epic = Color3.fromRGB(160, 90, 220),
	Legendary = Color3.fromRGB(240, 170, 40),
	Mythic = Color3.fromRGB(230, 70, 70),
	Secret = Color3.fromRGB(40, 220, 210),
	Exclusive = Color3.fromRGB(250, 120, 200),
}

-- 1 for Common up to 8 for Exclusive; nil for an unknown name.
function Rarity.Index(name: string): number?
	return table.find(Rarity.Order, name)
end

function Rarity.IsValid(name: any): boolean
	return type(name) == "string" and Rarity.Index(name) ~= nil
end

return Rarity
