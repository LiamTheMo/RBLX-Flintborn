-- Server authority over movement (GDD §24, §21.4): how far a client-owned point
-- may be from the validated position, the sustained-pace window that catches a
-- small steady speed-up, and the air checks that catch fly and hover hacks. Also
-- the tribe state no longer keeping alliance requests of tribes that are gone.
local Shared = game:GetService("ReplicatedStorage").Shared
local MovementRules = require(Shared.Security.MovementRules)
local SurvivalRules = require(Shared.Survival.SurvivalRules)
local TribeRules = require(Shared.Admission.TribeRules)

local WALK = SurvivalRules.WALK_SPEED

-- `seconds` of samples a quarter-second apart at `speed`, against `allowed`.
local function window(seconds: number, speed: number, allowed: number)
	local list = {}
	for _ = 1, math.round(seconds / 0.25) do
		MovementRules.PushWindow(list, 0.25, speed * 0.25, allowed)
	end
	return list
end

test("a vouched point may be only as far from the validated one as the time since allows", function()
	local cap = 12
	expectEq(MovementRules.Slack(WALK, 0, cap), MovementRules.SLACK_PAD, "just validated: only the pad")
	local sample = MovementRules.Slack(SurvivalRules.SPRINT_SPEED, 0.25, cap)
	expect(sample >= SurvivalRules.SPRINT_SPEED * 0.25, "a quarter-second of sprinting fits")
	expect(sample < cap, "and is well under the cap")
	expectEq(MovementRules.Slack(SurvivalRules.SPRINT_SPEED, 10, cap), cap, "never past the cap")
end)

test("a steady speed-up inside the per-sample tolerance is caught over the window", function()
	local seconds = MovementRules.WINDOW_SECONDS
	expect(not MovementRules.WindowOver(window(seconds, WALK, WALK)), "walking at the allowed pace")
	expect(
		not MovementRules.WindowOver(window(seconds, SurvivalRules.SPRINT_SPEED, SurvivalRules.SPRINT_SPEED)),
		"sprinting at the allowed pace"
	)
	expect(MovementRules.WindowOver(window(seconds, WALK * 1.24, WALK)), "24% fast for the whole window")
	expect(MovementRules.WindowOver(window(seconds, WALK * 1.2, WALK)), "20% fast for the whole window")
	expect(not MovementRules.WindowOver(window(seconds / 2, WALK * 1.24, WALK)), "a short window does not judge")
end)

test("a lag spike's backlog does not count as a speed-up", function()
	-- A full window of walking whose last sample brings a second and a quarter
	-- of it at once.
	local list = window(MovementRules.WINDOW_SECONDS - 0.25, WALK, WALK)
	MovementRules.PushWindow(list, 0.25, WALK * 1.25, WALK)
	expect(not MovementRules.WindowOver(list), "a 1.25 s backlog")
end)

test("the window keeps only its last WINDOW_SECONDS of samples", function()
	local list = window(MovementRules.WINDOW_SECONDS * 2, WALK, WALK)
	local seconds = 0
	for _, entry in list do
		seconds += entry.dt
	end
	expect(seconds <= MovementRules.WINDOW_SECONDS + 0.25, "older samples dropped")
	expect(seconds >= MovementRules.WINDOW_SECONDS - 0.25, "a full window kept")
end)

test("off the ground a player rises no higher than a jump and cannot hover", function()
	local jump = 7.2
	local air = { groundY = 10 }
	expectEq(MovementRules.JudgeAir(air, true, 10, jump, 0), "Ok", "standing")
	-- A jump: up and back down within half a second.
	expectEq(MovementRules.JudgeAir(air, false, 15, jump, 0.25), "Ok", "rising")
	expectEq(MovementRules.JudgeAir(air, false, 10 + jump, jump, 0.5), "Ok", "at the top of a jump")
	expectEq(MovementRules.JudgeAir(air, true, 10, jump, 0.75), "Ok", "landed")
	-- Flying straight up.
	expectEq(MovementRules.JudgeAir(air, false, 10 + jump + MovementRules.RISE_MARGIN + 1, jump, 1), "Fly", "too high")
	-- Hovering at one height.
	air = { groundY = 10 }
	MovementRules.JudgeAir(air, false, 12, jump, 0)
	expectEq(MovementRules.JudgeAir(air, false, 12, jump, MovementRules.HOVER_SECONDS - 0.1), "Ok", "a moment up")
	expectEq(MovementRules.JudgeAir(air, false, 12, jump, MovementRules.HOVER_SECONDS), "Fly", "hovering")
end)

test("falls are free, however long", function()
	local air = { groundY = 100 }
	MovementRules.JudgeAir(air, false, 100, 7.2, 0)
	for step = 1, 12 do
		expectEq(MovementRules.JudgeAir(air, false, 100 - step * step, 7.2, step * 0.25), "Ok", "falling")
	end
	expectEq(MovementRules.JudgeAir(air, true, -44, 7.2, 3.25), "Ok", "landed far below")
end)

test("a downed player (no jump) cannot hop", function()
	local air = { groundY = 0 }
	expectEq(MovementRules.JudgeAir(air, false, MovementRules.RISE_MARGIN, 0, 0.1), "Ok", "a stumble")
	expectEq(MovementRules.JudgeAir(air, false, 6.5, 0, 0.2), "Fly", "a jump")
end)

test("a tribe that is gone takes its alliance requests with it", function()
	local state = TribeRules.NewState()
	expect(TribeRules.Create(state, 1, "tribe:a"), "a")
	expect(TribeRules.Create(state, 2, "tribe:b"), "b")
	local ok, reason = TribeRules.Ally(state, 1, "tribe:b")
	expect(ok and reason == "Requested", "requested")
	expect(next(state.allianceRequests) ~= nil, "pending")
	TribeRules.Leave(state, 1)
	expectEq(next(state.allianceRequests), nil, "gone with tribe a")
	-- And requests to a tribe that is gone.
	expect(TribeRules.Create(state, 3, "tribe:c"), "c")
	TribeRules.Ally(state, 3, "tribe:b")
	TribeRules.Leave(state, 2)
	expectEq(next(state.allianceRequests), nil, "gone with tribe b")
end)
