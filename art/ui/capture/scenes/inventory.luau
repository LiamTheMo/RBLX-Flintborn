-- The Inventory & Vault window at the design size: the lobby layout with the
-- reference sheet's items (an Iron Axe chosen), then the run layout.
local Hud = game:GetService("StarterPlayer").StarterPlayerScripts.Client.Hud
local InventoryPanel = require(Hud.InventoryPanel)
local ItemCatalog = require(game:GetService("ReplicatedStorage").Shared.Items.ItemCatalog)

local gui, root = __screen()
local noop = function() end
local panel = InventoryPanel.new(root, { onClose = noop, onSlot = noop })
panel.screen.gui.Enabled = true
panel.screen:Fit(1672, 941, 0, 1)
-- Pinned to the sheet's own scale and place so the capture overlays the reference.
panel.screen.scale.Scale = 1
panel.screen.window.Position = UDim2.fromOffset(148 + 747, 6 + 393)

local function item(id, quantity)
	local def = ItemCatalog.Get(id)
	assert(def, id)
	return { catalogId = id, name = def.name, quantity = quantity, rarity = def.rarity }
end
local left = {}
for index, entry in
	{
		item("IronAxe"),
		item("IronPickaxe"),
		item("StoneSpear"),
		item("Wood", 64),
		item("Stone", 48),
		item("Fiber", 22),
		item("RawMeat", 12),
		item("Redberry", 25),
		item("Thornvine", 17),
		item("Hide", 6),
		item("IronBar", 8),
		item("IronOre", 3),
	}
do
	table.insert(left, { id = index, item = entry })
end
local right = {}
for index, entry in
	{
		item("Wood", 120),
		item("Stone", 84),
		item("IronBar", 36),
		item("Obsidian", 28),
		item("Hide", 40),
		item("Herbs", 73),
		item("CopperOre", 52),
		item("SilverOre", 18),
		item("Flint", 91),
		item("CobaltOre", 26),
		item("Thornvine", 30),
		item("Bone", 44),
	}
do
	table.insert(right, { id = index, item = entry })
end
panel:SetTitle("INVENTORY & VAULT")
panel:SetHeader("left", "INVENTORY")
panel:SetHeader("right", "VAULT", "pm_icon_chest", { 12, 25 })
panel:SetPane("left", { { entries = left } })
panel:SetPane("right", { { entries = right } })
panel:Select({ paneId = "left", id = 1 })
panel:SetDetail(left[1].item)
panel:SetMiddle({ true, noop }, { false, noop }, { "STORE\nALL", true, noop })
panel:SetActions({ { "TAKE", false, noop }, { "STORE", true, noop } })
__dump(panel.screen.gui, 1672, 941)

-- A vault material chosen: the amount picker.
panel:Select({ paneId = "right", id = 1 })
panel:SetDetail(right[1].item)
panel:SetAmounts({ "×1", "×10", "×100", "All" }, 2, noop)
panel:SetActions({ { "TAKE", true, noop }, { "STORE", false, noop } })
panel:SelectTab("Materials")
__dump(panel.screen.gui, 1672, 941)

-- The run: backpack slots in place, the hotbar and armour on the right.
panel:SetAmounts(nil)
panel:SelectTab("All")
panel:SetTitle("INVENTORY")
panel:SetHeader("left", "BACKPACK")
panel:SetHeader("right", "EQUIPMENT", "pm_cat_all", nil)
local backpack = {}
for index = 1, 50 do
	table.insert(backpack, { id = index, item = left[index] and left[index].item or nil })
end
local hotbar = {}
for index = 1, 6 do
	table.insert(
		hotbar,
		{ id = "h" .. index, item = if index <= 2 then left[index].item else nil, key = tostring(index) }
	)
end
local armor = {}
for index, slot in { "Head", "Chest", "Legs" } do
	table.insert(armor, { id = "a" .. index, item = if index == 2 then item("HideChest") else nil, key = slot })
end
panel:SetPane("left", { { entries = backpack } }, "dim")
panel:SetPane("right", { { header = "Hotbar", entries = hotbar }, { header = "Armour", entries = armor } }, "dim")
panel:Select({ paneId = "left", id = 4 }, { paneId = "right", id = "h1" })
panel:SetDetail(left[4].item)
panel:SetMiddle({ true, noop }, { false, noop }, { "DROP", true, noop })
panel:SetActions({ nil, { "EQUIP", false, noop } })
__dump(panel.screen.gui, 1672, 941)
