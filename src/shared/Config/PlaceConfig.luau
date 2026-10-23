-- Which Flintborn place this server or client is running in (GDD Q163). The deploy
-- job generates `Shared/Generated/PlaceIds` from the ROBLOX_LOBBY_PLACE_ID and
-- ROBLOX_MAIN_PLACE_ID secrets. Studio sessions without it use the workspace
-- attribute `FlintbornPlaceRole` ("Lobby" or "World"), defaulting to "World".

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
	local generated = script.Parent.Parent:FindFirstChild("Generated")
	local module = generated and generated:FindFirstChild("PlaceIds")
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

-- Place IDs for teleports; nil outside a deployed universe.
function PlaceConfig.PlaceIds()
	return loadPlaceIds()
end

function PlaceConfig.IsLobby(): boolean
	return PlaceConfig.Role() == PlaceConfig.Lobby
end

function PlaceConfig.IsWorld(): boolean
	return PlaceConfig.Role() == PlaceConfig.World
end

return PlaceConfig
