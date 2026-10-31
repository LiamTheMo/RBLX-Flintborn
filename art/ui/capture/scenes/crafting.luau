-- Field crafting: the same recipe window as the Forge in crafting mode, built by
-- the real CraftingController over a sample run backpack (the real recipes, with
-- carried counts), a furnace in reach and a smelt running.
--   1 Smelting: Copper Bar chosen, QUANTITY with All, the running job and Stop
--   2 Tools: an Iron recipe away from a Workbench (NEED WORKBENCH, disabled)

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
local screen = window.screen
screen.holder.Position = UDim2.fromOffset(285 + 1102 / 2, 132 + 682 / 2)
screen.scale.Scale = 1

local function check(cond, msg)
	print((cond and "  ok " or "  FAIL ") .. msg)
	if not cond then
		__failed = true
	end
end

window:SetCategory("Bars")
window:Select("CopperBar")
check(window.stepper.root.Visible and window.stepper.all ~= nil, "smelting takes a QUANTITY with All")
check(window.stepper.max == 7, "up to what the ore allows")
check(window.button.text == "Smelt", "the button says SMELT")
check(window.stop.root:GetAttribute("KitState") == "normal", "Stop is live while a smelt runs")
check(window.stationsText.root.Text == "Furnace", "the furnace in reach is listed")
check(window.materialRows.CopperOre.root:GetAttribute("KitState") == "selected", "the ore is highlighted")
__dump(player.PlayerGui, 1672, 941, { background = "art/reference/ui/lobby/01_hud.png" })

window:SetCategory("Tools")
window:Select("IronAxe")
check(not window.stepper.root.Visible, "one per request: no QUANTITY")
check(window.button.text == "Need Workbench", "away from a workbench the button says so")
check(window.button.root:GetAttribute("KitState") == "disabled", "and cannot be pressed")
__dump(player.PlayerGui, 1672, 941, { background = "art/reference/ui/lobby/01_hud.png" })

print(__failed and "CRAFTING SCENE FAILED" or "CRAFTING SCENE OK")
if __failed then
	error("crafting scene failed")
end
