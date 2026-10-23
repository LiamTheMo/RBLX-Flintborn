-- Ground height of the placeholder Shattered Crater (GDD §3): low beaches, rising
-- woodland, a higher jungle plateau, a volcanic ridge ringing the crater with route
-- gaps, and an open caldera floor. Used to generate the blocky island until the
-- authored map replaces it.

local BiomeCatalog = require(script.Parent.BiomeCatalog)
local PoiCatalog = require(script.Parent.PoiCatalog)

local IslandLayout = {}

IslandLayout.TILE = 48
IslandLayout.SEA_LEVEL = 0
IslandLayout.RIDGE_RADIUS = 300
IslandLayout.RIDGE_WIDTH = 34
IslandLayout.RIDGE_HEIGHT = 46
IslandLayout.GAP_DEGREES = 9

local function lerp(a: number, b: number, t: number): number
	return a + (b - a) * math.clamp(t, 0, 1)
end

local function inGap(angle: number): boolean
	for _, gap in PoiCatalog.RidgeGaps do
		local delta = math.abs((angle - gap + 180) % 360 - 180)
		if delta <= IslandLayout.GAP_DEGREES then
			return true
		end
	end
	return false
end

-- Height of the ground top at (x, z); below sea level outside the island.
function IslandLayout.HeightAt(x: number, z: number): number
	local distance = math.sqrt(x * x + z * z)
	local angle = math.deg(math.atan2(z, x)) % 360
	local bumps = math.noise(x / 160, z / 160, 0.37) * 4
	if distance > BiomeCatalog.MAP_RADIUS then
		return -18
	end
	if distance > 1050 then
		return lerp(6, 2, (distance - 1050) / 150)
	end
	if distance > 750 then
		return lerp(14, 6, (distance - 750) / 300) + bumps
	end
	local ridge = math.abs(distance - IslandLayout.RIDGE_RADIUS)
	if ridge < IslandLayout.RIDGE_WIDTH and not inGap(angle) then
		return IslandLayout.RIDGE_HEIGHT - ridge * 0.6
	end
	if distance > IslandLayout.RIDGE_RADIUS then
		return 20 + bumps * 1.5
	end
	-- The caldera floor dips gently toward the centre.
	return lerp(10, 16, distance / IslandLayout.RIDGE_RADIUS)
end

return IslandLayout
