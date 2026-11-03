-- Trade history and crash reconciliation (GDD §10.2): a giver who left before
-- Finalize keeps the trade pending in its saved profile, and its next load
-- reconciles against the receiver's saved history. That history is trimmed to
-- TradeRules.HISTORY entries, so cheap trades must never push out the one record a
-- pending counterpart still needs: a rollback then would leave the items on both
-- profiles. Runs the real TradeService session flow against fake Roblox services
-- and a fake clock.

local lobby
-- os.time follows the fake clock, so trade records are ordered as in a real
-- session (each trade takes at least the confirm countdown).
local realOs = os
os = setmetatable({
	time = function(date)
		return if date then realOs.time(date) else lobby.scheduler.clock
	end,
}, { __index = realOs })

lobby = require(game:GetService("ServerStorage").TestSupport.LobbyTrade).new()
local advance, join, leave, rejoin, trader = lobby.advance, lobby.join, lobby.leave, lobby.rejoin, lobby.trader
local profiles, stored, threadErrors = lobby.profiles, lobby.stored, lobby.threadErrors

local TradeRules = require(game:GetService("ReplicatedStorage").Shared.Economy.TradeRules)
local ProfileService = require(game:GetService("ServerScriptService").Server.Services.ProfileService)

local function sword(id)
	return { instanceId = id, catalogId = "IronSword", ownerId = 1, location = "LobbyBackpack", qualityRoll = 0 }
end

-- One full session: invite, accept, offer, lock both, wait out the countdown,
-- confirm both. Returns TradeConfirm's result for the last confirm.
local function trade(a, b, keys)
	local ok, id = lobby.handlers.TradeRequest(a, b.UserId)
	assert(ok, "invite: " .. tostring(id))
	assert(lobby.handlers.TradeRespond(b, id, true), "accept")
	if keys then
		assert(lobby.handlers.TradeOffer(a, id, keys, 0), "offer")
	end
	return lobby.lockAndConfirm(a, b, id)
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
	table.remove(lobby.Players._list, table.find(lobby.Players._list, b))
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
