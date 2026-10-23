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

-- Pending maintenance receipts (items saved by a safe kick, GDD §30).
local function pendingMaintenance(profile)
	local pending = {}
	for operationId, receipt in profile.receipts.maintenance do
		if receipt.status == "Pending" then
			table.insert(pending, operationId)
		end
	end
	table.sort(pending)
	return pending
end

-- Returns items saved by earlier safe kicks, each receipt exactly once.
local function restoreMaintenance(player: Player)
	local profile = ProfileService.GetProfile(player)
	local restored = {}
	if profile == nil then
		return restored
	end
	for _, operationId in pendingMaintenance(profile) do
		local ok, items = ProfileService.RunOperation(
			player,
			"restore:" .. operationId,
			"MaintenanceRestore",
			function(working)
				local receipt = working.receipts.maintenance[operationId]
				if receipt == nil or receipt.status ~= "Pending" then
					return {}
				end
				receipt.status = "Restored"
				return receipt.items
			end
		)
		if ok and type(items) == "table" then
			for _, item in items do
				table.insert(restored, item)
			end
		end
	end
	if #restored > 0 then
		player:SetAttribute("MaintenanceNotice", nil)
	end
	return restored
end

-- Consumes this player's reservation on a confirmed spawn and returns the items
-- that enter the run: the reservation plus anything a safe kick saved earlier.
function LoadoutService.Consume(player: Player)
	local restored = restoreMaintenance(player)
	local reservationId = arrivedWith[player]
	local profile = ProfileService.GetProfile(player)
	if reservationId == nil or profile == nil or profile.transit == nil then
		return true, restored
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
	if ok then
		for _, item in restored do
			table.insert(items, item)
		end
	end
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
	if #pendingMaintenance(profile) > 0 then
		-- Tell the player their items survived a game update (GDD §30.2 #6).
		player:SetAttribute("MaintenanceNotice", true)
	end
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
