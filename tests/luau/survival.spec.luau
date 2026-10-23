local Shared = game:GetService("ReplicatedStorage").Shared
local SurvivalRules = require(Shared.Survival.SurvivalRules)
local Consumables = require(Shared.Items.Consumables)

local function run(fn, seconds, dt)
	local steps = math.round(seconds / dt)
	for _ = 1, steps do
		fn(dt)
	end
end

test("a full stamina bar lasts 3 s of sprint and refills in 5 s", function()
	local state = SurvivalRules.NewState()
	state.sprintIntent = true
	run(function(dt)
		SurvivalRules.StepStamina(state, dt, true)
	end, 2.9, 0.1)
	expect(state.stamina > 0, "still has stamina at 2.9 s")
	expect(SurvivalRules.IsSprinting(state, true), "still sprinting")
	run(function(dt)
		SurvivalRules.StepStamina(state, dt, true)
	end, 0.1, 0.1)
	expectNear(state.stamina, 0, 1e-9, "empty at 3 s")
	expect(not SurvivalRules.IsSprinting(state, true), "sprint stops when empty")

	state.sprintIntent = false
	run(function(dt)
		SurvivalRules.StepStamina(state, dt, true)
	end, 5, 0.1)
	expectNear(state.stamina, 1, 1e-9, "full again after 5 s")
end)

test("only sprinting spends stamina", function()
	local state = SurvivalRules.NewState()
	state.stamina = 0.5
	SurvivalRules.StepStamina(state, 1, true)
	expect(state.stamina > 0.5, "walking regenerates")
	state.stamina = 0.5
	state.sprintIntent = true
	SurvivalRules.StepStamina(state, 1, false)
	expect(state.stamina > 0.5, "standing still with sprint held regenerates")
	state.stamina = 0.5
	state.crouching = true
	SurvivalRules.StepStamina(state, 1, true)
	expect(state.stamina > 0.5, "crouching never spends stamina")
end)

test("food empties in 300 s and slows strictly below 25% with nothing worse at 0%", function()
	local state = SurvivalRules.NewState()
	run(function(dt)
		SurvivalRules.StepFood(state, dt)
	end, 300, 1)
	expectNear(state.food, 0, 1e-9, "empty after 300 s")
	expectNear(SurvivalRules.MoveSpeed(state, true), SurvivalRules.WALK_SPEED * 0.9, 1e-9, "only -10% at 0%")

	state.food = 0.25
	expectEq(SurvivalRules.MoveSpeed(state, true), SurvivalRules.WALK_SPEED, "exactly 25% is not slowed")
	state.food = 0.2499
	expectNear(SurvivalRules.MoveSpeed(state, true), SurvivalRules.WALK_SPEED * 0.9, 1e-9, "below 25% is slowed")
end)

test("crouch and sprint speeds", function()
	local state = SurvivalRules.NewState()
	state.sprintIntent = true
	expectEq(SurvivalRules.MoveSpeed(state, true), SurvivalRules.SPRINT_SPEED, "sprint")
	state.crouching = true
	expectEq(SurvivalRules.MoveSpeed(state, true), SurvivalRules.CROUCH_SPEED, "crouch wins over sprint")
end)

test("medicine heals at once, caps at max HP and locks for its animation", function()
	local state = SurvivalRules.NewState()
	local basic = Consumables.Get("BasicMedicine")
	expectEq(SurvivalRules.UseMedicine(state, basic, 50, 100, 0), 60, "+10 immediately")
	expectEq(SurvivalRules.UseMedicine(state, basic, 60, 100, 0.4), nil, "locked during the 0.5 s animation")
	expectEq(SurvivalRules.UseMedicine(state, basic, 60, 100, 0.5), 70, "usable when the animation ends")

	local potion = Consumables.Get("Potion")
	expectEq(SurvivalRules.UseMedicine(state, potion, 80, 100, 10), 100, "capped at max HP")
	expectEq(state.medicineLockUntil, 11.5, "potion locks for 1.5 s")
	local advanced = Consumables.Get("AdvancedMedicine")
	expectEq(advanced.heal, 25, "advanced heals 25")
	expectEq(advanced.animationSeconds, 1, "advanced locks 1 s")
end)

test("food restores hunger and heals its total over exactly 10 s", function()
	local state = SurvivalRules.NewState()
	state.food = 0.5
	SurvivalRules.Eat(state, Consumables.Get("CookedMeat"), 0)
	expectNear(state.food, 0.85, 1e-9, "+35% hunger")
	local healed, now = 0, 0
	for _ = 1, 100 do
		healed += SurvivalRules.StepFoodHeals(state, now, 0.1)
		now += 0.1
	end
	expectNear(healed, 30, 1e-6, "cooked meat heals 30")
	expectEq(#state.foodHeals, 0, "finished after 10 s")
end)

test("a hit halves pending food healing and cancels it at 10 HP or less", function()
	local state = SurvivalRules.NewState()
	state.foodHeals = { { remaining = 40, endsAt = 10 } }
	SurvivalRules.OnDamaged(state)
	expectEq(state.foodHeals[1].remaining, 20, "40 -> 20")
	SurvivalRules.OnDamaged(state)
	expectEq(#state.foodHeals, 0, "20 -> 10 is cancelled")
end)

test("food heals stack with each other and with medicine", function()
	local state = SurvivalRules.NewState()
	SurvivalRules.Eat(state, Consumables.Get("CookedMeat"), 0)
	SurvivalRules.Eat(state, Consumables.Get("CookedMeat"), 0)
	expectEq(#state.foodHeals, 2, "two heals at once")
	expectEq(SurvivalRules.PendingFoodHealing(state), 60, "60 pending")
	expect(SurvivalRules.UseMedicine(state, Consumables.Get("BasicMedicine"), 50, 100, 0) == 60, "medicine still works")
	SurvivalRules.OnDamaged(state)
	expectEq(SurvivalRules.PendingFoodHealing(state), 30, "each heal halved separately")
end)

test("downed players lose pending food healing", function()
	local state = SurvivalRules.NewState()
	SurvivalRules.Eat(state, Consumables.Get("Berries"), 0)
	SurvivalRules.OnDowned(state)
	expectEq(SurvivalRules.PendingFoodHealing(state), 0, "cleared")
end)
