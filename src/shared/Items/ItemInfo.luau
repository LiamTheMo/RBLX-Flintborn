-- What the item screens say about an item (GDD §25.4; docs/ui/ARCHITECTURE.md
-- D10, D11): its category tab (All / Tools / Materials / Food / Plants / Misc),
-- a short description (authored here, in the UI layer, or derived from the
-- catalog), labelled stat rows for detail cards, the kit icon that depicts it
-- while it has no art of its own, and the older stat chips. Pure functions over
-- the catalogs, for the client and specs.

local ArmorRules = require(script.Parent.Parent.Combat.ArmorRules)
local GameConstants = require(script.Parent.Parent.GameConstants)
local ItemCatalog = require(script.Parent.ItemCatalog)
local NodeCatalog = require(script.Parent.Parent.Resources.NodeCatalog)
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

-- Kit icons that truly depict an item, shown while it has no item art of its own
-- (lk_item_<id> / item_<id>); nil leaves the kit's fallback (the name in ink).
ItemInfo.ICONS = {
	StoneAxe = "stone_axe",
	Wood = "logs",
	Stone = "stones",
	Flint = "stone",
	Fiber = "plant_fiber",
	Hide = "hide",
	Bone = "bone",
	RawMeat = "drumstick",
	CookedMeat = "drumstick",
	Redberry = "berries",
	Sweetberry = "berries",
	Raspberry = "berries",
	CaveMushroom = "mushroom",
	RedcapMushroom = "mushroom",
	ChestnutMushroom = "mushroom",
	Amethyst = "crystals",
	Stormglass = "crystals",
	GuardianFang = "tusk",
}

local KIND_ICONS = { Axe = "hatchet", Pickaxe = "pickaxe", Spear = "spear" }

function ItemInfo.Icon(catalogId: string?): string?
	local def = ItemCatalog.Get(catalogId)
	if def == nil then
		return nil
	end
	local kind = kindOf(def)
	return ItemInfo.ICONS[def.id] or (kind and KIND_ICONS[kind]) or nil
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
