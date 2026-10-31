-- The recipe window's model (src/shared/UI/RecipeModel.luau): forge entries from a
-- ForgeSnapshot view, field-crafting entries from the real recipes, the stepper's
-- bounds, REQUIRES costs, why the main button is off, highlighted inputs and the
-- materials lists.

local Shared = game:GetService("ReplicatedStorage").Shared
local RecipeModel = require(Shared.UI.RecipeModel)
local Recipes = require(Shared.Crafting.Recipes)
local CraftingRules = require(Shared.Crafting.CraftingRules)

local function input(id, name, owned, needed)
	return { catalogId = id, name = name, owned = owned, needed = needed }
end

local view = {
	maxBatch = 10,
	recipes = {
		{
			id = "PermanentIronSword",
			kind = "Permanent",
			category = "Permanent",
			name = "Permanent Iron Sword",
			output = "IronSword",
			quantity = 1,
			unlocked = true,
			requirement = "",
			maxCount = 1,
			inputs = { input("IronBar", "Iron Bar", 90, 60) },
			sources = { { instanceId = "s1", name = "Iron Sword", qualityRoll = 0.02 } },
		},
		{
			id = "ForgeIronPickaxe",
			kind = "Special",
			category = "Tools",
			name = "Iron Pickaxe",
			output = "IronPickaxe",
			quantity = 1,
			unlocked = true,
			requirement = "",
			maxCount = 2,
			inputs = { input("IronBar", "Iron Bar", 46, 20), input("Wood", "Wood", 34, 10) },
		},
		{
			id = "PermanentIronAxe",
			kind = "Permanent",
			category = "Permanent",
			name = "Permanent Iron Axe",
			output = "IronAxe",
			quantity = 1,
			unlocked = true,
			requirement = "",
			maxCount = 1,
			inputs = { input("IronBar", "Iron Bar", 90, 50), input("Hide", "Hide", 0, 4) },
			sources = {},
		},
		{
			id = "ForgeArrows",
			kind = "Special",
			category = "Supplies",
			name = "Flint Arrow",
			output = "FlintArrow",
			quantity = 50,
			unlocked = false,
			requirement = "Unlock: Crafting mastery 3",
			maxCount = 0,
			inputs = { input("Flint", "Flint", 0, 4) },
		},
	},
}

local function byId(entries)
	local map = {}
	for _, entry in entries do
		map[entry.id] = entry
	end
	return map
end

test("forge entries: special recipes first, then conversions for vault gear, then the rest", function()
	local entries = RecipeModel.ForgeEntries(view)
	expectEq(entries[1].id, "ForgeIronPickaxe", "special first")
	expectEq(entries[2].id, "ForgeArrows", "specials keep the server's order")
	expectEq(entries[3].id, "PermanentIronSword", "a conversion with a source next")
	expectEq(entries[4].id, "PermanentIronAxe", "conversions without one last")
	local map = byId(entries)
	expectEq(map.ForgeArrows.name, "Flint Arrow ×50", "quantity in the name")
	expect(map.ForgeArrows.locked, "unlocked == false is locked")
	expectEq(map.ForgeArrows.subtitle, "Unlock: Crafting mastery 3", "a locked row shows its unlock")
	expectEq(map.PermanentIronSword.verb, "Convert", "conversions convert")
	expectEq(map.ForgeIronPickaxe.verb, "Forge", "specials forge")
	expectEq(map.PermanentIronSword.sources[1].detail, "+2.0%", "source quality")
	expectEq(map.PermanentIronSword.name, "Iron Sword", "a conversion's row is named after the item, no prefix")
	expectEq(#RecipeModel.ForgeEntries(nil), 0, "no view, no entries")
end)

test("unlock lines read as plain English", function()
	expectEq(RecipeModel.Requirement("Unlock: extract 1 time(s), extract Iron Ore"), "Unlock: extract once, extract Iron Ore", "once")
	expectEq(RecipeModel.Requirement("Unlock: extract 3 time(s)"), "Unlock: extract 3 times", "plural")
	expectEq(RecipeModel.Requirement("Unlock: reach level 5"), "Unlock: reach level 5", "untouched")
	expectEq(RecipeModel.Requirement(nil), "", "missing")
end)

test("quantity: special recipes step up to the snapshot's maxCount; conversions and locked ones do not", function()
	local map = byId(RecipeModel.ForgeEntries(view))
	local shown, max = RecipeModel.Quantity(map.ForgeIronPickaxe)
	expect(shown, "a special recipe has a stepper")
	expectEq(max, 2, "bounded by maxCount")
	expectEq(RecipeModel.Clamp(map.ForgeIronPickaxe, 9), 2, "clamped to max")
	expectEq(RecipeModel.Clamp(map.ForgeIronPickaxe, 0), 1, "at least 1")
	shown = RecipeModel.Quantity(map.PermanentIronSword)
	expect(not shown, "no stepper for a Permanent conversion")
	shown = RecipeModel.Quantity(map.ForgeArrows)
	expect(not shown, "no stepper for a locked recipe")
	local short = table.clone(map.ForgeIronPickaxe)
	short.maxCount = 0
	shown, max = RecipeModel.Quantity(short)
	expect(shown and max == 1, "short materials still show 1")
	local missing = table.clone(view.recipes[2])
	missing.maxCount = nil
	expectEq(
		byId(RecipeModel.ForgeEntries({ maxBatch = 10, recipes = { missing } })).ForgeIronPickaxe.maxCount,
		2,
		"derived from the inputs when the snapshot has no maxCount"
	)
end)

test("cost and blockers", function()
	local map = byId(RecipeModel.ForgeEntries(view))
	local cost = RecipeModel.Cost(map.ForgeIronPickaxe, 2)
	expectEq(cost[1].need, 40, "need scales with the count")
	expect(not cost[1].short, "46 covers 40")
	expectEq(RecipeModel.Blocker(map.ForgeIronPickaxe, 2), nil, "two can be forged")
	local reason = RecipeModel.Blocker(map.ForgeIronPickaxe, 3)
	expect(reason ~= nil and string.find(reason, "Iron Bar", 1, true) ~= nil, "three are short of Iron Bar")
	expectEq(RecipeModel.Blocker(map.ForgeArrows, 1), "Unlock: Crafting mastery 3", "locked says how to unlock")
	reason = RecipeModel.Blocker(map.PermanentIronAxe, 1)
	expect(
		reason ~= nil and string.find(reason, "no Iron Axe", 1, true) ~= nil,
		"a conversion needs the item in the vault"
	)
	expectEq(RecipeModel.Blocker(map.PermanentIronSword, 1), nil, "a funded conversion with a source")
	expect(RecipeModel.Blocker(nil, 1) ~= nil, "nothing chosen")
end)

test("materials: distinct owned inputs, sorted; the chosen recipe's inputs are highlighted", function()
	local entries = RecipeModel.ForgeEntries(view)
	local materials = RecipeModel.Materials(entries)
	expectEq(#materials, 2, "Iron Bar and Wood (Hide and Flint are 0)")
	expectEq(materials[1].name, "Iron Bar", "sorted by name")
	expectEq(materials[2].quantity, 34, "vault count")
	local needed = RecipeModel.Needed(byId(entries).ForgeIronPickaxe)
	expect(needed.IronBar and needed.Wood and not needed.Hide, "inputs of the chosen recipe")
	expectEq(#RecipeModel.Filter(entries, "Tools"), 1, "category filter")
	expectEq(#RecipeModel.Filter(entries, RecipeModel.ALL), 4, "All lists everything")
end)

test("receipts and the conversion question name the item", function()
	local map = byId(RecipeModel.ForgeEntries(view))
	local title, text = RecipeModel.ForgeReceipt(map.ForgeArrows, { output = { quantity = 100 } }, 2)
	expectEq(title, "Forged", "title")
	expect(string.find(text, "×100", 1, true) ~= nil, "a stack reports what was made")
	_, text = RecipeModel.ForgeReceipt(map.ForgeIronPickaxe, { count = 2 }, 2)
	expect(string.find(text, "Iron Pickaxe ×2", 1, true) ~= nil, "a batch of gear")
	local question = RecipeModel.ConversionText(map.PermanentIronSword, map.PermanentIronSword.sources[1])
	expect(string.find(question, "Iron Sword (quality +2.0%", 1, true) ~= nil, "names the exact item")
	expect(string.find(question, "Iron Bar ×60", 1, true) ~= nil, "names the cost")
	expect(string.find(question, "cannot be undone", 1, true) ~= nil, "the Permanent rules")
end)

test("field crafting: only timed recipes take a count; stations gate the button", function()
	local carried = { Wood = 20, Stone = 20, Fiber = 20, CopperOre = 7 }
	local function count(id)
		return carried[id] or 0
	end
	local axe, bar = nil, nil
	for _, recipe in Recipes.List do
		if recipe.output == "StoneAxe" then
			axe = recipe
		elseif recipe.output == "CopperBar" then
			bar = recipe
		end
	end
	local entry = RecipeModel.CraftEntry(axe, count, {})
	local shown = RecipeModel.Quantity(entry)
	expect(not shown, "an instant recipe makes one per request")
	expectEq(entry.verb, "Craft", "crafts by hand")
	expectEq(RecipeModel.Blocker(entry, 1), nil, "affordable")
	local smelt = RecipeModel.CraftEntry(bar, count, {})
	expectEq(smelt.verb, "Need Furnace", "no furnace")
	expect(RecipeModel.Blocker(smelt, 1) ~= nil, "blocked away from a furnace")
	smelt = RecipeModel.CraftEntry(bar, count, { Furnace = true })
	local max
	shown, max = RecipeModel.Quantity(smelt)
	expect(shown, "smelting takes a count")
	expectEq(max, math.min(CraftingRules.MAX_BATCH, 7 // bar.inputs.CopperOre), "up to what the ore pays for")
	expectEq(smelt.verb, "Smelt", "smelts")
	expectEq(#RecipeModel.CraftEntries(Recipes.List, count, {}), #Recipes.List, "one entry per recipe")
end)

test("carried materials and station text", function()
	local list = RecipeModel.Carried({
		{ catalogId = "Wood", quantity = 5 },
		{ catalogId = "Wood", quantity = 7 },
		{ catalogId = "StoneAxe" },
		{ catalogId = "CopperOre", quantity = 3 },
	})
	expectEq(#list, 2, "materials only")
	expectEq(list[1].name, "Copper Ore", "sorted by name")
	expectEq(list[2].quantity, 12, "stacks summed")
	expectEq(RecipeModel.StationsText({ Furnace = true, Workbench = true }), "Workbench, Furnace", "menu order")
	expectEq(RecipeModel.StationsText({}), "None in reach", "none")
	expectEq(RecipeModel.JobText("Copper Bar", 2, 5, 6.2), "Copper Bar 2 / 5 · 7 s left", "job line")
end)
