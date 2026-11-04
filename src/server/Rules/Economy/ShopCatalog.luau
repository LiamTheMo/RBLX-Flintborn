-- Server half of Shared.Economy.ShopCatalog: what only the server uses. Everything in
-- ReplicatedStorage is downloaded to every player, so the shared module keeps
-- only what clients need; this one clones it and adds the rest, and server code
-- requires this module.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Recipes = require(ReplicatedStorage.Shared.Crafting.Recipes)
local SharedShopCatalog = require(ReplicatedStorage.Shared.Economy.ShopCatalog)

local ShopCatalog = table.clone(SharedShopCatalog)

-- Merchant prices for raw materials and berries (Coins per unit). Bars are worth a
-- little more than their ore (smelting time). Every shop entry costs more than a
-- merchant pays for it, so buying to sell never makes Coins.
ShopCatalog.MATERIAL_VALUES = {
	Wood = 2,
	Stone = 2,
	Flint = 3,
	Fiber = 1,
	Herbs = 3,
	Resin = 4,
	Redberry = 2,
	Sweetberry = 2,
	Hide = 5,
	RawMeat = 2,
	Bone = 3,
	CopperOre = 4,
	CopperBar = 5,
	IronOre = 8,
	IronBar = 10,
	SilverOre = 14,
	SilverBar = 17,
	CobaltOre = 22,
	CobaltBar = 26,
	MithrilOre = 35,
	MithrilBar = 42,
	AdamantineOre = 60,
	AdamantineBar = 72,
	Obsidian = 12,
	Jade = 20,
	-- Gathered materials with no use yet (GDD §53): priced by how deep they grow.
	Clay = 2,
	CaveMushroom = 3,
	RedcapMushroom = 3,
	ChestnutMushroom = 3,
	Thornvine = 3,
	Frostleaf = 4,
	JuniperBerry = 2,
	Elderberry = 2,
	Raspberry = 2,
	Hazelnut = 2,
	Amethyst = 16,
	Starstone = 40,
	Stormglass = 40,
	DireHide = 15,
	ChargedCore = 60,
	GlowFur = 60,
	GuardianHeart = 1000,
	AshenOil = 40,
	SiegeResin = 50,
	AbyssalShard = 150,
	Emberglass = 150,
	Bloodroot = 30,
	Moonpetal = 30,
	Sunberry = 25,
	Glimmerberry = 25,
	AncientEmber = 300,
}

ShopCatalog.CRAFTED_FRACTION = 0.4

-- Coins a merchant pays for one unit (or one unique item), or nil if it buys none.
function ShopCatalog.SellValue(catalogId: string): number?
	local direct = ShopCatalog.MATERIAL_VALUES[catalogId]
	if direct then
		return direct
	end
	local recipe = Recipes.Get(catalogId)
	if recipe == nil then
		return nil
	end
	local total = 0
	for input, quantity in recipe.inputs do
		total += (ShopCatalog.MATERIAL_VALUES[input] or 0) * quantity
	end
	local value = math.floor(total * ShopCatalog.CRAFTED_FRACTION / recipe.quantity)
	return if value > 0 then value else nil
end

return ShopCatalog
