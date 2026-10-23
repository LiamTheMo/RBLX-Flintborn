-- NPC shops, merchants, vault upgrades, respecs and codes (GDD §10, Q89, Q95–96,
-- Q116–122). Lobby only. Every request is a once-only operation keyed by the
-- client's nonce; prices and sell values come from the server catalog.

local HttpService = game:GetService("HttpService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local EconomyRules = require(ReplicatedStorage.Shared.Economy.EconomyRules)
local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local OfferCatalog = require(ReplicatedStorage.Shared.Economy.OfferCatalog)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local ShopCatalog = require(ReplicatedStorage.Shared.Economy.ShopCatalog)
local Codes = require(script.Parent.Parent.Config.Codes)
local CurrencyService = require(script.Parent.CurrencyService)
local ProfileService = require(script.Parent.ProfileService)
local ProgressionService = require(script.Parent.ProgressionService)

local ShopService = {}

local function nameOf(catalogId: string): string
	local def = ItemCatalog.Get(catalogId)
	return def and def.name or catalogId
end

-- Shop stock, merchant quotes for everything sellable, vault and offer info.
local function view(player: Player)
	local profile = ProfileService.GetProfile(player)
	if profile == nil then
		return nil
	end
	local stock = {}
	for _, entry in ShopCatalog.Stock do
		table.insert(stock, {
			id = entry.id,
			name = entry.title and ("Title: " .. entry.title) or nameOf(entry.catalogId),
			quantity = entry.quantity,
			price = entry.price,
			category = entry.category,
			owned = entry.title ~= nil and profile.progression.titles[entry.title] == true,
		})
	end
	local sellable = {}
	for index, item in profile.lobbyBackpack.slots do
		local coins, warning = EconomyRules.Quote(item, nil)
		if coins then
			table.insert(sellable, {
				source = "backpack",
				key = index,
				name = nameOf(item.catalogId),
				quantity = item.quantity,
				coins = coins,
				warning = warning,
			})
		end
	end
	for catalogId, quantity in profile.vault.materials do
		local each, warning = EconomyRules.Quote({ catalogId = catalogId, quantity = 1 }, 1)
		if each then
			table.insert(sellable, {
				source = "vault",
				key = catalogId,
				name = nameOf(catalogId) .. " (vault)",
				quantity = quantity,
				each = each,
				warning = warning,
			})
		end
	end
	local offers = {}
	for _, offer in OfferCatalog.Offers do
		table.insert(
			offers,
			{ id = offer.id, name = offer.name, productId = offer.productId, earnable = offer.earnable }
		)
	end
	return {
		stock = stock,
		sellable = sellable,
		offers = offers,
		vaultTier = profile.vault.upgradeTier or 0,
		vaultPrice = EconomyRules.VaultUpgradePrice(profile.vault.upgradeTier or 0),
		maxVaultTier = EconomyRules.MAX_VAULT_TIER,
		respecGems = EconomyRules.RESPEC_GEMS,
	}
end

function ShopService.Start()
	if not PlaceConfig.IsLobby() then
		return
	end
	Remotes.Get("ShopView").OnServerInvoke = view
	Remotes.Get("ShopBuy").OnServerInvoke = function(player, stockId, nonce)
		return CurrencyService.Run(player, "buy:", nonce, "ShopBuy", function(profile)
			return EconomyRules.Buy(profile, stockId, function()
				return HttpService:GenerateGUID(false)
			end, player.UserId)
		end)
	end
	Remotes.Get("MerchantSell").OnServerInvoke = function(player, source, key, quantity, nonce)
		if source ~= "backpack" and source ~= "vault" then
			return false, "BadRequest"
		end
		if source == "backpack" and type(key) ~= "number" then
			return false, "BadRequest"
		end
		if source == "vault" and ItemCatalog.Get(key) == nil then
			return false, "BadRequest"
		end
		return CurrencyService.Run(player, "sell:", nonce, "MerchantSale", function(profile)
			if profile.transit ~= nil then
				return false, "InTransit"
			end
			return EconomyRules.Sell(profile, source, key, quantity, "sale:" .. nonce, os.time())
		end)
	end
	Remotes.Get("VaultUpgrade").OnServerInvoke = function(player, nonce)
		return CurrencyService.Run(player, "vault:", nonce, "VaultUpgrade", EconomyRules.BuyVaultTier)
	end
	Remotes.Get("PerkRespec").OnServerInvoke = function(player, nonce)
		local ok, result = CurrencyService.Run(player, "respec:", nonce, "PerkRespec", function(profile)
			local spent, reason = EconomyRules.Spend(profile, 0, EconomyRules.RESPEC_GEMS)
			if not spent then
				return false, reason
			end
			return EconomyRules.Respec(profile)
		end)
		ProgressionService.Publish(player)
		return ok, result
	end
	Remotes.Get("RedeemCode").OnServerInvoke = function(player, code)
		if type(code) ~= "string" or #code > 40 then
			return false, "BadRequest"
		end
		code = string.upper(code)
		local grant = Codes[code]
		if grant == nil then
			return false, "UnknownCode"
		end
		-- One redemption per player: the code itself is the operation key.
		local ok, result = CurrencyService.Run(
			player,
			"code:",
			(code:gsub("[^%w%-_]", "")),
			"CodeRedeem",
			function(profile)
				return EconomyRules.Fulfil(profile, { grant = grant }, os.time())
			end
		)
		ProgressionService.Publish(player)
		return ok, result
	end
end

return ShopService
