-- Whether the play world's map is in place (GDD §54). The placeholder island is
-- built in the background at startup, so anything that reads the map's terrain or
-- its tagged POI parts waits for it here; the authored map is ready at once.

local WorldState = {}

WorldState.READY_ATTRIBUTE = "FlintbornWorldReady"
-- Set when the generated island's zones and heights (IslandLayout) describe the map.
WorldState.GENERATED_ATTRIBUTE = "FlintbornGeneratedIsland"

function WorldState.IsReady(): boolean
	return workspace:GetAttribute(WorldState.READY_ATTRIBUTE) == true
end

-- Yields until the map is ready.
function WorldState.WaitUntilReady()
	while workspace:GetAttribute(WorldState.READY_ATTRIBUTE) ~= true do
		workspace:GetAttributeChangedSignal(WorldState.READY_ATTRIBUTE):Wait()
	end
end

function WorldState.MarkReady()
	workspace:SetAttribute(WorldState.READY_ATTRIBUTE, true)
end

-- True when IslandLayout's zones describe this map (the island was generated).
function WorldState.IsGenerated(): boolean
	return workspace:GetAttribute(WorldState.GENERATED_ATTRIBUTE) == true
end

-- Where a creature stands at a column: always the ground, the bed under any water
-- (nothing swims, GDD §55), and whether that spot is in water. One extra ray only
-- over water.
function WorldState.Standing(origin: Vector3, depth: number, params: RaycastParams): (RaycastResult?, boolean)
	params.IgnoreWater = false
	local hit = workspace:Raycast(origin, Vector3.new(0, -depth, 0), params)
	if hit == nil or hit.Material ~= Enum.Material.Water then
		return hit, false
	end
	params.IgnoreWater = true
	local bed = workspace:Raycast(hit.Position, Vector3.new(0, -(depth - (origin.Y - hit.Position.Y)), 0), params)
	params.IgnoreWater = false
	return bed, true
end

-- How far below a character's root its feet are (R6: legs 2, half a torso 1).
WorldState.FEET_BELOW_ROOT = 3

-- True when terrain water stands at the feet of a character whose root is at
-- `rootPosition`: a short ray down from the root that stops at water.
function WorldState.FeetInWater(rootPosition: Vector3): boolean
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Include
	params.FilterDescendantsInstances = { workspace.Terrain }
	params.IgnoreWater = false
	local hit = workspace:Raycast(rootPosition, Vector3.new(0, -(WorldState.FEET_BELOW_ROOT + 1), 0), params)
	return hit ~= nil and hit.Material == Enum.Material.Water
end

return WorldState
