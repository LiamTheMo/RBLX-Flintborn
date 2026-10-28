-- Medicine, food and boosts (GDD §4.5, §51, Q64, Q135, Q137). Medicine heals at
-- once and its animation is the only cooldown; food restores hunger and heals over
-- the fixed 10-second window; some berries and every draught add a timed boost.

local GameConstants = require(script.Parent.Parent.GameConstants)

local Consumables = {}

Consumables.Medicine = "Medicine"
Consumables.Food = "Food"

local medicine = GameConstants.MEDICINE
local food = GameConstants.FOOD

-- Draughts and boost berries apply a timed boost (GDD §51): `boost` = {kind,
-- amount, seconds}. XP boosts add to Premium and paid boosters (Q162); Luck raises
-- rare-drop chances. A new boost of the same kind replaces the running one.
Consumables.Boost = "Boost"
Consumables.BoostKinds = { XP = "XP", Luck = "Luck" }

local function boost(kind: string, amount: number, seconds: number)
	return { kind = kind, amount = amount, seconds = seconds }
end

Consumables.Catalog = {
	BasicMedicine = {
		kind = Consumables.Medicine,
		name = "Basic Medicine",
		heal = medicine.Basic.heal,
		animationSeconds = medicine.Basic.animationSeconds,
	},
	AdvancedMedicine = {
		kind = Consumables.Medicine,
		name = "Advanced Medicine",
		heal = medicine.Advanced.heal,
		animationSeconds = medicine.Advanced.animationSeconds,
	},
	Potion = {
		kind = Consumables.Medicine,
		name = "Healing Potion",
		heal = medicine.Potion.heal,
		animationSeconds = medicine.Potion.animationSeconds,
	},
	-- Healing Potion brewed with Bloodroot (placeholder strength).
	GreaterPotion = {
		kind = Consumables.Medicine,
		name = "Greater Healing Potion",
		rarity = "Uncommon",
		heal = 75,
		animationSeconds = medicine.Potion.animationSeconds,
	},
	-- Berries: common varieties grow on bushes and in planters; Sunberry and
	-- Glimmerberry only on rare shrubs.
	Redberry = {
		kind = Consumables.Food,
		name = "Redberry",
		heal = food.Redberry.heal,
		hunger = food.Redberry.hunger,
	},
	Sweetberry = { kind = Consumables.Food, name = "Sweetberry", heal = 0, hunger = 0.25 },
	Sunberry = {
		kind = Consumables.Food,
		name = "Sunberry",
		rarity = "Rare",
		tradeable = true,
		heal = 0,
		hunger = 0.05,
		boost = boost("XP", 0.10, 180),
	},
	Glimmerberry = {
		kind = Consumables.Food,
		name = "Glimmerberry",
		rarity = "Rare",
		tradeable = true,
		heal = 0,
		hunger = 0.05,
		boost = boost("Luck", 0.05, 180),
	},
	CookedMeat = {
		kind = Consumables.Food,
		name = "Cooked Meat",
		heal = food.CookedMeat.heal,
		hunger = food.CookedMeat.hunger,
	},
	-- Brewed at a Cauldron (placeholder strengths and durations).
	HeartyTonic = { kind = Consumables.Food, name = "Hearty Tonic", rarity = "Uncommon", heal = 0, hunger = 0.60 },
	SunberryDraught = {
		kind = Consumables.Boost,
		name = "Sunberry Draught",
		rarity = "Uncommon",
		boost = boost("XP", 0.25, 600),
	},
	StrongSunberryDraught = {
		kind = Consumables.Boost,
		name = "Strong Sunberry Draught",
		rarity = "Rare",
		boost = boost("XP", 0.25, 900),
	},
	GlimmerDraught = {
		kind = Consumables.Boost,
		name = "Glimmer Draught",
		rarity = "Uncommon",
		boost = boost("Luck", 0.15, 600),
	},
	StrongGlimmerDraught = {
		kind = Consumables.Boost,
		name = "Strong Glimmer Draught",
		rarity = "Rare",
		boost = boost("Luck", 0.15, 900),
	},
}

function Consumables.Get(catalogId: any)
	return type(catalogId) == "string" and Consumables.Catalog[catalogId] or nil
end

return Consumables
