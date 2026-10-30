-- What the item screens say about an item (GDD §25.4; docs/ui/ARCHITECTURE.md
-- D10, D11): its category tab (All / Tools / Materials / Food / Plants / Misc),
-- a short description (authored here, in the UI layer, or derived from the
-- catalog), labelled stat rows for detail cards, the kit art (and tint) that
-- shows it while it has no art of its own, and the older stat chips. Pure functions over
-- the catalogs, for the client and specs.

local ArmorRules = require(script.Parent.Parent.Combat.ArmorRules)
local GameConstants = require(script.Parent.Parent.GameConstants)
local ItemCatalog = require(script.Parent.ItemCatalog)
local NodeCatalog = require(script.Parent.Parent.Resources.NodeCatalog)
local Tiers = require(script.Parent.Tiers)
local WeaponCatalog = require(script.Parent.Parent.Combat.WeaponCatalog)

local ItemInfo = {}

ItemInfo.CATEGORIES = { "All", "Tools", "Materials", "Food", "Plants", "Misc" }

local F = ItemCatalog.Families

local FAMILY_CATEGORY = {
	[F.Tool] = "Tools",
	[F.Weapon] = "Tools",
	[F.Material] = "Materials",
	[F.Consumable] = "Food",
}

-- Plants are the materials picked from plants (the resource nodes gathered with
-- the Farming mastery: fiber, herbs, shrubs, mushrooms). Berries that are food
-- stay under Food.
local PLANTS = {}
for _, node in NodeCatalog.Nodes do
	if node.mastery == "Farming" and ItemCatalog.IsMaterial(node.material) then
		PLANTS[node.material] = true
	end
end

-- The category tab an item belongs to besides All, or nil for an unknown item.
-- Items no other tab takes (armour, ammunition, siege items, placeables) are Misc.
function ItemInfo.Category(catalogId: string?): string?
	local def = ItemCatalog.Get(catalogId)
	if def == nil then
		return nil
	end
	if PLANTS[def.id] then
		return "Plants"
	end
	return FAMILY_CATEGORY[def.family] or "Misc"
end

-- Whether an item shows under tab `category`.
function ItemInfo.InCategory(catalogId: string?, category: string): boolean
	return category == "All" or ItemInfo.Category(catalogId) == category
end

-- Whether `name` matches a search (case-insensitive, plain text).
function ItemInfo.Matches(name: string?, query: string?): boolean
	if query == nil or query == "" then
		return true
	end
	return string.find(string.lower(name or ""), string.lower(query), 1, true) ~= nil
end

-- Short authored descriptions (D10). Per item first, then per kind of item;
-- an item with neither shows its derived summary (ItemInfo.Summary).
ItemInfo.DESCRIPTIONS = {
	Wood = "Chopped from trees. An axe gets more out of every swing.",
	Stone = "Mined from rocks. A pickaxe gets more out of every swing.",
	Flint = "Chips off rocks as you mine them. The only arrow tip.",
	Fiber = "Pulled from fiber plants by hand.",
	Herbs = "Picked from herb shrubs by hand.",
	Resin = "Sometimes drips from trees as you chop them.",
	GuardianFang = "The Guardian's own fang, stronger than any crafted sword.",
	FlintArrow = "Fired from a bow. Its damage adds to the bow's.",
	FireBomb = "Ready it, then throw it with the attack input.",
	BreachingCharge = "Set it on a wall or door in front of you.",
	Workbench = "Place it in the world to craft at it.",
	ExtractionRune = "Place it to open an extraction point for 30 seconds.",
	AncientEmber = "A rare reagent from the island's events.",
}

local KIND_DESCRIPTIONS = {
	Axe = "Chops trees for more wood per swing than bare hands.",
	Pickaxe = "Mines rock and ore. Better pickaxes reach deeper ores.",
	Spear = "The longest melee reach, with slower thrusts.",
	Sword = "Wide swings at a steady pace.",
	Dagger = "Short reach and quick strikes.",
	Bow = "Fires Flint Arrows: the bow's damage and the arrow's add up.",
	Armor = "Worn pieces add together to cut the damage you take.",
	Medicine = "Heals you at once.",
	Food = ("Eases hunger. Food that heals does so over %d seconds."):format(GameConstants.FOOD_HEAL_SECONDS),
	Boost = "Starts a timed boost when used.",
}

-- The kind an item's description and icon go by ("Axe", "Sword", "Food"...).
local function kindOf(def): string?
	if def.tool then
		return def.tool.kind
	elseif def.weapon then
		return def.weapon.family
	elseif def.armor then
		return "Armor"
	elseif def.consumable then
		return def.consumable.kind
	end
	return nil
end

-- The authored description of an item, or nil.
function ItemInfo.Description(catalogId: string?): string?
	local def = ItemCatalog.Get(catalogId)
	if def == nil then
		return nil
	end
	local kind = kindOf(def)
	return ItemInfo.DESCRIPTIONS[def.id] or (kind and KIND_DESCRIPTIONS[kind]) or nil
end

local FAMILY_NOUNS = {
	[F.Material] = "material",
	[F.Tool] = "tool",
	[F.Weapon] = "weapon",
	[F.Armor] = "armour",
	[F.Ammo] = "ammunition",
	[F.Consumable] = "consumable",
	[F.Siege] = "siege item",
	[F.Placeable] = "placeable",
}

-- The derived line for an item ({catalogId, permanent?}): rarity, family and what
-- a death in a run does to it (GDD §25.4), e.g. "Common tool · At risk — drops
-- on death".
function ItemInfo.Summary(item): string
	local def = ItemCatalog.Get(item and item.catalogId)
	if def == nil then
		return ""
	end
	local risk = if item.permanent then "Permanent — kept on death" else "At risk — drops on death"
	return ("%s %s · %s"):format(def.rarity, FAMILY_NOUNS[def.family] or "item", risk)
end

-- What a detail card writes under the name: the description, else the summary.
function ItemInfo.Text(item): string
	return ItemInfo.Description(item and item.catalogId) or ItemInfo.Summary(item)
end

local function percent(x: number): string
	return string.format("%d%%", math.round(x * 100))
end

local function duration(seconds: number): string
	if seconds >= 60 and seconds % 60 == 0 then
		return ("%d min"):format(seconds // 60)
	end
	return ("%d s"):format(seconds)
end

-- The node an item kind harvests, for Harvest Power.
local HARVEST_NODE = { Axe = "Tree", Pickaxe = "Rock" }

export type StatRow = { icon: string, label: string, value: string }

-- Labelled stats for a detail card, most telling first, for an item
-- ({catalogId, quantity?, qualityRoll?}). Every value is real: weapon damage
-- (with its quality roll) and attack speed (the real cooldown), harvest power
-- (drops per hit on a tree or rock) and tool tier, armour, healing, food,
-- boosts, a quality roll and the stack size. Nothing wears out in this game,
-- so there is no durability. Empty for an unknown item.
function ItemInfo.StatRows(item): { StatRow }
	local def = ItemCatalog.Get(item and item.catalogId)
	if def == nil then
		return {}
	end
	local rows: { StatRow } = {}
	local function add(icon: string, label: string, value: string)
		table.insert(rows, { icon = icon, label = label, value = value })
	end
	local roll = item.qualityRoll or 0
	if def.weapon then
		local profile = WeaponCatalog.For(def.id)
		if profile.bowDamage then
			add("spear", "Damage", ("%d + arrow"):format(math.round(profile.bowDamage * (1 + roll))))
		else
			add("spear", "Damage", ("%d"):format(math.round((profile.damage or 0) * (1 + roll))))
		end
		if profile.cooldown then
			add("clock", "Attack Speed", ("%.1fs"):format(profile.cooldown))
		end
	elseif def.tool then
		local node = HARVEST_NODE[def.tool.kind]
		if node then
			add("hammer", "Harvest Power", ("%d per hit"):format(NodeCatalog.YieldFor(node, def.tool)))
		end
		add(if def.tool.kind == "Axe" then "hatchet" else "pickaxe", "Tool Tier", tostring(def.tool.tier or 1))
	elseif def.armor then
		add("lock", "Armour", "+" .. percent(ArmorRules.PieceIncrement(def.armor.tier, def.armor.slot, roll)))
		add("backpack_small", "Worn On", def.armor.slot)
	elseif def.consumable then
		local c = def.consumable
		if (c.heal or 0) > 0 then
			add("heart", "Heals", tostring(c.heal))
		end
		if (c.hunger or 0) > 0 then
			add("drumstick", "Food", "+" .. percent(c.hunger))
		end
		if c.boost then
			add(
				if c.boost.kind == "Luck" then "star" else "lightning",
				c.boost.kind .. " Boost",
				("+%s · %s"):format(percent(c.boost.amount), duration(c.boost.seconds))
			)
		end
	elseif def.family == F.Ammo then
		local arrow = WeaponCatalog.Arrows[def.id]
		if arrow then
			add("spear", "Arrow Damage", "+" .. arrow.damage)
		end
	end
	if roll ~= 0 then
		add("star", "Quality", ("%+.1f%%"):format(roll * 100))
	end
	if item.quantity and item.quantity > 1 then
		local cap = ItemCatalog.StackCap(def.id)
		add(
			"backpack_small",
			"Quantity",
			if cap then ("%d / %d"):format(item.quantity, cap) else tostring(item.quantity)
		)
	end
	return rows
end

-- Item art (docs/ui/ITEM_ART.md). Until an item has art of its own (lk_item_<id>
-- / item_<id>), ItemInfo.Icon names the kit art that shows it: the exact icon
-- where the kit has one, otherwise the closest kit art, often tinted (an
-- ImageColor3 multiply, so tints only darken or shift a hue). Names are kit icon
-- ids (lk_icon_<id>) or full lk_ sprite names for other kit art. Bows have no
-- art that reads as a bow, so they keep the kit's fallback (their name).

-- Every kit sprite item art may use. KitModel's role table does not list icons
-- and specs cannot read the sprite manifest, so the item_info spec checks
-- Icon's answers against this list and the inventory capture checks the list
-- against the manifest.
ItemInfo.ART_SPRITES = {
	"lk_icon_berries",
	"lk_icon_bone",
	"lk_icon_build",
	"lk_icon_campfire",
	"lk_icon_crystals",
	"lk_icon_drumstick",
	"lk_icon_hatchet",
	"lk_icon_heart",
	"lk_icon_hide",
	"lk_icon_lightning",
	"lk_icon_logs",
	"lk_icon_magma_ore",
	"lk_icon_mushroom",
	"lk_icon_pickaxe",
	"lk_icon_plank",
	"lk_icon_plant_fiber",
	"lk_icon_rocks",
	"lk_icon_rope",
	"lk_icon_runestone",
	"lk_icon_spear",
	"lk_icon_star",
	"lk_icon_stone",
	"lk_icon_stone_axe",
	"lk_icon_stones",
	"lk_icon_torch",
	"lk_icon_tusk",
	"lk_icon_warning",
}

-- The sprite an icon name draws (lk_icon_<id> for an icon id).
function ItemInfo.Sprite(name: string): string
	return if string.sub(name, 1, 3) == "lk_" then name else "lk_icon_" .. name
end

local function rgb(r: number, g: number, b: number): Color3
	return Color3.fromRGB(r, g, b)
end

-- Material tints for gear made from it, ores and bars (multiplied over art
-- that is grey stone, iron, ivory or brown wood). The stone spear and the
-- iron-headed hatchet and pickaxe are drawn untinted.
ItemInfo.TIER_TINTS = {
	Wood = rgb(230, 175, 120),
	Stone = rgb(205, 205, 212),
	Flint = rgb(150, 150, 165),
	Bone = rgb(250, 240, 215),
	Obsidian = rgb(115, 100, 140),
	Jade = rgb(150, 225, 170),
	Hide = rgb(215, 165, 120),
	Copper = rgb(240, 160, 110),
	Iron = rgb(195, 200, 212),
	Silver = rgb(240, 245, 255),
	Cobalt = rgb(130, 160, 240),
	Mithril = rgb(170, 240, 235),
	Adamantine = rgb(190, 130, 215),
}

-- Items the kit draws exactly (the art depicts that very item).
ItemInfo.EXACT = {
	StoneAxe = true,
	IronAxe = true,
	IronPickaxe = true,
	StoneSpear = true,
	Wood = true,
	Stone = true,
	Fiber = true,
	Hide = true,
	Bone = true,
	Redberry = true,
	CookedMeat = true,
	ChestnutMushroom = true,
}

-- Per item: {icon, tint?}. Gear, ores and bars are filled in from their tier below.
local ART = {
	-- Materials.
	Wood = { "logs" },
	Stone = { "stones" },
	Flint = { "stone", ItemInfo.TIER_TINTS.Flint },
	Fiber = { "plant_fiber" },
	Herbs = { "plant_fiber", rgb(190, 235, 160) },
	Resin = { "crystals", rgb(255, 185, 70) },
	Hide = { "hide" },
	RawMeat = { "drumstick", rgb(255, 150, 150) },
	Bone = { "bone" },
	Clay = { "stone", rgb(225, 140, 100) },
	CaveMushroom = { "mushroom", rgb(250, 235, 215) },
	RedcapMushroom = { "mushroom", rgb(255, 120, 110) },
	ChestnutMushroom = { "mushroom" },
	Thornvine = { "rope", rgb(150, 200, 110) },
	Frostleaf = { "plant_fiber", rgb(175, 220, 255) },
	JuniperBerry = { "berries", rgb(140, 150, 230) },
	Elderberry = { "berries", rgb(120, 90, 160) },
	Raspberry = { "berries", rgb(255, 170, 190) },
	Hazelnut = { "berries", rgb(200, 140, 80) },
	Amethyst = { "crystals", rgb(200, 140, 255) },
	Starstone = { "stone", rgb(255, 235, 150) },
	Stormglass = { "crystals" },
	Obsidian = { "stone", ItemInfo.TIER_TINTS.Obsidian },
	Jade = { "crystals", rgb(120, 230, 150) },
	DireHide = { "hide", rgb(140, 115, 110) },
	ChargedCore = { "lightning" },
	GlowFur = { "hide", rgb(190, 245, 245) },
	GuardianHeart = { "heart", rgb(190, 90, 110) },
	AshenOil = { "magma_ore", rgb(170, 165, 160) },
	SiegeResin = { "crystals", rgb(230, 120, 60) },
	AbyssalShard = { "crystals", rgb(120, 90, 170) },
	Emberglass = { "crystals", rgb(255, 140, 70) },
	Bloodroot = { "plant_fiber", rgb(230, 120, 120) },
	Moonpetal = { "plant_fiber", rgb(220, 225, 255) },
	AncientEmber = { "campfire" },
	-- Ammunition, siege items and placeables.
	FlintArrow = { "spear", ItemInfo.TIER_TINTS.Flint },
	FireBomb = { "torch" },
	BreachingCharge = { "warning" },
	Workbench = { "build" },
	ExtractionRune = { "runestone" },
	GuardianFang = { "tusk" },
	-- Medicine, food and draughts.
	BasicMedicine = { "heart", rgb(255, 200, 200) },
	AdvancedMedicine = { "heart" },
	Potion = { "heart", rgb(230, 150, 200) },
	GreaterPotion = { "heart", rgb(190, 110, 200) },
	Redberry = { "berries" },
	Sweetberry = { "berries", rgb(255, 180, 220) },
	Sunberry = { "berries", rgb(255, 215, 110) },
	Glimmerberry = { "berries", rgb(150, 230, 255) },
	CookedMeat = { "drumstick" },
	HeartyTonic = { "heart", rgb(255, 180, 110) },
	SunberryDraught = { "lightning" },
	StrongSunberryDraught = { "lightning", rgb(255, 190, 90) },
	GlimmerDraught = { "star", rgb(170, 230, 255) },
	StrongGlimmerDraught = { "star", rgb(130, 190, 255) },
}

-- Gear by kind: the kit's art for it, and whether the art is already iron.
local GEAR = {
	Axe = { "hatchet", true },
	Pickaxe = { "pickaxe", true },
	Spear = { "spear", false },
	Dagger = { "tusk", false },
	Sword = { "tusk", false },
	Armor = { "hide", false },
}

for id, def in ItemCatalog.Items do
	if ART[id] then
		continue
	end
	local kind = if def.tool
		then def.tool.kind
		elseif def.weapon then def.weapon.family
		elseif def.armor then "Armor"
		else nil
	local gear = kind and GEAR[kind]
	if gear and def.tier then
		local plain = (def.tier == "Iron" and gear[2]) or (def.tier == "Stone" and kind == "Spear")
		ART[id] = { gear[1], if plain then nil else ItemInfo.TIER_TINTS[def.tier] }
	end
end
ART.StoneAxe = { "stone_axe" }
ART.StonePickaxe = { "pickaxe", rgb(215, 215, 220) }
for _, metal in Tiers.Metals do
	local tier = Tiers.Get(metal)
	local tint = ItemInfo.TIER_TINTS[metal]
	ART[tier.ore] = if metal == "Adamantine" then { "magma_ore", tint } else { "rocks", tint }
	ART[tier.material] = { "plank", tint }
end

-- Icon names and tints, kept as two tables (ICONS[id] = name, TINTS[id] = Color3).
ItemInfo.ICONS = {}
ItemInfo.TINTS = {}
for id, art in ART do
	ItemInfo.ICONS[id] = art[1]
	ItemInfo.TINTS[id] = art[2]
end

-- The kit art for an item and its tint, or nil when the kit has nothing that
-- reads as it (bows) or the item is unknown.
function ItemInfo.Icon(catalogId: string?): (string?, Color3?)
	if type(catalogId) ~= "string" then
		return nil, nil
	end
	return ItemInfo.ICONS[catalogId], ItemInfo.TINTS[catalogId]
end

-- "exact" (the art depicts the item), "stand-in" (the closest art, maybe
-- tinted) or "none".
function ItemInfo.ArtStatus(catalogId: string?): string
	if catalogId == nil or ItemInfo.ICONS[catalogId] == nil then
		return "none"
	end
	return if ItemInfo.EXACT[catalogId] then "exact" else "stand-in"
end

-- Stat chips for an item ({catalogId, quantity?, qualityRoll?}), at most three
-- ({glyph?, text}; the older compact form of StatRows).
function ItemInfo.Stats(item): { { glyph: string?, text: string } }
	local def = ItemCatalog.Get(item and item.catalogId)
	if def == nil then
		return {}
	end
	local chips = {}
	if def.weapon then
		local profile = WeaponCatalog.For(def.id)
		-- A bow's own damage (arrows add theirs).
		local base = profile.damage or profile.bowDamage or 0
		local damage = base * (1 + (item.qualityRoll or 0))
		table.insert(chips, { glyph = "sword", text = ("%d dmg"):format(math.round(damage)) })
		if profile.cooldown then
			table.insert(chips, { text = ("%.1fs"):format(profile.cooldown) })
		end
	elseif def.tool then
		table.insert(chips, { glyph = "hammer", text = ("Tier %d"):format(def.tool.tier or 1) })
		table.insert(chips, { text = def.tool.kind })
	elseif def.armor then
		local increment = ArmorRules.PieceIncrement(def.armor.tier, def.armor.slot, item.qualityRoll)
		table.insert(chips, { text = "Armour +" .. percent(increment) })
		table.insert(chips, { text = def.armor.slot })
	elseif def.consumable then
		local c = def.consumable
		if (c.heal or 0) > 0 then
			table.insert(chips, { text = ("Heals %d"):format(c.heal) })
		end
		if (c.hunger or 0) > 0 then
			table.insert(chips, { text = "Food +" .. percent(c.hunger) })
		end
		if c.boost then
			table.insert(chips, { text = ("%s +%s"):format(c.boost.kind, percent(c.boost.amount)) })
		end
	end
	if item.quantity and #chips < 3 then
		table.insert(chips, { glyph = "weight", text = ("×%d"):format(item.quantity) })
	end
	while #chips > 3 do
		table.remove(chips)
	end
	return chips
end

return ItemInfo
