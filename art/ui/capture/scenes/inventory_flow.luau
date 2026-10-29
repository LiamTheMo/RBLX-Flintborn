-- Drives the run InventoryController headlessly: open the backpack window, move
-- an item to the hotbar, wear armour, take it off and drop.
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
workspace:SetAttribute("FlintbornPlaceRole", "World")
local folder = Instance.new("Folder")
folder.Name = "FlintbornRemotes"
folder.Parent = ReplicatedStorage
local calls = {}
for _, name in
	{
		"EquipSlot",
		"MoveItem",
		"EquipArmor",
		"UnequipArmor",
		"DropItem",
		"UseConsumable",
		"PlaceCharge",
		"PlaceRune",
		"PlaceItem",
	}
do
	local remote = Instance.new("RemoteFunction")
	remote.Name = name
	remote.Parent = folder
	remote.InvokeServer = function(_, ...)
		table.insert(calls, { name, ... })
		return true
	end
end
for _, name in { "InventoryChanged", "Notify" } do
	local remote = Instance.new("RemoteEvent")
	remote.Name = name
	remote.Parent = folder
end
local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local InventoryController = require(Client.Controllers.InventoryController)
local player = Players.LocalPlayer
InventoryController.Start()
folder.InventoryChanged.OnClientEvent:Fire({
	slots = {
		{ area = "hotbar", index = 1, catalogId = "StoneAxe" },
		{ area = "backpack", index = 1, catalogId = "Wood", quantity = 40 },
		{ area = "backpack", index = 2, catalogId = "HideChest" },
		{ area = "armor", index = 1, catalogId = "HideHead" },
	},
	equipped = 1,
})
InventoryController.ToggleBackpack()
local gui = player.PlayerGui:FindFirstChild("FlintbornInventory")
local function check(cond, msg)
	print((cond and "  ok " or "  FAIL ") .. msg)
	if not cond then
		__failed = true
	end
end
check(gui and gui.Enabled, "backpack window opens")
local window = gui.Window
local function slot(pane, id)
	for _, d in window[pane]:GetDescendants() do
		if d.Name == id and d:FindFirstChild("Press") then
			return d
		end
	end
end
check(slot("Left", "backpack:50") ~= nil, "all fifty backpack slots shown")
-- Wood → first free hotbar slot (2).
slot("Left", "backpack:1").Press.Activated:Fire()
window.MoveRight.Press.Activated:Fire()
local last = calls[#calls]
check(last[1] == "MoveItem" and last[4] == "hotbar" and last[5] == 2, "→ moves to the first free hotbar slot")
-- Tap-to-move: backpack 1 onto backpack 7.
slot("Left", "backpack:1").Press.Activated:Fire()
slot("Left", "backpack:7").Press.Activated:Fire()
last = calls[#calls]
check(last[1] == "MoveItem" and last[5] == 7, "a second press moves the item there")
-- WEAR the chest piece.
slot("Left", "backpack:2").Press.Activated:Fire()
window.Action2.Press.Activated:Fire()
last = calls[#calls]
check(last[1] == "EquipArmor" and last[2] == "backpack" and last[3] == 2, "WEAR puts armour on")
-- TAKE OFF the helmet.
slot("Right", "armor:1").Press.Activated:Fire()
window.Action2.Press.Activated:Fire()
last = calls[#calls]
check(last[1] == "UnequipArmor" and last[2] == "Head", "TAKE OFF removes it")
-- DROP the chosen backpack item.
slot("Left", "backpack:1").Press.Activated:Fire()
window.Square.Press.Activated:Fire()
last = calls[#calls]
check(last[1] == "DropItem" and last[2] == "backpack" and last[3] == 1, "DROP drops the chosen slot")
window.Close.Activated:Fire()
check(not gui.Enabled, "close hides the window")
print(__failed and "FLOW FAILED" or "FLOW OK")
InventoryController.ToggleBackpack()
__dump(gui, 1672, 941)
if __failed then
	error("inventory flow failed")
end
