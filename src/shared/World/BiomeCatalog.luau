-- The Shattered Crater's regions and biomes (GDD §3, §18.1). One seamless island
-- with three concentric risk regions; each biome has its own resource pool (node
-- type -> count). Ores follow danger (GDD §51): copper and iron in the Outer Rim,
-- silver, cobalt, jade and obsidian in the Inner Ring, mithril in the Crater. Radii are
-- placeholders in studs.

local BiomeCatalog = {}

BiomeCatalog.MAP_RADIUS = 1200

BiomeCatalog.Regions = {
	OuterRim = { inner = 750, outer = 1200, risk = "Low" },
	InnerRing = { inner = 300, outer = 750, risk = "Medium" },
	CenterCrater = { inner = 0, outer = 300, risk = "Extreme" },
}

BiomeCatalog.Biomes = {
	Beach = {
		region = "OuterRim",
		inner = 1050,
		outer = 1180,
		color = Color3.fromRGB(222, 202, 150),
		material = "Sand",
		resources = { FiberPlant = 12, Rock = 10, RedberryBush = 5, SweetberryBush = 4, CopperDeposit = 4 },
	},
	Woodland = {
		region = "OuterRim",
		inner = 750,
		outer = 1050,
		color = Color3.fromRGB(104, 150, 74),
		material = "Grass",
		resources = {
			Tree = 55,
			Rock = 22,
			FiberPlant = 22,
			HerbShrub = 12,
			RedberryBush = 7,
			SweetberryBush = 6,
			CopperDeposit = 12,
			IronDeposit = 8,
		},
	},
	Jungle = {
		region = "InnerRing",
		inner = 330,
		outer = 750,
		color = Color3.fromRGB(58, 112, 52),
		material = "LeafyGrass",
		resources = {
			Tree = 45,
			Rock = 10,
			HerbShrub = 16,
			SilverDeposit = 10,
			CobaltDeposit = 7,
			JadeVein = 6,
			ObsidianOutcrop = 8,
		},
	},
	Caldera = {
		region = "CenterCrater",
		inner = 0,
		outer = 270,
		color = Color3.fromRGB(70, 56, 52),
		material = "Basalt",
		resources = { MithrilDeposit = 6, Rock = 6 },
	},
}

-- The region a horizontal distance from the island centre falls in.
function BiomeCatalog.RegionAt(distance: number): string?
	for name, region in BiomeCatalog.Regions do
		if distance >= region.inner and distance < region.outer then
			return name
		end
	end
	return nil
end

-- The biome at a distance (the ridge between rings counts as its outer neighbour).
function BiomeCatalog.BiomeAt(distance: number): string?
	local best, bestGap = nil, math.huge
	for name, biome in BiomeCatalog.Biomes do
		if distance >= biome.inner and distance < biome.outer then
			return name
		end
		local gap = math.min(math.abs(distance - biome.inner), math.abs(distance - biome.outer))
		if gap < bestGap then
			best, bestGap = name, gap
		end
	end
	return if distance <= BiomeCatalog.MAP_RADIUS then best else nil
end

return BiomeCatalog
