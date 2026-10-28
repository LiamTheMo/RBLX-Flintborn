-- Boosts pause between runs (GDD §53): a successful extraction saves each running
-- boost's remaining time in the profile, the next deploy resumes it with exactly
-- that time, and dying or leaving without extracting ends them and clears what
-- was saved. Drives the real ModifierService against a fake clock, a fake player
-- and in-memory profiles; covers BoostRules.Pause/Resume/Sanitize and the load
-- sanitizing of saved boosts.

local Shared = game:GetService("ReplicatedStorage").Shared
local Server = game:GetService("ServerScriptService").Server

-- Fake clock and task scheduler ---------------------------------------------------

local clock = 1000
local queue = {}

task = {}
function task.spawn(fn, ...)
	local thread = if type(fn) == "thread" then fn else coroutine.create(fn)
	coroutine.resume(thread, ...)
	return thread
end
function task.delay(seconds, fn, ...)
	table.insert(queue, { at = clock + (seconds or 0), fn = fn, args = table.pack(...) })
end
function task.defer(fn, ...)
	task.delay(0, fn, ...)
end
function task.wait(seconds)
	return seconds
end

local function advance(seconds: number)
	local target = clock + seconds
	while true do
		local best = nil
		for index, entry in queue do
			if entry.at <= target and (best == nil or entry.at < queue[best].at) then
				best = index
			end
		end
		if best == nil then
			break
		end
		local entry = table.remove(queue, best)
		clock = math.max(clock, entry.at)
		entry.fn(table.unpack(entry.args, 1, entry.args.n))
	end
	clock = target
end

workspace = {
	GetServerTimeNow = function()
		return clock
	end,
}

-- Fake Roblox services ------------------------------------------------------------

local removing = {}
local Players = {
	PlayerAdded = { Connect = function() end },
	PlayerRemoving = {
		Connect = function(_, fn)
			table.insert(removing, fn)
		end,
	},
	_list = {},
}
function Players.GetPlayers(self)
	return table.clone(self._list)
end
local originalGetService = game.GetService
game.GetService = function(self, name)
	if name == "Players" then
		return Players
	end
	return originalGetService(self, name)
end

local PlaceConfig = require(Shared.Config.PlaceConfig)
PlaceConfig.IsWorld = function()
	return true
end

local BoostRules = require(Shared.Survival.BoostRules)
local ProfileSchema = require(Shared.Data.ProfileSchema)

local ProfileService = require(Server.Services.ProfileService)
local profiles = {}
ProfileService.GetProfile = function(player)
	return profiles[player]
end
ProfileService.Mutate = function(player, apply)
	local profile = profiles[player]
	if profile == nil then
		return false
	end
	apply(profile)
	return true
end

local WorldAdmissionService = require(Server.Services.WorldAdmissionService)
local ModifierService = require(Server.Services.ModifierService)
ModifierService.Start()

local function newPlayer(userId: number)
	local player = { UserId = userId, Name = "Player" .. userId, Parent = Players, attributes = {} }
	function player.SetAttribute(self, key, value)
		self.attributes[key] = value
	end
	function player.GetAttribute(self, key)
		return self.attributes[key]
	end
	profiles[player] = ProfileSchema.Default(0)
	return player
end

local XP_DRAUGHT = { kind = "XP", amount = 0.25, seconds = 600 }
local LUCK_BERRY = { kind = "Luck", amount = 0.05, seconds = 180 }

local function startRun(player)
	WorldAdmissionService.RunStarted:Fire(player, nil, {}, "run")
end

local function endRun(player, reason: string)
	WorldAdmissionService.RunEnded:Fire(player, reason)
end

-- Cases ---------------------------------------------------------------------------

test("a successful extraction saves each running boost's remaining time", function()
	local player = newPlayer(1)
	startRun(player)
	ModifierService.ApplyBoost(player, XP_DRAUGHT)
	advance(60)
	ModifierService.ApplyBoost(player, LUCK_BERRY)
	advance(100)
	endRun(player, "Extracted")
	local paused = profiles[player].boosters.paused
	expectEq(#paused, 2, "both boosts saved")
	expectEq(paused[1].kind, "XP", "XP first")
	expectEq(paused[1].amount, 0.25, "with its amount")
	expectEq(paused[1].remaining, 440, "600 - 160 s left")
	expectEq(paused[2].kind, "Luck", "Luck too")
	expectEq(paused[2].remaining, 80, "180 - 100 s left")
	expectEq(player:GetAttribute("BoostXP"), nil, "the HUD shows no boost outside a run")
	expect(ModifierService.BoostTakes(player, { kind = "XP", amount = 0.01, seconds = 1 }), "nothing runs now")
end)

test("the next deploy resumes them with the same remaining time, whatever passed between", function()
	local player = newPlayer(2)
	startRun(player)
	ModifierService.ApplyBoost(player, XP_DRAUGHT)
	advance(200)
	endRun(player, "Extracted")
	-- Hours in the lobby do not count down.
	advance(3 * 3600)
	startRun(player)
	expectEq(player:GetAttribute("BoostXP"), 0.25, "the HUD amount is back")
	expectEq(player:GetAttribute("BoostXPUntil"), clock + 400, "with the 400 s it had left")
	expect(
		not ModifierService.BoostTakes(player, { kind = "XP", amount = 0.25, seconds = 900 }),
		"an equal boost still changes nothing"
	)
	expect(
		ModifierService.BoostTakes(player, { kind = "XP", amount = 0.5, seconds = 60 }),
		"a stronger one still takes over"
	)
	advance(399)
	expectEq(player:GetAttribute("BoostXP"), 0.25, "still running a second before the end")
	advance(1)
	expectEq(player:GetAttribute("BoostXP"), nil, "and ends on time")
	expectEq(player:GetAttribute("BoostXPUntil"), nil, "with its timer")
end)

test("death ends the boosts and clears what an earlier extraction saved", function()
	local player = newPlayer(3)
	startRun(player)
	ModifierService.ApplyBoost(player, XP_DRAUGHT)
	advance(100)
	endRun(player, "Extracted")
	startRun(player)
	expectEq(#profiles[player].boosters.paused, 1, "the saved copy stays while the run is on (a crash keeps it)")
	advance(50)
	endRun(player, "Died")
	expectEq(#profiles[player].boosters.paused, 0, "nothing saved after a death")
	expectEq(player:GetAttribute("BoostXP"), nil, "the boost ended")
	startRun(player)
	expectEq(player:GetAttribute("BoostXP"), nil, "and the next run starts without it")
end)

test("leaving the world without extracting ends them too", function()
	local player = newPlayer(4)
	startRun(player)
	ModifierService.ApplyBoost(player, LUCK_BERRY)
	advance(10)
	endRun(player, "Extracted")
	startRun(player)
	ModifierService.ApplyBoost(player, XP_DRAUGHT)
	endRun(player, "Left")
	expectEq(#profiles[player].boosters.paused, 0, "a logout saves nothing and clears the saved Luck")
end)

test("a boost drunk after a resume replaces a weaker resumed one only when stronger", function()
	local player = newPlayer(5)
	profiles[player].boosters.paused = { { kind = "XP", amount = 0.10, remaining = 100 } }
	startRun(player)
	local entry, started = ModifierService.ApplyBoost(player, { kind = "XP", amount = 0.10, seconds = 180 })
	expect(not started and entry.amount == 0.10, "an equal Sunberry keeps the resumed boost")
	expectEq(player:GetAttribute("BoostXPUntil"), clock + 100, "untouched")
	_, started = ModifierService.ApplyBoost(player, XP_DRAUGHT)
	expect(started, "a stronger draught takes over")
	expectEq(player:GetAttribute("BoostXPUntil"), clock + 600, "with its own timer")
	advance(100)
	expectEq(player:GetAttribute("BoostXP"), 0.25, "the resumed boost's timer never ends the new one")
	endRun(player, "Extracted")
	expectEq(profiles[player].boosters.paused[1].remaining, 500, "the stronger one is what gets saved")
end)

test("Pause and Resume round-trip; Sanitize drops anything invalid", function()
	local boosts = BoostRules.New()
	BoostRules.Apply(boosts, XP_DRAUGHT, 0)
	local saved = BoostRules.Pause(boosts, 250)
	expectEq(#saved, 1, "one saved")
	expectEq(saved[1].remaining, 350, "350 s left")
	local resumed = BoostRules.Resume(saved, 10000)
	expectEq(resumed.XP.endsAt, 10350, "resumed with the same time left")
	expectEq(resumed.XP.amount, 0.25, "and amount")
	expectEq(#BoostRules.Pause(boosts, 600), 0, "an expired boost is not saved")

	expectEq(BoostRules.MAX_SECONDS, 900, "the longest draught lasts 15 minutes")
	local clean = BoostRules.Sanitize({
		{ kind = "XP", amount = 0.1, remaining = 100 },
		{ kind = "XP", amount = 0.25, remaining = 50 },
		{ kind = "Speed", amount = 0.5, remaining = 100 },
		{ kind = "Luck", amount = 0, remaining = 100 },
		{ kind = "Luck", amount = -1, remaining = 100 },
		{ kind = "Luck", amount = 0 / 0, remaining = 100 },
		{ kind = "Luck", amount = math.huge, remaining = 100 },
		{ kind = "Luck", amount = 0.15, remaining = 0 },
		{ kind = "Luck", amount = 0.15, remaining = 901 },
		{ kind = "Luck", amount = 0.15, remaining = 0 / 0 },
		{ kind = "Luck", amount = 0.15, remaining = math.huge },
		{ kind = "Luck", amount = 0.15, remaining = "100" },
		"junk",
	})
	expectEq(#clean, 1, "one entry per kind and only valid ones")
	expectEq(clean[1].kind, "XP", "the XP entry")
	expectEq(clean[1].amount, 0.25, "the stronger of the two")
	expectEq(clean[1].remaining, 50, "with its own time")
	expectEq(#BoostRules.Sanitize(nil), 0, "nil is empty")
	expectEq(#BoostRules.Sanitize("junk"), 0, "a non-table is empty")
	local edge = BoostRules.Sanitize({ { kind = "Luck", amount = 0.15, remaining = 900 } })
	expectEq(#edge, 1, "exactly the longest draught's duration is kept")
end)

test("saved boosts are sanitized on load and old saves gain an empty list", function()
	local old = ProfileSchema.Default(0)
	old.boosters = { xpUntil = 5 }
	local loaded = ProfileSchema.Migrate(old, 0)
	expectEq(type(loaded.boosters.paused), "table", "a save from before GDD §53 gets the field")
	expectEq(#loaded.boosters.paused, 0, "empty")
	expectEq(loaded.boosters.xpUntil, 5, "the paid booster is untouched")

	local tampered = ProfileSchema.Default(0)
	tampered.boosters.paused = {
		{ kind = "XP", amount = 0.25, remaining = 100 },
		{ kind = "XP", amount = 9, remaining = 1e9 },
		{ kind = "Fly", amount = 1, remaining = 10 },
	}
	loaded = ProfileSchema.Migrate(tampered, 0)
	expectEq(#loaded.boosters.paused, 1, "only the valid boost survives")
	expectEq(loaded.boosters.paused[1].remaining, 100, "unchanged")

	tampered.boosters.paused = "nonsense"
	loaded = ProfileSchema.Migrate(tampered, 0)
	expectEq(#loaded.boosters.paused, 0, "a corrupt field loads empty")
end)
