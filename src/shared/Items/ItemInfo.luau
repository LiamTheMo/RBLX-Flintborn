-- What the inventory screens say about an item (GDD §25.4): its category tab
-- (All / Tools / Materials / Food), and short stat chips for the detail strip,
-- each {glyph?, text}: weapon damage, tool tier, armour, healing, hunger and
-- boosts, or a stack's size. Pure functions over the catalogs, for the client
-- and specs.

local ArmorRules = require(script.Parent.Parent.Combat.ArmorRules)
local ItemCatalog = require(script.Parent.ItemCatalog)
local WeaponCatalog = require(script.Parent.Parent.Combat.WeaponCatalog)

local ItemInfo = {}

ItemInfo.CATEGORIES = { "All", "Tools", "Materials", "Food" }

local FAMILY_CATEGORY = {
	Tool = "Tools",
	Weapon = "Tools",
	Material = "Materials",
	Consumable = "Food",
}

-- The category tab an item belongs to besides All, or nil (armour, ammunition,
-- siege items and placeables show under All only).
function ItemInfo.Category(catalogId: string?): string?
	local def = ItemCatalog.Get(catalogId)
	return def and FAMILY_CATEGORY[def.family] or nil
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

local function percent(x: number): string
	return string.format("%d%%", math.round(x * 100))
end

-- Stat chips for an item ({catalogId, quantity?, qualityRoll?}), at most three.
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
