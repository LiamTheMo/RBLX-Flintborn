-- Lobby trading (GDD §10.2, Q13, Q50, Q98, Q125, Q130). Two players in the same
-- lobby server exchange designated lobby-backpack items and Gems — never Coins.
-- Offers lock, a short countdown runs, and both confirm. Settlement changes both
-- profiles together, records the trade as pending on each, saves both, then
-- finalises. If the server dies between the two saves, the next load reconciles
-- against the counterpart's saved profile so exactly one outcome survives.

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local TradeRules = require(ReplicatedStorage.Shared.Economy.TradeRules)
local CurrencyService = require(script.Parent.CurrencyService)
local ProfileService = require(script.Parent.ProfileService)

local TradeService = {}

TradeService.COUNTDOWN_SECONDS = 5
TradeService.INVITE_SECONDS = 30

local sessions = {}
local sessionOf = {}

-- A stable key for a backpack slot: its instance ID, or "stack:<catalogId>".
local function keyOf(item): string
	return item.instanceId or ("stack:" .. item.catalogId)
end

local function indexesFor(profile, keys)
	local indexes = {}
	for _, key in keys do
		local found = nil
		for index, item in profile.lobbyBackpack.slots do
			if keyOf(item) == key and not table.find(indexes, index) then
				found = index
				break
			end
		end
		if found == nil then
			return nil
		end
		table.insert(indexes, found)
	end
	return indexes
end

local function other(session, player: Player): Player
	return if session.a == player then session.b else session.a
end

local function describe(profile, offer)
	local list = {}
	for _, key in offer.keys do
		for _, item in profile.lobbyBackpack.slots do
			if keyOf(item) == key then
				local def = ItemCatalog.Get(item.catalogId)
				table.insert(list, {
					key = key,
					name = (item.permanent and "★ " or "") .. (def and def.name or item.catalogId),
					quantity = item.quantity,
				})
				break
			end
		end
	end
	return { items = list, gems = offer.gems }
end

local function push(session)
	for _, player in { session.a, session.b } do
		local partner = other(session, player)
		local mine, theirs = ProfileService.GetProfile(player), ProfileService.GetProfile(partner)
		if mine and theirs and player.Parent then
			Remotes.Get("TradeChanged"):FireClient(player, {
				kind = "Session",
				id = session.id,
				partner = partner.DisplayName,
				mine = describe(mine, session.offers[player]),
				theirs = describe(theirs, session.offers[partner]),
				locked = { mine = session.locked[player] == true, theirs = session.locked[partner] == true },
				confirmed = { mine = session.confirmed[player] == true, theirs = session.confirmed[partner] == true },
				confirmAt = session.confirmAt,
			})
		end
	end
end

local function close(session, reason: string)
	if sessions[session.id] ~= session then
		return
	end
	sessions[session.id] = nil
	for _, player in { session.a, session.b } do
		sessionOf[player] = nil
		if player.Parent then
			Remotes.Get("TradeChanged"):FireClient(player, { kind = "Closed", id = session.id, reason = reason })
		end
	end
end

local function settle(session)
	local a, b = session.a, session.b
	local pa, pb = ProfileService.GetProfile(a), ProfileService.GetProfile(b)
	if pa == nil or pb == nil or pa.transit or pb.transit then
		close(session, "Unavailable")
		return
	end
	local now = os.time()
	local offerA = { items = indexesFor(pa, session.offers[a].keys), gems = session.offers[a].gems }
	local offerB = { items = indexesFor(pb, session.offers[b].keys), gems = session.offers[b].gems }
	if offerA.items == nil or offerB.items == nil then
		close(session, "ItemsChanged")
		return
	end
	-- Re-check both sides at the moment of settlement (§24): nothing ineligible
	-- passes even if both players accepted.
	local okA, reasonA = TradeRules.ValidateOffer(pa, offerA, now)
	local okB, reasonB = TradeRules.ValidateOffer(pb, offerB, now)
	if not okA or not okB then
		close(session, reasonA or reasonB)
		return
	end
	local tradeId = "trade:" .. HttpService:GenerateGUID(false)
	-- Both profiles change together, with no yield in between.
	ProfileService.Mutate(a, function()
		TradeRules.Settle(tradeId, { profile = pa, userId = a.UserId, offer = offerA }, {
			profile = pb,
			userId = b.UserId,
			offer = offerB,
		}, now)
	end)
	ProfileService.Mutate(b, function() end)
	close(session, "Completed")
	local savedA = ProfileService.SaveNow(a)
	local savedB = ProfileService.SaveNow(b)
	if savedA and savedB then
		for _, player in { a, b } do
			ProfileService.Mutate(player, function(profile)
				TradeRules.Finalize(profile, tradeId, os.time())
			end)
		end
	end
	CurrencyService.Publish(a)
	CurrencyService.Publish(b)
end

-- On load, settle or undo any trade an earlier session left pending.
local function reconcile(player: Player, profile)
	for tradeId, pending in profile.trades.pending do
		local ok, stored = ProfileService.ReadStored(pending.counterpart)
		if ok then
			local outcome
			ProfileService.Mutate(player, function(live)
				outcome = TradeRules.Reconcile(live, tradeId, stored, os.time())
			end)
			if outcome == "RolledBack" then
				warn(("[TradeService] Trade %s for %d rolled back after a crash"):format(tradeId, player.UserId))
			end
		end
	end
	CurrencyService.Publish(player)
end

local function sessionFor(player: Player, id: any)
	local session = type(id) == "string" and sessions[id]
	if not session or (session.a ~= player and session.b ~= player) then
		return nil
	end
	return session
end

local function request(player: Player, targetUserId: any)
	local target = type(targetUserId) == "number" and Players:GetPlayerByUserId(targetUserId)
	if not target or target == player or sessionOf[player] or sessionOf[target] then
		return false, "Unavailable"
	end
	if ProfileService.GetProfile(player) == nil or ProfileService.GetProfile(target) == nil then
		return false, "Unavailable"
	end
	local session = {
		id = HttpService:GenerateGUID(false),
		a = player,
		b = target,
		accepted = false,
		offers = { [player] = { keys = {}, gems = 0 }, [target] = { keys = {}, gems = 0 } },
		locked = {},
		confirmed = {},
	}
	sessions[session.id] = session
	sessionOf[player], sessionOf[target] = session, session
	Remotes.Get("TradeChanged"):FireClient(target, { kind = "Invite", id = session.id, from = player.DisplayName })
	task.delay(TradeService.INVITE_SECONDS, function()
		if sessions[session.id] == session and not session.accepted then
			close(session, "Expired")
		end
	end)
	return true, session.id
end

local function respond(player: Player, id: any, accept: any)
	local session = sessionFor(player, id)
	if session == nil or session.b ~= player or session.accepted then
		return false, "NoInvite"
	end
	if accept ~= true then
		close(session, "Declined")
		return true, nil
	end
	session.accepted = true
	push(session)
	return true, nil
end

local function offer(player: Player, id: any, keys: any, gems: any)
	local session = sessionFor(player, id)
	if session == nil or not session.accepted or type(keys) ~= "table" or type(gems) ~= "number" then
		return false, "BadRequest"
	end
	local profile = ProfileService.GetProfile(player)
	local clean = {}
	for _, key in keys do
		if type(key) == "string" and #key <= 64 then
			table.insert(clean, key)
		end
	end
	local indexes = profile and indexesFor(profile, clean)
	if indexes == nil then
		return false, "MissingItem"
	end
	local ok, reason = TradeRules.ValidateOffer(profile, { items = indexes, gems = gems }, os.time())
	if not ok then
		return false, reason
	end
	session.offers[player] = { keys = clean, gems = gems }
	-- Any change unlocks both sides (cancel protection).
	session.locked, session.confirmed, session.confirmAt = {}, {}, nil
	push(session)
	return true, nil
end

local function lock(player: Player, id: any)
	local session = sessionFor(player, id)
	if session == nil or not session.accepted then
		return false, "BadRequest"
	end
	session.locked[player] = true
	if session.locked[session.a] and session.locked[session.b] then
		session.confirmAt = workspace:GetServerTimeNow() + TradeService.COUNTDOWN_SECONDS
	end
	push(session)
	return true, nil
end

local function confirm(player: Player, id: any)
	local session = sessionFor(player, id)
	if session == nil or session.confirmAt == nil or workspace:GetServerTimeNow() < session.confirmAt then
		return false, "NotReady"
	end
	session.confirmed[player] = true
	if session.confirmed[session.a] and session.confirmed[session.b] then
		settle(session)
	else
		push(session)
	end
	return true, nil
end

function TradeService.Start()
	-- Recovery runs wherever a profile loads, since a crash can strike anywhere.
	ProfileService.ProfileLoaded:Connect(function(player, profile)
		if next(profile.trades.pending) then
			task.spawn(reconcile, player, profile)
		end
	end)
	if not PlaceConfig.IsLobby() then
		return
	end
	Remotes.Handle("TradeRequest", request)
	Remotes.Handle("TradeRespond", respond)
	Remotes.Handle("TradeOffer", offer)
	Remotes.Handle("TradeLock", lock)
	Remotes.Handle("TradeConfirm", confirm)
	Remotes.Handle("TradeCancel", function(player, id)
		local session = sessionFor(player, id)
		if session then
			close(session, "Cancelled")
		end
		return true, nil
	end)
	Players.PlayerRemoving:Connect(function(player)
		local session = sessionOf[player]
		if session then
			close(session, "PartnerLeft")
		end
	end)
end

return TradeService
