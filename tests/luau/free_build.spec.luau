-- Free placement (GDD §60): yaw parsing and request sanity, world bounds, turned
-- footprints, overlap between oriented pieces, support and slope, the face
-- offset and the magnetic snap.

local Shared = game:GetService("ReplicatedStorage").Shared
local Server = game:GetService("ServerScriptService").Server
local BuildRules = require(Shared.Building.BuildRules)
local IslandLayout = require(Server.Rules.World.IslandLayout)

local WALL = Vector3.new(8, 8, 1)
local FLOOR = Vector3.new(8, 1, 8)

local function box(x, y, z, size, yaw)
	return { center = Vector3.new(x, y, z), half = size / 2, yaw = yaw or 0 }
end

local function piece(x, y, z, size, yaw)
	return { position = Vector3.new(x, y, z), size = size, yaw = yaw or 0 }
end

local function near(a: Vector3, b: Vector3, tolerance: number?): boolean
	return (a - b).Magnitude <= (tolerance or 1e-6)
end

test("a yaw is a finite ROTATE_STEP multiple, normalised to [0, 360)", function()
	expectEq(BuildRules.ROTATE_STEP, 15, "15° steps")
	expectEq(BuildRules.ParseYaw(0), 0, "zero")
	expectEq(BuildRules.ParseYaw(45), 45, "a step multiple")
	expectEq(BuildRules.ParseYaw(-15), 345, "negative wraps")
	expectEq(BuildRules.ParseYaw(375), 15, "past a full turn wraps")
	expectEq(BuildRules.ParseYaw(360), 0, "a full turn is zero")
	expectEq(BuildRules.ParseYaw(30.0000001), 30, "float dust is forgiven")
	expectEq(BuildRules.ParseYaw(7), nil, "off-step angles are refused")
	expectEq(BuildRules.ParseYaw(0 / 0), nil, "NaN")
	expectEq(BuildRules.ParseYaw(math.huge), nil, "infinity")
	expectEq(BuildRules.ParseYaw(-math.huge), nil, "minus infinity")
	expectEq(BuildRules.ParseYaw(1e9), nil, "absurdly large")
	expectEq(BuildRules.ParseYaw("15"), nil, "a string")
	expectEq(BuildRules.ParseYaw(nil), nil, "missing")
	expectEq(BuildRules.ParseYaw({}), nil, "a table")
	expectEq(BuildRules.Turn(345, 1), 0, "turning wraps forward")
	expectEq(BuildRules.Turn(0, -1), 345, "and back")
end)

test("positions must be finite and inside the build area", function()
	expect(BuildRules.FiniteVector(Vector3.new(1, 2, 3)), "plain")
	expect(not BuildRules.FiniteVector(Vector3.new(0 / 0, 0, 0)), "NaN X")
	expect(not BuildRules.FiniteVector(Vector3.new(0, math.huge, 0)), "infinite Y")
	expect(not BuildRules.FiniteVector(nil), "missing")
	expectEq(BuildRules.WORLD_HALF, IslandLayout.BUILD_HALF, "the island's lattice")
	expect(BuildRules.InWorld(Vector3.new(100, 30, -200)), "on the island")
	expect(BuildRules.InWorld(Vector3.new(BuildRules.WORLD_HALF, 0, -BuildRules.WORLD_HALF)), "the corner")
	expect(not BuildRules.InWorld(Vector3.new(BuildRules.WORLD_HALF + 1, 0, 0)), "past the edge")
	expect(not BuildRules.InWorld(Vector3.new(0, BuildRules.WORLD_MIN_Y - 1, 0)), "under the sea floor")
	expect(not BuildRules.InWorld(Vector3.new(0, BuildRules.WORLD_MAX_Y + 1, 0)), "in the sky")
	expect(not BuildRules.InWorld(Vector3.new(0 / 0, 0, 0)), "NaN is never in the world")
end)

test("turning matches CFrame.Angles(0, yaw, 0) and footprints follow it", function()
	local x, z = BuildRules.ToWorld(1, 0, 90)
	expect(math.abs(x) < 1e-9 and math.abs(z + 1) < 1e-9, "local +X turns to world -Z at 90°")
	local wx, wz = BuildRules.ToWorld(3, -2, 75)
	local lx, lz = BuildRules.ToLocal(wx, wz, 75)
	expectNear(lx, 3, 1e-9, "round trip X")
	expectNear(lz, -2, 1e-9, "round trip Z")
	local straight = BuildRules.HalfExtents(WALL, 0)
	expect(straight == Vector3.new(4, 4, 0.5), "unturned: the piece's own half-size")
	local quarter = BuildRules.HalfExtents(WALL, 90)
	expect(quarter == Vector3.new(0.5, 4, 4), "a quarter turn swaps the sides exactly")
	local diagonal = BuildRules.HalfExtents(WALL, 45)
	expectNear(diagonal.X, 4.5 * math.sqrt(0.5), 1e-9, "45°: the box around it")
	expectNear(diagonal.Z, diagonal.X, 1e-9, "45°: square")
	-- Facing: yaw 0 looks down -Z, yaw 90 down -X.
	expectEq(BuildRules.YawFromLook(Vector3.new(0, 0, -1)), 0, "facing -Z")
	expectEq(BuildRules.YawFromLook(Vector3.new(-1, 0, 0)), 90, "facing -X")
	expectEq(BuildRules.YawFromLook(Vector3.new(0.26, 0, -0.97)), 345, "rounded to a step")
	expectEq(BuildRules.YawFromLook(Vector3.new(0, -1, 0)), 0, "straight down")
	-- Distances and containment use the turned footprint, not the box around it.
	local own = WALL / 2
	expectNear(BuildRules.HorizontalDistance(Vector3.new(0, 0, 3), Vector3.zero, own, 0), 2.5, 1e-9, "beside")
	expectNear(BuildRules.HorizontalDistance(Vector3.new(0, 0, 3), Vector3.zero, own, 90), 0, 1e-9, "turned onto it")
	expect(BuildRules.InFootprint(Vector3.new(0, 1, 3.5), Vector3.zero, own, 90), "inside when turned")
	expect(not BuildRules.InFootprint(Vector3.new(0, 1, 3.5), Vector3.zero, own, 0), "outside unturned")
end)

test("pieces may touch but not overlap, by their turned shapes", function()
	expect(not BuildRules.BoxesOverlap(box(0, 4, 0, WALL), box(8, 4, 0, WALL)), "end to end, flush")
	expect(not BuildRules.BoxesOverlap(box(0, 4, 0, WALL), box(0, 4, 1, WALL)), "side by side, flush")
	expect(not BuildRules.BoxesOverlap(box(0, 4, 0, WALL), box(7.8, 4, 0, WALL)), "within the tolerance")
	expect(BuildRules.BoxesOverlap(box(0, 4, 0, WALL), box(7, 4, 0, WALL)), "a stud into each other")
	expect(BuildRules.BoxesOverlap(box(0, 4, 0, WALL), box(0, 4, 0, WALL, 90)), "crossed")
	expect(not BuildRules.BoxesOverlap(box(0, 4, 0, WALL), box(0, 12, 0, WALL)), "stacked on top")
	expect(not BuildRules.BoxesOverlap(box(0, 0.5, 0, FLOOR), box(0, 5, 3.5, WALL)), "a wall standing on a floor")
	-- A 45° wall whose surrounding box reaches another wall, though the wall itself does not.
	local d = 4.5 * math.sqrt(0.5)
	expect(2 * BuildRules.HalfExtents(WALL, 45).X > d + 0.4, "the world-aligned boxes around them overlap")
	expect(
		not BuildRules.BoxesOverlap(box(0, 4, 0, WALL, 45), box(d + 0.4, 4, d + 0.4, WALL, 45)),
		"parallel diagonal walls do not"
	)
	expect(
		BuildRules.BoxesOverlap(box(0, 4, 0, WALL, 45), box(2, 4, 0, WALL, 0)),
		"a diagonal crossing a straight wall"
	)
	expect(BuildRules.BoxesOverlap(box(0, 4, 0, WALL), box(0, 4, 0.6, WALL), 0.1), "a tighter tolerance")
end)

test("a piece needs support close below its base, on ground that is not too steep", function()
	expectEq(BuildRules.SupportVerdict({ {}, {}, {}, {}, {} }), "NoGround", "nothing below")
	expectEq(BuildRules.SupportVerdict({ { drop = 0, normalY = 1 } }), nil, "flush on flat ground")
	expectEq(BuildRules.SupportVerdict({ {}, {}, { drop = 1, normalY = 1 }, {}, {} }), nil, "one corner on a wall top")
	expectEq(
		BuildRules.SupportVerdict({ { drop = 2, normalY = 1 }, {}, {}, {}, {} }),
		"NoGround",
		"floating 2 studs up"
	)
	expectEq(BuildRules.SupportVerdict({ { drop = -1, normalY = 1 } }), nil, "sunk a stud into a slope")
	local steep = math.cos(math.rad(BuildRules.MAX_SLOPE + 10))
	local gentle = math.cos(math.rad(BuildRules.MAX_SLOPE - 10))
	expectEq(BuildRules.SupportVerdict({ { drop = 0, normalY = steep } }), "TooSteep", "a cliff")
	expectEq(BuildRules.SupportVerdict({ { drop = 0, normalY = gentle } }), nil, "a gentle slope")
	expectEq(
		BuildRules.SupportVerdict({ { drop = 0.5, normalY = 1 }, { drop = 0, normalY = steep } }),
		nil,
		"the slope is read where the centre rests"
	)
	local points = BuildRules.SupportPoints(Vector3.new(10, 5, 0), WALL / 2, 90)
	expectEq(#points, 5, "centre and four corners")
	expect(points[1] == Vector3.new(10, 5, 0), "the centre first")
	for index = 2, 5 do
		local offset = points[index] - points[1]
		expectNear(math.abs(offset.X), 0.25, 1e-9, "turned: the thin side along X")
		expectNear(math.abs(offset.Z), 3.75, 1e-9, "turned: the long side along Z")
		expectEq(offset.Y, 0, "at the base")
	end
end)

test("aiming at a wall's face puts the piece beside it", function()
	local pushed = BuildRules.OffsetFromFace(Vector3.new(4, 3, 0), Vector3.new(1, 0, 0), WALL, 0)
	expectNear(pushed.X, 8.05, 1e-9, "a wall along X clears the face by its half-length")
	expectEq(pushed.Y, 3, "same height (the ghost then drops to the ground)")
	local turned = BuildRules.OffsetFromFace(Vector3.new(4, 3, 0), Vector3.new(1, 0, 0), WALL, 90)
	expectNear(turned.X, 4.55, 1e-9, "turned, its thin side faces the wall")
	expectEq(BuildRules.OffsetFromFace(Vector3.new(0, 1, 0), Vector3.new(0, 1, 0), WALL, 0), nil, "floors: no push")
end)

test("the magnetic snap lines pieces up and never pulls them into each other", function()
	local neighbour = piece(0, 4, 0, WALL)
	local base, yaw, snapped = BuildRules.SnapToNeighbours(Vector3.new(8.7, 0.4, 0.5), 0, WALL, { neighbour })
	expect(snapped, "close to the end of a wall")
	expect(near(base, Vector3.new(8, 0, 0)), "end to end, level with its base")
	expectEq(yaw, 0, "same turn")

	base, yaw, snapped = BuildRules.SnapToNeighbours(Vector3.new(3.4, 0, 4.3), 90, WALL, { neighbour })
	expect(snapped and near(base, Vector3.new(3.5, 0, 4.5)), "a right angle makes a corner")
	expectEq(yaw, 90, "keeps its right angle")

	base, _, snapped = BuildRules.SnapToNeighbours(Vector3.new(8.7, 0, 0.5), 15, WALL, { neighbour })
	expect(not snapped and near(base, Vector3.new(8.7, 0, 0.5)), "turned off-line it stays free")

	base, _, snapped = BuildRules.SnapToNeighbours(Vector3.new(14, 0, 0), 0, WALL, { neighbour })
	expect(not snapped, "too far away to stick")

	-- Aimed into the middle of the wall: it may slide beside it, never into it.
	base, yaw, snapped = BuildRules.SnapToNeighbours(Vector3.new(2, 0, 0.3), 0, WALL, { neighbour })
	expect(snapped, "lines up beside it")
	expect(
		not BuildRules.BoxesOverlap(box(base.X, base.Y + 4, base.Z, WALL, yaw), box(0, 4, 0, WALL)),
		"and does not overlap it"
	)

	-- A neighbour turned 30°: the snap works in its axes.
	local tilted = piece(10, 4, -6, WALL, 30)
	local ax, az = BuildRules.ToWorld(8.6, 0.3, 30)
	base, yaw, snapped = BuildRules.SnapToNeighbours(Vector3.new(10 + ax, 0, -6 + az), 30, WALL, { tilted })
	local ex, ez = BuildRules.ToWorld(8, 0, 30)
	expect(snapped and near(base, Vector3.new(10 + ex, 0, -6 + ez), 1e-6), "end to end along the turned wall")
	expectEq(yaw, 30, "keeps the shared turn")

	-- Standing on a floor: the wall drops onto its top and lines up with its edge.
	local floor = piece(0, 0.5, 0, FLOOR)
	base, _, snapped = BuildRules.SnapToNeighbours(Vector3.new(0.3, 1.2, 3.2), 0, WALL, { floor })
	expect(snapped and near(base, Vector3.new(0, 1, 3.5)), "on the floor, flush with its edge")

	-- The best of several neighbours wins; nothing nearby leaves the aim alone.
	base, _, snapped =
		BuildRules.SnapToNeighbours(Vector3.new(8.7, 0, 0.5), 0, WALL, { piece(40, 4, 0, WALL), neighbour })
	expect(snapped and near(base, Vector3.new(8, 0, 0)), "the near one")
	base, _, snapped = BuildRules.SnapToNeighbours(Vector3.new(5, 0, 5), 0, WALL, {})
	expect(not snapped and near(base, Vector3.new(5, 0, 5)), "free")
end)
