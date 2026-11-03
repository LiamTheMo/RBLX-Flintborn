-- Trade history and crash reconciliation (GDD §10.2): a giver who left before
-- Finalize keeps the trade pending in its saved profile, and its next load
-- reconciles against the receiver's saved history. That history is trimmed to
-- TradeRules.HISTORY entries, so cheap trades must never push out the one record a
-- pending counterpart still needs: a rollback then would leave the items on both
-- profiles. Runs the real TradeService session flow against fake Roblox services
-- and a fake clock.

local Shared = game:GetService("ReplicatedStorage").Shared
local Server = game:GetService("ServerScriptService").Server

-- Fake clock and task scheduler ---------------------------------------------------

local clock = 0
local queue = {}
local sequence = 0
local threadErrors = {}

local function resume(thread, ...)
	local ok, err = coroutine.resume(thread, ...)
	if not ok then
		table.insert(threadErrors, tostring(err))
	end
end

task = {}
function task.spawn(fn, ...)
	local thread = if type(fn) == "thread" then fn else coroutine.create(fn)
	resume(thread, ...)
	return thread
end
function task.delay(seconds, fn, ...)
	sequence += 1
	table.insert(
		queue,
		{ at = clock + (seconds or 0), sequence = sequence, thread = coroutine.create(fn), args = table.pack(...) }
	)
end
function task.wait(seconds)
	sequence += 1
	table.insert(
		queue,
		{ at = clock + (seconds or 0), sequence = sequence, thread = coroutine.running(), args = table.pack() }
	)
	coroutine.yield()
	return seconds
end

warn = function() end

-- os.time follows the fake clock, so trade records are ordered as in a real
-- session (each trade takes at least the confirm countdown).
local realOs = os
os = setmetatable({
	time = function(date)
		return if date then realOs.time(date) else clock
	end,
}, { __index = realOs })

-- Runs everything due within the next `seconds`, in time order.
local function advance(seconds: number)
	local target = clock + seconds
	while true do
		local best = nil
		for index, entry in queue do
			if entry.at <= target then
				local current = best and queue[best]
				if
					current == nil
					or entry.at < current.at
					or (entry.at == current.at and entry.sequence < current.sequence)
				then
					best = index
				end
			end
		end
		if best == nil then
			break
		end
		local entry = table.remove(queue, best)
		clock = math.max(clock, entry.at)
		resume(entry.thread, table.unpack(entry.args, 1, entry.args.n))
	end
	clock = target
end

-- Fake Roblox services ------------------------------------------------------------

local Players = { _list = {} }
local removing = {}
Players.PlayerRemoving = {
	Connect = function(_, fn)
		table.insert(removing, fn)
	end,
}
function Players.GetPlayers(self)
	return table.clone(self._list)
end
function Players.GetPlayerByUserId(self, userId)
	for _, player in self._list do
		if player.UserId == userId then
			return player
		end
	end
	return nil
end

local guids = 0
local fakes = {
	Players = Players,
	HttpService = {
		GenerateGUID = function()
			guids += 1
			return ("guid-%d"):format(guids)
		end,
	},
}
local originalGetService = game.GetService
game.GetService = function(self, name)
	return fakes[name] or originalGetService(self, name)
end
game.JobId = "job-trade"
workspace = {
	GetServerTimeNow = function()
		return clock
	end,
}

local PlaceConfig = require(Shared.Config.PlaceConfig)
PlaceConfig.IsLobby = function()
	return true
end
local Remotes = require(Shared.Net.Remotes)
local handlers = {}
local pushed = {}
Remotes.Handle = function(name, fn)
	handlers[name] = fn
end
Remotes.Get = function()
	return {
		FireClient = function(_, player, payload)
			pushed[player] = payload
		end,
	}
end

local ProfileSchema = require(Shared.Data.ProfileSchema)
local TradeRules = require(Shared.Economy.TradeRules)

-- Profiles live in memory; a save copies one into `stored`.
local ProfileService = require(Server.Services.ProfileService)
local profiles, stored = {}, {}
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
ProfileService.SaveNow = function(player)
	stored[player.UserId] = ProfileSchema.DeepCopy(profiles[player])
	return true
end
ProfileService.ReadStored = function(userId)
	return true, stored[userId]
end
local CurrencyService = require(Server.Services.CurrencyService)
CurrencyService.Publish = function() end

local TradeService = require(Server.Services.TradeService)
TradeService.Start()

local function sword(id)
	return { instanceId = id, catalogId = "IronSword", ownerId = 1, location = "LobbyBackpack", qualityRoll = 0 }
end

local function trader()
	local profile = ProfileSchema.Default(0)
	profile.progression.level = 12
	return profile
end

local nextUserId = 100
local function join(profile)
	nextUserId += 1
	local player = { UserId = nextUserId, DisplayName = "P" .. nextUserId, Parent = Players }
	function player.SetAttribute() end
	table.insert(Players._list, player)
	profiles[player] = profile
	stored[player.UserId] = ProfileSchema.DeepCopy(profile)
	return player
end

-- The player leaves: PlayerRemoving fires, the release save stores the live
-- profile and the server forgets it (ProfileService's PlayerRemoving handler).
local function leave(player)
	player.Parent = nil
	table.remove(Players._list, table.find(Players._list, player))
	for _, fn in removing do
		fn(player)
	end
	stored[player.UserId] = ProfileSchema.DeepCopy(profiles[player])
	profiles[player] = nil
end

-- The same account joins again: its saved profile loads and ProfileLoaded fires.
local function rejoin(player)
	player.Parent = Players
	table.insert(Players._list, player)
	profiles[player] = ProfileSchema.DeepCopy(stored[player.UserId])
	ProfileService.ProfileLoaded:Fire(player, profiles[player])
end

-- One full session: invite, accept, offer, lock both, wait out the countdown,
-- confirm both. Returns TradeConfirm's result for the last confirm.
local function trade(a, b, keys)
	local ok, id = handlers.TradeRequest(a, b.UserId)
	assert(ok, "invite: " .. tostring(id))
	assert(handlers.TradeRespond(b, id, true), "accept")
	if keys then
		assert(handlers.TradeOffer(a, id, keys, 0), "offer")
	end
	handlers.TradeLock(a, id)
	handlers.TradeLock(b, id)
	advance(TradeService.COUNTDOWN_SECONDS)
	handlers.TradeConfirm(a, id)
	return handlers.TradeConfirm(b, id)
end

local function holds(profile, instanceId): boolean
	for _, slot in profile.lobbyBackpack.slots do
		if slot.instanceId == instanceId then
			return true
		end
	end
	return false
end

-- A trades a sword to B and disconnects while its own post-trade save is in
-- flight, so finish() never finalises A: A's saved profile keeps the trade pending
-- while B reconciles it as Settled against that saved copy.
local function giverLeavesMidFinish()
	local a, b = join(trader()), join(trader())
	profiles[a].lobbyBackpack.slots = { sword("dup-1") }
	local realSave = ProfileService.SaveNow
	ProfileService.SaveNow = function(player)
		local result = realSave(player)
		if player == a and a.Parent then
			leave(a)
		end
		return result
	end
	expect(trade(a, b, { "dup-1" }), "confirmed")
	ProfileService.SaveNow = realSave
	advance(1)
	local tradeId = next(stored[a.UserId].trades.pending)
	return a, b, tradeId
end

test("a giver who left mid-finish settles on rejoin, even after the receiver's history filled up", function()
	local a, b, tradeId = giverLeavesMidFinish()
	expect(tradeId ~= nil, "A's saved profile keeps the trade pending (A left before Finalize)")
	expect(holds(profiles[b], "dup-1"), "B holds the sword")
	expectEq(next(profiles[b].trades.pending), nil, "B reconciled the trade")
	expectEq(profiles[b].trades.history[tradeId].outcome, "Settled", "as Settled")

	-- B trades TradeRules.HISTORY times with an alt (empty offers are allowed). The
	-- alt relogs between trades, which clears the pair's invite cooldown.
	local alt = join(trader())
	for _ = 1, TradeRules.HISTORY do
		expect(trade(b, alt), "pump trade")
		leave(alt)
		rejoin(alt)
	end
	expectEq(#threadErrors, 0, "no spawned thread errored: " .. tostring(threadErrors[1]))
	expectEq(next(profiles[b].trades.pending), nil, "every pump trade finalised")
	expect(profiles[b].trades.history[tradeId] ~= nil, "B still remembers the trade A has pending")
	leave(b)

	-- A rejoins: its load reconciles the pending trade against B's saved profile.
	rejoin(a)
	advance(1)
	local live = profiles[a]
	expectEq(next(live.trades.pending), nil, "A's pending trade is resolved")
	expectEq(live.trades.history[tradeId] and live.trades.history[tradeId].outcome, "Settled", "B saved it: it stands")
	expect(not (holds(live, "dup-1") and holds(stored[b.UserId], "dup-1")), "the sword must not exist on both profiles")
end)

test("the history stays at the cap and keeps the newest record with every counterpart", function()
	local profile = trader()
	local function settleWith(counterpart: number, tradeId: string, at: number)
		profile.trades.pending[tradeId] = {
			counterpart = counterpart,
			gave = { items = {}, gems = 0 },
			received = { items = {}, gems = 0 },
			at = at,
		}
		TradeRules.Finalize(profile, tradeId, at)
	end
	settleWith(7, "kept", 1)
	settleWith(8, "old", 2)
	for index = 1, TradeRules.HISTORY + 20 do
		settleWith(9, "pump-" .. index, 10 + index)
	end
	local count = 0
	for _ in profile.trades.history do
		count += 1
	end
	expectEq(count, TradeRules.HISTORY, "still capped")
	expect(profile.trades.history.kept ~= nil, "the only record with partner 7 is kept")
	expect(profile.trades.history.old ~= nil, "and with partner 8")
	expectEq(profile.trades.history["pump-22"], nil, "the oldest pump trades make room instead")
	expect(profile.trades.history["pump-23"] ~= nil, "and only as many as needed")
	expect(profile.trades.history["pump-" .. (TradeRules.HISTORY + 20)] ~= nil, "the newest pump trade is kept")
end)

test("a trade the receiver never saved still rolls back, however long its history", function()
	local a, b = join(trader()), join(trader())
	profiles[a].lobbyBackpack.slots = { sword("s2") }
	local realSave = ProfileService.SaveNow
	-- B's server never manages to save B; A leaves mid-finish as above.
	ProfileService.SaveNow = function(player)
		if player == b then
			return false
		end
		local result = realSave(player)
		if player == a and a.Parent then
			leave(a)
		end
		return result
	end
	expect(trade(a, b, { "s2" }), "confirmed")
	ProfileService.SaveNow = realSave
	local tradeId = next(stored[a.UserId].trades.pending)
	expect(tradeId ~= nil, "A's saved profile has it pending")
	-- B's server crashes: B's saved profile is the one from before the trade.
	profiles[b] = nil
	b.Parent = nil
	table.remove(Players._list, table.find(Players._list, b))
	rejoin(b)
	local alt = join(trader())
	for _ = 1, TradeRules.HISTORY + 5 do
		expect(trade(b, alt), "pump trade")
		leave(alt)
		rejoin(alt)
	end
	leave(b)
	rejoin(a)
	advance(1)
	local live = profiles[a]
	expectEq(live.trades.history[tradeId] and live.trades.history[tradeId].outcome, "RolledBack", "B never saved it")
	expect(holds(live, "s2"), "A has the sword back")
	expect(not holds(stored[b.UserId], "s2"), "B never had it")
	expectEq(#threadErrors, 0, "no spawned thread errored: " .. tostring(threadErrors[1]))
end)
