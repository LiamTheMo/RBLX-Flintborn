-- Placeholder models for resource nodes and world scenery (GDD §4.1, §54; visuals.md).
local Shared = game:GetService("ReplicatedStorage").Shared
local BiomeCatalog = require(Shared.World.BiomeCatalog)
local NodeCatalog = require(Shared.Resources.NodeCatalog)
local NodeModels = require(Shared.Visuals.NodeModels)
local Recipe = require(Shared.Visuals.Recipe)
local SceneryModels = require(Shared.Visuals.SceneryModels)

-- The lowest point of a recipe's parts (ignoring rotation, as Recipe.Bounds does).
local function lowest(recipe): number
	local low = Recipe.Bounds(recipe)
	return low[2]
end

local function highest(recipe): number
	local _, high = Recipe.Bounds(recipe)
	return high[2]
end

local function usesColor(recipe, color: { number }): boolean
	for _, spec in recipe.parts do
		if spec.color[1] == color[1] and spec.color[2] == color[2] and spec.color[3] == color[3] then
			return true
		end
	end
	return false
end

-- How many of a recipe's parts pass `keep`.
local function countParts(recipe, keep): number
	local total = 0
	for _, spec in recipe.parts do
		total += if keep(spec) then 1 else 0
	end
	return total
end

local function usesMaterial(recipe, material: string): boolean
	return countParts(recipe, function(spec)
		return spec.material == material
	end) > 0
end

local function isBall(spec): boolean
	return spec.shape == "Ball"
end

test("every node type, and only a node type, has a well formed grounded model in its catalog look", function()
	local seen = {}
	for nodeType in NodeCatalog.Nodes do
		local model = NodeModels.Get(nodeType)
		assert(model, "missing " .. nodeType)
		-- Light enough for ~1,400 nodes.
		local problems = Recipe.Problems(model.recipe, NodeModels.MAX_PARTS)
		expectEq(#problems, 0, nodeType .. " recipe: " .. table.concat(problems, "; "))
		expect(#model.recipe.parts >= 2, nodeType .. " has more than one shape")
		-- Hitboxes keep today's sizes so harvest reach is unchanged.
		local size = NodeCatalog.Looks[nodeType].size
		expectEq(model.hitbox[1], size.X, nodeType .. " hitbox x")
		expectEq(model.hitbox[2], size.Y, nodeType .. " hitbox y")
		expectEq(model.hitbox[3], size.Z, nodeType .. " hitbox z")
		-- Nothing floats or sinks.
		expectNear(lowest(model.recipe), -model.hitbox[2] / 2, 0.6, nodeType .. " lowest point is at the ground")
		-- Nodes keep their catalog colour so ores and berries read apart.
		local color = Recipe.Rgb(NodeCatalog.Looks[nodeType].color)
		expect(usesColor(model.recipe, color), nodeType .. " shows its Looks colour")
		local key = color[1] .. "," .. color[2] .. "," .. color[3]
		expect(seen[key] == nil, nodeType .. " colour differs from " .. tostring(seen[key]))
		seen[key] = nodeType
	end
	expectEq(NodeModels.Get("NoSuchNode"), nil, "unknown types have none")
end)

test("trees are a trunk under a layered canopy that spreads past it", function()
	local tree = NodeModels.Get("Tree")
	expect(#tree.recipe.parts <= NodeModels.MAX_TREE_PARTS, "trees stay within " .. NodeModels.MAX_TREE_PARTS)
	expect(tree.hitbox[1] <= 3.5 and tree.hitbox[2] >= 13, "the tree's hitbox is its trunk")
	local low, high = Recipe.Bounds(tree.recipe)
	expect(high[2] - low[2] > tree.hitbox[2] + 3, "the canopy rises above the trunk")
	expect(high[1] - low[1] > tree.hitbox[1] * 3, "and spreads around it")
	expect(countParts(tree.recipe, isBall) >= 3, "layered canopy of at least three balls")
end)

test("gems glow or gleam; rocks and plants have the right shapes", function()
	for _, gem in { "ObsidianOutcrop", "JadeVein", "AmethystGeode", "StormglassCluster" } do
		expect(usesMaterial(NodeModels.Get(gem).recipe, "Glass"), gem .. " has glass")
	end
	for _, glowing in { "StarstoneOutcrop", "AmethystGeode" } do
		expect(usesMaterial(NodeModels.Get(glowing).recipe, "Neon"), glowing .. " glows")
	end
	local rock = #NodeModels.Get("Rock").recipe.parts
	expect(rock >= 2 and rock <= 4, "rocks are 2-4 chunks")
	for _, bush in { "RedberryBush", "SweetberryBush", "RaspberryBush" } do
		expect(countParts(NodeModels.Get(bush).recipe, isBall) >= 5, bush .. " has leaf balls and berry dots")
	end
	for _, mushroom in { "CaveMushroomPatch", "RedcapMushroomPatch", "ChestnutMushroomPatch" } do
		local recipe = NodeModels.Get(mushroom).recipe
		local stems = countParts(recipe, function(spec)
			return spec.shape == "Block"
		end)
		local caps = countParts(recipe, function(spec)
			return spec.shape == "Ball" and spec.size[1] >= 0.8
		end)
		expect(stems >= 3 and caps >= 3, mushroom .. " has stems and caps")
	end
end)

-- Scenery ------------------------------------------------------------------------

test("scenery recipes are valid, small, and rooted in the ground", function()
	for kind, info in SceneryModels.Kinds do
		for paletteId in SceneryModels.Palettes do
			for variant = 1, info.variants do
				local label = kind .. "/" .. paletteId .. "/" .. variant
				local recipe = SceneryModels.Get(kind, paletteId, variant)
				assert(recipe, "missing " .. label)
				local problems = Recipe.Problems(recipe, 6)
				expectEq(#problems, 0, label .. ": " .. table.concat(problems, "; "))
				local low = lowest(recipe)
				expect(low <= 0.05 and low >= -SceneryModels.SINK, label .. " sits on the ground (" .. low .. ")")
				expect(highest(recipe) > 0.5, label .. " rises above it")
			end
		end
	end
	expectEq(SceneryModels.Get("Pine", "NoPalette"), nil, "unknown palette")
	expectEq(SceneryModels.Get("Dragon", "Pine"), nil, "unknown kind")
	expectEq(SceneryModels.Get("Pine", "Pine", 99), SceneryModels.Get("Pine", "Pine", 2), "variants clamp")
end)

test("only trunks, boulders and logs can block; tufts never do", function()
	for kind, info in SceneryModels.Kinds do
		local solid = 0
		for variant = 1, info.variants do
			for _, spec in SceneryModels.Get(kind, "Temperate", variant).parts do
				if SceneryModels.SOLID_PARTS[spec.name or spec.shape] then
					solid += 1
				end
			end
		end
		if info.solid then
			expect(solid >= info.variants, kind .. " has solid parts")
		else
			expectEq(solid, 0, kind .. " is walk-through")
		end
		expect(info.scale[1] > 0 and info.scale[1] <= info.scale[2], kind .. " scale range")
	end
end)

test("every zone has scenery in a known palette, within the part budget", function()
	for _, zoneId in BiomeCatalog.ZONE_IDS do
		expect(SceneryModels.Zones[zoneId] ~= nil, zoneId .. " has scenery")
	end
	for zoneId, zone in SceneryModels.Zones do
		expect(BiomeCatalog.Zones[zoneId] ~= nil, zoneId .. " is a map zone")
		expect(SceneryModels.Palettes[zone.palette] ~= nil, zoneId .. " palette")
		expect(zone.boulders >= 0 and zone.logs >= 0, zoneId .. " counts")
		expect(zone.clumpSize[1] <= zone.clumpSize[2], zoneId .. " clump size range")
		for _, clump in zone.clumps do
			expect(clump[1] == "Pine" or clump[1] == "Broadleaf", zoneId .. " clumps are trees")
			expect(clump[2] > 0 and zone.clumpSize[2] > 0 and zone.clumpRadius > 0, zoneId .. " clump numbers")
		end
		for _, cover in zone.groundcover do
			expect(cover[1] == "Tuft" or cover[1] == "Fern", zoneId .. " groundcover kinds")
			expect(cover[2] > 0, zoneId .. " groundcover count")
		end
	end
	local worst = SceneryModels.WorstCaseParts()
	expect(worst > 1000, "the island is dressed, not bare (" .. worst .. ")")
	expect(
		worst <= SceneryModels.PART_BUDGET,
		("scenery is at most %d parts (%d)"):format(SceneryModels.PART_BUDGET, worst)
	)
end)

test("zones keep their character: pines in the cold and the pinewoods, broadleaf in the wet", function()
	local function plants(zoneId: string, kind: string): boolean
		for _, clump in SceneryModels.Zones[zoneId].clumps do
			if clump[1] == kind then
				return true
			end
		end
		return false
	end
	expect(plants("PinewoodWilds", "Pine"), "Pinewood Wilds has pines")
	expect(plants("FrostpeakRidge", "Pine"), "Frostpeak has pines")
	expect(plants("MosswickForest", "Broadleaf"), "Mosswick has broadleaf trees")
	expect(not plants("MosswickForest", "Pine"), "and no pines")
	expect(plants("FallenTemple", "Broadleaf"), "the Fallen Temple jungle has broadleaf trees")
	expectEq(#SceneryModels.Zones.CraterLake.clumps, 0, "no trees on the crater shore")
	expectEq(#SceneryModels.Zones.ShatteredKeep.clumps, 0, "or on the Keep island")
end)
