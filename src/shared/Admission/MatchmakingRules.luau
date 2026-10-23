-- Choosing a public world for a lobby party (GDD §3.3, §34.1, Q1–Q5). Worlds are
-- reserved servers the lobby tracks in a registry; this picks one with room for the
-- whole party that no member is excluded from, or reports that a new one is needed.

local GameConstants = require(script.Parent.Parent.GameConstants)

local MatchmakingRules = {}

MatchmakingRules.CAPACITY = GameConstants.MAX_PLAYERS_PER_WORLD
-- A world that has not reported for this long is treated as gone.
MatchmakingRules.STALE_SECONDS = 90

export type World = {
	privateServerId: string,
	accessCode: string,
	players: number,
	updatedAt: number,
	excludedUserIds: { [string]: boolean }?,
}

local function isExcluded(world: World, userIds: { number }): boolean
	local excluded = world.excludedUserIds
	if excluded == nil then
		return false
	end
	for _, userId in userIds do
		if excluded[tostring(userId)] then
			return true
		end
	end
	return false
end

function MatchmakingRules.IsJoinable(world: World, userIds: { number }, now: number): boolean
	return now - world.updatedAt <= MatchmakingRules.STALE_SECONDS
		and world.players + #userIds <= MatchmakingRules.CAPACITY
		and not isExcluded(world, userIds)
end

-- Prefers the fullest joinable world so players meet others; ties break by ID for
-- determinism. Returns nil when a new world must be reserved.
function MatchmakingRules.Pick(worlds: { World }, userIds: { number }, now: number): World?
	local best = nil
	for _, world in worlds do
		if MatchmakingRules.IsJoinable(world, userIds, now) then
			if
				best == nil
				or world.players > best.players
				or (world.players == best.players and world.privateServerId < best.privateServerId)
			then
				best = world
			end
		end
	end
	return best
end

return MatchmakingRules
