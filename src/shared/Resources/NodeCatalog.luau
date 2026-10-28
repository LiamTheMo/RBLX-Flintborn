-- Harvestable resource nodes (GDD §4.1, §7.6, Q104, Q112). Ordinary nodes regrow
-- about 120 s after depletion; rare event nodes (v0.11) never regrow. Bare hands
-- can gather slowly so a fresh spawn can craft its first tools. Yields are
-- starting placeholders.

local GameConstants = require(script.Parent.Parent.GameConstants)
local ItemCatalog = require(script.Parent.Parent.Items.ItemCatalog)
local Tiers = require(script.Parent.Parent.Items.Tiers)

local NodeCatalog = {}

NodeCatalog.RESPAWN_SECONDS = GameConstants.NODE_RESPAWN_SECONDS
NodeCatalog.HARVEST_RANGE = 12
NodeCatalog.HARVEST_INTERVAL = 0.4

-- `hand` is the per-hit yield with no matching tool (plants are gathered by hand
-- at the old sickle rate; sickles no longer exist, GDD §51). `tool` names the tool
-- kind that gathers faster, at `toolBase` per hit for a Stone tool, ×1.25 per tier
-- (Wood 2, Stone 3, Copper 4 … Adamantine 11). Ores and gem nodes need a pickaxe of
-- at least `minRank` (the previous tier's pickaxe) and give 1 per hit, +1 per tier
-- above the minimum. `bonus` is a per-hit chance of an extra material (Flint from
-- rocks, Resin from trees) and `finishBonus` what the hit that depletes the node
-- also gives.
NodeCatalog.Nodes = {
	Tree = {
		material = "Wood",
		hits = 5,
		hand = 1,
		tool = "Axe",
		toolBase = 3,
		bonus = { catalogId = "Resin", chance = 0.10 },
		mastery = "Woodcutting",
	},
	Rock = {
		material = "Stone",
		hits = 5,
		hand = 1,
		tool = "Pickaxe",
		toolBase = 3,
		bonus = { catalogId = "Flint", chance = 0.15 },
		finishBonus = { catalogId = "Flint", quantity = 1 },
		mastery = "Mining",
	},
	FiberPlant = { material = "Fiber", hits = 2, hand = 3, mastery = "Farming" },
	HerbShrub = { material = "Herbs", hits = 2, hand = 2, mastery = "Farming" },
	RedberryBush = { material = "Redberry", hits = 2, hand = 2, mastery = "Farming" },
	SweetberryBush = { material = "Sweetberry", hits = 2, hand = 2, mastery = "Farming" },
	-- Ores by region (GDD §51): Outer Rim copper and iron, Inner Ring silver and
	-- cobalt, Crater mithril. Adamantine only comes from meteors and the Guardian.
	CopperDeposit = { material = "CopperOre", hits = 6, minRank = Tiers.ToolRank.Stone, mastery = "Mining" },
	IronDeposit = { material = "IronOre", hits = 6, minRank = Tiers.ToolRank.Copper, mastery = "Mining" },
	SilverDeposit = { material = "SilverOre", hits = 6, minRank = Tiers.ToolRank.Iron, mastery = "Mining" },
	CobaltDeposit = { material = "CobaltOre", hits = 6, minRank = Tiers.ToolRank.Silver, mastery = "Mining" },
	MithrilDeposit = { material = "MithrilOre", hits = 6, minRank = Tiers.ToolRank.Cobalt, mastery = "Mining" },
	-- Inner Ring gem-class nodes (GDD §18.1, §51).
	ObsidianOutcrop = { material = "Obsidian", hits = 4, minRank = Tiers.ToolRank.Iron, mastery = "Mining" },
	JadeVein = { material = "Jade", hits = 4, minRank = Tiers.ToolRank.Cobalt, mastery = "Mining" },
}

-- Placeholder looks until the real models arrive: every node type has its own
-- shape, colour and material so ores read apart at a glance.
local P = Enum.PartType
local M = Enum.Material
NodeCatalog.Looks = {
	Tree = { size = Vector3.new(3, 14, 3), color = Color3.fromRGB(110, 78, 46), shape = P.Cylinder, material = M.Wood },
	Rock = { size = Vector3.new(6, 4, 6), color = Color3.fromRGB(128, 126, 120), shape = P.Block, material = M.Rock },
	FiberPlant = {
		size = Vector3.new(2, 3, 2),
		color = Color3.fromRGB(130, 170, 80),
		shape = P.Block,
		material = M.Grass,
	},
	HerbShrub = { size = Vector3.new(3, 2, 3), color = Color3.fromRGB(70, 140, 90), shape = P.Ball, material = M.Grass },
	RedberryBush = {
		size = Vector3.new(3, 3, 3),
		color = Color3.fromRGB(150, 50, 80),
		shape = P.Ball,
		material = M.Grass,
	},
	SweetberryBush = {
		size = Vector3.new(3, 3, 3),
		color = Color3.fromRGB(200, 120, 160),
		shape = P.Ball,
		material = M.Grass,
	},
	CopperDeposit = {
		size = Vector3.new(5, 4, 5),
		color = Color3.fromRGB(184, 115, 72),
		shape = P.Block,
		material = M.Slate,
	},
	IronDeposit = {
		size = Vector3.new(5, 4, 5),
		color = Color3.fromRGB(112, 96, 90),
		shape = P.Block,
		material = M.CorrodedMetal,
	},
	SilverDeposit = {
		size = Vector3.new(5, 5, 5),
		color = Color3.fromRGB(196, 200, 206),
		shape = P.Block,
		material = M.Metal,
	},
	CobaltDeposit = {
		size = Vector3.new(5, 5, 5),
		color = Color3.fromRGB(70, 96, 180),
		shape = P.Block,
		material = M.Slate,
	},
	MithrilDeposit = {
		size = Vector3.new(5, 6, 5),
		color = Color3.fromRGB(150, 210, 220),
		shape = P.Block,
		material = M.Foil,
	},
	ObsidianOutcrop = {
		size = Vector3.new(5, 4, 5),
		color = Color3.fromRGB(30, 26, 40),
		shape = P.Block,
		material = M.Glass,
	},
	JadeVein = {
		size = Vector3.new(4, 5, 4),
		color = Color3.fromRGB(70, 190, 130),
		shape = P.Block,
		material = M.Glass,
	},
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

-- Amount one hit gives with the equipped tool ({kind, tier} or nil), or 0 when
-- that tool cannot harvest this node (an ore below its pickaxe gate).
function NodeCatalog.YieldFor(nodeType: string, tool): number
	local node = NodeCatalog.Nodes[nodeType]
	if node == nil then
		return 0
	end
	local rank = if tool then tool.tier or 1 else 0
	if node.minRank then
		if not NodeCatalog.MeetsPickaxe(tool, node.minRank) then
			return 0
		end
		return 1 + rank - node.minRank
	end
	if tool and node.tool == tool.kind then
		return Tiers.Value(node.toolBase, { power = rank })
	end
	return node.hand or 0
end

-- True when `tool` can gather `nodeType` at all (ores need their pickaxe tier).
function NodeCatalog.CanHarvest(nodeType: string, tool): boolean
	return NodeCatalog.YieldFor(nodeType, tool) > 0
end

-- Why `tool` cannot gather `nodeType`, or nil when it can.
function NodeCatalog.GateNotice(nodeType: string, tool): string?
	local node = NodeCatalog.Nodes[nodeType]
	if node == nil then
		return "You can't gather that."
	end
	return if node.minRank then NodeCatalog.PickaxeNotice(tool, node.minRank) else nil
end

-- The extra stacks one successful hit gives: the per-hit `bonus` roll and, when
-- the hit depletes the node, its `finishBonus`.
function NodeCatalog.Extras(nodeType: string, depletes: boolean, rng)
	local node = NodeCatalog.Nodes[nodeType]
	local extras = {}
	if node == nil then
		return extras
	end
	if node.bonus and rng:NextNumber() < node.bonus.chance then
		table.insert(extras, { catalogId = node.bonus.catalogId, quantity = node.bonus.quantity or 1 })
	end
	if depletes and node.finishBonus then
		table.insert(extras, { catalogId = node.finishBonus.catalogId, quantity = node.finishBonus.quantity or 1 })
	end
	return extras
end

return NodeCatalog
