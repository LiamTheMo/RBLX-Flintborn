-- Drives WalletController headlessly: the Market window's tabs, a purchase, a
-- vault sale, the perk respec question and a code.
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
workspace:SetAttribute("FlintbornPlaceRole", "Lobby")
local folder = Instance.new("Folder")
folder.Name = "FlintbornRemotes"
folder.Parent = ReplicatedStorage
local player = Players.LocalPlayer
player:SetAttribute("Coins", 240)
player:SetAttribute("Gems", 60)
local calls = {}
local view = {
	stock = {
		{ id = "StoneAxeKit", catalogId = "StoneAxe", name = "Stone Axe", price = 40, category = "Tools" },
		{ id = "TorchBundle", catalogId = "Torch", name = "Torch", quantity = 5, price = 25, category = "Tools" },
		{
			id = "BerryPack",
			catalogId = "Berries",
			name = "Berries",
			quantity = 10,
			price = 30,
			category = "Food",
			note = "Restores a little food; spoils in the field.",
		},
		{ id = "IronPick", catalogId = "IronPickaxe", name = "Iron Pickaxe", price = 600, category = "Tools" },
		{ id = "TitleScout", name = "Title: Scout", price = 150, category = "Titles", owned = true },
	},
	sellable = {
		{ source = "backpack", key = 2, catalogId = "Flint", name = "Flint", quantity = 6, coins = 12 },
		{ source = "vault", key = "IronBar", catalogId = "IronBar", name = "Iron Bar", quantity = 34, each = 6 },
		{
			source = "vault",
			key = "AncientShard",
			catalogId = "AncientShard",
			name = "Ancient Shard",
			quantity = 3,
			each = 40,
			warning = "Forge reagent: keep some for Permanent items.",
		},
	},
	offers = {
		{ id = "Gems100", name = "100 Gems", productId = 1234, earnable = "Daily quests pay Gems every week." },
		{ id = "XpBoost", name = "XP booster (1 hour)", productId = 0, earnable = "Quest chains award boosters." },
	},
	vaultTier = 1,
	vaultPrice = 25,
	maxVaultTier = 4,
	respecGems = 50,
}
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
check(gui and gui.Enabled, "the market opens on Shop")
local window = gui.Window
local list = window.List
check(list:FindFirstChild("StoneAxeKit") ~= nil, "stock is listed")
check(list.TitleScout:FindFirstChild("Done") ~= nil, "an owned title shows a tick")
check(not list.IronPick.Buy.Press.Selectable, "too dear to buy: BUY is off")
list.StoneAxeKit.Buy.Press.Activated:Fire()
check(calls[1] and calls[1][1] == "ShopBuy" and calls[1][2] == "StoneAxeKit", "BUY sends the stock id")
window.Sell.Press.Activated:Fire()
check(list:FindFirstChild("vaultIronBar") ~= nil, "Sell lists vault materials")
list.vaultIronBar.Step.Press.Activated:Fire()
local sale = calls[#calls]
check(sale[1] == "MerchantSell" and sale[2] == "vault" and sale[4] == 10, "SELL 10 sells ten")
check(list.vaultAncientShard:FindFirstChild("All") == nil, "a Forge reagent never offers SELL ALL")
window.Offers.Press.Activated:Fire()
list.Respec.Respec.Press.Activated:Fire()
check(window.Confirm.Visible, "a respec asks first")
window.Confirm.Yes.Press.Activated:Fire()
check(calls[#calls][1] == "PerkRespec", "confirming respecs")
window.Codes.Press.Activated:Fire()
local box = list:FindFirstChildWhichIsA("Frame"):FindFirstChild("Box", true) or list:FindFirstChild("Box", true)
box.Text = "WELCOME"
box.FocusLost:Fire(true)
check(calls[#calls][1] == "RedeemCode" and calls[#calls][2] == "WELCOME", "a code is redeemed")
print(__failed and "FLOW FAILED" or "FLOW OK")
gui.Window.UIScale.Scale = 1.3
gui.Window.Position = UDim2.fromOffset(836, 470)
for _, name in { "Shop", "Sell", "Offers" } do
	window[name].Press.Activated:Fire()
	__dump(gui, 1672, 941)
end
if __failed then
	error("market flow failed")
end
