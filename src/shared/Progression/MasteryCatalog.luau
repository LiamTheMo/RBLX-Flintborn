-- The five mastery tracks (GDD §33.2, Q71–80, Q139). Mastery XP comes only from
-- server-verified actions (one action = 1 mastery XP; the Center bonus can add
-- more XP but never action counts). Each track caps at level 10 with a buff at
-- every level and cosmetic/title milestones. Buffs are {stat, op, value}.

local GameConstants = require(script.Parent.Parent.GameConstants)

local MasteryCatalog = {}

MasteryCatalog.TRACKS = GameConstants.MASTERY_TRACKS
MasteryCatalog.MAX_LEVEL = GameConstants.MASTERY_MAX_LEVEL

-- Cumulative mastery XP needed for each level (placeholder thresholds).
MasteryCatalog.THRESHOLDS = { 25, 75, 150, 300, 500, 800, 1200, 1700, 2300, 3000 }

-- PvP combat perks are bounded for fairness (+5% damage at most, Q76).
MasteryCatalog.PVP_DAMAGE_CAP = 0.05

-- Titles and cosmetics shown in the lobby (Q79–80).
MasteryCatalog.MILESTONES = {
	Mining = { [5] = "Stonebreaker", [10] = "Master Miner" },
	Woodcutting = { [5] = "Timberhand", [10] = "Master Woodcutter" },
	Farming = { [5] = "Green Thumb", [10] = "Master Farmer" },
	Crafting = { [5] = "Artisan", [10] = "Master Crafter" },
	PvP = { [5] = "Duelist", [10] = "Warlord" },
}

local YIELD = GameConstants.MASTERY_YIELD_PER_LEVEL

-- Every buff a track gives at `level` (cumulative).
function MasteryCatalog.Buffs(track: string, level: number)
	local buffs = {}
	if level <= 0 then
		return buffs
	end
	if track == "Mining" or track == "Woodcutting" or track == "Farming" then
		-- +1% yield per level, +10% at level 10 (Q75).
		table.insert(buffs, { stat = track .. "Yield", op = "Additive", value = YIELD * level })
	elseif track == "Crafting" then
		-- All four benefit types (Q77) plus the best-roll bonus (Q139).
		table.insert(buffs, { stat = "BestRollLevel", op = "Additive", value = level })
		table.insert(buffs, { stat = "IngredientSave", op = "Additive", value = 0.02 * level })
		table.insert(buffs, { stat = "CraftOutput", op = "Additive", value = 0.1 * (level // 3) })
		table.insert(buffs, { stat = "CraftSpeed", op = "Additive", value = 0.03 * level })
		table.insert(buffs, { stat = "RecipeTier", op = "Additive", value = level })
	elseif track == "PvP" then
		table.insert(buffs, {
			stat = "PvpDamage",
			op = "Additive",
			value = math.min(MasteryCatalog.PVP_DAMAGE_CAP, 0.005 * level),
		})
		table.insert(buffs, { stat = "SprintEfficiency", op = "Additive", value = 0.02 * level })
	end
	return buffs
end

-- Level reached with `xp` total mastery XP.
function MasteryCatalog.LevelFor(xp: number): number
	local level = 0
	for index, threshold in MasteryCatalog.THRESHOLDS do
		if xp >= threshold then
			level = index
		end
	end
	return level
end

return MasteryCatalog
