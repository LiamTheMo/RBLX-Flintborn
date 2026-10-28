-- The play-world island's named zones (GDD §54; replaces the three rings of GDD §3,
-- §18.1). A 4,096-stud island in a 6,144-stud ocean: Crater Lake with the
-- Shattered Keep at the centre, Frostpeak Ridge to the north, the Rimlands curving
-- along the southern coast, and the forests, Riverlands, Timberwatch, the Fallen
-- Temple and Emberhollow Caves around them. −Z is north, +X east.
--
-- Each zone keeps one of the old risk-tier ids other code keys on (Low → OuterRim,
-- Medium → InnerRing, Extreme → CenterCrater), its habitat tags (wildlife) and its
-- resource pool (node type -> count). Ores follow danger (GDD §51, §54): Copper and
-- Iron in Low zones, Silver, Cobalt, Obsidian and Jade in Medium ones, Mithril only
-- in Extreme ones; every zone has the basics (GDD §53), fewer deeper in.
-- Envelopes are approximate and overlap as shared transition areas: a point
-- belongs to the zone whose envelope it sits deepest in (the lake and the Keep
-- island have hard edges). Positions and counts are placeholders.

local BiomeCatalog = {}

BiomeCatalog.ISLAND_SIZE = 4096
BiomeCatalog.WORLD_SIZE = 6144
-- Half the island, for code that still thinks of the map as a radius.
BiomeCatalog.MAP_RADIUS = BiomeCatalog.ISLAND_SIZE / 2

-- The coast is a rounded square (radius on the axes, wider on the diagonals) with
-- a gentle wobble, always inside the 4,096-stud square.
BiomeCatalog.COAST_RADIUS = 1940
BiomeCatalog.COAST_WOBBLE = 50

-- Risk tiers, by their old region ids (events, extraction and specs key on these).
BiomeCatalog.Regions = {
	OuterRim = { risk = "Low" },
	InnerRing = { risk = "Medium" },
	CenterCrater = { risk = "Extreme" },
}

BiomeCatalog.TierOfRisk = { Low = "OuterRim", Medium = "InnerRing", Extreme = "CenterCrater" }

BiomeCatalog.HABITATS = {
	"Beach",
	"Meadow",
	"Grassland",
	"Forest",
	"Jungle",
	"River",
	"Lakeshore",
	"Marsh",
	"Rocky",
	"Highland",
	"Cave",
	"Clearing",
}

BiomeCatalog.ZONE_IDS = {
	"Rimlands",
	"PinewoodWilds",
	"MosswickForest",
	"EmberhollowCaves",
	"FrostpeakRidge",
	"FallenTemple",
	"Timberwatch",
	"Riverlands",
	"CraterLake",
	"ShatteredKeep",
}

-- `shape`: Box envelopes {x, z, halfX, halfZ}; the Rimlands follow the coast
-- (`angle` ± `halfAngle` degrees, `depth` studs inland); the lake is a disc and the
-- Keep island an ellipse. `label` is where the map writes the name.
BiomeCatalog.Zones = {
	Rimlands = {
		name = "Rimlands",
		tier = "OuterRim",
		habitats = { "Beach", "Meadow", "Grassland", "Rocky", "Clearing" },
		shape = { kind = "Coast", angle = 90, halfAngle = 46, depth = 500 },
		color = Color3.fromRGB(176, 186, 110),
		material = "Grass",
		resources = {
			Tree = 40,
			Rock = 30,
			FiberPlant = 30,
			HerbShrub = 12,
			RedberryBush = 12,
			SweetberryBush = 10,
			CopperDeposit = 16,
			IronDeposit = 6,
			ClayDeposit = 12,
			JuniperShrub = 10,
			RaspberryBush = 8,
		},
	},
	PinewoodWilds = {
		name = "Pinewood Wilds",
		tier = "OuterRim",
		habitats = { "Forest", "Clearing", "Meadow", "Rocky" },
		shape = { kind = "Box", x = -1300, z = -950, halfX = 500, halfZ = 550 },
		color = Color3.fromRGB(70, 120, 70),
		material = "Grass",
		resources = {
			Tree = 80,
			Rock = 24,
			FiberPlant = 20,
			HerbShrub = 12,
			RedberryBush = 8,
			SweetberryBush = 8,
			CopperDeposit = 12,
			IronDeposit = 12,
			ChestnutMushroomPatch = 6,
			CaveMushroomPatch = 4,
			JuniperShrub = 8,
			HazelShrub = 8,
		},
	},
	MosswickForest = {
		name = "Mosswick Forest",
		tier = "OuterRim",
		habitats = { "Forest", "Marsh", "Clearing", "River" },
		shape = { kind = "Box", x = 1300, z = -1000, halfX = 450, halfZ = 450 },
		color = Color3.fromRGB(82, 132, 64),
		material = "LeafyGrass",
		resources = {
			Tree = 60,
			Rock = 14,
			FiberPlant = 18,
			HerbShrub = 14,
			RedberryBush = 8,
			SweetberryBush = 8,
			CopperDeposit = 10,
			IronDeposit = 8,
			ClayDeposit = 8,
			RedcapMushroomPatch = 6,
			ChestnutMushroomPatch = 6,
			CaveMushroomPatch = 4,
			ElderberryShrub = 6,
			HazelShrub = 6,
		},
	},
	EmberhollowCaves = {
		name = "Emberhollow Caves",
		tier = "InnerRing",
		habitats = { "Cave", "Rocky", "Highland", "Grassland" },
		shape = { kind = "Box", x = 750, z = 1000, halfX = 350, halfZ = 350 },
		-- The enterable interior under the hill (450 × 350), reached by a tunnel from
		-- the south; floor and ceiling heights in studs.
		interior = { x = 750, z = 1000, halfX = 225, halfZ = 175, floor = 52, ceiling = 108 },
		tunnel = { x = 750, halfWidth = 12, fromZ = 1170, toZ = 1330, ceiling = 76 },
		color = Color3.fromRGB(120, 70, 56),
		material = "Basalt",
		resources = {
			Tree = 12,
			Rock = 18,
			FiberPlant = 8,
			HerbShrub = 6,
			RedberryBush = 4,
			SweetberryBush = 3,
			SilverDeposit = 8,
			CobaltDeposit = 8,
			ObsidianOutcrop = 10,
			AmethystGeode = 8,
			JadeVein = 3,
			CaveMushroomPatch = 8,
			ThornShrub = 3,
		},
	},
	FrostpeakRidge = {
		name = "Frostpeak Ridge",
		tier = "CenterCrater",
		habitats = { "Highland", "Rocky", "Clearing" },
		shape = { kind = "Box", x = 0, z = -1400, halfX = 700, halfZ = 400 },
		color = Color3.fromRGB(214, 222, 232),
		material = "Snow",
		resources = {
			Tree = 14,
			Rock = 14,
			FiberPlant = 6,
			HerbShrub = 4,
			RedberryBush = 3,
			SweetberryBush = 3,
			MithrilDeposit = 10,
			StarstoneOutcrop = 4,
			StormglassCluster = 5,
			FrostShrub = 10,
			JuniperShrub = 4,
		},
	},
	FallenTemple = {
		name = "Fallen Temple",
		tier = "InnerRing",
		habitats = { "Jungle", "Clearing", "Rocky" },
		shape = { kind = "Box", x = -750, z = 1000, halfX = 400, halfZ = 400 },
		color = Color3.fromRGB(60, 112, 56),
		material = "LeafyGrass",
		resources = {
			Tree = 40,
			Rock = 14,
			FiberPlant = 14,
			HerbShrub = 14,
			RedberryBush = 5,
			SweetberryBush = 4,
			SilverDeposit = 8,
			CobaltDeposit = 6,
			JadeVein = 8,
			ObsidianOutcrop = 4,
			AmethystGeode = 4,
			ThornShrub = 8,
			RedcapMushroomPatch = 4,
		},
	},
	Timberwatch = {
		name = "Timberwatch",
		tier = "InnerRing",
		habitats = { "Forest", "Clearing", "Highland", "Rocky" },
		shape = { kind = "Box", x = -1250, z = 200, halfX = 400, halfZ = 450 },
		color = Color3.fromRGB(96, 116, 60),
		material = "Grass",
		resources = {
			Tree = 60,
			Rock = 18,
			FiberPlant = 14,
			HerbShrub = 10,
			RedberryBush = 6,
			SweetberryBush = 5,
			SilverDeposit = 10,
			CobaltDeposit = 6,
			ObsidianOutcrop = 4,
			JadeVein = 2,
			ChestnutMushroomPatch = 4,
			RedcapMushroomPatch = 3,
			HazelShrub = 5,
			ElderberryShrub = 4,
		},
	},
	Riverlands = {
		name = "Riverlands",
		tier = "OuterRim",
		habitats = { "River", "Meadow", "Grassland", "Marsh", "Clearing" },
		shape = { kind = "Box", x = 1350, z = 150, halfX = 550, halfZ = 450 },
		color = Color3.fromRGB(124, 170, 84),
		material = "Grass",
		resources = {
			Tree = 34,
			Rock = 18,
			FiberPlant = 28,
			HerbShrub = 12,
			RedberryBush = 10,
			SweetberryBush = 10,
			CopperDeposit = 12,
			IronDeposit = 10,
			ClayDeposit = 14,
			RaspberryBush = 8,
			ElderberryShrub = 4,
		},
	},
	CraterLake = {
		name = "Crater Lake",
		tier = "CenterCrater",
		habitats = { "Lakeshore", "Rocky" },
		-- ~1,400 across: open water to 600 studs from the centre, then the shore and
		-- the crater rim.
		shape = { kind = "Disc", x = 0, z = -100, radius = 700 },
		label = { x = -300, z = 300 },
		color = Color3.fromRGB(96, 92, 88),
		material = "Basalt",
		resources = {
			Tree = 8,
			Rock = 8,
			FiberPlant = 6,
			HerbShrub = 4,
			RedberryBush = 3,
			SweetberryBush = 2,
			MithrilDeposit = 6,
			StormglassCluster = 4,
			StarstoneOutcrop = 2,
			ClayDeposit = 3,
			ThornShrub = 2,
		},
	},
	ShatteredKeep = {
		name = "Shattered Keep",
		tier = "CenterCrater",
		habitats = { "Rocky", "Lakeshore", "Clearing" },
		shape = { kind = "Ellipse", x = 0, z = -100, halfX = 275, halfZ = 325 },
		color = Color3.fromRGB(120, 112, 124),
		material = "Slate",
		resources = {
			Tree = 4,
			Rock = 6,
			FiberPlant = 4,
			HerbShrub = 3,
			RedberryBush = 2,
			SweetberryBush = 2,
			MithrilDeposit = 5,
			StarstoneOutcrop = 3,
			ThornShrub = 3,
		},
	},
}

-- Old name for the zones: specs and tools that walk every pool by `region` still work.
BiomeCatalog.Biomes = BiomeCatalog.Zones
for _, zone in BiomeCatalog.Zones do
	zone.region = zone.tier
end

-- Distance from the centre to the coast along the direction (dx, dz) (any length).
function BiomeCatalog.CoastRadius(dx: number, dz: number): number
	local r = math.sqrt(dx * dx + dz * dz)
	if r < 1e-6 then
		return BiomeCatalog.COAST_RADIUS
	end
	local c, s = math.abs(dx) / r, math.abs(dz) / r
	local shape = (c ^ 4 + s ^ 4) ^ -0.25
	local wobble = math.noise(dx / r * 2.2, dz / r * 2.2, 4.1) * BiomeCatalog.COAST_WOBBLE
	return BiomeCatalog.COAST_RADIUS * shape + wobble
end

-- Inland distance from the coast at (x, z): negative out at sea.
function BiomeCatalog.CoastDistance(x: number, z: number): number
	return BiomeCatalog.CoastRadius(x, z) - math.sqrt(x * x + z * z)
end

local function angleGap(a: number, b: number): number
	return math.abs((a - b + 180) % 360 - 180)
end

-- How deep (x, z) sits in a zone's envelope: 0 at its heart, 1 on its edge, more
-- outside. Box envelopes are rounded (a superellipse), so corners blend.
function BiomeCatalog.EnvelopeDistance(zoneId: string, x: number, z: number): number
	local shape = BiomeCatalog.Zones[zoneId].shape
	if shape.kind == "Coast" then
		local inland = BiomeCatalog.CoastDistance(x, z)
		local across = (inland - shape.depth / 2) / (shape.depth / 2)
		local along = angleGap(math.deg(math.atan2(z, x)), shape.angle) / shape.halfAngle
		return (across ^ 4 + along ^ 4) ^ 0.25
	elseif shape.kind == "Disc" then
		local dx, dz = x - shape.x, z - shape.z
		return math.sqrt(dx * dx + dz * dz) / shape.radius
	elseif shape.kind == "Ellipse" then
		local dx, dz = (x - shape.x) / shape.halfX, (z - shape.z) / shape.halfZ
		return math.sqrt(dx * dx + dz * dz)
	end
	local dx, dz = (x - shape.x) / shape.halfX, (z - shape.z) / shape.halfZ
	return (dx ^ 4 + dz ^ 4) ^ 0.25
end

-- The zones whose envelopes compete (the lake and the Keep island have hard edges).
local OPEN_ZONES = {}
for _, zoneId in BiomeCatalog.ZONE_IDS do
	if zoneId ~= "CraterLake" and zoneId ~= "ShatteredKeep" then
		table.insert(OPEN_ZONES, zoneId)
	end
end
BiomeCatalog.OPEN_ZONES = OPEN_ZONES

-- The zone at a horizontal position, nil out at sea.
function BiomeCatalog.ZoneAt(x: number, z: number): string?
	if BiomeCatalog.CoastDistance(x, z) < 0 then
		return nil
	end
	if BiomeCatalog.EnvelopeDistance("ShatteredKeep", x, z) < 1 then
		return "ShatteredKeep"
	end
	if BiomeCatalog.EnvelopeDistance("CraterLake", x, z) < 1 then
		return "CraterLake"
	end
	local best, bestDistance = nil, math.huge
	for _, zoneId in OPEN_ZONES do
		local distance = BiomeCatalog.EnvelopeDistance(zoneId, x, z)
		if distance < bestDistance then
			best, bestDistance = zoneId, distance
		end
	end
	return best
end

-- The risk tier (OuterRim / InnerRing / CenterCrater) at a horizontal position.
function BiomeCatalog.RegionAt(x: number, z: number): string?
	local zoneId = BiomeCatalog.ZoneAt(x, z)
	return zoneId and BiomeCatalog.Zones[zoneId].tier
end

-- Old name: the zone at a position.
BiomeCatalog.BiomeAt = BiomeCatalog.ZoneAt

-- The zones of one tier, in ZONE_IDS order.
function BiomeCatalog.ZonesIn(tier: string): { string }
	local list = {}
	for _, zoneId in BiomeCatalog.ZONE_IDS do
		if BiomeCatalog.Zones[zoneId].tier == tier then
			table.insert(list, zoneId)
		end
	end
	return list
end

function BiomeCatalog.HasHabitat(zoneId: string, habitat: string): boolean
	local zone = BiomeCatalog.Zones[zoneId]
	return zone ~= nil and table.find(zone.habitats, habitat) ~= nil
end

-- A zone's centre (the middle of its envelope; the Rimlands' is on the coast arc).
function BiomeCatalog.Center(zoneId: string): (number, number)
	local zone = BiomeCatalog.Zones[zoneId]
	local shape = zone.shape
	if shape.kind == "Coast" then
		local radians = math.rad(shape.angle)
		local dx, dz = math.cos(radians), math.sin(radians)
		local coast = BiomeCatalog.CoastRadius(dx, dz)
		local r = coast - shape.depth / 2
		return dx * r, dz * r
	end
	return shape.x, shape.z
end

-- The horizontal box {minX, maxX, minZ, maxZ} that holds a zone's envelope.
function BiomeCatalog.Bounds(zoneId: string)
	local shape = BiomeCatalog.Zones[zoneId].shape
	if shape.kind == "Coast" then
		local half = BiomeCatalog.ISLAND_SIZE / 2
		return { minX = -half, maxX = half, minZ = 0, maxZ = half }
	elseif shape.kind == "Disc" then
		return {
			minX = shape.x - shape.radius,
			maxX = shape.x + shape.radius,
			minZ = shape.z - shape.radius,
			maxZ = shape.z + shape.radius,
		}
	end
	return {
		minX = shape.x - shape.halfX,
		maxX = shape.x + shape.halfX,
		minZ = shape.z - shape.halfZ,
		maxZ = shape.z + shape.halfZ,
	}
end

-- Rough land area of a zone's envelope in square studs (the lake counts its shore).
function BiomeCatalog.Area(zoneId: string): number
	local shape = BiomeCatalog.Zones[zoneId].shape
	if shape.kind == "Coast" then
		return math.rad(shape.halfAngle * 2) * (BiomeCatalog.COAST_RADIUS * 1.1) * shape.depth
	elseif shape.kind == "Disc" then
		return math.pi * (shape.radius ^ 2 - (shape.radius - 100) ^ 2)
	elseif shape.kind == "Ellipse" then
		return math.pi * shape.halfX * shape.halfZ
	end
	return 4 * shape.halfX * shape.halfZ
end

-- Where each node type prefers to grow, first habitat the zone offers wins
-- (ResourceService). `share` is how often the preference is used at all.
BiomeCatalog.NodeHabitats = {
	Tree = { habitats = { "Forest", "Jungle" }, share = 0.8 },
	Rock = { habitats = { "Rocky" }, share = 0.5 },
	ClayDeposit = { habitats = { "River", "Marsh", "Lakeshore", "Beach" }, share = 0.9 },
	CaveMushroomPatch = { habitats = { "Cave", "Forest" }, share = 0.8 },
	ObsidianOutcrop = { habitats = { "Cave", "Rocky" }, share = 0.6 },
	AmethystGeode = { habitats = { "Cave", "Rocky" }, share = 0.6 },
	SilverDeposit = { habitats = { "Cave", "Rocky" }, share = 0.4 },
	CobaltDeposit = { habitats = { "Cave", "Rocky" }, share = 0.4 },
	JadeVein = { habitats = { "Cave", "Rocky" }, share = 0.4 },
	MithrilDeposit = { habitats = { "Rocky", "Highland" }, share = 0.6 },
	StarstoneOutcrop = { habitats = { "Highland", "Rocky" }, share = 0.6 },
	StormglassCluster = { habitats = { "Lakeshore", "Highland" }, share = 0.6 },
	FrostShrub = { habitats = { "Highland" }, share = 1 },
	JuniperShrub = { habitats = { "Beach", "Highland" }, share = 0.7 },
	RedberryBush = { habitats = { "Clearing", "Meadow" }, share = 0.5 },
	SweetberryBush = { habitats = { "Clearing", "Meadow" }, share = 0.5 },
	RaspberryBush = { habitats = { "Meadow", "River" }, share = 0.5 },
	FiberPlant = { habitats = { "Grassland", "Meadow", "Marsh" }, share = 0.5 },
}

return BiomeCatalog
