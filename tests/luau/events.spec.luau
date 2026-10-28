local Shared = game:GetService("ReplicatedStorage").Shared
local BiomeCatalog = require(Shared.World.BiomeCatalog)
local EnemyCatalog = require(Shared.Enemies.EnemyCatalog)
local EventCatalog = require(Shared.Events.EventCatalog)
local EventRules = require(Shared.Events.EventRules)
local IslandLayout = require(Shared.World.IslandLayout)
local ItemCatalog = require(Shared.Items.ItemCatalog)
local WildlifeRules = require(Shared.Enemies.WildlifeRules)

local function entries(...)
	local list = {}
	for _, rarity in { ... } do
		table.insert(list, { id = rarity, rarity = rarity })
	end
	return list
end

test("each category rolls independently, so several can start in one tick", function()
	local rng = Random.new(11)
	local catalog = { A = entries("Common"), B = entries("Common"), C = entries("Common") }
	local best = 0
	for _ = 1, 2000 do
		best = math.max(best, #EventRules.RollTick(catalog, { "A", "B", "C" }, rng))
	end
	expect(best >= 2, "two or more categories triggered together")
end)

test("about 25% of ticks trigger per category", function()
	local rng = Random.new(12)
	local list = entries("Common")
	local hits, trials = 0, 40000
	for _ = 1, trials do
		if #EventRules.RollCategory(list, rng) > 0 then
			hits += 1
		end
	end
	expectNear(hits / trials, 0.25, 0.01, "trigger rate")
end)

test("a rare type rolls on its own and Common is the fallback", function()
	local rng = Random.new(13)
	local list = entries("Common", "Secret")
	local secret, common, trials = 0, 0, 400000
	for _ = 1, trials do
		local entry = EventRules.RollCategory(list, rng)[1]
		if entry and entry.rarity == "Secret" then
			secret += 1
		elseif entry then
			common += 1
		end
	end
	expectNear(secret / trials, 0.00025, 0.00008, "Secret ~0.025% per category per tick")
	expectNear(common / trials, 0.25 * 0.999, 0.01, "everything else falls back to Common")
end)

test("rare types of one rarity never compete: each keeps its own rate", function()
	local rng = Random.new(15)
	local list = { { id = "ShrubA", rarity = "Rare" }, { id = "ShrubB", rarity = "Rare" } }
	local a, b, both, trials = 0, 0, 0, 200000
	for _ = 1, trials do
		local seen = {}
		for _, entry in EventRules.RollCategory(list, rng) do
			seen[entry.id] = true
		end
		a += if seen.ShrubA then 1 else 0
		b += if seen.ShrubB then 1 else 0
		both += if seen.ShrubA and seen.ShrubB then 1 else 0
	end
	expectNear(a / trials, 0.25 * 0.12, 0.003, "the first type keeps the full Rare rate")
	expectNear(b / trials, 0.25 * 0.12, 0.003, "and so does the second")
	expect(both > 0, "both can start in the same tick")
end)

test("a category with no Common skips when nothing rarer hits", function()
	local rng = Random.new(14)
	local list = entries("Rare")
	local hits, trials = 0, 100000
	for _ = 1, trials do
		if #EventRules.RollCategory(list, rng) > 0 then
			hits += 1
		end
	end
	expectNear(hits / trials, 0.25 * 0.12, 0.004, "only the Rare roll can produce an event")
	expectEq(#EventRules.RollCategory({}, rng), 0, "empty categories never roll")
end)

test("footprint separation rejects overlapping candidates", function()
	local active = { { position = Vector3.new(0, 0, 0), radius = 40 } }
	expect(not EventRules.Separated(Vector3.new(50, 0, 0), 25, active), "overlaps")
	expect(EventRules.Separated(Vector3.new(70, 0, 0), 25, active), "clear")
end)

test("rare nodes give their reward once and never regrow", function()
	local site = {}
	expect(EventRules.Claim(site), "first claim")
	expect(not EventRules.Claim(site), "a repeated callback grants nothing")
end)

test("a cache channel needs the full 60 seconds", function()
	expect(not EventRules.ChannelComplete(nil, 100, 60), "never started")
	expect(not EventRules.ChannelComplete(50, 100, 60), "50 s is not enough")
	expect(EventRules.ChannelComplete(40, 100, 60), "60 s completes")
end)

test("the budget caps large events and event NPCs", function()
	local ruin = { footprint = 80 }
	expect(EventRules.WithinBudget(ruin, 5, 0, 0), "room for one more")
	expect(not EventRules.WithinBudget(ruin, 6, 0, 0), "six large events max")
	expect(not EventRules.WithinBudget({ footprint = 40 }, 0, 38, 3), "40 event NPCs max")
end)

test("biome distances stay inside their band", function()
	local rng = Random.new(15)
	local band = EventRules.BIOMES.InnerRing
	for _ = 1, 500 do
		local d = EventRules.BiomeDistance("InnerRing", rng)
		expect(d >= band[1] and d <= band[2], "inside the inner band")
	end
end)

test("events land on dry ground in their tier, zone and habitat (GDD §54)", function()
	local rng = Random.new(54)
	for _, entry in EventCatalog.ById do
		local tier = EventRules.TIERS[entry.biome]
		for _ = 1, 4 do
			local point = EventRules.PlacePoint(entry, rng)
			expect(point ~= nil, entry.id .. " finds a spot")
			if point then
				local zoneId = BiomeCatalog.ZoneAt(point.X, point.Z)
				expect(zoneId ~= nil, entry.id .. " on the island")
				if tier then
					expectEq(BiomeCatalog.RegionAt(point.X, point.Z), tier, entry.id .. " tier")
				end
				if entry.zone then
					expectEq(zoneId, entry.zone, entry.id .. " zone")
				end
				if entry.habitat == "Cave" then
					expect(IslandLayout.InCaveInterior(point.X, point.Z), entry.id .. " inside the cave")
				else
					expect(IslandLayout.IsDry(point.X, point.Z), entry.id .. " on dry ground")
					expect(
						math.abs(point.Y - IslandLayout.HeightAt(point.X, point.Z)) < 0.01,
						entry.id .. " on the ground"
					)
					if entry.habitat then
						expect(
							IslandLayout.HabitatMatches(entry.habitat, zoneId, point.X, point.Z),
							entry.id .. " in its " .. entry.habitat
						)
					end
				end
			end
		end
	end
	-- The catalog's "Center" key is the crater tier.
	expectEq(EventRules.TIERS.Center, "CenterCrater", "Center means the crater tier")
end)

test("the catalog is consistent: real items, real enemies, every theme", function()
	for _, entry in EventCatalog.ById do
		for _, row in entry.loot or {} do
			expect(ItemCatalog.Get(row[1]) ~= nil, entry.id .. " loot " .. row[1])
		end
		for _, member in entry.group or entry.defenders or {} do
			expect(EnemyCatalog.Get(member.enemy) ~= nil, entry.id .. " enemy " .. member.enemy)
		end
		if entry.cache then
			expect(EventCatalog.Get(entry.cache) ~= nil, entry.id .. " cache")
		end
		expect(table.find(entry.tags, "event") ~= nil, entry.id .. " tagged event")
	end
	local themes = {}
	for _, enemy in EnemyCatalog.Enemies do
		themes[enemy.theme] = true
	end
	for _, theme in EnemyCatalog.Themes do
		expect(themes[theme], "theme " .. theme)
	end
	local commons = 0
	for _, entry in EventCatalog.Entries.Cache do
		commons += entry.rarity == "Common" and 1 or 0
	end
	expectEq(commons, 0, "caches have no Common, so a missed roll skips")
end)

test("creature events follow the owner roster (GDD §54)", function()
	local function members(eventId: string)
		local entry = EventCatalog.Get(eventId)
		assert(entry, "missing " .. eventId)
		local found = {}
		for _, member in entry.group or {} do
			found[member.enemy] = (found[member.enemy] or 0) + member.count
		end
		return entry, found
	end
	for eventId, enemyId in
		{
			GiantGroundSloth = "GiantGroundSloth",
			SaberToothedTiger = "SaberToothedTiger",
			WoollyMammoth = "WoollyMammoth",
			AncientTortoise = "AncientTortoise",
			StonehideRhino = "StonehideRhino",
		}
	do
		local entry, found = members(eventId)
		expectEq(entry.category, "Npc", eventId .. " is a creature event")
		expectEq(found[enemyId], 1, eventId .. " brings one " .. enemyId)
		expect(next(found, next(found)) == nil, eventId .. " comes alone")
	end
	local _, boars = members("IronTuskBoar")
	expectEq(boars.IronTuskBoar, 1, "one Iron-Tusk Boar")
	expect((boars.WildBoar or 0) >= 2, "with protective Wild Boars")
	local gorilla = EventCatalog.Get("CraterGorillaEvent")
	expectEq(gorilla.category, "Boss", "the Crater Gorilla is an event boss")
	expectEq(gorilla.boss, "CraterGorilla", "it names its boss")
	expectEq(gorilla.biome, "InnerRing", "near the crater approaches")
	-- Every creature event rolls its own weight; nothing falls back to Common.
	for _, category in { "Npc", "Boss" } do
		for _, entry in EventCatalog.Entries[category] do
			expect(EventRules.RARITY_WEIGHTS[entry.rarity] ~= nil, entry.id .. " rolls its own weight")
		end
	end
	-- Earlier creatures keep their new homes; Bandits are gone.
	expectEq(EventCatalog.Get("SkeletonPatrol").zone, "FallenTemple", "Skeletons in the Fallen Temple")
	expectEq(EventCatalog.Get("EmberWisps").zone, "EmberhollowCaves", "Wisps in Emberhollow Caves")
	expectEq(EventCatalog.Get("Minotaur"), nil, "the Minotaur is the Keep's ritual boss, not an event")
	-- Generated camps and holds keep placeholder guards now that Bandits are gone.
	for _, structureId in { "RaiderCamp", "WarlordsHold" } do
		expect(EventRules.NpcCount(EventCatalog.Get(structureId).defenders) > 0, structureId .. " is guarded")
	end
	for _, entry in EventCatalog.ById do
		for _, member in entry.group or entry.defenders or {} do
			expect(member.enemy ~= "Bandit", entry.id .. " has no Bandits")
		end
		for _, old in { "WolfPack", "AlphaBoar", "RaiderWarband", "SabertoothAlpha" } do
			expect(entry.id ~= old, old .. " is retired")
		end
	end
end)

test("creature event preferences name real zones and habitats", function()
	local zones = {
		Rimlands = true,
		PinewoodWilds = true,
		MosswickForest = true,
		EmberhollowCaves = true,
		FrostpeakRidge = true,
		FallenTemple = true,
		Timberwatch = true,
		Riverlands = true,
		CraterLake = true,
		ShatteredKeep = true,
	}
	for _, entry in EventCatalog.ById do
		if entry.zone then
			expect(zones[entry.zone], entry.id .. " zone " .. entry.zone)
		end
		if entry.habitat then
			expect(table.find(WildlifeRules.HABITATS, entry.habitat) ~= nil, entry.id .. " habitat " .. entry.habitat)
		end
	end
end)
