-- Placeholder 3D bodies for every creature, boss and Guardian pillar (GDD §7.3, §8,
-- §54). Pure data in the shared recipe format (Recipe): each creature is a short
-- list of primitive parts that NpcService and BossService weld onto the invisible
-- hitbox (ModelBuilder.Decorate), so the hitbox keeps deciding hits and the
-- model is only what players see.
--
-- Recipes are `normalized`: sizes and offsets are fractions of the hitbox, the
-- origin is its centre and the creature faces -Z (the way NpcService turns it
-- while it walks). An elite (x1.4) or any new hitbox size therefore rescales the
-- model with no further work. Every model stands on the hitbox floor
-- (y = -0.5) and stays roughly inside it; tests/luau/creature_models.spec.luau
-- checks both. Colours come from the catalog colour with shading so the roster
-- keeps its look. Limits: at most 12 parts per creature, 20 per boss.
--
-- Body plans: quadruped (most animals), hopper (rabbit), bird (dodo), biped
-- skeleton, wisp, and hand-built large beasts and bosses. A creature without its
-- own plan falls back to its theme's plan, so a new catalog entry always has a
-- model. Real models replace a recipe later without touching gameplay code.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local EnemyCatalog = require(ReplicatedStorage.Shared.Enemies.EnemyCatalog)
local BossCatalog = require(ReplicatedStorage.Shared.Bosses.BossCatalog)
local Recipe = require(script.Parent.Recipe)

local CreatureModels = {}

CreatureModels.MAX_CREATURE_PARTS = 12
CreatureModels.MAX_BOSS_PARTS = 20

-- Shared tints.
local IVORY = { 232, 226, 204 }
local HOOF = { 42, 36, 32 }
local EYE = { 24, 18, 16 }
local STEEL = { 128, 130, 140 }
local DARK_STEEL = { 66, 68, 76 }
local RUNE = { 120, 200, 255 }
local EMBER = { 255, 150, 50 }

local shade = Recipe.Shade

local function part(name: string, shape: string, size, pos, color, material: string?, rot, transparency: number?)
	return Recipe.Part(shape, size, pos, color, material, rot, { name = name, transparency = transparency })
end

local function block(name: string, size, pos, color, material: string?, rot)
	return part(name, "Block", size, pos, color, material, rot)
end

local function ball(name: string, size, pos, color, material: string?, transparency: number?)
	return part(name, "Ball", size, pos, color, material, nil, transparency)
end

local function append(list, more)
	for _, spec in more do
		table.insert(list, spec)
	end
end

-- A four-legged body: body, head, snout, four legs, then optional ears, tail and
-- whatever `p.extra(c)` adds (horns, tusks, humps; `c` carries the computed
-- body and head positions). Fractions of the hitbox; defaults suit a medium
-- animal. leg = leg height; bw/bh/bl/bz = body width, height, length, centre z.
local function quadruped(base, p)
	local dark = shade(base, 0.7)
	local leg, legW, legD = p.leg or 0.38, p.legW or 0.2, p.legD or 0.13
	local bw, bh, bl, bz = p.bw or 0.8, p.bh or 0.36, p.bl or 0.72, p.bz or 0.06
	local hw, hh, hl = p.hw or 0.5, p.hh or 0.3, p.hl or 0.26
	local snout = p.snout
	local bodyBottom = -0.5 + leg - 0.04
	local bodyTop = bodyBottom + bh
	local headFront = -0.5 + (if snout then snout.l - 0.03 else 0)
	local headZ = headFront + hl / 2
	local headY = p.headY or (bodyTop - hh / 2 + (p.headRise or 0.08))
	local c = {
		bodyTop = bodyTop,
		headY = headY,
		headFront = headFront,
		headZ = headZ,
		hw = hw,
		hh = hh,
		hl = hl,
		snoutY = headY - hh * 0.15,
	}
	local legColor = p.legColor or dark
	local parts = {
		block("Body", { bw, bh, bl }, { 0, bodyBottom + bh / 2, bz }, p.bodyColor or base),
		block("Head", { hw, hh, hl }, { 0, headY, headZ }, p.headColor or base),
	}
	if snout then
		table.insert(
			parts,
			block(
				"Snout",
				{ snout.w, snout.h, snout.l },
				{ 0, c.snoutY, headFront - snout.l / 2 + 0.03 },
				p.snoutColor or shade(base, 1.2)
			)
		)
	end
	local legX = bw / 2 - legW / 2 - 0.02
	local frontZ = bz - bl / 2 + legD / 2 + 0.03
	local rearZ = bz + bl / 2 - legD / 2 - 0.03
	for _, z in { frontZ, rearZ } do
		for _, side in { -1, 1 } do
			table.insert(parts, block("Leg", { legW, leg, legD }, { side * legX, -0.5 + leg / 2, z }, legColor))
		end
	end
	local ears = p.ears
	if ears then
		for _, side in { -1, 1 } do
			table.insert(
				parts,
				block(
					"Ear",
					{ ears.w, ears.h, ears.l },
					{ side * hw * 0.32, headY + hh / 2 + ears.h / 2 - 0.03, headFront + hl * 0.7 },
					p.earColor or dark
				)
			)
		end
	end
	local tail = p.tail
	if tail then
		table.insert(
			parts,
			block(
				"Tail",
				{ tail.w, tail.h, tail.l },
				{ 0, bodyTop - tail.h / 2 - 0.02, bz + bl / 2 + tail.l / 2 - 0.03 },
				p.tailColor or dark
			)
		)
	end
	if p.extra then
		append(parts, p.extra(c))
	end
	return parts
end

-- A thin skeleton warrior: legs, pelvis, ribcage with a pair of rib bars (or iron
-- shoulder plates when armored), arms, skull with eye sockets and a raised sword.
local function skeleton(base, armored: boolean)
	local bone = base
	local dark = shade(base, 0.5)
	local parts = {}
	for _, side in { -1, 1 } do
		table.insert(parts, block("Leg", { 0.16, 0.46, 0.22 }, { side * 0.18, -0.27, 0 }, bone))
		table.insert(parts, block("Arm", { 0.12, 0.46, 0.2 }, { side * 0.38, 0.1, 0 }, bone))
	end
	table.insert(parts, block("Pelvis", { 0.5, 0.1, 0.5 }, { 0, -0.02, 0 }, bone))
	table.insert(parts, block("Ribcage", { 0.52, 0.28, 0.6 }, { 0, 0.17, 0 }, shade(base, 0.9)))
	if armored then
		for _, side in { -1, 1 } do
			table.insert(parts, block("Pauldron", { 0.2, 0.1, 0.26 }, { side * 0.4, 0.3, 0 }, DARK_STEEL, "Metal"))
		end
	else
		table.insert(parts, block("Ribs", { 0.54, 0.035, 0.05 }, { 0, 0.12, -0.3 }, dark))
		table.insert(parts, block("Ribs", { 0.54, 0.035, 0.05 }, { 0, 0.22, -0.3 }, dark))
	end
	table.insert(parts, block("Skull", { 0.4, 0.19, 0.5 }, { 0, 0.41, -0.02 }, bone))
	for _, side in { -1, 1 } do
		table.insert(parts, block("Eye", { 0.09, 0.05, 0.04 }, { side * 0.09, 0.44, -0.33 }, EYE))
	end
	table.insert(parts, block("Sword", { 0.05, 0.7, 0.06 }, { 0.58, 0, 0 }, STEEL, "Metal"))
	return parts
end

-- An ember wisp: a bright core in a translucent shell, flame tongues, two
-- drifting embers and a dark pair of eyes.
local function wisp(base)
	local glow = shade(base, 1.5)
	local parts = {
		ball("Shell", { 0.92, 0.92, 0.92 }, { 0, -0.04, 0 }, base, "Neon", 0.55),
		ball("Core", { 0.5, 0.5, 0.5 }, { 0, -0.04, 0 }, glow, "Neon"),
		part("Flame", "Block", { 0.2, 0.34, 0.2 }, { 0, 0.32, 0 }, EMBER, "Neon", nil, 0.2),
		part("Flame", "Block", { 0.14, 0.24, 0.14 }, { -0.2, 0.26, 0.04 }, base, "Neon", { 0, 0, 20 }, 0.3),
		part("Flame", "Block", { 0.14, 0.24, 0.14 }, { 0.2, 0.26, 0.04 }, base, "Neon", { 0, 0, -20 }, 0.3),
		ball("Ember", { 0.12, 0.12, 0.12 }, { -0.38, 0.1, 0.2 }, EMBER, "Neon"),
		ball("Ember", { 0.1, 0.1, 0.1 }, { 0.36, -0.12, 0.24 }, EMBER, "Neon"),
	}
	for _, side in { -1, 1 } do
		table.insert(parts, block("Eye", { 0.1, 0.1, 0.04 }, { side * 0.14, 0.02, -0.44 }, { 40, 10, 5 }))
	end
	return parts
end

-- A hopping rabbit: haunch and body, head with tall ears, four feet and a tail.
local function rabbit(base)
	local dark = shade(base, 0.75)
	local parts = {
		block("Haunch", { 0.7, 0.5, 0.3 }, { 0, -0.2, 0.22 }, base),
		block("Body", { 0.6, 0.42, 0.38 }, { 0, -0.18, -0.08 }, base),
		block("Head", { 0.5, 0.4, 0.22 }, { 0, 0.05, -0.32 }, shade(base, 1.1)),
		ball("Tail", { 0.16, 0.16, 0.14 }, { 0, -0.12, 0.4 }, shade(base, 1.6)),
	}
	for _, side in { -1, 1 } do
		table.insert(parts, block("Ear", { 0.1, 0.3, 0.05 }, { side * 0.12, 0.37, -0.28 }, dark))
		table.insert(parts, block("Hind foot", { 0.2, 0.12, 0.22 }, { side * 0.2, -0.44, 0.25 }, dark))
		table.insert(parts, block("Paw", { 0.14, 0.12, 0.12 }, { side * 0.18, -0.44, -0.2 }, dark))
	end
	return parts
end

-- A dodo: round body, neck and head, a big hooked beak, two legs, wings, tail.
local function dodo(base)
	local dark = shade(base, 0.75)
	local beak, leg = { 205, 170, 70 }, { 196, 160, 90 }
	local parts = {
		ball("Body", { 0.85, 0.5, 0.7 }, { 0, -0.12, 0.08 }, base),
		block("Neck", { 0.2, 0.3, 0.2 }, { 0, 0.15, -0.2 }, shade(base, 1.1)),
		ball("Head", { 0.34, 0.26, 0.3 }, { 0, 0.35, -0.28 }, shade(base, 1.1)),
		block("Beak", { 0.14, 0.12, 0.22 }, { 0, 0.32, -0.43 }, beak),
		block("Tail", { 0.3, 0.2, 0.1 }, { 0, -0.02, 0.42 }, shade(base, 1.35)),
	}
	for _, side in { -1, 1 } do
		table.insert(parts, block("Leg", { 0.09, 0.26, 0.09 }, { side * 0.16, -0.37, 0.05 }, leg))
		table.insert(parts, block("Wing", { 0.08, 0.25, 0.35 }, { side * 0.43, -0.1, 0.08 }, dark))
		table.insert(parts, block("Eye", { 0.05, 0.05, 0.04 }, { side * 0.1, 0.38, -0.42 }, EYE))
	end
	return parts
end

-- A giant ground sloth: heavy shaggy body, long arms ending in claws, small head.
local function sloth(base)
	local fur, dark = shade(base, 1.05), shade(base, 0.7)
	local parts = {
		block("Body", { 0.8, 0.5, 0.55 }, { 0, -0.05, 0.12 }, fur),
		block("Shag", { 0.7, 0.2, 0.4 }, { 0, 0.22, 0.14 }, dark),
		block("Head", { 0.34, 0.22, 0.28 }, { 0, 0.3, -0.3 }, fur),
		block("Snout", { 0.2, 0.12, 0.1 }, { 0, 0.26, -0.45 }, shade(base, 1.4)),
	}
	for _, side in { -1, 1 } do
		table.insert(parts, block("Leg", { 0.28, 0.3, 0.22 }, { side * 0.24, -0.35, 0.18 }, dark))
		table.insert(parts, block("Arm", { 0.16, 0.55, 0.16 }, { side * 0.46, -0.1, -0.2 }, fur))
		table.insert(parts, block("Claws", { 0.14, 0.1, 0.1 }, { side * 0.46, -0.43, -0.2 }, IVORY))
	end
	return parts
end

-- An ancient tortoise: a domed shell with plates, four stubby legs, head and tail.
local function tortoise(base)
	local shell, rim = shade(base, 0.8), shade(base, 0.6)
	local parts = {
		ball("Shell", { 0.9, 0.7, 0.8 }, { 0, 0.02, 0.04 }, shell),
		block("Rim", { 0.95, 0.12, 0.85 }, { 0, -0.2, 0.04 }, rim),
		block("Plate", { 0.34, 0.08, 0.3 }, { 0, 0.36, 0.04 }, shade(base, 0.55)),
		block("Plate", { 0.26, 0.1, 0.24 }, { -0.2, 0.28, 0.18 }, shade(base, 0.55)),
		block("Neck", { 0.2, 0.18, 0.22 }, { 0, -0.12, -0.42 }, base),
		block("Head", { 0.24, 0.2, 0.2 }, { 0, -0.08, -0.54 }, shade(base, 1.15)),
		block("Tail", { 0.08, 0.08, 0.14 }, { 0, -0.3, 0.5 }, base),
	}
	for _, z in { -0.26, 0.34 } do
		for _, side in { -1, 1 } do
			table.insert(parts, block("Leg", { 0.2, 0.22, 0.2 }, { side * 0.36, -0.39, z }, base))
		end
	end
	return parts
end

-- Per-creature plans (catalog colour in, parts out).
local ENEMY_PLANS = {}

function ENEMY_PLANS.WildBoar(base)
	return quadruped(base, {
		leg = 0.3,
		legW = 0.17,
		legD = 0.1,
		bw = 0.86,
		bh = 0.5,
		bl = 0.66,
		bz = 0.1,
		hw = 0.5,
		hh = 0.42,
		hl = 0.24,
		headRise = -0.02,
		snout = { w = 0.3, h = 0.22, l = 0.14 },
		snoutColor = shade(base, 0.75),
		ears = { w = 0.1, h = 0.1, l = 0.06 },
		tail = { w = 0.05, h = 0.05, l = 0.1 },
		extra = function(c)
			local parts = {}
			for _, side in { -1, 1 } do
				table.insert(parts, block("Tusk", { 0.05, 0.05, 0.12 }, { side * 0.14, c.headY - 0.12, -0.46 }, IVORY))
			end
			return parts
		end,
	})
end

function ENEMY_PLANS.ForestStag(base)
	return quadruped(base, {
		leg = 0.5,
		legW = 0.1,
		legD = 0.08,
		bw = 0.66,
		bh = 0.28,
		bl = 0.5,
		bz = 0.14,
		hw = 0.36,
		hh = 0.15,
		hl = 0.14,
		headY = 0.4,
		snout = { w = 0.2, h = 0.11, l = 0.1 },
		tail = { w = 0.08, h = 0.1, l = 0.07 },
		extra = function(c)
			local parts = { block("Neck", { 0.16, 0.26, 0.22 }, { 0, 0.32, -0.22 }, base) }
			for _, side in { -1, 1 } do
				table.insert(
					parts,
					block("Antler", { 0.05, 0.16, 0.05 }, { side * 0.1, c.headY + c.hh / 2 + 0.06, c.headZ }, IVORY)
				)
			end
			return parts
		end,
	})
end

function ENEMY_PLANS.GreyWolf(base)
	return quadruped(base, {
		leg = 0.36,
		legW = 0.13,
		legD = 0.09,
		bw = 0.62,
		bh = 0.3,
		bl = 0.6,
		bz = 0,
		hw = 0.4,
		hh = 0.28,
		hl = 0.18,
		snout = { w = 0.2, h = 0.14, l = 0.18 },
		ears = { w = 0.08, h = 0.12, l = 0.05 },
		tail = { w = 0.14, h = 0.14, l = 0.23 },
		extra = function(c)
			return { block("Saddle", { 0.5, 0.05, 0.4 }, { 0, c.bodyTop - 0.005, 0 }, shade(base, 0.6)) }
		end,
	})
end

function ENEMY_PLANS.BrownBear(base)
	return quadruped(base, {
		leg = 0.34,
		legW = 0.24,
		legD = 0.13,
		bw = 0.9,
		bh = 0.5,
		bl = 0.64,
		bz = 0.1,
		hw = 0.52,
		hh = 0.3,
		hl = 0.2,
		headRise = 0,
		snout = { w = 0.28, h = 0.17, l = 0.1 },
		snoutColor = shade(base, 1.35),
		ears = { w = 0.12, h = 0.08, l = 0.05 },
		tail = { w = 0.1, h = 0.1, l = 0.06 },
		extra = function(c)
			return { block("Hump", { 0.6, 0.14, 0.25 }, { 0, c.bodyTop + 0.05, -0.1 }, base) }
		end,
	})
end

function ENEMY_PLANS.RiverCrocodile(base)
	return quadruped(base, {
		leg = 0.3,
		legW = 0.2,
		legD = 0.07,
		bw = 0.84,
		bh = 0.46,
		bl = 0.34,
		bz = -0.03,
		hw = 0.6,
		hh = 0.32,
		hl = 0.16,
		headRise = -0.1,
		snout = { w = 0.4, h = 0.2, l = 0.22 },
		extra = function(c)
			local parts = {
				block("Tail", { 0.5, 0.3, 0.2 }, { 0, -0.08, 0.24 }, base),
				block("Tail", { 0.26, 0.18, 0.18 }, { 0, -0.12, 0.41 }, shade(base, 0.85)),
				block("Ridge", { 0.4, 0.06, 0.5 }, { 0, c.bodyTop + 0.02, 0.04 }, shade(base, 0.6)),
			}
			for _, side in { -1, 1 } do
				table.insert(
					parts,
					block(
						"Eye",
						{ 0.1, 0.08, 0.05 },
						{ side * 0.22, c.headY + c.hh / 2 + 0.02, c.headFront + 0.04 },
						EYE
					)
				)
			end
			return parts
		end,
	})
end

function ENEMY_PLANS.PlainsBison(base)
	return quadruped(base, {
		leg = 0.34,
		legW = 0.2,
		legD = 0.12,
		bw = 0.84,
		bh = 0.44,
		bl = 0.7,
		bz = 0.1,
		hw = 0.46,
		hh = 0.34,
		hl = 0.2,
		headRise = -0.14,
		snout = { w = 0.36, h = 0.22, l = 0.08 },
		tail = { w = 0.05, h = 0.05, l = 0.1 },
		extra = function(c)
			local parts = {
				block("Hump", { 0.7, 0.3, 0.34 }, { 0, c.bodyTop + 0.08, -0.08 }, shade(base, 0.9)),
				block("Mane", { 0.62, 0.46, 0.14 }, { 0, c.headY + 0.05, -0.22 }, shade(base, 0.6)),
			}
			for _, side in { -1, 1 } do
				table.insert(
					parts,
					block(
						"Horn",
						{ 0.05, 0.1, 0.05 },
						{ side * 0.2, c.headY + c.hh / 2 + 0.03, c.headFront + 0.06 },
						IVORY
					)
				)
			end
			return parts
		end,
	})
end

ENEMY_PLANS.MeadowRabbit = rabbit
ENEMY_PLANS.IslandDodo = dodo

function ENEMY_PLANS.RiverCapybara(base)
	return quadruped(base, {
		leg = 0.2,
		legW = 0.2,
		legD = 0.14,
		bw = 0.84,
		bh = 0.58,
		bl = 0.7,
		bz = 0.1,
		hw = 0.5,
		hh = 0.36,
		hl = 0.22,
		headRise = -0.05,
		snout = { w = 0.42, h = 0.3, l = 0.06 },
		ears = { w = 0.1, h = 0.08, l = 0.05 },
	})
end

function ENEMY_PLANS.HighlandGoat(base)
	return quadruped(base, {
		leg = 0.44,
		legW = 0.1,
		legD = 0.1,
		bw = 0.6,
		bh = 0.3,
		bl = 0.62,
		bz = 0.08,
		hw = 0.34,
		hh = 0.22,
		hl = 0.14,
		headRise = 0.14,
		snout = { w = 0.18, h = 0.14, l = 0.1 },
		ears = { w = 0.12, h = 0.05, l = 0.07 },
		extra = function(c)
			local parts = { block("Beard", { 0.06, 0.1, 0.06 }, { 0, c.headY - 0.15, c.headFront + 0.04 }, IVORY) }
			for _, side in { -1, 1 } do
				table.insert(
					parts,
					block(
						"Horn",
						{ 0.05, 0.2, 0.05 },
						{ side * 0.09, c.headY + c.hh / 2 + 0.08, c.headFront + 0.12 },
						shade(base, 0.6),
						nil,
						{ 25, 0, 0 }
					)
				)
			end
			return parts
		end,
	})
end

function ENEMY_PLANS.ForestTapir(base)
	return quadruped(base, {
		leg = 0.3,
		legW = 0.18,
		legD = 0.11,
		bw = 0.72,
		bh = 0.5,
		bl = 0.66,
		bz = 0.1,
		hw = 0.44,
		hh = 0.32,
		hl = 0.2,
		headRise = 0,
		snout = { w = 0.26, h = 0.2, l = 0.2 },
		snoutColor = shade(base, 1.1),
		ears = { w = 0.1, h = 0.1, l = 0.05 },
		tail = { w = 0.06, h = 0.06, l = 0.07 },
		extra = function(c)
			return { block("Saddle", { 0.76, 0.3, 0.3 }, { 0, c.bodyTop - 0.12, 0.2 }, { 222, 218, 212 }) }
		end,
	})
end

ENEMY_PLANS.GiantGroundSloth = sloth

function ENEMY_PLANS.SaberToothedTiger(base)
	return quadruped(base, {
		leg = 0.38,
		legW = 0.17,
		legD = 0.1,
		bw = 0.66,
		bh = 0.34,
		bl = 0.66,
		bz = 0.08,
		hw = 0.48,
		hh = 0.32,
		hl = 0.16,
		headRise = 0.06,
		snout = { w = 0.28, h = 0.18, l = 0.1 },
		ears = { w = 0.1, h = 0.1, l = 0.05 },
		tail = { w = 0.07, h = 0.07, l = 0.1 },
		extra = function(c)
			local parts = {}
			for _, side in { -1, 1 } do
				table.insert(parts, block("Fang", { 0.04, 0.18, 0.04 }, { side * 0.1, c.snoutY - 0.14, -0.47 }, IVORY))
			end
			return parts
		end,
	})
end

function ENEMY_PLANS.WoollyMammoth(base)
	return quadruped(base, {
		leg = 0.36,
		legW = 0.22,
		legD = 0.16,
		bw = 0.88,
		bh = 0.5,
		bl = 0.6,
		bz = 0.12,
		hw = 0.5,
		hh = 0.42,
		hl = 0.26,
		headRise = 0.04,
		extra = function(c)
			return {
				block("Dome", { 0.46, 0.2, 0.2 }, { 0, c.headY + c.hh / 2 + 0.04, c.headZ }, shade(base, 0.85)),
				block("Skirt", { 0.96, 0.2, 0.56 }, { 0, -0.2, 0.12 }, shade(base, 0.7)),
				block("Trunk", { 0.14, 0.34, 0.12 }, { 0, -0.07, -0.46 }, shade(base, 0.9)),
				block("Trunk tip", { 0.12, 0.1, 0.12 }, { 0, -0.27, -0.52 }, shade(base, 0.9)),
				block("Tusk", { 0.05, 0.05, 0.22 }, { -0.2, -0.05, -0.47 }, IVORY),
				block("Tusk", { 0.05, 0.05, 0.22 }, { 0.2, -0.05, -0.47 }, IVORY),
			}
		end,
	})
end

function ENEMY_PLANS.IronTuskBoar(base)
	return quadruped(base, {
		leg = 0.3,
		legW = 0.18,
		legD = 0.1,
		bw = 0.88,
		bh = 0.52,
		bl = 0.64,
		bz = 0.12,
		hw = 0.52,
		hh = 0.44,
		hl = 0.24,
		headRise = -0.02,
		snout = { w = 0.32, h = 0.24, l = 0.14 },
		snoutColor = shade(base, 0.8),
		ears = { w = 0.1, h = 0.1, l = 0.06 },
		extra = function(c)
			local parts = { block("Ridge", { 0.14, 0.1, 0.5 }, { 0, c.bodyTop + 0.03, 0.04 }, shade(base, 0.55)) }
			for _, side in { -1, 1 } do
				table.insert(
					parts,
					block("Iron tusk", { 0.06, 0.06, 0.2 }, { side * 0.16, c.headY - 0.14, -0.44 }, STEEL, "Metal")
				)
			end
			return parts
		end,
	})
end

ENEMY_PLANS.AncientTortoise = tortoise

function ENEMY_PLANS.StonehideRhino(base)
	return quadruped(base, {
		leg = 0.32,
		legW = 0.22,
		legD = 0.14,
		bw = 0.86,
		bh = 0.5,
		bl = 0.66,
		bz = 0.1,
		hw = 0.46,
		hh = 0.3,
		hl = 0.2,
		headRise = -0.02,
		snout = { w = 0.3, h = 0.2, l = 0.14 },
		tail = { w = 0.05, h = 0.05, l = 0.1 },
		extra = function(c)
			return {
				block("Horn", { 0.1, 0.2, 0.1 }, { 0, c.snoutY + 0.18, c.headFront - 0.04 }, IVORY),
				block("Horn", { 0.07, 0.12, 0.07 }, { 0, c.headY + c.hh / 2 + 0.04, c.headFront + 0.12 }, IVORY),
				block("Plate", { 0.9, 0.3, 0.15 }, { 0, c.bodyTop - 0.14, -0.1 }, shade(base, 0.75), "Slate"),
				block("Plate", { 0.9, 0.3, 0.15 }, { 0, c.bodyTop - 0.14, 0.25 }, shade(base, 0.75), "Slate"),
			}
		end,
	})
end

ENEMY_PLANS.Skeleton = function(base)
	return skeleton(base, false)
end
ENEMY_PLANS.KeepSkeleton = function(base)
	return skeleton(base, true)
end
ENEMY_PLANS.EmberWisp = wisp

-- A creature with no plan of its own looks like its theme.
local THEME_PLANS = {
	Primitive = function(base)
		return quadruped(base, {
			snout = { w = 0.28, h = 0.18, l = 0.12 },
			ears = { w = 0.1, h = 0.1, l = 0.05 },
			tail = { w = 0.06, h = 0.06, l = 0.1 },
		})
	end,
	Ancient = function(base)
		return quadruped(base, {
			leg = 0.34,
			legW = 0.22,
			legD = 0.15,
			bw = 0.86,
			bh = 0.5,
			snout = { w = 0.3, h = 0.2, l = 0.12 },
			tail = { w = 0.06, h = 0.06, l = 0.1 },
		})
	end,
	Skeletal = function(base)
		return skeleton(base, false)
	end,
	Elemental = wisp,
}

-- Boss plans: bigger, more detailed, up to 20 parts.
local BOSS_PLANS = {}

-- The Guardian: a stone golem with glowing runes.
function BOSS_PLANS.Guardian(base)
	local stone, dark = shade(base, 1.1), shade(base, 0.65)
	local parts = {
		block("Pelvis", { 0.62, 0.12, 0.4 }, { 0, -0.1, 0 }, dark, "Slate"),
		block("Torso", { 0.7, 0.36, 0.5 }, { 0, 0.14, 0 }, stone, "Slate"),
		block("Head", { 0.3, 0.16, 0.3 }, { 0, 0.4, -0.02 }, dark, "Slate"),
		block("Eye slit", { 0.2, 0.03, 0.02 }, { 0, 0.41, -0.17 }, RUNE, "Neon"),
		block("Chest rune", { 0.22, 0.2, 0.02 }, { 0, 0.14, -0.26 }, RUNE, "Neon"),
		block("Crown", { 0.05, 0.1, 0.05 }, { -0.1, 0.53, 0 }, dark, "Slate"),
		block("Crown", { 0.05, 0.1, 0.05 }, { 0.1, 0.53, 0 }, dark, "Slate"),
	}
	for _, side in { -1, 1 } do
		table.insert(parts, block("Leg", { 0.26, 0.34, 0.26 }, { side * 0.2, -0.33, 0 }, stone, "Slate"))
		table.insert(parts, block("Leg rune", { 0.04, 0.2, 0.02 }, { side * 0.2, -0.3, -0.14 }, RUNE, "Neon"))
		table.insert(parts, block("Shoulder", { 0.22, 0.2, 0.34 }, { side * 0.44, 0.25, 0 }, dark, "Slate"))
		table.insert(parts, block("Arm", { 0.16, 0.5, 0.22 }, { side * 0.47, -0.02, 0 }, stone, "Slate"))
		table.insert(parts, block("Fist", { 0.2, 0.2, 0.26 }, { side * 0.47, -0.33, 0 }, dark, "Slate"))
	end
	return parts
end

-- The Ironhide Behemoth: an armoured, horned beast with iron plates and spikes.
function BOSS_PLANS.IronhideBehemoth(base)
	return quadruped(base, {
		leg = 0.34,
		legW = 0.2,
		legD = 0.13,
		bw = 0.86,
		bh = 0.5,
		bl = 0.62,
		bz = 0.1,
		hw = 0.5,
		hh = 0.34,
		hl = 0.2,
		headRise = -0.04,
		snout = { w = 0.3, h = 0.2, l = 0.14 },
		tail = { w = 0.08, h = 0.08, l = 0.1 },
		extra = function(c)
			local parts = {}
			for _, side in { -1, 1 } do
				table.insert(parts, block("Tusk", { 0.05, 0.05, 0.2 }, { side * 0.14, c.snoutY - 0.1, -0.44 }, IVORY))
				table.insert(
					parts,
					block(
						"Horn",
						{ 0.07, 0.2, 0.07 },
						{ side * 0.16, c.headY + c.hh / 2 + 0.08, c.headFront + 0.06 },
						IVORY
					)
				)
			end
			for _, z in { -0.1, 0.12, 0.32 } do
				table.insert(parts, block("Plate", { 0.9, 0.07, 0.16 }, { 0, c.bodyTop + 0.01, z }, STEEL, "Metal"))
				table.insert(
					parts,
					block("Spike", { 0.06, 0.14, 0.06 }, { 0, c.bodyTop + 0.12, z }, DARK_STEEL, "Metal")
				)
			end
			return parts
		end,
	})
end

-- The Bone Colossus: a giant skeleton with a glowing ember in its ribcage.
function BOSS_PLANS.BoneColossus(base)
	local dark = shade(base, 0.6)
	local parts = {
		block("Pelvis", { 0.6, 0.1, 0.4 }, { 0, -0.05, 0 }, base),
		block("Spine", { 0.12, 0.3, 0.14 }, { 0, 0.14, 0.1 }, dark),
		block("Rib", { 0.6, 0.05, 0.5 }, { 0, 0.05, 0 }, base),
		block("Rib", { 0.6, 0.05, 0.5 }, { 0, 0.14, 0 }, base),
		block("Rib", { 0.6, 0.05, 0.5 }, { 0, 0.23, 0 }, base),
		block("Core", { 0.16, 0.14, 0.12 }, { 0, 0.14, -0.08 }, EMBER, "Neon"),
		block("Skull", { 0.34, 0.17, 0.46 }, { 0, 0.4, -0.04 }, base),
		block("Horn", { 0.05, 0.1, 0.05 }, { -0.14, 0.52, 0 }, dark),
		block("Horn", { 0.05, 0.1, 0.05 }, { 0.14, 0.52, 0 }, dark),
	}
	for _, side in { -1, 1 } do
		table.insert(parts, block("Leg", { 0.16, 0.42, 0.22 }, { side * 0.2, -0.29, 0 }, base))
		table.insert(parts, block("Shoulder", { 0.16, 0.12, 0.26 }, { side * 0.4, 0.29, 0 }, dark))
		table.insert(parts, block("Arm", { 0.1, 0.5, 0.14 }, { side * 0.44, 0.02, 0 }, base))
		table.insert(parts, block("Hand", { 0.14, 0.14, 0.24 }, { side * 0.44, -0.3, -0.04 }, dark))
		table.insert(parts, block("Eye", { 0.07, 0.05, 0.04 }, { side * 0.09, 0.42, -0.28 }, EMBER, "Neon"))
	end
	return parts
end

-- The Crater Gorilla: a dark silverback with long fists and ember cracks.
function BOSS_PLANS.CraterGorilla(base)
	local silver, dark = shade(base, 1.5), shade(base, 0.7)
	local parts = {
		block("Torso", { 0.85, 0.5, 0.7 }, { 0, 0, 0.08 }, base),
		block("Saddle", { 0.7, 0.1, 0.5 }, { 0, 0.27, 0.12 }, silver),
		block("Shoulders", { 0.9, 0.22, 0.4 }, { 0, 0.28, 0 }, base),
		block("Head", { 0.34, 0.26, 0.3 }, { 0, 0.36, -0.3 }, dark),
		block("Brow", { 0.34, 0.06, 0.1 }, { 0, 0.46, -0.43 }, shade(base, 0.5)),
		block("Muzzle", { 0.24, 0.12, 0.1 }, { 0, 0.3, -0.44 }, shade(base, 1.9)),
		block("Crack", { 0.04, 0.22, 0.02 }, { -0.1, -0.02, -0.28 }, EMBER, "Neon"),
		block("Crack", { 0.04, 0.22, 0.02 }, { 0.12, 0.02, -0.28 }, EMBER, "Neon"),
	}
	for _, side in { -1, 1 } do
		table.insert(parts, block("Leg", { 0.28, 0.32, 0.24 }, { side * 0.2, -0.34, 0.05 }, dark))
		table.insert(parts, block("Arm", { 0.2, 0.7, 0.22 }, { side * 0.52, -0.03, -0.1 }, base))
		table.insert(parts, block("Fist", { 0.26, 0.14, 0.26 }, { side * 0.52, -0.43, -0.1 }, dark))
	end
	return parts
end

-- The Minotaur: a bull-headed brute with a loincloth, big horns and an axe.
function BOSS_PLANS.Minotaur(base)
	local dark, hide = shade(base, 0.6), shade(base, 1.15)
	local parts = {
		block("Loincloth", { 0.6, 0.14, 0.36 }, { 0, -0.08, 0 }, { 80, 40, 40 }),
		block("Torso", { 0.8, 0.36, 0.5 }, { 0, 0.12, 0 }, hide),
		block("Head", { 0.34, 0.2, 0.36 }, { 0, 0.4, -0.04 }, base),
		block("Snout", { 0.2, 0.12, 0.14 }, { 0, 0.37, -0.26 }, shade(base, 1.4)),
		block("Horns", { 0.28, 0.05, 0.05 }, { -0.26, 0.47, -0.02 }, IVORY),
		block("Horns", { 0.28, 0.05, 0.05 }, { 0.26, 0.47, -0.02 }, IVORY),
		block("Axe haft", { 0.05, 0.7, 0.05 }, { 0.5, -0.1, -0.2 }, { 96, 66, 42 }, "Wood"),
		block("Axe blade", { 0.05, 0.2, 0.22 }, { 0.5, 0.2, -0.2 }, STEEL, "Metal"),
	}
	for _, side in { -1, 1 } do
		table.insert(parts, block("Leg", { 0.26, 0.4, 0.3 }, { side * 0.2, -0.3, 0 }, dark))
		table.insert(parts, block("Shoulder", { 0.22, 0.2, 0.3 }, { side * 0.46, 0.24, 0 }, hide))
		table.insert(parts, block("Arm", { 0.18, 0.5, 0.24 }, { side * 0.47, 0, 0 }, hide))
		table.insert(parts, block("Fist", { 0.22, 0.16, 0.26 }, { side * 0.47, -0.3, 0 }, dark))
	end
	return parts
end

-- The Raider Warlord: an armoured human in a red tabard and cape with a sword.
function BOSS_PLANS.RaiderWarlord(base)
	local leather = { 52, 40, 38 }
	local parts = {
		block("Belt", { 0.6, 0.06, 0.4 }, { 0, -0.05, 0 }, { 170, 130, 50 }),
		block("Torso", { 0.64, 0.32, 0.46 }, { 0, 0.13, 0 }, DARK_STEEL, "Metal"),
		block("Tabard", { 0.3, 0.34, 0.02 }, { 0, 0.1, -0.24 }, base),
		block("Helm", { 0.34, 0.17, 0.4 }, { 0, 0.4, 0 }, DARK_STEEL, "Metal"),
		block("Crest", { 0.06, 0.1, 0.34 }, { 0, 0.53, 0 }, base),
		block("Cape", { 0.6, 0.5, 0.04 }, { 0, 0.1, 0.26 }, shade(base, 0.8), "Fabric"),
		block("Sword", { 0.06, 0.06, 0.5 }, { 0.42, -0.2, -0.4 }, STEEL, "Metal"),
		block("Guard", { 0.2, 0.05, 0.05 }, { 0.42, -0.2, -0.14 }, { 170, 130, 50 }, "Metal"),
	}
	for _, side in { -1, 1 } do
		table.insert(parts, block("Leg", { 0.22, 0.42, 0.3 }, { side * 0.16, -0.29, 0 }, leather))
		table.insert(parts, block("Pauldron", { 0.22, 0.1, 0.34 }, { side * 0.4, 0.27, 0 }, STEEL, "Metal"))
		table.insert(parts, block("Arm", { 0.14, 0.4, 0.2 }, { side * 0.42, 0.06, 0 }, DARK_STEEL, "Metal"))
		table.insert(parts, block("Fist", { 0.18, 0.12, 0.22 }, { side * 0.42, -0.2, -0.02 }, leather))
		table.insert(parts, block("Horn", { 0.05, 0.14, 0.05 }, { side * 0.2, 0.48, 0 }, IVORY))
	end
	return parts
end

local function bossFallback(base)
	local dark = shade(base, 0.7)
	local parts = {
		block("Torso", { 0.8, 0.4, 0.5 }, { 0, 0.1, 0 }, base),
		block("Head", { 0.34, 0.2, 0.34 }, { 0, 0.4, -0.02 }, shade(base, 1.15)),
	}
	for _, side in { -1, 1 } do
		table.insert(parts, block("Leg", { 0.28, 0.4, 0.3 }, { side * 0.2, -0.3, 0 }, dark))
		table.insert(parts, block("Arm", { 0.18, 0.5, 0.24 }, { side * 0.47, 0, 0 }, dark))
	end
	return parts
end

local enemyRecipes = {}
local bossRecipes = {}

-- The normalized recipe of enemy `enemyId` (a theme look for unknown ids).
function CreatureModels.For(enemyId: string)
	local cached = enemyRecipes[enemyId]
	if cached then
		return cached
	end
	local def = EnemyCatalog.Get(enemyId)
	local base = Recipe.Rgb(if def then def.color else Color3.fromRGB(150, 140, 130))
	local plan = ENEMY_PLANS[enemyId] or THEME_PLANS[def and def.theme or "Primitive"] or THEME_PLANS.Primitive
	local recipe = { normalized = true, parts = plan(base) }
	if def then
		enemyRecipes[enemyId] = recipe
	end
	return recipe
end

-- The normalized recipe of boss `bossId`.
function CreatureModels.ForBoss(bossId: string)
	local cached = bossRecipes[bossId]
	if cached then
		return cached
	end
	local def = BossCatalog.Get(bossId)
	local base = Recipe.Rgb(if def then def.color else Color3.fromRGB(120, 110, 100))
	local recipe = { normalized = true, parts = (BOSS_PLANS[bossId] or bossFallback)(base) }
	if def then
		bossRecipes[bossId] = recipe
	end
	return recipe
end

local pillarRecipe = nil

-- A Guardian energy pillar: a stone column on a plinth with glowing runes and a
-- crystal on top.
function CreatureModels.ForPillar()
	if pillarRecipe == nil then
		local stone, dark = { 120, 124, 134 }, { 84, 88, 98 }
		local parts = {
			block("Plinth", { 1.2, 0.08, 1.2 }, { 0, -0.46, 0 }, dark, "Slate"),
			block("Shaft", { 0.85, 0.78, 0.85 }, { 0, -0.02, 0 }, stone, "Slate"),
			block("Capital", { 1.1, 0.07, 1.1 }, { 0, 0.4, 0 }, dark, "Slate"),
			ball("Crystal", { 0.5, 0.125, 0.5 }, { 0, 0.5, 0 }, RUNE, "Neon"),
		}
		for _, side in { -1, 1 } do
			table.insert(parts, block("Rune", { 0.4, 0.45, 0.05 }, { 0, 0.1, side * 0.43 }, RUNE, "Neon"))
			table.insert(parts, block("Rune", { 0.05, 0.45, 0.4 }, { side * 0.43, 0.1, 0 }, RUNE, "Neon"))
		end
		pillarRecipe = { normalized = true, parts = parts }
	end
	return pillarRecipe
end

local shieldRecipe = nil

-- The translucent bubble a shielded boss wears (the Guardian before its pillars
-- fall): a shell a little larger than the hitbox, resting on its floor.
function CreatureModels.Shield()
	if shieldRecipe == nil then
		shieldRecipe = {
			normalized = true,
			parts = { ball("Shield", { 1.3, 1.3, 1.3 }, { 0, 0.15, 0 }, RUNE, "ForceField", 0.6) },
		}
	end
	return shieldRecipe
end

return CreatureModels
