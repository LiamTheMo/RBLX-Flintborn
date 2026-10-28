-- Melee and bow profiles (GDD §21.1, Q66, Q133–134). Confirmed: rock 5 damage,
-- wooden spear ~15, stone spear ~25, cooldowns rock 0.3 / dagger 0.4 / sword 0.7 /
-- spear 0.9 s, and bow damage from bow + arrow that never changes with draw time.
-- Every other weapon is generated from the tier ladder (GDD §51). Reach, arcs and
-- arrow speeds are starting placeholders.

local GameConstants = require(script.Parent.Parent.GameConstants)
local ItemCatalog = require(script.Parent.Parent.Items.ItemCatalog)
local Tiers = require(script.Parent.Parent.Items.Tiers)

local WeaponCatalog = {}

local melee = GameConstants.MELEE

-- Used when no weapon is equipped (or a tool is): a rock/fist strike.
WeaponCatalog.Hand = { kind = "Melee", damage = melee.Rock.damage, cooldown = melee.Rock.cooldown, reach = 5, arc = 90 }

-- Reach, arc and attack cadence per family (Q133; reach and arc are placeholders).
WeaponCatalog.FAMILIES = {
	Spear = { cooldown = melee.Spear.cooldown, reach = 10, arc = 50 },
	Sword = { cooldown = melee.Sword.cooldown, reach = 7, arc = 90 },
	Dagger = { cooldown = melee.Dagger.cooldown, reach = 5, arc = 80 },
}
WeaponCatalog.BOW_COOLDOWN = 0.3

WeaponCatalog.Weapons = {
	-- One tier above an Adamantine sword (owner decision, GDD §51).
	GuardianFang = {
		kind = "Melee",
		damage = math.round(Tiers.Value(Tiers.BASE.Sword, Tiers.Get("Adamantine")) * Tiers.STEP),
		cooldown = melee.Sword.cooldown,
		reach = 8,
		arc = 100,
	},
}

-- Every crafted weapon from the tier ladder: damage follows the ×1.25 curve from
-- the confirmed stone spear (25); the wooden spear keeps its confirmed 15.
for _, tier in Tiers.Ladder do
	for family, profile in WeaponCatalog.FAMILIES do
		if tier.canMake[family] then
			local damage = if tier.id == "Wood" and family == "Spear"
				then melee.WoodenSpear.damage
				else Tiers.Value(Tiers.BASE[family], tier)
			WeaponCatalog.Weapons[ItemCatalog.GearId(tier.id, family)] = {
				kind = "Melee",
				damage = damage,
				cooldown = profile.cooldown,
				reach = profile.reach,
				arc = profile.arc,
			}
		end
	end
	if tier.canMake.Bow then
		WeaponCatalog.Weapons[ItemCatalog.GearId(tier.id, "Bow")] = {
			kind = "Bow",
			bowDamage = Tiers.BowDamage(tier.id),
			cooldown = WeaponCatalog.BOW_COOLDOWN,
		}
	end
end

-- Arrow damage added to the bow's own damage (both count, Q134). Flint is the
-- only arrow tip (GDD §51).
WeaponCatalog.Arrows = {
	FlintArrow = { damage = 6 },
}
WeaponCatalog.ARROW = "FlintArrow"

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
