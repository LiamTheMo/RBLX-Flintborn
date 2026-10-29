-- Drives CraftingController headlessly: open, craft an instant recipe, smelt a
-- batch with the stepper and Craft all, stop the smelt.
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
workspace:SetAttribute("FlintbornPlaceRole", "World")
local folder = Instance.new("Folder")
folder.Name = "FlintbornRemotes"
folder.Parent = ReplicatedStorage
local calls = {}
local craft = Instance.new("RemoteFunction")
craft.Name = "Craft"
craft.Parent = folder
craft.InvokeServer = function(_, _guid, recipeId, count)
	table.insert(calls, { recipeId, count })
	return true
end
for _, name in { "InventoryChanged", "Notify" } do
	local remote = Instance.new("RemoteEvent")
	remote.Name = name
	remote.Parent = folder
end
local Shared = ReplicatedStorage.Shared
local CraftingRules = require(Shared.Crafting.CraftingRules)
local Recipes = require(Shared.Crafting.Recipes)
local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local InventoryController = require(Client.Controllers.InventoryController)
local CraftingController = require(Client.Controllers.CraftingController)
local player = Players.LocalPlayer
InventoryController.Start()
CraftingController.Start()
folder.InventoryChanged.OnClientEvent:Fire({
	slots = {
		{ area = "backpack", index = 1, catalogId = "Wood", quantity = 20 },
		{ area = "backpack", index = 2, catalogId = "Stone", quantity = 20 },
		{ area = "backpack", index = 3, catalogId = "Fiber", quantity = 20 },
		{ area = "backpack", index = 4, catalogId = "CopperOre", quantity = 7 },
	},
})
CraftingController.Toggle()
local gui = player.PlayerGui:FindFirstChild("FlintbornCrafting")
-- Pinned to the sheet's own scale and place, as the crafting scene is.
if gui then
	gui.Window.UIScale.Scale = 1
	gui.Window.Position = UDim2.fromOffset(23 + 814.5, 58 + 371)
end
local function check(cond, msg)
	print((cond and "  ok " or "  FAIL ") .. msg)
	if not cond then
		__failed = true
	end
end
check(gui and gui.Enabled, "crafting opens")
local window = gui.Window
local axe, bar = nil, nil
for _, recipe in Recipes.List do
	if recipe.output == "StoneAxe" then
		axe = recipe
	end
	if recipe.output == "CopperBar" then
		bar = recipe
	end
end
window.Recipes[axe.id].Press.Activated:Fire()
window.Craft.Press.Activated:Fire()
check(#calls == 1 and calls[1][1] == axe.id and calls[1][2] == nil, "an instant recipe crafts one, no count")
-- Smelting needs a furnace: CRAFT stays off without one.
window.Bars.Press.Activated:Fire()
window.Recipes[bar.id].Press.Activated:Fire()
window.Craft.Press.Activated:Fire()
check(#calls == 1, "no furnace in reach: nothing sent")
-- A furnace nearby (stub the tag lookup by placing one).
local character = Instance.new("Model")
local rootPart = Instance.new("Part")
rootPart.Name = "HumanoidRootPart"
rootPart.Position = Vector3.new(0, 0, 0)
rootPart.Parent = character
player.Character = character
local furnace = Instance.new("Part")
furnace.Position = Vector3.new(3, 0, 0)
game:GetService("CollectionService"):AddTag(furnace, "Furnace")
CraftingController.Toggle()
CraftingController.Toggle()
window.Recipes[bar.id].Press.Activated:Fire()
window.Plus.Press.Activated:Fire()
window.Plus.Press.Activated:Fire()
window.Craft.Press.Activated:Fire()
local last = calls[#calls]
check(last and last[1] == bar.id and last[2] == 3, "the stepper sets the batch")
window.CraftAll.Press.Activated:Fire()
last = calls[#calls]
local per = bar.inputs.CopperOre or 1
check(last[2] == math.min(CraftingRules.MAX_BATCH, 7 // per), "Craft all smelts as many as the ore allows")
player:SetAttribute("SmeltRecipe", bar.id)
player:SetAttribute("SmeltCount", 3)
player:SetAttribute("SmeltDone", 1)
check(window.Job.Visible, "the running smelt shows")
window.Job.Stop.Activated:Fire()
last = calls[#calls]
check(last[1] == bar.id and last[2] == 0, "✕ stops the smelt")
print(__failed and "FLOW FAILED" or "FLOW OK")
__dump(gui, 1672, 941)
if __failed then
	error("crafting flow failed")
end
