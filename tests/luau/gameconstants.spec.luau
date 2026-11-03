local GameConstants = require(game:GetService("ReplicatedStorage").Shared.GameConstants)
local Tiers = require(game:GetService("ReplicatedStorage").Shared.Items.Tiers)

-- The full Hide → Adamantine EHP ladder is checked through ArmorRules in combat.spec.luau.
test("full armor sets give the confirmed EHP at 100 base HP and pieces add", function()
	expectEq(GameConstants.BASE_MAX_HEALTH, 100, "100 base HP")
	-- The confirmed anchors (Q134): Hide ×1.2 and Iron ×2.0.
	for set, ehp in { Hide = 120, Iron = 200 } do
		local factor = GameConstants.ARMOR_SET_FACTOR[set]
		expectNear(GameConstants.BASE_MAX_HEALTH * factor, ehp, 1e-9, set .. " full-set EHP")
		expectEq(Tiers.ArmorFactor(Tiers.Get(set)), factor, set .. " ladder uses the confirmed anchor")
	end
	-- Wood and Stone armor are removed (GDD §51).
	for _, set in { "Wood", "Stone" } do
		expectEq(GameConstants.ARMOR_SET_FACTOR[set], nil, "no " .. set .. " armor")
		expectEq(Tiers.ArmorFactor(Tiers.Get(set)), nil, set .. " makes no armor")
	end
	local factor = GameConstants.ArmorFactor({ 1 / 3, 1 / 3, 1 / 3 })
	expectNear(factor, GameConstants.ARMOR_SET_FACTOR.Iron, 1e-9, "three iron thirds add to x2.0")
	expectEq(GameConstants.ArmorFactor({}), 1, "unarmored factor")
end)

test("damage and revive go through effective HP and come back as actual HP", function()
	expectNear(GameConstants.ApplyDamage(100, 2, 50), 75, 1e-9, "50 raw damage on full iron")
	expectEq(GameConstants.ApplyDamage(10, 1, 50), 0, "never below zero")
	expectNear(GameConstants.ApplyDamage(20, 1.2, 12), 10, 1e-9, "downed pool keeps armor")
	-- Revive restores 10% of max EHP as actual HP.
	expectNear(GameConstants.RevivedHealth(100, 2), 10, 1e-9, "100 HP full iron")
	expectNear(GameConstants.RevivedHealth(150, 2), 15, 1e-9, "150 HP full iron")
end)

test("food healing halves on hit and cancels at the cutoff; food slows strictly below 25%", function()
	expectEq(GameConstants.FoodHealAfterHit(40), 20, "40 pending -> 20")
	expectEq(GameConstants.FoodHealAfterHit(20), 0, "20 pending -> 10 -> cancelled")
	expectEq(GameConstants.FoodHealAfterHit(22), 11, "just above the cutoff survives")
	expect(not GameConstants.IsFoodSlowed(0.25), "exactly 25% is not slowed")
	expect(GameConstants.IsFoodSlowed(0.2499), "just below 25% is slowed")
	expect(GameConstants.IsFoodSlowed(0), "0% is slowed")
	expectNear(GameConstants.FOOD_SLOW_MULTIPLIER, 0.9, 1e-9, "the only penalty is -10% speed")
end)

test("vault slots grow by upgrade; secure material stacks cap at 1,000 and delete the overflow", function()
	expectEq(GameConstants.VaultSlots(0), 25, "starting vault")
	expectEq(GameConstants.VaultSlots(2), 75, "two upgrades")
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
