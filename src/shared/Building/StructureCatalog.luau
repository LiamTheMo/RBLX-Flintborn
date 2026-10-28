-- Buildable pieces and totem levels (GDD §6.1–6.2, §51, Q35–36, Q144, Q159a).
-- Walls, floors, doors and roofs come in every building tier; furniture has one
-- tier. Sizes are in studs before rotation. HP and costs are starting placeholders
-- except totem HP (confirmed 500 / 1,000 / 2,500).

local GameConstants = require(script.Parent.Parent.GameConstants)
local Tiers = require(script.Parent.Parent.Items.Tiers)

local StructureCatalog = {}

-- Walls, floors, doors and roofs come in every building tier of the gear ladder
-- (GDD §51): Wood, Stone, then each metal, built from that metal's bars.
StructureCatalog.TIERS = {}
for _, tier in Tiers.Ladder do
	if tier.canMake.Building then
		table.insert(StructureCatalog.TIERS, tier.id)
	end
end

-- `wood` and `stone` are {hp, cost}; metal tiers take Stone's HP ×1.25 per tier and
-- cost `bars` of their bar plus `extra`.
local function tiered(size: Vector3, wood, stone, bars: number, extra)
	local tiers = {
		Wood = { hp = wood[1], cost = wood[2], material = "Wood" },
		Stone = { hp = stone[1], cost = stone[2], material = "Stone" },
	}
	for _, metal in Tiers.Metals do
		local tier = Tiers.Get(metal)
		local cost = { [tier.material] = bars }
		for input, amount in extra do
			cost[input] = amount
		end
		tiers[metal] = { hp = Tiers.Value(stone[1], tier), cost = cost, material = metal }
	end
	return { size = size, tiers = tiers }
end

local function single(size: Vector3, hp: number, cost, material: string)
	return { size = size, tiers = { Wood = { hp = hp, cost = cost, material = material } } }
end

StructureCatalog.Pieces = {
	Wall = tiered(Vector3.new(8, 8, 1), { 300, { Wood = 10 } }, { 800, { Stone = 12, Wood = 2 } }, 8, { Stone = 4 }),
	Floor = tiered(Vector3.new(8, 1, 8), { 200, { Wood = 8 } }, { 600, { Stone = 10 } }, 6, { Stone = 2 }),
	Door = tiered(Vector3.new(4, 8, 1), { 250, { Wood = 12 } }, { 700, { Stone = 14, Wood = 4 } }, 10, { Wood = 4 }),
	Roof = tiered(
		Vector3.new(8, 1, 8),
		{ 200, { Wood = 8, Fiber = 4 } },
		{ 600, { Stone = 10, Wood = 2 } },
		6,
		{ Stone = 2 }
	),
	Chest = single(Vector3.new(4, 3, 3), 200, { Wood = 15 }, "Wood"),
	Bed = single(Vector3.new(4, 2, 7), 150, { Wood = 10, Fiber = 10, Hide = 4 }, "Wood"),
	Workbench = single(Vector3.new(5, 3, 3), 300, { Wood = 20, Stone = 10 }, "Wood"),
	Furnace = single(Vector3.new(4, 5, 4), 600, { Stone = 30, Wood = 10 }, "Stone"),
	-- Silver-and-up and Jade gear (GDD §51).
	Anvil = single(Vector3.new(4, 3, 3), 900, { IronBar = 20, Stone = 30 }, "Iron"),
	-- Potions and draughts (GDD §51).
	Cauldron = single(Vector3.new(4, 3, 4), 500, { Stone = 20, CopperBar = 5 }, "Stone"),
	Trap = single(Vector3.new(4, 1, 4), 100, { Wood = 6, Stone = 4 }, "Wood"),
	Planter = single(Vector3.new(4, 1.5, 4), 150, { Wood = 8, Fiber = 4 }, "Wood"),
	Totem = single(Vector3.new(3, 8, 3), GameConstants.TOTEM_HEALTH_BY_LEVEL[1], { Wood = 30, Stone = 10 }, "Wood"),
}

StructureCatalog.ORDER = {
	"Wall",
	"Floor",
	"Door",
	"Roof",
	"Chest",
	"Bed",
	"Workbench",
	"Furnace",
	"Anvil",
	"Cauldron",
	"Trap",
	"Planter",
	"Totem",
}

-- Totem levels: placing buys level 1; each upgrade pays the next level's cost.
StructureCatalog.TotemLevels = {
	{ hp = GameConstants.TOTEM_HEALTH_BY_LEVEL[1], radius = 15, cost = { Wood = 30, Stone = 10 } },
	{ hp = GameConstants.TOTEM_HEALTH_BY_LEVEL[2], radius = 35, cost = { Stone = 40, Wood = 20 } },
	{ hp = GameConstants.TOTEM_HEALTH_BY_LEVEL[3], radius = 70, cost = { IronBar = 30, Stone = 60 } },
}

StructureCatalog.CHEST_SLOTS = 20
StructureCatalog.TRAP_DAMAGE = 15
StructureCatalog.TRAP_COOLDOWN = 2

-- Crops planted in a planter (GDD Q41): what one planting costs and yields.
StructureCatalog.Crops = {
	Redberry = { seed = { Redberry = 1 }, yield = { catalogId = "Redberry", quantity = 4 }, seconds = 180 },
	Sweetberry = { seed = { Sweetberry = 1 }, yield = { catalogId = "Sweetberry", quantity = 4 }, seconds = 180 },
	Herbs = { seed = { Herbs = 2 }, yield = { catalogId = "Herbs", quantity = 6 }, seconds = 300 },
	Sapling = { seed = { Wood = 5 }, yield = { catalogId = "Wood", quantity = 25 }, seconds = 600 },
	-- Fiber grows in planters too (GDD §53); Sunberry and Glimmerberry stay wild-only.
	Fiber = { seed = { Fiber = 3 }, yield = { catalogId = "Fiber", quantity = 12 }, seconds = 240 },
}
StructureCatalog.CROP_ORDER = { "Redberry", "Sweetberry", "Herbs", "Sapling", "Fiber" }

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
