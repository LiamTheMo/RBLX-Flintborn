-- Creature roster (GDD §7.3, Q44, §54 owner decisions 2026-10-28). Wildlife is
-- Primitive or Ancient; Skeletons and Ember Wisps keep their homes (Fallen Temple
-- and Shattered Keep, Emberhollow Caves). Elemental enemies never give players
-- magic. Bandits are gone (§54).
--
-- behaviour: Passive creatures always flee and never deal damage; Neutral ones
-- ignore players until they or their group are hurt, then fight back for a while;
-- Hostile ones attack on sight (AggroRules). role says how a creature appears:
-- Regular ones roam (WildlifeRules), the rest come from creature events
-- (EventCatalog). The bosses live in BossCatalog: the Crater Gorilla (event boss)
-- and the Minotaur (the Keep's ritual boss).
--
-- Drops are {catalogId, min, max, chance} and follow size (§54): small passives
-- give Raw Meat and a little Hide; medium animals Meat, Hide and Bone; large ones
-- plenty of each. Elites (`elite = true`, or an event's alpha member) also drop
-- ELITE_DROPS. Ore only where §54 says: Skeletons Copper and Iron (Keep Skeletons
-- Silver too) and the Stonehide Rhino a little Iron; no other animal ever drops
-- ore. Stats are placeholders.

local EnemyCatalog = {}

EnemyCatalog.Themes = { "Primitive", "Ancient", "Skeletal", "Elemental" }

EnemyCatalog.Behaviours = { Passive = "Passive", Neutral = "Neutral", Hostile = "Hostile" }
EnemyCatalog.Roles = {
	Regular = "Regular",
	RareEvent = "RareEvent",
	EventWildlife = "EventWildlife",
	EventElite = "EventElite",
	EventAlpha = "EventAlpha",
}
-- Size classes for animals; they set the drop table's scale.
EnemyCatalog.SizeClasses = { Small = "Small", Medium = "Medium", Large = "Large" }

-- An event's alpha member (group `elite = true`): stronger and larger than its kind.
EnemyCatalog.ELITE = { health = 3, damage = 1.5, size = 1.4 }
-- What an elite drops on top of its kind's drops (GDD §18.1, §51, §54; placeholders).
EnemyCatalog.ELITE_DROPS = {
	{ "DireHide", 1, 2, 0.8 },
	{ "ChargedCore", 1, 1, 0.35 },
	{ "GlowFur", 1, 1, 0.35 },
}

local function small(meat: number)
	return { { "RawMeat", 1, meat, 1 }, { "Hide", 1, 1, 0.5 } }
end

local function medium(meat: number, hide: number, bone: number)
	return { { "RawMeat", 2, meat, 1 }, { "Hide", 1, hide, 1 }, { "Bone", 1, bone, 1 } }
end

local function large(meat: number, hide: number, bone: number)
	return {
		{ "RawMeat", meat - 3, meat, 1 },
		{ "Hide", hide - 3, hide, 1 },
		{ "Bone", bone - 2, bone, 1 },
	}
end

EnemyCatalog.Enemies = {
	-- Regular roaming wildlife.
	WildBoar = {
		name = "Wild Boar",
		theme = "Primitive",
		behaviour = "Neutral",
		role = "Regular",
		sizeClass = "Medium",
		health = 90,
		damage = 10,
		speed = 14,
		reach = 5,
		cooldown = 1.4,
		size = Vector3.new(2.5, 2.5, 4),
		color = Color3.fromRGB(105, 76, 52),
		drops = {
			{ "RawMeat", 2, 3, 1 },
			{ "Hide", 1, 3, 1 },
			{ "Bone", 1, 2, 1 },
			{ "Redberry", 1, 3, 0.4 },
		},
	},
	ForestStag = {
		name = "Forest Stag",
		theme = "Primitive",
		behaviour = "Passive",
		role = "Regular",
		sizeClass = "Medium",
		health = 70,
		damage = 0,
		speed = 22,
		reach = 4,
		cooldown = 1.5,
		size = Vector3.new(2, 4, 4.5),
		color = Color3.fromRGB(150, 100, 60),
		drops = medium(3, 2, 2),
	},
	GreyWolf = {
		name = "Grey Wolf",
		theme = "Primitive",
		behaviour = "Hostile",
		role = "Regular",
		sizeClass = "Medium",
		health = 60,
		damage = 8,
		speed = 18,
		reach = 5,
		cooldown = 1.2,
		size = Vector3.new(2, 2.5, 4),
		color = Color3.fromRGB(110, 110, 115),
		drops = medium(2, 2, 2),
	},
	BrownBear = {
		name = "Brown Bear",
		theme = "Primitive",
		behaviour = "Neutral",
		role = "Regular",
		sizeClass = "Large",
		health = 240,
		damage = 18,
		speed = 15,
		reach = 6,
		cooldown = 1.6,
		size = Vector3.new(3.5, 4.5, 6),
		color = Color3.fromRGB(92, 64, 42),
		drops = large(8, 6, 5),
	},
	RiverCrocodile = {
		name = "River Crocodile",
		theme = "Primitive",
		behaviour = "Hostile",
		role = "Regular",
		sizeClass = "Medium",
		health = 110,
		damage = 14,
		speed = 11,
		reach = 5,
		cooldown = 1.6,
		size = Vector3.new(2.5, 1.6, 7),
		color = Color3.fromRGB(74, 92, 58),
		drops = medium(3, 3, 2),
	},
	PlainsBison = {
		name = "Plains Bison",
		theme = "Primitive",
		behaviour = "Neutral",
		role = "Regular",
		sizeClass = "Large",
		health = 220,
		damage = 16,
		speed = 15,
		reach = 6,
		cooldown = 1.8,
		size = Vector3.new(3.5, 4.5, 6.5),
		color = Color3.fromRGB(78, 58, 40),
		drops = large(8, 6, 5),
	},
	MeadowRabbit = {
		name = "Meadow Rabbit",
		theme = "Primitive",
		behaviour = "Passive",
		role = "Regular",
		sizeClass = "Small",
		health = 20,
		damage = 0,
		speed = 20,
		reach = 3,
		cooldown = 1.5,
		size = Vector3.new(1, 1, 1.6),
		color = Color3.fromRGB(176, 150, 120),
		drops = small(1),
	},
	IslandDodo = {
		name = "Island Dodo",
		theme = "Primitive",
		behaviour = "Passive",
		role = "Regular",
		sizeClass = "Small",
		health = 30,
		damage = 0,
		speed = 12,
		reach = 3,
		cooldown = 1.5,
		size = Vector3.new(1.6, 2.4, 2),
		color = Color3.fromRGB(128, 120, 140),
		drops = small(2),
	},
	RiverCapybara = {
		name = "River Capybara",
		theme = "Primitive",
		behaviour = "Passive",
		role = "Regular",
		sizeClass = "Small",
		health = 35,
		damage = 0,
		speed = 14,
		reach = 3,
		cooldown = 1.5,
		size = Vector3.new(1.8, 1.8, 3),
		color = Color3.fromRGB(140, 98, 62),
		drops = small(2),
	},
	HighlandGoat = {
		name = "Highland Goat",
		theme = "Primitive",
		behaviour = "Passive",
		role = "Regular",
		sizeClass = "Medium",
		health = 60,
		damage = 0,
		speed = 18,
		reach = 4,
		cooldown = 1.5,
		size = Vector3.new(1.8, 2.6, 3),
		color = Color3.fromRGB(225, 220, 205),
		drops = medium(3, 2, 2),
	},
	ForestTapir = {
		name = "Forest Tapir",
		theme = "Primitive",
		behaviour = "Passive",
		role = "Regular",
		sizeClass = "Medium",
		health = 90,
		damage = 0,
		speed = 13,
		reach = 4,
		cooldown = 1.5,
		size = Vector3.new(2.2, 2.6, 4.5),
		color = Color3.fromRGB(60, 55, 60),
		drops = medium(3, 2, 2),
	},
	-- Creature events (EventCatalog).
	GiantGroundSloth = {
		name = "Giant Ground Sloth",
		theme = "Ancient",
		behaviour = "Passive",
		role = "RareEvent",
		sizeClass = "Large",
		health = 600,
		damage = 0,
		speed = 8,
		reach = 6,
		cooldown = 2,
		size = Vector3.new(5, 7, 7),
		color = Color3.fromRGB(122, 104, 82),
		drops = large(14, 12, 10),
	},
	SaberToothedTiger = {
		name = "Saber-Toothed Tiger",
		theme = "Ancient",
		behaviour = "Hostile",
		role = "EventElite",
		sizeClass = "Large",
		elite = true,
		health = 450,
		damage = 22,
		speed = 19,
		reach = 6,
		cooldown = 1.3,
		size = Vector3.new(3.6, 4.2, 7.4),
		color = Color3.fromRGB(196, 150, 88),
		drops = large(8, 8, 5),
	},
	WoollyMammoth = {
		name = "Woolly Mammoth",
		theme = "Ancient",
		behaviour = "Neutral",
		role = "EventWildlife",
		sizeClass = "Large",
		health = 900,
		damage = 28,
		speed = 12,
		reach = 9,
		cooldown = 2.2,
		size = Vector3.new(7, 9, 11),
		color = Color3.fromRGB(120, 84, 54),
		drops = large(18, 14, 12),
	},
	IronTuskBoar = {
		name = "Iron-Tusk Boar",
		theme = "Primitive",
		behaviour = "Hostile",
		role = "EventAlpha",
		sizeClass = "Large",
		elite = true,
		health = 300,
		damage = 16,
		speed = 15,
		reach = 6,
		cooldown = 1.4,
		size = Vector3.new(3.5, 3.5, 5.6),
		color = Color3.fromRGB(70, 60, 56),
		drops = large(6, 6, 5),
	},
	AncientTortoise = {
		name = "Ancient Tortoise",
		theme = "Ancient",
		behaviour = "Passive",
		role = "RareEvent",
		sizeClass = "Large",
		health = 800,
		damage = 0,
		speed = 4,
		reach = 6,
		cooldown = 2,
		size = Vector3.new(6, 4, 7),
		color = Color3.fromRGB(96, 110, 82),
		drops = large(12, 10, 12),
	},
	StonehideRhino = {
		name = "Stonehide Rhino",
		theme = "Ancient",
		behaviour = "Neutral",
		role = "EventElite",
		sizeClass = "Large",
		elite = true,
		health = 700,
		damage = 26,
		speed = 16,
		reach = 7,
		cooldown = 2,
		size = Vector3.new(4, 5, 8),
		color = Color3.fromRGB(130, 128, 122),
		drops = {
			{ "RawMeat", 9, 12, 1 },
			{ "Hide", 9, 12, 1 },
			{ "Bone", 6, 8, 1 },
			{ "IronOre", 2, 4, 0.6 },
		},
	},
	-- Earlier creatures that keep their homes (§54).
	Skeleton = {
		name = "Skeleton Warrior",
		theme = "Skeletal",
		behaviour = "Hostile",
		role = "Regular",
		health = 80,
		damage = 10,
		speed = 12,
		reach = 6,
		cooldown = 1.3,
		size = Vector3.new(2, 5, 1.5),
		color = Color3.fromRGB(226, 220, 200),
		drops = {
			{ "Stone", 3, 6, 1 },
			{ "Bone", 1, 3, 0.6 },
			{ "CopperOre", 1, 3, 0.5 },
			{ "IronOre", 1, 2, 0.35 },
		},
	},
	-- The Shattered Keep's guards carry some of its silver too.
	KeepSkeleton = {
		name = "Keep Skeleton",
		theme = "Skeletal",
		behaviour = "Hostile",
		role = "Regular",
		health = 110,
		damage = 13,
		speed = 12,
		reach = 6,
		cooldown = 1.3,
		size = Vector3.new(2.2, 5.5, 1.6),
		color = Color3.fromRGB(200, 196, 180),
		drops = {
			{ "Stone", 3, 6, 1 },
			{ "Bone", 1, 3, 0.6 },
			{ "CopperOre", 1, 3, 0.5 },
			{ "IronOre", 1, 3, 0.45 },
			{ "SilverOre", 1, 2, 0.3 },
		},
	},
	EmberWisp = {
		name = "Ember Wisp",
		theme = "Elemental",
		behaviour = "Hostile",
		role = "Regular",
		health = 70,
		damage = 9,
		speed = 16,
		reach = 6,
		cooldown = 1.1,
		size = Vector3.new(2, 2, 2),
		color = Color3.fromRGB(255, 120, 40),
		drops = { { "AncientEmber", 1, 1, 0.05 } },
	},
}

-- Enemies notice players within AGGRO and give up past LEASH from home.
EnemyCatalog.AGGRO = 45
EnemyCatalog.LEASH = 90

function EnemyCatalog.Get(enemyId: any)
	return type(enemyId) == "string" and EnemyCatalog.Enemies[enemyId] or nil
end

return EnemyCatalog
