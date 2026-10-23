-- Server-initiated teleports between the lobby and public worlds (GDD §31.4). Retries
-- transient failures and reports teleports that fail after they started, so the
-- caller can roll back a reservation instead of losing anything.

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TeleportService = game:GetService("TeleportService")

local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Signal = require(ReplicatedStorage.Shared.Core.Signal)

local TravelService = {}

TravelService.ATTEMPTS = 3
TravelService.RETRY_SECONDS = 2

-- Fires (player, teleportResult, message) when a started teleport fails.
TravelService.TeleportFailed = Signal.new()

local function teleport(placeId: number, players: { Player }, options: TeleportOptions)
	local lastError = nil
	for attempt = 1, TravelService.ATTEMPTS do
		local ok, err = pcall(function()
			TeleportService:TeleportAsync(placeId, players, options)
		end)
		if ok then
			return true, nil
		end
		lastError = err
		if attempt < TravelService.ATTEMPTS then
			task.wait(TravelService.RETRY_SECONDS * attempt)
		end
	end
	warn("[TravelService] Teleport failed: " .. tostring(lastError))
	return false, tostring(lastError)
end

-- Reserves a new world server. Returns (accessCode, privateServerId) or nil, error.
function TravelService.ReserveWorld()
	local placeIds = PlaceConfig.PlaceIds()
	if placeIds == nil then
		return nil, "Place IDs are unavailable outside a deployed universe"
	end
	local ok, accessCode, privateServerId = pcall(function()
		return TeleportService:ReserveServer(placeIds.world)
	end)
	if not ok then
		return nil, tostring(accessCode)
	end
	return accessCode, privateServerId
end

-- Sends players to a reserved world. Only references (reservation and party IDs)
-- travel in teleport data; the destination re-checks them against the profile.
function TravelService.ToWorld(players: { Player }, accessCode: string, teleportData)
	local placeIds = PlaceConfig.PlaceIds()
	if placeIds == nil then
		return false, "Place IDs are unavailable outside a deployed universe"
	end
	local options = Instance.new("TeleportOptions")
	options.ReservedServerAccessCode = accessCode
	options:SetTeleportData(teleportData)
	return teleport(placeIds.world, players, options)
end

function TravelService.ToLobby(players: { Player })
	local placeIds = PlaceConfig.PlaceIds()
	if placeIds == nil then
		return false, "Place IDs are unavailable outside a deployed universe"
	end
	return teleport(placeIds.lobby, players, Instance.new("TeleportOptions"))
end

function TravelService.Start()
	TeleportService.TeleportInitFailed:Connect(function(player, result, message)
		warn(("[TravelService] Teleport for %s failed: %s %s"):format(player.Name, tostring(result), tostring(message)))
		TravelService.TeleportFailed:Fire(player, result, message)
	end)
end

return TravelService
