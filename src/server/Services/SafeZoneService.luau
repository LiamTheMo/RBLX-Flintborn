-- Designated PvP safe zones (GDD §3.2, §5.1, Q33, Q160a). Zones are parts tagged
-- "SafeZone" in the map; nobody deals or takes damage inside one. Which POIs get
-- safe zones is map content (v0.15); this provides the server-enforced mechanism.

local CollectionService = game:GetService("CollectionService")

local SafeZoneService = {}

SafeZoneService.TAG = "SafeZone"

-- True when a world position lies inside any tagged zone volume.
function SafeZoneService.Contains(position: Vector3): boolean
	for _, zone in CollectionService:GetTagged(SafeZoneService.TAG) do
		if zone:IsA("BasePart") then
			local localPoint = zone.CFrame:PointToObjectSpace(position)
			local half = zone.Size / 2
			if
				math.abs(localPoint.X) <= half.X
				and math.abs(localPoint.Y) <= half.Y
				and math.abs(localPoint.Z) <= half.Z
			then
				return true
			end
		end
	end
	return false
end

return SafeZoneService
