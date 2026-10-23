-- Enemy archetypes (GDD §7.3, Q44). Themes cover primitive animals, ancient
-- creatures, skeletons, elementals, evil NPCs and mythological beings; elemental
-- enemies never give players magic. Elites (alphas) have more health and hit
-- harder. Drops are {catalogId, min, max, chance}. Stats are placeholders.

local EnemyCatalog = {}

EnemyCatalog.Themes = { "Primitive", "Ancient", "Skeletal", "Elemental", "EvilNpc", "Mythological" }

EnemyCatalog.ELITE = { health = 3, damage = 1.5, size = 1.4 }

EnemyCatalog.Enemies = {
	Wolf = {
		name = "Wolf",
		theme = "Primitive",
		health = 60,
		damage = 8,
		speed = 18,
		reach = 5,
		cooldown = 1.2,
		size = Vector3.new(2, 2.5, 4),
		color = Color3.fromRGB(110, 110, 115),
		drops = { { "Hide", 1, 2, 1 } },
	},
	Boar = {
		name = "Boar",
		theme = "Primitive",
		health = 90,
		damage = 10,
		speed = 14,
		reach = 5,
		cooldown = 1.4,
		size = Vector3.new(2.5, 2.5, 4),
		color = Color3.fromRGB(105, 76, 52),
		drops = { { "Hide", 2, 3, 1 }, { "Berries", 1, 3, 0.4 } },
	},
	Sabertooth = {
		name = "Sabertooth",
		theme = "Ancient",
		health = 160,
		damage = 16,
		speed = 17,
		reach = 6,
		cooldown = 1.3,
		size = Vector3.new(3, 3.5, 6),
		color = Color3.fromRGB(196, 150, 88),
		drops = { { "Hide", 4, 6, 1 } },
	},
	Skeleton = {
		name = "Skeleton Warrior",
		theme = "Skeletal",
		health = 80,
		damage = 10,
		speed = 12,
		reach = 6,
		cooldown = 1.3,
		size = Vector3.new(2, 5, 1.5),
		color = Color3.fromRGB(226, 220, 200),
		drops = { { "Stone", 3, 6, 1 }, { "Iron", 1, 3, 0.5 } },
	},
	EmberWisp = {
		name = "Ember Wisp",
		theme = "Elemental",
		health = 70,
		damage = 9,
		speed = 16,
		reach = 6,
		cooldown = 1.1,
		size = Vector3.new(2, 2, 2),
		color = Color3.fromRGB(255, 120, 40),
		drops = { { "AncientEmber", 1, 1, 0.05 } },
	},
	Bandit = {
		name = "Raider",
		theme = "EvilNpc",
		health = 110,
		damage = 12,
		speed = 15,
		reach = 6,
		cooldown = 1.2,
		size = Vector3.new(2, 5, 1.5),
		color = Color3.fromRGB(120, 40, 40),
		drops = { { "Iron", 2, 5, 1 }, { "Fiber", 3, 6, 0.6 } },
	},
	Minotaur = {
		name = "Minotaur",
		theme = "Mythological",
		health = 600,
		damage = 24,
		speed = 13,
		reach = 8,
		cooldown = 1.8,
		size = Vector3.new(4, 8, 3),
		color = Color3.fromRGB(90, 60, 40),
		drops = { { "Iron", 15, 25, 1 }, { "AncientEmber", 1, 1, 1 } },
	},
}

-- Enemies notice players within AGGRO and give up past LEASH from home.
EnemyCatalog.AGGRO = 45
EnemyCatalog.LEASH = 90

function EnemyCatalog.Get(enemyId: any)
	return type(enemyId) == "string" and EnemyCatalog.Enemies[enemyId] or nil
end

return EnemyCatalog
