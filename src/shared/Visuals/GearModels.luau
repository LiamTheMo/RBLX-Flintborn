-- Placeholder models for held gear, worn armor and dropped gear (v0.19), as plain
-- Recipe tables (see Recipe for the format; ModelBuilder builds them). The shapes
-- are generated from the same tier ladder as the items (Tiers, GDD §51), so a new
-- tier or weapon family is one entry in TIERS or one builder here. Real models
-- replace these later without touching gameplay code (EquipmentVisualService and
-- DropService only ask for a recipe by catalog id).
--
--   Held(catalogId)  -> recipe?   origin = the grip, +Y up the handle to the business
--                                 end, -Z the side the blade edge or the bow's
--                                 belly faces. Tools, weapons, siege items, arrows,
--                                 plus a flask/pouch/crate for consumables and
--                                 placeables. Materials have none.
--   Armor(catalogId) -> { [bodyPart]: recipe }?   origin = the centre of each R6
--                                 body part it covers ("Head", "Torso", "Right Arm",
--                                 "Left Arm", "Right Leg", "Left Leg").
--   Drop(catalogId)  -> recipe?   a small ground model of a Tool, Weapon, Siege
--                                 item or Armor piece, centred on the drop's 1.4 stud
--                                 hitbox.
--
-- Recipes are cached and shared: callers must not modify them. Rotations here are
-- limited to the X axis (and a Cylinder stood upright, {0, 0, 90}) so Drop can lay
-- a held model flat by composing a single rotation.

local ItemCatalog = require(script.Parent.Parent.Items.ItemCatalog)
local Recipe = require(script.Parent.Recipe)

local GearModels = {}

local Part = Recipe.Part
local Shade = Recipe.Shade

-- Upright Cylinder rotation (a Cylinder's axis is X; this stands it along Y).
local UPRIGHT = { 0, 0, 90 }

-- Per-tier look: `color`/`material` for blades, heads and armor shells; `trim` for
-- the edge or rim. Wood, Stone, Flint, Bone, Obsidian and Jade are the knapped or
-- carved tiers; the metals follow the ladder. Hide is armor only.
local TIERS = {
	Wood = { color = { 150, 108, 64 }, material = "Wood", trim = { 112, 78, 46 } },
	Stone = { color = { 138, 138, 144 }, material = "Slate", trim = { 190, 190, 196 } },
	Hide = { color = { 140, 98, 58 }, material = "Fabric", trim = { 92, 62, 36 } },
	Bone = { color = { 232, 224, 200 }, material = "Limestone", trim = { 190, 180, 152 } },
	Flint = { color = { 72, 74, 84 }, material = "Slate", trim = { 130, 134, 148 } },
	Copper = { color = { 205, 118, 58 }, material = "Metal", trim = { 238, 168, 104 } },
	Iron = { color = { 118, 130, 150 }, material = "Metal", trim = { 190, 200, 216 } },
	Obsidian = { color = { 26, 22, 34 }, material = "Glass", trim = { 90, 80, 120 } },
	Silver = { color = { 214, 220, 230 }, material = "Metal", trim = { 250, 252, 255 } },
	Cobalt = { color = { 40, 92, 192 }, material = "Metal", trim = { 120, 168, 240 } },
	Jade = { color = { 70, 172, 112 }, material = "Marble", trim = { 150, 226, 176 } },
	Mithril = { color = { 150, 230, 236 }, material = "Foil", trim = { 220, 252, 255 } },
	Adamantine = { color = { 128, 30, 70 }, material = "Metal", trim = { 208, 72, 120 } },
}
GearModels.Tiers = TIERS

local FALLBACK_TIER = TIERS.Iron

-- Shared furniture colours.
local HANDLE = { 112, 80, 50 }
local WRAP = { 62, 48, 38 }
local STRING = { 225, 215, 190 }
local IRON_BAND = { 74, 76, 82 }
-- Guardian's Fang: ivory blade, ember-lit veins.
local FANG_BONE = { 236, 226, 200 }
local FANG_EMBER = { 255, 150, 60 }

local function tierLook(tierId: string?)
	return TIERS[tierId or ""] or FALLBACK_TIER
end

-- A shaft along +Y from y = `from` to `to`.
local function shaft(from: number, to: number, diameter: number, color: { number }, material: string?, name: string?)
	return Part(
		"Cylinder",
		{ to - from, diameter, diameter },
		{ 0, (from + to) / 2, 0 },
		color,
		material or "Wood",
		UPRIGHT,
		{ name = name or "Handle" }
	)
end

-- A diamond tip (a block turned 45 degrees) whose point reaches `y` + about 0.7 of `size`.
local function tip(y: number, thickness: number, size: number, look, name: string?)
	return Part(
		"Block",
		{ thickness, size, size },
		{ 0, y, 0 },
		look.color,
		look.material,
		{ 45, 0, 0 },
		{ name = name or "Tip" }
	)
end

-- Held items --------------------------------------------------------------------

local function spear(look)
	-- ~7 studs: butt at -1.5, leaf head ends near 6.1.
	return {
		parts = {
			shaft(-1.5, 4.7, 0.28, HANDLE, "Wood"),
			Part("Cylinder", { 0.3, 0.36, 0.36 }, { 0, 4.55, 0 }, WRAP, "Fabric", UPRIGHT, { name = "Binding" }),
			Part(
				"Block",
				{ 0.14, 1.1, 0.5 },
				{ 0, 5.15, 0 },
				look.color,
				look.material,
				nil,
				{ name = "Head" }
			),
			tip(5.7, 0.14, 0.5, look, "Tip"),
			Part(
				"Block",
				{ 0.2, 0.3, 0.3 },
				{ 0, -1.5, 0 },
				look.trim,
				look.material,
				nil,
				{ name = "Butt" }
			),
		},
	}
end

local function dagger(look)
	return {
		parts = {
			shaft(-0.45, 0.25, 0.26, HANDLE, "Wood"),
			Part("Ball", { 0.34, 0.34, 0.34 }, { 0, -0.5, 0 }, look.trim, look.material, nil, { name = "Pommel" }),
			Part("Block", { 0.2, 0.14, 0.6 }, { 0, 0.32, 0 }, look.trim, look.material, nil, { name = "Guard" }),
			Part("Block", { 0.1, 1.0, 0.32 }, { 0, 0.89, 0 }, look.color, look.material, nil, { name = "Blade" }),
			tip(1.4, 0.1, 0.22, look, "Tip"),
		},
	}
end

local function sword(look)
	-- ~4.4 studs with the hilt: blade from 0.55 to 3.75, the point just beyond.
	return {
		parts = {
			shaft(-0.45, 0.35, 0.28, HANDLE, "Wood"),
			Part("Ball", { 0.4, 0.4, 0.4 }, { 0, -0.55, 0 }, look.trim, look.material, nil, { name = "Pommel" }),
			Part("Block", { 0.3, 0.2, 1.3 }, { 0, 0.45, 0 }, look.trim, look.material, nil, { name = "Guard" }),
			Part("Block", { 0.14, 3.2, 0.46 }, { 0, 2.15, 0 }, look.color, look.material, nil, { name = "Blade" }),
			tip(3.76, 0.14, 0.32, look, "Tip"),
			Part("Block", { 0.16, 2.6, 0.1 }, { 0, 2.0, 0 }, look.trim, look.material, nil, { name = "Fuller" }),
		},
	}
end

local function guardianFang()
	local ivory = { color = FANG_BONE, material = "Marble", trim = FANG_EMBER }
	return {
		parts = {
			shaft(-0.5, 0.4, 0.3, WRAP, "Fabric"),
			Part("Ball", { 0.46, 0.46, 0.46 }, { 0, -0.62, 0 }, FANG_EMBER, "Neon", nil, { name = "Pommel" }),
			Part("Block", { 0.34, 0.24, 1.5 }, { 0, 0.52, 0 }, FANG_EMBER, "Neon", nil, { name = "Guard" }),
			Part("Block", { 0.2, 3.5, 0.58 }, { 0, 2.4, 0 }, ivory.color, ivory.material, nil, { name = "Blade" }),
			tip(4.2, 0.2, 0.44, ivory, "Tip"),
			Part("Block", { 0.24, 2.9, 0.12 }, { 0, 2.3, 0 }, FANG_EMBER, "Neon", nil, { name = "Vein" }),
			-- Twin barbs near the hilt, like a fang's roots.
			Part("Block", { 0.2, 0.7, 0.2 }, { 0, 0.95, -0.4 }, ivory.color, ivory.material, { -25, 0, 0 }, {
				name = "BarbFront",
			}),
			Part("Block", { 0.2, 0.7, 0.2 }, { 0, 0.95, 0.4 }, ivory.color, ivory.material, { 25, 0, 0 }, {
				name = "BarbBack",
			}),
		},
	}
end

local function axe(look)
	-- ~3 studs; the head's cutting edge faces -Z.
	return {
		parts = {
			shaft(-0.7, 2.3, 0.3, HANDLE, "Wood"),
			Part("Cylinder", { 0.3, 0.38, 0.38 }, { 0, 1.8, 0 }, WRAP, "Fabric", UPRIGHT, { name = "Binding" }),
			Part("Block", { 0.34, 0.7, 0.4 }, { 0, 2.1, 0.18 }, look.color, look.material, nil, { name = "Head" }),
			Part("Block", { 0.14, 1.05, 0.55 }, { 0, 2.1, -0.28 }, look.color, look.material, nil, { name = "Blade" }),
			Part("Block", { 0.1, 1.15, 0.1 }, { 0, 2.1, -0.58 }, look.trim, look.material, nil, { name = "Edge" }),
		},
	}
end

local function pickaxe(look)
	-- ~3 studs tall, the pick bar spans 2.2 studs across Z with both points swept down.
	return {
		parts = {
			shaft(-0.7, 2.3, 0.3, HANDLE, "Wood"),
			Part("Cylinder", { 0.3, 0.38, 0.38 }, { 0, 2.0, 0 }, WRAP, "Fabric", UPRIGHT, { name = "Binding" }),
			Part("Block", { 0.28, 0.34, 1.7 }, { 0, 2.4, 0 }, look.color, look.material, nil, { name = "Head" }),
			Part("Block", { 0.22, 0.6, 0.26 }, { 0, 2.25, -1.0 }, look.trim, look.material, { 35, 0, 0 }, {
				name = "PointFront",
			}),
			Part("Block", { 0.22, 0.6, 0.26 }, { 0, 2.25, 1.0 }, look.trim, look.material, { -35, 0, 0 }, {
				name = "PointBack",
			}),
		},
	}
end

local function bow(look)
	-- ~4 tall, held upright; limb tips and the string sit toward +Z (the archer), the
	-- belly toward -Z (the target). The limbs take the tier's colour.
	return {
		parts = {
			Part("Block", { 0.3, 0.8, 0.34 }, { 0, 0, 0 }, HANDLE, "Wood", nil, { name = "Grip" }),
			Part("Block", { 0.2, 1.6, 0.2 }, { 0, 1.2, 0.18 }, look.color, look.material, { 12, 0, 0 }, {
				name = "LimbUpper",
			}),
			Part("Block", { 0.2, 1.6, 0.2 }, { 0, -1.2, 0.18 }, look.color, look.material, { -12, 0, 0 }, {
				name = "LimbLower",
			}),
			Part("Block", { 0.04, 3.7, 0.04 }, { 0, 0, 0.38 }, STRING, "Fabric", nil, { name = "String" }),
			Part("Ball", { 0.28, 0.28, 0.28 }, { 0, 1.95, 0.38 }, look.trim, look.material, nil, { name = "NockUpper" }),
			Part("Ball", { 0.28, 0.28, 0.28 }, { 0, -1.95, 0.38 }, look.trim, look.material, nil, { name = "NockLower" }),
		},
	}
end

local function arrows(look)
	-- A tied bundle of three flint-tipped arrows (~2.2 studs).
	local parts = {}
	for index, x in { -0.14, 0, 0.14 } do
		table.insert(
			parts,
			Part("Cylinder", { 2.0, 0.07, 0.07 }, { x, 0.7, 0 }, HANDLE, "Wood", UPRIGHT, { name = "Shaft" .. index })
		)
		table.insert(
			parts,
			Part("Block", { 0.06, 0.2, 0.2 }, { x, 1.78, 0 }, look.color, look.material, { 45, 0, 0 }, {
				name = "Tip" .. index,
			})
		)
	end
	table.insert(parts, Part("Block", { 0.4, 0.12, 0.18 }, { 0, 0.5, 0 }, WRAP, "Fabric", nil, { name = "Binding" }))
	return { parts = parts }
end

local function fireBomb()
	return {
		parts = {
			Part("Ball", { 0.95, 0.95, 0.95 }, { 0, 0.45, 0 }, { 92, 58, 42 }, "Slate", nil, { name = "Flask" }),
			Part("Cylinder", { 0.3, 0.32, 0.32 }, { 0, 1.0, 0 }, { 70, 46, 34 }, "Slate", UPRIGHT, { name = "Neck" }),
			Part("Block", { 0.06, 0.34, 0.06 }, { 0, 1.3, 0 }, STRING, "Fabric", nil, { name = "Fuse" }),
			Part("Ball", { 0.22, 0.22, 0.22 }, { 0, 1.5, 0 }, { 255, 140, 40 }, "Neon", nil, { name = "Flame" }),
		},
	}
end

local function breachingCharge()
	return {
		parts = {
			Part("Cylinder", { 1.1, 0.9, 0.9 }, { 0, 0.55, 0 }, { 96, 64, 42 }, "Wood", UPRIGHT, { name = "Keg" }),
			Part("Cylinder", { 0.12, 0.96, 0.96 }, { 0, 0.2, 0 }, IRON_BAND, "Metal", UPRIGHT, { name = "BandLow" }),
			Part("Cylinder", { 0.12, 0.96, 0.96 }, { 0, 0.9, 0 }, IRON_BAND, "Metal", UPRIGHT, { name = "BandHigh" }),
			Part("Block", { 0.06, 0.4, 0.06 }, { 0, 1.3, 0 }, STRING, "Fabric", nil, { name = "Fuse" }),
			Part("Ball", { 0.2, 0.2, 0.2 }, { 0, 1.55, 0 }, { 255, 90, 40 }, "Neon", nil, { name = "Spark" }),
		},
	}
end

-- Consumables and placeables show as something small in the hand.
local function flask(color: { number }, material: string)
	return {
		parts = {
			Part("Ball", { 0.8, 0.8, 0.8 }, { 0, 0.4, 0 }, color, material, nil, { name = "Body" }),
			Part("Cylinder", { 0.3, 0.3, 0.3 }, { 0, 0.9, 0 }, Shade(color, 0.7), material, UPRIGHT, { name = "Neck" }),
			Part("Block", { 0.22, 0.2, 0.22 }, { 0, 1.12, 0 }, HANDLE, "Wood", nil, { name = "Cork" }),
		},
	}
end

local function pouch(color: { number })
	return {
		parts = {
			Part("Ball", { 0.85, 0.75, 0.85 }, { 0, 0.38, 0 }, color, "Fabric", nil, { name = "Body" }),
			Part("Block", { 0.4, 0.16, 0.4 }, { 0, 0.84, 0 }, Shade(color, 0.75), "Fabric", nil, { name = "Tie" }),
		},
	}
end

local function crate()
	return {
		parts = {
			Part("Block", { 1.0, 0.8, 1.0 }, { 0, 0.4, 0 }, { 140, 100, 62 }, "Wood", nil, { name = "Crate" }),
			Part("Block", { 1.06, 0.12, 1.06 }, { 0, 0.4, 0 }, IRON_BAND, "Metal", nil, { name = "Band" }),
		},
	}
end

local WEAPONS = { Spear = spear, Dagger = dagger, Sword = sword, Bow = bow }
local TOOLS = { Axe = axe, Pickaxe = pickaxe }

local heldCache = {}

local function buildHeld(catalogId: string)
	local def = ItemCatalog.Get(catalogId)
	if def == nil then
		return nil
	end
	local look = tierLook(def.tier)
	if catalogId == "GuardianFang" then
		return guardianFang()
	elseif def.weapon then
		local build = WEAPONS[def.weapon.family]
		return build and build(look)
	elseif def.tool then
		local build = TOOLS[def.tool.kind]
		return build and build(look)
	elseif def.family == ItemCatalog.Families.Ammo then
		return arrows(TIERS.Flint)
	elseif def.siege then
		return if def.siege.kind == "Thrown" then fireBomb() else breachingCharge()
	elseif def.consumable then
		local kind = def.consumable.kind
		if kind == "Medicine" then
			return flask({ 200, 72, 72 }, "Glass")
		elseif kind == "Boost" then
			return flask({ 150, 90, 220 }, "Glass")
		end
		return pouch({ 150, 110, 70 })
	elseif def.placeable then
		return crate()
	end
	return nil
end

function GearModels.Held(catalogId: string)
	local cached = heldCache[catalogId]
	if cached == nil then
		cached = buildHeld(catalogId) or false
		heldCache[catalogId] = cached
	end
	return cached or nil
end

-- True when a bow-like item is held upright in the off hand rather than gripped in
-- the right hand (EquipmentVisualService reads this).
function GearModels.IsBow(catalogId: string): boolean
	local def = ItemCatalog.Get(catalogId)
	return def ~= nil and def.weapon ~= nil and def.weapon.family == "Bow"
end

-- Worn armor -----------------------------------------------------------------------

-- Armor character: leather for Hide, bone plates, otherwise a metal-style shell.
local function armorStyle(tierId: string?)
	local look = tierLook(tierId)
	local kind = if tierId == "Hide" then "leather" elseif tierId == "Bone" then "bone" else "metal"
	return look, kind
end

local function helmet(tierId: string?)
	local look, kind = armorStyle(tierId)
	local parts = {
		-- Cap above the eyes, rim just proud of it.
		Part("Block", { 1.35, 0.55, 1.35 }, { 0, 0.34, 0 }, look.color, look.material, nil, { name = "Cap" }),
		Part("Block", { 1.45, 0.1, 1.45 }, { 0, 0.1, 0 }, look.trim, look.material, nil, { name = "Rim" }),
	}
	if kind == "bone" then
		for _, side in { -1, 1 } do
			table.insert(
				parts,
				Part(
					"Block",
					{ 0.18, 0.6, 0.18 },
					{ side * 0.72, 0.55, 0 },
					look.trim,
					look.material,
					nil,
					{ name = side < 0 and "HornLeft" or "HornRight" }
				)
			)
		end
	elseif kind == "metal" then
		table.insert(
			parts,
			Part("Block", { 0.16, 0.3, 1.1 }, { 0, 0.7, 0 }, look.trim, look.material, nil, { name = "Crest" })
		)
		table.insert(
			parts,
			Part("Block", { 0.16, 0.5, 0.1 }, { 0, 0.0, -0.7 }, look.color, look.material, nil, { name = "NoseGuard" })
		)
		if tierId == "Adamantine" or tierId == "Mithril" then
			table.insert(
				parts,
				Part("Ball", { 0.2, 0.2, 0.2 }, { 0, 0.3, -0.7 }, look.trim, "Neon", nil, { name = "Gem" })
			)
		end
	end
	return { parts = parts }
end

local function chestplate(tierId: string?)
	local look, kind = armorStyle(tierId)
	local parts = {
		Part("Block", { 2.1, 1.7, 1.1 }, { 0, 0.1, 0 }, look.color, look.material, nil, { name = "Plate" }),
		Part("Block", { 2.16, 0.26, 1.16 }, { 0, -0.88, 0 }, look.trim, look.material, nil, { name = "Belt" }),
		Part("Block", { 2.04, 0.2, 1.06 }, { 0, 0.98, 0 }, look.trim, look.material, nil, { name = "Collar" }),
	}
	if kind == "metal" then
		-- A raised ridge down the front.
		table.insert(
			parts,
			Part("Block", { 0.3, 1.3, 0.12 }, { 0, 0.15, -0.58 }, look.trim, look.material, nil, { name = "Ridge" })
		)
	elseif kind == "bone" then
		for index, y in { 0.55, 0.05 } do
			table.insert(
				parts,
				Part("Block", { 1.7, 0.16, 0.12 }, { 0, y, -0.58 }, look.trim, look.material, nil, { name = "Rib" .. index })
			)
		end
	else
		table.insert(
			parts,
			Part("Block", { 0.28, 1.7, 1.14 }, { 0, 0.1, 0 }, look.trim, look.material, nil, { name = "Strap" })
		)
	end
	return { parts = parts }
end

-- `side` is +1 for the right arm (outward is +X) and -1 for the left.
local function shoulder(tierId: string?, side: number)
	local look = armorStyle(tierId)
	return {
		parts = {
			Part("Block", { 1.2, 0.45, 1.2 }, { side * 0.08, 0.72, 0 }, look.color, look.material, nil, { name = "Pad" }),
			Part("Block", { 1.28, 0.12, 1.28 }, { side * 0.08, 0.48, 0 }, look.trim, look.material, nil, { name = "Trim" }),
		},
	}
end

local function greave(tierId: string?)
	local look, kind = armorStyle(tierId)
	local parts = {
		Part("Block", { 1.14, 0.8, 1.14 }, { 0, 0.5, 0 }, look.color, look.material, nil, { name = "Thigh" }),
		Part("Block", { 1.2, 0.3, 1.2 }, { 0, 0.05, 0 }, look.trim, look.material, nil, { name = "Knee" }),
		Part("Block", { 1.14, 0.7, 1.14 }, { 0, -0.5, 0 }, look.color, look.material, nil, { name = "Shin" }),
		Part("Block", { 1.2, 0.4, 1.3 }, { 0, -0.8, -0.05 }, look.trim, look.material, nil, { name = "Boot" }),
	}
	if kind == "metal" then
		table.insert(
			parts,
			Part("Block", { 0.14, 0.6, 0.1 }, { 0, -0.45, -0.6 }, look.trim, look.material, nil, { name = "ShinRidge" })
		)
	end
	return { parts = parts }
end

local armorCache = {}

local function buildArmor(catalogId: string)
	local def = ItemCatalog.Get(catalogId)
	local armor = def and def.armor
	if armor == nil then
		return nil
	end
	if armor.slot == "Head" then
		return { Head = helmet(armor.tier) }
	elseif armor.slot == "Chest" then
		return {
			Torso = chestplate(armor.tier),
			["Right Arm"] = shoulder(armor.tier, 1),
			["Left Arm"] = shoulder(armor.tier, -1),
		}
	elseif armor.slot == "Legs" then
		return { ["Right Leg"] = greave(armor.tier), ["Left Leg"] = greave(armor.tier) }
	end
	return nil
end

function GearModels.Armor(catalogId: string)
	local cached = armorCache[catalogId]
	if cached == nil then
		cached = buildArmor(catalogId) or false
		armorCache[catalogId] = cached
	end
	return cached or nil
end

-- Dropped gear ------------------------------------------------------------------------

-- Dropped models are scaled to fit the 1.4 stud pickup box and rest on its floor.
local DROP_SCALE = 0.7
local DROP_FLOOR = -0.7

-- `held` lying on its side: +Y (the business end) points along -Z, i.e. the whole
-- recipe turned by Rx(-90). Only X-axis rotations and the upright Cylinder occur in
-- held recipes, so the composed rotation stays a single Euler triple.
local function layFlat(held)
	local parts = {}
	local lowest = math.huge
	for _, spec in held.parts do
		local size = { spec.size[1] * DROP_SCALE, spec.size[2] * DROP_SCALE, spec.size[3] * DROP_SCALE }
		local pos = { spec.pos[1] * DROP_SCALE, spec.pos[3] * DROP_SCALE, -spec.pos[2] * DROP_SCALE }
		local rot
		local source = spec.rot
		if source == nil then
			rot = { -90, 0, 0 }
		elseif source[2] == 0 and source[3] == 0 then
			rot = { source[1] - 90, 0, 0 }
		else
			-- The upright Cylinder: its axis Y becomes Z.
			rot = { 0, 90, 0 }
		end
		local copy = table.clone(spec)
		copy.size = size
		copy.pos = pos
		copy.rot = rot
		-- Conservative resting height: the part's largest half-extent below its centre.
		local reach = math.max(size[1], size[2], size[3]) / 2
		lowest = math.min(lowest, pos[2] - math.min(reach, size[3] / 2 + 0.1))
		table.insert(parts, copy)
	end
	local lift = DROP_FLOOR - lowest
	local nearest, farthest = math.huge, -math.huge
	for _, spec in parts do
		nearest = math.min(nearest, spec.pos[3])
		farthest = math.max(farthest, spec.pos[3])
	end
	local centre = (nearest + farthest) / 2
	for _, spec in parts do
		spec.pos = { spec.pos[1], spec.pos[2] + lift, spec.pos[3] - centre }
	end
	return { parts = parts }
end

-- Centres `parts` (an armor recipe of one body part) and shrinks it to fit the box.
local function shrink(recipe)
	local parts = {}
	local low, high = Recipe.Bounds(recipe)
	local centre = { (low[1] + high[1]) / 2, (low[2] + high[2]) / 2, (low[3] + high[3]) / 2 }
	local biggest = math.max(high[1] - low[1], high[2] - low[2], high[3] - low[3])
	local scale = math.min(1, 1.3 / biggest)
	for _, spec in recipe.parts do
		local copy = table.clone(spec)
		copy.size = { spec.size[1] * scale, spec.size[2] * scale, spec.size[3] * scale }
		copy.pos = {
			(spec.pos[1] - centre[1]) * scale,
			(spec.pos[2] - centre[2]) * scale + (DROP_FLOOR + (high[2] - low[2]) * scale / 2),
			(spec.pos[3] - centre[3]) * scale,
		}
		table.insert(parts, copy)
	end
	return { parts = parts }
end

local dropCache = {}

local function buildDrop(catalogId: string)
	local def = ItemCatalog.Get(catalogId)
	if def == nil then
		return nil
	end
	if def.armor then
		local worn = GearModels.Armor(catalogId)
		local piece = worn and (worn.Head or worn.Torso or worn["Right Leg"])
		return piece and shrink(piece)
	end
	if def.tool or def.weapon or def.siege then
		local held = GearModels.Held(catalogId)
		if held == nil then
			return nil
		end
		-- Siege items stay upright; long gear lies down.
		return if def.siege then shrink(held) else layFlat(held)
	end
	return nil
end

function GearModels.Drop(catalogId: string)
	local cached = dropCache[catalogId]
	if cached == nil then
		cached = buildDrop(catalogId) or false
		dropCache[catalogId] = cached
	end
	return cached or nil
end

return GearModels
