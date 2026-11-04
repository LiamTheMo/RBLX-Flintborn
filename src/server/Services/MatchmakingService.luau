-- Public world matchmaking (GDD §3.3, §34.1, Q1–Q5). Lobbies pick a reserved world
-- with room for the whole party that no member is excluded from (the fullest such
-- world, so players meet others), or reserve a new one. Worlds report their player
-- count and exclusions to the shared registry.
--
-- A world nobody can see in the registry would never get another player, so both
-- ends guard the listing: the lobby retries its first writes (the entry and the
-- world's access code) and warns if they still fail, and a world whose entry has
-- gone lists itself again from its recorded code (WorldRegistry.GetCode).

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local MatchmakingRules = require(ReplicatedStorage.Shared.Admission.MatchmakingRules)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local WorldRegistry = require(script.Parent.Parent.Infrastructure.WorldRegistry)
local TravelService = require(script.Parent.TravelService)

local MatchmakingService = {}

MatchmakingService.HEARTBEAT_SECONDS = 30
-- Registry writes that list a new world: tries, and the wait before each retry
-- (multiplied by the attempt number).
MatchmakingService.WRITE_ATTEMPTS = 3
MatchmakingService.RETRY_SECONDS = 0.5

-- Players banned from rejoining this world (dead players, GDD Q5). Filled in v0.07.
local excluded = {}
-- World: this world's access code once read back from the registry (nil until then).
local ownCode: string? = nil
-- World: what the last report found, so each problem is logged once, not every heartbeat.
local lastProblem: string? = nil

-- Runs `write` (returning ok) until it succeeds or the tries run out. Returns ok.
local function retry(write: () -> boolean): boolean
	for attempt = 1, MatchmakingService.WRITE_ATTEMPTS do
		if write() then
			return true
		end
		if attempt < MatchmakingService.WRITE_ATTEMPTS then
			task.wait(MatchmakingService.RETRY_SECONDS * attempt)
		end
	end
	return false
end

-- Lobby: lists a just-reserved world: its access code first (so the world can
-- always list itself again), then its entry.
local function list(world)
	local id = world.privateServerId
	local codeSaved = retry(function()
		return (WorldRegistry.SaveCode(id, world.accessCode))
	end)
	local listed = retry(function()
		return (WorldRegistry.Update(id, function()
			return world
		end))
	end)
	if not listed and not codeSaved then
		warn("[MatchmakingService] Could not list world " .. id .. " or save its code: no lobby can find it")
	elseif not listed then
		warn("[MatchmakingService] Could not list world " .. id .. "; it will list itself from its saved code")
	elseif not codeSaved then
		warn("[MatchmakingService] Could not save world " .. id .. "'s code; it cannot list itself again")
	end
end

-- Lobby: a world for `userIds`. Returns (world) or (nil, reason).
function MatchmakingService.FindWorld(userIds: { number })
	local ok, worlds = WorldRegistry.List()
	if ok then
		local world = MatchmakingRules.Pick(worlds, userIds, os.time())
		if world then
			return world
		end
	else
		warn("[MatchmakingService] Registry unavailable, reserving a new world: " .. tostring(worlds))
	end
	local accessCode, privateServerId = TravelService.ReserveWorld()
	if accessCode == nil then
		return nil, privateServerId
	end
	local world = {
		privateServerId = privateServerId,
		accessCode = accessCode,
		players = 0,
		updatedAt = os.time(),
		excludedUserIds = {},
	}
	list(world)
	return world
end

-- World: whether a player may enter this world.
function MatchmakingService.IsExcluded(userId: number): boolean
	return excluded[tostring(userId)] == true
end

-- World: bars a player from this world for as long as it runs (GDD Q5).
function MatchmakingService.Exclude(userId: number)
	excluded[tostring(userId)] = true
	MatchmakingService.Report()
end

local function problem(kind: string?, message: string?)
	if kind ~= lastProblem and message then
		warn("[MatchmakingService] " .. message)
	end
	lastProblem = kind
end

-- World: publishes the current player count and exclusions, listing the world
-- again (from its recorded code) if its entry has gone.
function MatchmakingService.Report()
	local id = game.PrivateServerId
	if id == "" then
		return
	end
	if ownCode == nil then
		local ok, code = WorldRegistry.GetCode(id)
		if ok then
			ownCode = code
		end
	end
	local players, now, exclusions = #Players:GetPlayers(), os.time(), table.clone(excluded)
	local relisted = false
	local ok, result = WorldRegistry.Update(id, function(old)
		local entry, again = MatchmakingRules.Refresh(old, id, ownCode, players, now, exclusions)
		relisted = again
		return entry
	end)
	if not ok then
		problem("failed", "Could not report this world to the registry: " .. tostring(result))
	elseif result == nil then
		problem("unlisted", "This world is not listed and its code is unknown, so no lobby can send players here")
	elseif relisted then
		problem(nil, nil)
		warn("[MatchmakingService] This world's registry entry was missing; listed it again")
	else
		problem(nil, nil)
	end
end

function MatchmakingService.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	Players.PlayerAdded:Connect(MatchmakingService.Report)
	Players.PlayerRemoving:Connect(function()
		task.defer(MatchmakingService.Report)
	end)
	task.spawn(function()
		while true do
			MatchmakingService.Report()
			task.wait(MatchmakingService.HEARTBEAT_SECONDS)
		end
	end)
	game:BindToClose(function()
		if game.PrivateServerId ~= "" then
			WorldRegistry.Remove(game.PrivateServerId)
			WorldRegistry.RemoveCode(game.PrivateServerId)
		end
	end)
end

return MatchmakingService
