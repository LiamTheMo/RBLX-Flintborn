-- Field crafting recipes (GDD §16.8, §19.1–19.2, Q105–107). Basic recipes work
-- anywhere; advanced gear needs a workbench. Every arrow recipe makes exactly 10.
-- Ingredient amounts are starting placeholders (§19.2 marks costs as Proposed).

local ItemCatalog = require(script.Parent.Parent.Items.ItemCatalog)

local Recipes = {}

Recipes.Anywhere = "Anywhere"
Recipes.Workbench = "Workbench"
Recipes.Furnace = "Furnace"

local list = {
	-- Basic, craftable anywhere: a first set in about ten minutes (Q106).
	{ id = "WoodenSpear", inputs = { Wood = 5, Fiber = 3 } },
	{ id = "StoneSpear", inputs = { Stone = 3, Wood = 4, Fiber = 3 } },
	{ id = "StoneAxe", inputs = { Stone = 3, Wood = 3, Fiber = 2 } },
	{ id = "BasicPickaxe", inputs = { Stone = 4, Wood = 3, Fiber = 2 } },
	{ id = "StoneDagger", inputs = { Stone = 2, Fiber = 2 } },
	{ id = "BasicBow", inputs = { Wood = 6, Fiber = 5 } },
	{ id = "Arrow", quantity = 10, inputs = { Wood = 3, Fiber = 2 } },
	{ id = "BasicMedicine", inputs = { Fiber = 4, Herbs = 2 } },
	{ id = "Workbench", inputs = { Wood = 20, Stone = 10 } },
	{ id = "HideHead", inputs = { Hide = 3, Fiber = 2 } },
	{ id = "HideChest", inputs = { Hide = 5, Fiber = 3 } },
	{ id = "HideLegs", inputs = { Hide = 4, Fiber = 2 } },

	-- Advanced, workbench only.
	{ id = "Sickle", station = "Workbench", inputs = { Stone = 3, Wood = 2, Fiber = 2 } },
	{ id = "StoneSword", station = "Workbench", inputs = { Stone = 6, Wood = 3, Fiber = 2 } },
	{ id = "IronSword", station = "Workbench", inputs = { Iron = 8, Wood = 3, Fiber = 2 } },
	{ id = "IronAxe", station = "Workbench", inputs = { Iron = 5, Wood = 4 } },
	{ id = "IronPickaxe", station = "Workbench", inputs = { Iron = 6, Wood = 4 } },
	{ id = "AdvancedMedicine", station = "Workbench", inputs = { Herbs = 5, Fiber = 3 } },
	{ id = "Potion", station = "Workbench", inputs = { Herbs = 10, Fiber = 2 } },
	{ id = "WoodHead", station = "Workbench", inputs = { Wood = 10, Fiber = 4 } },
	{ id = "WoodChest", station = "Workbench", inputs = { Wood = 16, Fiber = 6 } },
	{ id = "WoodLegs", station = "Workbench", inputs = { Wood = 12, Fiber = 5 } },
	{ id = "StoneHead", station = "Workbench", inputs = { Stone = 12, Fiber = 4, Hide = 2 } },
	{ id = "StoneChest", station = "Workbench", inputs = { Stone = 20, Fiber = 6, Hide = 3 } },
	{ id = "StoneLegs", station = "Workbench", inputs = { Stone = 15, Fiber = 5, Hide = 2 } },
	{ id = "IronHead", station = "Workbench", inputs = { Iron = 8, Hide = 2, Fiber = 2 } },
	{ id = "IronChest", station = "Workbench", inputs = { Iron = 14, Hide = 3, Fiber = 3 } },
	{ id = "IronLegs", station = "Workbench", inputs = { Iron = 10, Hide = 2, Fiber = 2 } },

	-- Cooking, at a built furnace.
	{ id = "CookedMeat", station = "Furnace", inputs = { RawMeat = 1, Wood = 1 } },
}

Recipes.VERSION = 1
Recipes.ById = {}
Recipes.List = {}

for _, recipe in list do
	assert(ItemCatalog.Get(recipe.id), "Recipe output is not an item: " .. recipe.id)
	for input in recipe.inputs do
		assert(ItemCatalog.Get(input), "Recipe input is not an item: " .. input)
	end
	recipe.output = recipe.id
	recipe.quantity = recipe.quantity or 1
	recipe.station = recipe.station or Recipes.Anywhere
	recipe.version = Recipes.VERSION
	Recipes.ById[recipe.id] = recipe
	table.insert(Recipes.List, recipe)
end

function Recipes.Get(recipeId: any)
	return type(recipeId) == "string" and Recipes.ById[recipeId] or nil
end

return Recipes
