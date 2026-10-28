-- Every item archetype (GDD §4.2, §19.1, §51). Rarity is fixed per archetype;
-- individual unique items may carry a small quality roll. Stackable items
-- (materials, ammunition, consumables, siege items, placeables) occupy one slot per
-- type; tools, weapons and armor are unique instances. Gear is generated from the
-- tier ladder (Tiers): what each material can make, its rarity and its tool rank.
-- Values not confirmed by the GDD are starting placeholders.

local Consumables = require(script.Parent.Consumables)
local Rarity = require(script.Parent.Rarity)
local Tiers = require(script.Parent.Tiers)

local ItemCatalog = {}

ItemCatalog.Families = {
	Material = "Material",
	Tool = "Tool",
	Weapon = "Weapon",
	Armor = "Armor",
	Ammo = "Ammo",
	Consumable = "Consumable",
	Siege = "Siege",
	Placeable = "Placeable",
}

-- Per-slot stack caps by family (material cap matches the vault stack cap).
ItemCatalog.STACK_CAPS = {
	Material = 1000,
	Ammo = 500,
	Consumable = 50,
	Siege = 10,
	Placeable = 5,
}

local F = ItemCatalog.Families

-- `tradeable` marks the materials players may trade (GDD §51: elite, Guardian,
-- meteor and cache materials, rare herbs, and Ancient Ember); common materials,
-- ores and bars never trade.
local function material(id: string, name: string, rarity: string?, extra: any?)
	local entry = { id = id, name = name, family = F.Material, rarity = rarity or "Common" }
	for key, value in extra or {} do
		entry[key] = value
	end
	return entry
end

local entries = {
	-- Common materials (gathered everywhere).
	material("Wood", "Wood"),
	material("Stone", "Stone"),
	material("Flint", "Flint"),
	material("Fiber", "Plant Fiber"),
	material("Herbs", "Herbs"),
	material("Resin", "Resin"),
	material("Hide", "Hide"),
	material("RawMeat", "Raw Meat"),
	material("Bone", "Bone"),

	-- Restricted (gem-class) materials: daggers and spears only (Flint also arrows).
	material("Obsidian", "Obsidian", "Uncommon"),
	material("Jade", "Jade", "Rare"),

	-- Rare and endgame materials (tradeable).
	material("DireHide", "Dire Hide", "Uncommon", { tradeable = true }),
	material("ChargedCore", "Charged Core", "Rare", { tradeable = true }),
	material("GlowFur", "Glow-Fur", "Rare", { tradeable = true }),
	material("GuardianHeart", "Guardian Heart", "Legendary", { tradeable = true }),
	material("AshenOil", "Ashen Oil", "Rare", { tradeable = true }),
	material("SiegeResin", "Siege Resin", "Rare", { tradeable = true }),
	material("AbyssalShard", "Abyssal Shard", "Epic", { tradeable = true }),
	material("Emberglass", "Emberglass", "Epic", { tradeable = true }),
	material("Bloodroot", "Bloodroot", "Rare", { tradeable = true }),
	material("Moonpetal", "Moonpetal", "Rare", { tradeable = true }),
	-- Special material: the rare-event reagent (v0.11 events drop it).
	material("AncientEmber", "Ancient Ember", "Epic", { special = true, tradeable = true, tags = { "event" } }),

	-- Ammunition: Flint is the only arrow tip (Q107, GDD §51).
	{ id = "FlintArrow", name = "Flint Arrow", family = F.Ammo, rarity = "Common" },

	-- Siege items (GDD §51): thrown fire, placed breaching charge.
	{ id = "FireBomb", name = "Fire Bomb", family = F.Siege, rarity = "Rare", siege = { kind = "Thrown" } },
	{
		id = "BreachingCharge",
		name = "Breaching Charge",
		family = F.Siege,
		rarity = "Rare",
		siege = { kind = "Placed" },
	},

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

	-- The Guardian's once-per-encounter Legendary (GDD §8.1): stronger than any
	-- crafted sword (one tier above Adamantine).
	{
		id = "GuardianFang",
		name = "Guardian's Fang",
		family = F.Weapon,
		rarity = "Legendary",
		weapon = { family = "Sword" },
	},
}

-- Ores and bars for every metal (GDD §51): ore smelts 1:1 into bars at a Furnace.
for _, metal in Tiers.Metals do
	local tier = Tiers.Get(metal)
	table.insert(entries, material(tier.ore, metal .. " Ore", tier.rarity))
	table.insert(entries, material(tier.material, metal .. " Bar", tier.rarity))
end

local ARMOR_SLOTS = { "Head", "Chest", "Legs" }
local SLOT_NAMES = { Head = "Head", Chest = "Chest", Legs = "Legs/Boots" }

-- The display prefix for gear of a tier ("Wooden" for wood, otherwise the tier).
local function prefix(tierId: string): string
	return if tierId == "Wood" then "Wooden" else tierId
end

-- Gear id for a tier and family (e.g. "IronSword", "WoodenBow", "BoneChest").
function ItemCatalog.GearId(tierId: string, family: string): string
	return prefix(tierId) .. family
end

-- Gear from the ladder: weapons, tools and armor each material can make.
for _, tier in Tiers.Ladder do
	for _, family in { "Spear", "Dagger", "Sword", "Bow" } do
		if tier.canMake[family] then
			table.insert(entries, {
				id = ItemCatalog.GearId(tier.id, family),
				name = prefix(tier.id) .. " " .. family,
				family = F.Weapon,
				rarity = tier.rarity,
				tier = tier.id,
				weapon = { family = family },
			})
		end
	end
	for _, kind in { "Axe", "Pickaxe" } do
		if tier.canMake[kind] then
			table.insert(entries, {
				id = ItemCatalog.GearId(tier.id, kind),
				name = prefix(tier.id) .. " " .. kind,
				family = F.Tool,
				rarity = tier.rarity,
				tier = tier.id,
				tool = { kind = kind, tier = Tiers.ToolRank[tier.id] },
			})
		end
	end
	if tier.canMake.Armor then
		for _, slot in ARMOR_SLOTS do
			table.insert(entries, {
				id = tier.id .. slot,
				name = tier.id .. " " .. SLOT_NAMES[slot],
				family = F.Armor,
				rarity = tier.rarity,
				tier = tier.id,
				armor = { slot = slot, tier = tier.id },
			})
		end
	end
end

-- Medicine and food come from the consumables catalog.
for id, consumable in Consumables.Catalog do
	table.insert(entries, {
		id = id,
		name = consumable.name,
		family = F.Consumable,
		rarity = consumable.rarity or "Common",
		tradeable = consumable.tradeable,
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
