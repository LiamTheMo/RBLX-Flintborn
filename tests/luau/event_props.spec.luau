local Shared = game:GetService("ReplicatedStorage").Shared
local BossCatalog = require(Shared.Bosses.BossCatalog)
local EnemyCatalog = require(Shared.Enemies.EnemyCatalog)
local EventCatalog = require(Shared.Events.EventCatalog)
local EventKinds = require(Shared.Events.EventKinds)
local EventRules = require(Shared.Events.EventRules)
local GameConstants = require(Shared.GameConstants)
local HudModel = require(Shared.UI.HudModel)
local ItemCatalog = require(Shared.Items.ItemCatalog)
local NodeCatalog = require(Shared.Resources.NodeCatalog)
local PoiCatalog = require(Shared.World.PoiCatalog)
local PropModels = require(Shared.Visuals.PropModels)
local Rarity = require(Shared.Items.Rarity)
local Recipe = require(Shared.Visuals.Recipe)
local Tiers = require(Shared.Items.Tiers)

local function accents()
	local list = {}
	for _, rarity in Rarity.Order do
		table.insert(list, Recipe.Rgb(Rarity.Colors[rarity]))
	end
	return list
end

local function named(recipe, name: string): number
	local count = 0
	for _, spec in recipe.parts do
		if spec.name == name then
			count += 1
		end
	end
	return count
end

-- A part's axis-aligned box once rotated (the recipes only turn parts about one
-- axis at a time; Recipe.Bounds ignores rotation, which turns every standing log
-- on its side): centre and half sizes.
local function box(spec)
	local half = { spec.size[1] / 2, spec.size[2] / 2, spec.size[3] / 2 }
	for axis = 1, 3 do
		local angle = math.rad(spec.rot and spec.rot[axis] or 0)
		if angle ~= 0 then
			local sin, cos = math.abs(math.sin(angle)), math.abs(math.cos(angle))
			local a, b = if axis == 1 then 2 else 1, if axis == 3 then 2 else 3
			half[a], half[b] = cos * half[a] + sin * half[b], sin * half[a] + cos * half[b]
		end
	end
	return spec.pos, half
end

-- The extent of a whole recipe: {minX, minY, minZ}, {maxX, maxY, maxZ}.
local function extent(recipe)
	local low, high = { math.huge, math.huge, math.huge }, { -math.huge, -math.huge, -math.huge }
	for _, spec in recipe.parts do
		local pos, half = box(spec)
		for axis = 1, 3 do
			low[axis] = math.min(low[axis], pos[axis] - half[axis])
			high[axis] = math.max(high[axis], pos[axis] + half[axis])
		end
	end
	return low, high
end

-- Recipes ------------------------------------------------------------------------

test("every structure style in the catalog has dressing, a gate and walls", function()
	local used = {}
	for _, entry in EventCatalog.Entries.Structure do
		expect(entry.style ~= nil, entry.id .. " names a style")
		used[entry.style] = true
		expect(PropModels.Structure[entry.style] ~= nil, entry.id .. " dressing for " .. tostring(entry.style))
		expect(PropModels.Gate[entry.style] ~= nil, entry.id .. " gate for " .. tostring(entry.style))
		local wall = PropModels.Wall(entry.style, PropModels.RING.height)
		expect(#Recipe.Problems(wall, PropModels.MAX_PARTS) == 0, entry.id .. " wall recipe")
	end
	for style in used do
		expect(table.find(PropModels.STYLES, style) ~= nil, style .. " is a listed style")
	end
	for _, style in PropModels.STYLES do
		expect(used[style], style .. " is used by a structure event")
	end
end)

test("every prop recipe is buildable and within the part limit", function()
	local all = PropModels.All(accents())
	expect(#all > 30, "the recipes were gathered")
	for _, item in all do
		local problems = Recipe.Problems(item.recipe, 25)
		expect(#problems == 0, item.name .. ": " .. table.concat(problems, "; "))
		local low, high = extent(item.recipe)
		expect(low[2] > -12 and high[2] < 16, item.name .. " stays near its origin")
		expect(
			low[1] > -20 and high[1] < 20 and low[3] > -20 and high[3] < 20,
			item.name .. " stays within the footprint"
		)
	end
end)

test("walls cover their gameplay part and ruins keep their stone", function()
	local ring = PropModels.RING
	for _, style in PropModels.STYLES do
		-- Ruin walls crumble to any height in range; the others are always full height.
		local heights = if style == "Ruin"
			then { PropModels.RUIN_HEIGHT[1], 5, PropModels.RUIN_HEIGHT[2] }
			else { ring.height }
		for _, height in heights do
			local wall = PropModels.Wall(style, height)
			local low, high = extent(wall)
			expect(
				low[1] >= -ring.width / 2 - 0.2 and high[1] <= ring.width / 2 + 0.2,
				style .. " wall stays in its segment"
			)
			expect(low[2] >= -height / 2 - 0.6, style .. " wall reaches the ground")
			expect(high[2] <= height / 2 + 1.5, style .. " wall stays near the part's top ")
			expect(type(wall.hostVisible) == "boolean", style .. " says whether the part stays drawn")
			if not wall.hostVisible and style ~= "Ruin" then
				-- An invisible wall must be drawn all the way up.
				expect(high[2] >= height / 2 - 0.1, style .. " draws up to the top of its part")
			end
		end
	end
	expect(PropModels.Wall("Ruin", 5).hostVisible, "ruin stone stays visible")
	expect(not PropModels.Wall("Fort", 9).hostVisible, "the palisade replaces the plain wall")
end)

test("the wall ring is closed except at the doorway and ruin gaps", function()
	local ring = PropModels.RING
	-- Neighbouring segments touch: the chord between centres fits the width.
	local chord = 2 * ring.radius * math.sin(math.pi / ring.segments)
	expect(ring.width >= chord - 0.2, "walls meet around the ring")
	expect(ring.doorway >= 1 and ring.doorway <= ring.segments, "the doorway is a segment")
	for _, style in PropModels.STYLES do
		expect(not PropModels.HasWall(style, ring.doorway), style .. " leaves its doorway open")
		local walls = 0
		for index = 1, ring.segments do
			walls += if PropModels.HasWall(style, index) then 1 else 0
		end
		expect(walls >= 5, style .. " keeps most of its walls")
		if style == "Fort" then
			expectEq(walls, ring.segments - 1, "a Fort has one gap: the doorway")
		elseif style == "Ruin" then
			-- A column stands in each crumbled gap (every gap but the doorway).
			expectEq(named(PropModels.Structure.Ruin, "Column"), ring.segments - 1 - walls, "a column per gap")
		end
	end
end)

test("structure dressing leaves the cache, loot node and boss spots free", function()
	for style, recipe in PropModels.Structure do
		for _, spec in recipe.parts do
			local pos, half = box(spec)
			local reach = math.max(half[1], half[3])
			if pos[2] + half[2] > 0.5 then
				local fromCentre = math.sqrt(pos[1] ^ 2 + pos[3] ^ 2)
				expect(fromCentre - reach > 1.5, style .. " " .. tostring(spec.name) .. " keeps clear of the cache")
				-- The Warlord stands 6 studs on (EventDirectorService).
				if style == "Fort" then
					local fromBoss = math.sqrt(pos[1] ^ 2 + (pos[3] - 6) ^ 2)
					expect(fromBoss - reach > 2, style .. " " .. tostring(spec.name) .. " keeps clear of the boss")
				end
			end
		end
	end
end)

test("the chest, altar and nodes carry the parts their services drive", function()
	for _, accent in accents() do
		local chest = PropModels.Chest(accent)
		expect(named(chest, "Lid") >= 1 and named(chest, "Glow") >= 1, "a lid that opens and a lit lock")
		-- Every part a service turns is named the way the service looks for it.
		for _, spec in chest.parts do
			if spec.name == "LidBand" or spec.name == "LidGem" then
				expect(string.sub(spec.name, 1, #PropModels.LID_PREFIX) == PropModels.LID_PREFIX, spec.name)
			end
		end
		local low, high = extent(chest)
		expect(
			low[1] >= -2.3 and high[1] <= 2.3 and low[3] >= -1.8 and high[3] <= 1.8,
			"the chest stays near its 4 x 3 hitbox"
		)
		expect(low[2] >= -1.6, "the chest sits on the ground")
	end
	local hinge = PropModels.CHEST_HINGE
	expect(type(hinge[1]) == "number" and type(hinge[2]) == "number" and type(hinge[3]) == "number", "a hinge point")
	expect(PropModels.CHEST_OPEN_DEGREES > 45 and PropModels.CHEST_OPEN_DEGREES < 180, "the lid swings open")
	expect(named(PropModels.Altar, PropModels.ALTAR_GLOW) >= 3, "the altar has lit parts to recolour")
	expect(named(PropModels.Meteor, "Glow") >= 3 and named(PropModels.Meteor, "Rim") >= 6, "meteor cracks and rim")
	for _, accent in accents() do
		expect(named(PropModels.OreNode(accent), "Crystal") >= 4, "ore nodes grow crystals")
		for variant in { Patch = true, Bloom = true, Sapling = true } do
			expect(named(PropModels.PlantNode(variant, accent), "Glow") >= 3, variant .. " glows")
		end
	end
end)

test("plant variants name real vegetation events", function()
	for eventId, variant in PropModels.PLANT_VARIANTS do
		local entry = EventCatalog.Get(eventId)
		expect(entry ~= nil and entry.category == "Vegetation", eventId .. " is a vegetation event")
		expect(variant == "Bloom" or variant == "Sapling", eventId .. " has a known variant")
	end
	for _, entry in EventCatalog.Entries.Vegetation do
		local variant = PropModels.PlantVariant(entry.id)
		local recipe = PropModels.PlantNode(variant, Recipe.Rgb(Rarity.Colors[entry.rarity]))
		expect(#Recipe.Problems(recipe, 25) == 0, entry.id .. " plant recipe")
	end
	expectEq(PropModels.PlantVariant("WildHerbPatch"), "Patch", "herbs are a patch")
end)

test("the portal ring fits every extraction zone", function()
	local smallest = math.huge
	for _, portal in PoiCatalog.Portals do
		smallest = math.min(smallest, portal.zoneRadius)
	end
	for _, accent in { { 255, 170, 60 }, { 120, 220, 255 } } do
		local low, high = extent(PropModels.Portal(accent))
		expect(low[1] > -smallest and high[1] < smallest and low[3] > -smallest and high[3] < smallest, "inside")
	end
end)

-- Catalog cross-references ---------------------------------------------------------

test("every event kind is built by the director, in its own category", function()
	for category, entries in EventCatalog.Entries do
		expect(table.find(EventCatalog.Categories, category) ~= nil, category .. " is a director category")
		expect(#entries > 0, category .. " has entries")
		for _, entry in entries do
			expect(
				EventKinds.IsBuilt(entry.kind),
				entry.id .. " kind " .. tostring(entry.kind) .. " is built by start()"
			)
			expectEq(entry.kind, EventKinds.OfCategory[category], entry.id .. " kind matches its category")
			expectEq(entry.category, category, entry.id .. " knows its category")
		end
	end
	-- Every kind the catalog defines is one the director has a builder for, and back.
	for _, kind in EventCatalog.Kinds do
		expect(EventKinds.IsBuilt(kind), kind .. " has a builder")
	end
	for _, kind in EventKinds.Built do
		expect(EventCatalog.Kinds[kind] == kind, kind .. " is a catalog kind")
	end
	for category in EventKinds.OfCategory do
		expect(EventCatalog.Entries[category] ~= nil, category .. " is a catalog category")
	end
	for _, category in EventCatalog.Categories do
		expect(EventCatalog.Entries[category] ~= nil and EventKinds.OfCategory[category] ~= nil, category)
	end
end)

-- Item and enemy cross-references are checked in events.spec; boss sources in bosses.spec.
test("each entry carries what its spawner needs, with well-formed loot and pickaxe gates", function()
	local gate = {}
	for _, node in NodeCatalog.Nodes do
		if node.minRank then
			gate[node.material] = math.max(gate[node.material] or 0, node.minRank)
		end
	end
	local ranks = {}
	for _, rank in Tiers.ToolRank do
		ranks[rank] = true
	end
	for _, entry in EventCatalog.ById do
		local id = entry.id
		expect(type(entry.name) == "string" and entry.name ~= "", id .. " has a name")
		expect(entry.lifetime > 0 and entry.footprint > 0, id .. " expires and has a footprint")
		if entry.kind == "Node" then
			expect(entry.loot ~= nil and #entry.loot > 0, id .. " pays out")
			expectEq(entry.minRank ~= nil, entry.category == "Ore", id .. " needs a pickaxe only when it is ore")
		elseif entry.kind == "Cache" then
			expect(entry.loot ~= nil and #entry.loot > 0, id .. " has loot")
		elseif entry.kind == "Meteor" then
			expect(entry.chunks >= 1 and entry.chunks % 1 == 0, id .. " has chunks")
			expect(entry.loot ~= nil and #entry.loot > 0, id .. " has loot")
			expect(entry.minRank >= Tiers.ToolRank.Mithril, id .. " chunks need a Mithril Pickaxe (GDD §51)")
		elseif entry.kind == "Npc" then
			expect(EventRules.NpcCount(entry.group) > 0, id .. " has creatures")
		elseif entry.kind == "Structure" then
			expect(entry.cache or entry.loot or entry.boss, id .. " holds something to find")
			expect(entry.loot == nil or entry.cache == nil, id .. " has one reward node or cache, not both")
		elseif entry.kind == "Boss" then
			expect(entry.boss ~= nil, id .. " names its boss")
		end
		if entry.cache then
			local cache = EventCatalog.Get(entry.cache)
			expect(cache ~= nil and cache.kind == "Cache" and cache.loot ~= nil, id .. " cache is a cache with loot")
		end
		for _, row in entry.loot or {} do
			local item, low, high, chance = row[1], row[2], row[3], row[4]
			expect(low % 1 == 0 and high % 1 == 0 and low >= 1 and high >= low, id .. " " .. item .. " quantity")
			expect(type(chance) == "number" and chance > 0 and chance <= 1, id .. " " .. item .. " chance")
			if entry.minRank and gate[item] then
				expect(entry.minRank >= gate[item], id .. " pickaxe can mine its " .. item)
			end
		end
		expect(entry.minRank == nil or ranks[entry.minRank], id .. " minRank is a real tool rank")
		for _, member in entry.group or {} do
			expect(member.count >= 1, id .. " group count")
		end
		for _, member in entry.defenders or {} do
			expect(EnemyCatalog.Get(member.enemy) ~= nil, id .. " defender " .. member.enemy)
		end
	end
	-- Rituals: every altar zone resolves to a ritual with a real boss that takes time to summon.
	for _, site in PoiCatalog.RitualSites do
		local ritual = BossCatalog.RitualFor(site.zone)
		expect(BossCatalog.Get(ritual.boss) ~= nil and ritual.summonSeconds > 0, site.id .. " summons a real boss")
	end
end)

test("every event can be admitted by the budget and rolled", function()
	for _, entry in EventCatalog.ById do
		local npcs = EventRules.NpcCount(entry.group) + EventRules.NpcCount(entry.defenders)
		expect(EventRules.WithinBudget(entry, 0, 0, npcs), entry.id .. " fits an empty server")
		expect(
			EventRules.WithinBudget(entry, EventRules.MAX_LARGE_EVENTS - 1, EventRules.MAX_EVENT_NPCS - npcs, npcs),
			entry.id .. " fits the last free slot"
		)
		expect(npcs <= EventRules.MAX_EVENT_NPCS, entry.id .. " is smaller than the whole NPC budget")
		expect(Rarity.IsValid(entry.rarity), entry.id .. " rarity " .. tostring(entry.rarity))
		local weight = EventRules.RARITY_WEIGHTS[entry.rarity]
		expect(entry.rarity == "Common" or (weight ~= nil and weight > 0 and weight < 1), entry.id .. " can roll")
	end
	-- A category that triggers with nothing rarer falls back to a Common entry, so
	-- only categories with one skip; every other rarity must be able to roll.
	local rng = Random.new(21)
	local seen = {}
	for _ = 1, 60000 do
		for _, entry in EventRules.RollTick(EventCatalog.Entries, EventCatalog.Categories, rng) do
			seen[entry.id] = true
		end
	end
	for _, entry in EventCatalog.ById do
		if entry.rarity ~= "Secret" and entry.rarity ~= "Mythic" then
			expect(seen[entry.id], entry.id .. " rolled in 60,000 ticks")
		end
	end
end)

test("every event finds a spot clear of portals, camps and the Guardian arena", function()
	-- Worst case: every fixed portal is active, each with its no-build aura.
	local aura = GameConstants.PORTAL_NO_BUILD_METERS * GameConstants.STUDS_PER_METER
	local zones = {}
	for _, portal in PoiCatalog.Portals do
		table.insert(zones, { center = Vector3.new(portal.x, 0, portal.z), radius = aura })
	end
	for _, camp in PoiCatalog.SafeZones do
		table.insert(zones, { center = Vector3.new(camp.x, 0, camp.z), radius = camp.radius })
	end
	local arena = PoiCatalog.GuardianArena
	table.insert(zones, { center = Vector3.new(arena.x, 0, arena.z), radius = arena.radius })
	local rng = Random.new(77)
	for _, entry in EventCatalog.ById do
		local clear, tries = 0, 200
		for _ = 1, tries do
			local point = EventRules.PlacePoint(entry, rng)
			if point and EventRules.ClearOf(point, entry.footprint, zones) then
				clear += 1
			end
		end
		-- The director tries ten spots per start, so a few percent is already enough.
		expect(clear / tries > 0.25, entry.id .. " is placeable (" .. clear .. "/" .. tries .. ")")
	end
end)

test("announcements carry what the event feed, map and compass read", function()
	for _, entry in EventCatalog.ById do
		expect(Rarity.Colors[entry.rarity] ~= nil, entry.id .. " rarity colour for the beacon, area circle and map pin")
		expect(HudModel.EVENT_BLURBS[entry.category] ~= nil, entry.category .. " has a HUD blurb")
		-- The view EventDirectorService announces.
		local view = {
			id = "event",
			name = entry.name,
			rarity = entry.rarity,
			category = entry.category,
			kind = entry.kind,
			position = Vector3.new(100, 0, -200),
			radius = entry.footprint,
			endsAt = 600 + entry.lifetime,
		}
		local panel = HudModel.WorldEvent({ view }, 600, 0, 0)
		expect(panel ~= nil and panel.name == entry.name, entry.id .. " shows on the event panel")
		expect(
			panel == nil or string.find(panel.description, entry.rarity, 1, true) ~= nil,
			entry.id .. " names its rarity in words"
		)
		expect(panel == nil or panel.timer ~= "", entry.id .. " has a countdown")
	end
end)

test("solid hitboxes match the drawn stone", function()
	-- The part of a recipe that is solid, by name: the extent players walk into.
	local function solid(recipe, name: string)
		local picked = { parts = {} }
		for _, spec in recipe.parts do
			if spec.name == name then
				table.insert(picked.parts, spec)
			end
		end
		return extent(picked)
	end
	for _, case in
		{ { "Ore", PropModels.OreNode({ 120, 180, 255 }), "Boulder" }, { "Pile", PropModels.LootPile, "Heap" } }
	do
		local size, recipe, name = PropModels.HITBOX[case[1]], case[2], case[3]
		local low, high = solid(recipe, name)
		expect(
			size[1] / 2 <= high[1] + 0.2 and -size[1] / 2 >= low[1] - 0.2,
			case[1] .. " hitbox is no wider than its stone (x)"
		)
		expect(
			size[3] / 2 <= high[3] + 0.2 and -size[3] / 2 >= low[3] - 0.2,
			case[1] .. " hitbox is no wider than its stone (z)"
		)
		expect(size[2] / 2 <= high[2] + 0.1, case[1] .. " hitbox is no taller than its stone")
		expect(low[2] >= -size[2] / 2 - 0.1, case[1] .. " stone sits on the hitbox floor")
	end
	local core = PropModels.METEOR_CORE
	local low, high = solid(PropModels.Meteor, "Rock")
	expect(core.lift + core.diameter / 2 <= high[2] + 0.05, "the meteor core is no taller than the rock")
	expect(core.diameter / 2 <= (high[1] - low[1]) / 2, "the meteor core is no wider than the rock")
	expect(core.lift - core.diameter / 2 >= low[2] - 0.05, "the meteor core sinks no deeper than the rock")
end)
