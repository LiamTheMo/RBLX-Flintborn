-- Ground shape of the placeholder play-world island (GDD §54): sea level 0,
-- ordinary land 20–80, elevated terraces 100–220 (the Keep plateau, the Fallen
-- Temple mound, Timberwatch's lookout and the Emberhollow hill) and Frostpeak's
-- tallest peaks 450–600. Each zone has its own height profile; profiles blend
-- across the shared transition areas. Crater Lake sits in a rimmed crater with the
-- Keep island in the middle, reached by a land bridge from the south and a
-- shallow ford from the east; a river runs from the lake through the Riverlands to
-- the sea, fed by a creek out of Mosswick Forest. Heights are sampled on an
-- 8-stud lattice and blended in between, so the generated terrain and HeightAt
-- agree. Used to build the island until the authored map replaces it, and by
-- gameplay (resource nodes, wildlife, events) to find dry ground in a zone.

local BiomeCatalog = require(script.Parent.BiomeCatalog)
local PoiCatalog = require(script.Parent.PoiCatalog)

local IslandLayout = {}

IslandLayout.SEA_LEVEL = 0
IslandLayout.SEA_FLOOR = -40
IslandLayout.LATTICE = 8
-- The lattice (and the generated terrain) reaches past the island so the sea floor
-- slopes down before the open ocean.
IslandLayout.BUILD_HALF = 2304
IslandLayout.BEACH_WIDTH = 200

IslandLayout.LAKE_LEVEL = 28
IslandLayout.LAKE_WATER_RADIUS = 600
IslandLayout.RIM_HEIGHT = 72
IslandLayout.KEEP_HEIGHT = 120
IslandLayout.MAX_HEIGHT = 600
-- Spot height above the ground for a standing position.
IslandLayout.STAND_HEIGHT = 3
IslandLayout.POINT_TRIES = 30

local LAKE = BiomeCatalog.Zones.CraterLake.shape
local KEEP = BiomeCatalog.Zones.ShatteredKeep.shape
local CAVE = BiomeCatalog.Zones.EmberhollowCaves.interior
local TUNNEL = BiomeCatalog.Zones.EmberhollowCaves.tunnel

-- Courtyard of the Keep (the Guardian's arena), on the plateau.
IslandLayout.Courtyard = { x = 0, z = -140, halfX = 90, halfZ = 110 }

-- The Keep's way up: a ramp from the lower terrace to the plateau's south edge.
-- It runs from the plateau's south edge down over the lower terrace to meet the
-- land bridge, as a broad embankment (about 0.55 rise per stud).
IslandLayout.KeepRamp = { halfWidth = 12, topZ = 190, bottomZ = 345, bottom = 32, sideSlope = 0.6, sideWidth = 60 }
local KEEP_RAMP = IslandLayout.KeepRamp
local BRIDGE = { halfWidth = 14, fromZ = 150, toZ = 700 }
local FORD = { z = -100, halfWidth = 16, fromX = 180, toX = 640 }

-- Frostpeak's summits {x, z, height, radius}.
IslandLayout.Peaks = {
	{ x = -64, z = -1440, height = 596, radius = 300 },
	{ x = -472, z = -1376, height = 505, radius = 240 },
	{ x = 376, z = -1504, height = 470, radius = 240 },
}

-- Raised features {x, z, plateau height, plateau half-size or radius, slope width}.
IslandLayout.TempleMound = { x = -750, z = 980, height = 104, halfX = 80, halfZ = 80, slope = 70 }
IslandLayout.TempleRamp = { halfWidth = 14, length = 150 }
IslandLayout.Lookout = { x = -1330, z = 120, height = 148, radius = 110, slope = 110 }
IslandLayout.CaveHill = { height = 150, margin = 20, slope = 110 }

-- Rivers: polylines from source to mouth with water surface and half width at each
-- end and the channel depth.
IslandLayout.Rivers = {
	{
		id = "LakeRiver",
		points = {
			Vector3.new(560, 0, -80),
			Vector3.new(820, 0, -20),
			Vector3.new(1050, 0, 120),
			Vector3.new(1250, 0, 60),
			Vector3.new(1450, 0, 220),
			Vector3.new(1700, 0, 300),
			Vector3.new(2080, 0, 400),
		},
		surface = { 28, -1 },
		halfWidth = { 16, 26 },
		depth = 8,
	},
	{
		id = "MossCreek",
		points = {
			Vector3.new(1150, 0, -1250),
			Vector3.new(1250, 0, -900),
			Vector3.new(1330, 0, -600),
			Vector3.new(1300, 0, -300),
			Vector3.new(1250, 0, 60),
		},
		surface = { 30, 15 },
		halfWidth = { 7, 10 },
		depth = 4,
	},
}

for _, river in IslandLayout.Rivers do
	local total = 0
	river.lengths = { 0 }
	for index = 2, #river.points do
		total += (river.points[index] - river.points[index - 1]).Magnitude
		river.lengths[index] = total
	end
	river.length = total
end

local function lerp(a: number, b: number, t: number): number
	return a + (b - a) * t
end

local function smooth(t: number): number
	t = math.clamp(t, 0, 1)
	return t * t * (3 - 2 * t)
end

local function noise(x: number, z: number, scale: number, seed: number): number
	return math.noise(x / scale, z / scale, seed)
end

-- Distance from a rounded box's edge (0 inside it).
local function boxDistance(x: number, z: number, cx: number, cz: number, halfX: number, halfZ: number): number
	local dx = math.max(0, math.abs(x - cx) - halfX)
	local dz = math.max(0, math.abs(z - cz) - halfZ)
	return math.sqrt(dx * dx + dz * dz)
end

-- Raises ground toward a plateau: flat inside, easing back down across `slope`.
local function plateau(h: number, top: number, distance: number, slope: number): number
	if h >= top then
		return h
	end
	return lerp(top, h, smooth(distance / slope))
end

-- Nearest point of a river: distance, water surface and half width there.
function IslandLayout.RiverAt(x: number, z: number)
	local best = nil
	for _, river in IslandLayout.Rivers do
		local points = river.points
		for index = 2, #points do
			local a, b = points[index - 1], points[index]
			local abx, abz = b.X - a.X, b.Z - a.Z
			local lengthSq = abx * abx + abz * abz
			local t = math.clamp(((x - a.X) * abx + (z - a.Z) * abz) / lengthSq, 0, 1)
			local px, pz = a.X + abx * t, a.Z + abz * t
			local distance = math.sqrt((x - px) ^ 2 + (z - pz) ^ 2)
			if best == nil or distance < best.distance then
				local along = (river.lengths[index - 1] + math.sqrt(lengthSq) * t) / river.length
				best = {
					river = river,
					distance = distance,
					surface = lerp(river.surface[1], river.surface[2], along),
					halfWidth = lerp(river.halfWidth[1], river.halfWidth[2], along),
				}
			end
		end
	end
	return best
end

-- Each open zone's own ground before blending.
local PROFILES = {}

function PROFILES.Rimlands(x, z)
	return 28 + noise(x, z, 220, 1.7) * 12
end

function PROFILES.PinewoodWilds(x, z)
	return 50 + noise(x, z, 240, 2.2) * 26 + noise(x, z, 90, 2.9) * 6
end

function PROFILES.MosswickForest(x, z)
	return 32 + noise(x, z, 200, 3.1) * 10
end

function PROFILES.Riverlands(x, z)
	return 30 + noise(x, z, 260, 4.4) * 8
end

function PROFILES.Timberwatch(x, z)
	local h = 62 + noise(x, z, 200, 5.1) * 18
	local spot = IslandLayout.Lookout
	local distance = math.max(0, math.sqrt((x - spot.x) ^ 2 + (z - spot.z) ^ 2) - spot.radius)
	return plateau(h, spot.height, distance, spot.slope)
end

function PROFILES.FallenTemple(x, z)
	local h = 46 + noise(x, z, 210, 6.3) * 10
	local mound = IslandLayout.TempleMound
	h = plateau(h, mound.height, boxDistance(x, z, mound.x, mound.z, mound.halfX, mound.halfZ), mound.slope)
	-- A ramp up the mound's south face.
	local ramp = IslandLayout.TempleRamp
	local along = z - (mound.z + mound.halfZ)
	local side = math.abs(x - mound.x) - ramp.halfWidth
	if along >= 0 and along <= ramp.length and side < 24 then
		local top = lerp(mound.height, 46, along / ramp.length) - math.max(0, side) * 1.2
		h = math.max(h, top)
	end
	return h
end

function PROFILES.EmberhollowCaves(x, z)
	local h = 52 + noise(x, z, 180, 7.2) * 5
	local hill = IslandLayout.CaveHill
	local distance = boxDistance(x, z, CAVE.x, CAVE.z, CAVE.halfX + hill.margin, CAVE.halfZ + hill.margin)
	return plateau(h, hill.height + noise(x, z, 60, 7.5) * 5, distance, hill.slope)
end

function PROFILES.FrostpeakRidge(x, z)
	local depth = math.clamp(BiomeCatalog.EnvelopeDistance("FrostpeakRidge", x, z), 0, 1)
	local h = 95 + 235 * (1 - smooth(depth))
	local rise = 0
	for _, peak in IslandLayout.Peaks do
		local distance = math.sqrt((x - peak.x) ^ 2 + (z - peak.z) ^ 2)
		if distance < peak.radius then
			rise = math.max(rise, (peak.height - h) * (1 - distance / peak.radius) ^ 1.5)
		end
	end
	return h + rise + noise(x, z, 90, 8.1) * 16 * (1 - rise / 300)
end

-- Blended ground of the open zones; transition areas mix the nearest envelopes.
local BLEND = 0.35
local function blendedLand(x: number, z: number): number
	local distances, nearest = {}, math.huge
	for index, zoneId in BiomeCatalog.OPEN_ZONES do
		local distance = BiomeCatalog.EnvelopeDistance(zoneId, x, z)
		distances[index] = distance
		nearest = math.min(nearest, distance)
	end
	local total, weights = 0, 0
	for index, zoneId in BiomeCatalog.OPEN_ZONES do
		local weight = math.max(0, 1 - (distances[index] - nearest) / BLEND) ^ 2
		if weight > 0 then
			total += PROFILES[zoneId](x, z) * weight
			weights += weight
		end
	end
	return total / weights + noise(x, z, 64, 8.8) * 2.5
end

local function keepIsland(x: number, z: number): number
	local e = BiomeCatalog.EnvelopeDistance("ShatteredKeep", x, z)
	local shore = IslandLayout.LAKE_LEVEL + 2
	local h
	if e <= 0.58 then
		h = IslandLayout.KEEP_HEIGHT
	elseif e <= 0.75 then
		h = lerp(IslandLayout.KEEP_HEIGHT, 46, smooth((e - 0.58) / 0.17))
	elseif e <= 0.92 then
		h = lerp(46, 40, (e - 0.75) / 0.17)
	elseif e <= 1 then
		h = lerp(40, shore, (e - 0.92) / 0.08)
	else
		h = shore - (e - 1) * KEEP.halfZ * 0.3
	end
	-- The ramp from the bridge up to the plateau's south edge.
	local dz = z - KEEP.z
	local side = math.abs(x - KEEP.x) - KEEP_RAMP.halfWidth
	if dz >= KEEP_RAMP.topZ - 10 and dz <= KEEP_RAMP.bottomZ and side < KEEP_RAMP.sideWidth then
		local t = math.clamp((dz - KEEP_RAMP.topZ) / (KEEP_RAMP.bottomZ - KEEP_RAMP.topZ), 0, 1)
		local top = lerp(IslandLayout.KEEP_HEIGHT, KEEP_RAMP.bottom, t)
		h = math.max(h, top - math.max(0, side) * KEEP_RAMP.sideSlope)
	end
	return h
end

-- The crater: lake bed, shore, rim and the slope back down to the land outside,
-- with the Keep island, the land bridge and the ford.
local function crater(x: number, z: number, land: number): number
	local dx, dz = x - LAKE.x, z - LAKE.z
	local r = math.sqrt(dx * dx + dz * dz)
	local water = IslandLayout.LAKE_WATER_RADIUS
	local rim = IslandLayout.RIM_HEIGHT + noise(x, z, 60, 9.4) * 8
	local h
	if r < water then
		h = math.max(-8, IslandLayout.LAKE_LEVEL + 2 - (water - r) * 0.25)
	elseif r < LAKE.radius then
		h = lerp(IslandLayout.LAKE_LEVEL + 2, rim, smooth((r - water) / (LAKE.radius - water)))
	else
		h = lerp(rim, land, smooth((r - LAKE.radius) / 120))
	end
	if r < water + 40 then
		h = math.max(h, keepIsland(x, z))
		local side = math.abs(dx) - BRIDGE.halfWidth
		if z >= KEEP.z + BRIDGE.fromZ and z <= KEEP.z + BRIDGE.toZ then
			h = math.max(h, IslandLayout.LAKE_LEVEL + 4 - math.max(0, side) * 0.6)
		end
		local fordSide = math.abs(z - FORD.z) - FORD.halfWidth
		if dx >= FORD.fromX and dx <= FORD.toX then
			h = math.max(h, IslandLayout.LAKE_LEVEL - 1.5 - math.max(0, fordSide) * 0.4)
		end
	end
	return h
end

-- Ground height before lattice smoothing.
function IslandLayout.RawHeight(x: number, z: number): number
	local inland = BiomeCatalog.CoastDistance(x, z)
	if inland < -150 then
		return IslandLayout.SEA_FLOOR
	end
	local h = blendedLand(x, z)
	local dx, dz = x - LAKE.x, z - LAKE.z
	if dx * dx + dz * dz < (LAKE.radius + 120) ^ 2 then
		h = crater(x, z, h)
	end
	if inland < IslandLayout.BEACH_WIDTH then
		if inland < 0 then
			h = math.max(IslandLayout.SEA_FLOOR, 1.5 + inland * 0.35)
		else
			h = lerp(1.5, h, smooth(inland / IslandLayout.BEACH_WIDTH))
		end
	end
	local river = IslandLayout.RiverAt(x, z)
	if river then
		local edge = river.halfWidth
		if river.distance < edge then
			h = math.min(h, river.surface - river.river.depth * (1 - (river.distance / edge) ^ 2))
		elseif river.distance < edge + 60 and inland > 0 then
			-- Banks (and a low levee) keep the water in its channel.
			local beyond = river.distance - edge
			local top = river.surface + 1.5 + beyond * 0.6
			local bottom = river.surface + 1.5 - math.max(0, beyond - 20) * 0.25
			h = math.clamp(h, bottom, top)
		end
	end
	return math.min(h, IslandLayout.MAX_HEIGHT)
end

-- The lattice, filled lazily (the server's build fills all of it).
local SIDE = IslandLayout.BUILD_HALF * 2 / IslandLayout.LATTICE + 1
local lattice = {}

function IslandLayout.LatticeHeight(ix: number, iz: number): number
	-- Offset by one so the neighbours just past either edge get keys of their own.
	local key = (ix + 1) * (SIDE + 2) + iz + 1
	local h = lattice[key]
	if h == nil then
		h = IslandLayout.RawHeight(
			ix * IslandLayout.LATTICE - IslandLayout.BUILD_HALF,
			iz * IslandLayout.LATTICE - IslandLayout.BUILD_HALF
		)
		lattice[key] = h
	end
	return h
end

local function inTunnel(x: number, z: number): boolean
	return math.abs(x - TUNNEL.x) <= TUNNEL.halfWidth and z >= TUNNEL.fromZ and z <= TUNNEL.toZ
end

-- Height of the ground top at (x, z); below sea level out at sea. Over the
-- Emberhollow interior this is the hill above it, but the open mouth of its tunnel
-- is the tunnel floor.
function IslandLayout.HeightAt(x: number, z: number): number
	local half = IslandLayout.BUILD_HALF
	if math.abs(x) >= half or math.abs(z) >= half then
		return IslandLayout.SEA_FLOOR
	end
	local fx, fz = (x + half) / IslandLayout.LATTICE, (z + half) / IslandLayout.LATTICE
	local ix, iz = math.floor(fx), math.floor(fz)
	local tx, tz = fx - ix, fz - iz
	local h00, h10 = IslandLayout.LatticeHeight(ix, iz), IslandLayout.LatticeHeight(ix + 1, iz)
	local h01, h11 = IslandLayout.LatticeHeight(ix, iz + 1), IslandLayout.LatticeHeight(ix + 1, iz + 1)
	local h = lerp(lerp(h00, h10, tx), lerp(h01, h11, tx), tz)
	if inTunnel(x, z) and h < TUNNEL.ceiling + 6 then
		h = math.min(h, CAVE.floor)
	end
	return h
end

-- The water surface over (x, z): the lake, a river channel or the sea.
function IslandLayout.WaterLevelAt(x: number, z: number): number
	local dx, dz = x - LAKE.x, z - LAKE.z
	if dx * dx + dz * dz < IslandLayout.LAKE_WATER_RADIUS ^ 2 then
		return IslandLayout.LAKE_LEVEL
	end
	local river = IslandLayout.RiverAt(x, z)
	if river and river.distance < river.halfWidth then
		return river.surface
	end
	return IslandLayout.SEA_LEVEL
end

-- True when (x, z) is land above any water.
function IslandLayout.IsDry(x: number, z: number): boolean
	if BiomeCatalog.CoastDistance(x, z) <= 0 then
		return false
	end
	return IslandLayout.HeightAt(x, z) > IslandLayout.WaterLevelAt(x, z) + 0.5
end

-- Steepness (rise per stud) of the ground at (x, z).
function IslandLayout.SlopeAt(x: number, z: number): number
	local step = IslandLayout.LATTICE
	local gx = IslandLayout.HeightAt(x + step, z) - IslandLayout.HeightAt(x - step, z)
	local gz = IslandLayout.HeightAt(x, z + step) - IslandLayout.HeightAt(x, z - step)
	return math.sqrt(gx * gx + gz * gz) / (2 * step)
end

function IslandLayout.InCaveInterior(x: number, z: number): boolean
	return math.abs(x - CAVE.x) <= CAVE.halfX and math.abs(z - CAVE.z) <= CAVE.halfZ
end

-- Places nothing should spawn on: safe camps, the Keep's courtyard, the temple top,
-- landmarks, portal pads and the cave tunnel (structures stand there).
IslandLayout.LANDMARK_CLEARANCE = 30
function IslandLayout.KeepOut(x: number, z: number, margin: number?): boolean
	local pad = margin or 0
	for _, zone in PoiCatalog.SafeZones do
		if (x - zone.x) ^ 2 + (z - zone.z) ^ 2 < (zone.radius + 10 + pad) ^ 2 then
			return true
		end
	end
	local court = IslandLayout.Courtyard
	if math.abs(x - court.x) <= court.halfX + 12 + pad and math.abs(z - court.z) <= court.halfZ + 12 + pad then
		return true
	end
	local mound = IslandLayout.TempleMound
	if math.abs(x - mound.x) <= mound.halfX + pad and math.abs(z - mound.z) <= mound.halfZ + pad then
		return true
	end
	for _, landmark in PoiCatalog.Landmarks do
		if (x - landmark.x) ^ 2 + (z - landmark.z) ^ 2 < (IslandLayout.LANDMARK_CLEARANCE + pad) ^ 2 then
			return true
		end
	end
	for _, portal in PoiCatalog.Portals do
		if (x - portal.x) ^ 2 + (z - portal.z) ^ 2 < (portal.zoneRadius + 8 + pad) ^ 2 then
			return true
		end
	end
	return math.abs(x - TUNNEL.x) <= TUNNEL.halfWidth + 6 + pad and z >= TUNNEL.fromZ - 6 and z <= TUNNEL.toZ + 6 + pad
end

-- Noise fields for the soft habitats (open patches, marsh, rocky ground).
local function openness(x: number, z: number): number
	return noise(x, z, 200, 10.5)
end

-- Whether dry ground at (x, z) in `zoneId` counts as `habitat` (approximate).
function IslandLayout.HabitatMatches(habitat: string, zoneId: string, x: number, z: number): boolean
	if not BiomeCatalog.HasHabitat(zoneId, habitat) then
		return false
	end
	local h = IslandLayout.HeightAt(x, z)
	if habitat == "Beach" then
		return BiomeCatalog.CoastDistance(x, z) < IslandLayout.BEACH_WIDTH and h < 24
	elseif habitat == "Lakeshore" then
		local r = math.sqrt((x - LAKE.x) ^ 2 + (z - LAKE.z) ^ 2)
		local keep = BiomeCatalog.EnvelopeDistance("ShatteredKeep", x, z)
		return (r >= IslandLayout.LAKE_WATER_RADIUS - 10 and r < IslandLayout.LAKE_WATER_RADIUS + 70)
			or (keep > 0.85 and keep < 1)
			or (math.abs(z - FORD.z) < 60 and x - LAKE.x > FORD.fromX)
	elseif habitat == "River" then
		local river = IslandLayout.RiverAt(x, z)
		return river ~= nil and river.distance < river.halfWidth + 70
	elseif habitat == "Marsh" then
		return h < 36 and noise(x, z, 180, 11.3) > 0.05
	elseif habitat == "Rocky" then
		return IslandLayout.SlopeAt(x, z) > 0.45 or noise(x, z, 150, 12.7) > 0.25 or h > 200
	elseif habitat == "Highland" then
		return h >= 90
	elseif habitat == "Cave" then
		return IslandLayout.InCaveInterior(x, z)
	elseif habitat == "Clearing" then
		return openness(x, z) > 0.2 and IslandLayout.SlopeAt(x, z) < 0.35
	elseif habitat == "Forest" or habitat == "Jungle" then
		return openness(x, z) <= 0.2 and h < 260 and BiomeCatalog.CoastDistance(x, z) > 120
	elseif habitat == "Meadow" then
		return openness(x, z) > -0.1 and IslandLayout.SlopeAt(x, z) < 0.25 and h < 90
	elseif habitat == "Grassland" then
		return IslandLayout.SlopeAt(x, z) < 0.3 and h < 90 and BiomeCatalog.CoastDistance(x, z) > 80
	end
	return true
end

local KNOWN_HABITATS = {}
for _, habitat in BiomeCatalog.HABITATS do
	KNOWN_HABITATS[habitat] = true
end

-- A candidate (x, z) for a zone; narrow habitats are sampled where they lie.
local function candidate(zoneId: string, rng: Random, habitat: string?): (number, number)
	if habitat == "River" then
		local river = IslandLayout.Rivers[rng:NextInteger(1, #IslandLayout.Rivers)]
		local index = rng:NextInteger(2, #river.points)
		local a, b = river.points[index - 1], river.points[index]
		local t = rng:NextNumber()
		local along = a + (b - a) * t
		local direction = (b - a) / (b - a).Magnitude
		local side = if rng:NextNumber() < 0.5 then -1 else 1
		local offset = side * rng:NextNumber(32, 80)
		return along.X - direction.Z * offset, along.Z + direction.X * offset
	elseif habitat == "Lakeshore" and zoneId == "CraterLake" then
		local angle = rng:NextNumber(0, math.pi * 2)
		local r = rng:NextNumber(IslandLayout.LAKE_WATER_RADIUS, IslandLayout.LAKE_WATER_RADIUS + 60)
		return LAKE.x + math.cos(angle) * r, LAKE.z + math.sin(angle) * r
	end
	local shape = BiomeCatalog.Zones[zoneId].shape
	if shape.kind == "Coast" then
		local angle = math.rad(shape.angle + rng:NextNumber(-shape.halfAngle, shape.halfAngle))
		local dx, dz = math.cos(angle), math.sin(angle)
		local coast = BiomeCatalog.CoastRadius(dx, dz)
		local depth = if habitat == "Beach" then IslandLayout.BEACH_WIDTH else shape.depth
		local r = coast - rng:NextNumber(10, depth)
		return dx * r, dz * r
	elseif shape.kind == "Disc" then
		-- The dry shore and rim.
		local angle = rng:NextNumber(0, math.pi * 2)
		local r = rng:NextNumber(IslandLayout.LAKE_WATER_RADIUS, shape.radius)
		return shape.x + math.cos(angle) * r, shape.z + math.sin(angle) * r
	end
	local bounds = BiomeCatalog.Bounds(zoneId)
	return rng:NextNumber(bounds.minX, bounds.maxX), rng:NextNumber(bounds.minZ, bounds.maxZ)
end

-- A standing position (ground + STAND_HEIGHT) on dry ground in `zoneId`, outside
-- safe camps and structures, matching `habitat` when given (an unknown habitat is
-- ignored; a habitat the zone does not offer finds nothing). "Cave" stands on the
-- Emberhollow interior floor. Nil when nothing is found after POINT_TRIES tries.
function IslandLayout.RandomPointIn(zoneId: string, rng: Random, habitat: string?): Vector3?
	if BiomeCatalog.Zones[zoneId] == nil then
		return nil
	end
	if habitat and not KNOWN_HABITATS[habitat] then
		habitat = nil
	end
	if habitat == "Cave" then
		if not BiomeCatalog.HasHabitat(zoneId, "Cave") then
			return nil
		end
		local x = CAVE.x + rng:NextNumber(-CAVE.halfX + 20, CAVE.halfX - 20)
		local z = CAVE.z + rng:NextNumber(-CAVE.halfZ + 20, CAVE.halfZ - 20)
		return Vector3.new(x, CAVE.floor + IslandLayout.STAND_HEIGHT, z)
	end
	for _ = 1, IslandLayout.POINT_TRIES do
		local x, z = candidate(zoneId, rng, habitat)
		if
			BiomeCatalog.ZoneAt(x, z) == zoneId
			and IslandLayout.IsDry(x, z)
			and not IslandLayout.KeepOut(x, z)
			and (habitat == nil or IslandLayout.HabitatMatches(habitat, zoneId, x, z))
		then
			return Vector3.new(x, IslandLayout.HeightAt(x, z) + IslandLayout.STAND_HEIGHT, z)
		end
	end
	return nil
end

-- Player spawn candidates (GDD §3.1, Q33, §54): spread over every Low and Medium
-- zone on a fixed pattern, on dry, gentle ground away from camps, structures and
-- portals. Ground positions.
IslandLayout.SPAWN_PATTERN = {
	{ 0, 0 },
	{ -0.55, -0.55 },
	{ 0.55, -0.55 },
	{ -0.55, 0.55 },
	{ 0.55, 0.55 },
	{ 0, -0.7 },
	{ 0, 0.7 },
	{ -0.7, 0 },
	{ 0.7, 0 },
}
IslandLayout.SPAWN_PORTAL_CLEARANCE = 60

local function nearPortal(x: number, z: number): boolean
	for _, portal in PoiCatalog.Portals do
		if (x - portal.x) ^ 2 + (z - portal.z) ^ 2 < IslandLayout.SPAWN_PORTAL_CLEARANCE ^ 2 then
			return true
		end
	end
	return false
end

local spawnCache = nil
function IslandLayout.SpawnCandidates(): { Vector3 }
	if spawnCache then
		return spawnCache
	end
	local list = {}
	for _, zoneId in BiomeCatalog.ZONE_IDS do
		local zone = BiomeCatalog.Zones[zoneId]
		if zone.tier ~= "CenterCrater" then
			for _, offset in IslandLayout.SPAWN_PATTERN do
				local x, z
				if zone.shape.kind == "Coast" then
					local angle = math.rad(zone.shape.angle + offset[1] * zone.shape.halfAngle * 1.2)
					local dx, dz = math.cos(angle), math.sin(angle)
					local r = BiomeCatalog.CoastRadius(dx, dz) - zone.shape.depth * (0.5 + offset[2] * 0.5)
					x, z = dx * r, dz * r
				else
					local cx, cz = BiomeCatalog.Center(zoneId)
					x, z = cx + offset[1] * zone.shape.halfX, cz + offset[2] * zone.shape.halfZ
				end
				if
					BiomeCatalog.ZoneAt(x, z) == zoneId
					and IslandLayout.IsDry(x, z)
					and IslandLayout.SlopeAt(x, z) < 0.6
					and not IslandLayout.KeepOut(x, z, 20)
					and not IslandLayout.InCaveInterior(x, z)
					and not nearPortal(x, z)
				then
					table.insert(list, Vector3.new(x, IslandLayout.HeightAt(x, z), z))
				end
			end
		end
	end
	spawnCache = list
	return list
end

-- Surface material name for terrain at (x, z) with ground `h` and `slope`.
function IslandLayout.SurfaceMaterial(zoneId: string?, x: number, z: number, h: number, slope: number): string
	if zoneId == nil or BiomeCatalog.CoastDistance(x, z) < 60 and h < 14 then
		return "Sand"
	end
	local river = IslandLayout.RiverAt(x, z)
	if river and river.distance < river.halfWidth + 3 then
		return "Mud"
	end
	if zoneId == "CraterLake" then
		local r = math.sqrt((x - LAKE.x) ^ 2 + (z - LAKE.z) ^ 2)
		if r < IslandLayout.LAKE_WATER_RADIUS then
			return if h > IslandLayout.LAKE_LEVEL - 6 then "Sand" else "Mud"
		end
		return if slope > 0.5 then "Basalt" else "Ground"
	elseif zoneId == "ShatteredKeep" then
		if h < IslandLayout.LAKE_LEVEL + 1 then
			return "Sand"
		end
		return if h >= IslandLayout.KEEP_HEIGHT - 1 then "Cobblestone" elseif slope > 0.6 then "Slate" else "Ground"
	elseif zoneId == "FrostpeakRidge" then
		if h > 480 then
			return "Glacier"
		elseif h > 240 then
			return if slope > 1.5 then "Rock" else "Snow"
		end
		return if slope > 0.8 or h > 170 then "Rock" else "Grass"
	end
	if slope > 0.9 then
		return "Rock"
	end
	if zoneId == "MosswickForest" and h < 36 and noise(x, z, 180, 11.3) > 0.05 then
		return "Mud"
	elseif zoneId == "FallenTemple" and h >= IslandLayout.TempleMound.height - 1 then
		return "Limestone"
	elseif zoneId == "EmberhollowCaves" then
		return if h > 110 or slope > 0.5 then "Basalt" else "Ground"
	elseif zoneId == "Timberwatch" and h >= IslandLayout.Lookout.height - 1 then
		return "Ground"
	end
	return BiomeCatalog.Zones[zoneId].material
end

return IslandLayout
