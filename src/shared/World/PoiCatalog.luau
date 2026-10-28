-- Named points of interest on the play-world island (GDD §3.2, Q22, Q33, Q160a,
-- §54), given as world X/Z (−Z north) so gameplay reads the map without hard-coded
-- coordinates. Placeholders until the authored island.

local BiomeCatalog = require(script.Parent.BiomeCatalog)

local PoiCatalog = {}

-- Fixed portal candidates: 3 in Low zones, 3 in Medium zones, the Center on the
-- Keep island and 1 hidden (each server activates a different subset, the Center
-- always on).
PoiCatalog.Portals = {
	{ id = "DriftwoodCove", name = "Driftwood Cove", x = 300, z = 1720, kind = "Fixed", zoneRadius = 12 },
	{ id = "ElderGrove", name = "Elder Grove", x = -1350, z = -900, kind = "Fixed", zoneRadius = 12 },
	{ id = "ReedFerry", name = "Reed Ferry", x = 1550, z = 0, kind = "Fixed", zoneRadius = 12 },
	{ id = "LookoutGate", name = "Lookout Gate", x = -1130, z = 400, kind = "Fixed", zoneRadius = 10 },
	{ id = "TempleSteps", name = "Temple Steps", x = -560, z = 1150, kind = "Fixed", zoneRadius = 10 },
	{ id = "EmberGate", name = "Ember Gate", x = 900, z = 1320, kind = "Fixed", zoneRadius = 10 },
	{ id = "CraterHeart", name = "Crater Heart", x = 130, z = 150, kind = "Center", zoneRadius = 8 },
	{
		id = "SunkenShrine",
		name = "Sunken Shrine",
		x = 1600,
		z = -1350,
		kind = "Fixed",
		zoneRadius = 10,
		hidden = true,
	},
}

-- Safe POIs (Q160a): two trading camps in Low zones. Radius in studs.
PoiCatalog.SafeZones = {
	{ id = "TidewaterCamp", name = "Tidewater Camp", x = -450, z = 1720, radius = 30 },
	{ id = "MossfireCamp", name = "Mossfire Camp", x = 1450, z = -850, radius = 30 },
}

-- The Minotaur's altars stand on the Keep island's lower terrace (GDD §54).
PoiCatalog.RitualSites = {
	{ id = "KeepWestAltar", name = "Keep West Altar", x = -215, z = -60, zone = "ShatteredKeep" },
	{ id = "KeepNorthAltar", name = "Keep North Altar", x = 150, z = -330, zone = "ShatteredKeep" },
}

-- The Guardian fights in the Keep's courtyard (GDD §54).
PoiCatalog.GuardianArena = { x = 0, z = -140, radius = 80 }

-- Landmarks for navigation without a minimap.
PoiCatalog.Landmarks = {
	{ id = "FrostpeakSummit", name = "Frostpeak Summit", x = -64, z = -1440, style = "Peak" },
	{ id = "KeepTower", name = "Shattered Keep", x = 50, z = -262, style = "Keep" },
	{ id = "FallenTemple", name = "Fallen Temple", x = -750, z = 980, style = "Temple" },
	{ id = "TimberwatchTower", name = "Timberwatch Tower", x = -1330, z = 120, style = "Tower" },
	{ id = "EmberhollowMouth", name = "Emberhollow Mouth", x = 750, z = 1330, style = "CaveMouth" },
	{ id = "GiantRoots", name = "Giant Roots", x = 1130, z = -780, style = "Roots" },
	{ id = "Monoliths", name = "The Monoliths", x = -1500, z = -1250, style = "Monoliths" },
	{ id = "MillBridge", name = "Mill Bridge", x = 1050, z = 120, style = "Bridge" },
	{ id = "FerryBridge", name = "Ferry Bridge", x = 1450, z = 220, style = "Bridge" },
	{ id = "OldLighthouse", name = "Old Lighthouse", x = -1100, z = 1650, style = "Lighthouse" },
}

-- World position (y = 0) of a POI.
function PoiCatalog.Position(poi): Vector3
	return Vector3.new(poi.x, 0, poi.z)
end

-- The zone a POI stands in.
function PoiCatalog.ZoneOf(poi): string?
	return BiomeCatalog.ZoneAt(poi.x, poi.z)
end

-- The risk tier (OuterRim / InnerRing / CenterCrater) a POI stands in.
function PoiCatalog.RegionOf(poi): string?
	return BiomeCatalog.RegionAt(poi.x, poi.z)
end

return PoiCatalog
