-- Item icons (art/ui/items/build_item_icons.py): every catalog item draws its
-- own lk_item_<id> once that icon's atlas is uploaded (previewed here), its
-- older kit art (or the kind glyph) until then, never a slot of only a hero
-- copy; and the hero copy, an image of its own rather than an atlas, draws in
-- a hero box only once that image has loaded on this client (Widgets'
-- readyImage gate), in a slot never. Runs with the live loader (not the
-- capture shortcut) so load states are real; dumps the slots it built.
__FlintbornCapture = false
local Shared = game:GetService("ReplicatedStorage").Shared
local Hud = game:GetService("StarterPlayer").StarterPlayerScripts.Client.Hud
local ItemCatalog = require(Shared.Items.ItemCatalog)
local ItemInfo = require(Shared.Items.ItemInfo)
local UiAssets = require(Shared.UI.UiAssets)
local SpriteLoader = require(Hud.SpriteLoader)
local Widgets = require(Hud.Widgets)
local Kit = require(Hud.Kit)

local failures = 0
local function check(ok, message)
	print((ok and "  ok " or "  FAIL ") .. message)
	if not ok then
		failures += 1
	end
end

-- Every item has its icon and hero copy in the sprite table, and draws it.
local atlases = {}
local missing = {}
for id in ItemCatalog.Items do
	local name = ItemInfo.ItemSprite(id) :: string
	local entry = UiAssets.sprite(name)
	local copies = UiAssets.Copies(name)
	if entry == nil or #copies ~= 1 or Kit.Art.ItemIcon(id) ~= name then
		table.insert(missing, id)
	elseif type(entry.atlas) == "string" then
		atlases[entry.atlas] = true
	end
end
check(#missing == 0, "every catalog item draws its own icon (" .. table.concat(missing, ", ") .. ")")
check(atlases.atlas_lk_items2_1 and atlases.atlas_lk_items2_2, "packed into the atlas_lk_items2 atlases")

-- Without the new atlases' ids (the capture also previews each loose 1x PNG,
-- which the game never uploads): the older kit art, or the kind glyph.
local saved = {}
for atlas in atlases do
	saved[atlas] = UiAssets.Ids[atlas]
	UiAssets.Ids[atlas] = nil
end
for id in ItemCatalog.Items do
	local name = ItemInfo.ItemSprite(id) :: string
	saved[name] = UiAssets.Ids[name]
	UiAssets.Ids[name] = nil
end
check(Kit.Art.ItemIcon("Wood") == "lk_icon_logs", "not uploaded: wood keeps its logs")
local sprite, tint = Kit.Art.ItemIcon("IronOre")
check(sprite == "lk_icon_rocks" and tint ~= nil, "not uploaded: iron ore keeps its tinted rocks")
check(Kit.Art.ItemIcon("IronSword") == nil, "not uploaded: a sword has no older art")
local gui, root = __screen(420, 120)
local sword = Kit.Slot.new(root, { rect = { 10, 10, 92, 99 }, item = { catalogId = "IronSword" } })
check(sword.icon.root:GetAttribute("KitStandIn") == true, "so its slot shows the kind glyph")
local logs = Kit.Slot.new(root, { rect = { 110, 10, 92, 99 }, item = { catalogId = "Wood" } })
check(logs.icon.root:GetAttribute("KitRole") == "item.lk_icon_logs", "and wood's slot the logs")
-- Hero copies uploaded before their slot atlas: still the older art.
check(UiAssets.image("lk_item_Wood__hi") ~= nil, "the hero copy has its own image")
check(not Widgets.HasBaseArt("lk_item_Wood"), "a copy alone is not 1x art")
check(Kit.Art.ItemIcon("Wood") == "lk_icon_logs", "a copy alone keeps the older art")
for name, id in saved do
	UiAssets.Ids[name] = id
end
local wood = Kit.Slot.new(root, { rect = { 210, 10, 92, 99 }, item = { catalogId = "Wood" } })
check(wood.icon.root:GetAttribute("KitRole") == "item.lk_item_Wood", "uploaded: wood's slot draws its own icon")

-- The hero copy is gated on its own image: not drawn until it has loaded.
local atlasId = UiAssets.image(UiAssets.sprite("lk_item_Wood").atlas)
local heroId = UiAssets.image("lk_item_Wood__hi") :: string
local forge = 254 / 110
check(Widgets._readyImage("lk_item_Wood__hi") == nil, "a hero image not loaded yet is not ready")
check(Widgets.ImageId("lk_item_Wood", forge) == atlasId, "so the Forge picture draws the 1x atlas meanwhile")
local image = SpriteLoader._images[heroId]
check(image ~= nil, "and the hero image is fetched in the background")
if image then
	image.state = "loaded"
end
check(Widgets._readyImage("lk_item_Wood__hi") == heroId, "once loaded it is ready")
check(Widgets.ImageId("lk_item_Wood", forge) == heroId, "the Forge picture then draws the hero copy")
check(Widgets.ImageId("lk_item_Wood", 152 / 110) == heroId, "so does the Inventory detail card")
check(Widgets.ImageId("lk_item_Wood", 67 / 110) == atlasId, "a slot keeps the 1x atlas")

print(failures == 0 and "FLOW OK" or "FLOW FAILED")
__dump(gui, 420, 120)
if failures > 0 then
	error("item icons flow failed")
end
