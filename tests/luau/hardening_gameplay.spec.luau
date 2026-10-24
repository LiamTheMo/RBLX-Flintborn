-- Gameplay and anti-cheat hardening (GDD §3.2, §5.1, §6, §7, §8, §21, §24). Pure
-- pieces behind the server fixes: movement blinks and walk-speed limits, buried
-- placements, bow draw time, provoked enemies, event keep-out zones, crop XP caps
-- and channels that the server interrupts on its own.
local Server = game:GetService("ServerScriptService").Server
local Shared = game:GetService("ReplicatedStorage").Shared
local AggroRules = require(Shared.Enemies.AggroRules)
local BuildRules = require(Shared.Building.BuildRules)
local Channel = require(Server.Infrastructure.Channel)
local DamageRules = require(Shared.Combat.DamageRules)
local EventRules = require(Shared.Events.EventRules)
local MovementRules = require(Shared.Security.MovementRules)
local Signal = require(Shared.Core.Signal)
local StructureCatalog = require(Shared.Building.StructureCatalog)
local SurvivalRules = require(Shared.Survival.SurvivalRules)
local WeaponCatalog = require(Shared.Combat.WeaponCatalog)

-- Movement ----------------------------------------------------------------------

test("a far jump is a blink, pulled back without a forgiven sample", function()
	local from = Vector3.new(0, 10, 0)
	local walk = MovementRules.AllowedSpeed(false, SurvivalRules.WALK_SPEED)
	expect(not MovementRules.Blink(from, Vector3.new(14, 10, 0), 0.25, walk), "a small overrun only strikes")
	expect(MovementRules.Blink(from, Vector3.new(60, 10, 0), 0.25, walk), "60 studs in a quarter second")
	local verdict = MovementRules.Judge(MovementRules.ALLOWANCE, from, Vector3.new(60, 10, 0), 0.25, walk)
	expectEq(verdict, "Blink", "judged as a blink")
end)

test("the speed limit is the walk speed the server set, not the sprint speed", function()
	expectEq(MovementRules.AllowedSpeed(false, 16), 16, "walking")
	expectEq(MovementRules.AllowedSpeed(false, 16, 24), 24, "a sprint that just ended still counts for a sample")
	expectEq(MovementRules.AllowedSpeed(true, 24), MovementRules.CRAWL_SPEED, "downed players crawl")
	expectEq(MovementRules.AllowedSpeed(false, nil), MovementRules.MaxSpeed(false), "no humanoid: the fastest legal")
end)

test("sustained over-speed spends the latency budget; legal sprinting never does", function()
	local function run(speed: number, allowed: number, samples: number): string?
		local slack, position = MovementRules.ALLOWANCE, Vector3.new(0, 0, 0)
		for _ = 1, samples do
			local nextPosition = position + Vector3.new(speed * 0.25, 0, 0)
			local verdict, remaining = MovementRules.Judge(slack, position, nextPosition, 0.25, allowed)
			if verdict ~= "Ok" then
				return verdict
			end
			slack, position = remaining, nextPosition
		end
		return nil
	end
	expectEq(run(SurvivalRules.SPRINT_SPEED, SurvivalRules.SPRINT_SPEED, 200), nil, "sprinting for 50 s")
	expectEq(run(SurvivalRules.WALK_SPEED, SurvivalRules.WALK_SPEED, 200), nil, "walking for 50 s")
	expectEq(run(SurvivalRules.SPRINT_SPEED * 1.2, SurvivalRules.WALK_SPEED, 40), "Over", "sprint speed while walking")
	expectEq(run(40, SurvivalRules.SPRINT_SPEED, 40), "Over", "40 studs/s, once each sample's slack is gone")
	local _, slack = MovementRules.Judge(MovementRules.ALLOWANCE, Vector3.zero, Vector3.new(9, 0, 0), 0.25, 16)
	expect(slack < MovementRules.ALLOWANCE, "one burst spends slack")
	local _, refilled = MovementRules.Judge(slack, Vector3.zero, Vector3.new(1, 0, 0), 0.25, 16)
	expect(refilled > slack, "slower samples refill it")
end)

test("travel at sprint pace drains stamina without a sprint request", function()
	local function observe(speed: number, walkPace: number?): boolean
		local pace = SurvivalRules.NewPace()
		local observed = false
		for _ = 1, 5 do
			observed = SurvivalRules.ObservePace(pace, speed * 0.2, 0.2, SurvivalRules.WALK_SPEED, walkPace)
		end
		return observed
	end
	local state = SurvivalRules.NewState()
	SurvivalRules.StepStamina(state, 1, true, observe(SurvivalRules.SPRINT_SPEED))
	expect(state.stamina < 1, "no free sprint by never asking to")
	local walker = SurvivalRules.NewState()
	walker.stamina = 0.5
	SurvivalRules.StepStamina(walker, 1, true, observe(SurvivalRules.WALK_SPEED))
	expect(walker.stamina > 0.5, "walking still recovers")
	expect(not observe(20, SurvivalRules.WALK_SPEED * 1.5), "a fast swimmer is not sprinting")
end)

-- Building ----------------------------------------------------------------------

test("a piece must stand clear of the ground above its bottom stud", function()
	local half = BuildRules.HalfExtents(StructureCatalog.Pieces.Totem.size, 0)
	local base = Vector3.new(0, 10, 0)
	local center = base + Vector3.new(0, half.Y, 0)
	local boxCenter, boxSize = BuildRules.ClearanceBox(center, half)
	local bottom, top = boxCenter.Y - boxSize.Y / 2, boxCenter.Y + boxSize.Y / 2
	expectNear(bottom, base.Y + BuildRules.GROUND_ALLOWANCE, 1e-6, "may sit one stud into slopes")
	expect(top < base.Y + half.Y * 2 and top > base.Y + half.Y * 2 - 0.5, "reaches the top of the totem")
	expect(boxSize.X < half.X * 2 and boxSize.Z < half.Z * 2, "inset so flush neighbours fit")
	local floorHalf = BuildRules.HalfExtents(StructureCatalog.Pieces.Floor.size, 0)
	local _, floorSize = BuildRules.ClearanceBox(Vector3.new(0, 0.5, 0), floorHalf)
	expect(floorSize.Y > 0, "thin pieces still get a box")
end)

test("safe-zone tests cover every corner of the footprint, not just its centre", function()
	local center, half = Vector3.new(0, 4, 0), Vector3.new(4, 4, 0.5)
	local points = BuildRules.FootprintPoints(center, half)
	expectEq(#points, 15, "centre, 8 corners, 6 faces")
	local corner = Vector3.new(4, 0, 0.5)
	local found = false
	for _, point in points do
		if point == corner then
			found = true
		end
	end
	expect(found, "a bottom corner is sampled")
	expect(BuildRules.BoxContains(center, half, Vector3.new(3.9, 1, 0)), "a small zone inside the piece")
	expect(not BuildRules.BoxContains(center, half, Vector3.new(4.1, 1, 0)), "outside the footprint")
end)

test("the builder must see the spot; each owner keeps at most three totems", function()
	expect(BuildRules.InSight(nil, 20), "nothing in the way")
	expect(BuildRules.InSight(19, 20), "the ray grazes the ground at the base")
	expect(not BuildRules.InSight(8, 20), "a wall or the ground hides the spot")
	local totems = {}
	for index = 1, BuildRules.MAX_TOTEMS_PER_OWNER do
		table.insert(totems, { ownerKey = "tribe:a", position = Vector3.new(index * 100, 0, 0), radius = 15 })
	end
	expect(BuildRules.TotemLimitReached(totems, "tribe:a"), "three is the cap")
	expect(not BuildRules.TotemLimitReached(totems, "solo:7"), "per owner")
end)

test("a totem change only reconciles structures inside its radius", function()
	local totem = { position = Vector3.new(0, 0, 0), radius = 15 }
	local near = { position = Vector3.new(10, 50, 0) }
	local far = { position = Vector3.new(40, 0, 0) }
	local list = BuildRules.WithinTotem({ near, far }, totem)
	expectEq(#list, 1, "one structure in range")
	expectEq(list[1], near, "the near one, whatever its height")
end)

test("crop XP is capped per player per window, however many planters", function()
	local ledger = {}
	local granted = 0
	for _ = 1, 300 do
		if BuildRules.TakeCropCredit(ledger, 0) then
			granted += 1
		end
	end
	expectEq(granted, BuildRules.CROP_CREDITS_PER_WINDOW, "300 planters harvested at once")
	expect(BuildRules.TakeCropCredit(ledger, BuildRules.CROP_CREDIT_WINDOW), "the next window pays again")
end)

-- Combat ------------------------------------------------------------------------

test("bow draw time is capped at what the server observed", function()
	expectNear(DamageRules.ObservedDraw(5, 10, 10.2), 0.2, 1e-9, "a claimed full draw 0.2 s after the last shot")
	expectEq(DamageRules.ObservedDraw(0.3, 10, 12), 0.3, "an honest short draw")
	expectEq(DamageRules.ObservedDraw(9, nil, 1), WeaponCatalog.FULL_DRAW_SECONDS, "never more than a full draw")
	expect(
		DamageRules.ArrowSpeed(DamageRules.ObservedDraw(5, 10, 10.05)) < WeaponCatalog.MAX_ARROW_SPEED,
		"instant full-speed arrows are gone"
	)
end)

test("a hit from range provokes an enemy; bosses stay leashed", function()
	local home = Vector3.new(0, 0, 0)
	local archer = Vector3.new(130, 0, 0)
	expect(AggroRules.Provoked(100, 101, home, archer, 90), "an archer past aggro and leash is hunted")
	expect(not AggroRules.Provoked(100, 100 + AggroRules.PROVOKE_SECONDS + 1, home, archer, 90), "it cools off")
	expect(not AggroRules.Provoked(nil, 101, home, archer, 90), "never hit")
	expect(
		not AggroRules.Provoked(100, 101, home, Vector3.new(90 + AggroRules.BOW_RANGE + 5, 0, 0), 90),
		"out of bow range"
	)
	local goal = AggroRules.ClampToLeash(home, archer, 110)
	expectNear(goal.X, 110, 1e-6, "the boss stops at its leash")
	expectEq(AggroRules.ClampToLeash(home, Vector3.new(5, 0, 5), 110), Vector3.new(5, 0, 5), "inside: unchanged")
end)

-- Events ------------------------------------------------------------------------

test("events keep out of extraction auras, safe zones, the arena and bases", function()
	local zones = { { center = Vector3.new(0, 0, 0), radius = 80 } }
	expect(not EventRules.ClearOf(Vector3.new(100, 0, 0), 30, zones), "the footprint reaches the zone")
	expect(EventRules.ClearOf(Vector3.new(120, 0, 0), 30, zones), "clear of it")
	expect(EventRules.ClearOf(Vector3.new(0, 0, 0), 30, {}), "no zones")
end)

-- Channels ----------------------------------------------------------------------

local function fakePrompt()
	return {
		Enabled = true,
		HoldDuration = 0,
		PromptButtonHoldBegan = Signal.new(),
		PromptButtonHoldEnded = Signal.new(),
		Triggered = Signal.new(),
		Destroying = Signal.new(),
	}
end

test("the server interrupts a channel on its own when the holder walks off", function()
	local scheduled = {}
	Channel.Schedule = function(_, callback)
		table.insert(scheduled, callback)
	end
	local prompt = fakePrompt()
	local inRange, completed, interrupted = true, 0, 0
	local player = { Name = "p" }
	Channel.Attach(prompt, 60, function()
		return inRange
	end, function()
		completed += 1
	end, function()
		interrupted += 1
	end)
	prompt.PromptButtonHoldBegan:Fire(player)
	Channel.Poll()
	expectEq(interrupted, 0, "still in range")
	inRange = false
	Channel.Poll()
	expectEq(interrupted, 1, "no release message needed")
	expect(not prompt.Enabled, "the prompt is toggled so the hold bar resets")
	expectEq(#scheduled, 1, "and re-enabled shortly")
	scheduled[1]()
	expect(prompt.Enabled, "re-enabled")
	inRange = true
	prompt.Triggered:Fire(player)
	expectEq(completed, 0, "the old hold can never complete")
	prompt.Destroying:Fire()
end)

test("a hit interrupts; another holder keeps their hold bar", function()
	Channel.Schedule = function() end
	local prompt = fakePrompt()
	local a, b = { Name = "a" }, { Name = "b" }
	local interrupted = {}
	Channel.Attach(prompt, 60, function()
		return true
	end, function() end, function(player)
		interrupted[player] = true
	end)
	prompt.PromptButtonHoldBegan:Fire(a)
	prompt.PromptButtonHoldBegan:Fire(b)
	Channel.Interrupt(a)
	expect(interrupted[a] and not interrupted[b], "only the victim")
	expect(prompt.Enabled, "the prompt stays up while someone else holds it")
	Channel.Forget(b)
	Channel.Poll()
	expect(not interrupted[b], "a departed player is forgotten silently")
	prompt.Destroying:Fire()
end)
