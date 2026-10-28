-- The play-world island's zones, heights and POIs (GDD §54, owner request 2026-10-28).
local Shared = game:GetService("ReplicatedStorage").Shared
local BiomeCatalog = require(Shared.World.BiomeCatalog)
local CameraRules = require(Shared.World.CameraRules)
local IslandLayout = require(Shared.World.IslandLayout)
local NodeCatalog = require(Shared.Resources.NodeCatalog)
local PoiCatalog = require(Shared.World.PoiCatalog)

local TIERS = { OuterRim = true, InnerRing = true, CenterCrater = true }
local ZONE_TIERS = {
	Rimlands = "OuterRim",
	PinewoodWilds = "OuterRim",
	MosswickForest = "OuterRim",
	Riverlands = "OuterRim",
	Timberwatch = "InnerRing",
	FallenTemple = "InnerRing",
	EmberhollowCaves = "InnerRing",
	FrostpeakRidge = "CenterCrater",
	CraterLake = "CenterCrater",
	ShatteredKeep = "CenterCrater",
}

-- Dry ground samples on a grid over a zone's envelope: {x, z, h}.
local function samples(zoneId: string, step: number)
	local list = {}
	local bounds = BiomeCatalog.Bounds(zoneId)
	for x = bounds.minX, bounds.maxX, step do
		for z = bounds.minZ, bounds.maxZ, step do
			if BiomeCatalog.ZoneAt(x, z) == zoneId and IslandLayout.IsDry(x, z) then
				table.insert(list, { x, z, IslandLayout.HeightAt(x, z) })
			end
		end
	end
	return list
end

test("every zone exists with the interface fields and the owner's danger tier", function()
	expectEq(#BiomeCatalog.ZONE_IDS, 10, "ten zones")
	for _, zoneId in BiomeCatalog.ZONE_IDS do
		local zone = BiomeCatalog.Zones[zoneId]
		assert(zone, zoneId .. " exists")
		expect(type(zone.name) == "string" and #zone.name > 0, zoneId .. " name")
		expect(TIERS[zone.tier], zoneId .. " tier id")
		expectEq(zone.tier, ZONE_TIERS[zoneId], zoneId .. " danger tier")
		expect(#zone.habitats > 0, zoneId .. " habitats")
		for _, habitat in zone.habitats do
			expect(table.find(BiomeCatalog.HABITATS, habitat) ~= nil, zoneId .. " habitat " .. habitat)
		end
		expectEq(
			BiomeCatalog.Regions[zone.tier].risk,
			({
				OuterRim = "Low",
				InnerRing = "Medium",
				CenterCrater = "Extreme",
			})[zone.tier],
			zoneId .. " risk"
		)
	end
	for _, habitat in BiomeCatalog.HABITATS do
		local offered = false
		for _, zone in BiomeCatalog.Zones do
			offered = offered or table.find(zone.habitats, habitat) ~= nil
		end
		expect(offered, habitat .. " is offered somewhere")
	end
end)

test("ZoneAt agrees with each zone's footprint; nil out at sea", function()
	for _, zoneId in BiomeCatalog.ZONE_IDS do
		local x, z = BiomeCatalog.Center(zoneId)
		if zoneId == "CraterLake" then
			-- The Keep island fills the lake's middle; its label sits on open water.
			expectEq(BiomeCatalog.ZoneAt(x, z), "ShatteredKeep", "the Keep is in the lake")
			x, z = BiomeCatalog.Zones.CraterLake.label.x, BiomeCatalog.Zones.CraterLake.label.z
		end
		expectEq(BiomeCatalog.ZoneAt(x, z), zoneId, zoneId .. " at its centre")
		expectEq(BiomeCatalog.RegionAt(x, z), BiomeCatalog.Zones[zoneId].tier, zoneId .. " region")
	end
	local half = BiomeCatalog.ISLAND_SIZE / 2
	for _, corner in { { half, 0 }, { -half, 0 }, { 0, half }, { 0, -half }, { 2600, 2600 } } do
		expectEq(BiomeCatalog.ZoneAt(corner[1], corner[2]), nil, "sea at " .. corner[1] .. "," .. corner[2])
		expect(IslandLayout.HeightAt(corner[1], corner[2]) < 0, "under water at the edge")
	end
	expect(IslandLayout.HeightAt(3000, -3000) < 0, "the ocean reaches the 6,144-stud square")
	-- The coast along a direction does not depend on the direction's length.
	for degrees = 0, 350, 25 do
		local dx, dz = math.cos(math.rad(degrees)), math.sin(math.rad(degrees))
		local coast = BiomeCatalog.CoastRadius(dx, dz)
		expect(math.abs(coast - BiomeCatalog.CoastRadius(dx * 900, dz * 900)) < 0.01, "coast radius at " .. degrees)
		expect(math.abs(BiomeCatalog.CoastDistance(dx * coast, dz * coast)) < 0.01, "the coast is at " .. degrees)
		expect(coast > 1800 and coast < BiomeCatalog.ISLAND_SIZE * 0.6, "coast inside the island square")
	end
	-- Frostpeak is north (−Z), the Rimlands south.
	local _, frostZ = BiomeCatalog.Center("FrostpeakRidge")
	local _, rimZ = BiomeCatalog.Center("Rimlands")
	expect(frostZ < -1000 and rimZ > 1400, "Frostpeak north, Rimlands along the south coast")
end)

test("zone envelopes match the owner's footprints; transitions are shared", function()
	-- Square studs on a 32-stud grid: inside each zone's own envelope, and assigned
	-- to it (envelope plus its share of the transition areas).
	local expected = {
		Rimlands = 3000 * 500,
		PinewoodWilds = 1000 * 1100,
		MosswickForest = 900 * 900,
		EmberhollowCaves = 700 * 700,
		FrostpeakRidge = 1400 * 800,
		FallenTemple = 800 * 800,
		Timberwatch = 800 * 900,
		Riverlands = 1100 * 900,
		CraterLake = math.pi * 700 ^ 2,
		ShatteredKeep = math.pi * 275 * 325,
	}
	local inside, assigned = {}, {}
	local half = BiomeCatalog.ISLAND_SIZE / 2
	for x = -half, half, 32 do
		for z = -half, half, 32 do
			local zoneId = BiomeCatalog.ZoneAt(x, z)
			if zoneId then
				assigned[zoneId] = (assigned[zoneId] or 0) + 32 * 32
			end
			for _, id in BiomeCatalog.ZONE_IDS do
				if BiomeCatalog.EnvelopeDistance(id, x, z) <= 1 then
					inside[id] = (inside[id] or 0) + 32 * 32
				end
			end
		end
	end
	for zoneId, area in expected do
		local own = (inside[zoneId] or 0) / area
		expect(own > 0.85 and own < 1.15, ("%s envelope ratio %.2f"):format(zoneId, own))
		local share = (assigned[zoneId] or 0) / area
		expect(share > 0.6 and share < 2.1, ("%s assigned ratio %.2f"):format(zoneId, share))
	end
end)

test("heights stay within the owner's vertical ranges", function()
	local frostTop, otherTop = 0, 0
	for _, zoneId in BiomeCatalog.ZONE_IDS do
		local heights = {}
		for _, sample in samples(zoneId, 48) do
			table.insert(heights, sample[3])
			expect(sample[3] > 0 and sample[3] <= IslandLayout.MAX_HEIGHT, zoneId .. " height in range")
			if zoneId == "FrostpeakRidge" then
				frostTop = math.max(frostTop, sample[3])
			else
				otherTop = math.max(otherTop, sample[3])
			end
		end
		table.sort(heights)
		local median = heights[#heights // 2 + 1]
		if zoneId ~= "FrostpeakRidge" and zoneId ~= "EmberhollowCaves" and zoneId ~= "ShatteredKeep" then
			expect(median >= 20 and median <= 80, ("%s ordinary land at %.0f"):format(zoneId, median))
		end
	end
	local summit = IslandLayout.Peaks[1]
	frostTop = math.max(frostTop, IslandLayout.HeightAt(summit.x, summit.z))
	expect(frostTop >= 450 and frostTop <= 600, ("Frostpeak's peaks reach %.0f"):format(frostTop))
	expect(otherTop <= 220, ("nothing else rises past the terraces (%.0f)"):format(otherTop))
	-- Elevated terraces sit at 100–220.
	local court = IslandLayout.Courtyard
	local mound, lookout = IslandLayout.TempleMound, IslandLayout.Lookout
	for name, h in
		{
			Keep = IslandLayout.HeightAt(court.x, court.z),
			Temple = IslandLayout.HeightAt(mound.x, mound.z),
			Lookout = IslandLayout.HeightAt(lookout.x, lookout.z),
			CaveHill = IslandLayout.HeightAt(750, 1000),
		}
	do
		expect(h >= 100 and h <= 220, name .. " terrace height")
	end
	expect(IslandLayout.HeightAt(-300, 300) < IslandLayout.LAKE_LEVEL - 10, "the lake is deep water")
	expect(not IslandLayout.IsDry(-300, 300), "Crater Lake is wet")
end)

test("the Keep is reached across the lake by a land bridge and a ford", function()
	local level = IslandLayout.LAKE_LEVEL
	for z = 240, 480, 20 do
		expect(IslandLayout.IsDry(0, z), "the bridge stays dry at z " .. z)
		expect(IslandLayout.HeightAt(0, z) - level < 8, "the bridge stays low")
	end
	for x = 300, 580, 20 do
		local depth = level - IslandLayout.HeightAt(x, -100)
		expect(depth < 2.5, "the ford stays shallow at x " .. x)
	end
end)

-- The steepest rise per stud along a polyline (4-stud steps), and whether all of it
-- is dry ground.
local function walk(points)
	local worst, dry = 0, true
	for index = 2, #points do
		local a, b = points[index - 1], points[index]
		local steps = math.max(1, math.floor((b - a).Magnitude / 4))
		for step = 0, steps - 1 do
			local p, q = a + (b - a) * (step / steps), a + (b - a) * ((step + 1) / steps)
			local rise = math.abs(IslandLayout.HeightAt(q.X, q.Z) - IslandLayout.HeightAt(p.X, p.Z))
			worst = math.max(worst, rise / (q - p).Magnitude)
			dry = dry and IslandLayout.IsDry(q.X, q.Z)
		end
	end
	return worst, dry
end

test("walkable paths lead from the bridge and ford to the courtyard, portal and altars", function()
	local MAX_RISE = 0.7
	local function at(x, z)
		return Vector3.new(x, 0, z)
	end
	local portal, west, north
	for _, entry in PoiCatalog.Portals do
		if entry.kind == "Center" then
			portal = at(entry.x, entry.z)
		end
	end
	for _, site in PoiCatalog.RitualSites do
		if site.id == "KeepWestAltar" then
			west = at(site.x, site.z)
		elseif site.id == "KeepNorthAltar" then
			north = at(site.x, site.z)
		end
	end
	local court = IslandLayout.Courtyard
	local gate = at(court.x, court.z + court.halfZ)
	local paths = {
		-- Up the ramp from the land bridge to the courtyard's south gate.
		ramp = { at(0, 420), gate },
		bridgeToPortal = { at(0, 240), at(70, 200), portal },
		portalToFordToNorthAltar = { portal, at(230, 0), at(270, -100), at(215, -215), north },
		ford = { at(600, -100), at(270, -100) },
		bridgeToWestAltar = { at(0, 240), at(-90, 200), at(-190, 110), west },
		templeRamp = {
			at(IslandLayout.TempleMound.x, IslandLayout.TempleMound.z + 220),
			at(IslandLayout.TempleMound.x, IslandLayout.TempleMound.z),
		},
	}
	for name, points in paths do
		local worst, dry = walk(points)
		expect(worst <= MAX_RISE, ("%s rises %.2f per stud at worst"):format(name, worst))
		if name ~= "ford" then
			expect(dry, name .. " stays dry")
		end
	end
	expect(IslandLayout.HeightAt(gate.X, gate.Z) >= IslandLayout.KEEP_HEIGHT - 1, "the gate is on the plateau")
end)

test("the river runs from the lake to the sea in a contained channel", function()
	for _, river in IslandLayout.Rivers do
		for index = 2, #river.points do
			local a, b = river.points[index - 1], river.points[index]
			for t = 0.1, 0.9, 0.2 do
				local p = a + (b - a) * t
				if BiomeCatalog.CoastDistance(p.X, p.Z) > 40 and not IslandLayout.InCaveInterior(p.X, p.Z) then
					expect(not IslandLayout.IsDry(p.X, p.Z), river.id .. " has water")
					local direction = (b - a) / (b - a).Magnitude
					local info = IslandLayout.RiverAt(p.X, p.Z)
					local bank = info.halfWidth + 6
					local side = Vector3.new(-direction.Z, 0, direction.X) * bank
					local left, right = p + side, p - side
					expect(IslandLayout.HeightAt(left.X, left.Z) > info.surface, river.id .. " left bank holds")
					expect(IslandLayout.HeightAt(right.X, right.Z) > info.surface, river.id .. " right bank holds")
				end
			end
		end
	end
end)

test("portals, camps, altars and the arena sit on dry ground in the right tier", function()
	local counts = { OuterRim = 0, InnerRing = 0, CenterCrater = 0 }
	local centers = 0
	for _, portal in PoiCatalog.Portals do
		expect(type(portal.zoneRadius) == "number" and portal.zoneRadius > 0, portal.id .. " radius")
		expect(IslandLayout.IsDry(portal.x, portal.z), portal.id .. " on dry ground")
		expect(IslandLayout.SlopeAt(portal.x, portal.z) < 0.3, portal.id .. " on level ground")
		local region = PoiCatalog.RegionOf(portal)
		expect(region ~= nil, portal.id .. " on the island")
		counts[region] += 1
		if portal.kind == "Center" then
			centers += 1
			expectEq(PoiCatalog.ZoneOf(portal), "ShatteredKeep", "the Center portal is on the Keep island")
		end
	end
	expectEq(centers, 1, "one Center portal")
	expectEq(counts.OuterRim, 4, "3 Low + 1 hidden")
	expectEq(counts.InnerRing, 3, "3 Medium")
	expectEq(counts.CenterCrater, 1, "only the Center in the Extreme tier")
	expect(#PoiCatalog.SafeZones >= 2, "two trading camps")
	for _, zone in PoiCatalog.SafeZones do
		expect(zone.radius > 0, zone.id .. " volume")
		expectEq(PoiCatalog.RegionOf(zone), "OuterRim", zone.id .. " in a Low zone")
		expect(IslandLayout.IsDry(zone.x, zone.z), zone.id .. " on dry ground")
	end
	expectEq(
		PoiCatalog.ZoneOf(PoiCatalog.SafeZones[1]) ~= PoiCatalog.ZoneOf(PoiCatalog.SafeZones[2]),
		true,
		"camps apart"
	)
	for _, site in PoiCatalog.RitualSites do
		expectEq(PoiCatalog.ZoneOf(site), "ShatteredKeep", site.id .. " at the Keep")
		expect(IslandLayout.IsDry(site.x, site.z), site.id .. " on dry ground")
	end
	local arena = PoiCatalog.GuardianArena
	expectEq(PoiCatalog.ZoneOf(arena), "ShatteredKeep", "the Guardian fights on the Keep island")
	local court = IslandLayout.Courtyard
	expect(arena.x == court.x and arena.z == court.z, "in the Keep's courtyard")
	expectEq(court.halfX * 2, 180, "courtyard 180 wide")
	expectEq(court.halfZ * 2, 220, "courtyard 220 deep")
	for _, portal in PoiCatalog.Portals do
		local gap = math.sqrt((portal.x - arena.x) ^ 2 + (portal.z - arena.z) ^ 2)
		expect(gap > arena.radius + portal.zoneRadius, portal.id .. " outside the arena")
	end
	for _, landmark in PoiCatalog.Landmarks do
		expect(PoiCatalog.ZoneOf(landmark) ~= nil, landmark.id .. " on the island")
		if landmark.style ~= "Bridge" then
			expect(IslandLayout.IsDry(landmark.x, landmark.z), landmark.id .. " on dry ground")
		end
	end
end)

test("spawn candidates are spread over Low and Medium zones on dry ground", function()
	local seen = {}
	local candidates = IslandLayout.SpawnCandidates()
	expect(#candidates >= 30, "plenty of candidates")
	for _, position in candidates do
		local zoneId = BiomeCatalog.ZoneAt(position.X, position.Z)
		expect(zoneId ~= nil, "on the island")
		if zoneId then
			seen[zoneId] = true
			expect(BiomeCatalog.Zones[zoneId].tier ~= "CenterCrater", zoneId .. " is not Extreme")
		end
		expect(IslandLayout.IsDry(position.X, position.Z), "dry ground")
		expect(math.abs(position.Y - IslandLayout.HeightAt(position.X, position.Z)) < 0.01, "on the ground")
		expect(not IslandLayout.KeepOut(position.X, position.Z), "outside camps and structures")
	end
	for _, zoneId in BiomeCatalog.ZONE_IDS do
		if BiomeCatalog.Zones[zoneId].tier ~= "CenterCrater" then
			expect(seen[zoneId], zoneId .. " has spawn candidates")
		end
	end
end)

test("RandomPointIn finds dry standing ground in the zone and habitat", function()
	local rng = Random.new(7)
	for _, zoneId in BiomeCatalog.ZONE_IDS do
		local zone = BiomeCatalog.Zones[zoneId]
		local options = { false, "NotAHabitat" }
		for _, habitat in zone.habitats do
			table.insert(options, habitat)
		end
		for _, habitat in options do
			local found = 0
			for _ = 1, 20 do
				local point = IslandLayout.RandomPointIn(zoneId, rng, habitat or nil)
				if point then
					found += 1
					local label = zoneId .. " " .. tostring(habitat)
					if habitat == "Cave" then
						expect(IslandLayout.InCaveInterior(point.X, point.Z), label .. " inside the cave")
						local floor = zone.interior.floor
						expect(math.abs(point.Y - floor - IslandLayout.STAND_HEIGHT) < 0.01, label .. " on the floor")
					else
						expectEq(BiomeCatalog.ZoneAt(point.X, point.Z), zoneId, label .. " in the zone")
						expect(IslandLayout.IsDry(point.X, point.Z), label .. " on dry ground")
						expect(not IslandLayout.KeepOut(point.X, point.Z), label .. " outside camps")
						local ground = IslandLayout.HeightAt(point.X, point.Z)
						expect(math.abs(point.Y - ground - IslandLayout.STAND_HEIGHT) < 0.01, label .. " standing")
						if habitat and habitat ~= "NotAHabitat" then
							expect(IslandLayout.HabitatMatches(habitat, zoneId, point.X, point.Z), label .. " habitat")
						end
					end
				end
			end
			expect(found >= 15, ("%s %s found %d/20"):format(zoneId, tostring(habitat), found))
		end
	end
	expectEq(IslandLayout.RandomPointIn("FrostpeakRidge", rng, "Beach"), nil, "a habitat the zone lacks finds nothing")
	expectEq(IslandLayout.RandomPointIn("Atlantis", rng), nil, "an unknown zone finds nothing")
end)

test("every zone has a pool with the basics; ores follow danger", function()
	local ores = {
		CopperDeposit = "OuterRim",
		IronDeposit = "OuterRim",
		SilverDeposit = "InnerRing",
		CobaltDeposit = "InnerRing",
		ObsidianOutcrop = "InnerRing",
		JadeVein = "InnerRing",
		MithrilDeposit = "CenterCrater",
	}
	for _, zoneId in BiomeCatalog.ZONE_IDS do
		local zone = BiomeCatalog.Zones[zoneId]
		for _, basic in { "Tree", "Rock", "FiberPlant", "HerbShrub", "RedberryBush", "SweetberryBush" } do
			expect((zone.resources[basic] or 0) > 0, zoneId .. " has " .. basic)
		end
		local hasOre = false
		for nodeType, count in zone.resources do
			expect(NodeCatalog.Nodes[nodeType] ~= nil, zoneId .. " node " .. nodeType)
			expect(count > 0, zoneId .. " " .. nodeType .. " count")
			expect(not nodeType:find("Adamantine"), "no regrowing Adamantine in " .. zoneId)
			if ores[nodeType] then
				hasOre = true
				expectEq(zone.tier, ores[nodeType], nodeType .. " only in its tier (" .. zoneId .. ")")
			end
		end
		expect(hasOre, zoneId .. " has its tier's ore")
	end
	expect(BiomeCatalog.Zones.FrostpeakRidge.resources.FrostShrub > 0, "frost shrubs on Frostpeak")
	for nodeType, prefer in BiomeCatalog.NodeHabitats do
		expect(NodeCatalog.Nodes[nodeType] ~= nil, "habitat preference for a real node " .. nodeType)
		for _, habitat in prefer.habitats do
			expect(table.find(BiomeCatalog.HABITATS, habitat) ~= nil, nodeType .. " prefers " .. habitat)
		end
	end
end)

test("camera zoom stays within fair bounds", function()
	expectEq(CameraRules.Clamp(100), CameraRules.MAX_ZOOM, "max")
	expectEq(CameraRules.Clamp(1), CameraRules.MIN_ZOOM, "min")
	expectEq(CameraRules.Clamp(nil), CameraRules.DEFAULT_ZOOM, "default")
	expectEq(CameraRules.MIN_ZOOM, 8, "8 studs")
	expectEq(CameraRules.MAX_ZOOM, 40, "40 studs")
end)
