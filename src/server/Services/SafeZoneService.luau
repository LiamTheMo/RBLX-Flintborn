-- Designated PvP safe zones (GDD §3.2, §5.1, Q33, Q160a). Zones are parts tagged
-- "SafeZone" in the map; nobody deals or takes damage inside one, and nothing may
-- be built in one. Which POIs get safe zones is map content (v0.15); this provides
-- the server-enforced mechanism.

local CollectionService = game:GetService("CollectionService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local BuildRules = require(ReplicatedStorage.Shared.Building.BuildRules)

local SafeZoneService = {}

SafeZoneService.TAG = "SafeZone"

local function inside(zone: BasePart, position: Vector3): boolean
	local localPoint = zone.CFrame:PointToObjectSpace(position)
	local half = zone.Size / 2
	return math.abs(localPoint.X) <= half.X and math.abs(localPoint.Y) <= half.Y and math.abs(localPoint.Z) <= half.Z
end

-- True when a world position lies inside any tagged zone volume.
function SafeZoneService.Contains(position: Vector3): boolean
	for _, zone in CollectionService:GetTagged(SafeZoneService.TAG) do
		if zone:IsA("BasePart") and inside(zone, position) then
			return true
		end
	end
	return false
end

-- True when any part of an axis-aligned box (centre, half-size) touches a zone:
-- every corner and face of the box is tested, and so is a zone smaller than it.
function SafeZoneService.OverlapsBox(center: Vector3, half: Vector3): boolean
	local points = BuildRules.FootprintPoints(center, half)
	for _, zone in CollectionService:GetTagged(SafeZoneService.TAG) do
		if zone:IsA("BasePart") then
			if BuildRules.BoxContains(center, half, zone.Position) then
				return true
			end
			for _, point in points do
				if inside(zone, point) then
					return true
				end
			end
		end
	end
	return false
end

-- Each zone as a horizontal circle {center, radius} enclosing it (event placement).
function SafeZoneService.Circles()
	local list = {}
	for _, zone in CollectionService:GetTagged(SafeZoneService.TAG) do
		if zone:IsA("BasePart") then
			local size = zone.Size
			table.insert(list, { center = zone.Position, radius = math.sqrt(size.X * size.X + size.Z * size.Z) / 2 })
		end
	end
	return list
end

return SafeZoneService
