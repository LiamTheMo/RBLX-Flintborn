-- Placeholder 3D models for world events and their sites (GDD §7, §9, §51, §54;
-- art direction in visuals.md §8: stout timber, thick pointed palisade logs,
-- chunky stones, hide tents, a small campfire of logs and stones). Pure data
-- (Recipe) so headless specs can check every recipe; the services keep their
-- gameplay parts (prompts, hitboxes, tags, attributes) and dress them with these
-- through ModelBuilder, so real models replace a recipe later without touching
-- gameplay:
--   EventDirectorService  structure walls, dressing and gates, rare nodes, loot piles
--   CacheService          the supply chest       MeteorService       the crater and rock
--   RitualService         the ritual altar       ExtractionService   the portal ring
-- Nothing here collides or blocks rays (ModelBuilder.Build / Decorate defaults):
-- the invisible or plain gameplay part stays the solid, raidable thing.
--
-- Origins (every recipe faces -Z, +Y up; "ground" recipes write y up from the
-- ground, so shapes sit on the floor):
--   Structure[style]  the event centre on the ground (the cache and loot node
--                     stand there, so the middle is left free).
--   Gate[style]       the doorway on the wall ring, on the ground; local -Z points
--                     at the structure centre, X runs across the gap.
--   Wall(style, h)    the centre of one 10 x h x 1.5 wall segment, -Z the inside.
--   Chest(accent)     the centre of the 4 x 3 x 3 cache hitbox.
--   Meteor            the event centre on the ground (the crater floor).
--   OreNode / PlantNode / LootPile   the centre of the node's hitbox.
--   Altar             the centre of the 6 x 3 x 6 altar slab.
--   Portal(accent)    the centre of the portal's 6-stud disc, world-aligned.
-- Rotations are single-axis (or Y only) so they read the same whatever Euler order
-- the engine applies. Parts named "Glow" are the lit ones services may recolour.

local Recipe = require(script.Parent.Recipe)

local PropModels = {}

-- Part limit per recipe (the event props are spawned a few at a time, not by the thousand).
PropModels.MAX_PARTS = 25

local part, shade = Recipe.Part, Recipe.Shade

-- The ring of walls an event structure stands in. EventDirectorService builds its
-- gameplay walls from these numbers, so the dressing lines up with the gaps: the
-- doorway is the segment left out at `doorway`, and Ruins also lose every
-- `ruinGap`-th segment to crumbling.
PropModels.RING = { radius = 16, segments = 10, width = 10, thickness = 1.5, height = 9, doorway = 1, ruinGap = 3 }
-- Ruin walls crumble to a random height in this range.
PropModels.RUIN_HEIGHT = { 3, 7 }
-- Structure dressing sinks this far so a slope never leaves it hovering.
PropModels.STRUCTURE_SINK = 0.5
PropModels.STYLES = { "Camp", "Fort", "Ruin" }

-- The chest lid hinges here (cache hitbox space) and swings open this far; parts
-- named with LID_PREFIX turn with it and the CHEST_GLOW ones go dark.
PropModels.CHEST_HINGE = { 0, 0.2, 1.4 }
PropModels.CHEST_OPEN_DEGREES = 110
PropModels.LID_PREFIX = "Lid"
PropModels.CHEST_GLOW = { Glow = true, LidGem = true }

-- The altar's lit parts, and the colours the ritual swaps them between.
PropModels.ALTAR_GLOW = "Glow"

-- Plant event nodes that are not a plain patch (anything else is a Patch).
PropModels.PLANT_VARIANTS = {
	IronbarkSapling = "Sapling",
	ElderIronwood = "Sapling",
	WildbloomShrub = "Bloom",
	AncientWildbloom = "Bloom",
	Emberbloom = "Bloom",
	StarfallLotus = "Bloom",
}

-- Palette (visuals.md §10: warm timber, cool grey stone, tan hide, fire accents).
local WOOD = { 112, 80, 52 }
local WOOD_DARK = { 84, 60, 40 }
local WOOD_LIGHT = { 150, 112, 70 }
local BARK = { 98, 70, 46 }
local STONE = { 124, 120, 112 }
local STONE_DARK = { 92, 90, 86 }
local STONE_LIGHT = { 150, 146, 138 }
local MOSS = { 88, 112, 64 }
local HIDE = { 176, 140, 96 }
local HIDE_DARK = { 140, 104, 70 }
local CREAM = { 206, 184, 146 }
local ROPE = { 170, 148, 100 }
local METAL = { 96, 102, 112 }
local METAL_DARK = { 60, 64, 72 }
local CHAR = { 40, 34, 32 }
local EMBER = { 255, 140, 40 }
local LEAF = { 74, 138, 64 }
local LEAF_DARK = { 56, 110, 52 }
local DIRT = { 112, 88, 60 }
local SCORCH = { 52, 42, 40 }
local BANNER = { 150, 40, 36 }

local function mix(a: { number }, b: { number }, amount: number): { number }
	return {
		math.round(a[1] + (b[1] - a[1]) * amount),
		math.round(a[2] + (b[2] - a[2]) * amount),
		math.round(a[3] + (b[3] - a[3]) * amount),
	}
end

local function lifted(parts, dy: number)
	for _, spec in parts do
		spec.pos[2] += dy
	end
	return parts
end

local function add(parts, ...)
	for _, spec in { ... } do
		table.insert(parts, spec)
	end
end

-- A standing log: a Cylinder's axis is X, so it turns 90 degrees about Z to stand.
local function post(length: number, width: number, pos, color, material: string?, name: string?)
	return part("Cylinder", { length, width, width }, pos, color, material, { 0, 0, 90 }, { name = name })
end

-- Ring geometry ----------------------------------------------------------------

-- The ring's centre line at `index`, relative to the structure centre: x, z.
function PropModels.RingPoint(index: number, radius: number?): (number, number)
	local ring = PropModels.RING
	local angle = (index / ring.segments) * math.pi * 2
	local distance = radius or ring.radius
	return math.cos(angle) * distance, math.sin(angle) * distance
end

-- Whether a `style` structure has a wall segment at ring `index` (false for the
-- doorway and, in a Ruin, the crumbled gaps).
function PropModels.HasWall(style: string, index: number): boolean
	local ring = PropModels.RING
	if index == ring.doorway then
		return false
	end
	return style ~= "Ruin" or index % ring.ruinGap ~= 0
end

-- Walls ------------------------------------------------------------------------

local PALISADE_HEIGHTS = { 0.98, 0.9, 1.05, 0.95, 0.88, 1.02, 0.92 }
local FENCE_X = { -4.75, -2.85, -0.95, 0.95, 2.85, 4.75 }
local FENCE_PANELS = { 0.95, 1, 0.93, 0.98, 0.96 }

-- Sharpened logs side by side (no gaps) with two lashed rails on the inside.
local function palisade(height: number)
	local ring = PropModels.RING
	local half = height / 2
	local parts = {}
	local spacing = ring.width / #PALISADE_HEIGHTS
	for index, factor in PALISADE_HEIGHTS do
		local x = -ring.width / 2 + spacing * (index - 0.5)
		local length = height * factor
		local bottom = -half - 0.3
		add(
			parts,
			post(length, 1.5, { x, bottom + length / 2, 0 }, WOOD, "Wood", "Post"),
			part("Wedge", { 1.1, 1, 1.1 }, { x, bottom + length + 0.5, 0 }, WOOD_LIGHT, "Wood", nil, { name = "Point" })
		)
	end
	for _, y in { 2, 6.2 } do
		add(
			parts,
			part("Block", { ring.width + 0.2, 0.45, 0.4 }, { 0, -half + y, -0.95 }, WOOD_DARK, "Wood", nil, {
				name = "Rail",
			})
		)
	end
	return parts
end

-- Hide screens stretched between poles, lashed with rope: a raider fence.
local function fence(height: number)
	local half = height / 2
	local parts = {}
	for index, x in FENCE_X do
		local length = height + 0.2 + (index % 3) * 0.3
		add(parts, post(length, 0.7, { x, -half - 0.3 + length / 2, 0 }, WOOD_DARK, "Wood", "Pole"))
	end
	for index, factor in FENCE_PANELS do
		local panel = height * factor
		add(
			parts,
			part(
				"Block",
				{ 1.9, panel, 0.25 },
				{ (FENCE_X[index] + FENCE_X[index + 1]) / 2, -half - 0.2 + panel / 2, -0.2 },
				if index % 2 == 0 then HIDE_DARK else HIDE,
				"Fabric",
				nil,
				{ name = "Hide" }
			)
		)
	end
	for _, y in { 2.2, 6 } do
		add(
			parts,
			part("Block", { PropModels.RING.width, 0.25, 0.35 }, { 0, -half + y, -0.45 }, ROPE, "Fabric", nil, {
				name = "Lashing",
			})
		)
	end
	return parts
end

-- A crumbling stone wall: the plain wall stays visible, so this adds broken cap
-- stones, moss, a crack and rubble at its feet.
local function ruinWall(height: number)
	local half = height / 2
	local floor = -half
	return {
		part("Block", { 2.8, 0.9, 1.9 }, { -2.9, half + 0.35, 0 }, STONE_LIGHT, "Cobblestone", { 0, 8, 0 }, {
			name = "Cap",
		}),
		part("Block", { 1.9, 0.7, 1.8 }, { 0.8, half + 0.25, 0.1 }, STONE, "Cobblestone", { 0, -12, 0 }, {
			name = "Cap",
		}),
		part("Block", { 1.4, 1.1, 1.6 }, { 3.4, half + 0.4, 0 }, STONE_LIGHT, "Cobblestone", { 0, 20, 0 }, {
			name = "Cap",
		}),
		part("Block", { 2.6, 0.5, 0.15 }, { -1.2, half - 0.6, -0.8 }, MOSS, "Grass", nil, { name = "Moss" }),
		part("Block", { 0.5, height * 0.6, 0.12 }, { 3.6, floor + height * 0.3, -0.8 }, MOSS, "Grass", nil, {
			name = "Ivy",
		}),
		part("Block", { 0.12, height * 0.7, 0.1 }, { -3.8, -0.1, -0.8 }, STONE_DARK, "Slate", { 0, 0, 10 }, {
			name = "Crack",
		}),
		part("Block", { 1.8, 1, 1.4 }, { -3.2, floor + 0.4, 1.7 }, STONE, "Cobblestone", { 0, 30, 0 }, {
			name = "Rubble",
		}),
		part("Block", { 1.2, 0.8, 1.2 }, { 1.5, floor + 0.3, 2 }, STONE_DARK, "Cobblestone", { 0, -20, 0 }, {
			name = "Rubble",
		}),
		part("Block", { 2, 0.9, 1.5 }, { 4, floor + 0.35, 1.6 }, STONE, "Cobblestone", { 0, 12, 0 }, {
			name = "Rubble",
		}),
		part("Block", { 1.5, 0.8, 1.3 }, { -1, floor + 0.3, -1.7 }, STONE_LIGHT, "Cobblestone", { 0, 40, 0 }, {
			name = "Rubble",
		}),
		part("Block", { 1.1, 0.7, 1.1 }, { 2.6, floor + 0.25, -1.9 }, STONE_DARK, "Cobblestone", { 0, -35, 0 }, {
			name = "Rubble",
		}),
	}
end

-- The look of one wall segment of `style` for a gameplay wall `height` studs tall.
-- hostVisible: the plain wall part stays drawn (a Ruin's stone); otherwise the
-- recipe draws the whole wall and the part goes invisible.
function PropModels.Wall(style: string, height: number)
	if style == "Ruin" then
		return { parts = ruinWall(height), hostVisible = true }
	elseif style == "Fort" then
		return { parts = palisade(height), hostVisible = false }
	end
	return { parts = fence(height), hostVisible = false }
end

-- Structure dressing -------------------------------------------------------------

-- An A-frame hide tent: two sloped hide slabs and a ridge pole. `alongX` runs the
-- ridge along X (slabs tilt about X), else along Z (slabs tilt about Z). (x, z) is
-- the tent's centre on the ground.
local function tent(parts, x: number, z: number, alongX: boolean, colors)
	local width, length, rise = 5, 5.5, 3.6
	local slope = math.sqrt((width / 2) ^ 2 + rise ^ 2)
	local tilt = math.deg(math.atan2(rise, width / 2))
	if alongX then
		add(
			parts,
			part("Block", { length, 0.25, slope }, { x, rise / 2, z + width / 4 }, colors[1], "Fabric", { tilt, 0, 0 }, {
				name = "TentHide",
			}),
			part("Block", { length, 0.25, slope }, { x, rise / 2, z - width / 4 }, colors[2], "Fabric", { -tilt, 0, 0 }, {
				name = "TentHide",
			}),
			part("Cylinder", { length + 0.8, 0.3, 0.3 }, { x, rise + 0.05, z }, WOOD_DARK, "Wood", nil, {
				name = "Ridge",
			})
		)
	else
		add(
			parts,
			part("Block", { slope, 0.25, length }, { x + width / 4, rise / 2, z }, colors[1], "Fabric", { 0, 0, -tilt }, {
				name = "TentHide",
			}),
			part("Block", { slope, 0.25, length }, { x - width / 4, rise / 2, z }, colors[2], "Fabric", { 0, 0, tilt }, {
				name = "TentHide",
			}),
			part("Cylinder", { length + 0.8, 0.3, 0.3 }, { x, rise + 0.05, z }, WOOD_DARK, "Wood", { 0, 90, 0 }, {
				name = "Ridge",
			})
		)
	end
end

-- Three hide tents, a fire pit with glowing embers, log seats, crates and a skull
-- pole around the (free) middle: 24 parts.
local function camp()
	local parts = {}
	tent(parts, -9, -3, true, { HIDE, HIDE_DARK })
	tent(parts, -2, 10, false, { CREAM, HIDE })
	tent(parts, 9.5, -4, true, { HIDE_DARK, CREAM })
	local fx, fz = 0.5, -8
	for index, offset in { { 1.2, 0 }, { -1.2, 0.2 }, { 0, 1.2 }, { 0.2, -1.2 } } do
		add(
			parts,
			part("Block", { 0.9, 0.6, 0.9 }, { fx + offset[1], 0.3, fz + offset[2] }, STONE, "Cobblestone", {
				0,
				index * 25,
				0,
			}, { name = "FireStone" })
		)
	end
	add(
		parts,
		part("Cylinder", { 0.3, 2, 2 }, { fx, 0.1, fz }, CHAR, "Slate", { 0, 0, 90 }, { name = "Ashes" }),
		part("Ball", { 0.55, 0.55, 0.55 }, { fx, 0.45, fz }, EMBER, "Neon", nil, { name = "Glow" }),
		part("Ball", { 0.45, 0.45, 0.45 }, { fx - 0.4, 0.35, fz + 0.3 }, EMBER, "Neon", nil, { name = "Glow" }),
		part("Ball", { 0.4, 0.4, 0.4 }, { fx + 0.4, 0.35, fz - 0.3 }, shade(EMBER, 1.3), "Neon", nil, { name = "Glow" }),
		part("Cylinder", { 3, 0.8, 0.8 }, { fx, 0.4, fz + 3.2 }, WOOD, "Wood", nil, { name = "Seat" }),
		part("Cylinder", { 3, 0.8, 0.8 }, { fx - 3.3, 0.4, fz - 1 }, WOOD, "Wood", { 0, 90, 0 }, { name = "Seat" }),
		part("Cylinder", { 3, 0.8, 0.8 }, { fx + 3.3, 0.4, fz - 1.4 }, WOOD, "Wood", { 0, 70, 0 }, { name = "Seat" }),
		part("Block", { 1.4, 1.4, 1.4 }, { 7, 0.7, 5 }, WOOD_LIGHT, "WoodPlanks", { 0, 10, 0 }, { name = "Crate" }),
		part("Block", { 1.4, 1.4, 1.4 }, { 8.6, 0.7, 4.4 }, WOOD, "WoodPlanks", { 0, -20, 0 }, { name = "Crate" }),
		post(6, 0.35, { -6, 3 - 0.3, 6.5 }, WOOD_DARK, "Wood", "SkullPole"),
		part("Ball", { 0.9, 0.9, 0.9 }, { -6, 6.1, 6.5 }, CREAM, nil, nil, { name = "Skull" })
	)
	return parts
end

-- The Fort's watch platform on stilts with a ladder, a rack of spears and a
-- banner pole: 22 parts. It stands at ring point 7 (the far side from the gate).
local function fort()
	local parts = {}
	local px, pz = PropModels.RingPoint(7, 11)
	for _, sx in { -1.7, 1.7 } do
		for _, sz in { -1.7, 1.7 } do
			add(parts, post(7.6, 0.7, { px + sx, 3.8, pz + sz }, WOOD, "Wood", "Stilt"))
		end
	end
	add(
		parts,
		part("Block", { 4.6, 0.4, 4.6 }, { px, 7.8, pz }, WOOD_LIGHT, "WoodPlanks", nil, { name = "Deck" }),
		part("Block", { 4.6, 1, 0.25 }, { px, 8.5, pz - 2.2 }, WOOD, "WoodPlanks", nil, { name = "Rail" }),
		part("Block", { 4.6, 1, 0.25 }, { px, 8.5, pz + 2.2 }, WOOD, "WoodPlanks", nil, { name = "Rail" }),
		part("Block", { 0.25, 1, 4.6 }, { px - 2.2, 8.5, pz }, WOOD, "WoodPlanks", nil, { name = "Rail" }),
		part("Block", { 0.25, 4.5, 0.25 }, { px, 3, pz - 1.7 }, WOOD_DARK, "Wood", { 0, 0, 48 }, { name = "Brace" }),
		part("Block", { 0.25, 4.5, 0.25 }, { px, 3, pz + 1.7 }, WOOD_DARK, "Wood", { 0, 0, -48 }, { name = "Brace" }),
		part("Block", { 0.2, 7.6, 0.2 }, { px + 2.1, 3.9, pz - 0.6 }, WOOD_DARK, "Wood", nil, { name = "Ladder" }),
		part("Block", { 0.2, 7.6, 0.2 }, { px + 2.1, 3.9, pz + 0.6 }, WOOD_DARK, "Wood", nil, { name = "Ladder" })
	)
	for _, y in { 1.4, 3, 4.6, 6.2 } do
		add(parts, part("Block", { 0.15, 0.15, 1.4 }, { px + 2.1, y, pz }, WOOD_LIGHT, "Wood", nil, { name = "Rung" }))
	end
	add(
		parts,
		part("Block", { 0.3, 2.6, 0.3 }, { 4.3, 1.3, -10 }, WOOD, "Wood", nil, { name = "RackPost" }),
		part("Block", { 0.3, 2.6, 0.3 }, { 6.7, 1.3, -10 }, WOOD, "Wood", nil, { name = "RackPost" }),
		part("Block", { 2.8, 0.2, 0.2 }, { 5.5, 2.3, -10 }, WOOD_DARK, "Wood", nil, { name = "RackBar" }),
		part("Block", { 1.4, 1.4, 1.4 }, { 7, 0.7, 4 }, WOOD_LIGHT, "WoodPlanks", { 0, 15, 0 }, { name = "Crate" }),
		part("Block", { 1.4, 1.4, 1.4 }, { 7.4, 2.1, 3.8 }, WOOD, "WoodPlanks", { 0, -10, 0 }, { name = "Crate" }),
		post(8, 0.4, { 2, 3.7, -8 }, WOOD_DARK, "Wood", "BannerPole"),
		part("Block", { 0.1, 2.6, 1.8 }, { 2, 6.4, -7.1 }, BANNER, "Fabric", nil, { name = "Banner" })
	)
	return parts
end

-- Broken columns standing in the crumbled gaps, a fallen column, rubble heaps and
-- moss patches: 20 parts.
local function ruin()
	local ring = PropModels.RING
	local parts = {}
	local shafts = { 5.5, 3.5, 2.2 }
	local slot = 0
	for index = 1, ring.segments do
		if index ~= ring.doorway and not PropModels.HasWall("Ruin", index) then
			slot += 1
			local x, z = PropModels.RingPoint(index, ring.radius - 1)
			local length = shafts[(slot - 1) % #shafts + 1]
			add(
				parts,
				post(1.2, 2.8, { x, 0.5, z }, STONE_DARK, "Cobblestone", "ColumnBase"),
				post(length, 2, { x, 1.1 + length / 2, z }, STONE, "Cobblestone", "Column"),
				part(
					"Block",
					{ 1.8, 1.2, 1.4 },
					{ x + 2, 0.6, z + 1.4 },
					STONE_LIGHT,
					"Cobblestone",
					{ 0, slot * 37, 0 },
					{ name = "Fallen" }
				)
			)
		end
	end
	add(
		parts,
		part("Cylinder", { 6, 1.8, 1.8 }, { -3, 0.8, 5 }, STONE, "Cobblestone", { 0, 25, 0 }, { name = "FallenColumn" })
	)
	local heaps = { { 5, -6 }, { -6, -4 }, { -2, 8 }, { 7, 5 } }
	for index, heap in heaps do
		add(
			parts,
			part(
				"Block",
				{ 2.4, 1.2, 2 },
				{ heap[1], 0.5, heap[2] },
				STONE,
				"Cobblestone",
				{ 0, index * 31, 0 },
				{ name = "Rubble" }
			),
			part(
				"Block",
				{ 1.4, 0.9, 1.2 },
				{ heap[1] + 1.3, 0.35, heap[2] - 0.8 },
				STONE_DARK,
				"Cobblestone",
				{ 0, -index * 23, 0 },
				{ name = "Rubble" }
			)
		)
	end
	add(
		parts,
		part("Block", { 3, 0.1, 2.4 }, { -5, 0.05, 1 }, MOSS, "Grass", nil, { name = "Moss" }),
		part("Block", { 2.6, 0.1, 3 }, { 3, 0.05, 2 }, MOSS, "Grass", { 0, 30, 0 }, { name = "Moss" })
	)
	return parts
end

PropModels.Structure = {
	Camp = { parts = camp() },
	Fort = { parts = fort() },
	Ruin = { parts = ruin() },
}

-- Gates -------------------------------------------------------------------------

-- Two tall gate posts with a lintel above head height, hanging banners and
-- braziers: the Fort's entrance.
local function fortGate()
	return {
		post(11, 1.6, { -4.2, 5.2, 0 }, WOOD, "Wood", "GatePost"),
		post(11, 1.6, { 4.2, 5.2, 0 }, WOOD, "Wood", "GatePost"),
		part("Wedge", { 1.2, 1.2, 1.2 }, { -4.2, 11.3, 0 }, WOOD_LIGHT, "Wood", nil, { name = "Point" }),
		part("Wedge", { 1.2, 1.2, 1.2 }, { 4.2, 11.3, 0 }, WOOD_LIGHT, "Wood", nil, { name = "Point" }),
		part("Block", { 9.6, 0.8, 1 }, { 0, 10.3, 0 }, WOOD_DARK, "WoodPlanks", nil, { name = "Lintel" }),
		part("Block", { 1.6, 3, 0.12 }, { -2, 8.4, -0.55 }, BANNER, "Fabric", nil, { name = "Banner" }),
		part("Block", { 1.6, 3, 0.12 }, { 2, 8.4, -0.55 }, BANNER, "Fabric", nil, { name = "Banner" }),
		part("Ball", { 0.8, 0.8, 0.8 }, { -4.2, 8.2, -1.2 }, EMBER, "Neon", nil, { name = "Glow" }),
		part("Ball", { 0.8, 0.8, 0.8 }, { 4.2, 8.2, -1.2 }, EMBER, "Neon", nil, { name = "Glow" }),
	}
end

-- A cracked arch: one full pier and lintel, one broken pier, a fallen keystone.
local function ruinGate()
	return {
		part("Block", { 2.2, 3, 2.2 }, { -3.9, 1.5, 0 }, STONE, "Cobblestone", nil, { name = "Pier" }),
		part("Block", { 1.9, 3.2, 1.9 }, { -3.9, 4.6, 0 }, STONE_LIGHT, "Cobblestone", { 0, 6, 0 }, { name = "Pier" }),
		part("Block", { 2.2, 3, 2.2 }, { 3.9, 1.5, 0 }, STONE, "Cobblestone", nil, { name = "Pier" }),
		part("Block", { 1.9, 1.6, 1.9 }, { 3.9, 3.8, 0 }, STONE_DARK, "Cobblestone", { 0, -8, 0 }, { name = "Pier" }),
		part("Block", { 4.6, 1.3, 1.8 }, { -2.2, 7, 0 }, STONE_LIGHT, "Cobblestone", { 0, 0, -6 }, { name = "Lintel" }),
		part("Block", { 1.4, 1.4, 1.6 }, { 1.2, 0.7, -2.2 }, STONE, "Cobblestone", { 0, 25, 0 }, { name = "Keystone" }),
		part("Block", { 2.6, 1, 1.6 }, { 2.4, 0.5, 2 }, STONE_DARK, "Cobblestone", { 0, -35, 0 }, { name = "Fallen" }),
		part("Block", { 1.5, 0.8, 1.2 }, { -1.5, 0.4, -1.6 }, STONE_LIGHT, "Cobblestone", { 0, 15, 0 }, { name = "Rubble" }),
		part("Block", { 3.4, 0.1, 2.2 }, { -3.9, 3.1, 0 }, MOSS, "Grass", nil, { name = "Moss" }),
	}
end

-- Two hide poles with skulls, a rope between them and flags: the Camp's entrance.
local function campGate()
	return {
		post(7, 0.5, { -4, 3.2, 0 }, WOOD_DARK, "Wood", "GatePole"),
		post(7, 0.5, { 4, 3.2, 0 }, WOOD_DARK, "Wood", "GatePole"),
		part("Ball", { 0.8, 0.8, 0.8 }, { -4, 7.2, 0 }, CREAM, nil, nil, { name = "Skull" }),
		part("Ball", { 0.8, 0.8, 0.8 }, { 4, 7.2, 0 }, CREAM, nil, nil, { name = "Skull" }),
		part("Block", { 8, 0.12, 0.12 }, { 0, 6.4, 0 }, ROPE, "Fabric", nil, { name = "Rope" }),
		part("Block", { 1.2, 2, 0.1 }, { -4, 5.2, -0.4 }, HIDE, "Fabric", nil, { name = "Flag" }),
		part("Block", { 1.2, 2, 0.1 }, { 4, 5.2, -0.4 }, BANNER, "Fabric", nil, { name = "Flag" }),
	}
end

PropModels.Gate = {
	Camp = { parts = campGate() },
	Fort = { parts = fortGate() },
	Ruin = { parts = ruinGate() },
}

-- Cache chest -------------------------------------------------------------------

-- A wood chest with metal bands and a lid that opens (parts named LID_PREFIX), its
-- lock and lid gem glowing in `accent` (the cache's rarity colour). 13 parts.
function PropModels.Chest(accent: { number })
	local lit = shade(accent, 1.15)
	local parts = {
		part("Block", { 3.8, 1.7, 2.8 }, { 0, -0.65, 0 }, WOOD, "WoodPlanks", nil, { name = "Body" }),
		part("Block", { 4, 0.3, 3 }, { 0, -1.35, 0 }, WOOD_DARK, "Wood", nil, { name = "Base" }),
		part("Block", { 3.8, 0.9, 2.8 }, { 0, 0.65, 0 }, WOOD_LIGHT, "WoodPlanks", nil, { name = "Lid" }),
		part("Block", { 0.6, 0.7, 0.25 }, { 0, 0.25, -1.45 }, lit, "Neon", nil, { name = "Glow" }),
		part("Ball", { 0.7, 0.7, 0.7 }, { 0, 1.2, 0 }, lit, "Neon", nil, { name = "LidGem" }),
	}
	for _, x in { -1.2, 1.2 } do
		add(
			parts,
			part("Block", { 0.4, 1.8, 3 }, { x, -0.6, 0 }, METAL, "Metal", nil, { name = "Band" }),
			part("Block", { 0.4, 1, 3 }, { x, 0.65, 0 }, METAL, "Metal", nil, { name = "LidBand" })
		)
	end
	for _, x in { -1.85, 1.85 } do
		for _, z in { -1.3, 1.3 } do
			add(parts, part("Block", { 0.45, 0.45, 0.45 }, { x, -1.2, z }, METAL_DARK, "Metal", nil, { name = "Stud" }))
		end
	end
	return { parts = parts }
end

-- Meteor ------------------------------------------------------------------------

-- A glowing crack on the rock (a ball of radius `radius` centred at `centre`)
-- along a meridian in the XY plane (side +1/-1) or the YZ plane (axis "z"), `polar`
-- degrees from straight up.
local function crack(centre, radius: number, polar: number, side: number, alongZ: boolean)
	local sin, cos = math.sin(math.rad(polar)), math.cos(math.rad(polar))
	local tilt = (90 - polar) * side
	local pos, rot
	if alongZ then
		pos = { centre[1], centre[2] + radius * cos, centre[3] + radius * sin * side }
		rot = { -tilt, 0, 0 }
	else
		pos = { centre[1] + radius * sin * side, centre[2] + radius * cos, centre[3] }
		rot = { 0, 0, tilt }
	end
	return part("Block", { 0.5, 3.4, 0.5 }, pos, EMBER, "Neon", rot, { name = "Glow" })
end

-- Dark scorched rock with glowing cracks, a scorched floor and a ring of rubble for
-- the crater rim: 19 parts. The chunks (gameplay) ring it at 9 studs; the rim sits
-- outside them.
local function meteor()
	local parts = {
		part("Cylinder", { 0.2, 27, 27 }, { 0, 0.1, 0 }, CHAR, "Slate", { 0, 0, 90 }, { name = "Scorch" }),
		part("Ball", { 12, 10, 12 }, { 0, 3.5, 0 }, SCORCH, "Basalt", nil, { name = "Rock" }),
		part("Ball", { 7, 6, 7 }, { 3.5, 1.5, -2.5 }, shade(SCORCH, 1.2), "Basalt", nil, { name = "Rock" }),
		part("Ball", { 6, 5, 6 }, { -3.5, 1.2, 3 }, shade(SCORCH, 0.9), "Basalt", nil, { name = "Rock" }),
	}
	local centre = { 0, 3.5, 0 }
	add(
		parts,
		part("Block", { 3.5, 0.4, 0.5 }, { 0, 9.5, 0 }, EMBER, "Neon", { 0, 25, 0 }, { name = "Glow" }),
		crack(centre, 5.95, 40, 1, false),
		crack(centre, 5.95, 55, -1, false),
		crack(centre, 5.95, 70, 1, true),
		crack(centre, 5.95, 35, -1, true)
	)
	local rim = 13.5
	for index = 1, 10 do
		local angle = (index / 10) * math.pi * 2
		local w = 2.6 + (index % 3) * 0.7
		add(
			parts,
			part(
				"Block",
				{ w, 1.2 + (index % 2) * 0.5, 2.2 },
				{ math.cos(angle) * rim, 0.5, math.sin(angle) * rim },
				if index % 2 == 0 then SCORCH else shade(SCORCH, 1.35),
				"Basalt",
				{ 0, -math.deg(angle), 0 },
				{ name = "Rim" }
			)
		)
	end
	return parts
end

PropModels.Meteor = { parts = meteor() }

-- Rare event nodes -------------------------------------------------------------

-- A cluster of rock with Neon crystals in `accent` (the event's rarity colour),
-- on the 6 x 5 x 6 hitbox: 12 parts.
function PropModels.OreNode(accent: { number })
	local rock = mix({ 104, 100, 98 }, accent, 0.25)
	local crystal = shade(accent, 1.1)
	local parts = {
		part("Block", { 5.6, 2.6, 5.4 }, { 0, 1.3, 0 }, rock, "Slate", { 0, 12, 0 }, { name = "Boulder" }),
		part("Block", { 3.8, 2.4, 3.6 }, { -0.7, 3, 0.3 }, shade(rock, 1.15), "Slate", { 0, -18, 0 }, { name = "Boulder" }),
		part("Block", { 2.6, 1.8, 2.8 }, { 1.9, 1, -1.5 }, shade(rock, 0.9), "Slate", { 0, 25, 0 }, { name = "Boulder" }),
		part("Block", { 1, 0.7, 1 }, { 3.2, 0.35, 1.8 }, rock, "Slate", { 0, 40, 0 }, { name = "Rubble" }),
		part("Block", { 1, 0.7, 1 }, { -3, 0.3, -2 }, shade(rock, 0.85), "Slate", { 0, -25, 0 }, { name = "Rubble" }),
		part("Block", { 1.2, 0.6, 1 }, { 2.5, 0.3, -3 }, rock, "Slate", { 0, 15, 0 }, { name = "Rubble" }),
	}
	for _, spec in {
		{ { 0.9, 3.2, 0.9 }, { 0.2, 5, 0.2 }, { 0, 0, 6 } },
		{ { 0.8, 2.4, 0.8 }, { -1.5, 4.5, 0.8 }, { 0, 0, 24 } },
		{ { 0.7, 2, 0.7 }, { 1.4, 4.1, 0.9 }, { -20, 0, 0 } },
		{ { 0.8, 2.2, 0.8 }, { 1, 3.4, -1.3 }, { 22, 0, 0 } },
		{ { 0.6, 1.6, 0.6 }, { -2.4, 2.6, -0.6 }, { 0, 0, 50 } },
		{ { 0.6, 1.4, 0.6 }, { -0.4, 2.3, -2.4 }, { -35, 0, 0 } },
	} do
		add(parts, part("Block", spec[1], spec[2], crystal, "Neon", spec[3], { name = "Crystal" }))
	end
	return { parts = lifted(parts, -2.5) }
end

-- The plant variant an event node uses (a Patch unless PLANT_VARIANTS says so).
function PropModels.PlantVariant(eventId: string): string
	return PropModels.PLANT_VARIANTS[eventId] or "Patch"
end

local function patch(accent)
	local parts = {
		part("Cylinder", { 0.4, 4.6, 4.6 }, { 0, 0.2, 0 }, DIRT, "Ground", { 0, 0, 90 }, { name = "Soil" }),
	}
	for index, leaf in
		{
			{ { 2, 1.1, 1.8 }, { 0, 0.9, 0 } },
			{ { 1.8, 0.9, 1.6 }, { -1.3, 0.7, 0.6 } },
			{ { 1.7, 0.9, 1.5 }, { 1.2, 0.6, 0.8 } },
			{ { 1.6, 0.9, 1.6 }, { 0.4, 0.7, -1.3 } },
			{ { 1.6, 0.8, 1.4 }, { -0.8, 0.6, -1.1 } },
		}
	do
		add(parts, part("Ball", leaf[1], leaf[2], if index % 2 == 0 then LEAF_DARK else LEAF, "Grass", nil, { name = "Leaves" }))
	end
	for index, bloom in { { -0.9, 0.4 }, { 0.8, 0.3 }, { 0, -0.9 }, { -0.3, 1 }, { 1.3, -0.4 } } do
		local length = 1.2 + (index % 3) * 0.3
		add(
			parts,
			post(length, 0.15, { bloom[1], 1 + length / 2, bloom[2] }, LEAF_DARK, "Grass", "Stem"),
			part("Ball", { 0.55, 0.55, 0.55 }, { bloom[1], 1 + length + 0.1, bloom[2] }, accent, "Neon", nil, {
				name = "Glow",
			})
		)
	end
	return parts
end

local function bloom(accent)
	local parts = {
		part("Cylinder", { 0.4, 4.6, 4.6 }, { 0, 0.2, 0 }, DIRT, "Ground", { 0, 0, 90 }, { name = "Soil" }),
		post(2.8, 0.35, { 0, 1.8, 0 }, LEAF_DARK, "Grass", "Stalk"),
		part("Ball", { 0.9, 0.9, 0.9 }, { 0, 3.35, 0 }, shade(accent, 1.4), "Neon", nil, { name = "Glow" }),
	}
	for index, yaw in { 0, 90, 45, -45 } do
		add(
			parts,
			part("Ball", { 2.4, 0.4, 1 }, { 0, 0.7 + index * 0.05, 0 }, if index % 2 == 0 then LEAF else LEAF_DARK, "Grass", {
				0,
				yaw,
				0,
			}, { name = "Leaf" })
		)
	end
	for index = 1, 6 do
		local angle = (index / 6) * math.pi * 2
		add(
			parts,
			part(
				"Ball",
				{ 1.5, 0.3, 0.8 },
				{ math.cos(angle) * 0.95, 3.25, math.sin(angle) * 0.95 },
				accent,
				nil,
				{ 0, -math.deg(angle), 0 },
				{ name = "Petal" }
			)
		)
	end
	for _, bud in { { 1.5, 0.8 }, { -1.4, -0.9 }, { 0.4, 1.7 } } do
		add(parts, part("Ball", { 0.5, 0.5, 0.5 }, { bud[1], 1, bud[2] }, accent, "Neon", nil, { name = "Glow" }))
	end
	return parts
end

local function sapling(accent)
	local parts = {
		part("Cylinder", { 0.4, 4.4, 4.4 }, { 0, 0.2, 0 }, DIRT, "Ground", { 0, 0, 90 }, { name = "Soil" }),
		post(4.6, 0.9, { 0, 2.5, 0 }, BARK, "Wood", "Trunk"),
		part("Block", { 0.35, 2, 0.35 }, { 0.9, 3.9, 0 }, BARK, "Wood", { 0, 0, 50 }, { name = "Branch" }),
		part("Ball", { 3.6, 2.8, 3.6 }, { 0, 6, 0 }, LEAF, "Grass", nil, { name = "Canopy" }),
		part("Ball", { 2.6, 2.2, 2.6 }, { -1.6, 5, 0.6 }, LEAF_DARK, "Grass", nil, { name = "Canopy" }),
		part("Ball", { 2.4, 2, 2.4 }, { 1.5, 5.2, -0.8 }, LEAF, "Grass", nil, { name = "Canopy" }),
	}
	for _, at in { { 1.7, 6.2, 0.6 }, { -1, 7, -0.9 }, { 0.4, 5.2, 1.8 }, { -2.2, 5.1, -0.7 }, { 1.9, 4.9, -1.5 } } do
		add(parts, part("Ball", { 0.5, 0.5, 0.5 }, at, accent, "Neon", nil, { name = "Glow" }))
	end
	return parts
end

local PLANTS = { Patch = patch, Bloom = bloom, Sapling = sapling }

-- A glowing plant node for the 4-stud hitbox: a herb/berry Patch (16 parts), a
-- Bloom, one big flower with petals (16), or a Sapling tree (11), their blooms,
-- petals or fruit lit in `accent`.
function PropModels.PlantNode(variant: string, accent: { number })
	local build = PLANTS[variant] or patch
	return { parts = lifted(build(shade(accent, 1.1)), -2) }
end

-- A heap of broken stone, a smashed crate and a hide scrap: the search spot in a
-- ruin, on the 4 x 3 x 4 hitbox. 7 parts.
PropModels.LootPile = {
	parts = lifted({
		part("Block", { 3.4, 1.4, 3.2 }, { 0, 0.7, 0 }, STONE, "Cobblestone", { 0, 15, 0 }, { name = "Heap" }),
		part("Block", { 2.2, 1.2, 2 }, { -0.4, 1.9, 0.3 }, STONE_LIGHT, "Cobblestone", { 0, -25, 0 }, { name = "Heap" }),
		part("Block", { 1.6, 1, 1.4 }, { 1.2, 0.5, -1.6 }, STONE_DARK, "Cobblestone", { 0, 30, 0 }, { name = "Heap" }),
		part("Block", { 1.6, 1.1, 1.3 }, { -1.5, 0.6, 1.5 }, WOOD, "WoodPlanks", { 0, 35, 0 }, { name = "Crate" }),
		part("Block", { 1.8, 0.15, 0.4 }, { -1.2, 1.3, 1.3 }, WOOD_LIGHT, "Wood", { 0, 0, 15 }, { name = "Plank" }),
		part("Block", { 1.4, 0.1, 1 }, { 1.4, 1.2, 0.9 }, HIDE, "Fabric", { 0, 20, 0 }, { name = "Hide" }),
		part("Block", { 1, 0.6, 1 }, { 2, 0.3, 1.4 }, STONE, "Cobblestone", { 0, 50, 0 }, { name = "Rubble" }),
	}, -1.5),
}

-- Ritual altar -------------------------------------------------------------------

-- A raised plinth with four standing stones capped by runes, a bowl and a flame,
-- on the 6 x 3 x 6 altar slab. The Glow parts are lit in the ritual's colours. 15 parts.
local function altar()
	local parts = {
		part("Block", { 4.6, 0.5, 4.6 }, { 0, 1.75, 0 }, STONE_DARK, "Slate", nil, { name = "Plinth" }),
		part("Cylinder", { 0.4, 2.4, 2.4 }, { 0, 2.2, 0 }, METAL_DARK, "Metal", { 0, 0, 90 }, { name = "Bowl" }),
		part("Ball", { 1.1, 1.5, 1.1 }, { 0, 3.1, 0 }, EMBER, "Neon", nil, { name = "Glow" }),
	}
	local stones = {
		{ { -2.5, 3.6, -2.5 }, 4, 4.2 },
		{ { 2.5, 3.9, -2.5 }, -3, 4.8 },
		{ { 2.5, 3.3, 2.5 }, -6, 3.6 },
		{ { -2.5, 3.6, 2.5 }, 3, 4.2 },
	}
	for _, stone in stones do
		local pos = stone[1]
		add(
			parts,
			part("Block", { 0.9, stone[3], 0.9 }, { pos[1], 1.5 + stone[3] / 2, pos[3] }, STONE, "Slate", { 0, 0, stone[2] }, {
				name = "Standing",
			}),
			part("Block", { 0.7, 0.35, 0.7 }, { pos[1], 1.5 + stone[3] + 0.2, pos[3] }, EMBER, "Neon", nil, {
				name = "Glow",
			})
		)
	end
	for index, rune in { { 0, 1.9 }, { 0, -1.9 }, { 1.9, 0 }, { -1.9, 0 } } do
		add(
			parts,
			part("Block", { 1.4, 0.08, 0.35 }, { rune[1], 2.04, rune[2] }, EMBER, "Neon", { 0, if index > 2 then 90 else 0, 0 }, {
				name = "Glow",
			})
		)
	end
	return parts
end

PropModels.Altar = { parts = altar() }

-- Extraction portal ------------------------------------------------------------

-- A ring of low stones around the portal's glowing disc, four totem posts capped
-- in `accent`, and crossed rune bars on the disc: 18 parts. Its ground is 0.3 below
-- the disc's centre; the radius stays inside the smallest zone (8 studs).
function PropModels.Portal(accent: { number })
	local parts = {}
	local floor = -0.3
	for index = 1, 8 do
		local angle = (index / 8) * math.pi * 2
		add(
			parts,
			part(
				"Block",
				{ 1.6, 0.9, 1 },
				{ math.cos(angle) * 4.6, floor + 0.45, math.sin(angle) * 4.6 },
				if index % 2 == 0 then STONE else STONE_DARK,
				"Cobblestone",
				{ 0, -(math.deg(angle) + 90), 0 },
				{ name = "RingStone" }
			)
		)
	end
	for index = 1, 4 do
		local angle = (index / 4) * math.pi * 2 + math.pi / 4
		local x, z = math.cos(angle) * 5.4, math.sin(angle) * 5.4
		add(
			parts,
			part("Block", { 0.9, 4.2, 0.9 }, { x, floor + 2.1, z }, STONE_DARK, "Slate", nil, { name = "Totem" }),
			part("Block", { 0.7, 0.5, 0.7 }, { x, floor + 4.45, z }, accent, "Neon", nil, { name = "Glow" })
		)
	end
	for _, yaw in { 45, -45 } do
		add(parts, part("Block", { 4.4, 0.1, 0.5 }, { 0, 0.35, 0 }, METAL_DARK, "Slate", { 0, yaw, 0 }, { name = "Rune" }))
	end
	return { parts = parts }
end

-- Every recipe this module makes, for specs: {name, recipe}. `accents` are the
-- colours to build the tinted ones with (default: one sample).
function PropModels.All(accents: { { number } }?): { { name: string, recipe: any } }
	local list = {}
	local function include(name: string, recipe)
		table.insert(list, { name = name, recipe = recipe })
	end
	for _, style in PropModels.STYLES do
		include("Structure." .. style, PropModels.Structure[style])
		include("Gate." .. style, PropModels.Gate[style])
		for _, height in { PropModels.RUIN_HEIGHT[1], 5, PropModels.RUIN_HEIGHT[2], PropModels.RING.height } do
			include(("Wall.%s.%d"):format(style, height), PropModels.Wall(style, height))
		end
	end
	include("Meteor", PropModels.Meteor)
	include("LootPile", PropModels.LootPile)
	include("Altar", PropModels.Altar)
	for index, accent in accents or { { 120, 180, 255 } } do
		include("Chest." .. index, PropModels.Chest(accent))
		include("OreNode." .. index, PropModels.OreNode(accent))
		include("Portal." .. index, PropModels.Portal(accent))
		for variant in PLANTS do
			include(("PlantNode.%s.%d"):format(variant, index), PropModels.PlantNode(variant, accent))
		end
	end
	return list
end

return PropModels
