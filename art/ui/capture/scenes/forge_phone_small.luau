-- The Forge window on a phone held sideways (667 x 375, touch only, the top
-- bar 58 px down), fitted as in game; prints the smallest text it draws.
-- Page 2 chooses the locked Iron Legs/Boots (its two-line unlock note).
local UserInputService = game:GetService("UserInputService")
workspace.CurrentCamera.ViewportSize = Vector2.new(667, 375)
UserInputService.TouchEnabled = true
UserInputService.KeyboardEnabled = false
UserInputService.MouseEnabled = false
UserInputService.GetLastInputType = function()
	return Enum.UserInputType.Touch
end

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
	-- An empty lobby backpack: MaxCount also caps a batch by its room.
	local profile = {
		vault = { materials = materials, items = items or {} },
		recipes = { unlocked = {} },
		lobbyBackpack = { slots = {} },
	}
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
ForgeController.Toggle()
local window = ForgeController.window
local screen = window.screen

-- Effective screen size of every fixed-size kit label (scaled labels shrink to
-- their box and are listed apart).
local function report(gui, scale, tag)
	local smallest, count = math.huge, 0
	for _, item in gui:GetDescendants() do
		local shown = item.Visible
		local node = item.Parent
		while shown and node and node:IsA("GuiObject") do
			shown = node.Visible
			node = node.Parent
		end
		if shown and item:IsA("TextLabel") and item:GetAttribute("KitTextRole") and item.Text ~= "" then
			local px = item.TextSize * scale
			count += 1
			if px < smallest then
				smallest = px
			end
			if px < 9 then
				print(("  under 9 px: %s %q %.1f px (%s)"):format(tag, item.Text, px, item:GetAttribute("KitTextRole")))
			end
		end
	end
	print(("%s: window scale %.3f, %d labels, smallest %.1f screen px"):format(tag, scale, count, smallest))
end

screen:Fit(667, 375, 58, 1)
report(screen.gui, screen.scale.Scale, "forge_phone_small")
__dump(Players.LocalPlayer.PlayerGui, 667, 375)

-- 2: the locked Iron Legs/Boots chosen and scrolled into view: its unlock
-- note wraps onto two lines inside the taller phone row, and no recipe or
-- material name ends in "…" (they shrink to fit).
window:Select("ForgeIronLegs")
local fits = true
for id, row in window.rows do
	local sub = row.subtitle
	if row.titleCut or sub.Position.Y.Offset + sub.Size.Y.Offset > row.h then
		fits = false
		print("  FAIL forge_phone_small: row " .. id .. " does not fit its card")
	end
end
for id, row in window.materialRows do
	if row.titleCut then
		fits = false
		print("  FAIL forge_phone_small: material " .. id .. " is cut")
	end
end
local legs = window.rows.ForgeIronLegs
print(
	if fits
			and legs
			and legs.subtitle.TextWrapped
		then "  ok forge_phone_small: names whole, the unlock note on two lines inside its row"
		else "  FAIL forge_phone_small: a name or note does not fit"
)
if not (fits and legs and legs.subtitle.TextWrapped) then
	error("forge_phone_small: a row does not fit")
end
__dump(Players.LocalPlayer.PlayerGui, 667, 375)
