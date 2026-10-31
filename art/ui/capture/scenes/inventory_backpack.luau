-- The Inventory window's Backpack tab (art/reference/ui/lobby/02_inventory.png)
-- built by Hud/Screens/InventoryWindow with sample data, placed where the
-- mockup has it over the lobby HUD mockup. Compare with:
--   python3 art/ui/capture/capture.py inventory_backpack --compare art/reference/ui/lobby/02_inventory.png
local Players = game:GetService("Players")
local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local ItemInfo = require(game:GetService("ReplicatedStorage").Shared.Items.ItemInfo)
local InventoryWindow = require(Client.Hud.Screens.InventoryWindow)

local W, H = 1672, 941

-- Every kit sprite item art may use is in the sprite manifest (the item_info
-- spec checks every item resolves to one of them).
local Kit = require(Client.Hud.Kit)
for _, sprite in ItemInfo.ART_SPRITES do
	assert(Kit.Art.SizeOf(sprite) ~= nil, "item art missing from the manifest: " .. sprite)
end

-- Sample backpack in the mockup's order (real catalog items; ones without kit
-- art draw the kit's fallback, their name in ink).
local SAMPLE = {
	{ "StoneAxe" },
	{ "StonePickaxe" },
	{ "StoneSpear" },
	{ "Flint", 6 },
	{ "Wood", 32 },
	{ "Stone", 28 },
	{ "Resin", 18 },
	{ "Clay", 12 },
	{ "Fiber", 8 },
	{ "Redberry", 14 },
	{ "Herbs", 6 },
	{ "CaveMushroom", 11 },
	{ "WoodenAxe" },
	{ "WoodenPickaxe" },
	{ "IronBar", 4 },
	{ "Hide", 9 },
	{ "Bone", 7 },
	{ "DireHide", 3 },
	{ "Thornvine", 5 },
	{ "Frostleaf", 9 },
	{ "Hazelnut", 4 },
	{ "Amethyst", 3 },
	{ "IronOre", 6 },
}

local window = InventoryWindow.new({
	tabs = {
		{ id = "Backpack", label = "Backpack", icon = "backpack", iconSelected = "backpack_white" },
		{ id = "Vault", label = "Vault", icon = "chest" },
	},
})
local cells = {}
for index = 1, 50 do
	local entry = SAMPLE[index]
	table.insert(cells, {
		id = "b" .. index,
		item = entry and { catalogId = entry[1], quantity = entry[2] } or nil,
	})
end
window:SetSections({ { id = "backpack", cells = cells } })
window:SetSelected("b1")
local item = { catalogId = "StoneAxe" }
window:SetDetail({
	catalogId = "StoneAxe",
	name = "Stone Axe",
	text = ItemInfo.Text(item),
	rows = ItemInfo.StatRows(item),
	actions = { { id = "store", label = "Store" } },
})
window:Open()
window.screen.holder.Position = UDim2.fromOffset(243 + 1187 / 2, 150 + InventoryWindow.SIZE[2] / 2)
window.screen.scale.Scale = 1
__dump(Players.LocalPlayer.PlayerGui, W, H, { background = "art/reference/ui/lobby/01_hud.png" })
