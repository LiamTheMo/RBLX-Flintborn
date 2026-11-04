-- The placeholder model format (v0.19): every stand-in model (held gear, worn armor,
-- resource nodes, creatures, bosses, event props) is a plain table of primitive
-- parts, so the shapes live in data that headless specs can check and
-- ModelBuilder turns into Instances. Real models replace a recipe later without
-- touching gameplay code.
--
-- recipe = {
--   parts = {
--     {
--       shape = "Block" | "Ball" | "Cylinder" | "Wedge" | "CornerWedge",
--       size = { x, y, z },          -- studs (or fractions of the host when `normalized`)
--       pos = { x, y, z },           -- centre offset from the recipe's origin
--       rot = { rx, ry, rz }?,       -- degrees, as CFrame.Angles(rx, ry, rz)
--       color = { r, g, b },         -- 0..255
--       material = "Wood"?,          -- an Enum.Material name (default SmoothPlastic)
--       transparency = 0.2?,
--       name = "Blade"?,
--     },
--     ...
--   },
--   normalized = true?,              -- size/pos are fractions of the host part's size
-- }
--
-- Origins: held items are measured from the grip (the hand), +Y up the handle
-- and -Z forward; armor from the centre of the body part it covers; nodes, props
-- and creatures from the centre of their hitbox, facing -Z. A Cylinder's axis is
-- its X axis, as in Roblox.

local Recipe = {}

Recipe.SHAPES = { Block = true, Ball = true, Cylinder = true, Wedge = true, CornerWedge = true }

-- A part spec; keeps recipe tables short.
function Recipe.Part(
	shape: string,
	size: { number },
	pos: { number },
	color: { number },
	material: string?,
	rot: { number }?,
	extra: { [string]: any }?
)
	local spec = { shape = shape, size = size, pos = pos, color = color, material = material, rot = rot }
	for key, value in extra or {} do
		spec[key] = value
	end
	return spec
end

local function isTriple(value): boolean
	return type(value) == "table"
		and type(value[1]) == "number"
		and type(value[2]) == "number"
		and type(value[3]) == "number"
		and value[1] == value[1]
		and value[2] == value[2]
		and value[3] == value[3]
end

-- Problems with a recipe (empty when it is buildable). `maxParts` caps its size.
function Recipe.Problems(recipe, maxParts: number?): { string }
	local problems = {}
	if type(recipe) ~= "table" or type(recipe.parts) ~= "table" or #recipe.parts == 0 then
		return { "no parts" }
	end
	if maxParts and #recipe.parts > maxParts then
		table.insert(problems, ("%d parts (max %d)"):format(#recipe.parts, maxParts))
	end
	for index, spec in recipe.parts do
		local where = "part " .. index
		if not Recipe.SHAPES[spec.shape] then
			table.insert(problems, where .. ": unknown shape " .. tostring(spec.shape))
		end
		if not isTriple(spec.size) or spec.size[1] <= 0 or spec.size[2] <= 0 or spec.size[3] <= 0 then
			table.insert(problems, where .. ": bad size")
		end
		if not isTriple(spec.pos) then
			table.insert(problems, where .. ": bad pos")
		end
		if spec.rot ~= nil and not isTriple(spec.rot) then
			table.insert(problems, where .. ": bad rot")
		end
		local color = spec.color
		if not isTriple(color) then
			table.insert(problems, where .. ": bad color")
		elseif color[1] < 0 or color[1] > 255 or color[2] < 0 or color[2] > 255 or color[3] < 0 or color[3] > 255 then
			table.insert(problems, where .. ": color out of range")
		end
		if spec.material ~= nil and type(spec.material) ~= "string" then
			table.insert(problems, where .. ": bad material")
		end
	end
	return problems
end

-- The recipe's axis-aligned extent ({minX, minY, minZ}, {maxX, maxY, maxZ}),
-- ignoring rotation (good enough for sizing hitboxes and checks).
function Recipe.Bounds(recipe): ({ number }, { number })
	local low = { math.huge, math.huge, math.huge }
	local high = { -math.huge, -math.huge, -math.huge }
	for _, spec in recipe.parts do
		for axis = 1, 3 do
			low[axis] = math.min(low[axis], spec.pos[axis] - spec.size[axis] / 2)
			high[axis] = math.max(high[axis], spec.pos[axis] + spec.size[axis] / 2)
		end
	end
	return low, high
end

-- An RGB triple from a Color3 (0..1 channels), for recipes built from catalog colours.
function Recipe.Rgb(color): { number }
	return { math.round(color.R * 255), math.round(color.G * 255), math.round(color.B * 255) }
end

-- `rgb` scaled toward black (factor < 1) or white (factor > 1), clamped.
function Recipe.Shade(rgb: { number }, factor: number): { number }
	local out = {}
	for index = 1, 3 do
		local value = if factor <= 1 then rgb[index] * factor else rgb[index] + (255 - rgb[index]) * (factor - 1)
		out[index] = math.clamp(math.round(value), 0, 255)
	end
	return out
end

return Recipe
