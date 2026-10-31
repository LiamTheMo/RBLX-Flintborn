-- The lobby vault and lobby backpack (GDD §10.3, §25.2, §53, Q96, Q129, Q151–152,
-- Q155). Shows the latest extraction receipt on arrival, and handles manual
-- deposits and withdrawals (items, and material stacks by quantity) through
-- exactly-once profile operations, refused during an open trade. Lobby place only.

local HttpService = game:GetService("HttpService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local GameConstants = require(ReplicatedStorage.Shared.GameConstants)
local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Signal = require(ReplicatedStorage.Shared.Core.Signal)
local TradeRules = require(ReplicatedStorage.Shared.Economy.TradeRules)
local Validation = require(ReplicatedStorage.Shared.Data.Validation)
local VaultRules = require(ReplicatedStorage.Shared.Extraction.VaultRules)
local ProfileService = require(script.Parent.ProfileService)
local TradeService = require(script.Parent.TradeService)

local VaultService = {}

-- Fires (player) after a successful manual deposit.
VaultService.Deposited = Signal.new()

VaultService.OVERFLOW_NOTICE_SECONDS = 24 * 60 * 60

local function itemView(item)
	local def = ItemCatalog.Get(item.catalogId)
	return {
		catalogId = item.catalogId,
		name = def and def.name or item.catalogId,
		rarity = def and def.rarity or "Common",
		quantity = item.quantity,
		qualityRoll = item.qualityRoll,
		permanent = item.permanent,
		-- Trade offers name slots by this key (TradeService).
		key = item.instanceId or ("stack:" .. item.catalogId),
		tradeable = TradeRules.IsTradeable(item),
	}
end

local function snapshot(player: Player)
	local profile = ProfileService.GetProfile(player)
	if profile == nil then
		return nil
	end
	local view = {
		materials = {},
		items = {},
		backpack = {},
		itemCapacity = VaultRules.ItemCapacity(profile),
		backpackCapacity = 50,
	}
	for catalogId, quantity in profile.vault.materials do
		local def = ItemCatalog.Get(catalogId)
		table.insert(view.materials, {
			catalogId = catalogId,
			name = def and def.name or catalogId,
			quantity = quantity,
			tradeable = TradeRules.IsTradeable({ catalogId = catalogId, quantity = quantity }),
		})
	end
	-- Material deposits the vault had no room for, deleted past its capacity and
	-- shown for a day (GDD §53).
	local overflow = profile.vault.lastOverflow
	if type(overflow) == "table" and os.time() - (overflow.at or 0) < VaultService.OVERFLOW_NOTICE_SECONDS then
		view.overflow = {}
		for catalogId, quantity in overflow.deleted or {} do
			local def = ItemCatalog.Get(catalogId)
			table.insert(
				view.overflow,
				{ catalogId = catalogId, name = def and def.name or catalogId, quantity = quantity }
			)
		end
	end
	table.sort(view.materials, function(a, b)
		return a.name < b.name
	end)
	for _, item in profile.vault.items do
		table.insert(view.items, itemView(item))
	end
	for _, item in profile.lobbyBackpack.slots do
		table.insert(view.backpack, itemView(item))
	end
	return view
end

local function operate(player: Player, kind: string, apply)
	-- An open trade's offers must stay exactly as offered until it ends.
	if TradeService.InSession(player) then
		return false, "InTrade"
	end
	local ok, result = ProfileService.RunOperation(
		player,
		kind .. ":" .. HttpService:GenerateGUID(false),
		kind,
		function(profile)
			-- While a Deploy holds the backpack in transit, the vault stays untouched.
			if profile.transit ~= nil then
				error("InTransit", 0)
			end
			local success, reason = apply(profile)
			if not success then
				error(reason, 0)
			end
		end
	)
	if not ok then
		return false, tostring(result)
	end
	return true, nil
end

-- Sends the newest receipt the player has not seen, then marks it seen.
local function showReceipt(player: Player, profile)
	local newestId, newest = nil, nil
	for receiptId, receipt in profile.receipts.extraction do
		if not receipt.shown and (newest == nil or receipt.at > newest.at) then
			newestId, newest = receiptId, receipt
		end
	end
	if newest == nil then
		return
	end
	Remotes.Get("ExtractionReceipt"):FireClient(player, newest)
	ProfileService.RunOperation(player, "seen:" .. newestId, "ReceiptSeen", function(working)
		for _, receipt in working.receipts.extraction do
			receipt.shown = true
		end
	end)
end

function VaultService.Start()
	if not PlaceConfig.IsLobby() then
		return
	end
	ProfileService.ProfileLoaded:Connect(showReceipt)
	Remotes.Handle("VaultSnapshot", snapshot)
	-- A material deposit that would go past the vault's capacity is refused with
	-- the amount it would delete, until the client confirms the loss (GDD §53).
	-- The confirmation names the material and the loss shown, so a stack that
	-- changed in between (a withdraw merged into it, slots shifted) is refused again.
	Remotes.Handle("VaultDeposit", function(player, index, confirmCatalogId, confirmLoss)
		if not Validation.IsQuantity(index, 1, 50) then
			return false, "BadRequest"
		end
		local confirmed = nil
		if confirmCatalogId ~= nil then
			if type(confirmCatalogId) ~= "string" or not Validation.IsQuantity(confirmLoss, 0, 1000) then
				return false, "BadRequest"
			end
			confirmed = { catalogId = confirmCatalogId, loss = confirmLoss }
		end
		local ok, reason = operate(player, "VaultDeposit", function(profile)
			return VaultRules.Deposit(profile, index, os.time(), confirmed)
		end)
		if ok then
			VaultService.Deposited:Fire(player)
		elseif reason == VaultRules.WOULD_OVERFLOW then
			local profile = ProfileService.GetProfile(player)
			return false, reason, profile and VaultRules.DepositLoss(profile, index) or 0
		end
		return ok, reason
	end)
	Remotes.Handle("VaultWithdrawItem", function(player, index)
		if not Validation.IsQuantity(index, 1, 1000) then
			return false, "BadRequest"
		end
		return operate(player, "VaultWithdraw", function(profile)
			return VaultRules.WithdrawItem(profile, index)
		end)
	end)
	Remotes.Handle("VaultWithdrawMaterial", function(player, catalogId, quantity)
		if
			not ItemCatalog.IsMaterial(catalogId)
			or not Validation.IsQuantity(quantity, 1, GameConstants.MATERIAL_STACK_MAX)
		then
			return false, "BadRequest"
		end
		return operate(player, "VaultWithdrawMaterial", function(profile)
			return VaultRules.WithdrawMaterial(profile, catalogId, quantity)
		end)
	end)
end

return VaultService
