local Shared = game:GetService("ReplicatedStorage").Shared
local BossCatalog = require(Shared.Bosses.BossCatalog)
local BossRules = require(Shared.Bosses.BossRules)
local BossScaling = require(Shared.Bosses.BossScaling)
local EventCatalog = require(Shared.Events.EventCatalog)
local ItemCatalog = require(Shared.Items.ItemCatalog)

test("the Guardian returns 15–20 minutes after its last encounter with a 3 minute horn", function()
	local rng = Random.new(21)
	for _ = 1, 500 do
		local schedule = BossRules.GuardianSchedule(1000, rng)
		local delay = schedule.spawnAt - 1000
		expect(delay >= 900 and delay <= 1200, "15–20 minutes")
		expectEq(schedule.spawnAt - schedule.hornAt, 180, "3 minute warning")
	end
end)

test("the 25% Legendary is released once per encounter", function()
	expect(BossRules.CrossesLegendary(6500, 6000, 25000), "crossing 25%")
	expect(not BossRules.CrossesLegendary(6000, 5000, 25000), "already below")
	expect(not BossRules.CrossesLegendary(9000, 7000, 25000), "still above")
	local released = {}
	expect(BossRules.ReleaseLegendary(released, "enc1"), "first release")
	expect(not BossRules.ReleaseLegendary(released, "enc1"), "crossing again (healing) cannot duplicate it")
	expect(BossRules.ReleaseLegendary(released, "enc2"), "the next encounter has its own")
end)

test("scaling is clamped and frozen at spawn", function()
	expectEq(BossScaling.Multiplier({}), 0.75, "an empty server is the floor")
	local strong = {}
	for _ = 1, 30 do
		table.insert(strong, { level = 50, gearScore = 1 })
	end
	expectEq(BossScaling.Multiplier(strong), 2.0, "a full veteran server is the ceiling")
	local players = { { level = 25, gearScore = 0.5 }, { level = 40, gearScore = 0.8 } }
	local snapshot = BossScaling.Snapshot(players)
	local before = snapshot.multiplier
	players[1].gearScore = 0
	table.insert(players, { level = 1, gearScore = 0 })
	expectEq(snapshot.multiplier, before, "gear removal and alt joins after spawn change nothing")
	expect(before > 0.75 and before < 2.0, "inside the clamp")
end)

test("gear score rewards better weapons and armor", function()
	local naked = BossScaling.GearScore({})
	local armed = BossScaling.GearScore({
		{ catalogId = "IronSword" },
		{ catalogId = "IronHead" },
		{ catalogId = "IronChest" },
		{ catalogId = "IronLegs" },
	})
	expectEq(naked, 0, "nothing carried")
	expect(armed > 0.7 and armed <= 1, "full iron with a rare sword")
end)

test("each boss source resets by its own rule", function()
	expectEq(BossRules.ResetAction("Event", { idleSeconds = 999 }), nil, "event bosses ignore idling")
	expectEq(
		BossRules.ResetAction("Event", { idleSeconds = 0, eventExpired = true }),
		"Despawn",
		"until the event ends"
	)
	expectEq(BossRules.ResetAction("Structure", { idleSeconds = 31 }), "Heal", "structure bosses heal")
	expectEq(
		BossRules.ResetAction("Structure", { idleSeconds = 0, structureGone = true }),
		"Despawn",
		"with their hold"
	)
	expectEq(BossRules.ResetAction("Ritual", { idleSeconds = 61 }), "Despawn", "ritual bosses leave")
	expectEq(BossRules.ResetAction("Guardian", { idleSeconds = 60 }), nil, "the Guardian waits longer")
	expectEq(BossRules.ResetAction("Guardian", { idleSeconds = 121 }), "Despawn", "then leaves")
end)

test("boss data is consistent", function()
	for id, boss in BossCatalog.Bosses do
		expect(BossCatalog.Sources[boss.source] ~= nil, id .. " source")
		for _, row in boss.loot do
			expect(ItemCatalog.Get(row[1]) ~= nil, id .. " loot " .. row[1])
		end
	end
	local legendary = ItemCatalog.Get(BossCatalog.Bosses.Guardian.legendary)
	expectEq(legendary.rarity, "Legendary", "the Guardian drops a Legendary")
	expectEq(BossCatalog.Bosses.Guardian.health, 25000, "baseline")
end)

test("event and structure bosses name real bosses of the right source", function()
	for _, entry in EventCatalog.ById do
		if entry.boss then
			local boss = BossCatalog.Get(entry.boss)
			expect(boss ~= nil, entry.id .. " boss")
			local expected = if entry.kind == "Boss" then "Event" else "Structure"
			expectEq(boss.source, expected, entry.id .. " source")
		end
	end
	expectEq(BossCatalog.Get(BossCatalog.Ritual.boss).source, "Ritual", "ritual boss")
end)
