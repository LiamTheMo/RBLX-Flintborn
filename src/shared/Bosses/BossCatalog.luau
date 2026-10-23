-- Boss archetypes (GDD §8, Q45–47, Q147). Each has a fixed authored baseline that
-- scaling multiplies at spawn. Sources: the Guardian (own schedule), event
-- (director), ritual (player-placed offering) and structure (generated holds).
-- Attacks: Slam (melee), Bolt (slow projectile), Quake (telegraphed area).
-- Loot entries are {catalogId, min, max, chance}. Values are placeholders except
-- the Guardian baseline from §8 placeholders.

local BossCatalog = {}

BossCatalog.Sources = { Guardian = "Guardian", Event = "Event", Ritual = "Ritual", Structure = "Structure" }

BossCatalog.Bosses = {
	Guardian = {
		name = "The Guardian",
		source = "Guardian",
		health = 25000,
		damage = 30,
		speed = 10,
		reach = 12,
		size = Vector3.new(10, 18, 8),
		color = Color3.fromRGB(70, 90, 110),
		attacks = { "Slam", "Bolt", "Quake" },
		pillars = { count = 4, health = 1500 },
		legendary = "GuardianFang",
		loot = { { "Iron", 60, 90, 1 }, { "AncientEmber", 2, 3, 1 } },
	},
	IronhideBehemoth = {
		name = "Ironhide Behemoth",
		source = "Event",
		health = 4000,
		damage = 22,
		speed = 12,
		reach = 10,
		size = Vector3.new(8, 9, 12),
		color = Color3.fromRGB(96, 84, 76),
		attacks = { "Slam", "Quake" },
		loot = { { "Hide", 15, 25, 1 }, { "Iron", 20, 30, 1 }, { "AncientEmber", 1, 1, 0.5 } },
	},
	BoneColossus = {
		name = "Bone Colossus",
		source = "Event",
		health = 7000,
		damage = 26,
		speed = 9,
		reach = 11,
		size = Vector3.new(7, 16, 5),
		color = Color3.fromRGB(226, 220, 200),
		attacks = { "Slam", "Bolt", "Quake" },
		loot = { { "Iron", 40, 60, 1 }, { "AncientEmber", 1, 2, 1 } },
	},
	EmberTitan = {
		name = "Ember Titan",
		source = "Ritual",
		health = 6000,
		damage = 25,
		speed = 10,
		reach = 10,
		size = Vector3.new(7, 14, 6),
		color = Color3.fromRGB(255, 110, 40),
		attacks = { "Slam", "Bolt" },
		loot = { { "AncientEmber", 3, 5, 1 }, { "Iron", 30, 50, 1 }, { "ExtractionRune", 1, 1, 0.05 } },
	},
	RaiderWarlord = {
		name = "Raider Warlord",
		source = "Structure",
		health = 3000,
		damage = 20,
		speed = 14,
		reach = 8,
		size = Vector3.new(4, 7, 3),
		color = Color3.fromRGB(140, 30, 30),
		attacks = { "Slam", "Bolt" },
		loot = { { "Iron", 25, 40, 1 }, { "Potion", 1, 2, 0.6 } },
	},
}

-- What a ritual site asks for to summon its boss (consumed once on the server).
BossCatalog.Ritual = { boss = "EmberTitan", offering = { AncientEmber = 3, Iron = 50 }, summonSeconds = 10 }

function BossCatalog.Get(bossId: any)
	return type(bossId) == "string" and BossCatalog.Bosses[bossId] or nil
end

return BossCatalog
