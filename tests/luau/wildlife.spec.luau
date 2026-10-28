-- Creature roster, behaviour and roaming wildlife (GDD §54, owner decisions 2026-10-28).
local Shared = game:GetService("ReplicatedStorage").Shared
local AggroRules = require(Shared.Enemies.AggroRules)
local BiomeCatalog = require(Shared.World.BiomeCatalog)
local EnemyCatalog = require(Shared.Enemies.EnemyCatalog)
local ItemCatalog = require(Shared.Items.ItemCatalog)
local WildlifeRules = require(Shared.Enemies.WildlifeRules)

-- The map's zones, as the world layout names them (BiomeCatalog.ZONE_IDS).
local ZONE_IDS = {
	"Rimlands",
	"PinewoodWilds",
	"MosswickForest",
	"EmberhollowCaves",
	"FrostpeakRidge",
	"FallenTemple",
	"Timberwatch",
	"Riverlands",
	"CraterLake",
	"ShatteredKeep",
}

local ROSTER = {
	WildBoar = { "Regular", "Neutral" },
	ForestStag = { "Regular", "Passive" },
	GreyWolf = { "Regular", "Hostile" },
	BrownBear = { "Regular", "Neutral" },
	RiverCrocodile = { "Regular", "Hostile" },
	PlainsBison = { "Regular", "Neutral" },
	MeadowRabbit = { "Regular", "Passive" },
	IslandDodo = { "Regular", "Passive" },
	RiverCapybara = { "Regular", "Passive" },
	HighlandGoat = { "Regular", "Passive" },
	ForestTapir = { "Regular", "Passive" },
	GiantGroundSloth = { "RareEvent", "Passive" },
	SaberToothedTiger = { "EventElite", "Hostile" },
	WoollyMammoth = { "EventWildlife", "Neutral" },
	IronTuskBoar = { "EventAlpha", "Hostile" },
	AncientTortoise = { "RareEvent", "Passive" },
	StonehideRhino = { "EventElite", "Neutral" },
}

local function amount(drops, catalogId: string): number
	for _, row in drops do
		if row[1] == catalogId then
			return (row[2] + row[3]) / 2 * row[4]
		end
	end
	return 0
end

test("the owner roster is in the catalog with its type and behaviour", function()
	for enemyId, expected in ROSTER do
		local enemy = EnemyCatalog.Get(enemyId)
		assert(enemy, "missing " .. enemyId)
		expectEq(enemy.role, expected[1], enemyId .. " role")
		expectEq(enemy.behaviour, expected[2], enemyId .. " behaviour")
		expect(EnemyCatalog.SizeClasses[enemy.sizeClass] ~= nil, enemyId .. " has a size class")
	end
	for _, oldId in { "Wolf", "Boar", "Sabertooth", "Bandit" } do
		expectEq(EnemyCatalog.Get(oldId), nil, oldId .. " is renamed or removed")
	end
	for _, kept in { "Skeleton", "KeepSkeleton", "EmberWisp" } do
		expectEq(EnemyCatalog.Get(kept).behaviour, "Hostile", kept .. " stays hostile")
	end
end)

test("every creature is well formed; passives never deal damage", function()
	for enemyId, enemy in EnemyCatalog.Enemies do
		expect(EnemyCatalog.Behaviours[enemy.behaviour] ~= nil, enemyId .. " behaviour")
		expect(EnemyCatalog.Roles[enemy.role] ~= nil, enemyId .. " role")
		expect(table.find(EnemyCatalog.Themes, enemy.theme) ~= nil, enemyId .. " theme")
		expect(enemy.health > 0 and enemy.speed > 0 and enemy.reach > 0 and enemy.cooldown > 0, enemyId .. " stats")
		expect(enemy.size.X > 0 and enemy.size.Y > 0 and enemy.size.Z > 0, enemyId .. " body")
		for _, row in enemy.drops do
			expect(ItemCatalog.Get(row[1]) ~= nil, enemyId .. " drop " .. row[1])
			expect(row[2] <= row[3] and row[4] > 0 and row[4] <= 1, enemyId .. " drop row " .. row[1])
		end
		if enemy.behaviour == "Passive" then
			expectEq(enemy.damage, 0, enemyId .. " never deals damage")
		else
			expect(enemy.damage > 0, enemyId .. " can fight")
		end
	end
end)

test("drops follow size; event elites carry the elite materials", function()
	local means = { Small = {}, Medium = {}, Large = {} }
	for enemyId, enemy in EnemyCatalog.Enemies do
		local class = enemy.sizeClass
		if class then
			local meat, hide, bone =
				amount(enemy.drops, "RawMeat"), amount(enemy.drops, "Hide"), amount(enemy.drops, "Bone")
			expect(meat > 0 and hide > 0, enemyId .. " gives meat and hide")
			if class == "Small" then
				expectEq(bone, 0, enemyId .. " is too small for bone")
				expect(hide < meat, enemyId .. " gives only a little hide")
			else
				expect(bone > 0, enemyId .. " gives bone")
			end
			table.insert(means[class], meat + hide + bone)
		end
		local elite = enemy.role == "EventElite" or enemy.role == "EventAlpha"
		expectEq(enemy.elite == true, elite, enemyId .. " elite drops")
	end
	local function lowest(list)
		return math.min(table.unpack(list))
	end
	local function highest(list)
		return math.max(table.unpack(list))
	end
	expect(highest(means.Small) < lowest(means.Medium), "small < medium")
	expect(highest(means.Medium) < lowest(means.Large), "medium < large")
	local elites = {}
	for _, row in EnemyCatalog.ELITE_DROPS do
		elites[row[1]] = true
	end
	expect(elites.DireHide and elites.ChargedCore and elites.GlowFur, "Dire Hide, Charged Core and Glow-Fur")
end)

test("spawn tables cover every zone with its regular creatures in real habitats", function()
	for zoneId, zone in WildlifeRules.Zones do
		expect(table.find(ZONE_IDS, zoneId) ~= nil, zoneId .. " is a map zone")
		expect(zone.groups >= 2 and zone.groups <= 4, zoneId .. " keeps 2-4 groups")
		expect(#zone.spawns > 0, zoneId .. " has a spawn table")
		for _, entry in zone.spawns do
			local enemy = EnemyCatalog.Get(entry.enemy)
			assert(enemy, zoneId .. " spawns unknown " .. tostring(entry.enemy))
			expectEq(enemy.role, "Regular", zoneId .. " " .. entry.enemy .. " roams")
			expect(entry.weight > 0, zoneId .. " " .. entry.enemy .. " weight")
			expect(entry.min >= 1 and entry.min <= entry.max and entry.max <= 3, entry.enemy .. " small group")
			if entry.habitat then
				expect(table.find(WildlifeRules.HABITATS, entry.habitat) ~= nil, entry.enemy .. " " .. entry.habitat)
				-- Once the map describes its zones, the habitat must be one the zone has.
				local mapped = BiomeCatalog.Zones and BiomeCatalog.Zones[zoneId]
				if mapped and mapped.habitats then
					expect(
						table.find(mapped.habitats, entry.habitat) ~= nil,
						zoneId .. " has no " .. entry.habitat .. " for " .. entry.enemy
					)
				end
			end
		end
	end
	for _, zoneId in ZONE_IDS do
		expect(WildlifeRules.Zones[zoneId] ~= nil, zoneId .. " has wildlife")
	end
	-- Each regular creature roams somewhere.
	local roams = {}
	for _, zone in WildlifeRules.Zones do
		for _, entry in zone.spawns do
			roams[entry.enemy] = true
		end
	end
	for enemyId, enemy in EnemyCatalog.Enemies do
		if enemy.role == "Regular" then
			expect(roams[enemyId], enemyId .. " roams in some zone")
		end
	end
end)

test("creatures live where the owner put them", function()
	local function zonesOf(enemyId: string)
		local found = {}
		for zoneId, zone in WildlifeRules.Zones do
			for _, entry in zone.spawns do
				if entry.enemy == enemyId then
					found[zoneId] = true
				end
			end
		end
		return found
	end
	expect(zonesOf("RiverCrocodile").Riverlands and zonesOf("RiverCrocodile").CraterLake, "crocodiles by water")
	expect(zonesOf("RiverCapybara").Riverlands and zonesOf("RiverCapybara").CraterLake, "capybaras by water")
	expect(zonesOf("HighlandGoat").FrostpeakRidge, "goats on Frostpeak")
	expect(zonesOf("Skeleton").FallenTemple, "skeletons roam the Fallen Temple")
	expect(zonesOf("KeepSkeleton").ShatteredKeep, "and guard the Shattered Keep")
	expect(zonesOf("EmberWisp").EmberhollowCaves, "wisps in the caves")
	expect(zonesOf("IslandDodo").Rimlands, "dodos on the beaches")
	local inner = { Timberwatch = true, FallenTemple = true, EmberhollowCaves = true }
	for zoneId in zonesOf("GreyWolf") do
		expect(inner[zoneId] or zoneId == "FrostpeakRidge", "no wolves in the Outer Rim: " .. zoneId)
	end
end)

test("light density: about 40-60 roaming creatures under a hard cap", function()
	local expected = WildlifeRules.ExpectedCreatures()
	expect(expected >= 40 and expected <= 60, ("expected %.1f creatures"):format(expected))
	expect(WildlifeRules.MAX_CREATURES >= 40 and WildlifeRules.MAX_CREATURES <= 60, "cap")
	expectEq(WildlifeRules.RESPAWN_SECONDS, 180, "groups return after about three minutes")
	expectEq(WildlifeRules.PLAYER_CLEARANCE, 150, "away from players")
	local slots = WildlifeRules.Slots()
	local total = 0
	for _, zone in WildlifeRules.Zones do
		total += zone.groups
	end
	expectEq(#slots, total, "one slot per group")
	expect(WildlifeRules.HasRoom(WildlifeRules.MAX_CREATURES - 3, 3), "fits exactly")
	expect(not WildlifeRules.HasRoom(WildlifeRules.MAX_CREATURES - 2, 3), "never over the cap")
end)

test("spawn picks follow the weights", function()
	local rng = Random.new(54)
	local spawns = { { enemy = "A", weight = 3, min = 1, max = 3 }, { enemy = "B", weight = 1, min = 2, max = 2 } }
	local hits, trials = 0, 20000
	for _ = 1, trials do
		if WildlifeRules.Pick(spawns, rng).enemy == "A" then
			hits += 1
		end
		local size = WildlifeRules.GroupSize(spawns[1], rng)
		expect(size >= 1 and size <= 3, "group size in range")
	end
	expectNear(hits / trials, 0.75, 0.02, "weight 3 of 4")
end)

test("groups appear away from players and far groups make room", function()
	local spot = Vector3.new(0, 10, 0)
	expect(WildlifeRules.ClearOfPlayers(spot, {}), "nobody around")
	expect(not WildlifeRules.ClearOfPlayers(spot, { Vector3.new(149, 0, 0) }), "too close")
	expect(WildlifeRules.ClearOfPlayers(spot, { Vector3.new(151, 0, 0) }), "far enough")
	expect(WildlifeRules.AnyNear({ spot }, { Vector3.new(0, 0, 399) }, 400), "near")
	expect(not WildlifeRules.AnyNear({ spot }, { Vector3.new(0, 0, 401) }, 400), "far")
	local fresh, stale, older = { lastNear = 900 }, { lastNear = 600 }, { lastNear = 500 }
	expectEq(WildlifeRules.MostIdle({ fresh, stale, older }, 1000), older, "the longest-idle group goes first")
	expectEq(WildlifeRules.MostIdle({ fresh }, 1000), nil, "a recently visited group stays")
end)

test("neutral groups fight back at their attacker, then calm down", function()
	local group = AggroRules.NewGroup()
	local attacker, bystander = {}, {}
	expect(not AggroRules.Hunts("Neutral", group, attacker, 0), "ignores players at first")
	AggroRules.Anger(group, attacker, 10)
	expect(AggroRules.Hunts("Neutral", group, attacker, 11), "the whole group fights back")
	expect(not AggroRules.Hunts("Neutral", group, bystander, 11), "only at the attacker")
	expect(AggroRules.Hunts("Neutral", group, attacker, 10 + AggroRules.CALM_SECONDS), "still angry")
	expect(not AggroRules.Hunts("Neutral", group, attacker, 11 + AggroRules.CALM_SECONDS), "calms down")
	expectEq(group.angry[attacker], nil, "and forgets")
	expect(AggroRules.Hunts("Hostile", group, bystander, 0), "hostile creatures attack on sight")
	AggroRules.Anger(group, bystander, 0)
	expect(not AggroRules.Hunts("Passive", group, bystander, 0), "passive creatures never attack")
end)

test("passive creatures run away and stay near home", function()
	local home = Vector3.new(0, 0, 0)
	expectEq(AggroRules.FleeGoal(home, {}, home, 90), nil, "nothing to run from")
	local goal = AggroRules.FleeGoal(Vector3.new(10, 0, 0), { Vector3.new(0, 0, 0) }, home, 90)
	expect(goal.X > 10, "away from the player")
	-- Cornered at the leash, it slips sideways rather than standing still.
	local edge = Vector3.new(90, 0, 0)
	local side = AggroRules.FleeGoal(edge, { Vector3.new(80, 0, 0) }, home, 90)
	expect(math.sqrt(side.X * side.X + side.Z * side.Z) <= 90 + 1e-6, "inside the leash")
	expect(math.abs(side.Z) > 5, "sideways")
	local rng = Random.new(3)
	for _ = 1, 200 do
		local amble = AggroRules.WanderGoal(home, Vector3.new(200, 0, 0), rng)
		expect(math.sqrt(amble.X * amble.X + amble.Z * amble.Z) <= AggroRules.WANDER_RADIUS, "ambles near home")
	end
end)
