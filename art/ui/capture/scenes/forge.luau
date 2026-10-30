-- The Ancestral Forge (docs/ui/ForgeScreen.md, mockup art/reference/ui/lobby/06_forge.png)
-- built by the real ForgeController over a mocked ForgeSnapshot. The snapshot is
-- made the way ForgeService makes it, from the real recipes (ForgeRules, ForgeRecipes)
-- and a sample vault, so names, costs and limits are the game's own.
--
--   1 default: Iron Pickaxe chosen, quantity 1, placed where the mockup has it
--   2 states: a hovered row, the stepper at its max (+ disabled), FORGE pressed
--   3 a locked recipe chosen (LOCKED, the unlock text)
--   4 short materials (red have count, FORGE disabled)
--   5 three inputs (compact cards) with FORGE busy
--   6 the category dropdown open on Tools
--   7 a Permanent conversion (no stepper, CONVERT)
--   8 its confirmation: pick the vault item, press-and-hold CONVERT
--   9 phone 844 × 390

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
local player = Players.LocalPlayer
ForgeController.Start()
ForgeController.Toggle()
local window = ForgeController.window
local screen = window.screen

local function check(cond, msg)
	print((cond and "  ok " or "  FAIL ") .. msg)
	if not cond then
		__failed = true
	end
end

-- The mockup's place and size (window 285, 132, 1102 × 682).
local function pin()
	screen.holder.Position = UDim2.fromOffset(285 + 1102 / 2, 132 + 682 / 2)
	screen.scale.Scale = 1
end

local function force(component, state)
	component.root:SetAttribute("DebugState", state)
end

local function clear()
	for _, root in { window.button.root, window.stepper.root } do
		root:SetAttribute("DebugState", nil)
	end
	for _, row in window.rows do
		row.root:SetAttribute("DebugState", nil)
	end
end

-- 1 default ----------------------------------------------------------------------------
pin()
check(window:Selected() and window:Selected().id == "ForgeIronPickaxe", "the first recipe is chosen")
check(window.button.root:GetAttribute("KitState") == "normal", "FORGE ready")
check(window.stepper.root.Visible, "the stepper shows for a special recipe")
check(window.stepper.max == 2, "QUANTITY is bounded by the snapshot's maxCount (46 bars / 20)")
check(window.materialRows.IronBar.root:GetAttribute("KitState") == "selected", "the recipe's inputs are highlighted")
check(window.materialRows.Hide.root:GetAttribute("KitState") ~= "selected", "other materials are not")
__dump(player.PlayerGui, W, H, BACKGROUND)

-- 2 states -------------------------------------------------------------------------------
window:Select("ForgeIronPickaxe")
window.stepper.plus.control:Activate()
check(window:Count() == 2, "+ raises the quantity")
check(window.stepper.root.Visible and window.stepper.plus.root:GetAttribute("KitState") == "disabled", "+ disabled at max")
force(window.rows.ForgeIronAxe, "hover")
force(window.button, "pressed")
__dump(player.PlayerGui, W, H, BACKGROUND)
clear()

-- 3 locked -------------------------------------------------------------------------------
window.rows.ForgeIronLegs.control:Activate()
check(window:Selected().id == "ForgeIronLegs", "a locked recipe can still be chosen")
check(window.button.root:GetAttribute("KitState") == "disabled", "LOCKED cannot be pressed")
check(window.rows.ForgeIronLegs.root:GetAttribute("KitState") == "locked", "the row draws locked")
__dump(player.PlayerGui, W, H, BACKGROUND)

-- 4 short --------------------------------------------------------------------------------
window:Select("ForgeIronChest")
check(window.button.root:GetAttribute("KitState") == "disabled", "short materials disable FORGE")
check(string.find(window.blocker or "", "Hide", 1, true) ~= nil, "the reason names the short input")
__dump(player.PlayerGui, W, H, BACKGROUND)

-- 5 three inputs, busy -------------------------------------------------------------------
window:Select("ForgeArrows")
window:SetBusy(true)
check(window.button.root:GetAttribute("KitState") == "busy", "FORGE busy while a request is in flight")
check(#window.cards == 3, "one card per input")
__dump(player.PlayerGui, W, H, BACKGROUND)
window:SetBusy(false)

-- 6 dropdown -----------------------------------------------------------------------------
window:SetCategory("Tools")
window.dropdown:SetOpen(true)
check(#window.filtered == 2, "Tools lists the two tool recipes")
__dump(player.PlayerGui, W, H, BACKGROUND)
window.dropdown:SetOpen(false)
window:SetCategory("All")

-- 7 Permanent ----------------------------------------------------------------------------
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
-- The capture cannot scroll a list, so show the Permanent category.
window:SetCategory("Permanent")
window:Select("PermanentIronPickaxe")
check(not window.stepper.root.Visible, "no stepper for a Permanent conversion")
check(window.button.text == "Convert", "the button says CONVERT")
check(window.rows.PermanentIronPickaxe.root.LayoutOrder < window.rows.PermanentWoodenSpear.root.LayoutOrder, "conversions for vault gear come first")
__dump(player.PlayerGui, W, H, BACKGROUND)

-- 8 confirmation -------------------------------------------------------------------------
window.button.control:Activate()
local dialog = player.PlayerGui:FindFirstChild("KitDialog")
check(dialog ~= nil and dialog.Enabled, "a conversion asks first")
check(window.confirm and window.confirm.dialog.body:FindFirstChild("Sources", true) ~= nil, "two vault items: pick one")
__dump(player.PlayerGui, W, H, BACKGROUND)
window.confirm.Close()
window:SetCategory("All")

-- 9 phone --------------------------------------------------------------------------------
view = snapshot(VAULT, UNLOCKED)
ForgeController.Refresh()
window:Select("ForgeIronPickaxe")
-- A touch-only phone: the window fills the screen below the top bar.
local UserInputService = game:GetService("UserInputService")
UserInputService.TouchEnabled = true
UserInputService.KeyboardEnabled = false
screen:Fit(844, 390, 52, 1)
__dump(player.PlayerGui, 844, 390)

print(__failed and "FORGE SCENE FAILED" or "FORGE SCENE OK")
if __failed then
	error("forge scene failed")
end
