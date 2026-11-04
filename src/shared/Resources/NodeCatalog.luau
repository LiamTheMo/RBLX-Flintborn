-- Harvestable resource nodes (GDD §4.1, §7.6, §53, Q104, Q112). Every node has
-- health and takes many hits; each hit drops its material on the ground as a
-- pickup and removes as much health as it dropped, so a better tool empties a node
-- in fewer hits but never gets more out of it. Ordinary nodes regrow by tier after
-- depletion; rare event nodes (v0.11) never regrow. Bare hands can gather trees,
-- rocks, clay and plants so a fresh spawn can craft its first tools. Numbers are
-- starting placeholders.

local GameConstants = require(script.Parent.Parent.GameConstants)
local ItemCatalog = require(script.Parent.Parent.Items.ItemCatalog)
local Tiers = require(script.Parent.Parent.Items.Tiers)

local NodeCatalog = {}

NodeCatalog.HARVEST_RANGE = 12
NodeCatalog.HARVEST_INTERVAL = 0.4

local REGROW = GameConstants.NODE_REGROW_SECONDS
local R = Tiers.ToolRank

-- `health` is the node's total material. Drops per hit (GDD §53) are
-- 1 + max(0, toolRank − nodeRank), clamped to the health left. `tool` names the
-- tool kind that counts for a hand-or-tool node (trees, rocks, clay: node rank 0,
-- bare hands rank 0, so a Wooden tool drops 2 and a Stone one 3). Ores and gem
-- nodes need a pickaxe of at least `minRank` (the previous tier's pickaxe), which
-- is also their node rank: 1 per hit at the gate, +1 per pickaxe tier above it.
-- Nodes without a `tool` are gathered by hand at 1 per hit; tools add nothing.
-- `bonus` is a per-hit chance of an extra material (Flint from rocks, Resin from
-- trees) and `finishBonus` what the hit that depletes the node also drops; neither
-- uses health. `regrow` is the seconds until a depleted node is back.
NodeCatalog.Nodes = {
	Tree = {
		material = "Wood",
		health = 12,
		tool = "Axe",
		regrow = REGROW.Basic,
		bonus = { catalogId = "Resin", chance = 0.10 },
		mastery = "Woodcutting",
	},
	Rock = {
		material = "Stone",
		health = 12,
		tool = "Pickaxe",
		regrow = REGROW.Basic,
		bonus = { catalogId = "Flint", chance = 0.15 },
		finishBonus = { catalogId = "Flint", quantity = 1 },
		mastery = "Mining",
	},
	FiberPlant = { material = "Fiber", health = 3, regrow = REGROW.Basic, mastery = "Farming" },
	HerbShrub = { material = "Herbs", health = 3, regrow = REGROW.Basic, mastery = "Farming" },
	RedberryBush = { material = "Redberry", health = 3, regrow = REGROW.Basic, mastery = "Farming" },
	SweetberryBush = { material = "Sweetberry", health = 3, regrow = REGROW.Basic, mastery = "Farming" },
	-- Ores by region (GDD §51): Outer Rim copper and iron, Inner Ring silver and
	-- cobalt, Crater mithril. Adamantine only comes from meteors, the Guardian and
	-- rare events: there is no Adamantine node.
	CopperDeposit = { material = "CopperOre", health = 8, minRank = R.Stone, regrow = REGROW.Low, mastery = "Mining" },
	IronDeposit = { material = "IronOre", health = 8, minRank = R.Copper, regrow = REGROW.Low, mastery = "Mining" },
	SilverDeposit = { material = "SilverOre", health = 8, minRank = R.Iron, regrow = REGROW.Mid, mastery = "Mining" },
	CobaltDeposit = { material = "CobaltOre", health = 8, minRank = R.Silver, regrow = REGROW.Mid, mastery = "Mining" },
	MithrilDeposit = {
		material = "MithrilOre",
		health = 6,
		minRank = R.Cobalt,
		regrow = REGROW.High,
		mastery = "Mining",
	},
	-- Inner Ring gem-class nodes (GDD §18.1, §51).
	ObsidianOutcrop = { material = "Obsidian", health = 5, minRank = R.Iron, regrow = REGROW.Mid, mastery = "Mining" },
	JadeVein = { material = "Jade", health = 5, minRank = R.Cobalt, regrow = REGROW.High, mastery = "Mining" },
	-- New nodes (GDD §53) for materials with no use yet. Clay digs by hand or with
	-- any pickaxe; the stones are gated like ores; the rest are picked by hand.
	ClayDeposit = { material = "Clay", health = 4, tool = "Pickaxe", regrow = REGROW.Basic, mastery = "Mining" },
	AmethystGeode = { material = "Amethyst", health = 4, minRank = R.Iron, regrow = REGROW.Mid, mastery = "Mining" },
	StarstoneOutcrop = {
		material = "Starstone",
		health = 4,
		minRank = R.Cobalt,
		regrow = REGROW.High,
		mastery = "Mining",
	},
	StormglassCluster = {
		material = "Stormglass",
		health = 4,
		minRank = R.Cobalt,
		regrow = REGROW.High,
		mastery = "Mining",
	},
	CaveMushroomPatch = { material = "CaveMushroom", health = 4, regrow = REGROW.Basic, mastery = "Farming" },
	RedcapMushroomPatch = { material = "RedcapMushroom", health = 4, regrow = REGROW.Basic, mastery = "Farming" },
	ChestnutMushroomPatch = { material = "ChestnutMushroom", health = 4, regrow = REGROW.Basic, mastery = "Farming" },
	ThornShrub = { material = "Thornvine", health = 4, regrow = REGROW.Basic, mastery = "Farming" },
	FrostShrub = { material = "Frostleaf", health = 4, regrow = REGROW.Basic, mastery = "Farming" },
	JuniperShrub = { material = "JuniperBerry", health = 4, regrow = REGROW.Basic, mastery = "Farming" },
	ElderberryShrub = { material = "Elderberry", health = 4, regrow = REGROW.Basic, mastery = "Farming" },
	RaspberryBush = { material = "Raspberry", health = 4, regrow = REGROW.Basic, mastery = "Farming" },
	HazelShrub = { material = "Hazelnut", health = 4, regrow = REGROW.Basic, mastery = "Farming" },
}

-- The pickaxe rank each mined material needs: the gated nodes' materials plus every
-- metal's ore (the previous tier's pickaxe), so event and meteor ore share the gate.
NodeCatalog.MineRanks = {}
for _, node in NodeCatalog.Nodes do
	if node.minRank then
		NodeCatalog.MineRanks[node.material] = node.minRank
	end
end
for _, metal in Tiers.Metals do
	local tier = Tiers.Get(metal)
	NodeCatalog.MineRanks[tier.ore] = NodeCatalog.MineRanks[tier.ore] or Tiers.ToolRank[metal] - 1
end

-- True when `tool` ({kind, tier} or nil) is a pickaxe of at least `minRank`.
function NodeCatalog.MeetsPickaxe(tool, minRank: number): boolean
	return tool ~= nil and tool.kind == "Pickaxe" and (tool.tier or 1) >= minRank
end

-- Display name of the weakest pickaxe of `rank` ("Copper Pickaxe").
function NodeCatalog.PickaxeName(rank: number): string
	for tierId, tierRank in Tiers.ToolRank do
		if tierRank == rank then
			local item = ItemCatalog.Get(ItemCatalog.GearId(tierId, "Pickaxe"))
			if item then
				return item.name
			end
		end
	end
	return "better pickaxe"
end

-- What to tell a player whose `tool` is below `minRank` ("Needs a Copper Pickaxe
-- or better"), or nil when it is good enough.
function NodeCatalog.PickaxeNotice(tool, minRank: number): string?
	if NodeCatalog.MeetsPickaxe(tool, minRank) then
		return nil
	end
	return ("Needs a %s or better"):format(NodeCatalog.PickaxeName(minRank))
end

-- A node's rank (GDD §53): an ore or gem node's pickaxe gate, otherwise 0.
function NodeCatalog.Rank(nodeType: string): number
	local node = NodeCatalog.Nodes[nodeType]
	return node and node.minRank or 0
end

-- Drops one full hit gives with the equipped tool ({kind, tier} or nil), before the
-- clamp to the health left, or 0 when that tool cannot harvest this node (an ore
-- below its pickaxe gate). Bare hands and the wrong tool kind count as rank 0.
function NodeCatalog.YieldFor(nodeType: string, tool): number
	local node = NodeCatalog.Nodes[nodeType]
	if node == nil then
		return 0
	end
	if node.minRank and not NodeCatalog.MeetsPickaxe(tool, node.minRank) then
		return 0
	end
	local counts = tool ~= nil and (node.minRank ~= nil or (node.tool ~= nil and node.tool == tool.kind))
	local toolRank = if counts then tool.tier or 1 else 0
	return 1 + math.max(0, toolRank - NodeCatalog.Rank(nodeType))
end

-- Why `tool` cannot gather `nodeType`, or nil when it can.
function NodeCatalog.GateNotice(nodeType: string, tool): string?
	local node = NodeCatalog.Nodes[nodeType]
	if node == nil then
		return "You can't gather that."
	end
	return if node.minRank then NodeCatalog.PickaxeNotice(tool, node.minRank) else nil
end

return NodeCatalog
