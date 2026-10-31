-- Turns placeholder recipes (Recipe) into Instances. Three ways:
--   Build(recipe, origin, options)    -> an anchored stand-alone Model (props).
--   Decorate(host, recipe, options)   -> parts welded onto an existing part (an
--                                        invisible hitbox, a body part); they follow it
--                                        when it moves and never block rays or players.
--   Attach(host, recipe, offset, opt) -> Decorate into its own Model at an offset from
--                                        the host (held gear, worn armor).
-- Rotations are CFrame.Angles(rx, ry, rz) in degrees. Server and client both use it.

local Recipe = require(script.Parent.Recipe)

local ModelBuilder = {}

local CLASS = { Wedge = "WedgePart", CornerWedge = "CornerWedgePart" }
local SHAPE = { Ball = Enum.PartType.Ball, Cylinder = Enum.PartType.Cylinder, Block = Enum.PartType.Block }

local materials = {}
local function material(name: string?): Enum.Material
	if name == nil then
		return Enum.Material.SmoothPlastic
	end
	local value = materials[name]
	if value == nil then
		local ok, found = pcall(function()
			return (Enum.Material :: any)[name]
		end)
		value = if ok and found then found else Enum.Material.SmoothPlastic
		materials[name] = value
	end
	return value
end

-- The local CFrame of a spec inside its recipe, with `scale` multiplying positions.
function ModelBuilder.LocalCFrame(spec, scale: Vector3?): CFrame
	local s = scale or Vector3.one
	local position = Vector3.new(spec.pos[1] * s.X, spec.pos[2] * s.Y, spec.pos[3] * s.Z)
	local rot = spec.rot
	if rot then
		return CFrame.new(position) * CFrame.Angles(math.rad(rot[1]), math.rad(rot[2]), math.rad(rot[3]))
	end
	return CFrame.new(position)
end

-- One part from a spec, placed at `cframe`, sizes multiplied by `scale`.
function ModelBuilder.MakePart(spec, cframe: CFrame, scale: Vector3?): BasePart
	local s = scale or Vector3.one
	local part = Instance.new(CLASS[spec.shape] or "Part") :: BasePart
	if SHAPE[spec.shape] then
		(part :: Part).Shape = SHAPE[spec.shape]
	end
	part.Name = spec.name or spec.shape
	part.Size = Vector3.new(
		math.max(0.05, spec.size[1] * s.X),
		math.max(0.05, spec.size[2] * s.Y),
		math.max(0.05, spec.size[3] * s.Z)
	)
	part.Color = Color3.fromRGB(spec.color[1], spec.color[2], spec.color[3])
	part.Material = material(spec.material)
	part.Transparency = spec.transparency or 0
	if spec.transparency then
		part:SetAttribute("BaseTransparency", spec.transparency)
	end
	part.TopSurface = Enum.SurfaceType.Smooth
	part.BottomSurface = Enum.SurfaceType.Smooth
	part.CastShadow = spec.shadow ~= false
	part.CFrame = cframe
	return part
end

local function passive(part: BasePart)
	part.CanCollide = false
	part.CanQuery = false
	part.CanTouch = false
	part.Massless = true
end

-- An anchored Model of the recipe with its origin at `origin`.
-- options: {name?, parent?, scale?: Vector3, collide?: boolean (default false),
-- query?: boolean (default false), tags?: {string}}
function ModelBuilder.Build(recipe, origin: CFrame, options): Model
	options = options or {}
	local model = Instance.new("Model")
	model.Name = options.name or "Placeholder"
	for _, spec in recipe.parts do
		local part = ModelBuilder.MakePart(spec, origin * ModelBuilder.LocalCFrame(spec, options.scale), options.scale)
		part.Anchored = true
		part.CanCollide = options.collide == true
		part.CanQuery = options.query == true
		part.CanTouch = false
		part.Parent = model
	end
	model.WorldPivot = origin
	if options.parent then
		model.Parent = options.parent
	end
	return model
end

-- Welds the recipe's parts onto `host`, measured from host.CFrame * (options.offset
-- or identity). A `normalized` recipe is scaled by the host's size. The parts are
-- non-colliding, non-querying and massless; they go under options.parent (default
-- the host). Returns the parts.
function ModelBuilder.Decorate(host: BasePart, recipe, options): { BasePart }
	options = options or {}
	local scale = if recipe.normalized then host.Size else options.scale
	local base = host.CFrame * (options.offset or CFrame.identity)
	local parts = {}
	for _, spec in recipe.parts do
		local part = ModelBuilder.MakePart(spec, base * ModelBuilder.LocalCFrame(spec, scale), scale)
		passive(part)
		part.Anchored = false
		local weld = Instance.new("Weld")
		weld.Part0 = host
		weld.Part1 = part
		weld.C0 = host.CFrame:ToObjectSpace(part.CFrame)
		weld.Parent = part
		part.Parent = options.parent or host
		table.insert(parts, part)
	end
	return parts
end

-- Decorate into a new Model named options.name under options.parent (default the
-- host's parent), at `offset` from the host. Destroy the model to take it off.
function ModelBuilder.Attach(host: BasePart, recipe, offset: CFrame, options): Model
	options = options or {}
	local model = Instance.new("Model")
	model.Name = options.name or "Attachment"
	ModelBuilder.Decorate(host, recipe, { offset = offset, scale = options.scale, parent = model })
	model.Parent = options.parent or host.Parent
	return model
end

-- Shows or hides decoration parts (a depleted node, a dead creature).
function ModelBuilder.SetVisible(parts: { BasePart }, visible: boolean)
	for _, part in parts do
		part.Transparency = if visible then (part:GetAttribute("BaseTransparency") or 0) else 1
	end
end

-- Problems with a recipe (re-exported so callers need one module).
ModelBuilder.Problems = Recipe.Problems

return ModelBuilder
