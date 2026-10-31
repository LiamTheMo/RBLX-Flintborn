-- Placeholder scenery for the generated island (GDD §54; visuals.md: chunky
-- low-poly, bold geometric trees, faceted stone, grassy ground). Decorative extras
-- that are NOT harvestable: forest clumps (pines or broadleaf trees), boulders,
-- grass and fern tufts and fallen logs, so the world reads as a place rather than a
-- scatter of resource nodes. Pure data (Recipe) so specs can check it;
-- WorldBuildService places it with ModelBuilder.Build.
--
-- SceneryModels.Get(kind, palette, variant) -> recipe: the origin is a point on the
-- ground, facing -Z; shapes sink up to SceneryModels.SINK studs below it so they
-- never hover on a slope. Variants differ in silhouette; WorldBuildService adds a
-- random yaw and a size within the kind's scale range.
-- SceneryModels.Zones: per-zone palette and counts (named constants), kept in step
-- with the budget (PART_BUDGET, checked by WorstCaseParts).
-- Parts named in SOLID_PARTS may collide (trunks, boulders, logs); everything else
-- is walk-through. Nothing is ever queryable (rays pass), see WorldBuildService.

local Recipe = require(script.Parent.Recipe)

local SceneryModels = {}

-- How far below the ground point a shape may reach.
SceneryModels.SINK = 1.2
-- All scenery together stays under this many parts (the island is also a game).
SceneryModels.PART_BUDGET = 3000
-- Part names that block players; the rest of a model never does.
SceneryModels.SOLID_PARTS = { Trunk = true, Boulder = true, Log = true }

local part, shade = Recipe.Part, Recipe.Shade

-- Palettes: leaf and pine are the canopy base colours, rock is the boulder colour.
-- A zone picks one so its trees, stones and grass match its terrain.
SceneryModels.Palettes = {
	Temperate = {
		leaf = { 86, 150, 70 },
		pine = { 54, 112, 70 },
		trunk = { 112, 80, 50 },
		rock = { 134, 130, 122 },
		rockMaterial = "Rock",
		grass = { 118, 168, 74 },
	},
	Pine = {
		leaf = { 70, 128, 64 },
		pine = { 38, 96, 64 },
		trunk = { 96, 68, 44 },
		rock = { 120, 118, 114 },
		rockMaterial = "Rock",
		grass = { 96, 146, 72 },
	},
	Moss = {
		leaf = { 66, 132, 54 },
		pine = { 44, 100, 60 },
		trunk = { 86, 64, 44 },
		rock = { 100, 120, 98 },
		rockMaterial = "Rock",
		grass = { 80, 142, 62 },
	},
	Jungle = {
		leaf = { 48, 152, 62 },
		pine = { 40, 120, 70 },
		trunk = { 100, 72, 48 },
		rock = { 172, 166, 150 },
		rockMaterial = "Limestone",
		grass = { 68, 162, 70 },
	},
	Ember = {
		leaf = { 134, 138, 70 },
		pine = { 98, 106, 60 },
		trunk = { 86, 62, 46 },
		rock = { 92, 68, 62 },
		rockMaterial = "Basalt",
		grass = { 152, 146, 80 },
	},
	Frost = {
		leaf = { 120, 170, 150 },
		pine = { 62, 112, 112 },
		trunk = { 90, 70, 56 },
		rock = { 176, 186, 198 },
		rockMaterial = "Rock",
		grass = { 170, 200, 190 },
		snow = { 236, 242, 250 },
	},
	Crater = {
		leaf = { 100, 136, 80 },
		pine = { 66, 100, 72 },
		trunk = { 90, 68, 50 },
		rock = { 98, 94, 92 },
		rockMaterial = "Basalt",
		grass = { 112, 142, 90 },
	},
}

-- Per kind: how many silhouettes it has, the size range placement picks from, the
-- footprint radius (studs, before scale) the ground is sampled over and whether
-- its SOLID_PARTS collide.
SceneryModels.Kinds = {
	Pine = { variants = 2, scale = { 0.85, 1.4 }, radius = 2, solid = true },
	Broadleaf = { variants = 2, scale = { 0.85, 1.35 }, radius = 2, solid = true },
	Boulder = { variants = 2, scale = { 0.7, 1.9 }, radius = 2.5, solid = true },
	Tuft = { variants = 1, scale = { 0.8, 1.5 }, radius = 1, solid = false },
	Fern = { variants = 1, scale = { 0.9, 1.6 }, radius = 1, solid = false },
	Log = { variants = 2, scale = { 0.9, 1.3 }, radius = 3.5, solid = true },
}

local function block(size, pos, color, material, rot, name)
	return part("Block", size, pos, color, material, rot, if name then { name = name } else nil)
end

local BUILDERS = {}

-- Pines: a trunk and stacked square tiers, turned against each other. Frost pines
-- carry snow on the top tier.
function BUILDERS.Pine(palette, variant)
	local pine = palette.pine
	local cap = palette.snow or shade(pine, 1.25)
	if variant == 1 then
		return {
			block({ 1.6, 6.8, 1.6 }, { 0, 2.6, 0 }, palette.trunk, "Wood", nil, "Trunk"),
			block({ 7.6, 3, 7.6 }, { 0, 5.6, 0 }, shade(pine, 0.85), "Grass"),
			block({ 5.8, 3, 5.8 }, { 0, 8.1, 0 }, pine, "Grass", { 0, 45, 0 }),
			block({ 4, 3, 4 }, { 0, 10.6, 0 }, shade(pine, 1.1), "Grass", { 0, 20, 0 }),
			block({ 2, 2.6, 2 }, { 0, 12.8, 0 }, cap, "Grass", { 0, 60, 0 }),
		}
	end
	return {
		block({ 1.4, 8.8, 1.4 }, { 0, 3.6, 0 }, palette.trunk, "Wood", nil, "Trunk"),
		block({ 6.2, 3.4, 6.2 }, { 0, 7, 0 }, shade(pine, 0.88), "Grass"),
		block({ 4.8, 3.2, 4.8 }, { 0, 9.6, 0 }, pine, "Grass", { 0, 45, 0 }),
		block({ 3.4, 3, 3.4 }, { 0, 12, 0 }, shade(pine, 1.1), "Grass", { 0, 20, 0 }),
		block({ 1.8, 2.6, 1.8 }, { 0, 14.2, 0 }, cap, "Grass", { 0, 60, 0 }),
	}
end

-- Broadleaf trees: a trunk under a few overlapping ball canopies.
function BUILDERS.Broadleaf(palette, variant)
	local leaf = palette.leaf
	if variant == 1 then
		return {
			block({ 1.8, 7.8, 1.8 }, { 0, 3.1, 0 }, palette.trunk, "Wood", nil, "Trunk"),
			part("Ball", { 8, 5.5, 8 }, { 0, 8.2, 0 }, shade(leaf, 0.85), "LeafyGrass"),
			part("Ball", { 6, 4.6, 6 }, { 0.6, 11.2, -0.5 }, leaf, "LeafyGrass"),
			part("Ball", { 4.6, 4, 4.6 }, { -2.6, 7.4, 1.4 }, shade(leaf, 1.12), "LeafyGrass"),
		}
	end
	return {
		block({ 2.2, 6.8, 2.2 }, { 0, 2.6, 0 }, palette.trunk, "Wood", nil, "Trunk"),
		part("Ball", { 10, 5, 10 }, { 0, 7.6, 0 }, shade(leaf, 0.82), "LeafyGrass"),
		part("Ball", { 7, 4.4, 7 }, { -1, 10.6, 1 }, leaf, "LeafyGrass"),
		part("Ball", { 5, 4, 5 }, { 3.2, 8.4, -1.6 }, shade(leaf, 0.95), "LeafyGrass"),
		part("Ball", { 4, 3.6, 4 }, { 0.4, 13, 0.4 }, shade(leaf, 1.15), "LeafyGrass"),
	}
end

-- Boulders: a squat cluster, or a leaning spire on a wide foot.
function BUILDERS.Boulder(palette, variant)
	local rock, material = palette.rock, palette.rockMaterial
	if variant == 1 then
		return {
			block({ 5, 3, 4.4 }, { 0, 1.1, 0 }, rock, material, { 0, 15, 0 }, "Boulder"),
			part(
				"Wedge",
				{ 3, 2.2, 3 },
				{ 2.4, 0.7, 1 },
				shade(rock, 0.88),
				material,
				{ 0, 130, 0 },
				{ name = "Boulder" }
			),
			block({ 1.4, 1, 1.4 }, { -2.2, 0.1, -1.6 }, shade(rock, 1.12), material, { 0, 35, 0 }, "Pebble"),
		}
	end
	return {
		block({ 3.6, 2.4, 3.4 }, { 0, 0.8, 0 }, shade(rock, 0.9), material, { 0, -10, 0 }, "Boulder"),
		block({ 2.6, 5.4, 2.4 }, { -0.3, 2.3, 0.2 }, rock, material, { 4, 25, 0 }, "Boulder"),
		part(
			"Wedge",
			{ 2, 1.6, 2.4 },
			{ 1.8, 0.4, -1 },
			shade(rock, 1.1),
			material,
			{ 0, 200, 0 },
			{ name = "Pebble" }
		),
	}
end

-- Grass tuft: three flat blades, one upright and two splayed. Sunk a little so the
-- bottoms hide in the turf.
function BUILDERS.Tuft(palette)
	local grass = palette.grass
	return {
		block({ 0.8, 2.4, 0.25 }, { 0, 0.9, 0 }, grass, "Grass", { 0, 20, 0 }),
		block({ 0.7, 2, 0.25 }, { 0.5, 0.7, 0.2 }, shade(grass, 1.15), "Grass", { 0, 80, -16 }),
		block({ 0.7, 1.8, 0.25 }, { -0.4, 0.6, -0.3 }, shade(grass, 0.85), "Grass", { 12, -30, 14 }),
	}
end

-- Fern: a low mound with two crossed, raised fronds.
function BUILDERS.Fern(palette)
	local grass = palette.grass
	local frond = shade(grass, 0.8)
	return {
		part("Ball", { 1.2, 0.7, 1.2 }, { 0, 0.05, 0 }, shade(grass, 0.7), "Grass"),
		block({ 0.9, 0.15, 3 }, { 0, 0.9, 0 }, frond, "Grass", { 25, 0, 0 }),
		block({ 0.9, 0.15, 2.6 }, { 0, 0.8, 0 }, shade(frond, 1.15), "Grass", { 25, 100, 0 }),
	}
end

-- Fallen log with a knot and a strip of moss, or a cut stump with a root.
function BUILDERS.Log(palette, variant)
	local wood = shade(palette.trunk, 0.95)
	if variant == 1 then
		return {
			part("Cylinder", { 7, 1.8, 1.8 }, { 0, 0.7, 0 }, wood, "Wood", nil, { name = "Log" }),
			block({ 0.6, 0.6, 2 }, { 1.6, 1.3, 0.9 }, shade(wood, 0.85), "Wood", { -20, 0, 0 }, "Branch"),
			block({ 3.6, 0.3, 1 }, { -0.8, 1.65, 0.1 }, palette.grass, "Grass", nil, "Moss"),
		}
	end
	return {
		block({ 2.2, 1.5, 2.2 }, { 0, 0.35, 0 }, wood, "Wood", { 0, 12, 0 }, "Log"),
		block({ 1.7, 0.1, 1.7 }, { 0, 1.12, 0 }, { 190, 160, 110 }, "Wood", { 0, 12, 0 }, "Cut"),
		part("Wedge", { 1, 0.8, 1.6 }, { 1.5, 0.1, 0.5 }, shade(wood, 0.85), "Wood", { 0, 20, 0 }, { name = "Root" }),
	}
end

local cache = {}

-- The recipe for `kind` in `paletteId` (a SceneryModels.Palettes key) and `variant`
-- (1 .. Kinds[kind].variants). The table is shared: do not modify it.
function SceneryModels.Get(kind: string, paletteId: string, variant: number?)
	local info, palette = SceneryModels.Kinds[kind], SceneryModels.Palettes[paletteId]
	if info == nil or palette == nil then
		return nil
	end
	local which = math.clamp(variant or 1, 1, info.variants)
	local key = kind .. "/" .. paletteId .. "/" .. which
	local recipe = cache[key]
	if recipe == nil then
		recipe = { parts = BUILDERS[kind](palette, which) }
		cache[key] = recipe
	end
	return recipe
end

-- Most parts any variant of `kind` has.
function SceneryModels.MaxParts(kind: string): number
	local most = 0
	for variant = 1, SceneryModels.Kinds[kind].variants do
		most = math.max(most, #SceneryModels.Get(kind, "Temperate", variant).parts)
	end
	return most
end

-- Per-zone scenery (BiomeCatalog zone ids). `clumps` are { tree kind, clump count }
-- pairs (an array, so the build order is fixed); each clump holds clumpSize[1..2]
-- trees within clumpRadius studs of a centre in forest where the zone has it.
-- `boulders` and `logs` are single pieces, `groundcover` { kind, count } pairs of
-- tufts and ferns. Counts are what placement aims for; spots that hit a camp,
-- structure, water or a cliff are dropped, so the island carries a little less.
SceneryModels.Zones = {
	Rimlands = {
		palette = "Temperate",
		clumps = { { "Broadleaf", 5 } },
		clumpSize = { 3, 5 },
		clumpRadius = 36,
		boulders = 12,
		groundcover = { { "Tuft", 26 } },
		logs = 2,
	},
	PinewoodWilds = {
		palette = "Pine",
		clumps = { { "Pine", 14 }, { "Broadleaf", 2 } },
		clumpSize = { 5, 7 },
		clumpRadius = 48,
		boulders = 18,
		groundcover = { { "Tuft", 24 }, { "Fern", 16 } },
		logs = 6,
	},
	MosswickForest = {
		palette = "Moss",
		clumps = { { "Broadleaf", 12 } },
		clumpSize = { 4, 6 },
		clumpRadius = 44,
		boulders = 8,
		groundcover = { { "Fern", 24 }, { "Tuft", 14 } },
		logs = 6,
	},
	EmberhollowCaves = {
		palette = "Ember",
		clumps = { { "Pine", 3 } },
		clumpSize = { 3, 4 },
		clumpRadius = 30,
		boulders = 20,
		groundcover = { { "Tuft", 12 } },
		logs = 2,
	},
	FrostpeakRidge = {
		palette = "Frost",
		clumps = { { "Pine", 7 } },
		clumpSize = { 3, 5 },
		clumpRadius = 34,
		boulders = 26,
		groundcover = { { "Tuft", 6 } },
		logs = 0,
	},
	FallenTemple = {
		palette = "Jungle",
		clumps = { { "Broadleaf", 9 } },
		clumpSize = { 4, 6 },
		clumpRadius = 40,
		boulders = 12,
		groundcover = { { "Fern", 22 }, { "Tuft", 8 } },
		logs = 5,
	},
	Timberwatch = {
		palette = "Temperate",
		clumps = { { "Pine", 4 }, { "Broadleaf", 4 } },
		clumpSize = { 3, 5 },
		clumpRadius = 38,
		boulders = 9,
		groundcover = { { "Tuft", 18 } },
		logs = 3,
	},
	Riverlands = {
		palette = "Temperate",
		clumps = { { "Broadleaf", 5 } },
		clumpSize = { 3, 5 },
		clumpRadius = 36,
		boulders = 8,
		groundcover = { { "Tuft", 22 } },
		logs = 3,
	},
	-- The crater shore and the Keep island carry stones and grass only: the land
	-- bridge, the ramp and the courtyard approach must stay open.
	CraterLake = {
		palette = "Crater",
		clumps = {},
		clumpSize = { 0, 0 },
		clumpRadius = 0,
		boulders = 8,
		groundcover = { { "Tuft", 10 } },
		logs = 0,
	},
	ShatteredKeep = {
		palette = "Crater",
		clumps = {},
		clumpSize = { 0, 0 },
		clumpRadius = 0,
		boulders = 5,
		groundcover = { { "Tuft", 6 } },
		logs = 0,
	},
}

-- The most parts the island's scenery can have (every clump full, every spot kept).
function SceneryModels.WorstCaseParts(): number
	local total = 0
	for _, zone in SceneryModels.Zones do
		for _, clump in zone.clumps do
			total += clump[2] * zone.clumpSize[2] * SceneryModels.MaxParts(clump[1])
		end
		total += zone.boulders * SceneryModels.MaxParts("Boulder")
		for _, cover in zone.groundcover do
			total += cover[2] * SceneryModels.MaxParts(cover[1])
		end
		total += zone.logs * SceneryModels.MaxParts("Log")
	end
	return total
end

return SceneryModels
