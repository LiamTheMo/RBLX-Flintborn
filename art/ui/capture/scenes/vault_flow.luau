-- Drives the lobby VaultController headlessly: store, an overflow that asks
-- first, take a material in the picked amount, take an item, STORE ALL.
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
workspace:SetAttribute("FlintbornPlaceRole", "Lobby")
local folder = Instance.new("Folder")
folder.Name = "FlintbornRemotes"
folder.Parent = ReplicatedStorage
local calls = {}
local view = {
	backpack = {
		{ catalogId = "StoneAxe", name = "Stone Axe", rarity = "Common" },
		{ catalogId = "Wood", name = "Wood", quantity = 900, rarity = "Common" },
		{ catalogId = "Fiber", name = "Plant Fiber", quantity = 10, rarity = "Common" },
	},
	items = { { catalogId = "IronSword", name = "Iron Sword", rarity = "Uncommon" } },
	materials = { { catalogId = "Stone", name = "Stone", quantity = 84 } },
	itemCapacity = 25,
	backpackCapacity = 50,
}
local handlers = {
	VaultSnapshot = function()
		return view
	end,
	VaultDeposit = function(index, confirmId, loss)
		table.insert(calls, { "VaultDeposit", index, confirmId, loss })
		local item = view.backpack[index]
		if item and item.catalogId == "Wood" and confirmId == nil then
			return false, "VaultWouldOverflow", 40
		end
		table.remove(view.backpack, index)
		return true
	end,
	VaultWithdrawItem = function(index)
		table.insert(calls, { "VaultWithdrawItem", index })
		return true
	end,
	VaultWithdrawMaterial = function(id, amount)
		table.insert(calls, { "VaultWithdrawMaterial", id, amount })
		return true
	end,
}
for name, fn in handlers do
	local remote = Instance.new("RemoteFunction")
	remote.Name = name
	remote.Parent = folder
	remote.InvokeServer = function(_, ...)
		return fn(...)
	end
end
local receipt = Instance.new("RemoteEvent")
receipt.Name = "ExtractionReceipt"
receipt.Parent = folder

local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local VaultController = require(Client.Controllers.VaultController)
local player = Players.LocalPlayer
VaultController.Start()
VaultController.Toggle()
local gui = player.PlayerGui:FindFirstChild("FlintbornInventory")
local function check(cond, msg)
	print((cond and "  ok " or "  FAIL ") .. msg)
	if not cond then
		__failed = true
	end
end
check(gui and gui.Enabled, "window opens")
local window = gui.Window
local function slot(pane, id)
	for _, d in window[pane]:GetDescendants() do
		if d.Name == id and d:FindFirstChild("Press") then
			return d
		end
	end
end
check(slot("Left", "b1") ~= nil and slot("Right", "i1") ~= nil and slot("Right", "mStone") ~= nil, "both panes filled")
-- Store the axe with STORE.
slot("Left", "b1").Press.Activated:Fire()
window.Action2.Press.Activated:Fire()
check(calls[1] and calls[1][1] == "VaultDeposit" and calls[1][2] == 1, "STORE deposits the chosen slot")
-- Wood overflows: asks first, then deposits with the confirmation.
slot("Left", "b1").Press.Activated:Fire()
window.MoveRight.Press.Activated:Fire()
check(window.Confirm.Visible, "an overflow asks first")
local before = #calls
window.Confirm.Yes.Press.Activated:Fire()
local last = calls[#calls]
check(#calls == before + 1 and last[3] == "Wood" and last[4] == 40, "deposit anyway names the stack and loss")
-- Take 100 stone (×100 picked).
slot("Right", "mStone").Press.Activated:Fire()
window.Amount3.Press.Activated:Fire()
window.Action1.Press.Activated:Fire()
last = calls[#calls]
check(last[1] == "VaultWithdrawMaterial" and last[2] == "Stone" and last[3] == 84, "takes at most the stack")
slot("Right", "i1").Press.Activated:Fire()
window.MoveLeft.Press.Activated:Fire()
last = calls[#calls]
check(last[1] == "VaultWithdrawItem" and last[2] == 1, "← takes the chosen vault item")
window.Square.Press.Activated:Fire()
last = calls[#calls]
check(last[1] == "VaultDeposit" and #view.backpack == 0, "STORE ALL empties the backpack")
window.Close.Activated:Fire()
check(not gui.Enabled, "close hides the window")
print(__failed and "FLOW FAILED" or "FLOW OK")
__dump(gui, 1672, 941)
if __failed then
	error("vault flow failed")
end
