-- World events by category and rarity (GDD §7, §51, Q42–48, Q111–112, Q140–143).
-- Each category rolls on its own every director tick, and after it triggers every
-- non-Common entry rolls its own rarity weight, so event types never compete; a
-- category without a Common entry skips when nothing rarer hits. Footprints are
-- radii in studs; biomes are the placeholder rings until the real island arrives
-- (v0.15). Loot entries are {catalogId, min, max, chance}. Ore events and meteors
-- carry `minRank`, the pickaxe they need. Creature events (GDD §54) may name a
-- preferred map `zone` or `habitat` (WildlifeRules.HABITATS) inside their biome
-- tier for placement. Names, loot and NPC groups are placeholders.

local Tiers = require(script.Parent.Parent.Items.Tiers)

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

-- Ore events need a pickaxe that can mine every ore they drop (GDD §51).
local function ore(id, name, rarity, biome, minRank, loot)
	local entry = node(id, name, rarity, biome, loot)
	entry.footprint = 25
	entry.minRank = minRank
	return entry
end

local R = Tiers.ToolRank

-- `where` = {zone?, habitat?}: where in the biome the creatures prefer (§54).
local function npc(id, name, rarity, biome, group, where)
	return {
		id = id,
		name = name,
		rarity = rarity,
		kind = K.Npc,
		biome = biome,
		zone = where and where.zone,
		habitat = where and where.habitat,
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
		node("WildHerbPatch", "Wild Herb Patch", "Common", "OuterRim", {
			{ "Herbs", 6, 10, 1 },
			{ "Sweetberry", 2, 4, 0.5 },
		}),
		node("BloodberryThicket", "Bloodberry Thicket", "Uncommon", "InnerRing", {
			{ "Redberry", 8, 12, 1 },
			{ "Sweetberry", 4, 8, 1 },
			{ "Herbs", 4, 8, 1 },
		}),
		node("IronbarkSapling", "Ironbark Sapling", "Rare", "Any", { { "Wood", 40, 60, 1 }, { "Resin", 3, 6, 1 } }),
		-- The rare shrub (GDD §51): gathered by hand for rare berries and rare herbs.
		node("WildbloomShrub", "Wildbloom Shrub", "Rare", "Any", {
			{ "Sunberry", 2, 4, 1 },
			{ "Glimmerberry", 2, 4, 1 },
			{ "Bloodroot", 1, 2, 0.5 },
			{ "Moonpetal", 1, 2, 0.5 },
		}),
		node("AncientWildbloom", "Ancient Wildbloom", "Epic", "InnerRing", {
			{ "Sunberry", 5, 8, 1 },
			{ "Glimmerberry", 5, 8, 1 },
			{ "Bloodroot", 2, 3, 1 },
			{ "Moonpetal", 2, 3, 1 },
		}),
		node("Emberbloom", "Emberbloom", "Epic", "Center", {
			{ "AncientEmber", 1, 1, 1 },
			{ "Herbs", 10, 14, 1 },
			{ "Bloodroot", 1, 2, 0.5 },
		}),
		node("ElderIronwood", "Elder Ironwood", "Legendary", "Any", {
			{ "Wood", 100, 140, 1 },
			{ "Resin", 8, 12, 1 },
			{ "AncientEmber", 1, 2, 1 },
		}),
		node("StarfallLotus", "Starfall Lotus", "Secret", "Center", {
			{ "AncientEmber", 3, 3, 1 },
			{ "Herbs", 30, 30, 1 },
			{ "Moonpetal", 3, 3, 1 },
			{ "Bloodroot", 3, 3, 1 },
		}),
	},
	-- Ore by region (GDD §51): Outer Rim copper and iron, Inner Ring silver and
	-- cobalt, the Crater mithril; Adamantine only in the rarest Crater seam.
	Ore = {
		ore("SurfaceStoneVein", "Surface Stone Vein", "Common", "OuterRim", R.Wood, {
			{ "Stone", 30, 40, 1 },
			{ "Flint", 4, 8, 1 },
		}),
		ore("IronOutcrop", "Iron Outcrop", "Uncommon", "OuterRim", R.Copper, {
			{ "IronOre", 15, 25, 1 },
			{ "CopperOre", 10, 15, 1 },
		}),
		ore("CobaltLode", "Rich Cobalt Lode", "Rare", "InnerRing", R.Silver, {
			{ "CobaltOre", 15, 25, 1 },
			{ "SilverOre", 20, 30, 1 },
		}),
		ore("EmberVeinedRock", "Ember-Veined Rock", "Epic", "Center", R.Cobalt, {
			{ "MithrilOre", 15, 25, 1 },
			{ "AncientEmber", 1, 1, 1 },
		}),
		ore("HeartstoneSeam", "Heartstone Seam", "Mythic", "Center", R.Mithril, {
			{ "MithrilOre", 40, 60, 1 },
			{ "AdamantineOre", 4, 8, 1 },
			{ "AncientEmber", 2, 2, 1 },
		}),
	},
	-- Creature events (GDD §54). Regular wildlife roams on its own (WildlifeRules),
	-- so there is no Common fallback: a missed roll spawns nothing, and every
	-- creature event rolls its own weight. The Minotaur comes only from the Keep's
	-- ritual altar (BossCatalog.Rituals).
	Npc = {
		npc("SkeletonPatrol", "Skeleton Patrol", "Uncommon", "InnerRing", {
			{ enemy = "Skeleton", count = 3 },
		}, { zone = "FallenTemple" }),
		npc("WoollyMammoth", "Woolly Mammoth", "Uncommon", "Any", {
			{ enemy = "WoollyMammoth", count = 1 },
		}, { habitat = "Grassland" }),
		npc("GiantGroundSloth", "Giant Ground Sloth", "Rare", "Any", {
			{ enemy = "GiantGroundSloth", count = 1 },
		}, { habitat = "Clearing" }),
		npc("AncientTortoise", "Ancient Tortoise", "Rare", "Any", {
			{ enemy = "AncientTortoise", count = 1 },
		}, { habitat = "Lakeshore" }),
		npc("IronTuskBoar", "Iron-Tusk Boar", "Rare", "InnerRing", {
			{ enemy = "IronTuskBoar", count = 1 },
			{ enemy = "WildBoar", count = 3 },
		}, { habitat = "Clearing" }),
		npc("SaberToothedTiger", "Saber-Toothed Tiger", "Epic", "InnerRing", {
			{ enemy = "SaberToothedTiger", count = 1 },
		}, { habitat = "Jungle" }),
		npc("StonehideRhino", "Stonehide Rhino", "Epic", "InnerRing", {
			{ enemy = "StonehideRhino", count = 1 },
		}, { habitat = "Rocky" }),
		npc("EmberWisps", "Ember Wisps", "Legendary", "InnerRing", {
			{ enemy = "EmberWisp", count = 1, elite = true },
			{ enemy = "EmberWisp", count = 3 },
		}, { zone = "EmberhollowCaves", habitat = "Cave" }),
	},
	Cache = {
		cache("WeatheredCache", "Weathered Supply Cache", "Uncommon", {
			{ "IronOre", 10, 20, 1 },
			{ "Hide", 4, 8, 1 },
			{ "BasicMedicine", 1, 2, 0.5 },
		}),
		cache("AncientCache", "Ancient Supply Cache", "Rare", {
			{ "IronOre", 20, 35, 1 },
			{ "AdvancedMedicine", 1, 2, 0.6 },
			{ "AshenOil", 1, 2, 0.5 },
			{ "SiegeResin", 1, 1, 0.3 },
			{ "AncientEmber", 1, 1, 0.5 },
			RUNE,
		}),
		cache("GildedCache", "Gilded Ancient Cache", "Epic", {
			{ "SilverOre", 20, 35, 1 },
			{ "Potion", 1, 1, 0.6 },
			{ "AshenOil", 1, 3, 0.8 },
			{ "SiegeResin", 1, 2, 0.6 },
			{ "AncientEmber", 1, 2, 1 },
			RUNE,
		}),
		cache("ElderCache", "Elder Ancient Cache", "Legendary", {
			{ "CobaltOre", 30, 50, 1 },
			{ "Potion", 1, 2, 1 },
			{ "AshenOil", 2, 4, 1 },
			{ "SiegeResin", 2, 3, 1 },
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
			-- Meteors carry Adamantine Ore, so chunks need a Mithril Pickaxe (GDD §51).
			minRank = R.Mithril,
			loot = {
				{ "AdamantineOre", 4, 8, 1 },
				{ "AbyssalShard", 1, 2, 0.6 },
				{ "Emberglass", 1, 2, 0.6 },
				{ "AncientEmber", 1, 1, 0.25 },
			},
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
			minRank = R.Mithril,
			loot = {
				{ "AdamantineOre", 10, 16, 1 },
				{ "AbyssalShard", 2, 4, 1 },
				{ "Emberglass", 2, 4, 1 },
				{ "AncientEmber", 1, 1, 0.6 },
			},
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
			-- A ruined camp the dead still hold (placeholder guards since Bandits left, §54).
			defenders = { { enemy = "Skeleton", count = 3 } },
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
			defenders = { { enemy = "Skeleton", count = 2 } },
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
		-- The Crater Gorilla holds a large jungle clearing near the crater approaches (§54).
		{
			id = "CraterGorillaEvent",
			name = "Crater Gorilla",
			rarity = "Epic",
			kind = K.Boss,
			boss = "CraterGorilla",
			biome = "InnerRing",
			habitat = "Clearing",
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
