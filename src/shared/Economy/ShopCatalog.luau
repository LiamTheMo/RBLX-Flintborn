-- NPC shops and merchants (GDD §10.1, Q90, Q95, Q116, Q120). Shops sell starter
-- supplies, seeds, basic tools and cosmetic titles for Coins; purchases land in the
-- lobby backpack. Merchants buy materials, monster drops and crafted gear at fixed
-- prices: crafted items are worth 40% of their recipe's material value. Selling
-- something a Forge recipe uses shows a warning. Prices are placeholders.

local ForgeRecipes = require(script.Parent.Parent.Crafting.ForgeRecipes)
local ItemCatalog = require(script.Parent.Parent.Items.ItemCatalog)
local Recipes = require(script.Parent.Parent.Crafting.Recipes)

local ShopCatalog = {}

ShopCatalog.Stock = {
	{ id = "Bandage", catalogId = "BasicMedicine", quantity = 1, price = 50, category = "Supplies" },
	{ id = "BerryPack", catalogId = "Berries", quantity = 5, price = 40, category = "Supplies" },
	{ id = "ArrowBundle", catalogId = "Arrow", quantity = 10, price = 60, category = "Supplies" },
	{ id = "HerbSeeds", catalogId = "Herbs", quantity = 2, price = 25, category = "Seeds" },
	{ id = "BerrySeeds", catalogId = "Berries", quantity = 2, price = 15, category = "Seeds" },
	{ id = "StoneAxe", catalogId = "StoneAxe", quantity = 1, price = 150, category = "Tools" },
	{ id = "BasicPickaxe", catalogId = "BasicPickaxe", quantity = 1, price = 150, category = "Tools" },
	{ id = "Sickle", catalogId = "Sickle", quantity = 1, price = 150, category = "Tools" },
	{ id = "TitleWanderer", title = "Wanderer", price = 2000, category = "Cosmetics" },
	{ id = "TitleEmberborn", title = "Emberborn", price = 8000, category = "Cosmetics" },
}

ShopCatalog.ById = {}
for _, entry in ShopCatalog.Stock do
	ShopCatalog.ById[entry.id] = entry
	assert(entry.price > 0, "Shop prices must be positive")
	assert(entry.title or ItemCatalog.Get(entry.catalogId), "Shop item missing: " .. entry.id)
end

-- Merchant prices for raw materials (Coins per unit).
ShopCatalog.MATERIAL_VALUES = {
	Wood = 2,
	Stone = 2,
	Fiber = 1,
	Herbs = 3,
	Berries = 2,
	Hide = 5,
	RawMeat = 2,
	Iron = 8,
	Jade = 12,
	Obsidian = 10,
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
