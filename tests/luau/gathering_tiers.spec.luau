local Shared = game:GetService("ReplicatedStorage").Shared
local BiomeCatalog = require(Shared.World.BiomeCatalog)
local EventCatalog = require(Shared.Events.EventCatalog)
local EventRules = require(Shared.Events.EventRules)
local ItemCatalog = require(Shared.Items.ItemCatalog)
local NodeCatalog = require(Shared.Resources.NodeCatalog)
local Rarity = require(Shared.Items.Rarity)
local Tiers = require(Shared.Items.Tiers)

local LADDER = { "Wood", "Stone", "Copper", "Iron", "Silver", "Cobalt", "Mithril", "Adamantine" }

-- The real tool definition a player would hold.
local function tool(tierId: string, kind: string)
	local item = ItemCatalog.Get(ItemCatalog.GearId(tierId, kind))
	assert(item and item.tool, "no " .. tierId .. " " .. kind)
	return item.tool
end

test("plants are gathered by hand at the old sickle rate, whatever is held", function()
	local rates = { FiberPlant = 3, HerbShrub = 2, RedberryBush = 2, SweetberryBush = 2 }
	for nodeType, rate in rates do
		expectEq(NodeCatalog.YieldFor(nodeType, nil), rate, nodeType .. " by hand")
		expectEq(NodeCatalog.YieldFor(nodeType, tool("Mithril", "Axe")), rate, nodeType .. " with an axe")
		expect(NodeCatalog.GateNotice(nodeType, nil) == nil, nodeType .. " has no gate")
	end
	for _, item in ItemCatalog.Items do
		expect(item.tool == nil or item.tool.kind ~= "Sickle", item.id .. " is not a sickle")
	end
end)

test("axes on trees and pickaxes on rock follow the §4.3 curve; bare hands gather 1", function()
	local expected = { 2, 3, 4, 5, 6, 7, 9, 11 }
	for index, tierId in LADDER do
		expectEq(NodeCatalog.YieldFor("Tree", tool(tierId, "Axe")), expected[index], tierId .. " axe on a tree")
		expectEq(NodeCatalog.YieldFor("Rock", tool(tierId, "Pickaxe")), expected[index], tierId .. " pickaxe on rock")
	end
	expectEq(NodeCatalog.YieldFor("Tree", nil), 1, "bare hands chop")
	expectEq(NodeCatalog.YieldFor("Rock", nil), 1, "bare hands quarry")
	expectEq(NodeCatalog.YieldFor("Tree", tool("Adamantine", "Pickaxe")), 1, "the wrong tool is bare hands")
end)

test("each ore and gem needs the pickaxe the catalog names", function()
	local needs = {
		CopperOre = "Stone",
		IronOre = "Copper",
		SilverOre = "Iron",
		CobaltOre = "Silver",
		MithrilOre = "Cobalt",
		AdamantineOre = "Mithril",
		Obsidian = "Iron",
		Jade = "Cobalt",
	}
	for material, tierId in needs do
		expectEq(NodeCatalog.MineRanks[material], Tiers.ToolRank[tierId], material .. " gate")
	end
	expectEq(NodeCatalog.MineRanks.Stone, nil, "rock is not gated")
	expectEq(NodeCatalog.MineRanks.Flint, nil, "flint is not gated")
end)

test("mining below the gate gives nothing and names the pickaxe needed", function()
	for nodeType, node in NodeCatalog.Nodes do
		if node.minRank then
			local needed = LADDER[node.minRank]
			local message = ("Needs a %s Pickaxe or better"):format(needed)
			expectEq(NodeCatalog.YieldFor(nodeType, nil), 0, nodeType .. " by hand")
			expectEq(NodeCatalog.GateNotice(nodeType, nil), message, nodeType .. " notice by hand")
			expectEq(NodeCatalog.YieldFor(nodeType, tool("Adamantine", "Axe")), 0, nodeType .. " with an axe")
			if node.minRank > 1 then
				local below = tool(LADDER[node.minRank - 1], "Pickaxe")
				expect(not NodeCatalog.CanHarvest(nodeType, below), nodeType .. " one tier below")
				expectEq(NodeCatalog.GateNotice(nodeType, below), message, nodeType .. " notice one tier below")
			end
			for rank = node.minRank, #LADDER do
				local pickaxe = tool(LADDER[rank], "Pickaxe")
				expectEq(NodeCatalog.YieldFor(nodeType, pickaxe), 1 + rank - node.minRank, nodeType .. " at " .. rank)
				expectEq(NodeCatalog.GateNotice(nodeType, pickaxe), nil, nodeType .. " no notice at " .. rank)
			end
		end
	end
	expectEq(NodeCatalog.GateNotice("IronDeposit", nil), "Needs a Copper Pickaxe or better", "the spec's example")
end)

test("trees drop Resin and rocks Flint per hit; the finishing hit on rock adds Flint", function()
	local rng = Random.new(41)
	local function rate(nodeType: string, catalogId: string, trials: number)
		local hits = 0
		for _ = 1, trials do
			for _, extra in NodeCatalog.Extras(nodeType, false, rng) do
				if extra.catalogId == catalogId then
					hits += extra.quantity
				end
			end
		end
		return hits / trials
	end
	expectNear(rate("Tree", "Resin", 40000), 0.10, 0.01, "Resin 10% per hit")
	expectNear(rate("Rock", "Flint", 40000), 0.15, 0.01, "Flint 15% per hit")
	expectEq(rate("FiberPlant", "Fiber", 1000), 0, "plants give no extras")
	local finished = 0
	for _ = 1, 1000 do
		for _, extra in NodeCatalog.Extras("Rock", true, rng) do
			finished += if extra.catalogId == "Flint" then extra.quantity else 0
		end
	end
	expect(finished >= 1000, "every finished rock gives at least one Flint")
	for _, extra in NodeCatalog.Extras("Tree", true, Random.new(1)) do
		expectEq(extra.catalogId, "Resin", "a finished tree only has the per-hit roll")
	end
	for nodeType, node in NodeCatalog.Nodes do
		for _, bonus in { node.bonus, node.finishBonus } do
			expect(ItemCatalog.Get(bonus.catalogId) ~= nil, nodeType .. " bonus " .. bonus.catalogId)
		end
	end
end)

test("every node type spawns in its region with its own look", function()
	local regions = {
		CopperDeposit = "OuterRim",
		IronDeposit = "OuterRim",
		SilverDeposit = "InnerRing",
		CobaltDeposit = "InnerRing",
		ObsidianOutcrop = "InnerRing",
		JadeVein = "InnerRing",
		MithrilDeposit = "CenterCrater",
	}
	local placed, seenLooks = {}, {}
	for name, biome in BiomeCatalog.Biomes do
		for nodeType, count in biome.resources do
			expect(count > 0, name .. " " .. nodeType .. " count")
			placed[nodeType] = true
			if regions[nodeType] then
				expectEq(biome.region, regions[nodeType], nodeType .. " in " .. name)
			end
		end
	end
	for nodeType, node in NodeCatalog.Nodes do
		expect(ItemCatalog.Get(node.material) ~= nil, nodeType .. " yields a real item")
		expect(placed[nodeType], nodeType .. " is placed in some biome")
		local look = NodeCatalog.Looks[nodeType]
		expect(look ~= nil, nodeType .. " has a look")
		if look then
			local key = table.concat({
				tostring(look.shape),
				tostring(look.material),
				("%.3f,%.3f,%.3f"):format(look.color.R, look.color.G, look.color.B),
			}, "|")
			expect(seenLooks[key] == nil, nodeType .. " looks like " .. tostring(seenLooks[key]))
			seenLooks[key] = nodeType
		end
	end
	for nodeType in NodeCatalog.Looks do
		expect(NodeCatalog.Nodes[nodeType] ~= nil, "look for a real node " .. nodeType)
	end
end)

test("meteor chunks give Adamantine Ore and need a Mithril Pickaxe", function()
	local meteors = 0
	for _, entry in EventCatalog.Entries.Meteor do
		meteors += 1
		expectEq(entry.minRank, Tiers.ToolRank.Mithril, entry.id .. " gate")
		local adamantine = false
		for _, row in entry.loot do
			adamantine = adamantine or row[1] == "AdamantineOre"
		end
		expect(adamantine, entry.id .. " drops Adamantine Ore")
		expectEq(
			NodeCatalog.PickaxeNotice(tool("Cobalt", "Pickaxe"), entry.minRank),
			"Needs a Mithril Pickaxe or better",
			entry.id .. " refuses a Cobalt Pickaxe"
		)
		expectEq(NodeCatalog.PickaxeNotice(tool("Mithril", "Pickaxe"), entry.minRank), nil, entry.id .. " Mithril")
		expectEq(NodeCatalog.PickaxeNotice(tool("Adamantine", "Pickaxe"), entry.minRank), nil, entry.id .. " better")
	end
	expect(meteors >= 1, "meteors exist")
end)

test("luck raises a meteor's rare rows, never above certain", function()
	local loot = { { "AdamantineOre", 4, 8, 1 }, { "AbyssalShard", 1, 2, 0.4 } }
	local function shardRate(luck: number)
		local rng, hits, trials = Random.new(43), 0, 40000
		for _ = 1, trials do
			for _, item in EventRules.RollLoot(loot, rng, luck) do
				hits += if item.catalogId == "AbyssalShard" then 1 else 0
			end
		end
		return hits / trials
	end
	expectNear(shardRate(0), 0.4, 0.01, "no luck")
	expectNear(shardRate(0.5), 0.6, 0.01, "+50% luck")
	expectNear(shardRate(5), 1, 0, "capped at certain")
end)

test("ore events give their region's ores and need a pickaxe that mines all of them", function()
	local regionOres = {
		OuterRim = { Stone = true, Flint = true, CopperOre = true, IronOre = true },
		InnerRing = { SilverOre = true, CobaltOre = true, Obsidian = true, Jade = true },
		Center = { MithrilOre = true, AdamantineOre = true },
	}
	for _, entry in EventCatalog.Entries.Ore do
		expect(type(entry.minRank) == "number", entry.id .. " has a pickaxe gate")
		local allowed = regionOres[entry.biome]
		expect(allowed ~= nil, entry.id .. " sits in one region, not Any")
		for _, row in entry.loot do
			local id = row[1]
			expect(ItemCatalog.Get(id) ~= nil, entry.id .. " loot " .. id)
			if id ~= "AncientEmber" then
				expect(allowed == nil or allowed[id], entry.id .. " " .. id .. " belongs to " .. entry.biome)
				expect((NodeCatalog.MineRanks[id] or 1) <= (entry.minRank or 0), entry.id .. " gate covers " .. id)
			end
		end
	end
end)

test("the rare shrub is a hand-gathered Rare vegetation event with rare berries and herbs", function()
	local wanted = { "Sunberry", "Glimmerberry", "Bloodroot", "Moonpetal" }
	local rares, epics = 0, 0
	for _, entry in EventCatalog.Entries.Vegetation do
		expectEq(entry.kind, EventCatalog.Kinds.Node, entry.id .. " is a node event")
		expectEq(entry.minRank, nil, entry.id .. " is gathered by hand")
		local drops = {}
		for _, row in entry.loot do
			expect(ItemCatalog.Get(row[1]) ~= nil, entry.id .. " loot " .. row[1])
			drops[row[1]] = true
		end
		local shrub = true
		for _, id in wanted do
			shrub = shrub and drops[id] == true
		end
		if shrub then
			rares += if entry.rarity == "Rare" then 1 else 0
			epics += if entry.rarity == "Epic" then 1 else 0
			expect(entry.rarity == "Rare" or entry.rarity == "Epic", entry.id .. " rarity")
			expect(table.find(entry.tags, "event") ~= nil, entry.id .. " is announced as an event")
		end
	end
	expectEq(rares, 1, "one Rare shrub")
	expect(epics <= 1, "at most one Epic shrub")
	for _, id in { "Bloodroot", "Moonpetal" } do
		expect(ItemCatalog.Get(id).tradeable, id .. " is tradeable")
	end
end)

local function list(...)
	local entries = {}
	for index, rarity in { ... } do
		table.insert(entries, { id = rarity .. index, rarity = rarity })
	end
	return entries
end

test("every rare type rolls on its own at its rarity's old frequency", function()
	local rng = Random.new(47)
	local entries = list("Common", "Rare", "Rare", "Epic")
	local counts, both, common, trials = {}, 0, 0, 400000
	for _ = 1, trials do
		local results = EventRules.RollCategory(entries, rng)
		local rares = 0
		for _, entry in results do
			counts[entry.id] = (counts[entry.id] or 0) + 1
			rares += if entry.rarity == "Rare" then 1 else 0
			common += if entry.rarity == "Common" then 1 else 0
		end
		both += if rares == 2 then 1 else 0
		for index = 2, #results do
			expect(
				Rarity.Index(results[index - 1].rarity) >= Rarity.Index(results[index].rarity),
				"results come rarest first"
			)
		end
	end
	local trigger = EventRules.TRIGGER_CHANCE
	local rare, epic = EventRules.RARITY_WEIGHTS.Rare, EventRules.RARITY_WEIGHTS.Epic
	expectNear((counts.Rare2 or 0) / trials, trigger * rare, 0.002, "first Rare type")
	expectNear((counts.Rare3 or 0) / trials, trigger * rare, 0.002, "second Rare type, not halved")
	expectNear((counts.Epic4 or 0) / trials, trigger * epic, 0.0015, "Epic type")
	expectNear(both / trials, trigger * rare * rare, 0.0008, "both Rare types can start in one tick")
	local none = (1 - rare) * (1 - rare) * (1 - epic)
	expectNear(common / trials, trigger * none, 0.003, "Common only when no rarer type hits")
end)

test("a category without Common skips when no type hits; ticks gather every result", function()
	local rng = Random.new(53)
	local entries = list("Rare", "Rare")
	local empty, trials = 0, 100000
	for _ = 1, trials do
		empty += if #EventRules.RollCategory(entries, rng) == 0 then 1 else 0
	end
	local rare = EventRules.RARITY_WEIGHTS.Rare
	expectNear(1 - empty / trials, EventRules.TRIGGER_CHANCE * (1 - (1 - rare) ^ 2), 0.003, "either Rare type")
	expectEq(#EventRules.RollCategory({}, rng), 0, "an empty category never rolls")

	local catalog = { A = list("Uncommon", "Uncommon", "Uncommon"), B = list("Common") }
	local best = 0
	for _ = 1, 5000 do
		local results = EventRules.RollTick(catalog, { "A", "B" }, rng)
		local fromA = 0
		for _, entry in results do
			fromA += if entry.rarity == "Uncommon" then 1 else 0
		end
		best = math.max(best, fromA)
	end
	expect(best >= 2, "one category can start several types in one tick")
end)

test("rolls are reproducible from an injected rng", function()
	local function run(seed: number)
		local rng, ids = Random.new(seed), {}
		for _ = 1, 2000 do
			for _, entry in EventRules.RollTick(EventCatalog.Entries, EventCatalog.Categories, rng) do
				table.insert(ids, entry.id)
			end
		end
		return table.concat(ids, ",")
	end
	expectEq(run(59), run(59), "same seed, same events")
	expect(#run(59) > 0, "the real catalog produces events")
end)
