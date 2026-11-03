-- World queries for free placement (GDD §60), shared so the server (which decides)
-- and the build ghost (which previews) ask the world the same questions. The
-- verdicts themselves are BuildRules' pure functions; this module only casts the
-- rays and reads the structure parts around a spot.

local BuildRules = require(script.Parent.BuildRules)
local Characters = require(script.Parent.Parent.World.Characters)

local PlacementProbe = {}

-- The folder that holds every player-built piece (BuildingService creates it).
PlacementProbe.FOLDER_NAME = "PlayerStructures"

-- Support samples for a piece (own half-size `half`, turned `yaw`) whose base
-- sits at `base`: one downward ray from above each SupportPoints point, ignoring
-- characters (and `ignore`). Feed the result to BuildRules.SupportVerdict.
function PlacementProbe.SupportSamples(base: Vector3, half: Vector3, yaw: number, ignore: { Instance }?)
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	params.FilterDescendantsInstances = Characters.All(ignore)
	params.RespectCanCollide = true
	params.IgnoreWater = true
	local probe = BuildRules.SUPPORT_PROBE
	local down = Vector3.new(0, -(probe + BuildRules.SUPPORT_TOLERANCE + 0.05), 0)
	local samples = {}
	for _, point in BuildRules.SupportPoints(base, half, yaw) do
		local hit = workspace:Raycast(point + Vector3.new(0, probe, 0), down, params)
		if hit then
			table.insert(samples, { drop = base.Y - hit.Position.Y, normalY = hit.Normal.Y })
		else
			table.insert(samples, {})
		end
	end
	return samples
end

-- Player-built pieces with any part within `radius` of `center`, as
-- {part, position (centre), size (own), half (own), yaw}.
function PlacementProbe.NearbyPieces(center: Vector3, radius: number)
	local folder = workspace:FindFirstChild(PlacementProbe.FOLDER_NAME)
	if folder == nil then
		return {}
	end
	local params = OverlapParams.new()
	params.FilterType = Enum.RaycastFilterType.Include
	params.FilterDescendantsInstances = { folder }
	local list = {}
	for _, part in workspace:GetPartBoundsInRadius(center, radius, params) do
		if part.Parent == folder and part:GetAttribute("Piece") then
			table.insert(list, {
				part = part,
				position = part.Position,
				size = part.Size,
				half = part.Size / 2,
				yaw = part:GetAttribute("Yaw") or 0,
			})
		end
	end
	return list
end

return PlacementProbe
