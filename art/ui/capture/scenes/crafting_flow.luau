-- Drives CraftingController and the recipe window in crafting mode through real
-- events: an instant recipe crafts one and sends no count; smelting needs a
-- furnace (nothing is sent without one); with one in reach the stepper and All
-- set the batch; the running smelt shows and Stop sends a count of 0; the Craft
-- key's toggle opens and closes the window; a refusal's reason shows.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local CollectionService = game:GetService("CollectionService")
workspace:SetAttribute("FlintbornPlaceRole", "World")

local folder = Instance.new("Folder")
folder.Name = "FlintbornRemotes"
folder.Parent = ReplicatedStorage
local calls = {}
local reply = nil
local craft = Instance.new("RemoteFunction")
craft.Name = "Craft"
craft.Parent = folder
craft.InvokeServer = function(_, guid, recipeId, count)
	table.insert(calls, { recipeId, count, guid })
	local answer = reply or { true }
	reply = nil
	return table.unpack(answer)
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

player:SetAttribute("SessionState", "ActiveRun")
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

local function check(cond, msg)
	print((cond and "  ok " or "  FAIL ") .. msg)
	if not cond then
		__failed = true
	end
end

local function toasts(): string
	local gui = player.PlayerGui:FindFirstChild("KitToasts")
	local out = {}
	for _, d in (gui and gui:GetDescendants()) or {} do
		if d:IsA("TextLabel") then
			table.insert(out, d.Text)
		end
	end
	return table.concat(out, " | ")
end

CraftingController.Toggle()
local window = CraftingController.window
check(window:IsOpen(), "the Craft key opens field crafting")
check(string.find(window.window.title.root.Text, "RAFTING", 1, true) ~= nil, "titled for crafting")
check(window.materialRows.CopperOre ~= nil and window.materialRows.Wood ~= nil, "YOUR MATERIALS lists the carried materials")

local axe, bar = nil, nil
for _, recipe in Recipes.List do
	if recipe.output == "StoneAxe" then
		axe = recipe
	end
	if recipe.output == "CopperBar" then
		bar = recipe
	end
end

-- An instant recipe: one per request, no count.
window:SetCategory("Tools")
window.rows[axe.id].control.hit.Activated:Fire()
check(not window.stepper.root.Visible, "an instant recipe has no QUANTITY")
window.button.control:Activate()
check(#calls == 1 and calls[1][1] == axe.id and calls[1][2] == nil, "an instant recipe crafts one, no count")
check(string.find(toasts(), "Stone Axe", 1, true) ~= nil, "the receipt names it")

-- Smelting needs a furnace.
window:SetCategory("Bars")
window.rows[bar.id].control.hit.Activated:Fire()
check(window.button.text == "Need Furnace", "no furnace: the button says so")
window.button.control:Activate()
check(#calls == 1, "no furnace in reach: nothing sent")

-- A furnace nearby: walking up refreshes the window.
local character = Instance.new("Model")
local rootPart = Instance.new("Part")
rootPart.Name = "HumanoidRootPart"
rootPart.Position = Vector3.new(0, 0, 0)
rootPart.Parent = character
player.Character = character
local furnace = Instance.new("Part")
furnace.Position = Vector3.new(3, 0, 0)
CollectionService:AddTag(furnace, "Furnace")
CraftingController.Refresh()
check(window.button.text == "Smelt" and window.stationsText.root.Text == "Furnace", "a furnace in reach: SMELT")
window.stepper.plus.control:Activate()
window.stepper.plus.control:Activate()
window.button.control:Activate()
local last = calls[#calls]
check(last and last[1] == bar.id and last[2] == 3, "the stepper sets the batch")
window.stepper.all.control:Activate()
window.button.control:Activate()
last = calls[#calls]
local per = bar.inputs.CopperOre or 1
check(last[2] == math.min(CraftingRules.MAX_BATCH, 7 // per), "All smelts as many as the ore allows")

-- The running smelt and Stop.
player:SetAttribute("SmeltRecipe", bar.id)
player:SetAttribute("SmeltCount", 3)
player:SetAttribute("SmeltDone", 1)
check(string.find(window.jobText.root.Text, "1 / 3", 1, true) ~= nil, "the running smelt shows")
window.stop.control:Activate()
last = calls[#calls]
check(last[1] == bar.id and last[2] == 0, "Stop sends a count of 0")

-- A refusal says why.
reply = { false, "Busy" }
window.button.control:Activate()
check(string.find(toasts(), "already smelting", 1, true) ~= nil, "a refusal says why")

-- The toggle closes it; leaving the run closes it too.
CraftingController.Toggle()
check(not window:IsOpen(), "the Craft key closes it")
CraftingController.Toggle()
player:SetAttribute("SessionState", "Lobby")
check(not window:IsOpen(), "leaving the run closes it")
player:SetAttribute("SessionState", "ActiveRun")
CraftingController.Toggle()

print(__failed and "FLOW FAILED" or "FLOW OK")
window.screen.holder.Position = UDim2.fromOffset(285 + 1102 / 2, 132 + 682 / 2)
window.screen.scale.Scale = 1
__dump(player.PlayerGui, 1672, 941, { background = "art/reference/ui/lobby/01_hud.png" })
if __failed then
	error("crafting flow failed")
end
