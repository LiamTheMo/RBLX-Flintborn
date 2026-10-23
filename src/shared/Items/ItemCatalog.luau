-- Every launch item archetype (GDD §4.2, §19.1, Q100–108). Rarity is fixed per
-- archetype; individual unique items may carry a small quality roll. Stackable items
-- (materials, ammunition, consumables, placeables) occupy one slot per type; tools,
-- weapons and armor are unique instances. Values not confirmed by the GDD are
-- starting placeholders.

local Consumables = require(script.Parent.Consumables)
local Rarity = require(script.Parent.Rarity)

local ItemCatalog = {}

ItemCatalog.Families = {
	Material = "Material",
	Tool = "Tool",
	Weapon = "Weapon",
	Armor = "Armor",
	Ammo = "Ammo",
	Consumable = "Consumable",
	Placeable = "Placeable",
}

-- Per-slot stack caps by family (material cap matches the vault stack cap).
ItemCatalog.STACK_CAPS = {
	Material = 1000,
	Ammo = 500,
	Consumable = 50,
	Placeable = 5,
}

local F = ItemCatalog.Families

local function material(id: string, name: string, rarity: string?)
	return { id = id, name = name, family = F.Material, rarity = rarity or "Common" }
end

local function tool(id: string, name: string, kind: string, tier: number, rarity: string?)
	return { id = id, name = name, family = F.Tool, rarity = rarity or "Common", tool = { kind = kind, tier = tier } }
end

local function weapon(id: string, name: string, weaponFamily: string, rarity: string?)
	return { id = id, name = name, family = F.Weapon, rarity = rarity or "Common", weapon = { family = weaponFamily } }
end

local function armor(tier: string, slot: string, rarity: string?)
	return {
		id = tier .. slot,
		name = tier .. " " .. (slot == "Legs" and "Legs/Boots" or slot),
		family = F.Armor,
		rarity = rarity or "Common",
		armor = { slot = slot, tier = tier },
	}
end

local entries = {
	-- Materials (GDD Q104 small starting catalog)
	material("Wood", "Wood"),
	material("Stone", "Stone"),
	material("Iron", "Iron"),
	material("Fiber", "Plant Fiber"),
	material("Herbs", "Herbs"),
	material("Hide", "Hide"),
	-- Inner Ring materials (GDD §18.1).
	material("Jade", "Jade", "Uncommon"),
	material("Obsidian", "Obsidian", "Uncommon"),
	-- Special material: rare-event reagent (v0.11 events drop it). Special materials
	-- wait in the lobby backpack after extraction instead of auto-banking (Q129).
	{
		id = "AncientEmber",
		name = "Ancient Ember",
		family = F.Material,
		rarity = "Epic",
		special = true,
		tags = { "event" },
	},

	-- Tools
	tool("StoneAxe", "Stone Axe", "Axe", 1),
	tool("BasicPickaxe", "Basic Pickaxe", "Pickaxe", 1),
	tool("Sickle", "Sickle", "Sickle", 1),
	tool("IronAxe", "Iron Axe", "Axe", 2, "Uncommon"),
	tool("IronPickaxe", "Iron Pickaxe", "Pickaxe", 2, "Uncommon"),

	-- Weapons (Q100: spears, daggers, swords, bows)
	weapon("WoodenSpear", "Wooden Spear", "Spear"),
	weapon("StoneSpear", "Stone Spear", "Spear"),
	weapon("StoneDagger", "Stone Dagger", "Dagger"),
	weapon("StoneSword", "Stone Sword", "Sword"),
	weapon("IronSword", "Iron Sword", "Sword", "Rare"),
	weapon("BasicBow", "Basic Bow", "Bow"),
	-- The Guardian's once-per-encounter Legendary (GDD §8.1); ordinary world loot.
	weapon("GuardianFang", "Guardian's Fang", "Sword", "Legendary"),

	-- Armor (Q101: Head, Chest, Legs/Boots)
	armor("Hide", "Head"),
	armor("Hide", "Chest"),
	armor("Hide", "Legs"),
	armor("Wood", "Head"),
	armor("Wood", "Chest"),
	armor("Wood", "Legs"),
	armor("Stone", "Head", "Uncommon"),
	armor("Stone", "Chest", "Uncommon"),
	armor("Stone", "Legs", "Uncommon"),
	armor("Iron", "Head", "Rare"),
	armor("Iron", "Chest", "Rare"),
	armor("Iron", "Legs", "Rare"),

	-- Ammunition (Q107)
	{ id = "Arrow", name = "Arrow", family = F.Ammo, rarity = "Common" },

	-- Placeables
	{ id = "Workbench", name = "Workbench", family = F.Placeable, rarity = "Common", placeable = "Workbench" },
	-- Extremely rare portable extraction rune (GDD Q22, Q158): 30 s, anywhere but inside
	-- structures, never the Center bonus.
	{
		id = "ExtractionRune",
		name = "Portable Extraction Rune",
		family = F.Placeable,
		rarity = "Legendary",
		placeable = "ExtractionRune",
	},
}

-- Medicine and food come from the consumables catalog.
for id, consumable in Consumables.Catalog do
	table.insert(entries, {
		id = id,
		name = consumable.name,
		family = F.Consumable,
		rarity = "Common",
		consumable = consumable,
	})
end

ItemCatalog.Items = {}
for _, entry in entries do
	assert(ItemCatalog.Items[entry.id] == nil, "Duplicate item " .. entry.id)
	assert(Rarity.IsValid(entry.rarity), "Bad rarity for " .. entry.id)
	entry.tags = entry.tags or {}
	ItemCatalog.Items[entry.id] = entry
end

function ItemCatalog.Get(catalogId: any)
	return type(catalogId) == "string" and ItemCatalog.Items[catalogId] or nil
end

-- Stack cap for stackable items, or nil for unique instances.
function ItemCatalog.StackCap(catalogId: string): number?
	local item = ItemCatalog.Get(catalogId)
	return item and ItemCatalog.STACK_CAPS[item.family] or nil
end

function ItemCatalog.IsStackable(catalogId: string): boolean
	return ItemCatalog.StackCap(catalogId) ~= nil
end

-- Ordinary materials auto-bank into the vault on extraction; special materials
-- (flagged `special`, e.g. event reagents) wait in the lobby backpack (Q129).
function ItemCatalog.IsOrdinaryMaterial(catalogId: string): boolean
	local item = ItemCatalog.Get(catalogId)
	return item ~= nil and item.family == F.Material and not item.special
end

function ItemCatalog.IsMaterial(catalogId: string): boolean
	local item = ItemCatalog.Get(catalogId)
	return item ~= nil and item.family == F.Material
end

-- Tools, weapons, consumables, ammo and placeables go to the hotbar first;
-- materials and armor go to the backpack first.
function ItemCatalog.PrefersHotbar(catalogId: string): boolean
	local item = ItemCatalog.Get(catalogId)
	return item ~= nil and item.family ~= F.Material and item.family ~= F.Armor
end

return ItemCatalog
