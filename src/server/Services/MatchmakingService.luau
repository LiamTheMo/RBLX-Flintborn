-- Public world matchmaking (GDD §3.3, §34.1, Q1–Q5). Lobbies pick a reserved world
-- with room for the whole party that no member is excluded from, or reserve a new
-- one. Worlds report their player count and exclusions to the shared registry.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local MatchmakingRules = require(ReplicatedStorage.Shared.Admission.MatchmakingRules)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local WorldRegistry = require(script.Parent.Parent.Infrastructure.WorldRegistry)
local TravelService = require(script.Parent.TravelService)

local MatchmakingService = {}

MatchmakingService.HEARTBEAT_SECONDS = 30

-- Players banned from rejoining this world (dead players, GDD Q5). Filled in v0.07.
local excluded = {}

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
	WorldRegistry.Update(privateServerId, function()
		return world
	end)
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

-- World: publishes the current player count and exclusions.
function MatchmakingService.Report()
	local id = game.PrivateServerId
	if id == "" then
		return
	end
	WorldRegistry.Update(id, function(old)
		if old == nil then
			-- Never recreate an entry without the lobby's access code.
			return nil
		end
		old.players = #Players:GetPlayers()
		old.updatedAt = os.time()
		old.excludedUserIds = table.clone(excluded)
		return old
	end)
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
		end
	end)
end

return MatchmakingService
