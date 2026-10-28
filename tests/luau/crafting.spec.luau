local Shared = game:GetService("ReplicatedStorage").Shared
local InventoryRules = require(Shared.Inventory.InventoryRules)
local ItemCatalog = require(Shared.Items.ItemCatalog)
local Rarity = require(Shared.Items.Rarity)
local Recipes = require(Shared.Crafting.Recipes)
local QualityRoll = require(Shared.Crafting.QualityRoll)
local NodeCatalog = require(Shared.Resources.NodeCatalog)

local function unique(id, catalogId)
	return { instanceId = id, catalogId = catalogId, ownerId = 1, location = "Carried", qualityRoll = 0 }
end

test("one slot per stackable type, capped at its stack size", function()
	local inv = InventoryRules.New()
	expectEq(InventoryRules.Add(inv, { catalogId = "Wood", quantity = 30 }), 0, "wood added")
	expectEq(InventoryRules.Add(inv, { catalogId = "Wood", quantity = 50 }), 0, "more wood added")
	local slots = 0
	for _, entry in InventoryRules.Items(inv) do
		if entry.catalogId == "Wood" then
			slots += 1
		end
	end
	expectEq(slots, 1, "all wood in one slot")
	expectEq(InventoryRules.Count(inv, "Wood"), 80, "80 wood")
	expectEq(InventoryRules.Add(inv, { catalogId = "Wood", quantity = 1000 }), 80, "cap 1,000 leaves 80 over")
	expectEq(InventoryRules.Count(inv, "Wood"), 1000, "capped")
	expectEq(InventoryRules.At(inv, "backpack", 1).catalogId, "Wood", "materials go to the backpack first")
end)

test("unique items never merge and fill hotbar then backpack up to 6 + 50", function()
	local inv = InventoryRules.New()
	expectEq(InventoryRules.Add(inv, unique("a", "StoneSword")), 0, "first sword")
	expectEq(InventoryRules.Add(inv, unique("b", "StoneSword")), 0, "second sword")
	expectEq(InventoryRules.At(inv, "hotbar", 1).instanceId, "a", "weapon on the hotbar")
	expectEq(InventoryRules.At(inv, "hotbar", 2).instanceId, "b", "separate slot")
	for i = 3, 56 do
		expectEq(InventoryRules.Add(inv, unique("x" .. i, "StoneDagger")), 0, "fits " .. i)
	end
	expectEq(#InventoryRules.Items(inv), 56, "6 + 50 slots used")
	expectEq(InventoryRules.Add(inv, unique("overflow", "StoneDagger")), 1, "the 57th does not fit")
	expectEq(InventoryRules.Add(inv, { catalogId = "Stone", quantity = 5 }), 5, "no slot for a new stack")
end)

test("removing is all or nothing and empties the slot at zero", function()
	local inv = InventoryRules.New()
	InventoryRules.Add(inv, { catalogId = "Fiber", quantity = 5 })
	InventoryRules.Add(inv, { catalogId = "Wood", quantity = 2 })
	expect(not InventoryRules.RemoveAll(inv, { Fiber = 3, Wood = 5 }), "not enough wood")
	expectEq(InventoryRules.Count(inv, "Fiber"), 5, "nothing removed")
	expect(InventoryRules.RemoveAll(inv, { Fiber = 5, Wood = 2 }), "exact amounts")
	expectEq(#InventoryRules.Items(inv), 0, "slots emptied")
end)

test("moves swap slots and reject invalid indices", function()
	local inv = InventoryRules.New()
	InventoryRules.Add(inv, unique("s", "StoneSpear"))
	InventoryRules.Add(inv, { catalogId = "Stone", quantity = 4 })
	expect(InventoryRules.Move(inv, "hotbar", 1, "backpack", 1), "swap")
	expectEq(InventoryRules.At(inv, "backpack", 1).instanceId, "s", "spear moved")
	expectEq(InventoryRules.At(inv, "hotbar", 1).catalogId, "Stone", "stone swapped in")
	expect(not InventoryRules.Move(inv, "hotbar", 7, "backpack", 1), "hotbar has 6 slots")
	expect(not InventoryRules.Move(inv, "backpack", 51, "hotbar", 1), "backpack has 50 slots")
	expect(not InventoryRules.Move(inv, "hotbar", 5, "hotbar", 6), "cannot move an empty slot")
	expect(not InventoryRules.Move(inv, "vault", 1, "hotbar", 1), "unknown area")
end)

test("recipes are valid, arrows make exactly 10 and each tier is crafted at its own station", function()
	local stations = {
		[Recipes.Anywhere] = true,
		[Recipes.Workbench] = true,
		[Recipes.Furnace] = true,
		[Recipes.Anvil] = true,
		[Recipes.Cauldron] = true,
	}
	for _, recipe in Recipes.List do
		expect(ItemCatalog.Get(recipe.output) ~= nil, recipe.id .. " output exists")
		expect(stations[recipe.station] == true, recipe.id .. " station")
		if ItemCatalog.Get(recipe.output).family == ItemCatalog.Families.Ammo then
			expectEq(recipe.quantity, 10, recipe.id .. " makes exactly 10")
		end
	end
	expectEq(Recipes.Get("Arrow"), nil, "the plain Arrow is gone")
	expectEq(Recipes.Get("FlintArrow").quantity, 10, "10 arrows per craft")
	expect((Recipes.Get("FlintArrow").inputs.Flint or 0) > 0, "flint is the arrow tip")
	expectEq(Recipes.Get("WoodenSpear").station, Recipes.Anywhere, "basic spear anywhere")
	expectEq(Recipes.Get("IronSword").station, Recipes.Workbench, "iron sword needs a workbench")
	expectEq(Recipes.Get("CookedMeat").station, Recipes.Furnace, "cooking needs a furnace")
	-- Wood, Stone, Flint, Bone and Hide by hand; Copper, Iron and Obsidian at a
	-- Workbench; Silver and up, and Jade, at an Anvil (GDD §51).
	local tierStation = {
		Wood = Recipes.Anywhere,
		Hide = Recipes.Anywhere,
		Stone = Recipes.Anywhere,
		Flint = Recipes.Anywhere,
		Bone = Recipes.Anywhere,
		Copper = Recipes.Workbench,
		Iron = Recipes.Workbench,
		Obsidian = Recipes.Workbench,
		Silver = Recipes.Anvil,
		Cobalt = Recipes.Anvil,
		Jade = Recipes.Anvil,
		Mithril = Recipes.Anvil,
		Adamantine = Recipes.Anvil,
	}
	local gearRecipes = 0
	for _, recipe in Recipes.List do
		local def = ItemCatalog.Get(recipe.output)
		if def.tier then
			gearRecipes += 1
			expectEq(recipe.station, tierStation[def.tier], recipe.id .. " station")
		end
	end
	expect(gearRecipes > 0, "gear recipes come from the ladder")
	expectEq(Recipes.Get("SilverSword").station, Recipes.Anvil, "silver needs an anvil")
	expectEq(Recipes.Get("JadeDagger").station, Recipes.Anvil, "jade needs an anvil")
	expectEq(Recipes.Get("ObsidianSpear").station, Recipes.Workbench, "obsidian at a workbench")
	-- Potions and draughts brew at a Cauldron.
	for _, id in
		{
			"Potion",
			"GreaterPotion",
			"HeartyTonic",
			"SunberryDraught",
			"StrongSunberryDraught",
			"GlimmerDraught",
			"StrongGlimmerDraught",
		}
	do
		expectEq(Recipes.Get(id).station, Recipes.Cauldron, id .. " brews at a cauldron")
	end
	expectEq(Recipes.Get("Potion").inputs.Redberry, 5, "a Healing Potion is brewed from Redberries")
	-- Rarity rises slowly with tier; Legendary and above stay for boss and event drops.
	expectEq(ItemCatalog.Get("IronSword").rarity, "Common", "Common Iron Sword")
	expectEq(ItemCatalog.Get("StoneSword").rarity, "Common", "Common Stone Sword")
	expectEq(ItemCatalog.Get("SilverSword").rarity, "Uncommon", "Uncommon Silver Sword")
	expectEq(ItemCatalog.Get("MithrilSword").rarity, "Rare", "Rare Mithril Sword")
	expectEq(ItemCatalog.Get("AdamantineSword").rarity, "Epic", "Epic Adamantine Sword")
	for id, item in ItemCatalog.Items do
		expect(Rarity.IsValid(item.rarity), id .. " has a valid rarity")
	end
	for _, recipe in Recipes.List do
		expect(
			Rarity.Index(ItemCatalog.Get(recipe.output).rarity) < Rarity.Index("Legendary"),
			recipe.id .. " is below Legendary"
		)
	end
end)

test("ores smelt 1:1 into bars at a furnace, costing only time", function()
	local seconds = { Copper = 2, Iron = 3, Silver = 4, Cobalt = 5, Mithril = 6, Adamantine = 8 }
	for metal, time in seconds do
		local recipe = Recipes.Get(metal .. "Bar")
		expectEq(recipe.station, Recipes.Furnace, metal .. " smelts at a furnace")
		expectEq(recipe.quantity, 1, "one " .. metal .. " bar")
		expectEq(recipe.seconds, time, metal .. " smelt time")
		local inputs = 0
		for input, amount in recipe.inputs do
			inputs += 1
			expectEq(input, metal .. "Ore", metal .. " bar is made from its ore")
			expectEq(amount, 1, "one " .. metal .. " ore")
		end
		expectEq(inputs, 1, metal .. " needs no fuel")
		expect(ItemCatalog.IsMaterial(metal .. "Ore"), metal .. " ore is a material")
	end
	expectEq(ItemCatalog.Get("Iron"), nil, "the old Iron material is gone")
	for _, recipe in Recipes.List do
		if recipe.station == Recipes.Anywhere then
			expectEq(recipe.seconds, nil, recipe.id .. " by hand takes no time")
		end
	end
end)

test("gem-class materials make only daggers and spears; sickles and Wood/Stone armor are gone", function()
	for _, gem in { "Flint", "Obsidian", "Jade" } do
		expect(Recipes.Get(gem .. "Spear") ~= nil, gem .. " makes a spear")
		expect(Recipes.Get(gem .. "Dagger") ~= nil, gem .. " makes a dagger")
		for _, family in { "Sword", "Bow", "Axe", "Pickaxe", "Head", "Chest", "Legs" } do
			expectEq(ItemCatalog.Get(gem .. family), nil, gem .. " makes no " .. family)
		end
	end
	for _, recipe in Recipes.List do
		local def = ItemCatalog.Get(recipe.output)
		local family = def.weapon and def.weapon.family
		for _, gem in { "Obsidian", "Jade" } do
			if (recipe.inputs[gem] or 0) > 0 then
				expect(family == "Spear" or family == "Dagger", recipe.id .. " uses " .. gem)
			end
		end
		if (recipe.inputs.Flint or 0) > 0 then
			expect(
				family == "Spear" or family == "Dagger" or def.family == ItemCatalog.Families.Ammo,
				recipe.id .. " uses Flint"
			)
		end
	end
	-- Bone makes armor, daggers and spears only.
	for _, id in { "BoneSpear", "BoneDagger", "BoneHead", "BoneChest", "BoneLegs" } do
		expect(Recipes.Get(id) ~= nil, id .. " is craftable")
	end
	expectEq(ItemCatalog.Get("BoneSword"), nil, "no bone sword")
	for id, item in ItemCatalog.Items do
		expect(not string.find(id, "Sickle"), id .. " is not a sickle")
		expect(item.tool == nil or item.tool.kind == "Axe" or item.tool.kind == "Pickaxe", id .. " tool kind")
	end
	for _, id in { "WoodHead", "WoodChest", "WoodLegs", "StoneHead", "StoneChest", "StoneLegs" } do
		expectEq(ItemCatalog.Get(id), nil, id .. " is removed")
	end
	-- Axes and pickaxes exist at every tier from Wood to Adamantine.
	for _, tier in { "Wooden", "Stone", "Copper", "Iron", "Silver", "Cobalt", "Mithril", "Adamantine" } do
		expect(Recipes.Get(tier .. "Axe") ~= nil, tier .. " axe")
		expect(Recipes.Get(tier .. "Pickaxe") ~= nil, tier .. " pickaxe")
	end
end)

test("a first gear set needs only a few gathered materials", function()
	local totals = {}
	for _, id in { "WoodenSpear", "WoodenBow", "FlintArrow", "BasicMedicine", "StoneAxe" } do
		for input, amount in Recipes.Get(id).inputs do
			totals[input] = (totals[input] or 0) + amount
		end
	end
	local sum = 0
	for _, amount in totals do
		sum += amount
	end
	expect(sum <= 60, "starter set costs " .. sum .. " materials")
end)

test("quality rolls stay within ±5% and only world workbenches roll", function()
	local rng = Random.new(3)
	for _ = 1, 2000 do
		local roll = QualityRoll.Roll(rng, QualityRoll.Stations.WorldWorkbench, 10)
		expect(roll >= -0.05 and roll <= 0.05, "within ±5%")
	end
	expectEq(QualityRoll.Roll(rng, QualityRoll.Stations.Anywhere, 10), 0, "anywhere crafts are default")
	expectEq(QualityRoll.Roll(rng, QualityRoll.Stations.LobbyWorkbench, 10), 0, "lobby workbench is default")
end)

test("the best roll chance grows 5% relative per Crafting mastery level", function()
	local function bestRate(level)
		local rng = Random.new(11)
		local best = 0
		local trials = 200000
		for _ = 1, trials do
			if QualityRoll.Roll(rng, QualityRoll.Stations.WorldWorkbench, level, 0.1) == 0.05 then
				best += 1
			end
		end
		return best / trials
	end
	expectNear(bestRate(0), 0.1, 0.005, "base 10% chance")
	expectNear(bestRate(10), 0.15, 0.005, "level 10 gives 1.5x")
end)

test("node drops per hit depend on the tool; basic nodes regrow after 120 s", function()
	local function tool(catalogId)
		return ItemCatalog.Get(catalogId).tool
	end
	expectEq(NodeCatalog.YieldFor("Tree", nil), 1, "bare hands chop slowly")
	expectEq(NodeCatalog.YieldFor("Rock", nil), 1, "bare hands mine slowly")
	-- Axe on trees and pickaxe on rock: 1 + tool rank (GDD §53), Wood 2 to Adamantine 9.
	local ladder = { Wooden = 2, Stone = 3, Copper = 4, Iron = 5, Silver = 6, Cobalt = 7, Mithril = 8, Adamantine = 9 }
	for tier, amount in ladder do
		expectEq(NodeCatalog.YieldFor("Tree", tool(tier .. "Axe")), amount, tier .. " axe")
		expectEq(NodeCatalog.YieldFor("Rock", tool(tier .. "Pickaxe")), amount, tier .. " pickaxe")
	end
	expectEq(NodeCatalog.YieldFor("IronDeposit", nil), 0, "iron needs a pickaxe")
	expectEq(NodeCatalog.YieldFor("IronDeposit", tool("IronAxe")), 0, "an axe cannot mine iron")
	expectEq(NodeCatalog.YieldFor("IronDeposit", tool("StonePickaxe")), 0, "a stone pickaxe cannot mine iron")
	expectEq(NodeCatalog.YieldFor("IronDeposit", tool("CopperPickaxe")), 1, "a copper pickaxe mines iron")
	expectEq(NodeCatalog.YieldFor("IronDeposit", tool("IronPickaxe")), 2, "+1 per tier above the minimum")
	expectEq(NodeCatalog.Nodes.IronDeposit.material, "IronOre", "iron deposits give ore")
	-- Each ore and gem needs the previous tier's pickaxe.
	local gates = {
		CopperDeposit = "Stone",
		IronDeposit = "Copper",
		SilverDeposit = "Iron",
		CobaltDeposit = "Silver",
		MithrilDeposit = "Cobalt",
		ObsidianOutcrop = "Iron",
		JadeVein = "Cobalt",
	}
	local order = { "Wooden", "Stone", "Copper", "Iron", "Silver", "Cobalt", "Mithril", "Adamantine" }
	for nodeType, needed in gates do
		local rank = table.find(order, needed)
		expectEq(NodeCatalog.YieldFor(nodeType, tool(needed .. "Pickaxe")), 1, nodeType .. " opens at " .. needed)
		expectEq(NodeCatalog.YieldFor(nodeType, tool(order[rank - 1] .. "Pickaxe")), 0, nodeType .. " gated")
	end
	-- Sickles are gone: plants are gathered by hand, and no tool changes that.
	for _, nodeType in { "FiberPlant", "HerbShrub", "RedberryBush", "SweetberryBush" } do
		expectEq(NodeCatalog.YieldFor(nodeType, nil), 1, nodeType .. " gives 1 per hit by hand")
		expectEq(NodeCatalog.YieldFor(nodeType, tool("IronAxe")), 1, nodeType .. " ignores tools")
		expectEq(NodeCatalog.RegrowSeconds(nodeType), 120, nodeType .. " two-minute regrowth")
	end
	expectEq(NodeCatalog.Nodes.BerryBush, nil, "plain berry bushes are gone")
	for nodeType, node in NodeCatalog.Nodes do
		expect(ItemCatalog.Get(node.material) ~= nil, nodeType .. " yields a real item")
	end
end)
