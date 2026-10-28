-- Drives ForgeController headlessly: forge a special recipe, and see a Permanent
-- conversion ask first (its confirm button is armed only after a delay, which
-- never passes in a capture).
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
workspace:SetAttribute("FlintbornPlaceRole", "Lobby")
local folder = Instance.new("Folder")
folder.Name = "FlintbornRemotes"
folder.Parent = ReplicatedStorage
local calls = {}
local view = {
	recipes = {
		{
			id = "ForgeIronAxe",
			kind = "Special",
			category = "Tools",
			name = "Iron Axe",
			output = "IronAxe",
			quantity = 1,
			unlocked = true,
			requirement = "",
			inputs = {
				{ catalogId = "IronBar", name = "Iron Bar", owned = 40, needed = 16 },
				{ catalogId = "Wood", name = "Wood", owned = 30, needed = 10 },
			},
		},
		{
			id = "PermanentIronSword",
			kind = "Permanent",
			category = "Permanent",
			name = "Permanent Iron Sword",
			output = "IronSword",
			quantity = 1,
			unlocked = true,
			requirement = "",
			inputs = { { catalogId = "IronBar", name = "Iron Bar", owned = 40, needed = 20 } },
			sources = { { instanceId = "sword-1", name = "Iron Sword", qualityRoll = 0.02 } },
		},
		{
			id = "ForgeMithrilSword",
			kind = "Special",
			category = "Weapons",
			name = "Mithril Sword",
			output = "MithrilSword",
			quantity = 1,
			unlocked = false,
			requirement = "Unlock: Crafting mastery 20",
			inputs = { { catalogId = "MithrilBar", name = "Mithril Bar", owned = 0, needed = 30 } },
		},
	},
	categories = { "Tools", "Weapons", "Armor", "Supplies", "Permanent" },
}
for name, fn in
	{
		ForgeSnapshot = function()
			return view
		end,
		ForgeCraft = function(...)
			table.insert(calls, { ... })
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
local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local ForgeController = require(Client.Controllers.ForgeController)
local player = Players.LocalPlayer
ForgeController.Start()
ForgeController.Toggle()
local gui = player.PlayerGui:FindFirstChild("FlintbornForge")
local function check(cond, msg)
	print((cond and "  ok " or "  FAIL ") .. msg)
	if not cond then
		__failed = true
	end
end
check(gui and gui.Enabled, "the forge opens")
local window = gui.Window
check(window.Recipes:FindFirstChild("PermanentIronSword") ~= nil, "every recipe listed")
window.Recipes.ForgeIronAxe.Press.Activated:Fire()
window.Craft.Press.Activated:Fire()
check(#calls == 1 and calls[1][1] == "ForgeIronAxe" and calls[1][2] == nil, "FORGE sends the recipe")
window.Recipes.PermanentIronSword.Press.Activated:Fire()
check(window.Sources:FindFirstChild("sword-1") ~= nil, "the vault gear to convert is listed")
window.Craft.Press.Activated:Fire()
check(#calls == 1 and window.Confirm.Visible, "a conversion asks first")
window.Confirm.Yes.Press.Activated:Fire()
check(#calls == 1, "the confirm button is not armed before its delay")
window.Confirm.No.Press.Activated:Fire()
check(not window.Confirm.Visible, "cancel closes the question")
window.Recipes.ForgeMithrilSword.Press.Activated:Fire()
window.Craft.Press.Activated:Fire()
check(#calls == 1, "a locked recipe cannot be forged")
print(__failed and "FLOW FAILED" or "FLOW OK")
window.Recipes.PermanentIronSword.Press.Activated:Fire()
-- Placed as on the sheet for the picture.
window.Position = UDim2.fromOffset(23 + 814.5, 58 + 371)
window:FindFirstChildOfClass("UIScale").Scale = 1
__dump(gui, 1672, 941)
if __failed then
	error("forge flow failed")
end
