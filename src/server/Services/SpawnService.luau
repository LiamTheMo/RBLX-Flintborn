-- Random spawn points anywhere valid on the map, away from living players
-- (GDD §3.1, Q160). Uses parts tagged "SpawnCandidate" when the map provides them;
-- otherwise samples ground points by raycasting across the map area.

local CollectionService = game:GetService("CollectionService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local SpawnRules = require(ReplicatedStorage.Shared.Admission.SpawnRules)
local WorldState = require(ReplicatedStorage.Shared.World.WorldState)

local SpawnService = {}

SpawnService.TAG = "SpawnCandidate"
SpawnService.SAMPLED_CANDIDATES = 48
-- Map radius (studs) around the origin used when sampling; override with the
-- workspace attribute FlintbornMapRadius.
SpawnService.DEFAULT_MAP_RADIUS = 1000
SpawnService.SPAWN_HEIGHT_OFFSET = 4

local rng = Random.new()

local function sampleGround(): { Vector3 }
	local radius = workspace:GetAttribute("FlintbornMapRadius") or SpawnService.DEFAULT_MAP_RADIUS
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	params.FilterDescendantsInstances = {}
	local points = {}
	for _ = 1, SpawnService.SAMPLED_CANDIDATES * 3 do
		if #points >= SpawnService.SAMPLED_CANDIDATES then
			break
		end
		local angle = rng:NextNumber(0, math.pi * 2)
		local distance = radius * math.sqrt(rng:NextNumber())
		local origin = Vector3.new(math.cos(angle) * distance, 1000, math.sin(angle) * distance)
		local hit = workspace:Raycast(origin, Vector3.new(0, -2000, 0), params)
		-- Skip water and deep drops: only solid ground above sea level.
		if hit and hit.Material ~= Enum.Material.Water and hit.Position.Y > -50 then
			table.insert(points, hit.Position)
		end
	end
	return points
end

local function candidates(): { Vector3 }
	local tagged = {}
	for _, part in CollectionService:GetTagged(SpawnService.TAG) do
		if part:IsA("BasePart") then
			table.insert(tagged, part.Position)
		end
	end
	if #tagged > 0 then
		return tagged
	end
	return sampleGround()
end

-- Whether the map (and its spawn points) is in place yet: the placeholder island
-- builds in the background after the server starts (GDD §54).
function SpawnService.WorldReady(): boolean
	return WorldState.IsReady()
end

-- A spawn CFrame for one player. `livingPositions` are other active players.
-- Returns nil when the map offers no valid ground at all.
function SpawnService.Pick(livingPositions: { Vector3 }): CFrame?
	local position, isFallback = SpawnRules.Choose(candidates(), livingPositions, rng)
	if position == nil then
		return nil
	end
	if isFallback then
		warn("[SpawnService] No candidate met the minimum distance; using the farthest one")
	end
	return CFrame.new(position + Vector3.new(0, SpawnService.SPAWN_HEIGHT_OFFSET, 0))
end

return SpawnService
