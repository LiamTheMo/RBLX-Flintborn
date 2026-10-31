-- The lobby Inventory window's Vault tab, built by the real VaultController
-- over mocked remotes (sample data). Pages:
--   1 the Vault tab with a material chosen: the amount stepper and TAKE
--   2 a full vault: "More Space" links to vault upgrades; an item chosen
--   3 an empty backpack and vault: empty slots, empty-section text and the hint
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
workspace:SetAttribute("FlintbornPlaceRole", "Lobby")
local folder = Instance.new("Folder")
folder.Name = "FlintbornRemotes"
folder.Parent = ReplicatedStorage
local view = {
	backpack = { { catalogId = "StoneAxe", name = "Stone Axe" } },
	items = {
		{ catalogId = "IronSword", name = "Iron Sword", qualityRoll = 0.03 },
		{ catalogId = "StonePickaxe", name = "Stone Pickaxe", permanent = true },
		{ catalogId = "HideChest", name = "Hide Chest" },
		{ catalogId = "WoodenBow", name = "Wooden Bow" },
	},
	materials = {
		{ catalogId = "Stone", name = "Stone", quantity = 84 },
		{ catalogId = "Wood", name = "Wood", quantity = 412 },
		{ catalogId = "Fiber", name = "Plant Fiber", quantity = 37 },
		{ catalogId = "IronBar", name = "Iron Bar", quantity = 12 },
		{ catalogId = "Hide", name = "Hide", quantity = 9 },
	},
	itemCapacity = 25,
	backpackCapacity = 50,
}
for _, name in { "VaultSnapshot", "VaultDeposit", "VaultWithdrawItem", "VaultWithdrawMaterial" } do
	local remote = Instance.new("RemoteFunction")
	remote.Name = name
	remote.Parent = folder
	remote.InvokeServer = function()
		if name == "VaultSnapshot" then
			return view
		end
		return true
	end
end
local receipt = Instance.new("RemoteEvent")
receipt.Name = "ExtractionReceipt"
receipt.Parent = folder

local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local VaultController = require(Client.Controllers.VaultController)
local InventoryWindow = require(Client.Hud.Screens.InventoryWindow)
local player = Players.LocalPlayer
VaultController.Start()
local window = VaultController.window
local function place()
	window.screen.holder.Position = UDim2.fromOffset(243 + 1187 / 2, 150 + InventoryWindow.SIZE[2] / 2)
	window.screen.scale.Scale = 1
end
local function dump()
	__dump(player.PlayerGui, 1672, 941, { background = "art/reference/ui/lobby/01_hud.png" })
end

-- 1: a material with the stepper.
VaultController.Open("Vault")
place()
window:SlotFor("mWood").control:Activate()
dump()

-- 2: a full vault.
for i = #view.items + 1, 25 do
	view.items[i] = { catalogId = if i % 2 == 0 then "StoneAxe" else "StoneSpear" }
end
VaultController.Open("Vault")
window:SlotFor("i1").control:Activate()
assert(window.toolbar.upgrade ~= nil, "a full vault links to upgrades")
dump()

-- 3: empty.
view.backpack, view.items, view.materials = {}, {}, {}
window.tabs.Backpack.control:Activate()
VaultController.Open("Backpack")
dump()
