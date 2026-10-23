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

test("unique items never merge and fill hotbar then backpack up to 9 + 50", function()
	local inv = InventoryRules.New()
	expectEq(InventoryRules.Add(inv, unique("a", "StoneSword")), 0, "first sword")
	expectEq(InventoryRules.Add(inv, unique("b", "StoneSword")), 0, "second sword")
	expectEq(InventoryRules.At(inv, "hotbar", 1).instanceId, "a", "weapon on the hotbar")
	expectEq(InventoryRules.At(inv, "hotbar", 2).instanceId, "b", "separate slot")
	for i = 3, 59 do
		expectEq(InventoryRules.Add(inv, unique("x" .. i, "StoneDagger")), 0, "fits " .. i)
	end
	expectEq(#InventoryRules.Items(inv), 59, "9 + 50 slots used")
	expectEq(InventoryRules.Add(inv, unique("overflow", "StoneDagger")), 1, "the 60th does not fit")
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
	expect(not InventoryRules.Move(inv, "hotbar", 10, "backpack", 1), "hotbar has 9 slots")
	expect(not InventoryRules.Move(inv, "backpack", 51, "hotbar", 1), "backpack has 50 slots")
	expect(not InventoryRules.Move(inv, "hotbar", 5, "hotbar", 6), "cannot move an empty slot")
	expect(not InventoryRules.Move(inv, "vault", 1, "hotbar", 1), "unknown area")
end)

test("recipes are valid, arrows make exactly 10 and advanced gear needs a workbench", function()
	for _, recipe in Recipes.List do
		expect(ItemCatalog.Get(recipe.output) ~= nil, recipe.id .. " output exists")
		expect(
			recipe.station == Recipes.Anywhere
				or recipe.station == Recipes.Workbench
				or recipe.station == Recipes.Furnace,
			recipe.id .. " station"
		)
	end
	expectEq(Recipes.Get("Arrow").quantity, 10, "10 arrows per craft")
	expectEq(Recipes.Get("WoodenSpear").station, Recipes.Anywhere, "basic spear anywhere")
	expectEq(Recipes.Get("IronSword").station, Recipes.Workbench, "iron sword needs a workbench")
	expectEq(Recipes.Get("CookedMeat").station, Recipes.Furnace, "cooking needs a furnace")
	expectEq(ItemCatalog.Get("IronSword").rarity, "Rare", "Rare Iron Sword")
	expectEq(ItemCatalog.Get("StoneSword").rarity, "Common", "Common Stone Sword")
	for id, item in ItemCatalog.Items do
		expect(Rarity.IsValid(item.rarity), id .. " has a valid rarity")
	end
end)

test("a first gear set needs only a few gathered materials", function()
	local totals = {}
	for _, id in { "WoodenSpear", "BasicBow", "Arrow", "BasicMedicine", "StoneAxe" } do
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

test("node yields depend on the tool and respawn after about 120 s", function()
	expectEq(NodeCatalog.YieldFor("Tree", nil), 1, "bare hands chop slowly")
	expectEq(NodeCatalog.YieldFor("Tree", { kind = "Axe", tier = 1 }), 3, "stone axe")
	expectEq(NodeCatalog.YieldFor("Tree", { kind = "Axe", tier = 2 }), 4, "iron axe")
	expectEq(NodeCatalog.YieldFor("IronDeposit", nil), 0, "iron needs a pickaxe")
	expectEq(NodeCatalog.YieldFor("IronDeposit", { kind = "Axe", tier = 2 }), 0, "an axe cannot mine iron")
	expectEq(NodeCatalog.YieldFor("IronDeposit", { kind = "Pickaxe", tier = 1 }), 1, "pickaxe mines iron")
	expectEq(NodeCatalog.RESPAWN_SECONDS, 120, "two-minute regrowth")
	for nodeType, node in NodeCatalog.Nodes do
		expect(ItemCatalog.Get(node.material) ~= nil, nodeType .. " yields a real item")
	end
end)
