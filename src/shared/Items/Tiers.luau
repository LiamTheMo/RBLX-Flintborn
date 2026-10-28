-- The gear ladder (GDD §51, owner decisions 2026-10-27): Wood → Stone → Copper →
-- Iron → Silver → Cobalt → Mithril → Adamantine, each about 25% stronger than the
-- last, plus the restricted materials (Flint, Bone, Obsidian, Jade) that slot in
-- between. Items, recipes, weapon damage, armor and building tiers are all
-- generated from this table, so adding a tier later is one entry here. Every
-- number is a starting value except the confirmed anchors (wooden spear 15,
-- stone spear 25, Hide armor ×1.2, Iron armor ×2.0).

local GameConstants = require(script.Parent.Parent.GameConstants)

local Tiers = {}

-- Strength multiplies by this per tier.
Tiers.STEP = 1.25

-- `power` is the tier's position on the strength curve (Stone = 2). `material` is
-- the item gear is made from; `station` where it is crafted. `makes` lists the
-- gear families the material can make (restricted materials make few). `rarity`
-- rises slowly: Legendary and above stay for boss and event drops.
Tiers.Ladder = {
	{
		id = "Wood",
		power = 1,
		material = "Wood",
		station = "Anywhere",
		rarity = "Common",
		makes = { "Spear", "Bow", "Axe", "Pickaxe", "Building" },
	},
	{
		id = "Stone",
		power = 2,
		material = "Stone",
		station = "Anywhere",
		rarity = "Common",
		makes = { "Spear", "Dagger", "Sword", "Axe", "Pickaxe", "Building" },
	},
	{
		id = "Hide",
		power = 1,
		armorFactor = GameConstants.ARMOR_SET_FACTOR.Hide,
		material = "Hide",
		station = "Anywhere",
		rarity = "Common",
		makes = { "Armor" },
	},
	{
		id = "Bone",
		power = 2.3,
		armorFactor = 1.5,
		material = "Bone",
		station = "Anywhere",
		rarity = "Common",
		makes = { "Spear", "Dagger", "Armor" },
	},
	{
		id = "Flint",
		power = 2.5,
		material = "Flint",
		station = "Anywhere",
		rarity = "Common",
		makes = { "Spear", "Dagger" },
	},
	{
		id = "Copper",
		power = 3,
		armorFactor = 1.8,
		material = "CopperBar",
		ore = "CopperOre",
		station = "Workbench",
		rarity = "Common",
		makes = { "Spear", "Dagger", "Sword", "Bow", "Axe", "Pickaxe", "Armor", "Building" },
	},
	{
		id = "Iron",
		power = 4,
		armorFactor = GameConstants.ARMOR_SET_FACTOR.Iron,
		material = "IronBar",
		ore = "IronOre",
		station = "Workbench",
		rarity = "Common",
		makes = { "Spear", "Dagger", "Sword", "Bow", "Axe", "Pickaxe", "Armor", "Building" },
	},
	{
		id = "Obsidian",
		power = 4.5,
		material = "Obsidian",
		station = "Workbench",
		rarity = "Uncommon",
		makes = { "Spear", "Dagger" },
	},
	{
		id = "Silver",
		power = 5,
		material = "SilverBar",
		ore = "SilverOre",
		station = "Anvil",
		rarity = "Uncommon",
		makes = { "Spear", "Dagger", "Sword", "Bow", "Axe", "Pickaxe", "Armor", "Building" },
	},
	{
		id = "Cobalt",
		power = 6,
		material = "CobaltBar",
		ore = "CobaltOre",
		station = "Anvil",
		rarity = "Uncommon",
		makes = { "Spear", "Dagger", "Sword", "Bow", "Axe", "Pickaxe", "Armor", "Building" },
	},
	{
		id = "Jade",
		power = 6.5,
		material = "Jade",
		station = "Anvil",
		rarity = "Rare",
		makes = { "Spear", "Dagger" },
	},
	{
		id = "Mithril",
		power = 7,
		material = "MithrilBar",
		ore = "MithrilOre",
		station = "Anvil",
		rarity = "Rare",
		makes = { "Spear", "Dagger", "Sword", "Bow", "Axe", "Pickaxe", "Armor", "Building" },
	},
	{
		id = "Adamantine",
		power = 8,
		material = "AdamantineBar",
		ore = "AdamantineOre",
		station = "Anvil",
		rarity = "Epic",
		makes = { "Spear", "Dagger", "Sword", "Bow", "Axe", "Pickaxe", "Armor", "Building" },
	},
}

-- The metal tiers in order (ores, bars, bows).
Tiers.Metals = { "Copper", "Iron", "Silver", "Cobalt", "Mithril", "Adamantine" }

-- Tool tier rank (1 = Wood … 8 = Adamantine): a node needing rank N takes a
-- pickaxe of rank N or higher.
Tiers.ToolRank = { Wood = 1, Stone = 2, Copper = 3, Iron = 4, Silver = 5, Cobalt = 6, Mithril = 7, Adamantine = 8 }

-- Base values at Stone (power 2); the curve scales them per tier.
Tiers.BASE = {
	Spear = 25,
	Sword = 18,
	Dagger = 9,
}
-- The wooden spear's confirmed damage (Q66) sits below the curve.
Tiers.WOODEN_SPEAR_DAMAGE = 15
-- Bows: the Wooden Bow's damage, then ×STEP per metal bow in ladder order.
Tiers.WOODEN_BOW_DAMAGE = 6
-- Armor above Iron's confirmed ×2.0 compounds by STEP per tier (owner decision).
Tiers.IRON_ARMOR_FACTOR = GameConstants.ARMOR_SET_FACTOR.Iron

local byId = {}
for _, tier in Tiers.Ladder do
	byId[tier.id] = tier
	local makes = {}
	for _, family in tier.makes do
		makes[family] = true
	end
	tier.canMake = makes
end

function Tiers.Get(id: string)
	return byId[id]
end

-- The multiplier for a tier relative to Stone.
function Tiers.Scale(tier): number
	return Tiers.STEP ^ (tier.power - 2)
end

-- Rounded strength of `base` (a value at Stone) for `tier`.
function Tiers.Value(base: number, tier): number
	return math.max(1, math.round(base * Tiers.Scale(tier)))
end

-- Full-set armor factor: confirmed Hide and Iron, and ×STEP per metal above Iron.
function Tiers.ArmorFactor(tier): number?
	if tier.armorFactor then
		return tier.armorFactor
	end
	if not tier.canMake.Armor then
		return nil
	end
	return Tiers.IRON_ARMOR_FACTOR * Tiers.STEP ^ (tier.power - Tiers.Get("Iron").power)
end

-- A bow's own damage: Wooden 6, then ×STEP per metal in ladder order.
function Tiers.BowDamage(tierId: string): number
	if tierId == "Wood" then
		return Tiers.WOODEN_BOW_DAMAGE
	end
	local step = table.find(Tiers.Metals, tierId)
	return math.round(Tiers.WOODEN_BOW_DAMAGE * Tiers.STEP ^ (step or 0))
end

return Tiers
