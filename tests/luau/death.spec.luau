local Shared = game:GetService("ReplicatedStorage").Shared
local DownedRules = require(Shared.Combat.DownedRules)
local TribeRules = require(Shared.Admission.TribeRules)
local DeathRules = require(Shared.Admission.DeathRules)

local function steps(state, seconds, dt)
	local outcome = nil
	for _ = 1, math.round(seconds / dt) do
		outcome = DownedRules.Step(state, dt) or outcome
		if outcome then
			break
		end
	end
	return outcome
end

test("the 60 s bleed-out pauses during a revive and resumes from where it was", function()
	local state = DownedRules.New()
	expectEq(state.downedHealth, 20, "20 downed HP")
	steps(state, 20, 0.1)
	expectNear(state.remaining, 40, 1e-6, "40 s left")
	expect(DownedRules.StartRevive(state, 7), "revive starts")
	steps(state, 5, 0.1)
	expectNear(state.remaining, 40, 1e-6, "paused while reviving")
	DownedRules.StopRevive(state, 7)
	expectEq(state.reviveProgress, 0, "cancelled progress restarts")
	steps(state, 10, 0.1)
	expectNear(state.remaining, 30, 1e-6, "resumed, not reset to 60")
	expectEq(steps(state, 31, 0.1), "BledOut", "bleeds out when the timer runs out")
end)

test("a revive completes after 10 continuous seconds", function()
	local state = DownedRules.New()
	DownedRules.StartRevive(state, 3)
	expectEq(steps(state, 9.9, 0.1), nil, "not yet at 9.9 s")
	expectEq(DownedRules.Step(state, 0.1), "Revived", "revived at 10 s")
end)

test("only one reviver at a time", function()
	local state = DownedRules.New()
	expect(DownedRules.StartRevive(state, 1), "first reviver")
	expect(not DownedRules.StartRevive(state, 2), "second reviver refused")
	DownedRules.StopRevive(state, 2)
	expectEq(state.reviverId, 1, "another player cannot cancel the revive")
	DownedRules.StopRevive(state, 1)
	expect(DownedRules.StartRevive(state, 2), "free again")
end)

test("armor protects the downed pool and enemies can finish at any time", function()
	local state = DownedRules.New()
	DownedRules.StartRevive(state, 1)
	expect(not DownedRules.Damage(state, 2, 20), "20 raw on full iron leaves 10")
	expectNear(state.downedHealth, 10, 1e-9, "armor halves it")
	expect(DownedRules.Damage(state, 2, 20), "finished mid-revive")
end)

test("revived health is 10% of max EHP as actual HP", function()
	expectNear(DownedRules.RevivedHealth(100, 2), 10, 1e-9, "100 HP full iron")
	expectNear(DownedRules.RevivedHealth(150, 2), 15, 1e-9, "150 HP full iron")
end)

test("tribes cap at eight, leaders invite and kick, leadership passes on", function()
	local state = TribeRules.NewState()
	expect(TribeRules.Create(state, 1, "t1"), "create")
	for userId = 2, 8 do
		expect(TribeRules.JoinOrCreate(state, userId, "t1"), "join " .. userId)
	end
	local ok, reason = TribeRules.JoinOrCreate(state, 9, "t1")
	expect(not ok and reason == "TribeFull", "no ninth member")
	ok, reason = TribeRules.Invite(state, 2, 9)
	expect(not ok and reason == "NotLeader", "members cannot invite")
	expect(TribeRules.Kick(state, 1, 8), "leader kicks")
	expect(TribeRules.Invite(state, 1, 9), "room again")
	expect(TribeRules.Accept(state, 9, "t1"), "invitee accepts")
	TribeRules.Leave(state, 1)
	expectEq(TribeRules.TribeOf(state, 2).leader, 2, "leadership passes on")
end)

test("alliances need both leaders", function()
	local state = TribeRules.NewState()
	TribeRules.Create(state, 1, "a")
	TribeRules.Create(state, 2, "b")
	local _, first = TribeRules.Ally(state, 1, "b")
	expectEq(first, "Requested", "one side requests")
	expect(state.tribes.a.allies.b == nil, "not allied yet")
	local _, second = TribeRules.Ally(state, 2, "a")
	expectEq(second, "Allied", "the other side accepts")
	expect(state.tribes.a.allies.b and state.tribes.b.allies.a, "mutual")
	TribeRules.Leave(state, 2)
	expect(state.tribes.a.allies.b == nil, "dissolved tribe leaves the alliance")
end)

test("Permanent items never enter a body; bodies last exactly 600 s", function()
	local items = {
		{ catalogId = "Wood", quantity = 10 },
		{ instanceId = "p", catalogId = "StonePickaxe", permanent = true },
		{ instanceId = "s", catalogId = "StoneSpear" },
	}
	local body, kept = DeathRules.Split(items)
	expectEq(#body, 2, "ordinary items drop")
	expectEq(#kept, 1, "Permanent item kept")
	expectEq(kept[1].instanceId, "p", "the pickaxe")
	expect(not DeathRules.IsExpired(0, 599.9), "still there at 599.9 s")
	expect(DeathRules.IsExpired(0, 600), "gone at 600 s")
	local taken = DeathRules.Take(body, 1)
	expectEq(taken.catalogId, "Wood", "looted")
	expectEq(#body, 1, "one entry left")
	expectEq(DeathRules.Take(body, 5), nil, "nothing at a missing index")
end)
