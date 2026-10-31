-- QA: the lobby Inventory window (Vault tab) through the real VaultController
-- (mocked remotes), fitted by its own screen:Watch. Opened as the HUD tile does
-- (VaultController.Open("Backpack")), with gamepad selection on the tile first
-- for the console profile. Page 1 sample data with an item chosen; page 2 long
-- item names on the Vault tab; then B is pressed and the result reported.
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local GuiService = game:GetService("GuiService")
workspace:SetAttribute("FlintbornPlaceRole", "Lobby")
local folder = Instance.new("Folder")
folder.Name = "FlintbornRemotes"
folder.Parent = ReplicatedStorage
local view = {
	backpack = { { catalogId = "StoneAxe", name = "Stone Axe" }, { catalogId = "Redberry", name = "Redberry", quantity = 5 } },
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
local player = Players.LocalPlayer
VaultController.Start()
local window = VaultController.window
if QA.gamepad then
	-- the HUD tile the player pressed A on
	local tile = Instance.new("TextButton")
	tile.Name = "HudTile"
	tile.Parent = player.PlayerGui
	GuiService.SelectedObject = tile
end
VaultController.Open("Backpack")
QA.report(player.PlayerGui, { scale = window.screen.scale.Scale, opened = "Backpack" })
__dump(player.PlayerGui, QA.W, QA.H)

-- 2: long names on the Vault tab, an item chosen.
view.items[1] = { catalogId = "IronSword", name = "Permanent Portable Extraction Rune", qualityRoll = 0.99 }
view.items[2] = { catalogId = "StonePickaxe", name = "Masterwork Obsidian Pickaxe of the Deep", permanent = true }
view.materials[1] = { catalogId = "Stone", name = "Ancient Petrified Heartwood", quantity = 99999 }
VaultController.Open("Vault")
pcall(function()
	window:SlotFor("i1").control:Activate()
end)
QA.report(player.PlayerGui, { scale = window.screen.scale.Scale })
__dump(player.PlayerGui, QA.W, QA.H)
print("QA back:", QA.back(), "open after B:", window.screen:IsOpen(), "selected after:", GuiService.SelectedObject and GuiService.SelectedObject.Name)
