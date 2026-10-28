-- Lobby trading (GDD §10.2, Q13, Q50, Q56, Q98, Q125, Q130, Q164). Two players in
-- the same lobby trade designated items and Gems — never Coins. Raw materials trade
-- only when flagged rare or Exclusive, and only out of the vault, where every
-- material lives; they land in the receiver's vault, so an offer needs room there
-- and a trade never deletes. Gem trades need level 10 on both sides, are
-- capped per UTC day for sending and receiving, and pay a 5% fee. Settlement
-- writes the trade into both profiles as pending; Reconcile later finalises it
-- (the counterpart saved it too) or rolls one side back (the counterpart never
-- saved it, or rolled back), and waits while the counterpart may still save.
-- Until then the profile is "settling": nothing a rollback could not claw back
-- (sales, Forge crafts, Gem spending, a Deploy) may consume what it received.

local GameConstants = require(script.Parent.Parent.GameConstants)
local ItemCatalog = require(script.Parent.Parent.Items.ItemCatalog)
local PermanentRules = require(script.Parent.Parent.Items.PermanentRules)
local Validation = require(script.Parent.Parent.Data.Validation)

local TradeRules = {}

TradeRules.MIN_GEM_LEVEL = 10
TradeRules.DAILY_GEM_LIMIT = 2000
TradeRules.GEM_FEE = 0.05
TradeRules.MAX_ITEMS = 9
TradeRules.HISTORY = 500
-- Why a sale, craft, Gem spend or Deploy is refused while a trade may roll back.
TradeRules.SETTLING = "TradeSettling"
-- Offer key of a vault material: "mat:<catalogId>".
TradeRules.MATERIAL_PREFIX = "mat:"

local TRADEABLE_FAMILIES = { Tool = true, Weapon = true, Armor = true, Placeable = true }

-- Designated items only (Q130): gear, tools, placeables (runes), Permanent items,
-- and materials or consumables flagged tradeable (rare materials and berries, GDD
-- §51) or Exclusive (Q56).
function TradeRules.IsTradeable(item): boolean
	local def = ItemCatalog.Get(item.catalogId)
	if def == nil then
		return false
	end
	if item.permanent then
		return true
	end
	if def.family == ItemCatalog.Families.Material or def.family == ItemCatalog.Families.Consumable then
		return def.tradeable == true or def.rarity == "Exclusive"
	end
	return TRADEABLE_FAMILIES[def.family] == true
end

-- A lobby backpack slot that may be offered: never a material, which trades only
-- from the vault (Q164).
function TradeRules.IsTradeableSlot(item): boolean
	return not ItemCatalog.IsMaterial(item.catalogId) and TradeRules.IsTradeable(item)
end

-- A vault material that may be offered: flagged rare or Exclusive (Q56).
function TradeRules.IsTradeableMaterial(catalogId: any): boolean
	return type(catalogId) == "string"
		and ItemCatalog.IsMaterial(catalogId)
		and TradeRules.IsTradeable({ catalogId = catalogId })
end

function TradeRules.MaterialKey(catalogId: string): string
	return TradeRules.MATERIAL_PREFIX .. catalogId
end

-- The catalog ID a vault material offer key names, or nil for a backpack key.
function TradeRules.MaterialOf(key: string): string?
	local prefix = TradeRules.MATERIAL_PREFIX
	return if key:sub(1, #prefix) == prefix then key:sub(#prefix + 1) else nil
end

-- True while a settled trade awaits its counterpart's save (Reconcile clears it).
function TradeRules.IsSettling(profile): boolean
	return next(profile.trades.pending) ~= nil
end

local function today(now: number): number
	return now // 86400
end

-- Checks one side's offer against its own profile. offer = {items = {lobby
-- backpack slot indexes...}, materials = {[catalogId] = vault quantity}?, gems,
-- coins?}.
function TradeRules.ValidateOffer(profile, offer, now: number)
	if offer.coins ~= nil and offer.coins ~= 0 then
		return false, "CoinsNotTradeable"
	end
	-- A trade still awaiting its counterpart's save could yet be undone.
	if TradeRules.IsSettling(profile) then
		return false, "TradePending"
	end
	local count = #offer.items
	for _ in offer.materials or {} do
		count += 1
	end
	if count > TradeRules.MAX_ITEMS then
		return false, "TooManyItems"
	end
	local seen = {}
	for _, index in offer.items do
		local item = profile.lobbyBackpack.slots[index]
		if item == nil or seen[index] then
			return false, "MissingItem"
		end
		seen[index] = true
		if not TradeRules.IsTradeableSlot(item) then
			return false, "NotTradeable"
		end
	end
	for catalogId, quantity in offer.materials or {} do
		if not Validation.IsQuantity(quantity, 1) then
			return false, "BadQuantity"
		end
		if not TradeRules.IsTradeableMaterial(catalogId) then
			return false, "NotTradeable"
		end
		if (profile.vault.materials[catalogId] or 0) < quantity then
			return false, "MissingItem"
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

-- Checks that `profile` may receive `gems` (before the fee) today, and has vault
-- room for `materials` ({[catalogId] = quantity}): a trade never deletes.
function TradeRules.ValidateReceive(profile, gems: number, now: number, materials: { [string]: number }?)
	for catalogId, quantity in materials or {} do
		if (profile.vault.materials[catalogId] or 0) + quantity > GameConstants.MATERIAL_STACK_MAX then
			return false, "PartnerVaultFull"
		end
	end
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

-- Takes the offered items, vault materials and Gems out of the giver. Returns
-- what was taken.
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
	local materials = {}
	for catalogId, quantity in offer.materials or {} do
		local left = (profile.vault.materials[catalogId] or 0) - quantity
		-- Never give what is not there (the caller restores both profiles).
		assert(left >= 0, "MissingMaterial")
		profile.vault.materials[catalogId] = if left > 0 then left else nil
		materials[catalogId] = quantity
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
	return { items = items, materials = materials, gems = gems }
end

-- Banks materials into a vault; anything over the capacity is deleted (Q154).
local function bank(profile, materials)
	for catalogId, quantity in materials or {} do
		local stored = GameConstants.SettleMaterialStack(profile.vault.materials[catalogId] or 0, quantity)
		profile.vault.materials[catalogId] = if stored > 0 then stored else nil
	end
end

-- Puts a received or returned item into the lobby backpack. A stack (a tradeable
-- consumable such as Sunberry) tops up the slot of its type first, keeping one
-- slot per type (Q128); whatever is over the cap gets its own slot, since a trade
-- never deletes.
local function land(slots, item)
	local cap = if item.instanceId == nil then ItemCatalog.StackCap(item.catalogId) else nil
	if cap then
		local quantity = item.quantity or 0
		for _, slot in slots do
			if quantity <= 0 then
				break
			end
			if slot.instanceId == nil and slot.catalogId == item.catalogId and slot.quantity < cap then
				local added = math.min(quantity, cap - slot.quantity)
				slot.quantity += added
				quantity -= added
			end
		end
		if quantity <= 0 then
			return
		end
		item.quantity = quantity
	end
	table.insert(slots, item)
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
		land(profile.lobbyBackpack.slots, copy)
	end
	-- ValidateReceive made room for them.
	bank(profile, taken.materials)
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

-- Claws received vault materials back: vault first, then any backpack stack.
local function takeMaterials(profile, materials)
	local stock = profile.vault.materials
	for catalogId, quantity in materials or {} do
		local taken = math.min(quantity, stock[catalogId] or 0)
		local remaining = (stock[catalogId] or 0) - taken
		stock[catalogId] = if remaining > 0 then remaining else nil
		takeStack(profile.lobbyBackpack.slots, catalogId, quantity - taken)
	end
end

local function rollBack(profile, pending, now: number)
	for _, item in pending.received.items do
		takeBack(profile, item)
	end
	takeMaterials(profile, pending.received.materials)
	for _, item in pending.gave.items do
		land(profile.lobbyBackpack.slots, table.clone(item))
		if item.permanent then
			profile.permanentItems[item.instanceId] = PermanentRules.LedgerEntry(item, now)
		end
	end
	-- Given materials go back to the vault; past its capacity they are deleted.
	bank(profile, pending.gave.materials)
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
