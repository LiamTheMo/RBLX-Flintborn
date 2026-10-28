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

-- Where a creature stands at a column: the ground, or the water's surface where it
-- is deeper than `wade` studs (it swims there). One extra ray only over water.
function WorldState.Standing(origin: Vector3, depth: number, params: RaycastParams, wade: number): RaycastResult?
	params.IgnoreWater = false
	local hit = workspace:Raycast(origin, Vector3.new(0, -depth, 0), params)
	if hit == nil or hit.Material ~= Enum.Material.Water then
		return hit
	end
	params.IgnoreWater = true
	local bed = workspace:Raycast(hit.Position, Vector3.new(0, -(depth - (origin.Y - hit.Position.Y)), 0), params)
	params.IgnoreWater = false
	if bed and hit.Position.Y - bed.Position.Y <= wade then
		return bed
	end
	return hit
end

return WorldState
