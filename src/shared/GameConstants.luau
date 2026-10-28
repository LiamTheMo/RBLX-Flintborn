-- Owner-confirmed Flintborn rules from GDD.md, shared by server and client.
-- Values marked "starting target" are confirmed playtest baselines, not final
-- balance. Anything the GDD still lists as Open does not belong here yet.

local GameConstants = {}

-- Survival (GDD §4.3, Q61-63) --------------------------------------------------

GameConstants.BASE_MAX_HEALTH = 100
GameConstants.SPRINT_SECONDS = 3
GameConstants.STAMINA_RECOVERY_SECONDS = 5
-- Stamina stops recovering while sprinting and for this long after (owner, GDD §47).
GameConstants.STAMINA_REGEN_DELAY_SECONDS = 3
-- A full food meter empties in 60 minutes (owner, GDD §49).
GameConstants.FOOD_DRAIN_SECONDS = 3600
-- Strictly below this fraction of food, movement is slowed. 0% adds nothing more (Q160).
GameConstants.FOOD_SLOW_THRESHOLD = 0.25
GameConstants.FOOD_SLOW_MULTIPLIER = 0.9

-- Healing (GDD §4.5, Q64-65, Q135, Q137) ----------------------------------------

-- Medicine heals immediately; the animation that follows is the only cooldown.
GameConstants.MEDICINE = {
	Basic = { heal = 10, animationSeconds = 0.5 },
	Advanced = { heal = 25, animationSeconds = 1.0 },
	Potion = { heal = 50, animationSeconds = 1.5 },
}
GameConstants.FOOD_HEAL_SECONDS = 10
GameConstants.FOOD_HIT_CUTOFF = 10
-- Accepted starter examples (Q137); the full food catalog is still Open.
GameConstants.FOOD = {
	Redberry = { hunger = 0.10, heal = 10 },
	CookedMeat = { hunger = 0.35, heal = 30 },
}

-- Combat (GDD §21.1, §21.5, Q66, Q132-133) ---------------------------------------

-- Confirmed full three-piece set factors; pieces add, they never multiply. Every
-- other armor tier is set by the tier ladder (Items/Tiers, GDD §51).
GameConstants.ARMOR_SET_FACTOR = {
	None = 1.0,
	Hide = 1.2,
	Iron = 2.0,
}
-- Starting targets (raw damage and seconds between attacks).
GameConstants.MELEE = {
	Rock = { damage = 5, cooldown = 0.3 },
	Dagger = { cooldown = 0.4 },
	Sword = { cooldown = 0.7 },
	Spear = { cooldown = 0.9 },
	WoodenSpear = { damage = 15, cooldown = 0.9 },
	StoneSpear = { damage = 25, cooldown = 0.9 },
}
GameConstants.ARROWS_PER_CRAFT = 10

-- Downed and revive (GDD §5.3, Q68, Q136, Q159) ----------------------------------

GameConstants.DOWNED_HEALTH = 20
GameConstants.BLEED_OUT_SECONDS = 60
GameConstants.REVIVE_SECONDS = 10
GameConstants.REVIVE_EHP_FRACTION = 0.10
GameConstants.MAX_TRIBE_SIZE = 8

-- Death and departure (GDD §29) --------------------------------------------------

GameConstants.CORPSE_SECONDS = 600

-- Extraction (GDD §9, Q154-158) ---------------------------------------------------

GameConstants.FIXED_EXTRACTION_SECONDS = 120
GameConstants.PORTABLE_EXTRACTION_SECONDS = 30
GameConstants.CENTER_MULTIPLIER = 2
GameConstants.PORTAL_NO_BUILD_METERS = 50
-- Roblox's standard character scale: 1 stud is 0.28 m.
GameConstants.STUDS_PER_METER = 1 / 0.28

-- Inventory and vault (GDD §10.3, Q126-129, Q151, Q154) ---------------------------

GameConstants.HOTBAR_SLOTS = 9
GameConstants.BACKPACK_SLOTS = 50
GameConstants.VAULT_START_SLOTS = 25
GameConstants.VAULT_SLOTS_PER_UPGRADE = 25
GameConstants.MATERIAL_STACK_MAX = 1000

-- Building (GDD §6.2, Q146, Q159) ---------------------------------------------------

GameConstants.TOTEM_HEALTH_BY_LEVEL = { 500, 1000, 2500 }
GameConstants.UNCLAIMED_DECAY_MIN_SECONDS = 240
GameConstants.UNCLAIMED_DECAY_MAX_SECONDS = 360

-- World (GDD §3.3, §7, Q1, Q111-112) -------------------------------------------------

GameConstants.MAX_PLAYERS_PER_WORLD = 30
GameConstants.EVENT_CHECK_SECONDS = 300
GameConstants.EVENT_CATEGORY_TRIGGER_CHANCE = 0.25
GameConstants.NODE_RESPAWN_SECONDS = 120

-- Progression (GDD §16.8, §33, §39.5, Q75, Q139, Q150) -------------------------------

GameConstants.MASTERY_TRACKS = { "Mining", "Woodcutting", "Farming", "Crafting", "PvP" }
GameConstants.MASTERY_MAX_LEVEL = 10
GameConstants.MASTERY_YIELD_PER_LEVEL = 0.01
GameConstants.CRAFT_QUALITY_ROLL = 0.05
GameConstants.BEST_ROLL_RELATIVE_PER_LEVEL = 0.05
-- Crafting mastery's chance per level of one bonus bar for each bar smelted
-- (owner decision 2026-10-28; placeholder rate, 20% at level 10).
GameConstants.SMELT_BONUS_BAR_PER_LEVEL = 0.02
GameConstants.PREMIUM_XP_BONUS = 0.25

GameConstants.RARITIES = { "Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic", "Secret", "Exclusive" }

-- Rules -------------------------------------------------------------------------

-- Combined armor factor for worn pieces: A = 1 + sum of piece increments.
function GameConstants.ArmorFactor(pieceIncrements: { number }): number
	local factor = 1
	for _, increment in pieceIncrements do
		factor += increment
	end
	return factor
end

-- Applies raw damage through effective HP (EHP = HP x A) and returns actual HP.
function GameConstants.ApplyDamage(health: number, armorFactor: number, damage: number): number
	local effective = math.max(0, health * armorFactor - damage)
	return effective / armorFactor
end

-- Actual HP after a revive: 10% of max EHP converted back through the armor factor.
function GameConstants.RevivedHealth(maxHealth: number, armorFactor: number): number
	return GameConstants.REVIVE_EHP_FRACTION * maxHealth * armorFactor / armorFactor
end

-- Remaining food healing after a damaging hit: halved, cancelled at or below the cutoff.
function GameConstants.FoodHealAfterHit(pending: number): number
	local halved = pending / 2
	if halved <= GameConstants.FOOD_HIT_CUTOFF then
		return 0
	end
	return halved
end

function GameConstants.IsFoodSlowed(foodFraction: number): boolean
	return foodFraction < GameConstants.FOOD_SLOW_THRESHOLD
end

-- Settles a material deposit into one secure stack: anything over the cap is deleted (Q154).
function GameConstants.SettleMaterialStack(current: number, incoming: number): (number, number)
	local total = current + incoming
	local stored = math.min(total, GameConstants.MATERIAL_STACK_MAX)
	return stored, total - stored
end

-- Best quality-roll chance with the relative Crafting mastery bonus (Q139).
function GameConstants.BestRollChance(baseChance: number, masteryLevel: number): number
	return math.min(1, baseChance * (1 + GameConstants.BEST_ROLL_RELATIVE_PER_LEVEL * masteryLevel))
end

function GameConstants.VaultSlots(upgrades: number): number
	return GameConstants.VAULT_START_SLOTS + GameConstants.VAULT_SLOTS_PER_UPGRADE * upgrades
end

return GameConstants
