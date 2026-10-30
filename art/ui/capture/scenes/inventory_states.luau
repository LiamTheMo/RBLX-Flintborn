-- Every interactive state of the Inventory window (Hud/Screens/InventoryWindow),
-- forced through the kit's DebugState hook as verifiers do, plus the phone
-- layout. Sample data. Pages:
--   1 hover / pressed / focused / disabled / locked across tabs, categories,
--     slots, toolbar and card buttons; the search box focused with text;
--     a busy main action
--   2 a category filter with a search that matches nothing
--   3 the window fitted to an 844 × 390 phone screen (touch: fills the screen)
local Players = game:GetService("Players")
local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local ItemInfo = require(game:GetService("ReplicatedStorage").Shared.Items.ItemInfo)
local InventoryWindow = require(Client.Hud.Screens.InventoryWindow)

local SAMPLE = {
	{ "StoneAxe" },
	{ "StonePickaxe" },
	{ "StoneSpear" },
	{ "Flint", 6 },
	{ "Wood", 32 },
	{ "Stone", 28 },
	{ "Fiber", 8 },
	{ "Redberry", 14 },
	{ "CaveMushroom", 11 },
	{ "Hide", 9 },
	{ "Bone", 7 },
}

local window = InventoryWindow.new({
	tabs = {
		{ id = "Backpack", label = "Backpack", icon = "backpack", iconSelected = "backpack_white" },
		{ id = "Vault", label = "Vault 4/25", icon = "chest" },
	},
})
local cells = {}
for index = 1, 50 do
	local entry = SAMPLE[index]
	table.insert(cells, { id = "b" .. index, item = entry and { catalogId = entry[1], quantity = entry[2] } or nil })
end
cells[11].state = "disabled"
cells[12].state = "locked"
window:SetSections({ { id = "backpack", cells = cells } })
window:SetSelected("b1")
window:SetToolbar({ { id = "sort", label = "Sort: Name" }, { id = "storeAll", label = "Store All", enabled = false } })
local item = { catalogId = "StoneSpear", qualityRoll = 0.02 }
window:SetDetail({
	catalogId = "StoneSpear",
	name = "Stone Spear",
	text = ItemInfo.Text(item),
	rows = ItemInfo.StatRows(item),
	actions = {
		{ id = "equip", label = "Equip" },
		{ id = "move", label = "Move" },
		{ id = "drop", label = "Drop (Q)", enabled = false },
	},
})
window:Open()
window.screen.holder.Position = UDim2.fromOffset(243 + 1187 / 2, 150 + 652 / 2)
window.screen.scale.Scale = 1

local function force(component, state)
	component.root:SetAttribute("DebugState", state)
end
force(window.tabs.Vault, "hover")
force(window.categories.tabs[2], "hover")
force(window.categories.tabs[3], "pressed")
force(window:SlotFor("b2"), "hover")
force(window:SlotFor("b3"), "pressed")
force(window:SlotFor("b4"), "focused")
force(window.toolbar.sort, "pressed")
force(window:ActionButton("move"), "hover")
force(window:ActionButton("equip"), "pressed")
window.window.close.root:SetAttribute("DebugState", "hover")
window.search:SetText("sto")
force(window.search, "focused")
__dump(Players.LocalPlayer.PlayerGui, 1672, 941, { background = "art/reference/ui/lobby/01_hud.png" })

-- 2: filters, nothing matches; the main action busy.
for _, part in window.screen.gui:GetDescendants() do
	if part:GetAttribute("DebugState") then
		part:SetAttribute("DebugState", "")
	end
end
window:SetCategory("Food")
window:SetQuery("axe")
window:SetBusy(true)
__dump(Players.LocalPlayer.PlayerGui, 1672, 941, { background = "art/reference/ui/lobby/01_hud.png" })
window:SetBusy(false)

-- 3: phone.
window:SetQuery("")
window:SetCategory("All")
window.screen:Fit(844, 390, 0)
__dump(Players.LocalPlayer.PlayerGui, 844, 390)
