local Shared = game:GetService("ReplicatedStorage").Shared
local Server = game:GetService("ServerScriptService").Server
local BiomeCatalog = require(Shared.World.BiomeCatalog)
local EnemyCatalog = require(Server.Rules.Enemies.EnemyCatalog)
local EventCatalog = require(Server.Rules.Events.EventCatalog)
local EventRules = require(Server.Rules.Events.EventRules)
local IslandLayout = require(Server.Rules.World.IslandLayout)
local ItemCatalog = require(Shared.Items.ItemCatalog)
local Rarity = require(Shared.Items.Rarity)

local function list(...)
	local entries = {}
	for index, rarity in { ... } do
		table.insert(entries, { id = rarity .. index, rarity = rarity })
	end
	return entries
end

test("a category triggers 25% of ticks; each rare type rolls on its own; Common is the fallback", function()
	local rng = Random.new(47)
	local entries = list("Common", "Rare", "Rare", "Epic", "Secret")
	local counts, both, common, trials = {}, 0, 0, 400000
	for _ = 1, trials do
		local results = EventRules.RollCategory(entries, rng)
		local rares = 0
		for _, entry in results do
			counts[entry.id] = (counts[entry.id] or 0) + 1
			rares += if entry.rarity == "Rare" then 1 else 0
			common += if entry.rarity == "Common" then 1 else 0
		end
		both += if rares == 2 then 1 else 0
		for index = 2, #results do
			expect(
				Rarity.Index(results[index - 1].rarity) >= Rarity.Index(results[index].rarity),
				"results come rarest first"
			)
		end
	end
	local trigger, rare, epic, secret = 0.25, 0.12, 0.05, 0.001
	expectNear((counts.Rare2 or 0) / trials, trigger * rare, 0.002, "first Rare type")
	expectNear((counts.Rare3 or 0) / trials, trigger * rare, 0.002, "second Rare type, not halved")
	expectNear((counts.Epic4 or 0) / trials, trigger * epic, 0.0015, "Epic type")
	expectNear((counts.Secret5 or 0) / trials, trigger * secret, 0.00008, "Secret ~0.025% per category per tick")
	expectNear(both / trials, trigger * rare * rare, 0.0008, "both Rare types can start in one tick")
	local none = (1 - rare) * (1 - rare) * (1 - epic) * (1 - secret)
	expectNear(common / trials, trigger * none, 0.003, "Common only when no rarer type hits")
	local hits = 0
	for _ = 1, 40000 do
		hits += if #EventRules.RollCategory(list("Common"), rng) > 0 then 1 else 0
	end
	expectNear(hits / 40000, trigger, 0.01, "a Common-only category triggers 25% of ticks")
end)

test("a category without Common skips when no type hits; ticks gather every result", function()
	local rng = Random.new(53)
	local entries = list("Rare", "Rare")
	local empty, trials = 0, 100000
	for _ = 1, trials do
		empty += if #EventRules.RollCategory(entries, rng) == 0 then 1 else 0
	end
	expectNear(1 - empty / trials, 0.25 * (1 - (1 - 0.12) ^ 2), 0.003, "either Rare type")
	expectEq(#EventRules.RollCategory({}, rng), 0, "an empty category never rolls")

	local catalog = { A = list("Uncommon", "Uncommon", "Uncommon"), B = list("Common"), C = list("Common") }
	local bestA, bestCategories = 0, 0
	for _ = 1, 5000 do
		local results = EventRules.RollTick(catalog, { "A", "B", "C" }, rng)
		local fromA = 0
		for _, entry in results do
			fromA += if entry.rarity == "Uncommon" then 1 else 0
		end
		bestA = math.max(bestA, fromA)
		bestCategories = math.max(bestCategories, #results - fromA + math.min(fromA, 1))
	end
	expect(bestA >= 2, "one category can start several types in one tick")
	expect(bestCategories >= 2, "categories roll independently, so several can start in one tick")
end)

test("rolls are reproducible from an injected rng", function()
	local function run(seed: number)
		local rng, ids = Random.new(seed), {}
		for _ = 1, 2000 do
			for _, entry in EventRules.RollTick(EventCatalog.Entries, EventCatalog.Categories, rng) do
				table.insert(ids, entry.id)
			end
		end
		return table.concat(ids, ",")
	end
	expectEq(run(59), run(59), "same seed, same events")
	expect(#run(59) > 0, "the real catalog produces events")
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
