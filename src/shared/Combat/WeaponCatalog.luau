-- Melee and bow profiles (GDD §21.1, Q66, Q133–134). Confirmed: rock 5 damage,
-- wooden spear ~15, stone spear ~25, cooldowns rock 0.3 / dagger 0.4 / sword 0.7 /
-- spear 0.9 s, and bow damage from bow + arrow that never changes with draw time.
-- Reach, arcs, dagger/sword damage and arrow speeds are starting placeholders.

local GameConstants = require(script.Parent.Parent.GameConstants)

local WeaponCatalog = {}

local melee = GameConstants.MELEE

-- Used when no weapon is equipped (or a tool is): a rock/fist strike.
WeaponCatalog.Hand = { kind = "Melee", damage = melee.Rock.damage, cooldown = melee.Rock.cooldown, reach = 5, arc = 90 }

WeaponCatalog.Weapons = {
	WoodenSpear = {
		kind = "Melee",
		damage = melee.WoodenSpear.damage,
		cooldown = melee.Spear.cooldown,
		reach = 10,
		arc = 50,
	},
	StoneSpear = {
		kind = "Melee",
		damage = melee.StoneSpear.damage,
		cooldown = melee.Spear.cooldown,
		reach = 10,
		arc = 50,
	},
	StoneDagger = { kind = "Melee", damage = 9, cooldown = melee.Dagger.cooldown, reach = 5, arc = 80 },
	StoneSword = { kind = "Melee", damage = 18, cooldown = melee.Sword.cooldown, reach = 7, arc = 90 },
	IronSword = { kind = "Melee", damage = 26, cooldown = melee.Sword.cooldown, reach = 7, arc = 90 },
	BasicBow = { kind = "Bow", bowDamage = 6, cooldown = 0.3 },
}

-- Arrow damage added to the bow's own damage (both tiers count, Q134).
WeaponCatalog.Arrows = {
	Arrow = { damage = 6 },
}

WeaponCatalog.FULL_DRAW_SECONDS = 1.0
WeaponCatalog.MIN_ARROW_SPEED = 60
WeaponCatalog.MAX_ARROW_SPEED = 120
WeaponCatalog.ARROW_GRAVITY_SCALE = 0.35
WeaponCatalog.ARROW_LIFETIME = 5

-- The profile for an equipped catalog ID (Hand for tools, empty hands or unknowns).
function WeaponCatalog.For(catalogId: string?)
	return catalogId and WeaponCatalog.Weapons[catalogId] or WeaponCatalog.Hand
end

return WeaponCatalog
