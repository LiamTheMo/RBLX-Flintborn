-- Drives WalletController headlessly in the kit Market window (Hud/ListWindow,
-- docs/ui/ListWindows.md): the tabs, a purchase through its confirm dialog, a
-- vault sale, the perk respec question and a code. Stock and offers are the real
-- ShopCatalog / OfferCatalog entries; sale quotes come from EconomyRules.
--
--   python3 art/ui/capture/capture.py market_flow
--
-- Pages: 1 Shop, 2 Sell, 3 Offers, 4 Codes, 5 the Buy dialog, 6 forced states
-- (hover, pressed, disabled buttons; a hovered tab), 7 phone 844 × 390.

for key, widths in table.clone(__textWidths or {}) do
	__textWidths["Enum." .. key] = __textWidths["Enum." .. key] or widths
end

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

check(gui and gui.Enabled, "the market opens on Shop")
check(find(gui, "StoneAxe") ~= nil, "stock is listed")
check(find(find(gui, "TitleWanderer"), "Done") ~= nil, "an owned title shows a tick")
check(find(find(gui, "TitleEmberborn"), "Buy"):GetAttribute("KitState") == "disabled", "too dear to buy: Buy is off")
check(find(gui, "Coins") and find(gui, "Coins"):GetAttribute("KitValue") == 2450, "the header shows the wallet")
press(find(find(gui, "StoneAxe"), "Buy"))
check(dialog() ~= nil and #calls == 0, "Buy asks first")
press(find(dialog(), "Confirm"))
check(calls[1] and calls[1][1] == "ShopBuy" and calls[1][2] == "StoneAxe", "confirming buys the stock id")
press(find(gui, "Sell"))
check(find(gui, "vaultIronBar") ~= nil, "Sell lists vault materials")
press(find(find(gui, "vaultIronBar"), "Step"))
local sale = calls[#calls]
check(sale[1] == "MerchantSell" and sale[2] == "vault" and sale[4] == 10, "Sell 10 sells ten")
press(find(gui, "Offers"))
press(find(find(gui, "Respec"), "Respec"))
check(dialog() ~= nil, "a respec asks first")
press(find(dialog(), "Confirm"))
check(calls[#calls][1] == "PerkRespec", "confirming respecs")
press(find(gui, "Codes"))
local box = find(gui, "Box") :: TextBox
box.Text = "WELCOME"
box.FocusLost:Fire(true)
check(calls[#calls][1] == "RedeemCode" and calls[#calls][2] == "WELCOME", "a code is redeemed with Enter")
box.Text = "FLINT"
press(find(gui, "Submit"))
check(calls[#calls][2] == "FLINT", "Redeem submits the typed code")
check(Kit.Modal.Top() ~= nil, "the window is on the modal stack")
Kit.Modal.Back()
check(not gui:GetAttribute("KitState") or gui:GetAttribute("KitState") == "closed", "Escape / B closes it")
print(__failed and "FLOW FAILED" or "FLOW OK")

local W, H = 1672, 941
local BG = { background = "art/reference/ui/lobby/01_hud.png" }
local function place(width: number, height: number, top: number)
	local k, centre = Kit.Scale.WindowFit(width, height, top, ListWindow.SIZE[1], ListWindow.SIZE[2], 1)
	gui.Holder.Fit.Scale = k
	gui.Holder.Position = UDim2.fromOffset(centre.X, centre.Y)
	return k
end
WalletController.Open("Shop")
place(W, H, 58)
gui.Holder.Fit.Scale = 1
gui.Holder.Position = UDim2.fromOffset(W / 2, H / 2 + 20)
for _, name in { "Shop", "Sell", "Offers", "Codes" } do
	press(find(gui, name))
	__dump(player.PlayerGui, W, H, BG)
end
press(find(gui, "Shop"))
press(find(find(gui, "WoodenAxe"), "Buy"))
local d = dialog()
d.Holder.Fit.Scale = 1
d.Holder.Position = UDim2.fromOffset(W / 2, H / 2 + 20)
__dump(player.PlayerGui, W, H, BG)
press(find(d, "Cancel"))
-- Forced states, as verifiers set them.
find(find(gui, "Bandage"), "Buy"):SetAttribute("DebugState", "hover")
find(find(gui, "RedberryPack"), "Buy"):SetAttribute("DebugState", "pressed")
find(find(gui, "SweetberryPack"), "Buy"):SetAttribute("DebugState", "busy")
find(gui, "Offers"):SetAttribute("DebugState", "hover")
__dump(player.PlayerGui, W, H, BG)
for _, part in player.PlayerGui:GetDescendants() do
	if part:GetAttribute("DebugState") then
		part:SetAttribute("DebugState", "")
	end
end
-- A phone held sideways: touch only, the window fills the height.
workspace.CurrentCamera.ViewportSize = Vector2.new(844, 390)
UserInputService.TouchEnabled = true
UserInputService.KeyboardEnabled = false
UserInputService.MouseEnabled = false
local k = place(844, 390, 58)
print(("market phone: window scale %.3f"):format(k))
__dump(player.PlayerGui, 844, 390)
if __failed then
	error("market flow failed")
end
