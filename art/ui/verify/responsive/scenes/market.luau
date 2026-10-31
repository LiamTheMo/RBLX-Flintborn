-- QA: the Market (Hud/ListWindow, shared by Trade and Progress) through the real
-- WalletController (setup copied from art/ui/capture/scenes/market_flow.luau),
-- fitted by its own Watch. Pages: Shop, Sell, Codes, the Buy ConfirmDialog; then B.
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local UserInputService = game:GetService("UserInputService")
workspace:SetAttribute("FlintbornPlaceRole", "Lobby")
local folder = Instance.new("Folder")
folder.Name = "FlintbornRemotes"
folder.Parent = ReplicatedStorage
local player = Players.LocalPlayer
player:SetAttribute("Coins", 2450)
player:SetAttribute("Gems", 300)

local Shared = ReplicatedStorage.Shared
local ItemCatalog = require(Shared.Items.ItemCatalog)
local ShopCatalog = require(Shared.Economy.ShopCatalog)
local OfferCatalog = require(Shared.Economy.OfferCatalog)
local EconomyRules = require(Shared.Economy.EconomyRules)

local function nameOf(id: string): string
	local def = ItemCatalog.Get(id)
	return def and def.name or id
end

local stock = {}
for _, entry in ShopCatalog.Stock do
	table.insert(stock, {
		id = entry.id,
		catalogId = entry.catalogId,
		name = entry.title and ("Title: " .. entry.title) or nameOf(entry.catalogId),
		quantity = entry.quantity,
		price = entry.price,
		category = entry.category,
		note = entry.note,
		owned = entry.title == "Wanderer",
	})
end
local sellable = {}
for index, item in { { catalogId = "Flint", quantity = 6 }, { catalogId = "Redberry", quantity = 4 } } do
	local coins, warning = EconomyRules.Quote(item, nil)
	assert(coins, "a merchant buys " .. item.catalogId)
	table.insert(sellable, {
		source = "backpack",
		key = index,
		catalogId = item.catalogId,
		name = nameOf(item.catalogId),
		quantity = item.quantity,
		coins = coins,
		warning = warning,
	})
end
for _, entry in { { "IronBar", 34 }, { "Hide", 9 }, { "Wood", 32 } } do
	local each, warning = EconomyRules.Quote({ catalogId = entry[1], quantity = 1 }, 1)
	table.insert(sellable, {
		source = "vault",
		key = entry[1],
		catalogId = entry[1],
		name = nameOf(entry[1]),
		quantity = entry[2],
		each = each or 1,
		warning = warning,
	})
end
local offers = {}
for _, offer in OfferCatalog.Offers do
	table.insert(offers, { id = offer.id, name = offer.name, productId = offer.productId, earnable = offer.earnable })
end
-- One offer purchasable, so both button states show.
offers[4].productId = 1234
local view = {
	stock = stock,
	sellable = sellable,
	offers = offers,
	vaultTier = 1,
	vaultPrice = EconomyRules.VaultUpgradePrice(1),
	maxVaultTier = EconomyRules.MAX_VAULT_TIER,
	respecGems = EconomyRules.RESPEC_GEMS,
}

local calls = {}
for name, fn in
	{
		ShopView = function()
			return view
		end,
		ShopBuy = function(...)
			table.insert(calls, { "ShopBuy", ... })
			return true
		end,
		MerchantSell = function(...)
			table.insert(calls, { "MerchantSell", ... })
			return true
		end,
		VaultUpgrade = function()
			table.insert(calls, { "VaultUpgrade" })
			return true
		end,
		PerkRespec = function()
			table.insert(calls, { "PerkRespec" })
			return true
		end,
		RedeemCode = function(code)
			table.insert(calls, { "RedeemCode", code })
			return true
		end,
	}
do
	local remote = Instance.new("RemoteFunction")
	remote.Name = name
	remote.Parent = folder
	remote.InvokeServer = function(_, ...)
		return fn(...)
	end
end

local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local Kit = require(Client.Hud.Kit)
local ListWindow = require(Client.Hud.ListWindow)
local WalletController = require(Client.Controllers.WalletController)
WalletController.Start()
WalletController.Open("Shop")
local gui = player.PlayerGui:FindFirstChild("FlintbornMarket")
local function check(cond, msg)
	print((cond and "  ok " or "  FAIL ") .. msg)
	if not cond then
		__failed = true
	end
end
-- A named part anywhere under `root`, and a press on a kit control's hit.
local function find(root: Instance?, name: string): Instance?
	return root and root:FindFirstChild(name, true)
end
local function press(component: Instance?)
	local hit = component and component:FindFirstChild("Hit")
	assert(hit, "nothing to press")
	-- Past the kit's press debounce (time only passes for real here).
	local start = os.clock()
	while os.clock() - start < 0.16 do
	end
	hit.Activated:Fire()
end
local function dialog(): Instance?
	-- A closed dialog lingers until its close tween ends; the open one is enabled.
	for _, d in player.PlayerGui:GetChildren() do
		if d.Name == "KitDialog" and d.Enabled then
			return d
		end
	end
	return nil
end
for _, name in { "Shop", "Sell", "Codes" } do
	press(find(gui, name))
	QA.report(player.PlayerGui, { scale = gui.Holder.Fit.Scale, tab = name })
	__dump(player.PlayerGui, QA.W, QA.H)
end
press(find(gui, "Shop"))
press(find(find(gui, "WoodenAxe"), "Buy"))
local d = dialog()
QA.report(player.PlayerGui, { scale = d and d.Holder.Fit.Scale, dialog = d ~= nil })
__dump(player.PlayerGui, QA.W, QA.H)
print("QA back:", QA.back(), "dialog after B:", dialog() ~= nil, "market:", gui:GetAttribute("KitState"))
