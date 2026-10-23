-- Random spawn selection (GDD §3.1, Q33, Q160): anywhere valid on the map, never
-- within the minimum distance of a living player. There is no spawn protection, so
-- distance is the only safeguard.

local SpawnRules = {}

SpawnRules.MIN_PLAYER_DISTANCE = 150
SpawnRules.MAX_ATTEMPTS = 20

local function distance(a, b): number
	local dx, dy, dz = a.X - b.X, a.Y - b.Y, a.Z - b.Z
	return math.sqrt(dx * dx + dy * dy + dz * dz)
end

local function nearest(candidate, players): number
	local best = math.huge
	for _, position in players do
		best = math.min(best, distance(candidate, position))
	end
	return best
end

-- Picks a candidate position. `candidates` is a list of positions (anything with
-- X/Y/Z), `players` the positions of living players, `rng` a Random. Tries random
-- candidates first; if none is far enough, falls back to the candidate farthest
-- from every player. Returns (position, isFallback) or nil when there are none.
function SpawnRules.Choose(candidates, players, rng, minDistance: number?, attempts: number?)
	if #candidates == 0 then
		return nil, false
	end
	local required = minDistance or SpawnRules.MIN_PLAYER_DISTANCE
	for _ = 1, attempts or SpawnRules.MAX_ATTEMPTS do
		local candidate = candidates[rng:NextInteger(1, #candidates)]
		if nearest(candidate, players) >= required then
			return candidate, false
		end
	end
	local best, bestDistance = candidates[1], -1
	for _, candidate in candidates do
		local d = nearest(candidate, players)
		if d > bestDistance then
			best, bestDistance = candidate, d
		end
	end
	return best, bestDistance < required
end

return SpawnRules
