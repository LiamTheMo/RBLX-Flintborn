-- Boss scaling from the active population (GDD §8.2, Q148). Each active player
-- contributes 50% normalised account level + 50% normalised gear score; the sum
-- sets a multiplier on the authored baseline, clamped to 0.75×–2.0×. The snapshot
-- is taken once at spawn, so later gear removal or low-level alt joins change
-- nothing.

local ItemCatalog = require(script.Parent.Parent.Items.ItemCatalog)
local Rarity = require(script.Parent.Parent.Items.Rarity)

local BossScaling = {}

BossScaling.MIN = 0.75
BossScaling.MAX = 2.0
BossScaling.PER_SCORE = 0.25
BossScaling.MAX_LEVEL = 50

local ARMOR_TIERS = { Hide = 1, Wood = 2, Stone = 3, Iron = 4 }

-- 0..1 from the best carried weapon's rarity and worn/carried armor tiers.
function BossScaling.GearScore(items): number
	local bestWeapon, armor = 0, {}
	for _, item in items do
		local def = ItemCatalog.Get(item.catalogId)
		if def and def.weapon then
			bestWeapon = math.max(bestWeapon, Rarity.Index(def.rarity) or 1)
		elseif def and def.armor then
			local tier = ARMOR_TIERS[def.armor.tier] or 0
			armor[def.armor.slot] = math.max(armor[def.armor.slot] or 0, tier)
		end
	end
	local armorTotal = (armor.Head or 0) + (armor.Chest or 0) + (armor.Legs or 0)
	return math.clamp(0.5 * math.min(bestWeapon / 5, 1) + 0.5 * armorTotal / 12, 0, 1)
end

-- One player's 0..1 contribution.
function BossScaling.PlayerScore(level: number, gearScore: number): number
	local levelPart = math.clamp((level - 1) / (BossScaling.MAX_LEVEL - 1), 0, 1)
	return 0.5 * levelPart + 0.5 * math.clamp(gearScore, 0, 1)
end

-- The multiplier for a snapshot list of {level, gearScore}.
function BossScaling.Multiplier(snapshot): number
	local combined = 0
	for _, entry in snapshot do
		combined += BossScaling.PlayerScore(entry.level, entry.gearScore)
	end
	return math.clamp(BossScaling.MIN + BossScaling.PER_SCORE * combined, BossScaling.MIN, BossScaling.MAX)
end

-- Freezes a multiplier at spawn time: a copy that later changes cannot touch.
function BossScaling.Snapshot(players)
	local frozen = {}
	for _, entry in players do
		table.insert(frozen, { level = entry.level, gearScore = entry.gearScore })
	end
	return { players = frozen, multiplier = BossScaling.Multiplier(frozen) }
end

return BossScaling
