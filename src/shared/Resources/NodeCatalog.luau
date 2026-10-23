-- Harvestable resource nodes (GDD §4.1, §7.6, Q104, Q112). Ordinary nodes regrow
-- about 120 s after depletion; rare event nodes (v0.11) never regrow. Bare hands
-- can gather slowly so a fresh spawn can craft its first tools. Yields are
-- starting placeholders.

local GameConstants = require(script.Parent.Parent.GameConstants)

local NodeCatalog = {}

NodeCatalog.RESPAWN_SECONDS = GameConstants.NODE_RESPAWN_SECONDS
NodeCatalog.HARVEST_RANGE = 12
NodeCatalog.HARVEST_INTERVAL = 0.4

-- yields: per-hit amount by tool kind ("Hand" for no matching tool); a missing
-- entry means that tool cannot harvest the node. minTier applies to tool yields.
NodeCatalog.Nodes = {
	Tree = { material = "Wood", hits = 5, yields = { Hand = 1, Axe = 3 } },
	Rock = { material = "Stone", hits = 5, yields = { Hand = 1, Pickaxe = 2 } },
	IronDeposit = { material = "Iron", hits = 6, yields = { Pickaxe = 1 } },
	FiberPlant = { material = "Fiber", hits = 2, yields = { Hand = 2, Sickle = 3 } },
	HerbShrub = { material = "Herbs", hits = 2, yields = { Hand = 1, Sickle = 2 } },
	BerryBush = { material = "Berries", hits = 2, yields = { Hand = 1, Sickle = 2 } },
}

-- Amount one hit gives with the equipped tool ({kind, tier} or nil), or 0 when
-- that tool cannot harvest this node. Higher tool tiers add one per tier above 1.
function NodeCatalog.YieldFor(nodeType: string, tool): number
	local node = NodeCatalog.Nodes[nodeType]
	if node == nil then
		return 0
	end
	if tool and node.yields[tool.kind] then
		return node.yields[tool.kind] + math.max(0, (tool.tier or 1) - 1)
	end
	return node.yields.Hand or 0
end

return NodeCatalog
