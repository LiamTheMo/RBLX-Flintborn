-- Boss archetypes (GDD §8, Q45–47, Q147). Each has a fixed authored baseline that
-- scaling multiplies at spawn. Sources: the Guardian (own schedule), event
-- (director), ritual (player-placed offering) and structure (generated holds).
-- Attacks: Slam (melee), Bolt (slow projectile), Quake (telegraphed area).
-- Loot entries are {catalogId, min, max, chance}. Values are placeholders except
-- the Guardian baseline from §8 placeholders.

local BossCatalog = {}

BossCatalog.Sources = { Guardian = "Guardian", Event = "Event", Ritual = "Ritual", Structure = "Structure" }

BossCatalog.Bosses = {
	Guardian = {
		name = "The Guardian",
		source = "Guardian",
		health = 25000,
		damage = 30,
		speed = 10,
		reach = 12,
		size = Vector3.new(10, 18, 8),
		color = Color3.fromRGB(70, 90, 110),
		attacks = { "Slam", "Bolt", "Quake" },
		pillars = { count = 4, health = 1500 },
		legendary = "GuardianFang",
		-- Elite loot (GDD §51): the unique Guardian Heart, plenty of elite materials
		-- and Adamantine Ore, besides the mid-fight Legendary.
		loot = {
			{ "GuardianHeart", 1, 1, 1 },
			{ "ChargedCore", 4, 6, 1 },
			{ "GlowFur", 4, 6, 1 },
			{ "AdamantineOre", 10, 20, 1 },
			{ "AncientEmber", 2, 3, 1 },
		},
	},
	IronhideBehemoth = {
		name = "Ironhide Behemoth",
		source = "Event",
		health = 4000,
		damage = 22,
		speed = 12,
		reach = 10,
		size = Vector3.new(8, 9, 12),
		color = Color3.fromRGB(96, 84, 76),
		attacks = { "Slam", "Quake" },
		loot = { { "Hide", 15, 25, 1 }, { "IronOre", 20, 30, 1 }, { "AncientEmber", 1, 1, 0.5 } },
	},
	BoneColossus = {
		name = "Bone Colossus",
		source = "Event",
		health = 7000,
		damage = 26,
		speed = 9,
		reach = 11,
		size = Vector3.new(7, 16, 5),
		color = Color3.fromRGB(226, 220, 200),
		attacks = { "Slam", "Bolt", "Quake" },
		loot = { { "IronOre", 40, 60, 1 }, { "AncientEmber", 1, 2, 1 } },
	},
	-- The roster's event boss (GDD §54): hostile, plenty of a large animal's meat,
	-- hide and bone, the elite materials, and Inner Ring silver and cobalt.
	CraterGorilla = {
		name = "Crater Gorilla",
		source = "Event",
		health = 5000,
		damage = 24,
		speed = 15,
		reach = 9,
		size = Vector3.new(7, 9, 6),
		color = Color3.fromRGB(58, 54, 56),
		attacks = { "Slam", "Bolt", "Quake" },
		loot = {
			{ "RawMeat", 12, 18, 1 },
			{ "Hide", 10, 14, 1 },
			{ "Bone", 8, 12, 1 },
			{ "DireHide", 2, 4, 1 },
			{ "ChargedCore", 1, 2, 1 },
			{ "GlowFur", 1, 2, 1 },
			{ "SilverOre", 8, 14, 1 },
			{ "CobaltOre", 5, 10, 1 },
		},
	},
	-- The Shattered Keep's ritual boss (GDD §54): Inner Ring silver and cobalt in
	-- bulk and the elite materials.
	Minotaur = {
		name = "Minotaur",
		source = "Ritual",
		health = 6000,
		damage = 26,
		speed = 13,
		reach = 9,
		size = Vector3.new(5.6, 11.2, 4.2),
		color = Color3.fromRGB(90, 60, 40),
		attacks = { "Slam", "Quake" },
		loot = {
			{ "SilverOre", 15, 25, 1 },
			{ "CobaltOre", 10, 18, 1 },
			{ "AncientEmber", 3, 5, 1 },
			{ "DireHide", 2, 3, 1 },
			{ "ChargedCore", 1, 2, 0.6 },
			{ "GlowFur", 1, 2, 0.6 },
			{ "ExtractionRune", 1, 1, 0.05 },
		},
	},
	RaiderWarlord = {
		name = "Raider Warlord",
		source = "Structure",
		health = 3000,
		damage = 20,
		speed = 14,
		reach = 8,
		size = Vector3.new(4, 7, 3),
		color = Color3.fromRGB(140, 30, 30),
		attacks = { "Slam", "Bolt" },
		loot = { { "IronOre", 25, 40, 1 }, { "Potion", 1, 2, 0.6 } },
	},
}

-- What a ritual site asks for to summon its boss (consumed once on the server).
-- A site summons the ritual of its map zone, else the first one. The Minotaur is
-- the Shattered Keep's ritual boss, and the Keep holds every altar (§54).
BossCatalog.Rituals = {
	{ boss = "Minotaur", zone = "ShatteredKeep", offering = { AncientEmber = 3, IronOre = 50 }, summonSeconds = 10 },
}

function BossCatalog.Get(bossId: any)
	return type(bossId) == "string" and BossCatalog.Bosses[bossId] or nil
end

-- The ritual a site in `zoneId` (nil when unknown) performs.
function BossCatalog.RitualFor(zoneId: string?)
	local fallback = nil
	for _, ritual in BossCatalog.Rituals do
		if ritual.zone ~= nil and ritual.zone == zoneId then
			return ritual
		elseif ritual.zone == nil and fallback == nil then
			fallback = ritual
		end
	end
	return fallback or BossCatalog.Rituals[1]
end

return BossCatalog
