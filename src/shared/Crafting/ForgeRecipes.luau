-- Ancestral Forge recipes (GDD §16, Q15–16, Q55, Q105, Q109–110, Q149). Lobby only;
-- inputs come from the vault alone and outputs have default quality (no roll).
-- Special recipes make ordinary gear and supplies; Permanent recipes convert one
-- vaulted source item. Unlocks come from discoveries (anything ever extracted)
-- and extraction counts until levels arrive in v0.13. Amounts are placeholders.

local ItemCatalog = require(script.Parent.Parent.Items.ItemCatalog)
local PermanentRules = require(script.Parent.Parent.Items.PermanentRules)

local ForgeRecipes = {}

ForgeRecipes.VERSION = 1

ForgeRecipes.Kinds = { Special = "Special", Permanent = "Permanent" }

ForgeRecipes.Categories = { "Tools", "Weapons", "Armor", "Supplies", "Permanent" }

local list = {
	-- Special: ordinary gear at default quality.
	{ id = "ForgeIronPickaxe", output = "IronPickaxe", category = "Tools", inputs = { Iron = 20, Wood = 10 } },
	{ id = "ForgeIronAxe", output = "IronAxe", category = "Tools", inputs = { Iron = 16, Wood = 10 } },
	{
		id = "ForgeIronSword",
		output = "IronSword",
		category = "Weapons",
		inputs = { Iron = 30, Wood = 10, Hide = 4 },
		unlock = { extractions = 1, discovered = { "Iron" } },
	},
	{
		id = "ForgeIronHead",
		output = "IronHead",
		category = "Armor",
		inputs = { Iron = 24, Hide = 6 },
		unlock = { extractions = 1, discovered = { "Iron" } },
	},
	{
		id = "ForgeIronChest",
		output = "IronChest",
		category = "Armor",
		inputs = { Iron = 40, Hide = 10 },
		unlock = { extractions = 1, discovered = { "Iron" } },
	},
	{
		id = "ForgeIronLegs",
		output = "IronLegs",
		category = "Armor",
		inputs = { Iron = 30, Hide = 8 },
		unlock = { extractions = 1, discovered = { "Iron" } },
	},
	{
		id = "ForgeArrows",
		output = "Arrow",
		quantity = 50,
		category = "Supplies",
		inputs = { Wood = 12, Stone = 6, Fiber = 8 },
	},
	{
		id = "ForgePotion",
		output = "Potion",
		quantity = 2,
		category = "Supplies",
		inputs = { Herbs = 20, Fiber = 4 },
		unlock = { discovered = { "Herbs" } },
	},

	-- Permanent conversions. The pickaxe is the first target: roughly two
	-- extractions plus one rare event (Q110, Q149). Higher tiers need materials from
	-- several activities (Q16) and event reagents that farming cannot supply (Q55).
	{
		id = "PermanentBasicPickaxe",
		source = "BasicPickaxe",
		inputs = { Stone = 150, Wood = 60, Iron = 20, AncientEmber = 1 },
		unlock = { extractions = 2, discovered = { "AncientEmber" } },
	},
	{
		id = "PermanentStoneSpear",
		source = "StoneSpear",
		inputs = { Stone = 200, Wood = 120, Fiber = 60, AncientEmber = 2 },
		unlock = { extractions = 4, discovered = { "AncientEmber" } },
	},
	{
		id = "PermanentIronSword",
		source = "IronSword",
		inputs = { Iron = 120, Wood = 40, Hide = 20, AncientEmber = 3 },
		unlock = { extractions = 6, discovered = { "AncientEmber", "Iron" } },
	},
	{
		id = "PermanentIronHead",
		source = "IronHead",
		inputs = { Iron = 100, Hide = 20, AncientEmber = 2 },
		unlock = { extractions = 6, discovered = { "AncientEmber", "Iron" } },
	},
	{
		id = "PermanentIronChest",
		source = "IronChest",
		inputs = { Iron = 160, Hide = 30, AncientEmber = 3 },
		unlock = { extractions = 6, discovered = { "AncientEmber", "Iron" } },
	},
	{
		id = "PermanentIronLegs",
		source = "IronLegs",
		inputs = { Iron = 120, Hide = 24, AncientEmber = 2 },
		unlock = { extractions = 6, discovered = { "AncientEmber", "Iron" } },
	},
}

ForgeRecipes.ById = {}
ForgeRecipes.List = {}

for _, recipe in list do
	assert(ForgeRecipes.ById[recipe.id] == nil, "Duplicate forge recipe " .. recipe.id)
	for input in recipe.inputs do
		assert(ItemCatalog.IsMaterial(input), "Forge input must be a vault material: " .. input)
	end
	if recipe.source then
		assert(PermanentRules.IsEligible(recipe.source), "Not a Permanent archetype: " .. recipe.source)
		recipe.kind = ForgeRecipes.Kinds.Permanent
		recipe.category = "Permanent"
		recipe.output = recipe.source
	else
		assert(ItemCatalog.Get(recipe.output), "Forge output is not an item: " .. tostring(recipe.output))
		recipe.kind = ForgeRecipes.Kinds.Special
	end
	recipe.quantity = recipe.quantity or 1
	recipe.unlock = recipe.unlock or {}
	recipe.version = ForgeRecipes.VERSION
	ForgeRecipes.ById[recipe.id] = recipe
	table.insert(ForgeRecipes.List, recipe)
end

function ForgeRecipes.Get(recipeId: any)
	return type(recipeId) == "string" and ForgeRecipes.ById[recipeId] or nil
end

return ForgeRecipes
