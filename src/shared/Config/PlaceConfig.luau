-- Which Flintborn place this server or client is running in (GDD Q163), by its
-- place ID in `Config/PlaceIds`. A place with another ID (an unpublished Studio
-- file, a test copy) uses the workspace attribute `FlintbornPlaceRole` ("Lobby"
-- or "World"), and Studio defaults to "World".

local RunService = game:GetService("RunService")

local PlaceConfig = {}

PlaceConfig.Lobby = "Lobby"
PlaceConfig.World = "World"
PlaceConfig.Unknown = "Unknown"

-- Pure resolution, so specs can check every case.
function PlaceConfig.Resolve(placeIds, placeId: number, attribute: any, isStudio: boolean): string
	if placeIds then
		if placeId == placeIds.lobby then
			return PlaceConfig.Lobby
		elseif placeId == placeIds.world then
			return PlaceConfig.World
		end
	end
	if attribute == PlaceConfig.Lobby or attribute == PlaceConfig.World then
		return attribute
	end
	if isStudio then
		return PlaceConfig.World
	end
	return PlaceConfig.Unknown
end

local function loadPlaceIds()
	local module = script.Parent:FindFirstChild("PlaceIds")
	return module and require(module) or nil
end

local cachedRole = nil

function PlaceConfig.Role(): string
	if cachedRole == nil then
		cachedRole = PlaceConfig.Resolve(
			loadPlaceIds(),
			game.PlaceId,
			workspace:GetAttribute("FlintbornPlaceRole"),
			RunService:IsStudio()
		)
	end
	return cachedRole
end

-- Place IDs for teleports; nil in Studio, where TeleportService cannot travel.
function PlaceConfig.PlaceIds()
	if RunService:IsStudio() then
		return nil
	end
	return loadPlaceIds()
end

function PlaceConfig.IsLobby(): boolean
	return PlaceConfig.Role() == PlaceConfig.Lobby
end

function PlaceConfig.IsWorld(): boolean
	return PlaceConfig.Role() == PlaceConfig.World
end

return PlaceConfig
