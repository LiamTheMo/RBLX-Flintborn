-- Server half of Shared.Progression.LevelCurve: what only the server uses. Everything in
-- ReplicatedStorage is downloaded to every player, so the shared module keeps
-- only what clients need; this one clones it and adds the rest, and server code
-- requires this module.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local SharedLevelCurve = require(ReplicatedStorage.Shared.Progression.LevelCurve)

local LevelCurve = table.clone(SharedLevelCurve)

LevelCurve.MAX_LEVEL = 50

function LevelCurve.XpForLevel(level: number): number
	return math.floor(100 * level ^ 1.5)
end

-- The fraction (0..1) of the way from `level` to the next one, for XP bars that
-- other players see (the LevelProgress attribute). Full at the cap.
function LevelCurve.Progress(level: number, xp: number): number
	if level >= LevelCurve.MAX_LEVEL then
		return 1
	end
	return math.clamp(xp / LevelCurve.XpForLevel(level), 0, 1)
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
