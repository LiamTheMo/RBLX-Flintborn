local Shared = game:GetService("ReplicatedStorage").Shared
local BiomeCatalog = require(Shared.World.BiomeCatalog)
local CameraRules = require(Shared.World.CameraRules)
local IslandLayout = require(Shared.World.IslandLayout)
local NodeCatalog = require(Shared.Resources.NodeCatalog)
local PoiCatalog = require(Shared.World.PoiCatalog)

test("every portal POI has an authored zone radius and sits inside its region", function()
	local counts = { OuterRim = 0, InnerRing = 0, CenterCrater = 0 }
	local centers = 0
	for _, portal in PoiCatalog.Portals do
		expect(type(portal.zoneRadius) == "number" and portal.zoneRadius > 0, portal.id .. " radius")
		local region = PoiCatalog.RegionOf(portal)
		expect(region ~= nil, portal.id .. " inside the island")
		counts[region] += 1
		if portal.kind == "Center" then
			centers += 1
			expectEq(region, "CenterCrater", "the Center portal is in the crater")
		end
	end
	expectEq(centers, 1, "one Center portal")
	expectEq(counts.OuterRim, 4, "3 Outer + 1 hidden")
	expectEq(counts.InnerRing, 3, "3 Inner")
end)

test("every biome has a resource pool; jade and obsidian only in the Inner Ring", function()
	for name, biome in BiomeCatalog.Biomes do
		local total = 0
		for nodeType, count in biome.resources do
			expect(NodeCatalog.Nodes[nodeType] ~= nil, name .. " node " .. nodeType)
			total += count
			if nodeType == "JadeVein" or nodeType == "ObsidianOutcrop" then
				expectEq(biome.region, "InnerRing", nodeType .. " only in the Inner Ring")
			end
		end
		expect(total > 0, name .. " has resources")
	end
end)

test("every safe zone has a volume and lies in the Outer Rim", function()
	expect(#PoiCatalog.SafeZones >= 2, "two trading camps")
	for _, zone in PoiCatalog.SafeZones do
		expect(zone.radius > 0, zone.id .. " volume")
		expectEq(PoiCatalog.RegionOf(zone), "OuterRim", zone.id .. " region")
	end
end)

test("spawn candidates exist in all three regions", function()
	local seen = {}
	for _, candidate in PoiCatalog.SpawnCandidates() do
		local region = BiomeCatalog.RegionAt(candidate.distance)
		expect(region ~= nil, "on the island")
		seen[region] = true
	end
	expect(seen.OuterRim and seen.InnerRing and seen.CenterCrater, "all three regions")
end)

test("the island rises from the beach to a ridge with route gaps around the caldera", function()
	expect(IslandLayout.HeightAt(1300, 0) < 0, "sea outside the island")
	expect(IslandLayout.HeightAt(1100, 0) > 0, "beach above the sea")
	local ridge = IslandLayout.HeightAt(300, 0)
	local gapAngle = math.rad(PoiCatalog.RidgeGaps[1])
	local gap = IslandLayout.HeightAt(math.cos(gapAngle) * 300, math.sin(gapAngle) * 300)
	expect(ridge > 30, "the ridge stands tall")
	expect(gap < 30, "routes cut through it")
	expect(IslandLayout.HeightAt(0, 0) < ridge, "the caldera is an open bowl")
end)

test("camera zoom stays within fair bounds", function()
	expectEq(CameraRules.Clamp(100), CameraRules.MAX_ZOOM, "max")
	expectEq(CameraRules.Clamp(1), CameraRules.MIN_ZOOM, "min")
	expectEq(CameraRules.Clamp(nil), CameraRules.DEFAULT_ZOOM, "default")
	expectEq(CameraRules.MIN_ZOOM, 8, "8 studs")
	expectEq(CameraRules.MAX_ZOOM, 40, "40 studs")
end)
