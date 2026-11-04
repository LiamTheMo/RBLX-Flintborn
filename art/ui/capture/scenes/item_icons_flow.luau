-- Item icons (art/ui/items/build_item_icons.py): every catalog item draws its
-- own lk_item_<id> and nothing else. While the icon's atlas
-- (atlas_lk_items3_*) is still pending on this client, each item picture shows
-- its kind glyph (Art.KindGlyph: never a letter); when the atlas loads, the
-- same picture swaps to the icon by itself, with nothing rebuilt. The hero copy
-- (an image of its own) replaces the slot icon in a hero box once it has
-- loaded, in the same label, and never in a slot.
--
-- Runs with the live loader (not the capture shortcut), so load states are
-- real: the capture runtime's clock never runs, so the loader's ticks are
-- called by hand, and the grace period before a stand-in shows is taken as
-- passed. Page 1 is every picture while the atlases are pending, page 2 the
-- same pictures once they have loaded.
__FlintbornCapture = false
__preloadStatus = {}
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
check(atlases.atlas_lk_items3_1 and atlases.atlas_lk_items3_2, "packed into the atlas_lk_items3 atlases")
check(
	UiAssets.image("atlas_lk_items3_1") ~= nil and UiAssets.image("atlas_lk_items3_2") ~= nil,
	"both icon atlases have ids"
)
check(ItemInfo.Icon == nil and ItemInfo.ART_SPRITES == nil, "no older item art is left in ItemInfo")
check(Kit.Art.ItemIcon("Nope") == nil, "an unknown item has no icon")

-- The loader runs its first tick inside the first Assign (this image); after
-- that nothing loads until the scene ticks it, so every atlas below stays
-- pending until then.
SpriteLoader.Assign(Instance.new("ImageLabel"), "rbxassetid://1")
Kit.Art.GRACE = 0

local function atlasOf(id: string): string
	return UiAssets.image(UiAssets.sprite("lk_item_" .. id).atlas) :: string
end
local function kindGlyph(id: string): string
	return Kit.Art.ITEM_KIND_GLYPH[string.gsub(Kit.Art.KindGlyph(id), "^ink:", "")]
end
-- The picture's image and its stand-in glyph (Art.Icon names them Item and
-- ItemStandIn).
local function parts(icon)
	local root = if typeof(icon) == "Instance" then icon else icon.root
	local image, glyph = nil, nil
	for _, child in root:GetDescendants() do
		if child.Name == "Item" and child:IsA("ImageLabel") then
			image = child
		elseif child.Name == "ItemStandIn" and child:IsA("TextLabel") then
			glyph = child
		end
	end
	return image, glyph
end

local W, H = 980, 300
local gui, root = __screen(W, H)
Kit.Panel.new(root, { name = "Back", rect = { 0, 0, W, H }, zIndex = 1 })
-- Every place an item is drawn goes through Kit.ItemIcon: inventory and vault
-- slots, the hotbar, list rows (market, trade, loot, storage), the Inventory
-- detail card and the Forge / Crafting picture (hero boxes), recipe rows.
local itemSlot = Kit.Slot.new(root, { rect = { 20, 20, 92, 99 }, item = { catalogId = "Wood", quantity = 32 } })
local hotbar = Kit.Slot.new(root, { rect = { 124, 20, 96, 96 }, variant = "hotbar", item = { catalogId = "StoneAxe" } })
local row = Kit.ListRow.new(root, { rect = { 20, 140, 320, 64 }, catalogId = "IronChest", title = "Iron Chest" })
local recipeRow = Kit.ItemIcon.new(root, { rect = { 20, 220, 52, 52 }, itemId = "AdamantineAxe" })
local detail = Kit.ItemIcon.new(root, { rect = { 360, 20, 152, 166 }, catalogId = "IronSword", maxScale = false })
local forge = Kit.ItemIcon.new(root, { rect = { 540, 20, 254, 254 }, catalogId = "Wood", maxScale = false })
local pictures = {
	{ "the inventory slot", itemSlot.icon, "Wood" },
	{ "the hotbar slot", hotbar.icon, "StoneAxe" },
	{ "the list row", row.icon, "IronChest" },
	{ "the recipe row", recipeRow, "AdamantineAxe" },
	{ "the detail card", detail, "IronSword" },
	{ "the Forge picture", forge, "Wood" },
}
local pending = {}
for _, picture in pictures do
	pending[atlasOf(picture[3])] = true
end
check(
	pending[UiAssets.image("atlas_lk_items3_1")] and pending[UiAssets.image("atlas_lk_items3_2")],
	"both atlases in use"
)
for atlas in pending do
	check(SpriteLoader.State(atlas) ~= "loaded", "pending: " .. atlas .. " has not loaded")
end
local held = {}
for _, picture in pictures do
	local label, icon, id = picture[1], picture[2], picture[3]
	local image, glyph = parts(icon)
	held[label] = { image = image, glyph = glyph }
	check(image ~= nil and not image.Visible, "pending: " .. label .. " hides the icon")
	check(
		glyph ~= nil and glyph.Visible and glyph.Text == kindGlyph(id),
		"pending: " .. label .. " shows " .. id .. "'s kind glyph " .. kindGlyph(id)
	)
	check(glyph ~= nil and string.find(glyph.Text, "%a") == nil, "pending: " .. label .. " shows no letter")
end
check(kindGlyph("StoneAxe") ~= kindGlyph("Wood") and kindGlyph("IronChest") ~= kindGlyph("Wood"), "kinds differ")
__dump(gui, W, H)

-- The atlases load: every picture swaps to its icon by itself.
for _ = 1, 20 do
	SpriteLoader._tick()
end
for atlas in pending do
	check(SpriteLoader.State(atlas) == "loaded", "loaded: " .. atlas)
end
local oldAtlas = UiAssets.image("atlas_lk_items")
for _, picture in pictures do
	local label, icon, id = picture[1], picture[2], picture[3]
	local image, glyph = parts(icon)
	local before = held[label]
	check(image == before.image and image.Parent ~= nil, "loaded: " .. label .. " is the same picture (no rebuild)")
	check(image.Visible and not before.glyph.Visible, "loaded: " .. label .. " shows the icon, not the glyph")
	check(glyph == before.glyph, "loaded: " .. label .. " keeps its hidden stand-in")
	check(image.Image ~= "" and image.Image ~= oldAtlas, "loaded: " .. label .. " draws no older item art")
	if icon == forge or icon == detail then
		-- Hero boxes: the slot icon until the hero copy loads, then the copy.
		check(
			image.Image == atlasOf(id) or image.Image == UiAssets.image("lk_item_" .. id .. "__hi"),
			"loaded: " .. label .. " draws " .. id .. "'s icon or hero copy"
		)
	else
		check(image.Image == atlasOf(id), "loaded: " .. label .. " draws " .. id .. "'s atlas")
	end
end

-- Hero copies: gated on their own image, which the loader fetches once the
-- slot icons are in; once loaded the copy takes the hero box's label, and a
-- slot keeps the 1x atlas.
local heroId = UiAssets.image("lk_item_Wood__hi") :: string
local forgeImage = parts(forge)
check(SpriteLoader.State(heroId) == "loaded", "the Forge picture's hero copy is fetched after the icons")
check(forgeImage.Image == heroId, "and replaces the slot icon in the same label")
check(forgeImage.ImageRectSize == Vector2.zero, "drawn whole (an image of its own)")
check(Widgets._readyImage("lk_item_Wood__hi") == heroId, "the hero image is ready")
check(Widgets.ImageId("lk_item_Wood", 254 / 110) == heroId, "the Forge picture draws the hero copy")
check(Widgets.ImageId("lk_item_Wood", 152 / 110) == heroId, "so does the Inventory detail card")
check(Widgets.ImageId("lk_item_Wood", 67 / 110) == atlasOf("Wood"), "a slot keeps the 1x atlas")
check(parts(itemSlot.icon).Image == atlasOf("Wood"), "and the Wood slot still draws it")

print(failures == 0 and "FLOW OK" or "FLOW FAILED")
__dump(gui, W, H)
if failures > 0 then
	error("item icons flow failed")
end
