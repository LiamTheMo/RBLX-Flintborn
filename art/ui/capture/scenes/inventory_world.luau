-- Drives the run InventoryController and its Inventory window headlessly
-- through real presses: open, choose, EQUIP to the hotbar, MOVE onto another
-- slot, WEAR armour, the Equipped tab (hotbar keys, armour), TAKE OFF, USE,
-- DROP, search and close. Remotes are mocked; the server's snapshots are pushed
-- through InventoryChanged as in game. The page is the Equipped tab.
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
local function check(cond, msg)
	print((cond and "  ok " or "  FAIL ") .. msg)
	if not cond then
		__failed = true
	end
end
InventoryController.Start()
folder.InventoryChanged.OnClientEvent:Fire({
	slots = {
		{ area = "hotbar", index = 1, catalogId = "StoneAxe" },
		{ area = "hotbar", index = 2, catalogId = "Redberry", quantity = 6 },
		{ area = "backpack", index = 1, catalogId = "Wood", quantity = 40 },
		{ area = "backpack", index = 2, catalogId = "HideChest" },
		{ area = "backpack", index = 3, catalogId = "StoneSpear", qualityRoll = 0.02 },
		{ area = "armor", index = 1, catalogId = "HideHead" },
	},
	equipped = 1,
})
local toggled = {}
InventoryController.BackpackToggled:Connect(function(open)
	table.insert(toggled, open)
end)
InventoryController.ToggleBackpack()
local gui = player.PlayerGui:FindFirstChild("FlintbornInventory")
local window = InventoryController.window
check(gui and gui.Enabled and InventoryController.IsOpen(), "the Backpack key opens the window")
check(toggled[1] == true, "BackpackToggled reports it")
check(window:SlotFor("backpack:50") ~= nil, "all fifty backpack slots shown")
check(window.hint.root.Visible, "the card explains what to do before a choice")

local function press(component)
	component.control:Activate()
end

-- EQUIP wood → first free hotbar slot (3).
press(window:SlotFor("backpack:1"))
check(window.detailName.root.Text == "Wood", "a press shows the item in the card")
press(window:ActionButton("toHotbar"))
local last = calls[#calls]
check(last[1] == "MoveItem" and last[4] == "hotbar" and last[5] == 3, "EQUIP moves it to the first free hotbar slot")
check(not window.busy, "the buttons are live again after the reply")
-- MOVE the spear onto backpack slot 7.
press(window:SlotFor("backpack:3"))
press(window:ActionButton("move"))
check(window:ActionButton("cancelMove") ~= nil, "MOVE waits for a slot")
press(window:SlotFor("backpack:7"))
last = calls[#calls]
check(
	last[1] == "MoveItem" and last[2] == "backpack" and last[3] == 3 and last[5] == 7,
	"the next press moves it there"
)
-- WEAR the chest piece.
press(window:SlotFor("backpack:2"))
press(window:ActionButton("wear"))
last = calls[#calls]
check(last[1] == "EquipArmor" and last[2] == "backpack" and last[3] == 2, "WEAR puts armour on")
-- DROP the chosen backpack item.
press(window:SlotFor("backpack:1"))
press(window:ActionButton("drop"))
last = calls[#calls]
check(last[1] == "DropItem" and last[2] == "backpack" and last[3] == 1, "DROP drops the chosen slot")
-- Search narrows the grid.
window:SetQuery("spear")
check(window:SlotFor("backpack:3") ~= nil and window:SlotFor("backpack:1") == nil, "search filters the grid")
window:SetQuery("")

-- The Equipped tab: hotbar with keys, armour with captions.
window.tabs.Equipped.control.hit.Activated:Fire()
check(window.tabId == "Equipped", "the Equipped tab opens")
local axe = window:SlotFor("hotbar:1")
check(axe ~= nil and axe.hotkey ~= nil and axe.hotkey.root.Visible, "hotbar slots carry their keys")
check(window:SlotFor("armor:3") ~= nil, "three armour slots")
press(window:SlotFor("hotbar:1"))
check(window:ActionButton("activate").text == "Put Away", "the held tool offers PUT AWAY")
press(window:SlotFor("hotbar:2"))
press(window:ActionButton("activate"))
last = calls[#calls]
check(last[1] == "UseConsumable" and last[3] == "Redberry", "USE eats the berries")
press(window:SlotFor("armor:1"))
check(window:ActionButton("drop") == nil, "worn armour cannot be dropped")
press(window:ActionButton("takeOff"))
last = calls[#calls]
check(last[1] == "UnequipArmor" and last[2] == "Head", "TAKE OFF removes it")
press(window:SlotFor("hotbar:2"))
print(__failed and "FLOW FAILED" or "FLOW OK")
__dump(player.PlayerGui, 1672, 941, { background = "art/reference/ui/lobby/01_hud.png" })
window.window.close.control.hit.Activated:Fire()
check(not InventoryController.IsOpen() and toggled[#toggled] == false, "close hides the window")
print(__failed and "FLOW FAILED" or "FLOW OK")
if __failed then
	error("inventory world flow failed")
end
