-- World events by category and rarity (GDD §7, Q42–48, Q111–112, Q140–143). Each
-- category rolls on its own every director tick; a category without a Common entry
-- skips when nothing rarer hits. Footprints are radii in studs; biomes are the
-- placeholder rings until the real island arrives (v0.15). Loot entries are
-- {catalogId, min, max, chance}. Names, loot and NPC groups are placeholders.

local EventCatalog = {}

EventCatalog.Kinds =
	{ Node = "Node", Npc = "Npc", Cache = "Cache", Meteor = "Meteor", Structure = "Structure", Boss = "Boss" }

-- Every director category, in announcement order.
EventCatalog.Categories = { "Vegetation", "Ore", "Npc", "Cache", "Meteor", "Structure", "Boss" }

local K = EventCatalog.Kinds

local function node(id, name, rarity, biome, loot)
	return {
		id = id,
		name = name,
		rarity = rarity,
		kind = K.Node,
		biome = biome,
		footprint = 15,
		lifetime = 600,
		loot = loot,
	}
end

local function ore(id, name, rarity, biome, loot)
	local entry = node(id, name, rarity, biome, loot)
	entry.footprint = 25
	entry.tool = "Pickaxe"
	return entry
end

local function npc(id, name, rarity, biome, group)
	return {
		id = id,
		name = name,
		rarity = rarity,
		kind = K.Npc,
		biome = biome,
		footprint = 40,
		lifetime = 600,
		group = group,
	}
end

local function cache(id, name, rarity, loot)
	return {
		id = id,
		name = name,
		rarity = rarity,
		kind = K.Cache,
		biome = "Any",
		footprint = 40,
		lifetime = 600,
		loot = loot,
	}
end

-- Rare-or-higher cache loot rolls carry a 1% portable rune (§7 placeholders).
local RUNE = { "ExtractionRune", 1, 1, 0.01 }

EventCatalog.Entries = {
	Vegetation = {
		node("WildHerbPatch", "Wild Herb Patch", "Common", "OuterRim", { { "Herbs", 6, 10, 1 } }),
		node("BloodberryThicket", "Bloodberry Thicket", "Uncommon", "InnerRing", {
			{ "Berries", 8, 12, 1 },
			{ "Herbs", 4, 8, 1 },
		}),
		node("IronbarkSapling", "Ironbark Sapling", "Rare", "Any", { { "Wood", 40, 60, 1 } }),
		node("Emberbloom", "Emberbloom", "Epic", "Center", { { "AncientEmber", 1, 1, 1 }, { "Herbs", 10, 14, 1 } }),
		node("ElderIronwood", "Elder Ironwood", "Legendary", "Any", {
			{ "Wood", 100, 140, 1 },
			{ "AncientEmber", 1, 2, 1 },
		}),
		node("StarfallLotus", "Starfall Lotus", "Secret", "Center", {
			{ "AncientEmber", 3, 3, 1 },
			{ "Herbs", 30, 30, 1 },
		}),
	},
	Ore = {
		ore("SurfaceStoneVein", "Surface Stone Vein", "Common", "OuterRim", { { "Stone", 30, 40, 1 } }),
		ore("IronOutcrop", "Iron Outcrop", "Uncommon", "InnerRing", { { "Iron", 15, 25, 1 } }),
		ore("RichIronLode", "Rich Iron Lode", "Rare", "Any", { { "Iron", 40, 60, 1 } }),
		ore("EmberVeinedRock", "Ember-Veined Rock", "Epic", "Center", {
			{ "Iron", 25, 35, 1 },
			{ "AncientEmber", 1, 1, 1 },
		}),
		ore("HeartstoneSeam", "Heartstone Seam", "Mythic", "Center", {
			{ "Iron", 70, 90, 1 },
			{ "AncientEmber", 2, 2, 1 },
		}),
	},
	Npc = {
		npc("WolfPack", "Wolf Pack", "Common", "OuterRim", { { enemy = "Wolf", count = 3 } }),
		npc("SkeletonPatrol", "Skeleton Patrol", "Uncommon", "InnerRing", { { enemy = "Skeleton", count = 3 } }),
		npc("AlphaBoar", "Alpha Boar", "Rare", "Any", {
			{ enemy = "Boar", count = 1, elite = true },
			{ enemy = "Boar", count = 2 },
		}),
		npc("RaiderWarband", "Raider Warband", "Epic", "Any", {
			{ enemy = "Bandit", count = 1, elite = true },
			{ enemy = "Bandit", count = 3 },
		}),
		npc("EmberWisps", "Ember Wisps", "Legendary", "Center", {
			{ enemy = "EmberWisp", count = 1, elite = true },
			{ enemy = "EmberWisp", count = 3 },
		}),
		npc("SabertoothAlpha", "Sabertooth Alpha", "Legendary", "InnerRing", {
			{ enemy = "Sabertooth", count = 1, elite = true },
			{ enemy = "Wolf", count = 2 },
		}),
		npc("Minotaur", "Minotaur", "Mythic", "Center", {
			{ enemy = "Minotaur", count = 1, elite = true },
			{ enemy = "Skeleton", count = 2 },
		}),
	},
	Cache = {
		cache("WeatheredCache", "Weathered Supply Cache", "Uncommon", {
			{ "Iron", 10, 20, 1 },
			{ "Hide", 4, 8, 1 },
			{ "BasicMedicine", 1, 2, 0.5 },
		}),
		cache("AncientCache", "Ancient Supply Cache", "Rare", {
			{ "Iron", 20, 35, 1 },
			{ "AdvancedMedicine", 1, 2, 0.6 },
			{ "AncientEmber", 1, 1, 0.5 },
			RUNE,
		}),
		cache("GildedCache", "Gilded Ancient Cache", "Epic", {
			{ "Iron", 40, 60, 1 },
			{ "Potion", 1, 1, 0.6 },
			{ "AncientEmber", 1, 2, 1 },
			RUNE,
		}),
		cache("ElderCache", "Elder Ancient Cache", "Legendary", {
			{ "Iron", 60, 90, 1 },
			{ "Potion", 1, 2, 1 },
			{ "AncientEmber", 2, 3, 1 },
			RUNE,
		}),
	},
	Meteor = {
		{
			id = "MeteorCrash",
			name = "Meteor Crash",
			rarity = "Rare",
			kind = K.Meteor,
			biome = "Any",
			footprint = 100,
			lifetime = 900,
			chunks = 8,
			loot = { { "Iron", 15, 25, 1 }, { "AncientEmber", 1, 1, 0.25 } },
		},
		{
			id = "GreatMeteor",
			name = "Great Meteor",
			rarity = "Legendary",
			kind = K.Meteor,
			biome = "Any",
			footprint = 100,
			lifetime = 900,
			chunks = 8,
			loot = { { "Iron", 30, 45, 1 }, { "AncientEmber", 1, 1, 0.6 } },
		},
	},
	Structure = {
		{
			id = "CrumblingRuins",
			name = "Crumbling Ruins",
			rarity = "Common",
			kind = K.Structure,
			style = "Ruin",
			biome = "OuterRim",
			footprint = 80,
			lifetime = 900,
			loot = { { "Stone", 20, 30, 1 }, { "Hide", 2, 4, 0.5 } },
		},
		{
			id = "AbandonedFort",
			name = "Abandoned Fort",
			rarity = "Uncommon",
			kind = K.Structure,
			style = "Fort",
			biome = "InnerRing",
			footprint = 80,
			lifetime = 900,
			cache = "WeatheredCache",
		},
		{
			id = "RaiderCamp",
			name = "Raider Camp",
			rarity = "Rare",
			kind = K.Structure,
			style = "Camp",
			biome = "Any",
			footprint = 80,
			lifetime = 900,
			cache = "AncientCache",
			defenders = { { enemy = "Bandit", count = 3 } },
		},
		{
			id = "WarlordsHold",
			name = "Warlord's Hold",
			rarity = "Epic",
			kind = K.Structure,
			style = "Fort",
			biome = "Any",
			footprint = 80,
			lifetime = 900,
			cache = "GildedCache",
			boss = "RaiderWarlord",
			defenders = { { enemy = "Bandit", count = 2 } },
		},
	},
	-- Event bosses (Q45). No Common entry: a missed roll spawns nothing.
	Boss = {
		{
			id = "IronhideBehemothEvent",
			name = "Ironhide Behemoth",
			rarity = "Epic",
			kind = K.Boss,
			boss = "IronhideBehemoth",
			biome = "InnerRing",
			footprint = 150,
			lifetime = 900,
		},
		{
			id = "BoneColossusEvent",
			name = "Bone Colossus",
			rarity = "Legendary",
			kind = K.Boss,
			boss = "BoneColossus",
			biome = "Any",
			footprint = 150,
			lifetime = 900,
		},
	},
}

EventCatalog.ById = {}
for category, entries in EventCatalog.Entries do
	for _, entry in entries do
		assert(EventCatalog.ById[entry.id] == nil, "Duplicate event " .. entry.id)
		entry.category = category
		-- Event loot keeps the "event" tag on the event, per item (Q161a).
		entry.tags = { "event" }
		EventCatalog.ById[entry.id] = entry
	end
end

function EventCatalog.Get(eventId: any)
	return type(eventId) == "string" and EventCatalog.ById[eventId] or nil
end

return EventCatalog
