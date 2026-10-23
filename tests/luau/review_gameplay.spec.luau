-- Review of the gameplay and anti-cheat hardening (GDD §5.1, §5.2, §4.3, §6, §24).
-- Pure pieces behind the follow-up fixes: structure control after leaving a tribe,
-- swings and shots measured against the server-validated position, the first bow
-- draw of a run, and a sprint that really stops when stamina runs out.
local Shared = game:GetService("ReplicatedStorage").Shared
local BuildRules = require(Shared.Building.BuildRules)
local DamageRules = require(Shared.Combat.DamageRules)
local MovementRules = require(Shared.Security.MovementRules)
local SurvivalRules = require(Shared.Survival.SurvivalRules)
local WeaponCatalog = require(Shared.Combat.WeaponCatalog)

-- Building ----------------------------------------------------------------------

test("a member who leaves or is kicked keeps nothing they built for the tribe", function()
	local tribe = "tribe:abc"
	local builder = 7
	local soloKey = BuildRules.SoloKey(builder)
	-- Built while in the tribe, then kicked: back to their solo key.
	expect(not BuildRules.Controls(soloKey, builder, tribe), "a kicked builder cannot open the tribe's doors")
	expect(BuildRules.Controls(tribe, 8, tribe), "the tribe still controls it")
	-- Built solo, then joined a tribe: their solo pieces stay theirs.
	expect(BuildRules.Controls(tribe, builder, soloKey), "a solo builder who joined a tribe keeps their pieces")
	expect(not BuildRules.Controls(tribe, 8, soloKey), "their new tribe-mates do not")
	expect(not BuildRules.Controls(BuildRules.SoloKey(9), 9, tribe), "strangers never")
end)

-- Combat ------------------------------------------------------------------------

test("a swing or shot far from the validated position is refused; normal lag is not", function()
	local validated = Vector3.new(0, 10, 0)
	local slack = 12
	expect(MovementRules.NearValidated(Vector3.new(30, 10, 0), nil, slack), "untracked: nothing to compare")
	-- One quarter-second sample of sprinting behind the live root.
	local lag = SurvivalRules.SPRINT_SPEED * 0.25
	expect(MovementRules.NearValidated(Vector3.new(lag, 10, 0), validated, slack), "a sprinting swing")
	expect(MovementRules.NearValidated(Vector3.new(2, -20, 0), validated, slack), "mid-fall: vertical is ignored")
	expect(
		not MovementRules.NearValidated(Vector3.new(30, 10, 0), validated, slack),
		"teleport onto a target, swing, teleport back"
	)
end)

test("the first shot of a new run cannot claim a draw from the previous run", function()
	-- Last shot 120 s ago in an earlier run; respawned 0.1 s ago and fired at once.
	local start = DamageRules.DrawStart(0, 119.9)
	expectNear(DamageRules.ObservedDraw(9, start, 120), 0.1, 1e-9, "only the time since the respawn counts")
	expect(DamageRules.ObservedDraw(9, start, 120) < WeaponCatalog.FULL_DRAW_SECONDS, "no instant full draw")
	expectEq(DamageRules.DrawStart(50, 10), 50, "within a run the last attack counts")
	expectEq(DamageRules.DrawStart(nil, 10), 10, "no attack yet: the run start")
	expectEq(DamageRules.DrawStart(nil, nil), nil, "nothing known")
end)

-- Survival ----------------------------------------------------------------------

-- One SurvivalService frame: stamina steps first, then the walk speed is set.
local function frame(state, dt: number): number
	SurvivalRules.StepStamina(state, dt, true)
	return SurvivalRules.MoveSpeed(state, true)
end

test("an exhausted sprinter walks until they let go of sprint", function()
	local state = SurvivalRules.NewState()
	state.sprintIntent = true
	local sprintFrames = 0
	-- 3 s empties the bar; the next 2 s are held sprint on an empty bar.
	for index = 1, 300 do
		local speed = frame(state, 1 / 60)
		if index > 185 and speed == SurvivalRules.SPRINT_SPEED then
			sprintFrames += 1
		end
	end
	expectEq(sprintFrames, 0, "the walk speed never flickers back to sprint on an empty bar")
	expect(state.stamina > 0, "walking still recovers while sprint is held")
	state.sprintIntent = false
	frame(state, 1 / 60)
	state.sprintIntent = true
	expectEq(frame(state, 1 / 60), SurvivalRules.SPRINT_SPEED, "pressing sprint again uses what recovered")
	local held = SurvivalRules.NewState()
	held.sprintIntent = true
	for _ = 1, 600 do
		frame(held, 1 / 60)
	end
	expect(SurvivalRules.IsSprinting(held, true), "a bar refilled while sprint stayed held sprints again")
end)
