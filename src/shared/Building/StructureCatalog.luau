-- Buildable pieces and totem levels (GDD §6.1–6.2, Q35–36, Q144, Q159a). Walls,
-- floors, doors and roofs come in wood → stone → iron tiers; furniture has one
-- tier. Sizes are in studs before rotation. HP and costs are starting placeholders
-- except totem HP (confirmed 500 / 1,000 / 2,500).

local GameConstants = require(script.Parent.Parent.GameConstants)

local StructureCatalog = {}

StructureCatalog.TIERS = { "Wood", "Stone", "Iron" }

local function tiered(size: Vector3, hp, costs)
	return {
		size = size,
		tiers = {
			Wood = { hp = hp[1], cost = costs[1], material = "Wood" },
			Stone = { hp = hp[2], cost = costs[2], material = "Stone" },
			Iron = { hp = hp[3], cost = costs[3], material = "Iron" },
		},
	}
end

local function single(size: Vector3, hp: number, cost, material: string)
	return { size = size, tiers = { Wood = { hp = hp, cost = cost, material = material } } }
end

StructureCatalog.Pieces = {
	Wall = tiered(
		Vector3.new(8, 8, 1),
		{ 300, 800, 1600 },
		{ { Wood = 10 }, { Stone = 12, Wood = 2 }, { Iron = 8, Stone = 4 } }
	),
	Floor = tiered(Vector3.new(8, 1, 8), { 200, 600, 1200 }, { { Wood = 8 }, { Stone = 10 }, { Iron = 6, Stone = 2 } }),
	Door = tiered(
		Vector3.new(4, 8, 1),
		{ 250, 700, 1400 },
		{ { Wood = 12 }, { Stone = 14, Wood = 4 }, { Iron = 10, Wood = 4 } }
	),
	Roof = tiered(
		Vector3.new(8, 1, 8),
		{ 200, 600, 1200 },
		{ { Wood = 8, Fiber = 4 }, { Stone = 10, Wood = 2 }, { Iron = 6, Stone = 2 } }
	),
	Chest = single(Vector3.new(4, 3, 3), 200, { Wood = 15 }, "Wood"),
	Bed = single(Vector3.new(4, 2, 7), 150, { Wood = 10, Fiber = 10, Hide = 4 }, "Wood"),
	Workbench = single(Vector3.new(5, 3, 3), 300, { Wood = 20, Stone = 10 }, "Wood"),
	Furnace = single(Vector3.new(4, 5, 4), 600, { Stone = 30, Wood = 10 }, "Stone"),
	Trap = single(Vector3.new(4, 1, 4), 100, { Wood = 6, Stone = 4 }, "Wood"),
	Planter = single(Vector3.new(4, 1.5, 4), 150, { Wood = 8, Fiber = 4 }, "Wood"),
	Totem = single(Vector3.new(3, 8, 3), GameConstants.TOTEM_HEALTH_BY_LEVEL[1], { Wood = 30, Stone = 10 }, "Wood"),
}

StructureCatalog.ORDER =
	{ "Wall", "Floor", "Door", "Roof", "Chest", "Bed", "Workbench", "Furnace", "Trap", "Planter", "Totem" }

-- Totem levels: placing buys level 1; each upgrade pays the next level's cost.
StructureCatalog.TotemLevels = {
	{ hp = GameConstants.TOTEM_HEALTH_BY_LEVEL[1], radius = 15, cost = { Wood = 30, Stone = 10 } },
	{ hp = GameConstants.TOTEM_HEALTH_BY_LEVEL[2], radius = 35, cost = { Stone = 40, Wood = 20 } },
	{ hp = GameConstants.TOTEM_HEALTH_BY_LEVEL[3], radius = 70, cost = { Iron = 30, Stone = 60 } },
}

StructureCatalog.CHEST_SLOTS = 20
StructureCatalog.TRAP_DAMAGE = 15
StructureCatalog.TRAP_COOLDOWN = 2

-- Crops planted in a planter (GDD Q41): what one planting costs and yields.
StructureCatalog.Crops = {
	Berries = { seed = { Berries = 1 }, yield = { catalogId = "Berries", quantity = 4 }, seconds = 180 },
	Herbs = { seed = { Herbs = 2 }, yield = { catalogId = "Herbs", quantity = 6 }, seconds = 300 },
	Sapling = { seed = { Wood = 5 }, yield = { catalogId = "Wood", quantity = 25 }, seconds = 600 },
}
StructureCatalog.CROP_ORDER = { "Berries", "Herbs", "Sapling" }

function StructureCatalog.Get(pieceId: any, tier: any)
	local piece = type(pieceId) == "string" and StructureCatalog.Pieces[pieceId] or nil
	local stats = piece and type(tier) == "string" and piece.tiers[tier] or nil
	return piece, stats
end

for _, level in StructureCatalog.TotemLevels do
	for _, amount in level.cost do
		assert(amount > 0, "Totem costs must be positive")
	end
end

return StructureCatalog
