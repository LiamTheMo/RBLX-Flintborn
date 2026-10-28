-- Ancestral Forge recipes (GDD §16, Q15–16, Q55, Q105, Q109–110, Q149). Lobby only;
-- inputs come from the vault alone and outputs have default quality (no roll).
-- Special recipes make ordinary gear and supplies; Permanent recipes convert one
-- vaulted source item. Unlocks come from discoveries (anything ever extracted)
-- and extraction counts until levels arrive in v0.13. Amounts are placeholders.

local ItemCatalog = require(script.Parent.Parent.Items.ItemCatalog)
local PermanentRules = require(script.Parent.Parent.Items.PermanentRules)
local Recipes = require(script.Parent.Recipes)

local ForgeRecipes = {}

ForgeRecipes.VERSION = 1

ForgeRecipes.Kinds = { Special = "Special", Permanent = "Permanent" }

ForgeRecipes.Categories = { "Tools", "Weapons", "Armor", "Supplies", "Permanent" }

local list = {
	-- Special: ordinary gear at default quality, from vaulted bars.
	{ id = "ForgeIronPickaxe", output = "IronPickaxe", category = "Tools", inputs = { IronBar = 20, Wood = 10 } },
	{ id = "ForgeIronAxe", output = "IronAxe", category = "Tools", inputs = { IronBar = 16, Wood = 10 } },
	{
		id = "ForgeIronSword",
		output = "IronSword",
		category = "Weapons",
		inputs = { IronBar = 30, Wood = 10, Hide = 4 },
		unlock = { extractions = 1, discovered = { "IronOre" } },
	},
	{
		id = "ForgeIronHead",
		output = "IronHead",
		category = "Armor",
		inputs = { IronBar = 24, Hide = 6 },
		unlock = { extractions = 1, discovered = { "IronOre" } },
	},
	{
		id = "ForgeIronChest",
		output = "IronChest",
		category = "Armor",
		inputs = { IronBar = 40, Hide = 10 },
		unlock = { extractions = 1, discovered = { "IronOre" } },
	},
	{
		id = "ForgeIronLegs",
		output = "IronLegs",
		category = "Armor",
		inputs = { IronBar = 30, Hide = 8 },
		unlock = { extractions = 1, discovered = { "IronOre" } },
	},
	{
		id = "ForgeArrows",
		output = "FlintArrow",
		quantity = 50,
		category = "Supplies",
		inputs = { Wood = 12, Flint = 4, Fiber = 8 },
	},
	{
		id = "ForgePotion",
		output = "Potion",
		quantity = 2,
		category = "Supplies",
		inputs = { Herbs = 20, Fiber = 4 },
		unlock = { discovered = { "Herbs" }, crafting = 3 },
	},
}

-- Permanent conversions (GDD §51): any weapon, tool or armor piece, for 10× its
-- crafting recipe plus Ancient Ember and, at the top tiers, rare materials from
-- several activities (Q16, Q55). The first conversions need roughly two extractions
-- plus one rare event (Q110, Q149). Amounts are placeholders.
ForgeRecipes.PERMANENT_MULTIPLIER = 10
local PERMANENT_GROUPS = {
	-- {tiers, Ember, unlock {extractions, level}, rare inputs for gear, for armor}
	{ tiers = { "Wood", "Stone", "Flint", "Bone", "Hide", "Copper" }, ember = 1, extractions = 2, level = 0 },
	{ tiers = { "Iron", "Obsidian", "Silver" }, ember = 2, extractions = 4, level = 10 },
	{
		tiers = { "Cobalt", "Jade" },
		ember = 3,
		extractions = 6,
		level = 20,
		gear = { Moonpetal = 2 },
		armor = { Moonpetal = 2 },
	},
	{
		tiers = { "Mithril" },
		ember = 4,
		extractions = 8,
		level = 30,
		gear = { ChargedCore = 3 },
		armor = { GlowFur = 3 },
	},
	{
		tiers = { "Adamantine" },
		ember = 5,
		extractions = 10,
		level = 40,
		gear = { GuardianHeart = 1, AbyssalShard = 3 },
		armor = { GuardianHeart = 1, Emberglass = 3 },
	},
}

local groupOf = {}
for _, group in PERMANENT_GROUPS do
	for _, tier in group.tiers do
		groupOf[tier] = group
	end
end

local function permanent(source: string, inputs, group, isArmor: boolean)
	local cost = {}
	for input, amount in inputs do
		cost[input] = amount * ForgeRecipes.PERMANENT_MULTIPLIER
	end
	cost.AncientEmber = (cost.AncientEmber or 0) + group.ember
	for input, amount in (if isArmor then group.armor else group.gear) or {} do
		cost[input] = (cost[input] or 0) + amount
	end
	table.insert(list, {
		id = "Permanent" .. source,
		source = source,
		inputs = cost,
		unlock = { extractions = group.extractions, discovered = { "AncientEmber" }, level = group.level },
	})
end

for _, recipe in Recipes.List do
	local def = ItemCatalog.Get(recipe.output)
	if PermanentRules.IsEligible(recipe.output) and def.tier and groupOf[def.tier] then
		permanent(recipe.output, recipe.inputs, groupOf[def.tier], def.family == ItemCatalog.Families.Armor)
	end
end
-- The Guardian's Fang has no recipe: its conversion is priced directly.
table.insert(list, {
	id = "PermanentGuardianFang",
	source = "GuardianFang",
	inputs = { AncientEmber = 5, GuardianHeart = 2, ChargedCore = 5, GlowFur = 5 },
	unlock = { extractions = 10, discovered = { "AncientEmber" }, level = 40 },
})

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
