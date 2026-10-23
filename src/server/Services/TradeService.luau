-- Lobby trading (GDD §10.2, Q13, Q50, Q98, Q125, Q130, Q164). Two players in the
-- same lobby server exchange designated lobby-backpack items, eligible vault
-- materials and Gems — never Coins. An invite binds the target only once
-- accepted, and the same pair waits a short cooldown between invites. Offers
-- snapshot each slot and its quantity, and each vault material quantity; any
-- backpack or vault material change unlocks both sides, and settlement needs the
-- exact snapshot.
-- Vault, shop and Forge actions wait while a session is open. Settlement changes
-- both profiles together (all or nothing), records the trade as pending on each,
-- saves both, then finalises. If a save never lands, the next load (or a retry
-- while the player stays) reconciles against the counterpart's saved profile so
-- exactly one outcome survives. While pending, sales, Forge crafts, Gem spending
-- and Deploy are refused ("TradeSettling"); Reconcile always ends it, at the latest
-- once the counterpart's lease expires.

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local ProfileSchema = require(ReplicatedStorage.Shared.Data.ProfileSchema)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local TradeRules = require(ReplicatedStorage.Shared.Economy.TradeRules)
local Validation = require(ReplicatedStorage.Shared.Data.Validation)
local CurrencyService = require(script.Parent.CurrencyService)
local ProfileService = require(script.Parent.ProfileService)

local TradeService = {}

TradeService.COUNTDOWN_SECONDS = 5
TradeService.INVITE_SECONDS = 30
TradeService.INVITE_COOLDOWN_SECONDS = 10
TradeService.WATCH_SECONDS = 1
TradeService.SAVE_ATTEMPTS = 3
TradeService.SAVE_RETRY_SECONDS = 2
TradeService.RECONCILE_RETRY_SECONDS = 60

-- The profile groups a settlement touches, restored together if it fails.
local SETTLED_GROUPS = { "lobbyBackpack", "vault", "permanentItems", "currency", "trades" }
local SERVER = if game.JobId ~= "" then game.JobId else nil

local sessions = {}
local sessionOf = {}
local lastInvite = {}
local reconciling = {}

-- A stable key for a backpack slot: its instance ID, or "stack:<catalogId>".
local function keyOf(item): string
	return item.instanceId or ("stack:" .. item.catalogId)
end

-- True while `player` is in an accepted trade session.
function TradeService.InSession(player: Player): boolean
	local session = sessionOf[player]
	return session ~= nil and session.accepted
end

-- Snapshots the offered slots and vault materials ({[catalogId] = quantity}) as
-- {key, quantity}, or nil if a slot is missing. Material keys are "mat:<catalogId>".
local function snapshotOffer(profile, keys, materials)
	local entries, used = {}, {}
	for _, key in keys do
		if type(key) ~= "string" or #key > 64 or TradeRules.MaterialOf(key) then
			continue
		end
		local found = nil
		for index, item in profile.lobbyBackpack.slots do
			if not used[index] and keyOf(item) == key then
				found = index
				break
			end
		end
		if found == nil then
			return nil
		end
		used[found] = true
		table.insert(entries, { key = key, quantity = profile.lobbyBackpack.slots[found].quantity })
		if #entries > TradeRules.MAX_ITEMS then
			return entries
		end
	end
	for catalogId, quantity in materials do
		table.insert(entries, { key = TradeRules.MaterialKey(catalogId), quantity = quantity })
		if #entries > TradeRules.MAX_ITEMS then
			break
		end
	end
	return entries
end

-- The TradeRules offer (slot indexes and vault materials) matching every snapshot
-- entry exactly, or nil if anything changed.
local function resolve(profile, entries, gems: number)
	local indexes, materials = {}, {}
	for _, entry in entries do
		local catalogId = TradeRules.MaterialOf(entry.key)
		if catalogId then
			local total = (materials[catalogId] or 0) + entry.quantity
			if (profile.vault.materials[catalogId] or 0) < total then
				return nil
			end
			materials[catalogId] = total
			continue
		end
		local found = nil
		for index, item in profile.lobbyBackpack.slots do
			if keyOf(item) == entry.key and item.quantity == entry.quantity and not table.find(indexes, index) then
				found = index
				break
			end
		end
		if found == nil then
			return nil
		end
		table.insert(indexes, found)
	end
	return { items = indexes, materials = materials, gems = gems }
end

local function fingerprint(player: Player): string
	local profile = ProfileService.GetProfile(player)
	if profile == nil then
		return ""
	end
	local parts, stock = {}, {}
	for _, item in profile.lobbyBackpack.slots do
		table.insert(parts, keyOf(item) .. "x" .. tostring(item.quantity or 1))
	end
	-- Vault materials too, since offers draw on them.
	for catalogId, quantity in profile.vault.materials do
		table.insert(stock, TradeRules.MaterialKey(catalogId) .. "x" .. tostring(quantity))
	end
	table.sort(stock)
	return table.concat(parts, "|") .. "#" .. table.concat(stock, "|")
end

local function other(session, player: Player): Player
	return if session.a == player then session.b else session.a
end

local function describe(profile, offer)
	local list = {}
	for _, entry in offer.items do
		local catalogId = TradeRules.MaterialOf(entry.key)
		if catalogId then
			local def = ItemCatalog.Get(catalogId)
			table.insert(list, { key = entry.key, name = def and def.name or catalogId, quantity = entry.quantity })
			continue
		end
		for _, item in profile.lobbyBackpack.slots do
			if keyOf(item) == entry.key then
				local def = ItemCatalog.Get(item.catalogId)
				table.insert(list, {
					key = entry.key,
					name = (item.permanent and "★ " or "") .. (def and def.name or item.catalogId),
					quantity = entry.quantity,
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
		if sessionOf[player] == session then
			sessionOf[player] = nil
		end
		if player.Parent then
			Remotes.Get("TradeChanged"):FireClient(player, { kind = "Closed", id = session.id, reason = reason })
		end
	end
end

local function stamp(session)
	session.prints = { [session.a] = fingerprint(session.a), [session.b] = fingerprint(session.b) }
end

-- Any change to either backpack unlocks both sides and updates both screens.
-- Returns true when something changed.
local function refresh(session): boolean
	local changed = false
	for _, player in { session.a, session.b } do
		local now = fingerprint(player)
		if now ~= session.prints[player] then
			session.prints[player] = now
			changed = true
		end
	end
	if changed then
		session.locked, session.confirmed, session.confirmAt = {}, {}, nil
		push(session)
	end
	return changed
end

local function watch(session)
	while sessions[session.id] == session do
		task.wait(TradeService.WATCH_SECONDS)
		if sessions[session.id] == session then
			refresh(session)
		end
	end
end

-- On load (and every minute while deferred), settle or undo any trade an
-- earlier session left pending.
local function reconcile(player: Player)
	if reconciling[player] then
		return
	end
	reconciling[player] = true
	while player.Parent do
		local profile = ProfileService.GetProfile(player)
		if profile == nil or next(profile.trades.pending) == nil then
			break
		end
		local deferred = false
		for tradeId, pending in table.clone(profile.trades.pending) do
			local ok, stored = ProfileService.ReadStored(pending.counterpart)
			local outcome = nil
			if ok then
				ProfileService.Mutate(player, function(live)
					outcome = TradeRules.Reconcile(live, tradeId, stored, os.time())
				end)
			end
			if outcome == "RolledBack" then
				warn(("[TradeService] Trade %s for %d rolled back after a crash"):format(tradeId, player.UserId))
			end
			deferred = deferred or outcome == nil or outcome == "Deferred"
		end
		CurrencyService.Publish(player)
		if not deferred then
			break
		end
		task.wait(TradeService.RECONCILE_RETRY_SECONDS)
	end
	reconciling[player] = nil
end

-- Applies the trade to both profiles at once; on any error both are restored.
local function transfer(tradeId: string, sides, now: number): boolean
	local backups = {}
	for _, side in sides do
		local backup = {}
		for _, group in SETTLED_GROUPS do
			backup[group] = ProfileSchema.DeepCopy(side.profile[group])
		end
		backups[side] = backup
	end
	local ok, err = pcall(function()
		TradeRules.Settle(tradeId, sides[1], sides[2], now)
		for _, side in sides do
			side.profile.trades.pending[tradeId].server = SERVER
		end
	end)
	if not ok then
		for side, backup in backups do
			for group, value in backup do
				side.profile[group] = value
			end
		end
		warn(("[TradeService] Trade %s failed and was undone: %s"):format(tradeId, tostring(err)))
	end
	return ok
end

-- Saves both sides (retrying), and finalises only once both saves landed.
local function finish(tradeId: string, players: { Player })
	local saved = {}
	for attempt = 1, TradeService.SAVE_ATTEMPTS do
		local gone = false
		for _, player in players do
			if not saved[player] then
				saved[player] = player.Parent ~= nil and ProfileService.SaveNow(player) == true
				gone = gone or player.Parent == nil
			end
		end
		if gone then
			break
		end
		if saved[players[1]] and saved[players[2]] then
			for _, player in players do
				ProfileService.Mutate(player, function(profile)
					TradeRules.Finalize(profile, tradeId, os.time())
				end)
			end
			return
		end
		if attempt < TradeService.SAVE_ATTEMPTS then
			task.wait(TradeService.SAVE_RETRY_SECONDS)
		end
	end
	-- Unconfirmed: each side still here resolves it against the other's saved copy.
	for _, player in players do
		if player.Parent then
			task.spawn(reconcile, player)
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
	local offerA = resolve(pa, session.offers[a].items, session.offers[a].gems)
	local offerB = resolve(pb, session.offers[b].items, session.offers[b].gems)
	if offerA == nil or offerB == nil then
		close(session, "ItemsChanged")
		return
	end
	-- Re-check both sides at the moment of settlement (§24): nothing ineligible
	-- passes even if both players accepted.
	local checks = {
		{ TradeRules.ValidateOffer(pa, offerA, now) },
		{ TradeRules.ValidateOffer(pb, offerB, now) },
		{ TradeRules.ValidateReceive(pb, offerA.gems, now, offerA.materials) },
		{ TradeRules.ValidateReceive(pa, offerB.gems, now, offerB.materials) },
	}
	for _, check in checks do
		if not check[1] then
			close(session, check[2])
			return
		end
	end
	local tradeId = "trade:" .. HttpService:GenerateGUID(false)
	-- Both profiles change together, with no yield in between.
	local sides = {
		{ profile = pa, userId = a.UserId, offer = offerA },
		{ profile = pb, userId = b.UserId, offer = offerB },
	}
	if not transfer(tradeId, sides, now) then
		close(session, "Failed")
		return
	end
	ProfileService.Mutate(a, function() end)
	ProfileService.Mutate(b, function() end)
	close(session, "Completed")
	CurrencyService.Publish(a)
	CurrencyService.Publish(b)
	task.spawn(finish, tradeId, { a, b })
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
	if not target or target == player or sessionOf[player] or TradeService.InSession(target) then
		return false, "Unavailable"
	end
	if ProfileService.GetProfile(player) == nil or ProfileService.GetProfile(target) == nil then
		return false, "Unavailable"
	end
	local pair = player.UserId .. ":" .. target.UserId
	local now = os.clock()
	if lastInvite[pair] and now - lastInvite[pair] < TradeService.INVITE_COOLDOWN_SECONDS then
		return false, "Cooldown"
	end
	lastInvite[pair] = now
	local session = {
		id = HttpService:GenerateGUID(false),
		a = player,
		b = target,
		accepted = false,
		offers = { [player] = { items = {}, gems = 0 }, [target] = { items = {}, gems = 0 } },
		locked = {},
		confirmed = {},
		prints = {},
	}
	sessions[session.id] = session
	-- Only the inviter is bound now; the target is bound when they accept.
	sessionOf[player] = session
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
	local current = sessionOf[player]
	if current and current.accepted then
		return false, "Unavailable"
	end
	if current then
		-- Accepting replaces this player's own outgoing invite.
		close(current, "Cancelled")
	end
	sessionOf[player] = session
	session.accepted = true
	stamp(session)
	push(session)
	task.spawn(watch, session)
	return true, nil
end

-- Bounds a client's {[catalogId] = quantity} vault material offer, or nil.
local function materialsArg(materials: any)
	if materials == nil then
		return {}
	end
	if type(materials) ~= "table" then
		return nil
	end
	local count = 0
	for catalogId, quantity in materials do
		count += 1
		if count > TradeRules.MAX_ITEMS or not Validation.IsId(catalogId) or not Validation.IsQuantity(quantity, 1) then
			return nil
		end
	end
	return materials
end

local function offer(player: Player, id: any, keys: any, gems: any, materials: any)
	local session = sessionFor(player, id)
	materials = materialsArg(materials)
	if
		session == nil
		or not session.accepted
		or type(keys) ~= "table"
		or type(gems) ~= "number"
		or materials == nil
	then
		return false, "BadRequest"
	end
	local profile = ProfileService.GetProfile(player)
	local partner = ProfileService.GetProfile(other(session, player))
	if profile == nil or partner == nil then
		return false, "Unavailable"
	end
	local entries = snapshotOffer(profile, keys, materials)
	if entries == nil then
		return false, "MissingItem"
	end
	local now = os.time()
	local resolved = resolve(profile, entries, gems)
	if resolved == nil then
		return false, "MissingItem"
	end
	local ok, reason = TradeRules.ValidateOffer(profile, resolved, now)
	if ok then
		ok, reason = TradeRules.ValidateReceive(partner, gems, now, resolved.materials)
	end
	if not ok then
		return false, reason
	end
	session.offers[player] = { items = entries, gems = gems }
	-- Any change unlocks both sides (cancel protection).
	session.locked, session.confirmed, session.confirmAt = {}, {}, nil
	stamp(session)
	push(session)
	return true, nil
end

local function lock(player: Player, id: any)
	local session = sessionFor(player, id)
	if session == nil or not session.accepted then
		return false, "BadRequest"
	end
	local profile = ProfileService.GetProfile(player)
	if refresh(session) or profile == nil or resolve(profile, session.offers[player].items, 0) == nil then
		return false, "ItemsChanged"
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
	if refresh(session) then
		return false, "ItemsChanged"
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
			task.spawn(reconcile, player)
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
		for _, session in table.clone(sessions) do
			if session.a == player or session.b == player then
				close(session, "PartnerLeft")
			end
		end
		local prefix, suffix = player.UserId .. ":", ":" .. player.UserId
		for pair in table.clone(lastInvite) do
			if pair:sub(1, #prefix) == prefix or pair:sub(-#suffix) == suffix then
				lastInvite[pair] = nil
			end
		end
	end)
end

return TradeService
