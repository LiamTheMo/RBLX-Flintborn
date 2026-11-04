-- Server half of Shared.Economy.EconomyRules: what only the server uses. Everything in
-- ReplicatedStorage is downloaded to every player, so the shared module keeps
-- only what clients need; this one clones it and adds the rest, and server code
-- requires this module.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local ExtractionRules = require(script.Parent.Parent.Extraction.ExtractionRules)
local GameConstants = require(ReplicatedStorage.Shared.GameConstants)
local ItemCatalog = require(script.Parent.Parent.Items.ItemCatalog)
local PerkCatalog = require(script.Parent.Parent.Progression.PerkCatalog)
local QuestCatalog = require(script.Parent.QuestCatalog)
local Receipts = require(script.Parent.Parent.Data.Receipts)
local ShopCatalog = require(script.Parent.ShopCatalog)
local TradeRules = require(script.Parent.TradeRules)
local SharedEconomyRules = require(ReplicatedStorage.Shared.Economy.EconomyRules)

local EconomyRules = table.clone(SharedEconomyRules)

EconomyRules.VAULT_UPGRADE_GEMS = 500
EconomyRules.MAX_VAULT_TIER = 8
EconomyRules.RESPEC_GEMS = 250

function EconomyRules.Grant(profile, coins: number?, gems: number?)
	profile.currency.coins += math.max(0, coins or 0)
	profile.currency.gems += math.max(0, gems or 0)
end

-- Spends all or nothing. Returns (ok, reason). Gems wait while a trade settles:
-- its rollback could not take back Gems already spent.
function EconomyRules.Spend(profile, coins: number?, gems: number?)
	local currency = profile.currency
	if (gems or 0) > 0 and TradeRules.IsSettling(profile) then
		return false, TradeRules.SETTLING
	end
	if currency.coins < (coins or 0) then
		return false, "NotEnoughCoins"
	end
	if currency.gems < (gems or 0) then
		return false, "NotEnoughGems"
	end
	currency.coins -= coins or 0
	currency.gems -= gems or 0
	return true, nil
end

-- Same Gem price for every tier (Q122); +25 slots each (Q96).
function EconomyRules.VaultUpgradePrice(_tier: number): number
	return EconomyRules.VAULT_UPGRADE_GEMS
end

function EconomyRules.AddVaultTier(profile)
	if (profile.vault.upgradeTier or 0) >= EconomyRules.MAX_VAULT_TIER then
		return false, "MaxTier"
	end
	profile.vault.upgradeTier = (profile.vault.upgradeTier or 0) + 1
	return true, nil
end

function EconomyRules.BuyVaultTier(profile)
	if (profile.vault.upgradeTier or 0) >= EconomyRules.MAX_VAULT_TIER then
		return false, "MaxTier"
	end
	local ok, reason = EconomyRules.Spend(profile, 0, EconomyRules.VaultUpgradePrice(profile.vault.upgradeTier))
	if not ok then
		return false, reason
	end
	return EconomyRules.AddVaultTier(profile)
end

function EconomyRules.AddBooster(profile, seconds: number, now: number)
	profile.boosters.xpUntil = math.max(profile.boosters.xpUntil or 0, now) + seconds
end

-- Refunds every token spent on perks (Q89).
function EconomyRules.Respec(profile)
	local refund = 0
	for perkId, rank in profile.rebirth.ownedPerks do
		local perk = PerkCatalog.Get(perkId)
		for index = 1, rank do
			refund += perk and perk.costs[index] or 0
		end
	end
	if refund == 0 then
		return false, "NothingToRespec"
	end
	profile.rebirth.ownedPerks = {}
	profile.rebirth.tokens += refund
	return true, nil
end

-- The most of one shop entry a single purchase may buy (a pack counts once).
EconomyRules.MAX_BUY_QUANTITY = 50

-- Whether `quantity` is a whole number from 1 to `max` (never NaN or infinite).
local function wholeCount(quantity: any, max: number): boolean
	return type(quantity) == "number"
		and quantity == quantity
		and quantity >= 1
		and quantity <= max
		and quantity % 1 == 0
end

-- How many of shop entry `entry` (packs) the lobby backpack has room for: a
-- stackable item fills its one stack up to the cap (Q128), anything else takes
-- a free slot per copy; a title fits once.
function EconomyRules.BuyRoom(profile, entry): number
	if entry.catalogId == nil then
		return if profile.progression.titles[entry.title] then 0 else 1
	end
	local slots = profile.lobbyBackpack.slots
	local cap = ItemCatalog.StackCap(entry.catalogId)
	if cap == nil then
		return math.max(0, GameConstants.BACKPACK_SLOTS - #slots)
	end
	local pack = math.max(1, entry.quantity or 1)
	for _, slot in slots do
		if slot.instanceId == nil and slot.catalogId == entry.catalogId then
			return math.max(0, cap - (slot.quantity or 0)) // pack
		end
	end
	return if #slots >= GameConstants.BACKPACK_SLOTS then 0 else cap // pack
end

-- The most of shop entry `stockId` one purchase can buy now: the per-purchase
-- limit, what the player's Coins cover and what the backpack holds (0: none).
function EconomyRules.MaxBuy(profile, stockId: any): number
	local entry = ShopCatalog.ById[stockId]
	if entry == nil then
		return 0
	end
	local limit = if entry.title then 1 else EconomyRules.MAX_BUY_QUANTITY
	local afford = math.floor(profile.currency.coins / entry.price)
	return math.max(0, math.min(limit, afford, EconomyRules.BuyRoom(profile, entry)))
end

-- Buys `quantity` (default 1) of one shop entry, all or nothing: every copy must
-- fit the lobby backpack and the Coins must cover them all. Items land in the
-- lobby backpack, titles (one only) in the profile. `quantity` comes from the
-- client, so anything but a whole number in 1..MAX_BUY_QUANTITY is refused.
function EconomyRules.Buy(profile, stockId: any, newId: () -> string, ownerId: number, quantity: any?)
	local entry = ShopCatalog.ById[stockId]
	if entry == nil then
		return false, "UnknownItem"
	end
	local count = if quantity == nil then 1 else quantity
	if not wholeCount(count, if entry.title then 1 else EconomyRules.MAX_BUY_QUANTITY) then
		return false, "BadQuantity"
	end
	if entry.title and profile.progression.titles[entry.title] then
		return false, "AlreadyOwned"
	end
	local items = {}
	if entry.catalogId then
		if ItemCatalog.IsStackable(entry.catalogId) then
			table.insert(items, { catalogId = entry.catalogId, quantity = (entry.quantity or 1) * count })
		else
			for _ = 1, count do
				table.insert(items, {
					instanceId = newId(),
					catalogId = entry.catalogId,
					ownerId = ownerId,
					location = "LobbyBackpack",
					qualityRoll = 0,
				})
			end
		end
		local trial = table.clone(profile.lobbyBackpack.slots)
		for index, slot in trial do
			trial[index] = table.clone(slot)
		end
		for _, item in items do
			if ExtractionRules.AddToLobbyBackpack(trial, table.clone(item)) > 0 then
				return false, "BackpackFull"
			end
		end
	end
	local ok, reason = EconomyRules.Spend(profile, entry.price * count, 0)
	if not ok then
		return false, reason
	end
	if entry.catalogId then
		for _, item in items do
			ExtractionRules.AddToLobbyBackpack(profile.lobbyBackpack.slots, item)
		end
	else
		profile.progression.titles[entry.title] = true
	end
	return true, nil
end

-- What a merchant pays for one backpack slot or a quantity of a vaulted material.
-- Returns (coins, warning) or (nil, reason).
function EconomyRules.Quote(item, quantity: number?)
	if item.permanent then
		return nil, "PermanentNotSold"
	end
	local value = ShopCatalog.SellValue(item.catalogId)
	if value == nil then
		return nil, "NotBought"
	end
	local amount = if item.instanceId then 1 else (quantity or item.quantity or 0)
	local warning = if ShopCatalog.ForgeInputs[item.catalogId] and ItemCatalog.Get(item.catalogId).special
		then "A Forge recipe needs this."
		else nil
	return value * amount, warning
end

-- Sells from the lobby backpack (`source` = "backpack", key = slot index) or the
-- vault's materials ("vault", key = catalogId) at fixed prices. A backpack sale
-- takes `quantity` of the slot's stack (nil: the whole slot; a unique item is
-- always one), and `expected` (the slot's catalogId as the client saw it, when
-- given) must still match, so a backpack that changed meanwhile sells nothing.
-- Quantities come from the client: anything but a whole number from 1 to what is
-- owned is refused. Waits while a trade settles: a rollback could not take back
-- what was sold.
function EconomyRules.Sell(
	profile,
	source: string,
	key: any,
	quantity: any,
	receiptId: string,
	now: number,
	expected: any?
)
	if TradeRules.IsSettling(profile) then
		return false, TradeRules.SETTLING
	end
	local coins, reason
	if source == "backpack" then
		local item = profile.lobbyBackpack.slots[key]
		if item == nil then
			return false, "Empty"
		end
		if expected ~= nil and item.catalogId ~= expected then
			return false, "SlotChanged"
		end
		local owned = if item.instanceId then 1 else (item.quantity or 1)
		local amount = if quantity == nil then owned else quantity
		if not wholeCount(amount, owned) then
			return false, "BadQuantity"
		end
		coins, reason = EconomyRules.Quote(item, amount)
		if coins == nil then
			return false, reason
		end
		if amount >= owned then
			table.remove(profile.lobbyBackpack.slots, key)
		else
			item.quantity = owned - amount
		end
	elseif source == "vault" then
		local owned = profile.vault.materials[key] or 0
		if type(quantity) ~= "number" or quantity % 1 ~= 0 or quantity <= 0 or quantity > owned then
			return false, "NotEnough"
		end
		coins, reason = EconomyRules.Quote({ catalogId = key, quantity = quantity }, quantity)
		if coins == nil then
			return false, reason
		end
		local left = owned - quantity
		profile.vault.materials[key] = if left > 0 then left else nil
	else
		return false, "BadSource"
	end
	EconomyRules.Grant(profile, coins, 0)
	Receipts.Store(profile.currency.npcSaleReceipts, receiptId, { at = now, coins = coins, source = source })
	return true, coins
end

local function questState(profile, quest, now: number)
	local period = QuestCatalog.Period(quest, now)
	local quests = profile.quests
	local entry = quests.progress[quest.id]
	if entry == nil or entry.period ~= period then
		entry = { period = period, count = 0, claimed = false }
		quests.progress[quest.id] = entry
	end
	return entry
end

-- Counts a verified action toward every matching quest.
function EconomyRules.RecordQuest(profile, action: string, now: number)
	for _, quest in QuestCatalog.Quests do
		if quest.action == action then
			local entry = questState(profile, quest, now)
			entry.count = math.min(quest.count, entry.count + 1)
		end
	end
end

function EconomyRules.QuestView(profile, now: number)
	local list = {}
	for _, quest in QuestCatalog.Quests do
		local entry = questState(profile, quest, now)
		table.insert(list, {
			id = quest.id,
			name = quest.name,
			tier = quest.tier,
			coins = quest.coins,
			gems = quest.gems,
			booster = quest.booster,
			count = entry.count,
			needed = quest.count,
			claimed = entry.claimed,
			repeats = quest.repeats,
			action = quest.action,
		})
	end
	return list
end

-- Pays a finished quest once per period.
function EconomyRules.ClaimQuest(profile, questId: any, now: number)
	local quest = QuestCatalog.Get(questId)
	if quest == nil then
		return false, "UnknownQuest"
	end
	local entry = questState(profile, quest, now)
	if entry.claimed then
		return false, "AlreadyClaimed"
	end
	if entry.count < quest.count then
		return false, "NotFinished"
	end
	entry.claimed = true
	EconomyRules.Grant(profile, quest.coins, quest.gems)
	if quest.booster then
		EconomyRules.AddBooster(profile, EconomyRules.BOOSTER_SECONDS, now)
	end
	return true, nil
end

-- Applies a Robux offer's grant (the caller makes it once per purchase ID).
function EconomyRules.Fulfil(profile, offer, now: number)
	local grant = offer.grant
	if grant.vaultTier then
		local ok, reason = EconomyRules.AddVaultTier(profile)
		if not ok then
			-- A maxed vault turns the purchase into its Gem value instead of nothing.
			EconomyRules.Grant(profile, 0, EconomyRules.VAULT_UPGRADE_GEMS)
			return true, reason
		end
	end
	if grant.boosterSeconds then
		EconomyRules.AddBooster(profile, grant.boosterSeconds, now)
	end
	if grant.respec then
		-- A paid respec with no perks to refund is worth its Gem price instead.
		if not EconomyRules.Respec(profile) then
			EconomyRules.Grant(profile, 0, EconomyRules.RESPEC_GEMS)
		end
	end
	if grant.gems then
		EconomyRules.Grant(profile, 0, grant.gems)
	end
	return true, nil
end

-- Redeems a code once per player, ever (Q89): the record outlives the operation
-- journal. A respec code with nothing to refund fails and grants nothing, so it
-- stays usable for a later respec.
function EconomyRules.RedeemCode(profile, code: string, grant, now: number)
	local redeemed = profile.currency.redeemedCodes
	if redeemed[code] then
		return false, "AlreadyRedeemed"
	end
	local rest = table.clone(grant)
	if rest.respec then
		local ok, reason = EconomyRules.Respec(profile)
		if not ok then
			return false, reason
		end
		rest.respec = nil
	end
	redeemed[code] = true
	return EconomyRules.Fulfil(profile, { grant = rest }, now)
end

-- Fulfils a Robux purchase once per purchase ID, ever: the entitlement record
-- outlives the operation journal, so a late retry grants nothing.
function EconomyRules.FulfilPurchase(profile, purchaseId: string, offer, productId: number, now: number)
	local entitlements = profile.currency.purchaseEntitlements
	if entitlements[purchaseId] then
		return true, "AlreadyGranted"
	end
	local ok, reason = EconomyRules.Fulfil(profile, offer, now)
	entitlements[purchaseId] = { offer = offer.id, at = now, productId = productId }
	return ok, reason
end

return EconomyRules
