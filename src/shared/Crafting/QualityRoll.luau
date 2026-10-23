-- Small quality rolls on crafted gear (GDD §16.8, Q103, Q105, Q138–139). A rolled
-- instance deviates at most ±5% from catalog stats. Only qualified world
-- workbenches roll; anywhere-crafts and lobby workbenches give default quality.
-- Crafting mastery raises the best-roll chance relatively: p × (1 + 0.05 × level).

local GameConstants = require(script.Parent.Parent.GameConstants)

local QualityRoll = {}

QualityRoll.MAX = GameConstants.CRAFT_QUALITY_ROLL
QualityRoll.BASE_BEST_CHANCE = 0.01

QualityRoll.Stations = {
	Anywhere = "Anywhere",
	WorldWorkbench = "WorldWorkbench",
	LobbyWorkbench = "LobbyWorkbench",
}

function QualityRoll.Rolls(station: string): boolean
	return station == QualityRoll.Stations.WorldWorkbench
end

-- Returns a roll in [-MAX, +MAX]. The best roll (+MAX) has its own boosted chance;
-- otherwise the roll is uniform below it. Rounded to 0.1% for display and storage.
function QualityRoll.Roll(rng, station: string, masteryLevel: number?, baseChance: number?): number
	if not QualityRoll.Rolls(station) then
		return 0
	end
	local best = GameConstants.BestRollChance(baseChance or QualityRoll.BASE_BEST_CHANCE, masteryLevel or 0)
	if rng:NextNumber() < best then
		return QualityRoll.MAX
	end
	local roll = rng:NextNumber(-QualityRoll.MAX, QualityRoll.MAX)
	return math.clamp(math.round(roll * 1000) / 1000, -QualityRoll.MAX, QualityRoll.MAX - 0.001)
end

return QualityRoll
