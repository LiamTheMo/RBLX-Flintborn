local Shared = game:GetService("ReplicatedStorage").Shared
local EnemyCatalog = require(Shared.Enemies.EnemyCatalog)
local EventCatalog = require(Shared.Events.EventCatalog)
local EventRules = require(Shared.Events.EventRules)
local ItemCatalog = require(Shared.Items.ItemCatalog)

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
		if EventRules.RollCategory(list, rng) then
			hits += 1
		end
	end
	expectNear(hits / trials, 0.25, 0.01, "trigger rate")
end)

test("the waterfall tries Secret first and falls back to Common", function()
	local rng = Random.new(13)
	local list = entries("Common", "Secret")
	local secret, common, trials = 0, 0, 400000
	for _ = 1, trials do
		local entry = EventRules.RollCategory(list, rng)
		if entry and entry.rarity == "Secret" then
			secret += 1
		elseif entry then
			common += 1
		end
	end
	expectNear(secret / trials, 0.00025, 0.00008, "Secret ~0.025% per category per tick")
	expectNear(common / trials, 0.25 * 0.999, 0.01, "everything else falls back to Common")
end)

test("a category with no Common skips when nothing rarer hits", function()
	local rng = Random.new(14)
	local list = entries("Rare")
	local hits, trials = 0, 100000
	for _ = 1, trials do
		if EventRules.RollCategory(list, rng) then
			hits += 1
		end
	end
	expectNear(hits / trials, 0.25 * 0.12, 0.004, "only the Rare roll can produce an event")
	expectEq(EventRules.RollCategory({}, rng), nil, "empty categories (bosses until v0.12) never roll")
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

test("biome distances stay inside their ring", function()
	local rng = Random.new(15)
	for _ = 1, 500 do
		local d = EventRules.BiomeDistance("InnerRing", rng)
		expect(d >= 0.3 and d <= 0.65, "inside the inner ring")
	end
end)

test("the catalog is consistent: real items, real enemies, all six themes", function()
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
