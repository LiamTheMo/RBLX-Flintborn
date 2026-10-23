-- Lobby trading (GDD §10.2, Q13, Q50, Q56, Q98, Q125, Q130). Two players in the
-- same lobby trade designated items and Gems — never Coins. Raw materials trade
-- only when flagged rare or Exclusive. Gem trades need level 10 on both sides, are
-- capped per UTC day for sending and receiving, and pay a 5% fee. Settlement
-- writes the trade into both profiles as pending; Reconcile later finalises it
-- (the counterpart saved it too) or rolls one side back (the counterpart never
-- saved it, or rolled back), and waits while the counterpart may still save.
-- Until then the profile is "settling": nothing a rollback could not claw back
-- (sales, Forge crafts, Gem spending, a Deploy) may consume what it received.

local ItemCatalog = require(script.Parent.Parent.Items.ItemCatalog)
local PermanentRules = require(script.Parent.Parent.Items.PermanentRules)

local TradeRules = {}

TradeRules.MIN_GEM_LEVEL = 10
TradeRules.DAILY_GEM_LIMIT = 2000
TradeRules.GEM_FEE = 0.05
TradeRules.MAX_ITEMS = 9
TradeRules.HISTORY = 500
-- Why a sale, craft, Gem spend or Deploy is refused while a trade may roll back.
TradeRules.SETTLING = "TradeSettling"

local TRADEABLE_FAMILIES = { Tool = true, Weapon = true, Armor = true, Placeable = true }

-- Designated items only (Q130): gear, tools, placeables (runes), Permanent items,
-- and materials flagged rare/Exclusive (Q56).
function TradeRules.IsTradeable(item): boolean
	local def = ItemCatalog.Get(item.catalogId)
	if def == nil then
		return false
	end
	if item.permanent then
		return true
	end
	if def.family == ItemCatalog.Families.Material then
		return def.special == true or def.rarity == "Exclusive"
	end
	return TRADEABLE_FAMILIES[def.family] == true
end

-- True while a settled trade awaits its counterpart's save (Reconcile clears it).
function TradeRules.IsSettling(profile): boolean
	return next(profile.trades.pending) ~= nil
end

local function today(now: number): number
	return now // 86400
end

-- Checks one side's offer against its own profile. offer = {items = {instanceId
-- or catalogId keys of lobby backpack slots...}, gems, coins?}.
function TradeRules.ValidateOffer(profile, offer, now: number)
	if offer.coins ~= nil and offer.coins ~= 0 then
		return false, "CoinsNotTradeable"
	end
	-- A trade still awaiting its counterpart's save could yet be undone.
	if TradeRules.IsSettling(profile) then
		return false, "TradePending"
	end
	if #offer.items > TradeRules.MAX_ITEMS then
		return false, "TooManyItems"
	end
	local seen = {}
	for _, index in offer.items do
		local item = profile.lobbyBackpack.slots[index]
		if item == nil or seen[index] then
			return false, "MissingItem"
		end
		seen[index] = true
		if not TradeRules.IsTradeable(item) then
			return false, "NotTradeable"
		end
	end
	local gems = offer.gems or 0
	if gems < 0 or gems % 1 ~= 0 then
		return false, "BadGems"
	end
	if gems > 0 then
		if profile.progression.level < TradeRules.MIN_GEM_LEVEL then
			return false, "GemLevel"
		end
		if profile.currency.gems < gems then
			return false, "NotEnoughGems"
		end
		local sentToday = if profile.currency.gemTradeDay == today(now) then profile.currency.gemsTradedToday else 0
		if sentToday + gems > TradeRules.DAILY_GEM_LIMIT then
			return false, "GemDailyLimit"
		end
	end
	return true, nil
end

function TradeRules.GemsAfterFee(gems: number): number
	return math.floor(gems * (1 - TradeRules.GEM_FEE))
end

-- Checks that `profile` may receive `gems` (before the fee) today.
function TradeRules.ValidateReceive(profile, gems: number, now: number)
	if gems <= 0 then
		return true, nil
	end
	if profile.progression.level < TradeRules.MIN_GEM_LEVEL then
		return false, "PartnerGemLevel"
	end
	local currency = profile.currency
	local receivedToday = if currency.gemReceiveDay == today(now) then currency.gemsReceivedToday else 0
	if receivedToday + TradeRules.GemsAfterFee(gems) > TradeRules.DAILY_GEM_LIMIT then
		return false, "PartnerGemDailyLimit"
	end
	return true, nil
end

-- Takes the offered items and Gems out of the giver. Returns what was taken.
local function takeOffer(profile, offer, now: number)
	local indexes = table.clone(offer.items)
	table.sort(indexes, function(a, b)
		return a > b
	end)
	local items = {}
	for _, index in indexes do
		local item = table.remove(profile.lobbyBackpack.slots, index)
		if item.permanent then
			-- Trading a Permanent item hands over ownership (Q13).
			profile.permanentItems[item.instanceId] = nil
		end
		table.insert(items, item)
	end
	local gems = offer.gems or 0
	if gems > 0 then
		local currency = profile.currency
		if currency.gemTradeDay ~= today(now) then
			currency.gemTradeDay, currency.gemsTradedToday = today(now), 0
		end
		currency.gemsTradedToday += gems
		currency.gems -= gems
	end
	return { items = items, gems = gems }
end

local function give(profile, taken, receiverId: number, now: number)
	for _, item in taken.items do
		local copy = table.clone(item)
		if copy.instanceId then
			copy.ownerId = receiverId
			copy.location = "LobbyBackpack"
			if copy.permanent then
				copy.ownershipVersion = (copy.ownershipVersion or 1) + 1
				profile.permanentItems[copy.instanceId] = PermanentRules.LedgerEntry(copy, now)
			end
		end
		-- Received items always land, even past 50 slots: a trade never deletes.
		table.insert(profile.lobbyBackpack.slots, copy)
	end
	local gems = TradeRules.GemsAfterFee(taken.gems)
	if gems > 0 then
		local currency = profile.currency
		if currency.gemReceiveDay ~= today(now) then
			currency.gemReceiveDay, currency.gemsReceivedToday = today(now), 0
		end
		currency.gemsReceivedToday += gems
		currency.gems += gems
	end
end

-- Settles a validated trade between two loaded profiles. Both get a pending record
-- naming what they gave and received, for Reconcile after a crash.
function TradeRules.Settle(tradeId: string, a, b, now: number)
	local fromA = takeOffer(a.profile, a.offer, now)
	local fromB = takeOffer(b.profile, b.offer, now)
	give(a.profile, fromB, a.userId, now)
	give(b.profile, fromA, b.userId, now)
	a.profile.trades.pending[tradeId] = { counterpart = b.userId, gave = fromA, received = fromB, at = now }
	b.profile.trades.pending[tradeId] = { counterpart = a.userId, gave = fromB, received = fromA, at = now }
end

local function record(profile, tradeId: string, outcome: string, now: number)
	profile.trades.pending[tradeId] = nil
	profile.trades.history[tradeId] = { outcome = outcome, at = now }
	local ids = {}
	for id in profile.trades.history do
		table.insert(ids, id)
	end
	table.sort(ids, function(x, y)
		return profile.trades.history[x].at < profile.trades.history[y].at
	end)
	for index = 1, #ids - TradeRules.HISTORY do
		profile.trades.history[ids[index]] = nil
	end
end

-- Clears a pending trade once both sides are known to be saved.
function TradeRules.Finalize(profile, tradeId: string, now: number)
	record(profile, tradeId, "Settled", now)
end

-- True while the counterpart's stored lease is unexpired and held by the server
-- that settled the trade (or an unknown one): that server may still save it.
function TradeRules.CounterpartMaySave(pending, counterpartStored, now: number): boolean
	local lease = counterpartStored and counterpartStored.sessionLease
	if lease == nil or lease.expiresAt <= now then
		return false
	end
	return pending.server == nil or lease.jobId == pending.server
end

-- Removes up to `quantity` of a stack from a list of slots. Returns what is left.
local function takeStack(slots, catalogId: string, quantity: number): number
	for index = #slots, 1, -1 do
		local slot = slots[index]
		if quantity <= 0 then
			break
		end
		if slot.instanceId == nil and slot.catalogId == catalogId then
			local taken = math.min(quantity, slot.quantity)
			slot.quantity -= taken
			quantity -= taken
			if slot.quantity <= 0 then
				table.remove(slots, index)
			end
		end
	end
	return quantity
end

local function takeInstance(slots, instanceId: string): boolean
	for index, slot in slots do
		if slot.instanceId == instanceId then
			table.remove(slots, index)
			return true
		end
	end
	return false
end

-- Claws a received item back from wherever it now sits: backpack, then vault.
local function takeBack(profile, item)
	if item.instanceId then
		if item.permanent then
			profile.permanentItems[item.instanceId] = nil
		end
		if not takeInstance(profile.lobbyBackpack.slots, item.instanceId) then
			takeInstance(profile.vault.items, item.instanceId)
		end
		return
	end
	local left = takeStack(profile.lobbyBackpack.slots, item.catalogId, item.quantity or 0)
	left = takeStack(profile.vault.items, item.catalogId, left)
	local materials = profile.vault.materials
	if left > 0 and materials[item.catalogId] then
		local remaining = materials[item.catalogId] - left
		materials[item.catalogId] = if remaining > 0 then remaining else nil
	end
end

local function rollBack(profile, pending, now: number)
	for _, item in pending.received.items do
		takeBack(profile, item)
	end
	for _, item in pending.gave.items do
		table.insert(profile.lobbyBackpack.slots, table.clone(item))
		if item.permanent then
			profile.permanentItems[item.instanceId] = PermanentRules.LedgerEntry(item, now)
		end
	end
	local currency = profile.currency
	currency.gems = math.max(0, currency.gems - TradeRules.GemsAfterFee(pending.received.gems) + pending.gave.gems)
end

-- Resolves a pending trade against the counterpart's saved profile. It stands if
-- the counterpart has it pending or settled; it waits ("Deferred") while the
-- counterpart's server may still save it; otherwise this side is undone. Returns
-- "None", "Settled", "Deferred" or "RolledBack".
function TradeRules.Reconcile(profile, tradeId: string, counterpartStored, now: number): string
	local pending = profile.trades.pending[tradeId]
	if pending == nil then
		return "None"
	end
	local other = counterpartStored and counterpartStored.trades
	local entry = other and other.history[tradeId]
	if other and (other.pending[tradeId] or (entry and entry.outcome == "Settled")) then
		record(profile, tradeId, "Settled", now)
		return "Settled"
	end
	if entry == nil and TradeRules.CounterpartMaySave(pending, counterpartStored, now) then
		return "Deferred"
	end
	rollBack(profile, pending, now)
	record(profile, tradeId, "RolledBack", now)
	return "RolledBack"
end

return TradeRules
