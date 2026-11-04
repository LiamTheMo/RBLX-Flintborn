-- NPC shops and merchants (GDD §10.1, §51, Q90, Q95, Q116, Q120). Shops sell
-- starter supplies, seeds, basic tools and cosmetic titles for Coins; purchases land in the
-- lobby backpack. Merchants buy materials, monster drops and crafted gear at fixed
-- prices: crafted items are worth 40% of their recipe's material value. Selling
-- something a Forge recipe uses shows a warning. Prices are placeholders.

local ForgeRecipes = require(script.Parent.Parent.Crafting.ForgeRecipes)
local ItemCatalog = require(script.Parent.Parent.Items.ItemCatalog)
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

-- Materials any Forge recipe uses: selling them shows a warning.
ShopCatalog.ForgeInputs = {}
for _, recipe in ForgeRecipes.List do
	for catalogId in recipe.inputs do
		ShopCatalog.ForgeInputs[catalogId] = true
	end
end

return ShopCatalog
