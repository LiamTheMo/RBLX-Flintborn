-- Crafting recipes (GDD §16.8, §19.1–19.2, §51, Q105–107). Gear comes from the
-- tier ladder: Wood, Stone, Flint, Bone and Hide by hand; Copper, Iron and
-- Obsidian at a Workbench; Silver and up, and Jade, at an Anvil. Ores smelt 1:1
-- into bars at a Furnace, costing only time (`seconds`); potions and draughts brew
-- at a Cauldron. Every arrow recipe makes exactly 10. Amounts are placeholders.

local ItemCatalog = require(script.Parent.Parent.Items.ItemCatalog)
local Tiers = require(script.Parent.Parent.Items.Tiers)

local Recipes = {}

Recipes.Anywhere = "Anywhere"
Recipes.Workbench = "Workbench"
Recipes.Furnace = "Furnace"
Recipes.Anvil = "Anvil"
Recipes.Cauldron = "Cauldron"

local list = {
	-- Supplies and stations.
	{ id = "FlintArrow", quantity = 10, inputs = { Wood = 3, Flint = 1, Fiber = 2 } },
	{ id = "BasicMedicine", inputs = { Fiber = 4, Herbs = 2 } },
	{ id = "Workbench", inputs = { Wood = 20, Stone = 10 } },
	{ id = "AdvancedMedicine", station = "Workbench", inputs = { Herbs = 5, Fiber = 3 } },

	-- Siege items (GDD §51).
	{ id = "FireBomb", station = "Workbench", inputs = { AshenOil = 1, Resin = 1, Fiber = 2 } },
	{ id = "BreachingCharge", station = "Workbench", inputs = { SiegeResin = 2, IronBar = 2, Fiber = 2 } },

	-- Cooking, at a built furnace.
	{ id = "CookedMeat", station = "Furnace", inputs = { RawMeat = 1, Wood = 1 } },

	-- Brewing, at a built cauldron.
	{ id = "Potion", station = "Cauldron", inputs = { Redberry = 5, Herbs = 5 } },
	{ id = "GreaterPotion", station = "Cauldron", inputs = { Redberry = 5, Herbs = 5, Bloodroot = 1 } },
	{ id = "HeartyTonic", station = "Cauldron", inputs = { Sweetberry = 6 } },
	{ id = "SunberryDraught", station = "Cauldron", inputs = { Sunberry = 3, Herbs = 2 } },
	{ id = "StrongSunberryDraught", station = "Cauldron", inputs = { Sunberry = 3, Herbs = 2, Moonpetal = 1 } },
	{ id = "GlimmerDraught", station = "Cauldron", inputs = { Glimmerberry = 3, Herbs = 2 } },
	{ id = "StrongGlimmerDraught", station = "Cauldron", inputs = { Glimmerberry = 3, Herbs = 2, Moonpetal = 1 } },
}

-- Smelting: 1 ore → 1 bar at a Furnace, slower for higher metals (no fuel).
Recipes.SMELT_SECONDS = { Copper = 2, Iron = 3, Silver = 4, Cobalt = 5, Mithril = 6, Adamantine = 8 }
for _, metal in Tiers.Metals do
	local tier = Tiers.Get(metal)
	table.insert(list, {
		id = tier.material,
		station = "Furnace",
		inputs = { [tier.ore] = 1 },
		seconds = Recipes.SMELT_SECONDS[metal],
	})
end

-- What one piece of gear costs in its tier's material (bars for metals), plus the
-- shared parts. Wooden gear is all wood.
local GEAR_COSTS = {
	Spear = { main = 3, parts = { Wood = 4, Fiber = 3 } },
	Dagger = { main = 2, parts = { Fiber = 2 } },
	Sword = { main = 6, parts = { Wood = 3, Fiber = 2 } },
	Bow = { main = 3, parts = { Wood = 6, Fiber = 5 } },
	Axe = { main = 3, parts = { Wood = 3, Fiber = 2 } },
	Pickaxe = { main = 4, parts = { Wood = 3, Fiber = 2 } },
	Head = { main = 3, parts = { Fiber = 2 } },
	Chest = { main = 5, parts = { Fiber = 3 } },
	Legs = { main = 4, parts = { Fiber = 2 } },
}
local WOODEN = {
	Spear = { Wood = 5, Fiber = 3 },
	Bow = { Wood = 6, Fiber = 5 },
	Axe = { Wood = 6, Fiber = 2 },
	Pickaxe = { Wood = 7, Fiber = 2 },
}
-- Rare inputs the top metals also need (GDD §51): weapons and tools vs armor.
local TOP_INPUTS = {
	Silver = { gear = { Resin = 1 }, armor = { Resin = 1 } },
	Cobalt = { gear = { Resin = 2 }, armor = { Resin = 2 } },
	Mithril = { gear = { ChargedCore = 1, Bloodroot = 1 }, armor = { GlowFur = 1, DireHide = 2 } },
	Adamantine = { gear = { AbyssalShard = 1, Bloodroot = 2 }, armor = { Emberglass = 1, DireHide = 3 } },
}

local function gearRecipe(tier, family: string, outputId: string, isArmor: boolean)
	local inputs = {}
	if tier.id == "Wood" then
		for input, amount in WOODEN[family] do
			inputs[input] = amount
		end
	else
		local cost = GEAR_COSTS[family]
		inputs[tier.material] = cost.main
		for input, amount in cost.parts do
			inputs[input] = (inputs[input] or 0) + amount
		end
		-- Metal armor is strapped with hide; Bone armor too.
		if isArmor and tier.id ~= "Hide" then
			inputs.Hide = (inputs.Hide or 0) + (if family == "Chest" then 3 else 2)
		end
		local top = TOP_INPUTS[tier.id]
		if top then
			for input, amount in (if isArmor then top.armor else top.gear) do
				inputs[input] = (inputs[input] or 0) + amount
			end
		end
	end
	table.insert(list, { id = outputId, station = tier.station, inputs = inputs })
end

for _, tier in Tiers.Ladder do
	for _, family in { "Spear", "Dagger", "Sword", "Bow", "Axe", "Pickaxe" } do
		if tier.canMake[family] then
			gearRecipe(tier, family, ItemCatalog.GearId(tier.id, family), false)
		end
	end
	if tier.canMake.Armor then
		for _, slot in { "Head", "Chest", "Legs" } do
			gearRecipe(tier, slot, tier.id .. slot, true)
		end
	end
end

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
	assert(recipe.station ~= "Anywhere" or recipe.seconds == nil, "Only station recipes take time: " .. recipe.id)
	recipe.version = Recipes.VERSION
	Recipes.ById[recipe.id] = recipe
	table.insert(Recipes.List, recipe)
end

function Recipes.Get(recipeId: any)
	return type(recipeId) == "string" and Recipes.ById[recipeId] or nil
end

return Recipes
