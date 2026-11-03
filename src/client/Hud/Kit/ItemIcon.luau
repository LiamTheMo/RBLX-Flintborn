-- A catalog item's picture: its own icon, lk_item_<CatalogId> (Art.ItemIcon,
-- built from the owner's item art, STYLE_GUIDE §9.7), drawn through Art.Icon.
-- While the icon's atlas has not loaded on this client the item's kind glyph
-- stands in (faded, never a letter), and the icon replaces it by itself the
-- moment the atlas loads: nothing is rebuilt and no window has to be reopened.
-- An unknown item shows the `icon` prop, else its kind glyph (KitStandIn);
-- KitItemName carries the name for tooltips and detail cards, so no slot prints
-- text.
--
-- In slots, rows and tiles the picture is never drawn larger than its art
-- (MAX_SCALE design px per pixel of the art that draws there, Art.Capped): a
-- box bigger than the art centres it at that size instead of blurring it. The
-- hero boxes (the Forge and Crafting picture, the Inventory detail card) pass
-- `maxScale = false`: every item fills the box. There the slot icon draws
-- until the item's hero copy (`lk_item_<id>__hi`, 356 px, an image of its own)
-- has loaded on this client, which then takes its place in the same label
-- (Widgets).
--
--   Kit.ItemIcon.new(slot, { rect = { 10, 10, 70, 70 }, catalogId = "StoneAxe" })
--   Kit.ItemIcon.new(card, { rect = { 73, 38, 152, 166 }, catalogId = "StoneAxe", maxScale = false })

local Art = require(script.Parent.Art)
local Core = require(script.Parent.Core)
local Tokens = require(script.Parent.Tokens)

local ItemIcon = {}
ItemIcon.__index = ItemIcon

-- The largest an item picture is drawn: design px per pixel of its art (the
-- 1x art; a high-resolution copy once the box reaches its HiFrom).
ItemIcon.MAX_SCALE = 1

-- props: rect | size, catalogId (or itemId), icon (an icon id shown when the
-- id is not a catalog item), zIndex, name, maxScale
-- (default MAX_SCALE; false draws the art at the full box: the hero boxes).
function ItemIcon.new(parent: Instance, props)
	local w, h = Core.Size(props, 70, 70)
	local base = Core.Root(parent, "ItemIcon", "item", props, w, h)
	local self = setmetatable({ root = base.root, base = base, w = w, h = h, image = nil }, ItemIcon)
	self.maxScale = if props.maxScale == false then nil else props.maxScale or ItemIcon.MAX_SCALE
	self:SetItem(props.catalogId or props.itemId, props.icon)
	return self
end

function ItemIcon:SetItem(catalogId: string?, icon: string?)
	if self.image then
		self.image:Destroy()
		self.image = nil
	end
	self.catalogId = catalogId
	self.root:SetAttribute("KitStandIn", nil)
	local z = self.base.z + 1
	local sprite = Art.ItemIcon(catalogId)
	self.root:SetAttribute("KitRole", "item." .. tostring(sprite or icon or catalogId))
	if sprite or icon then
		self.image = Art.Icon(self.base.visual, sprite or icon :: string, { 0, 0, self.w, self.h }, {
			z = z,
			name = "Item",
			-- While the icon's image is not served: the item's kind glyph, about
			-- the no-art placeholder's size.
			standInScale = 0.5,
			maxScale = self.maxScale,
		})
		if sprite and not Art.HasArt(sprite) then
			-- No id for its atlas: the kind glyph is all there is.
			self.root:SetAttribute("KitStandIn", true)
		end
	elseif catalogId then
		-- Not a catalog item: a neutral kind glyph, never its name in the slot
		-- (the name is in KitItemName for tooltips and detail cards).
		local s = math.floor(math.min(self.w, self.h) * 0.62)
		self.image = Art.Icon(self.base.visual, Art.KindGlyph(catalogId), {
			(self.w - s) / 2,
			(self.h - s) / 2,
			s,
			s,
		}, { z = z, name = "Item", tint = "inkSoft", transparency = Art.STAND_IN_FADE, maxScale = self.maxScale })
		self.root:SetAttribute("KitStandIn", true)
	end
	self.root:SetAttribute("KitItemName", if catalogId then Art.ItemName(catalogId) else nil)
end

function ItemIcon:Destroy()
	self.base.maid:Clean()
end

return ItemIcon
