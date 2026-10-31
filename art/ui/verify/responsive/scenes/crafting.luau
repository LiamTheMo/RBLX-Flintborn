-- QA: field Crafting through the real CraftingController (setup copied from
-- art/ui/capture/scenes/crafting.luau), fitted by window:Watch, opened by
-- CraftingController.Toggle() (window:Open() -> RecipeWindow:Open uses GamepadEnabled).
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local CollectionService = game:GetService("CollectionService")
workspace:SetAttribute("FlintbornPlaceRole", "World")

local folder = Instance.new("Folder")
folder.Name = "FlintbornRemotes"
folder.Parent = ReplicatedStorage
local craft = Instance.new("RemoteFunction")
craft.Name = "Craft"
craft.Parent = folder
craft.InvokeServer = function()
	return true
end
for _, name in { "InventoryChanged", "Notify" } do
	local remote = Instance.new("RemoteEvent")
	remote.Name = name
	remote.Parent = folder
end

local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local InventoryController = require(Client.Controllers.InventoryController)
local CraftingController = require(Client.Controllers.CraftingController)
local player = Players.LocalPlayer

-- A furnace beside the player.
local character = Instance.new("Model")
local rootPart = Instance.new("Part")
rootPart.Name = "HumanoidRootPart"
rootPart.Position = Vector3.new(0, 0, 0)
rootPart.Parent = character
player.Character = character
local furnace = Instance.new("Part")
furnace.Position = Vector3.new(4, 0, 0)
CollectionService:AddTag(furnace, "Furnace")

player:SetAttribute("SessionState", "ActiveRun")
InventoryController.Start()
CraftingController.Start()
folder.InventoryChanged.OnClientEvent:Fire({
	slots = {
		{ area = "backpack", index = 1, catalogId = "Wood", quantity = 24 },
		{ area = "backpack", index = 2, catalogId = "Stone", quantity = 18 },
		{ area = "backpack", index = 3, catalogId = "Fiber", quantity = 11 },
		{ area = "backpack", index = 4, catalogId = "CopperOre", quantity = 7 },
		{ area = "backpack", index = 5, catalogId = "IronBar", quantity = 5 },
		{ area = "backpack", index = 6, catalogId = "Hide", quantity = 3 },
	},
})
player:SetAttribute("SmeltRecipe", "CopperBar")
player:SetAttribute("SmeltCount", 5)
player:SetAttribute("SmeltDone", 2)
player:SetAttribute("SmeltSeconds", 2)
player:SetAttribute("SmeltEndsAt", workspace:GetServerTimeNow() + 1)

CraftingController.Toggle()
local window = CraftingController.window
window:SetCategory("Bars")
window:Select("CopperBar")
QA.report(player.PlayerGui, { scale = window.screen.scale.Scale })
__dump(player.PlayerGui, QA.W, QA.H)
print("QA back:", QA.back(), "open after B:", window.screen:IsOpen())
