-- Placeholder 3D models for the harvestable resource nodes (GDD §4.1, §53; art
-- direction in visuals.md: primitive-fantasy, chunky low-poly, readable
-- silhouettes). One recipe (Recipe) per NodeCatalog node type, pure data so specs
-- can check it; ResourceService keeps the node's invisible hitbox part and
-- decorates it with the recipe (ModelBuilder.Decorate), so real models replace
-- these later without touching gameplay.
--
-- NodeModels.Get(nodeType) -> { hitbox = {x, y, z}, recipe = recipe }?
--   hitbox: the unrotated Block the node harvests through, with its bottom on the
--   ground; sized like NodeCatalog.Looks so harvest reach stays the same (the
--   tree's hitbox is its trunk only; the canopy spreads above and around it).
--   recipe: its origin is the hitbox CENTRE (ground at y = -hitbox.y / 2), facing
--   -Z. Parts are written with y measured up from the ground and lifted by
--   `entry`, so every shape sits on the floor without hand-computed offsets.
-- The returned tables are shared: callers must not modify them.
--
-- Palette: each node keeps its NodeCatalog.Looks colour on its most visible part
-- (ore chunk, berries, cap, trunk...), so ores and berries still read apart at a
-- glance, on a neutral host rock or green leaves. Gems use Glass or Neon accents.
-- Budget: at most NodeModels.MAX_PARTS per node (trees MAX_TREE_PARTS) because the
-- island carries about 400 trees and 1,000 nodes.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Recipe = require(script.Parent.Recipe)
local NodeCatalog = require(ReplicatedStorage.Shared.Resources.NodeCatalog)

local NodeModels = {}

NodeModels.MAX_PARTS = 8
NodeModels.MAX_TREE_PARTS = 6

local part, rgb, shade = Recipe.Part, Recipe.Rgb, Recipe.Shade
local Looks = NodeCatalog.Looks

local function block(size, pos, color, material, rot, extra)
	return part("Block", size, pos, color, material, rot, extra)
end

local function ball(size, pos, color, material, rot, extra)
	return part("Ball", size, pos, color, material, rot, extra)
end

local function wedge(size, pos, color, material, rot, extra)
	return part("Wedge", size, pos, color, material, rot, extra)
end

-- A node's hitbox (its Looks size) and recipe from parts whose y is measured up
-- from the ground; the parts' positions move so the origin is the hitbox centre.
local function entry(nodeType: string, parts)
	local size = Looks[nodeType].size
	local hitbox = { size.X, size.Y, size.Z }
	for _, spec in parts do
		spec.pos[2] -= hitbox[2] / 2
	end
	return { hitbox = hitbox, recipe = { parts = parts } }
end

local function looks(nodeType: string): { number }
	return rgb(Looks[nodeType].color)
end

local MODELS = {}

-- Trees --------------------------------------------------------------------------

-- A broadleaf: root flare, a 14-stud trunk (the hitbox) and a layered canopy of
-- three stacked balls plus a side clump. Six parts.
local LEAF = { 74, 138, 64 }
do
	local trunk = looks("Tree")
	MODELS.Tree = entry("Tree", {
		block({ 3.8, 1.4, 3.8 }, { 0, 0.7, 0 }, shade(trunk, 0.85), "Wood"),
		block({ 2.4, 14, 2.4 }, { 0, 7, 0 }, trunk, "Wood"),
		ball({ 11, 6.5, 11 }, { 0, 10.5, 0 }, shade(LEAF, 0.82), "LeafyGrass"),
		ball({ 9, 6.5, 9 }, { 0.5, 14.5, -0.5 }, LEAF, "LeafyGrass"),
		ball({ 5.5, 5, 5.5 }, { -0.5, 18.2, 0.5 }, shade(LEAF, 1.15), "LeafyGrass"),
		ball({ 6, 5, 6 }, { 4.2, 12.5, 2 }, shade(LEAF, 0.95), "LeafyGrass"),
	})
end

-- Rocks and ores ----------------------------------------------------------------

-- Plain rock: a wide slab, a taller leaning chunk, a wedge and a boulder at its foot.
do
	local base = looks("Rock")
	MODELS.Rock = entry("Rock", {
		block({ 5.8, 2.6, 5.4 }, { 0, 1.3, 0 }, base, "Rock", { 0, 12, 0 }),
		block({ 3.4, 3.8, 3.2 }, { -1.2, 1.9, -1 }, shade(base, 1.12), "Rock", { 0, -28, 0 }),
		wedge({ 2.6, 1.8, 3.2 }, { 2.1, 0.9, 1.8 }, shade(base, 0.88), "Rock", { 0, 150, 0 }),
		block({ 1.6, 1.2, 1.6 }, { 2.3, 0.6, -2.2 }, shade(base, 0.8), "Rock", { 0, 35, 0 }),
	})
end

-- A metal deposit: a dull host rock (low slab and taller block) with four chunks of
-- coloured ore set into it. The layout scales with the node's hitbox. `flip` mirrors
-- it so neighbouring metals do not share a silhouette.
local function oreDeposit(
	nodeType: string,
	host: { number },
	hostMaterial: string,
	ore: { number },
	material: string,
	flip: number
)
	local size = Looks[nodeType].size
	local w, h = size.X, size.Y
	return entry(nodeType, {
		block({ w * 0.96, h * 0.45, w * 0.88 }, { 0, h * 0.225, 0 }, host, hostMaterial, { 0, 8 * flip, 0 }),
		block(
			{ w * 0.6, h * 0.75, w * 0.6 },
			{ -w * 0.16 * flip, h * 0.375, w * 0.12 },
			shade(host, 1.1),
			hostMaterial,
			{ 0, -20 * flip, 0 }
		),
		block(
			{ w * 0.36, h * 0.4, w * 0.32 },
			{ w * 0.3 * flip, h * 0.5, -w * 0.24 },
			ore,
			material,
			{ 0, 25 * flip, 0 }
		),
		wedge(
			{ w * 0.3, h * 0.36, w * 0.4 },
			{ -w * 0.38 * flip, h * 0.42, w * 0.26 },
			shade(ore, 0.9),
			material,
			{ 0, 160 * flip, 0 }
		),
		block(
			{ w * 0.26, h * 0.3, w * 0.26 },
			{ w * 0.08 * flip, h * 0.82, w * 0.1 },
			shade(ore, 1.1),
			material,
			{ 0, 40 * flip, 0 }
		),
		block(
			{ w * 0.2, h * 0.26, w * 0.2 },
			{ -w * 0.04 * flip, h * 0.13, -w * 0.48 },
			ore,
			material,
			{ 0, -15 * flip, 0 }
		),
	})
end

MODELS.CopperDeposit = oreDeposit("CopperDeposit", { 112, 108, 104 }, "Slate", looks("CopperDeposit"), "Metal", 1)
MODELS.IronDeposit = oreDeposit("IronDeposit", { 78, 74, 78 }, "Slate", looks("IronDeposit"), "CorrodedMetal", -1)
MODELS.SilverDeposit = oreDeposit("SilverDeposit", { 104, 106, 112 }, "Slate", looks("SilverDeposit"), "Metal", 1)
MODELS.CobaltDeposit = oreDeposit("CobaltDeposit", { 70, 76, 96 }, "Slate", looks("CobaltDeposit"), "Slate", -1)

-- Gem nodes: a low host rock with tall faceted crystals (Glass), one glowing core.

do
	-- Mithril: pale cold rock with tall foil crystals of different lean.
	local crystal = looks("MithrilDeposit")
	local host = { 96, 110, 116 }
	MODELS.MithrilDeposit = entry("MithrilDeposit", {
		block({ 4.8, 1.8, 4.4 }, { 0, 0.9, 0 }, host, "Slate", { 0, 10, 0 }),
		block({ 3, 2.6, 3 }, { -0.8, 1.5, 0.6 }, shade(host, 1.12), "Slate", { 0, -20, 0 }),
		block({ 1.5, 5.4, 1.5 }, { 0.2, 3.4, 0 }, crystal, "Foil", { 0, 20, 6 }),
		block({ 1.2, 4, 1.2 }, { 1.5, 2.8, 0.8 }, shade(crystal, 0.9), "Foil", { 0, -30, -16 }),
		block({ 1.1, 3.2, 1.1 }, { -1.5, 2.3, -0.6 }, shade(crystal, 1.1), "Foil", { 8, 10, 18 }),
		wedge({ 1.4, 1.6, 1.8 }, { 1.2, 0.9, -1.8 }, crystal, "Foil", { 0, 200, 0 }),
	})

	-- Obsidian: black glassy shards leaning out of dark basalt.
	local shard = looks("ObsidianOutcrop")
	MODELS.ObsidianOutcrop = entry("ObsidianOutcrop", {
		block({ 5, 1.4, 4.6 }, { 0, 0.7, 0 }, { 42, 38, 50 }, "Basalt", { 0, 15, 0 }),
		block({ 1.5, 3.8, 1.5 }, { -0.9, 2.0, 0.3 }, shard, "Glass", { 0, 20, 10 }, { transparency = 0.1 }),
		block(
			{ 1.2, 3, 1.2 },
			{ 1.2, 1.7, -0.6 },
			shade(shard, 1.15),
			"Glass",
			{ -12, 50, -8 },
			{ transparency = 0.1 }
		),
		wedge({ 1.4, 2.2, 1.8 }, { 0.2, 1.2, 1.5 }, shard, "Glass", { 0, 200, 0 }, { transparency = 0.1 }),
		block({ 1, 2, 1 }, { -1.8, 1.4, -1.2 }, shade(shard, 1.25), "Glass", { 14, -25, 0 }, { transparency = 0.1 }),
	})

	-- Jade: green polished crystals from mossy grey stone.
	local jade = looks("JadeVein")
	local jadeHost = { 96, 108, 100 }
	MODELS.JadeVein = entry("JadeVein", {
		block({ 4, 1.5, 3.6 }, { 0, 0.75, 0 }, jadeHost, "Slate", { 0, -10, 0 }),
		block({ 1.4, 4, 1.4 }, { 0.2, 2.5, 0 }, jade, "Glass", { 0, 25, 8 }, { transparency = 0.12 }),
		block({ 1.1, 3, 1.1 }, { 1.2, 2, 0.6 }, shade(jade, 0.85), "Glass", { 0, -20, -18 }, { transparency = 0.12 }),
		block({ 1, 2.6, 1 }, { -1.1, 1.9, -0.5 }, shade(jade, 1.15), "Glass", { 10, 10, 16 }, { transparency = 0.12 }),
		block({ 0.9, 1.6, 0.9 }, { 0.3, 1.2, -1.4 }, jade, "Glass", { -25, 0, 0 }, { transparency = 0.12 }),
	})

	-- Amethyst: a half-buried grey geode shell cracked open on a cluster of purple
	-- prisms around a glowing core.
	local violet = looks("AmethystGeode")
	MODELS.AmethystGeode = entry("AmethystGeode", {
		ball({ 4.2, 3.4, 4.2 }, { 0, 1.5, 0 }, { 116, 108, 126 }, "Rock"),
		block({ 1.2, 3, 1.2 }, { 0, 3, 0 }, violet, "Glass", { 0, 15, 0 }, { transparency = 0.15 }),
		block(
			{ 0.9, 2.4, 0.9 },
			{ 1.2, 2.6, 0.4 },
			shade(violet, 1.2),
			"Glass",
			{ 0, 0, -22 },
			{ transparency = 0.15 }
		),
		block(
			{ 0.9, 2.2, 0.9 },
			{ -1.1, 2.5, -0.5 },
			shade(violet, 0.85),
			"Glass",
			{ 10, 0, 20 },
			{ transparency = 0.15 }
		),
		block({ 0.8, 2, 0.8 }, { 0.2, 2.4, -1.2 }, violet, "Glass", { -25, 0, 0 }, { transparency = 0.15 }),
		ball({ 1.1, 1.1, 1.1 }, { 0.1, 2.5, 0.1 }, { 196, 140, 245 }, "Neon"),
	})

	-- Starstone: dark rock holding tall glowing pale-gold spires.
	local glow = looks("StarstoneOutcrop")
	local dark = { 78, 76, 90 }
	MODELS.StarstoneOutcrop = entry("StarstoneOutcrop", {
		block({ 4, 1.6, 3.6 }, { 0, 0.8, 0 }, dark, "Slate", { 0, 12, 0 }),
		block({ 2.4, 2.6, 2.4 }, { -0.4, 1.5, 0.4 }, shade(dark, 1.12), "Slate", { 0, -25, 0 }),
		block({ 1.3, 3.6, 1.3 }, { 0.4, 2.8, 0.2 }, glow, "Neon", { 0, 25, 8 }),
		block({ 1, 2.4, 1 }, { -1.2, 2.2, -0.8 }, shade(glow, 0.9), "Neon", { 0, -15, -14 }),
		block({ 0.8, 0.8, 0.8 }, { 1.4, 1.2, 1.2 }, glow, "Neon", { 20, 40, 0 }),
	})

	-- Stormglass: short thick glass tubes branching out of a sand mound.
	local glass = looks("StormglassCluster")
	MODELS.StormglassCluster = entry("StormglassCluster", {
		block({ 3.2, 0.8, 3.2 }, { 0, 0.4, 0 }, { 218, 200, 150 }, "Sand", { 0, 20, 0 }),
		block({ 1, 5.6, 1 }, { 0, 3.2, 0 }, glass, "Glass", { 0, 0, 6 }, { transparency = 0.2 }),
		block({ 0.9, 4.2, 0.9 }, { 1, 2.5, 0.4 }, shade(glass, 1.2), "Glass", { 0, 0, -18 }, { transparency = 0.2 }),
		block(
			{ 0.8, 3.4, 0.8 },
			{ -0.9, 2.1, -0.5 },
			shade(glass, 0.85),
			"Glass",
			{ 12, 0, 14 },
			{ transparency = 0.2 }
		),
		block({ 0.6, 2.4, 0.6 }, { 0.3, 1.6, -1 }, shade(glass, 1.3), "Glass", { -22, 0, 0 }, { transparency = 0.2 }),
	})
end

-- Clay: a flat pit of orange clay, two stacked mounds and a few lumps.
do
	local clay = looks("ClayDeposit")
	MODELS.ClayDeposit = entry("ClayDeposit", {
		block({ 5, 1, 5 }, { 0, 0.5, 0 }, shade(clay, 0.9), "Mud", { 0, 10, 0 }),
		block({ 3.4, 1.2, 3.2 }, { 0.3, 1.4, 0 }, clay, "Mud", { 0, -20, 0 }),
		ball({ 1.6, 1, 1.6 }, { -1.9, 0.5, 1.6 }, shade(clay, 1.12), "Mud"),
		ball({ 1.3, 0.9, 1.3 }, { 1.9, 0.45, -1.7 }, shade(clay, 1.2), "Mud"),
		ball({ 1.1, 0.8, 1.1 }, { -2, 0.4, -1.4 }, shade(clay, 0.8), "Mud"),
	})
end

-- Plants and bushes -------------------------------------------------------------

-- Fiber: a tuft of tall, slightly splayed blades on a small mound.
do
	local blade = looks("FiberPlant")
	MODELS.FiberPlant = entry("FiberPlant", {
		ball({ 1.8, 0.8, 1.8 }, { 0, 0.3, 0 }, shade(blade, 0.7), "Grass"),
		block({ 0.35, 3, 0.35 }, { 0, 1.5, 0 }, blade, "Grass"),
		block({ 0.35, 2.6, 0.35 }, { 0.5, 1.3, 0.2 }, shade(blade, 1.12), "Grass", { 0, 0, -14 }),
		block({ 0.35, 2.4, 0.35 }, { -0.5, 1.2, 0.1 }, shade(blade, 0.9), "Grass", { 0, 0, 16 }),
		block({ 0.35, 2.2, 0.35 }, { 0.1, 1.1, -0.5 }, shade(blade, 1.2), "Grass", { -14, 0, 0 }),
		block({ 0.35, 2.4, 0.35 }, { -0.1, 1.2, 0.5 }, blade, "Grass", { 15, 0, 0 }),
	})
end

-- Herbs: two leafy mounds with a few pale flowers.
do
	local leaf = looks("HerbShrub")
	local flower = { 240, 230, 200 }
	MODELS.HerbShrub = entry("HerbShrub", {
		ball({ 3, 1.6, 3 }, { 0, 0.8, 0 }, leaf, "Grass"),
		ball({ 1.8, 1.3, 1.8 }, { 0.5, 1.3, -0.4 }, shade(leaf, 1.15), "Grass"),
		ball({ 0.5, 0.5, 0.5 }, { 0.4, 2, -0.3 }, flower, "SmoothPlastic"),
		ball({ 0.5, 0.5, 0.5 }, { -0.8, 1.4, 0.6 }, shade(flower, 0.95), "SmoothPlastic"),
		ball({ 0.5, 0.5, 0.5 }, { 1, 1.2, 0.5 }, flower, "SmoothPlastic"),
	})
end

-- A rounded bush: three leaf balls with five dots (berries, nuts). 3x3x3.
local function bush(leaf: { number }, dot: { number }, dotSize: number, dotMaterial: string?, extra)
	local parts = {
		ball({ 3.2, 2.4, 3 }, { 0, 1.2, 0 }, leaf, "Grass"),
		ball({ 2.2, 2, 2.2 }, { 0.3, 2, -0.2 }, shade(leaf, 1.12), "Grass"),
		ball({ 1.8, 1.6, 1.8 }, { -1, 0.9, 1 }, shade(leaf, 0.85), "Grass"),
	}
	local spots = {
		{ 1.12, 1.8, -0.75 },
		{ -0.96, 1.92, 0.78 },
		{ 0.63, 2.9, 0.13 },
		{ -0.58, 2.4, -0.7 },
		{ -0.16, 1.44, -1.46 },
	}
	for index, spot in spots do
		local d = dotSize * (if index % 2 == 0 then 0.85 else 1)
		table.insert(parts, ball({ d, d, d }, spot, dot, dotMaterial or "SmoothPlastic"))
	end
	for _, more in extra or {} do
		table.insert(parts, more)
	end
	return parts
end

local GREEN = { 70, 124, 62 }
MODELS.RedberryBush = entry("RedberryBush", bush(GREEN, looks("RedberryBush"), 0.6))
MODELS.SweetberryBush = entry("SweetberryBush", bush(shade(GREEN, 1.1), looks("SweetberryBush"), 0.6))
MODELS.RaspberryBush = entry("RaspberryBush", bush(shade(GREEN, 0.95), looks("RaspberryBush"), 0.55))
MODELS.ElderberryShrub = entry("ElderberryShrub", bush({ 62, 98, 60 }, looks("ElderberryShrub"), 0.7))
MODELS.JuniperShrub = entry("JuniperShrub", bush(looks("JuniperShrub"), { 84, 96, 160 }, 0.6))
MODELS.HazelShrub = entry("HazelShrub", bush(looks("HazelShrub"), { 112, 78, 46 }, 0.55, "Wood"))

-- Thorn shrub: two olive mounds bristling with brown thorns (wedges).
do
	local leaf = looks("ThornShrub")
	local thorn = { 76, 56, 40 }
	MODELS.ThornShrub = entry("ThornShrub", {
		ball({ 3.2, 2.4, 3 }, { 0, 1.2, 0 }, leaf, "Grass"),
		ball({ 2.2, 1.9, 2.2 }, { 0.3, 2, -0.2 }, shade(leaf, 0.85), "Grass"),
		wedge({ 0.5, 1.4, 0.7 }, { 1.5, 1.6, 0.2 }, thorn, "Wood", { 0, 90, -50 }),
		wedge({ 0.5, 1.4, 0.7 }, { -1.5, 1.5, -0.4 }, thorn, "Wood", { 0, -90, 50 }),
		wedge({ 0.5, 1.4, 0.7 }, { 0.2, 1.5, -1.5 }, thorn, "Wood", { 50, 0, 0 }),
		wedge({ 0.5, 1.6, 0.7 }, { 0.2, 2.9, 0.2 }, thorn, "Wood", { 0, 45, 0 }),
		wedge({ 0.5, 1.2, 0.7 }, { -0.6, 0.9, 1.5 }, thorn, "Wood", { -50, 180, 0 }),
	})
end

-- Frost shrub: two icy mounds with pale glass shards.
do
	local ice = looks("FrostShrub")
	local shardColor = { 220, 242, 255 }
	MODELS.FrostShrub = entry("FrostShrub", {
		ball({ 3.2, 2.4, 3 }, { 0, 1.2, 0 }, ice, "Ice"),
		ball({ 2.2, 1.9, 2.2 }, { -0.3, 2, 0.2 }, shade(ice, 1.1), "Ice"),
		block({ 0.6, 2.4, 0.6 }, { 0.8, 2.6, -0.3 }, shardColor, "Glass", { 0, 20, -14 }, { transparency = 0.2 }),
		block(
			{ 0.5, 1.8, 0.5 },
			{ -0.9, 2.4, 0.4 },
			shade(shardColor, 0.9),
			"Glass",
			{ 10, 0, 18 },
			{ transparency = 0.2 }
		),
		wedge({ 0.7, 1.2, 0.9 }, { 0.2, 0.9, -1.5 }, shardColor, "Glass", { 0, 0, 0 }, { transparency = 0.2 }),
		block({ 0.5, 1.5, 0.5 }, { 0.1, 3, 0.1 }, shardColor, "Glass", { 0, 40, 0 }, { transparency = 0.2 }),
	})
end

-- Mushrooms ------------------------------------------------------------------------

-- A patch of three mushrooms (stem and squashed ball cap each) in a 2x2 hitbox:
-- {x, z, stem height, cap diameter}. `flat` squashes the caps further.
local PATCH = { { -0.2, 0.1, 1.3, 1.5 }, { 0.6, -0.5, 0.9, 1.1 }, { -0.6, -0.6, 0.7, 0.9 } }

local function patch(stem: { number }, cap: { number }, flat: number, material: string?)
	local parts = {}
	for _, m in PATCH do
		local x, z, stemHeight, d = m[1], m[2], m[3], m[4]
		table.insert(parts, block({ 0.4, stemHeight, 0.4 }, { x, stemHeight / 2, z }, stem, "SmoothPlastic"))
		table.insert(parts, ball({ d, d * flat, d }, { x, stemHeight + d * 0.2, z }, cap, material or "SmoothPlastic"))
	end
	return parts
end

MODELS.CaveMushroomPatch = entry("CaveMushroomPatch", patch({ 236, 230, 214 }, looks("CaveMushroomPatch"), 0.65))

do
	local parts = patch({ 232, 222, 200 }, looks("RedcapMushroomPatch"), 0.65)
	local spot = { 245, 240, 230 }
	table.insert(parts, ball({ 0.3, 0.3, 0.3 }, { 0.05, 2.05, -0.1 }, spot))
	table.insert(parts, ball({ 0.25, 0.25, 0.25 }, { -0.6, 1.85, 0.4 }, spot))
	MODELS.RedcapMushroomPatch = entry("RedcapMushroomPatch", parts)
end

do
	local parts = patch({ 204, 174, 132 }, looks("ChestnutMushroomPatch"), 0.5)
	table.insert(parts, ball({ 0.5, 0.35, 0.5 }, { 0.9, 0.2, 0.7 }, { 118, 76, 42 }))
	MODELS.ChestnutMushroomPatch = entry("ChestnutMushroomPatch", parts)
end

-- The recipe for `nodeType`, or nil for a type without a model.
function NodeModels.Get(nodeType: string)
	return MODELS[nodeType]
end

return NodeModels
