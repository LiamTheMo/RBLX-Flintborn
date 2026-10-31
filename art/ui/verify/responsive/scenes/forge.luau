-- QA: the Ancestral Forge through the real ForgeController (setup copied from
-- art/ui/capture/scenes/forge.luau lines 15-131), fitted by window:Watch.
-- Page 1 default; page 2 a Permanent conversion's ConfirmDialog over the window
-- (dialog layer); then B twice (dialog first, then the window).

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
workspace:SetAttribute("FlintbornPlaceRole", "Lobby")

local Shared = ReplicatedStorage.Shared
local ForgeRecipes = require(Shared.Crafting.ForgeRecipes)
local ForgeRules = require(Shared.Crafting.ForgeRules)
local ItemCatalog = require(Shared.Items.ItemCatalog)

local W, H = 1672, 941
local BACKGROUND = { background = "art/reference/ui/lobby/01_hud.png" }

local function nameOf(catalogId)
	local def = ItemCatalog.Get(catalogId)
	return def and def.name or catalogId
end

-- ForgeService.snapshot for a sample profile: vault materials, unlocked recipe
-- ids, and vault gear ({instanceId, catalogId, qualityRoll}).
local function snapshot(materials, unlocked, items)
	local profile = { vault = { materials = materials, items = items or {} }, recipes = { unlocked = {} } }
	for _, id in unlocked do
		profile.recipes.unlocked[id] = { unlockSource = "Discovery", unlockedAt = 0 }
	end
	local recipes = {}
	for _, recipe in ForgeRules.Ordered() do
		local inputs = {}
		for catalogId, needed in recipe.inputs do
			table.insert(inputs, {
				catalogId = catalogId,
				name = nameOf(catalogId),
				owned = ForgeRules.Owned(profile, catalogId),
				needed = needed,
			})
		end
		table.sort(inputs, function(a, b)
			return a.name < b.name
		end)
		local parts = {}
		if (recipe.unlock.extractions or 0) > 0 then
			table.insert(parts, ("extract %d time(s)"):format(recipe.unlock.extractions))
		end
		for _, catalogId in recipe.unlock.discovered or {} do
			table.insert(parts, "extract " .. nameOf(catalogId))
		end
		if (recipe.unlock.level or 0) > 0 then
			table.insert(parts, ("reach level %d"):format(recipe.unlock.level))
		end
		if (recipe.unlock.crafting or 0) > 0 then
			table.insert(parts, ("Crafting mastery %d"):format(recipe.unlock.crafting))
		end
		local view = {
			id = recipe.id,
			kind = recipe.kind,
			category = recipe.category,
			name = (recipe.kind == ForgeRecipes.Kinds.Permanent and "Permanent " or "") .. nameOf(recipe.output),
			output = recipe.output,
			quantity = recipe.quantity,
			unlocked = ForgeRules.IsUnlocked(profile, recipe.id),
			requirement = if #parts > 0 then "Unlock: " .. table.concat(parts, ", ") else "",
			inputs = inputs,
			maxCount = ForgeRules.MaxCount(profile, recipe),
		}
		if recipe.kind == ForgeRecipes.Kinds.Permanent then
			view.sources = {}
			for _, item in profile.vault.items do
				if item.catalogId == recipe.source then
					table.insert(view.sources, {
						instanceId = item.instanceId,
						name = nameOf(item.catalogId),
						qualityRoll = item.qualityRoll,
					})
				end
			end
		end
		table.insert(recipes, view)
	end
	return {
		recipes = recipes,
		categories = ForgeRecipes.Categories,
		tiers = ForgeRules.TIER_ORDER,
		maxBatch = ForgeRules.MAX_BATCH,
	}
end

local VAULT = { IronBar = 46, Wood = 34, Hide = 8, Flint = 9, Fiber = 14, Herbs = 6 }
local UNLOCKED =
	{ "ForgeIronPickaxe", "ForgeIronAxe", "ForgeIronSword", "ForgeIronHead", "ForgeIronChest", "ForgeArrows" }
local view = snapshot(VAULT, UNLOCKED)

local folder = Instance.new("Folder")
folder.Name = "FlintbornRemotes"
folder.Parent = ReplicatedStorage
for name, fn in
	{
		ForgeSnapshot = function()
			return view
		end,
		ForgeCraft = function()
			return true, { count = 1 }
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
local RecipeWindow = require(Client.Hud.Screens.RecipeWindow)
local player = Players.LocalPlayer
ForgeController.Start()
local GuiService = game:GetService("GuiService")
if QA.gamepad then
	local tile = Instance.new("TextButton")
	tile.Name = "HudForgeTile"
	tile.Parent = player.PlayerGui
	GuiService.SelectedObject = tile
end
ForgeController.Toggle()
local window = ForgeController.window
local screen = window.screen
window:Select("ForgeIronPickaxe")
QA.report(player.PlayerGui, { scale = screen.scale.Scale })
__dump(player.PlayerGui, QA.W, QA.H)

local permanentVault = table.clone(VAULT)
permanentVault.IronBar = 60
permanentVault.Wood = 40
permanentVault.Fiber = 24
permanentVault.AncientEmber = 3
local unlocked = table.clone(UNLOCKED)
table.insert(unlocked, "PermanentIronPickaxe")
view = snapshot(permanentVault, unlocked, {
	{ instanceId = "pick-1", catalogId = "IronPickaxe", qualityRoll = 0.034 },
	{ instanceId = "pick-2", catalogId = "IronPickaxe", qualityRoll = -0.012 },
})
ForgeController.Refresh()
window:SetCategory("Permanent")
window:Select("PermanentIronPickaxe")
window.button.control:Activate()
local dialog = player.PlayerGui:FindFirstChild("KitDialog")
local Modal = require(Client.Hud.Kit.Modal)
QA.report(player.PlayerGui, { scale = screen.scale.Scale, dialog = dialog ~= nil and dialog.Enabled, modalCount = Modal.Count() })
__dump(player.PlayerGui, QA.W, QA.H)
local r1 = QA.back()
local afterOne = { window = screen:IsOpen(), dialog = dialog and dialog.Enabled }
local r2 = QA.back()
print("QA back1:", r1, "window open:", afterOne.window, "dialog enabled:", afterOne.dialog, "| back2:", r2, "window open:", screen:IsOpen())
