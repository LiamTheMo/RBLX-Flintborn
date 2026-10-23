local GameConstants = require(game:GetService("ReplicatedStorage").Shared.GameConstants)

test("full armor sets give the confirmed EHP at 100 base HP", function()
	local expected = { Hide = 120, Wood = 150, Stone = 180, Iron = 200 }
	for set, ehp in expected do
		local factor = GameConstants.ARMOR_SET_FACTOR[set]
		expectNear(GameConstants.BASE_MAX_HEALTH * factor, ehp, 1e-9, set .. " full-set EHP")
	end
end)

test("armor pieces add instead of multiplying", function()
	local factor = GameConstants.ArmorFactor({ 1 / 3, 1 / 3, 1 / 3 })
	expectNear(factor, GameConstants.ARMOR_SET_FACTOR.Iron, 1e-9, "three iron thirds add to x2.0")
	expectEq(GameConstants.ArmorFactor({}), 1, "unarmored factor")
end)

test("damage goes through effective HP and comes back as actual HP", function()
	expectNear(GameConstants.ApplyDamage(100, 2, 50), 75, 1e-9, "50 raw damage on full iron")
	expectEq(GameConstants.ApplyDamage(10, 1, 50), 0, "never below zero")
	expectNear(GameConstants.ApplyDamage(20, 1.2, 12), 10, 1e-9, "downed pool keeps armor")
end)

test("revive restores 10% of max EHP as actual HP", function()
	expectNear(GameConstants.RevivedHealth(100, 2), 10, 1e-9, "100 HP full iron")
	expectNear(GameConstants.RevivedHealth(150, 2), 15, 1e-9, "150 HP full iron")
end)

test("food healing halves on hit and cancels at the cutoff", function()
	expectEq(GameConstants.FoodHealAfterHit(40), 20, "40 pending -> 20")
	expectEq(GameConstants.FoodHealAfterHit(20), 0, "20 pending -> 10 -> cancelled")
	expectEq(GameConstants.FoodHealAfterHit(22), 11, "just above the cutoff survives")
end)

test("food slows strictly below 25% and 0% adds nothing more", function()
	expect(not GameConstants.IsFoodSlowed(0.25), "exactly 25% is not slowed")
	expect(GameConstants.IsFoodSlowed(0.2499), "just below 25% is slowed")
	expect(GameConstants.IsFoodSlowed(0), "0% is slowed")
	expectNear(GameConstants.FOOD_SLOW_MULTIPLIER, 0.9, 1e-9, "the only penalty is -10% speed")
end)

test("secure material stacks cap at 1,000 and delete the overflow", function()
	local stored, deleted = GameConstants.SettleMaterialStack(0, 600 * GameConstants.CENTER_MULTIPLIER)
	expectEq(stored, 1000, "600 doubled stores 1,000")
	expectEq(deleted, 200, "and deletes 200")
	stored, deleted = GameConstants.SettleMaterialStack(400, 100)
	expectEq(stored, 500, "under the cap stores everything")
	expectEq(deleted, 0, "nothing deleted under the cap")
end)

test("crafting mastery raises the best-roll chance relatively", function()
	expectNear(GameConstants.BestRollChance(0.01, 0), 0.01, 1e-12, "level 0")
	expectNear(GameConstants.BestRollChance(0.01, 1), 0.0105, 1e-12, "level 1 is 1.05%")
	expectNear(GameConstants.BestRollChance(0.01, 10), 0.015, 1e-12, "level 10 is 1.5%")
	expectEq(GameConstants.BestRollChance(0.99, 10), 1, "never above 100%")
end)

test("inventory, vault and world limits match the GDD", function()
	expectEq(GameConstants.HOTBAR_SLOTS, 9, "hotbar")
	expectEq(GameConstants.BACKPACK_SLOTS, 50, "backpack")
	expectEq(GameConstants.VaultSlots(0), 25, "starting vault")
	expectEq(GameConstants.VaultSlots(2), 75, "two upgrades")
	expectEq(#GameConstants.MASTERY_TRACKS, 5, "five mastery tracks")
	expectEq(#GameConstants.RARITIES, 8, "eight rarities")
	expectEq(GameConstants.TOTEM_HEALTH_BY_LEVEL[3], 2500, "level 3 totem")
end)

test("medicine heals grow with their animation lock", function()
	local previous = nil
	for _, tier in { "Basic", "Advanced", "Potion" } do
		local medicine = GameConstants.MEDICINE[tier]
		if previous then
			expect(medicine.heal > previous.heal, tier .. " heals more")
			expect(medicine.animationSeconds > previous.animationSeconds, tier .. " locks longer")
		end
		previous = medicine
	end
end)
