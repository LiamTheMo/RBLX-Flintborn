-- Drives TradeController headlessly: inviting a player, then a running trade's
-- two offers, adding a backpack item and vault materials, gems and the lock.
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
workspace:SetAttribute("FlintbornPlaceRole", "Lobby")
local folder = Instance.new("Folder")
folder.Name = "FlintbornRemotes"
folder.Parent = ReplicatedStorage
local player = Players.LocalPlayer
local friend = Instance.new("Player")
friend.Name = "RiverFox"
friend.DisplayName = "River"
friend.UserId = 2
friend.Parent = Players
local calls = {}
local vault = {
	backpack = {
		{ key = "b1", catalogId = "Truffle", name = "Golden Truffle", quantity = 3, tradeable = true },
		{ key = "b2", catalogId = "IronSword", name = "★ Iron Sword", tradeable = true, permanent = true },
	},
	materials = {
		{ catalogId = "Amber", name = "Amber", quantity = 24 },
		{ catalogId = "IronBar", name = "Iron Bar", quantity = 40 },
	},
	items = {},
}
for name, fn in
	{
		VaultSnapshot = function()
			return vault
		end,
		TradeRequest = function(userId)
			table.insert(calls, { "TradeRequest", userId })
			return true
		end,
		TradeOffer = function(id, keys, gems, materials)
			table.insert(calls, { "TradeOffer", keys, gems, materials })
			return true
		end,
		TradeLock = function()
			table.insert(calls, { "TradeLock" })
			return true
		end,
		TradeConfirm = function()
			return true
		end,
		TradeCancel = function()
			return true
		end,
		TradeRespond = function()
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
local changed = Instance.new("RemoteEvent")
changed.Name = "TradeChanged"
changed.Parent = folder
local Shared = ReplicatedStorage.Shared
local TradeRules = require(Shared.Economy.TradeRules)
-- Every listed slot and material trades in this scene.
TradeRules.IsTradeableSlot = function(item)
	return item.tradeable == true
end
TradeRules.IsTradeableMaterial = function(catalogId)
	return catalogId == "Amber"
end
local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local TradeController = require(Client.Controllers.TradeController)
TradeController.Start()
TradeController.Toggle()
local gui = player.PlayerGui:FindFirstChild("FlintbornTrade")
local function check(cond, msg)
	print((cond and "  ok " or "  FAIL ") .. msg)
	if not cond then
		__failed = true
	end
end
check(gui and gui.Enabled, "the trade window opens")
local window = gui.Window
local list = window.List
list.Player2.Invite.Press.Activated:Fire()
check(calls[1] and calls[1][2] == 2, "INVITE asks that player")
changed.OnClientEvent:Fire({
	kind = "Session",
	id = "t1",
	partner = "River",
	mine = { items = { { key = "b1", name = "Golden Truffle", quantity = 3 } }, gems = 0 },
	theirs = { items = { { key = "m:Amber", name = "Amber", quantity = 10 } }, gems = 15 },
	locked = { mine = false, theirs = true },
	confirmed = { mine = false, theirs = false },
})
check(list:FindFirstChild("Pair") ~= nil, "both offers show")
check(list.Slotb1.Toggle:FindFirstChild("Text", true).Text == "REMOVE", "an offered item can be removed")
list.Slotb2.Toggle.Press.Activated:Fire()
local offer = calls[#calls]
check(offer[1] == "TradeOffer" and table.find(offer[2], "b2") ~= nil, "ADD puts the item in the offer")
list.MaterialAmber.Ten.Press.Activated:Fire()
offer = calls[#calls]
check(offer[4].Amber == 10, "+10 offers ten of a vault material")
check(list:FindFirstChild("MaterialIronBar") == nil, "untradeable materials are not offered")
local box = list:FindFirstChild("Box", true)
box.Text = "25"
box.FocusLost:Fire(false)
check(calls[#calls][3] == 25, "the gems box offers gems")
list:FindFirstChild("Lock", true).Press.Activated:Fire()
check(calls[#calls][1] == "TradeLock", "LOCK OFFER locks")
print(__failed and "FLOW FAILED" or "FLOW OK")
gui.Window.UIScale.Scale = 1.3
gui.Window.Position = UDim2.fromOffset(836, 470)
__dump(gui, 1672, 941)
if __failed then
	error("trade flow failed")
end
