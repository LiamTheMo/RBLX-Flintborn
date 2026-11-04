-- Server half of Shared.World.PoiCatalog: what only the server uses. Everything in
-- ReplicatedStorage is downloaded to every player, so the shared module keeps
-- only what clients need; this one clones it and adds the rest, and server code
-- requires this module.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local BiomeCatalog = require(ReplicatedStorage.Shared.World.BiomeCatalog)
local SharedPoiCatalog = require(ReplicatedStorage.Shared.World.PoiCatalog)

local PoiCatalog = table.clone(SharedPoiCatalog)

-- The Minotaur's altars stand on the Keep island's lower terrace (GDD §54).
PoiCatalog.RitualSites = {
	{ id = "KeepWestAltar", name = "Keep West Altar", x = -215, z = -60, zone = "ShatteredKeep" },
	{ id = "KeepNorthAltar", name = "Keep North Altar", x = 150, z = -330, zone = "ShatteredKeep" },
}

-- The Guardian fights in the Keep's courtyard (GDD §54).
PoiCatalog.GuardianArena = { x = 0, z = -140, radius = 80 }

-- The zone a POI stands in.
function PoiCatalog.ZoneOf(poi): string?
	return BiomeCatalog.ZoneAt(poi.x, poi.z)
end

-- The risk tier (OuterRim / InnerRing / CenterCrater) a POI stands in.
function PoiCatalog.RegionOf(poi): string?
	return BiomeCatalog.RegionAt(poi.x, poi.z)
end

return PoiCatalog
