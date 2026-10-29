-- The Crafting window at the design size: a tool chosen with the materials to
-- make it and a smelt running, then the Smelting tab away from a furnace.
local Shared = game:GetService("ReplicatedStorage").Shared
local Hud = game:GetService("StarterPlayer").StarterPlayerScripts.Client.Hud
local CraftingPanel = require(Hud.CraftingPanel)
local CraftingRules = require(Shared.Crafting.CraftingRules)
local Recipes = require(Shared.Crafting.Recipes)

local gui, root = __screen()
local noop = function() end
local categories = {}
local glyphs = {
	Weapons = "pm_glyph_sword",
	Tools = "pm_glyph_tools",
	Armor = "pm_glyph_armor",
	Bars = "pm_glyph_bag",
	Consumables = "pm_glyph_heart",
	Other = "pm_glyph_bench",
}
for _, category in CraftingRules.CATEGORIES do
	table.insert(categories, { id = category.id, label = category.label, glyph = glyphs[category.id] })
end
local panel = CraftingPanel.new(root, { onClose = noop, onCraft = noop, onStop = noop }, {
	mode = "crafting",
	name = "FlintbornCrafting",
	window = "pm_window_crafting",
	categories = categories,
})
panel:SetStations(CraftingRules.STATIONS)
panel.screen.gui.Enabled = true
panel.screen:Fit(1672, 941, 0, 1)
-- Pinned to the sheet's own scale and place so the capture overlays the reference.
panel.screen.scale.Scale = 1
panel.screen.window.Position = UDim2.fromOffset(23 + 814.5, 58 + 371)

local carried = { Wood = 12, Stone = 8, Fiber = 6, Flint = 4, CopperOre = 9, Hide = 3 }
local ItemCatalog = require(Shared.Items.ItemCatalog)
local function name(id)
	local def = ItemCatalog.Get(id)
	return def and def.name or id
end
local nearby = { Workbench = true }
local entries = {}
for _, recipe in CraftingRules.Sorted(Recipes.List) do
	local inputs, can = {}, 50
	for input, amount in recipe.inputs do
		can = math.min(can, (carried[input] or 0) // amount)
		table.insert(inputs, { id = input, name = name(input), owned = carried[input] or 0, needed = amount })
	end
	table.sort(inputs, function(a, b)
		return a.name < b.name
	end)
	local station = CraftingRules.StationFor(recipe)
	table.insert(entries, {
		id = recipe.id,
		output = recipe.output,
		name = name(recipe.output),
		quantity = recipe.quantity,
		category = CraftingRules.Category(recipe),
		inputs = inputs,
		can = can,
		here = CraftingRules.AvailableHere(recipe, nearby),
		where = station or "Anywhere",
		timed = CraftingRules.IsTimed(recipe),
		verb = if CraftingRules.IsTimed(recipe) then "SMELT" else "CRAFT",
	})
end
panel:SetNearby(nearby)
panel:SetEntries(entries)
panel:SelectCategory("Tools")
local first = nil
for _, recipe in Recipes.List do
	if recipe.output == "StoneAxe" then
		first = recipe
	end
end
if first then
	panel:Select(first.id)
end
local bar = nil
for _, entry in entries do
	if entry.timed and bar == nil then
		bar = entry
	end
end
panel:SetJob({ entry = bar, count = 3, done = 2, progress = 0.8, left = 24 })
panel:SetHint("Stand within 12 studs of a station to use its recipes. Build stations with X.")
__dump(panel.screen.gui, 1672, 941)

panel:SelectCategory("Bars")
panel:SetJob(nil)
__dump(panel.screen.gui, 1672, 941)
