-- Named points of interest on the Shattered Crater (GDD §3.2, Q22, Q33, Q160a),
-- given as polar positions (degrees, studs from the centre) so gameplay reads the
-- map without hard-coded coordinates. Placeholders until the authored island.

local BiomeCatalog = require(script.Parent.BiomeCatalog)

local PoiCatalog = {}

-- Fixed portal candidates: 3 Outer, 3 Inner, 1 Center, 1 hidden (each server
-- activates a different subset, the Center always on).
PoiCatalog.Portals = {
	{ id = "DriftwoodCove", name = "Driftwood Cove", angle = 30, distance = 920, kind = "Fixed", zoneRadius = 12 },
	{ id = "SaltCliffs", name = "Salt Cliffs", angle = 150, distance = 900, kind = "Fixed", zoneRadius = 12 },
	{ id = "ElderGrove", name = "Elder Grove", angle = 280, distance = 880, kind = "Fixed", zoneRadius = 12 },
	{ id = "JadeSteps", name = "Jade Steps", angle = 95, distance = 540, kind = "Fixed", zoneRadius = 10 },
	{ id = "BoneHollow", name = "Bone Hollow", angle = 215, distance = 520, kind = "Fixed", zoneRadius = 10 },
	{ id = "VineGate", name = "Vine Gate", angle = 335, distance = 560, kind = "Fixed", zoneRadius = 10 },
	{ id = "CraterHeart", name = "Crater Heart", angle = 0, distance = 120, kind = "Center", zoneRadius = 8 },
	{
		id = "SunkenShrine",
		name = "Sunken Shrine",
		angle = 200,
		distance = 1120,
		kind = "Fixed",
		zoneRadius = 10,
		hidden = true,
	},
}

-- Safe POIs (Q160a): two Outer Rim trading camps. Radius in studs.
PoiCatalog.SafeZones = {
	{ id = "EastCamp", name = "Tidewater Camp", angle = 75, distance = 980, radius = 30 },
	{ id = "WestCamp", name = "Ashfall Camp", angle = 255, distance = 980, radius = 30 },
}

PoiCatalog.RitualSites = {
	{ id = "NorthAltar", name = "North Altar", angle = 0, distance = 610 },
	{ id = "SouthAltar", name = "South Altar", angle = 180, distance = 610 },
}

PoiCatalog.GuardianArena = { angle = 0, distance = 0, radius = 80 }

-- Landmarks for navigation without a minimap.
PoiCatalog.Landmarks = {
	{ id = "GiantRoots", name = "Giant Roots", angle = 120, distance = 860, style = "Roots" },
	{ id = "OldRuins", name = "Old Ruins", angle = 320, distance = 960, style = "Ruins" },
	{ id = "Monoliths", name = "The Monoliths", angle = 40, distance = 560, style = "Monoliths" },
	{ id = "JadeFalls", name = "Jade Falls", angle = 260, distance = 470, style = "Jade" },
	{ id = "VolcanicRidge", name = "Volcanic Ridge", angle = 0, distance = 300, style = "Ridge" },
}

-- Route gaps through the volcanic ridge (degrees).
PoiCatalog.RidgeGaps = { 45, 135, 225, 315 }

-- Spread-out spawn candidates in every region (Q33); the server still filters
-- them for crowding at spawn time.
function PoiCatalog.SpawnCandidates()
	local list = {}
	local rings = { { 980, 12 }, { 600, 9 }, { 420, 6 }, { 180, 4 } }
	for ringIndex, ring in rings do
		local distance, count = ring[1], ring[2]
		for index = 1, count do
			table.insert(list, { angle = (index / count) * 360 + ringIndex * 11, distance = distance })
		end
	end
	return list
end

-- World position (y = 0) of a polar POI.
function PoiCatalog.Position(poi): Vector3
	local radians = math.rad(poi.angle)
	return Vector3.new(math.cos(radians) * poi.distance, 0, math.sin(radians) * poi.distance)
end

function PoiCatalog.RegionOf(poi): string?
	return BiomeCatalog.RegionAt(poi.distance)
end

return PoiCatalog
