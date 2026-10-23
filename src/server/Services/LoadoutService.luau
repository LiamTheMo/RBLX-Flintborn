-- Moves a player's unvaulted items in and out of transit (GDD §31.4, Q155). Deploy
-- reserves every lobby backpack item; successful Play consumes the reservation once;
-- any failure, menu exit or stale reservation rolls it back. Nothing is ever lost
-- before a confirmed spawn.

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local TransitRules = require(ReplicatedStorage.Shared.Admission.TransitRules)
local ProfileService = require(script.Parent.ProfileService)
local TravelService = require(script.Parent.TravelService)

local LoadoutService = {}

-- Reservation ID each world player arrived with, from teleport data.
local arrivedWith = {}

-- Reserves every unvaulted item and saves before the player travels.
-- Returns (reservationId) or (nil, reason).
function LoadoutService.Reserve(player: Player)
	local reservationId = HttpService:GenerateGUID(false)
	local ok, result = ProfileService.RunOperation(
		player,
		"transit:" .. reservationId,
		"TransitReserve",
		function(profile)
			return TransitRules.Reserve(profile, reservationId, os.time())
		end
	)
	if not ok then
		return nil, tostring(result)
	end
	local saved, reason = ProfileService.SaveNow(player)
	if not saved then
		LoadoutService.Rollback(player)
		return nil, "Could not save before travelling: " .. tostring(reason)
	end
	return reservationId
end

-- Returns reserved items to the lobby backpack. Safe to call when nothing is reserved.
function LoadoutService.Rollback(player: Player)
	local profile = ProfileService.GetProfile(player)
	if profile == nil or profile.transit == nil then
		return true
	end
	local id = "rollback:" .. profile.transit.reservationId
	local ok = ProfileService.RunOperation(player, id, "TransitRollback", TransitRules.Rollback)
	return ok
end

-- Consumes this player's reservation on a confirmed spawn and returns the items
-- that enter the run (an empty list when they arrived without one).
function LoadoutService.Consume(player: Player)
	local reservationId = arrivedWith[player]
	local profile = ProfileService.GetProfile(player)
	if reservationId == nil or profile == nil or profile.transit == nil then
		return true, {}
	end
	local ok, items = ProfileService.RunOperation(
		player,
		"consume:" .. reservationId,
		"TransitConsume",
		function(working)
			return TransitRules.Consume(working, reservationId)
		end
	)
	arrivedWith[player] = nil
	return ok, items
end

-- Items that will enter the run on the next Deploy (lobby preview).
function LoadoutService.Preview(player: Player)
	local profile = ProfileService.GetProfile(player)
	return profile and profile.lobbyBackpack.slots or {}
end

local function reservationFromTeleport(player: Player)
	local joinData = player:GetJoinData()
	local data = joinData and joinData.TeleportData
	local reservations = type(data) == "table" and data.reservations
	local id = type(reservations) == "table" and reservations[tostring(player.UserId)]
	return type(id) == "string" and id or nil
end

-- A reservation is only valid in the world it was made for. Anything else (the
-- lobby after a teleport that never landed, or a mismatched ID) is rolled back.
local function reconcile(player: Player, profile)
	if profile.transit == nil then
		return
	end
	if PlaceConfig.IsWorld() then
		local claimed = reservationFromTeleport(player)
		if claimed ~= nil and claimed == profile.transit.reservationId then
			arrivedWith[player] = claimed
			return
		end
	end
	LoadoutService.Rollback(player)
end

function LoadoutService.Start()
	ProfileService.ProfileLoaded:Connect(reconcile)
	TravelService.TeleportFailed:Connect(function(player)
		if PlaceConfig.IsLobby() then
			LoadoutService.Rollback(player)
		end
	end)
	Players.PlayerRemoving:Connect(function(player)
		arrivedWith[player] = nil
	end)
end

return LoadoutService
