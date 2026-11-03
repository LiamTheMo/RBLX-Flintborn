-- Small geometry helpers shared by the rules, the server and the client.

local Geometry = {}

-- The horizontal (XZ-plane) distance between two positions; height is ignored.
function Geometry.FlatDistance(a: Vector3, b: Vector3): number
	local dx, dz = a.X - b.X, a.Z - b.Z
	return math.sqrt(dx * dx + dz * dz)
end

return Geometry
