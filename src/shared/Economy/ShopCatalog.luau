-- NPC shops and merchants (GDD §10.1, §51, Q90, Q95, Q116, Q120). Shops sell
-- starter supplies, seeds, basic tools and cosmetic titles for Coins; purchases land in the
-- lobby backpack. Merchants buy materials, monster drops and crafted gear at fixed
-- prices: crafted items are worth 40% of their recipe's material value. Selling
-- something a Forge recipe uses shows a warning. Prices are placeholders.

local ForgeRecipes = require(script.Parent.Parent.Crafting.ForgeRecipes)
local ItemCatalog = require(script.Parent.Parent.Items.ItemCatalog)
local Recipes = require(script.Parent.Parent.Crafting.Recipes)

local ShopCatalog = {}

-- Starter supplies only (GDD §51): Wood and Stone tools, Flint Arrows, basic
-- medicine and common berries. No metal, bars or higher gear.
ShopCatalog.Stock = {
	{ id = "Bandage", catalogId = "BasicMedicine", quantity = 1, price = 50, category = "Supplies" },
	{ id = "RedberryPack", catalogId = "Redberry", quantity = 5, price = 40, category = "Supplies" },
	{ id = "SweetberryPack", catalogId = "Sweetberry", quantity = 5, price = 40, category = "Supplies" },
	{ id = "ArrowBundle", catalogId = "FlintArrow", quantity = 10, price = 60, category = "Supplies" },
	-- A planter's seed is the berry itself (StructureCatalog crops): one grows four.
	{
		id = "RedberrySeeds",
		catalogId = "Redberry",
		quantity = 2,
		price = 15,
		category = "Seeds",
		note = "Plant one in a planter to grow four.",
	},
	{
		id = "SweetberrySeeds",
		catalogId = "Sweetberry",
		quantity = 2,
		price = 15,
		category = "Seeds",
		note = "Plant one in a planter to grow four.",
	},
	{ id = "WoodenAxe", catalogId = "WoodenAxe", quantity = 1, price = 60, category = "Tools" },
	{ id = "WoodenPickaxe", catalogId = "WoodenPickaxe", quantity = 1, price = 60, category = "Tools" },
	{ id = "StoneAxe", catalogId = "StoneAxe", quantity = 1, price = 150, category = "Tools" },
	{ id = "StonePickaxe", catalogId = "StonePickaxe", quantity = 1, price = 150, category = "Tools" },
	{ id = "TitleWanderer", title = "Wanderer", price = 2000, category = "Cosmetics" },
	{ id = "TitleEmberborn", title = "Emberborn", price = 8000, category = "Cosmetics" },
}

ShopCatalog.ById = {}
for _, entry in ShopCatalog.Stock do
	ShopCatalog.ById[entry.id] = entry
	assert(entry.price > 0, "Shop prices must be positive")
	assert(entry.title or ItemCatalog.Get(entry.catalogId), "Shop item missing: " .. entry.id)
end

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

-- Materials any Forge recipe uses: selling them shows a warning.
ShopCatalog.ForgeInputs = {}
for _, recipe in ForgeRecipes.List do
	for catalogId in recipe.inputs do
		ShopCatalog.ForgeInputs[catalogId] = true
	end
end

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
