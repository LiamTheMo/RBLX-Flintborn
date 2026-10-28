-- Gathering by node health and ground drops (GDD §53).
local Shared = game:GetService("ReplicatedStorage").Shared
local BiomeCatalog = require(Shared.World.BiomeCatalog)
local BossCatalog = require(Shared.Bosses.BossCatalog)
local EnemyCatalog = require(Shared.Enemies.EnemyCatalog)
local GameConstants = require(Shared.GameConstants)
local GroundDrops = require(Shared.Resources.GroundDrops)
local ItemCatalog = require(Shared.Items.ItemCatalog)
local MasteryCatalog = require(Shared.Progression.MasteryCatalog)
local NodeCatalog = require(Shared.Resources.NodeCatalog)
local ShopCatalog = require(Shared.Economy.ShopCatalog)
local StructureCatalog = require(Shared.Building.StructureCatalog)
local Tiers = require(Shared.Items.Tiers)
local TradeRules = require(Shared.Economy.TradeRules)

local LADDER = { "Wood", "Stone", "Copper", "Iron", "Silver", "Cobalt", "Mithril", "Adamantine" }

local function tool(tierId: string, kind: string)
	local item = ItemCatalog.Get(ItemCatalog.GearId(tierId, kind))
	assert(item and item.tool, "no " .. tierId .. " " .. kind)
	return item.tool
end

-- Hits a fresh node until it is empty; returns the hits taken and the material dropped.
local function empty(nodeType: string, held, extraChance: number?, rng)
	local health, hits, material = NodeCatalog.Health(nodeType), 0, 0
	while health > 0 do
		local hit = NodeCatalog.Hit(nodeType, health, held, extraChance, rng)
		assert(hit, nodeType .. " refused a hit")
		expectEq(hit.health, health - hit.removed, nodeType .. " loses what it dropped")
		expectEq(hit.depleted, hit.health <= 0, nodeType .. " depletes at zero")
		health = hit.health
		hits += 1
		material += hit.stacks[1].quantity
		expect(hits <= 100, nodeType .. " empties")
	end
	return hits, material
end

test("drops per hit are 1 + max(0, tool rank - node rank)", function()
	expectEq(NodeCatalog.Rank("Tree"), 0, "trees are rank 0")
	expectEq(NodeCatalog.Rank("Rock"), 0, "rocks are rank 0")
	for index, tierId in LADDER do
		expectEq(NodeCatalog.YieldFor("Tree", tool(tierId, "Axe")), 1 + index, tierId .. " axe")
		expectEq(NodeCatalog.YieldFor("Rock", tool(tierId, "Pickaxe")), 1 + index, tierId .. " pickaxe")
		expectEq(NodeCatalog.YieldFor("Tree", tool(tierId, "Pickaxe")), 1, tierId .. " pickaxe on a tree is hands")
	end
	expectEq(NodeCatalog.YieldFor("Tree", nil), 1, "bare hands")
	expectEq(NodeCatalog.YieldFor("Tree", tool("Wood", "Axe")), 2, "Wooden axe 2")
	expectEq(NodeCatalog.YieldFor("Rock", tool("Stone", "Pickaxe")), 3, "Stone pickaxe 3")
	for nodeType, node in NodeCatalog.Nodes do
		if node.minRank then
			expectEq(NodeCatalog.Rank(nodeType), node.minRank, nodeType .. " rank is its gate")
			for rank = node.minRank, #LADDER do
				local drops = NodeCatalog.YieldFor(nodeType, tool(LADDER[rank], "Pickaxe"))
				expectEq(drops, 1 + rank - node.minRank, nodeType .. " with a rank " .. rank .. " pickaxe")
			end
		end
	end
end)

test("ores still need their pickaxe; hands and axes can't mine them", function()
	local rng = Random.new(3)
	for nodeType, node in NodeCatalog.Nodes do
		if node.minRank then
			local health = NodeCatalog.Health(nodeType)
			expectEq(NodeCatalog.Hit(nodeType, health, nil, 1, rng), nil, nodeType .. " by hand")
			expectEq(NodeCatalog.Hit(nodeType, health, tool("Adamantine", "Axe"), 1, rng), nil, nodeType .. " axe")
			if node.minRank > 1 then
				local below = tool(LADDER[node.minRank - 1], "Pickaxe")
				expectEq(NodeCatalog.Hit(nodeType, health, below, 1, rng), nil, nodeType .. " one tier below")
			end
			expect(NodeCatalog.Hit(nodeType, health, tool(LADDER[node.minRank], "Pickaxe"), 0, rng), nodeType)
		end
	end
	expectEq(NodeCatalog.Nodes.AdamantineDeposit, nil, "Adamantine stays event-only")
	for _, node in NodeCatalog.Nodes do
		expect(node.material ~= "AdamantineOre", "no node gives Adamantine Ore")
	end
end)

test("a node's total is its health whatever the tool; the last hit drops only what is left", function()
	local rng = Random.new(5)
	for nodeType in NodeCatalog.Nodes do
		local health = NodeCatalog.Health(nodeType)
		-- `false` stands for bare hands.
		local held: { any } = { false }
		local node = NodeCatalog.Nodes[nodeType]
		if node.minRank then
			held = { tool(LADDER[node.minRank], "Pickaxe"), tool("Adamantine", "Pickaxe") }
		elseif node.tool then
			held = { false, tool("Wood", node.tool), tool("Stone", node.tool), tool("Adamantine", node.tool) }
		end
		for _, entry in held do
			local equipped = if entry then entry else nil
			local perHit = NodeCatalog.YieldFor(nodeType, equipped)
			local hits, material = empty(nodeType, equipped, 0, rng)
			expectEq(material, health, nodeType .. " gives exactly its health")
			expectEq(hits, math.ceil(health / perHit), nodeType .. " hits at " .. perHit .. " per hit")
		end
	end
	-- A Stone pickaxe (3) on a rock with 2 left drops 2 and finishes it.
	local last = NodeCatalog.Hit("Rock", 2, tool("Stone", "Pickaxe"), 0, rng)
	expectEq(last.removed, 2, "clamped to what is left")
	expectEq(last.stacks[1].quantity, 2, "drops what is left")
	expect(last.depleted, "the rock is finished")
	-- Hands take a tree in 12 hits, a Wooden axe in 6, a Stone axe in 4.
	expectEq((empty("Tree", nil, 0, rng)), 12, "hands")
	expectEq((empty("Tree", tool("Wood", "Axe"), 0, rng)), 6, "Wooden axe")
	expectEq((empty("Tree", tool("Stone", "Axe"), 0, rng)), 4, "Stone axe")
end)

test("node health follows the placeholders", function()
	local expected = {
		Tree = 12,
		Rock = 12,
		FiberPlant = 3,
		HerbShrub = 3,
		RedberryBush = 3,
		SweetberryBush = 3,
		CopperDeposit = 8,
		IronDeposit = 8,
		SilverDeposit = 8,
		CobaltDeposit = 8,
		MithrilDeposit = 6,
		ObsidianOutcrop = 5,
		JadeVein = 5,
	}
	for nodeType, node in NodeCatalog.Nodes do
		expectEq(node.health, expected[nodeType] or 4, nodeType .. " health")
	end
end)

test("mastery's extra drop is a per-hit chance that costs no health", function()
	local rng = Random.new(7)
	local always = NodeCatalog.Hit("Tree", 12, tool("Stone", "Axe"), 1, rng)
	expectEq(always.removed, 3, "the hit still removes 3")
	expectEq(always.health, 9, "health ignores the extra")
	expectEq(always.stacks[1].quantity, 4, "one extra Wood")
	local hits, material = empty("Rock", nil, 1, rng)
	expectEq(hits, 12, "the extra never shortens a node")
	expectEq(material, 24, "one extra per hit")
	-- Level 10 is a 10% chance per hit.
	local level10 = 0
	for _, buff in MasteryCatalog.Buffs("Mining", 10) do
		level10 += if buff.stat == "MiningYield" then buff.value else 0
	end
	expectNear(level10, 10 * GameConstants.MASTERY_YIELD_PER_LEVEL, 1e-9, "1% per level")
	local extras, trials = 0, 40000
	for _ = 1, trials do
		local hit = NodeCatalog.Hit("FiberPlant", 3, nil, level10, rng)
		extras += hit.stacks[1].quantity - hit.removed
	end
	expectNear(extras / trials, 0.10, 0.01, "10% at level 10")
end)

test("Flint and Resin still drop from rocks and trees, Flint also when a rock is finished", function()
	local rng = Random.new(11)
	local function count(stacks, catalogId: string): number
		local total = 0
		for _, stack in stacks do
			total += if stack.catalogId == catalogId then stack.quantity else 0
		end
		return total
	end
	local resin, flint, trials = 0, 0, 40000
	for _ = 1, trials do
		resin += count(NodeCatalog.Hit("Tree", 12, nil, 0, rng).stacks, "Resin")
		flint += count(NodeCatalog.Hit("Rock", 12, nil, 0, rng).stacks, "Flint")
	end
	expectNear(resin / trials, 0.10, 0.01, "Resin 10% per hit")
	expectNear(flint / trials, 0.15, 0.01, "Flint 15% per hit")
	for _ = 1, 200 do
		local finish = NodeCatalog.Hit("Rock", 1, nil, 0, rng)
		expect(finish.depleted and count(finish.stacks, "Flint") >= 1, "a finished rock drops Flint")
		expectEq(finish.removed, 1, "bonus Flint uses no health")
	end
	expectEq(NodeCatalog.Hit("Tree", 12, nil, 0, Random.new(1)).stacks[1].catalogId, "Wood", "material first")
end)

test("nodes regrow by tier", function()
	local expected = {
		Tree = 120,
		Rock = 120,
		FiberPlant = 120,
		HerbShrub = 120,
		RedberryBush = 120,
		SweetberryBush = 120,
		CopperDeposit = 180,
		IronDeposit = 180,
		SilverDeposit = 300,
		CobaltDeposit = 300,
		ObsidianOutcrop = 300,
		JadeVein = 480,
		MithrilDeposit = 480,
		AmethystGeode = 300,
		StarstoneOutcrop = 480,
		StormglassCluster = 480,
	}
	for nodeType in NodeCatalog.Nodes do
		expectEq(NodeCatalog.RegrowSeconds(nodeType), expected[nodeType] or 120, nodeType .. " regrowth")
	end
end)

test("only the hitter may take a ground drop for 10 s; it lasts 2 minutes", function()
	expectEq(GroundDrops.OWNER_SECONDS, 10, "10 s owner window")
	expectEq(GroundDrops.LIFETIME_SECONDS, 120, "2 minute life")
	local rules = GroundDrops.New(7, 100)
	expect(GroundDrops.CanClaim(rules, 7, 2, 100), "the hitter at once")
	local ok, reason = GroundDrops.CanClaim(rules, 8, 2, 109.9)
	expect(not ok and reason == "NotYours", "someone else inside the window")
	expect(GroundDrops.CanClaim(rules, 8, 2, 110), "anyone after 10 s")
	ok, reason = GroundDrops.CanClaim(rules, 7, GroundDrops.PICKUP_RANGE + 0.5, 101)
	expect(not ok and reason == "TooFar", "out of reach")
	expect(GroundDrops.CanClaim(rules, 7, GroundDrops.PICKUP_RANGE, 101), "at the edge of reach")
	expect(not GroundDrops.Expired(rules, 219.9), "still there just before 2 minutes")
	expect(GroundDrops.Expired(rules, 220), "gone after 2 minutes")
	ok, reason = GroundDrops.CanClaim(rules, 7, 1, 220)
	expect(not ok and reason == "Expired", "an expired drop can't be taken")
end)

test("every zone has the basics; new nodes sit in fitting zones (GDD §53, §54)", function()
	local basics = { "Tree", "Rock", "FiberPlant", "HerbShrub", "RedberryBush", "SweetberryBush" }
	for name, zone in BiomeCatalog.Zones do
		for _, nodeType in basics do
			expect((zone.resources[nodeType] or 0) > 0, name .. " has " .. nodeType)
		end
	end
	-- Fewer basics deeper in: every Extreme zone has fewer trees than any Low zone.
	for _, deep in BiomeCatalog.ZonesIn("CenterCrater") do
		for _, outer in BiomeCatalog.ZonesIn("OuterRim") do
			expect(
				BiomeCatalog.Zones[deep].resources.Tree < BiomeCatalog.Zones[outer].resources.Tree,
				deep .. " has fewer trees than " .. outer
			)
		end
	end
	local homes = {
		ClayDeposit = { Rimlands = true, MosswickForest = true, Riverlands = true, CraterLake = true },
		AmethystGeode = { EmberhollowCaves = true, FallenTemple = true },
		StarstoneOutcrop = { FrostpeakRidge = true, CraterLake = true, ShatteredKeep = true },
		StormglassCluster = { FrostpeakRidge = true, CraterLake = true },
		FrostShrub = { FrostpeakRidge = true },
		CaveMushroomPatch = { PinewoodWilds = true, MosswickForest = true, EmberhollowCaves = true },
		RedcapMushroomPatch = { MosswickForest = true, Timberwatch = true, FallenTemple = true },
		ChestnutMushroomPatch = { PinewoodWilds = true, MosswickForest = true, Timberwatch = true },
	}
	for nodeType, allowed in homes do
		local found = 0
		for name, zone in BiomeCatalog.Zones do
			if zone.resources[nodeType] then
				found += 1
				expect(allowed[name], nodeType .. " does not belong in " .. name)
			end
		end
		expect(found > 0, nodeType .. " is placed")
	end
end)

test("the new materials are bankable, sellable and never traded", function()
	local new = {
		Clay = "ClayDeposit",
		Amethyst = "AmethystGeode",
		Starstone = "StarstoneOutcrop",
		Stormglass = "StormglassCluster",
		CaveMushroom = "CaveMushroomPatch",
		RedcapMushroom = "RedcapMushroomPatch",
		ChestnutMushroom = "ChestnutMushroomPatch",
		Thornvine = "ThornShrub",
		Frostleaf = "FrostShrub",
		JuniperBerry = "JuniperShrub",
		Elderberry = "ElderberryShrub",
		Raspberry = "RaspberryBush",
		Hazelnut = "HazelShrub",
	}
	for catalogId, nodeType in new do
		local item = ItemCatalog.Get(catalogId)
		expect(item ~= nil, catalogId .. " exists")
		expect(ItemCatalog.IsMaterial(catalogId), catalogId .. " is a bankable material")
		expect((ShopCatalog.SellValue(catalogId) or 0) > 0, catalogId .. " sells")
		expect(not TradeRules.IsTradeableMaterial(catalogId), catalogId .. " never trades")
		expectEq(NodeCatalog.Nodes[nodeType].material, catalogId, nodeType .. " gives " .. catalogId)
	end
	expectEq(ItemCatalog.Get("Amethyst").rarity, "Uncommon", "Amethyst is Uncommon")
	expectEq(ItemCatalog.Get("Starstone").rarity, "Rare", "Starstone is Rare")
	expectEq(ItemCatalog.Get("Stormglass").rarity, "Rare", "Stormglass is Rare")
	expectEq(NodeCatalog.Rank("AmethystGeode"), Tiers.ToolRank.Iron, "Amethyst needs an Iron pickaxe")
	expectEq(NodeCatalog.Rank("StarstoneOutcrop"), Tiers.ToolRank.Cobalt, "Starstone needs a Cobalt pickaxe")
	expectEq(NodeCatalog.Rank("StormglassCluster"), Tiers.ToolRank.Cobalt, "Stormglass needs a Cobalt pickaxe")
	for catalogId, nodeType in new do
		if catalogId ~= "Clay" and NodeCatalog.Nodes[nodeType].minRank == nil then
			expectEq(NodeCatalog.Nodes[nodeType].tool, nil, nodeType .. " is hand-gathered")
		end
	end
end)

test("creatures drop ore by where they live (GDD §54)", function()
	local function ores(drops)
		local found = {}
		for _, row in drops do
			if row[1]:match("Ore$") then
				found[row[1]] = row
			end
		end
		return found
	end
	-- Animals never drop ore, except the Stonehide Rhino's little iron.
	for enemyId, enemy in EnemyCatalog.Enemies do
		if (enemy.theme == "Primitive" or enemy.theme == "Ancient") and enemyId ~= "StonehideRhino" then
			expect(next(ores(enemy.drops)) == nil, enemyId .. " drops no ore")
		end
	end
	expect(next(ores(EnemyCatalog.Get("EmberWisp").drops)) == nil, "Ember Wisps drop no ore")
	local rhino = ores(EnemyCatalog.Get("StonehideRhino").drops)
	expect(rhino.IronOre and next(rhino, next(rhino)) == nil, "the Rhino drops only iron")
	expect(rhino.IronOre[3] <= 5, "a little iron")
	local skeleton = ores(EnemyCatalog.Get("Skeleton").drops)
	expect(skeleton.CopperOre and skeleton.IronOre, "Skeletons carry copper and iron")
	expect(skeleton.SilverOre == nil, "no silver on Fallen Temple Skeletons")
	local keep = ores(EnemyCatalog.Get("KeepSkeleton").drops)
	expect(keep.CopperOre and keep.IronOre and keep.SilverOre, "Keep Skeletons add silver")
	expectEq(EnemyCatalog.Get("Bandit"), nil, "Bandits are gone")
	local minotaur = ores(BossCatalog.Get("Minotaur").loot)
	expect(minotaur.SilverOre and minotaur.CobaltOre, "the Minotaur hoards silver and cobalt")
	expect(minotaur.IronOre == nil, "no more iron from the Minotaur")
	expect(minotaur.SilverOre[2] + minotaur.CobaltOre[2] >= 10, "in bulk")
	local gorilla = ores(BossCatalog.Get("CraterGorilla").loot)
	expect(gorilla.SilverOre and gorilla.CobaltOre, "the Crater Gorilla drops silver and cobalt")
end)

test("Fiber is a planter crop; the rare berries stay wild", function()
	local fiber = StructureCatalog.Crops.Fiber
	expect(fiber ~= nil and table.find(StructureCatalog.CROP_ORDER, "Fiber") ~= nil, "planters grow Fiber")
	expectEq(fiber.yield.catalogId, "Fiber", "it yields Fiber")
	expect(fiber.yield.quantity > (fiber.seed.Fiber or 0), "it grows more than it costs")
	for _, crop in StructureCatalog.Crops do
		expect(crop.yield.catalogId ~= "Sunberry" and crop.yield.catalogId ~= "Glimmerberry", "rare berries are wild")
	end
end)
