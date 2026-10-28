-- Samples the play-world island on a grid for render_island.py: per cell the zone
-- (index into BiomeCatalog.ZONE_IDS, 0 for open sea), whether it is dry, the
-- ground height and the water level. Printed as one JSON line.
local World = game:GetService("ReplicatedStorage").Shared.World
local BiomeCatalog = require(World.BiomeCatalog)
local IslandLayout = require(World.IslandLayout)

local N = __mapCells or 360
local SPAN = __mapSpan or 4400
local zoneIndex = {}
for index, id in BiomeCatalog.ZONE_IDS do
	zoneIndex[id] = index
end
local zones, dry, heights, water = {}, {}, {}, {}
local cell = SPAN / N
for row = 0, N - 1 do
	local z = -SPAN / 2 + (row + 0.5) * cell
	for column = 0, N - 1 do
		local x = -SPAN / 2 + (column + 0.5) * cell
		local zone = BiomeCatalog.ZoneAt(x, z)
		table.insert(zones, if zone then zoneIndex[zone] or 0 else 0)
		local isDry = IslandLayout.IsDry(x, z)
		table.insert(dry, if isDry then 1 else 0)
		table.insert(heights, math.round(IslandLayout.HeightAt(x, z) * 10) / 10)
		local level = IslandLayout.WaterLevelAt(x, z)
		table.insert(water, if level then math.round(level * 10) / 10 else -999)
	end
end
local colors = {}
for _, id in BiomeCatalog.ZONE_IDS do
	local c = BiomeCatalog.Zones[id].color
	table.insert(colors, { id, math.round(c.R * 255), math.round(c.G * 255), math.round(c.B * 255) })
end
print("@@MAP@@" .. __json({
	n = N,
	span = SPAN,
	zones = zones,
	dry = dry,
	heights = heights,
	water = water,
	colors = colors,
	coastRadius = BiomeCatalog.COAST_RADIUS,
}) .. "@@END@@")
