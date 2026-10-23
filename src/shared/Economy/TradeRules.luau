-- Lobby trading (GDD §10.2, Q13, Q50, Q56, Q98, Q125, Q130). Two players in the
-- same lobby trade designated items and Gems — never Coins. Raw materials trade
-- only when flagged rare or Exclusive. Gem trades need level 10, are capped per
-- UTC day and pay a 5% fee. Settlement writes the trade into both profiles as
-- pending; Reconcile later finalises it (both sides saved) or rolls one side back
-- (the other never saved), so a crash between the two writes leaves one outcome.

local ItemCatalog = require(script.Parent.Parent.Items.ItemCatalog)
local PermanentRules = require(script.Parent.Parent.Items.PermanentRules)

local TradeRules = {}

TradeRules.MIN_GEM_LEVEL = 10
TradeRules.DAILY_GEM_LIMIT = 2000
TradeRules.GEM_FEE = 0.05
TradeRules.MAX_ITEMS = 9
TradeRules.HISTORY = 50

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

local function today(now: number): number
	return now // 86400
end

-- Checks one side's offer against its own profile. offer = {items = {instanceId
-- or catalogId keys of lobby backpack slots...}, gems, coins?}.
function TradeRules.ValidateOffer(profile, offer, now: number)
	if offer.coins ~= nil and offer.coins ~= 0 then
		return false, "CoinsNotTradeable"
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
	profile.currency.gems += TradeRules.GemsAfterFee(taken.gems)
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

-- Resolves a pending trade against the counterpart's saved profile: if the
-- counterpart also recorded it, it stands; otherwise this side is undone.
function TradeRules.Reconcile(profile, tradeId: string, counterpartStored, now: number): string
	local pending = profile.trades.pending[tradeId]
	if pending == nil then
		return "None"
	end
	local other = counterpartStored and counterpartStored.trades
	if other and (other.pending[tradeId] or other.history[tradeId]) then
		record(profile, tradeId, "Settled", now)
		return "Settled"
	end
	-- Undo: remove what was received, restore what was given.
	local slots = profile.lobbyBackpack.slots
	for _, item in pending.received.items do
		if item.permanent then
			profile.permanentItems[item.instanceId] = nil
		end
		for index = #slots, 1, -1 do
			local slot = slots[index]
			local same = if item.instanceId
				then slot.instanceId == item.instanceId
				else slot.instanceId == nil and slot.catalogId == item.catalogId
			if same then
				if item.instanceId or slot.quantity <= item.quantity then
					table.remove(slots, index)
				else
					slot.quantity -= item.quantity
				end
				break
			end
		end
	end
	for _, item in pending.gave.items do
		table.insert(slots, table.clone(item))
		if item.permanent then
			profile.permanentItems[item.instanceId] = PermanentRules.LedgerEntry(item, now)
		end
	end
	local currency = profile.currency
	currency.gems = math.max(0, currency.gems - TradeRules.GemsAfterFee(pending.received.gems) + pending.gave.gems)
	record(profile, tradeId, "RolledBack", now)
	return "RolledBack"
end

return TradeRules
