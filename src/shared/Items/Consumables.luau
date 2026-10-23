-- Medicine and food definitions (GDD §4.5, Q64, Q135, Q137). Medicine heals at once
-- and its animation is the only cooldown; food restores hunger and heals over the
-- fixed 10-second window. The full food catalog is still Open; these are the
-- confirmed examples.

local GameConstants = require(script.Parent.Parent.GameConstants)

local Consumables = {}

Consumables.Medicine = "Medicine"
Consumables.Food = "Food"

local medicine = GameConstants.MEDICINE
local food = GameConstants.FOOD

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
	Berries = {
		kind = Consumables.Food,
		name = "Berries",
		heal = food.Berries.heal,
		hunger = food.Berries.hunger,
	},
	CookedMeat = {
		kind = Consumables.Food,
		name = "Cooked Meat",
		heal = food.CookedMeat.heal,
		hunger = food.CookedMeat.hunger,
	},
}

function Consumables.Get(catalogId: any)
	return type(catalogId) == "string" and Consumables.Catalog[catalogId] or nil
end

return Consumables
