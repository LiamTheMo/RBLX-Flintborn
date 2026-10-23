-- General XP levels (GDD §33.1, Q52, Q70). xpForLevel(n) = 100 × n^1.5 is the XP
-- needed to go from level n to n + 1; the level caps at 50 before rebirth.

local LevelCurve = {}

LevelCurve.MAX_LEVEL = 50

function LevelCurve.XpForLevel(level: number): number
	return math.floor(100 * level ^ 1.5)
end

-- Adds XP and returns (level, xp, levelsGained). XP past the cap is kept as a
-- total but no further levels are gained until rebirth.
function LevelCurve.Add(level: number, xp: number, amount: number)
	local gained = 0
	xp += math.max(0, amount)
	while level < LevelCurve.MAX_LEVEL and xp >= LevelCurve.XpForLevel(level) do
		xp -= LevelCurve.XpForLevel(level)
		level += 1
		gained += 1
	end
	return level, xp, gained
end

return LevelCurve
