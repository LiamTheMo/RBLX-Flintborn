-- What every part of the island build shares (WorldBuildService): the build's
-- state, the yield between chunks of work, tagged parts and anchors, structure
-- blocks and the stone and wood palette.

local CollectionService = game:GetService("CollectionService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local IslandLayout = require(ReplicatedStorage.Shared.World.IslandLayout)

local BuildKit = {}

-- `service` is WorldBuildService (its tunables are read as the build runs),
-- `folder` the map folder being filled and `lastYield` when the build last yielded.
BuildKit.state = { service = nil, folder = nil, lastYield = 0 }
local state = BuildKit.state

local function breathe()
	if os.clock() - state.lastYield >= state.service.YIELD_SECONDS then
		task.wait()
		state.lastYield = os.clock()
	end
end

local function part(props, tags)
	local instance = Instance.new(props.ClassName or "Part")
	instance.Anchored = true
	instance.TopSurface = Enum.SurfaceType.Smooth
	instance.BottomSurface = Enum.SurfaceType.Smooth
	for key, value in props do
		if key ~= "ClassName" then
			instance[key] = value
		end
	end
	for _, tag in tags or {} do
		CollectionService:AddTag(instance, tag)
		if tag == "GeneratedStructure" then
			-- Map ruins are never claimable (Q39); BuildingService marks tagged parts at
			-- Start, before this background build has made them.
			instance:SetAttribute("Generated", true)
		end
	end
	instance.Parent = props.Parent or state.folder
	return instance
end

-- An invisible anchor the gameplay services read by tag.
local function anchor(name: string, position: Vector3, tag: string, attributes)
	local marker = part({
		Name = name,
		Size = Vector3.new(2, 2, 2),
		CFrame = CFrame.new(position + Vector3.new(0, 1, 0)),
		Transparency = 1,
		CanCollide = false,
		CanQuery = false,
		CanTouch = false,
	}, { tag })
	for key, value in attributes or {} do
		marker:SetAttribute(key, value)
	end
	return marker
end

local function groundAt(x: number, z: number): Vector3
	return Vector3.new(x, IslandLayout.HeightAt(x, z), z)
end

local STONE = Color3.fromRGB(150, 146, 136)
local DARK_STONE = Color3.fromRGB(92, 88, 96)
local WOOD = Color3.fromRGB(110, 78, 50)

local function model(name: string, attributes)
	local instance = Instance.new("Model")
	instance.Name = name
	for key, value in attributes or {} do
		instance:SetAttribute(key, value)
	end
	instance.Parent = state.folder
	return instance
end

local function block(parent, name: string, cframe: CFrame, size: Vector3, color: Color3, mat: Enum.Material)
	return part({
		Name = name,
		CFrame = cframe,
		Size = size,
		Color = color,
		Material = mat,
		Parent = parent,
	}, { "GeneratedStructure" })
end

-- Pure decoration (a painted opening, a flame, a tent floor): no tag, no collision,
-- no query, so it never blocks building, rays or projectiles.
local function decor(parent, name: string, cframe: CFrame, size: Vector3, color: Color3, mat: Enum.Material)
	return part({
		Name = name,
		CFrame = cframe,
		Size = size,
		Color = color,
		Material = mat,
		CanCollide = false,
		CanQuery = false,
		CanTouch = false,
		Parent = parent,
	})
end

BuildKit.breathe = breathe
BuildKit.part = part
BuildKit.anchor = anchor
BuildKit.groundAt = groundAt
BuildKit.model = model
BuildKit.block = block
BuildKit.decor = decor
BuildKit.STONE = STONE
BuildKit.DARK_STONE = DARK_STONE
BuildKit.WOOD = WOOD

return BuildKit
