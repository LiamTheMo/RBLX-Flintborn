-- Pure building rules (GDD §6.2, §3.1, §22.4, Q39, Q144–146, Q159, §60). Placement
-- is free (§60): a piece stands wherever it is aimed, upright, turned about the
-- vertical axis in ROTATE_STEP degrees, and may stick to a nearby piece's faces
-- and edges (SnapToNeighbours). Footprints are oriented boxes: `half` is the
-- piece's own half-size and `yaw` its turn in degrees; HalfExtents gives the
-- world-aligned box around a turned piece for coarse queries. Totems stop decay for
-- their own tribe's structures only; they never stop raids. A structure that
-- loses cover gets one 240–360 s deadline and is then removed outright; regaining
-- cover clears it. Uncovered structures can be claimed by another tribe's totem,
-- never while a totem of their owner still covers them. Server-generated
-- structures are never claimable and never decay. A piece must stand in the open:
-- no more than GROUND_ALLOWANCE studs sunk into the ground, on support no more
-- than SUPPORT_TOLERANCE studs below its base and no steeper than MAX_SLOPE,
-- inside the world, clear of other pieces (OVERLAP_TOLERANCE), visible from the
-- builder, and with no part of its footprint in a safe zone; each owner may keep
-- at most MAX_TOTEMS_PER_OWNER totems.

local StructureCatalog = require(script.Parent.StructureCatalog)
local Validation = require(script.Parent.Parent.Data.Validation)

local BuildRules = {}

BuildRules.REACH = 24
-- Free placement (§60). Pieces turn in ROTATE_STEP-degree steps; the server
-- accepts no other angle.
BuildRules.ROTATE_STEP = 15
-- Holding the rotate input repeats a step this often after the first.
BuildRules.ROTATE_REPEAT_DELAY = 0.35
BuildRules.ROTATE_REPEAT = 0.08
-- Two pieces may touch and overlap by this much on each side (flush walls,
-- rounding after a turn) before they count as overlapping.
BuildRules.OVERLAP_TOLERANCE = 0.25
-- Support: some point of the base (centre or a corner) must have solid ground,
-- a structure or a part at most this far below it ...
BuildRules.SUPPORT_TOLERANCE = 1.5
-- ... measured by rays that start this far above the base.
BuildRules.SUPPORT_PROBE = 1.5
-- Supporting ground no steeper than this (degrees from level).
BuildRules.MAX_SLOPE = 40
-- Magnetic snap: an edge or face this close to a neighbour's lines up with it
-- (only while the piece is turned like the neighbour or at a right angle to it,
-- so one rotate step always turns the piece away from a snap).
BuildRules.SNAP_DISTANCE = 1.5
-- The build area: the generated island's lattice (IslandLayout.BUILD_HALF) and
-- the heights between its sea floor and well above Frostpeak.
BuildRules.WORLD_HALF = 2304
BuildRules.WORLD_MIN_Y = -40
BuildRules.WORLD_MAX_Y = 1000

-- True when a Vector3's components are all finite numbers (no NaN or infinity).
function BuildRules.FiniteVector(position: any): boolean
	return position ~= nil
		and Validation.IsFinite(position.X)
		and Validation.IsFinite(position.Y)
		and Validation.IsFinite(position.Z)
end

-- `yaw` turned by `steps` rotate steps, in [0, 360).
function BuildRules.Turn(yaw: number, steps: number): number
	return (yaw + steps * BuildRules.ROTATE_STEP) % 360
end

-- True when a base position lies in the build area.
function BuildRules.InWorld(position: Vector3): boolean
	return BuildRules.FiniteVector(position)
		and math.abs(position.X) <= BuildRules.WORLD_HALF
		and math.abs(position.Z) <= BuildRules.WORLD_HALF
		and position.Y >= BuildRules.WORLD_MIN_Y
		and position.Y <= BuildRules.WORLD_MAX_Y
end

-- A piece-local horizontal offset turned by `yaw` degrees into world axes, as
-- CFrame.Angles(0, rad(yaw), 0) turns it.
function BuildRules.ToWorld(x: number, z: number, yaw: number): (number, number)
	local r = math.rad(yaw)
	local c, s = math.cos(r), math.sin(r)
	return c * x + s * z, -s * x + c * z
end

-- The inverse of ToWorld: a world horizontal offset in the piece's own axes.
function BuildRules.ToLocal(x: number, z: number, yaw: number): (number, number)
	local r = math.rad(yaw)
	local c, s = math.cos(r), math.sin(r)
	return c * x - s * z, s * x + c * z
end

-- Half-size of the world-aligned box around a piece of `size` turned `yaw`
-- degrees (the piece's own half-size at 0, 90, 180 and 270).
function BuildRules.HalfExtents(size: Vector3, yaw: number?): Vector3
	local r = math.rad(yaw or 0)
	local c, s = math.abs(math.cos(r)), math.abs(math.sin(r))
	-- Drop float dust so quarter turns give exact sizes.
	c = if c < 1e-9 then 0 else c
	s = if s < 1e-9 then 0 else s
	local hx, hz = size.X / 2, size.Z / 2
	return Vector3.new(c * hx + s * hz, size.Y / 2, s * hx + c * hz)
end

-- Horizontal distance from `point` to the nearest part of the footprint. With
-- `yaw`, `half` is the piece's own half-size turned by it; without, `half` is a
-- world-aligned box.
function BuildRules.HorizontalDistance(point: Vector3, center: Vector3, half: Vector3, yaw: number?): number
	local x, z = point.X - center.X, point.Z - center.Z
	if yaw then
		x, z = BuildRules.ToLocal(x, z, yaw)
	end
	local dx = math.max(math.abs(x) - half.X, 0)
	local dz = math.max(math.abs(z) - half.Z, 0)
	return math.sqrt(dx * dx + dz * dz)
end

-- True when any part of the footprint enters a no-build aura (not just its centre).
function BuildRules.OverlapsAura(center: Vector3, half: Vector3, auras, yaw: number?): boolean
	for _, aura in auras do
		if BuildRules.HorizontalDistance(aura.center, center, half, yaw) < aura.radius then
			return true
		end
	end
	return false
end

-- True when two upright pieces ({center, half (own), yaw}) overlap by more than
-- `tolerance` (default OVERLAP_TOLERANCE) on each side: flush or touching
-- pieces do not overlap. Separating axes on the ground plane, intervals in height.
function BuildRules.BoxesOverlap(a, b, tolerance: number?): boolean
	local inset = tolerance or BuildRules.OVERLAP_TOLERANCE
	local ay, by = math.max(a.half.Y - inset, 0.01), math.max(b.half.Y - inset, 0.01)
	if math.abs(a.center.Y - b.center.Y) >= ay + by then
		return false
	end
	local function axes(yaw)
		local x1, z1 = BuildRules.ToWorld(1, 0, yaw)
		local x2, z2 = BuildRules.ToWorld(0, 1, yaw)
		return { x1, z1 }, { x2, z2 }
	end
	local ax, az = axes(a.yaw or 0)
	local bx, bz = axes(b.yaw or 0)
	local ahx, ahz = math.max(a.half.X - inset, 0.01), math.max(a.half.Z - inset, 0.01)
	local bhx, bhz = math.max(b.half.X - inset, 0.01), math.max(b.half.Z - inset, 0.01)
	local dx, dz = b.center.X - a.center.X, b.center.Z - a.center.Z
	for _, axis in { ax, az, bx, bz } do
		local function along(v)
			return math.abs(v[1] * axis[1] + v[2] * axis[2])
		end
		local reach = ahx * along(ax) + ahz * along(az) + bhx * along(bx) + bhz * along(bz)
		if math.abs(dx * axis[1] + dz * axis[2]) >= reach then
			return false
		end
	end
	return true
end

-- Aiming at a wall-like face (normal mostly sideways): the point pushed out along
-- the face's horizontal normal far enough that a piece of `size` turned `yaw`
-- stands just clear of it (the ghost then drops to the ground below). Returns nil
-- for floor-like faces, where the piece stands on the point itself.
function BuildRules.OffsetFromFace(point: Vector3, normal: Vector3, size: Vector3, yaw: number): Vector3?
	if normal.Y >= 0.5 then
		return nil
	end
	local length = math.sqrt(normal.X * normal.X + normal.Z * normal.Z)
	if length < 1e-6 then
		return nil
	end
	local nx, nz = normal.X / length, normal.Z / length
	local lx, lz = BuildRules.ToLocal(nx, nz, yaw)
	local reach = math.abs(lx) * size.X / 2 + math.abs(lz) * size.Z / 2 + 0.05
	return Vector3.new(point.X + nx * reach, point.Y, point.Z + nz * reach)
end

-- Where the support rays go down from: the base's centre and its four corners
-- (pulled in by OVERLAP_TOLERANCE so a corner flush with a wall still finds it).
function BuildRules.SupportPoints(base: Vector3, half: Vector3, yaw: number)
	local points = { base }
	local hx = math.max(half.X - BuildRules.OVERLAP_TOLERANCE, 0)
	local hz = math.max(half.Z - BuildRules.OVERLAP_TOLERANCE, 0)
	for _, corner in { { -1, -1 }, { 1, -1 }, { -1, 1 }, { 1, 1 } } do
		local x, z = BuildRules.ToWorld(corner[1] * hx, corner[2] * hz, yaw)
		table.insert(points, base + Vector3.new(x, 0, z))
	end
	return points
end

-- Whether the base is held up, from one sample per SupportPoints point (the
-- centre first): {drop = studs from the base down to what the ray hit (negative
-- when it is above the base), normalY = that surface's normal Y}, or {} when the
-- ray hit nothing. Returns nil when supported, else "NoGround" or "TooSteep".
-- The slope is read where the piece rests: its centre when that is supported,
-- else the first supported corner.
function BuildRules.SupportVerdict(samples): string?
	local resting = nil
	for _, sample in samples do
		local drop = sample.drop
		if drop ~= nil and drop >= -BuildRules.SUPPORT_PROBE and drop <= BuildRules.SUPPORT_TOLERANCE then
			resting = sample
			break
		end
	end
	if resting == nil then
		return "NoGround"
	end
	local normalY = resting.normalY or 1
	if normalY < math.cos(math.rad(BuildRules.MAX_SLOPE)) - 1e-9 then
		return "TooSteep"
	end
	return nil
end

-- Positions along one axis that line a piece (half-length `own`) up with a
-- neighbour (half-length `other`) centred at 0: beside each face, flush with each
-- edge, and centred.
local function alignments(other: number, own: number)
	return { other + own, -(other + own), other - own, -(other - own), 0 }
end

-- Magnetic snap (§60). `neighbours` are nearby pieces {position (centre), size
-- (own), yaw}. When the piece at `base` (bottom centre, turned `yaw`) comes within
-- SNAP_DISTANCE of a neighbour and is turned like it or at a right angle to it,
-- it slides at most SNAP_DISTANCE per axis so its faces and edges line up: beside
-- it, flush with an edge, centred, or level with its base or top. Arrangements
-- that would sink into the neighbour are skipped; the arrangement aligning the
-- most axes with the least movement wins. Returns (base, yaw, snapped).
function BuildRules.SnapToNeighbours(base: Vector3, yaw: number, size: Vector3, neighbours): (Vector3, number, boolean)
	local limit = BuildRules.SNAP_DISTANCE
	local best, bestScore = nil, nil
	for _, other in neighbours do
		local otherYaw = other.yaw or 0
		local relative = (yaw - otherYaw) % 360
		local turns = math.round(relative / 90)
		if math.abs(relative - turns * 90) > 0.01 then
			continue
		end
		local alignedYaw = (otherYaw + turns * 90) % 360
		local ownX, ownZ = size.X / 2, size.Z / 2
		if turns % 2 == 1 then
			ownX, ownZ = ownZ, ownX
		end
		local otherHalf = other.size / 2
		local x, z = BuildRules.ToLocal(base.X - other.position.X, base.Z - other.position.Z, otherYaw)
		local gapX = math.max(math.abs(x) - (otherHalf.X + ownX), 0)
		local gapZ = math.max(math.abs(z) - (otherHalf.Z + ownZ), 0)
		if gapX > limit or gapZ > limit then
			continue
		end
		-- Height: level with the neighbour's base or standing on its top.
		local bottom, top = other.position.Y - otherHalf.Y, other.position.Y + otherHalf.Y
		local y = base.Y
		local levelled = false
		local level = if math.abs(y - bottom) <= math.abs(y - top) then bottom else top
		if math.abs(y - level) <= limit then
			y, levelled = level, true
		end
		local stacked = y >= top - BuildRules.OVERLAP_TOLERANCE or y + size.Y <= bottom + BuildRules.OVERLAP_TOLERANCE
		local xs, zs = { x }, { z }
		for _, value in alignments(otherHalf.X, ownX) do
			if math.abs(value - x) <= limit then
				table.insert(xs, value)
			end
		end
		for _, value in alignments(otherHalf.Z, ownZ) do
			if math.abs(value - z) <= limit then
				table.insert(zs, value)
			end
		end
		for xi, sx in xs do
			for zi, sz in zs do
				local count = (if xi > 1 then 1 else 0) + (if zi > 1 then 1 else 0) + (if levelled then 0.5 else 0)
				if count < 1 then
					continue
				end
				local reachX, reachZ = otherHalf.X + ownX, otherHalf.Z + ownZ
				local tolerance = BuildRules.OVERLAP_TOLERANCE
				local withinX = math.abs(sx) < reachX - tolerance
				local withinZ = math.abs(sz) < reachZ - tolerance
				if withinX and withinZ and not stacked then
					continue
				end
				-- Face to face (beside along one axis, overlapping along the other) or
				-- standing on it beats touching at an edge only.
				local besideX = math.abs(math.abs(sx) - reachX) < 1e-6
				local besideZ = math.abs(math.abs(sz) - reachZ) < 1e-6
				local contact = stacked or (besideX and withinZ) or (besideZ and withinX)
				local moved = math.abs(sx - x) + math.abs(sz - z) + math.abs(y - base.Y)
				local score = count * 100 + (if contact then 50 else 0) - moved
				if bestScore == nil or score > bestScore then
					local wx, wz = BuildRules.ToWorld(sx, sz, otherYaw)
					best = { Vector3.new(other.position.X + wx, y, other.position.Z + wz), alignedYaw }
					bestScore = score
				end
			end
		end
	end
	if best then
		return best[1], best[2], true
	end
	return base, yaw, false
end

-- The tiers a piece comes in, in ladder order: every StructureCatalog tier for
-- walls, floors, doors and roofs; the one tier of furniture and stations.
function BuildRules.TiersOf(pieceId: string): { string }
	local piece = StructureCatalog.Pieces[pieceId]
	local list = {}
	for _, tier in StructureCatalog.TIERS do
		if piece and piece.tiers[tier] then
			table.insert(list, tier)
		end
	end
	return list
end

function BuildRules.IsTiered(pieceId: string): boolean
	return #BuildRules.TiersOf(pieceId) > 1
end

-- The tier to build `pieceId` in when the player picked `wanted`: that tier when
-- the piece comes in it, otherwise the piece's lowest tier.
function BuildRules.TierFor(pieceId: string, wanted: string?): string?
	local tiers = BuildRules.TiersOf(pieceId)
	return if table.find(tiers, wanted) then wanted else tiers[1]
end

-- The tier `delta` steps from `tier` along the piece's tiers, wrapping round.
function BuildRules.CycleTier(pieceId: string, tier: string, delta: number): string?
	local tiers = BuildRules.TiersOf(pieceId)
	if #tiers == 0 then
		return nil
	end
	local index = table.find(tiers, tier) or 1
	return tiers[(index - 1 + delta) % #tiers + 1]
end

return BuildRules
