-- Choosing a public world for a lobby party (GDD §3.3, §34.1, Q1–Q5). Worlds are
-- reserved servers the lobby tracks in a registry; this picks one with room for the
-- whole party that no member is excluded from, or reports that a new one is needed.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local GameConstants = require(ReplicatedStorage.Shared.GameConstants)

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

-- A world's next registry entry from its report: `old` (its current entry, or nil
-- when it has none) updated with its player count, the time and its exclusions.
-- With no entry it lists itself again from `accessCode` (its recorded code), or
-- stays unlisted (nil) when the code is unknown: an entry without the code would
-- send nobody anywhere. Returns (entry | nil, relisted).
function MatchmakingRules.Refresh(
	old: World?,
	privateServerId: string,
	accessCode: string?,
	players: number,
	now: number,
	excluded: { [string]: boolean }
): (World?, boolean)
	local relisted = false
	local entry = old
	if entry == nil then
		if type(accessCode) ~= "string" or accessCode == "" then
			return nil, false
		end
		entry = { privateServerId = privateServerId, accessCode = accessCode, players = 0, updatedAt = now }
		relisted = true
	end
	entry.players = players
	entry.updatedAt = now
	entry.excludedUserIds = excluded
	return entry, relisted
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
