-- A catalog item's picture, from ItemInfo.Icon(catalogId) (the single
-- item-to-icon source; it may return a tint too), then lk_item_<CatalogId> /
-- item_<CatalogId>, then the `icon` prop; with none, the item's name in ink,
-- then a neutral glyph for the item's kind (KitItemName carries the name for
-- tooltips), so nothing reads blank and no slot prints text.
--
-- The picture is never drawn larger than its art (MAX_SCALE design px per pixel
-- of the sharpest art): in a big box (the Forge's 254 px picture, the Inventory
-- detail card) it is centred at that size instead of blurred.
--
--   Kit.ItemIcon.new(slot, { rect = { 10, 10, 70, 70 }, catalogId = "StoneAxe" })

local Art = require(script.Parent.Art)
local Core = require(script.Parent.Core)
local Tokens = require(script.Parent.Tokens)

local ItemIcon = {}
ItemIcon.__index = ItemIcon

-- The largest an item picture is drawn: design px per pixel of its art.
ItemIcon.MAX_SCALE = 1

-- props: rect | size, catalogId (or itemId), icon (an icon id shown untinted
-- only when ItemInfo has no art for the item), zIndex, name, maxScale
-- (default MAX_SCALE; false draws the art at the full box).
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
	-- ItemInfo.Icon is the one item-to-art source (owned with the item data);
	-- its optional tint recolours shared art (an ore drawn from the stone icon).
	local artIcon, tint = Art.ItemIcon(catalogId)
	local sprite = if artIcon then nil else Art.ItemSprite(catalogId)
	self.root:SetAttribute("KitRole", "item." .. tostring(artIcon or sprite or icon or catalogId))
	if artIcon or (sprite == nil and icon) then
		self.image = Art.Icon(self.base.visual, artIcon or icon :: string, { 0, 0, self.w, self.h }, {
			z = z,
			name = "Item",
			color = if artIcon then tint else nil,
			-- While the art is not served: a small letter, not a slot-filling one.
			standInScale = 0.45,
			maxScale = self.maxScale,
		})
	elseif sprite then
		local r = Art.Capped(sprite, { 0, 0, self.w, self.h }, self.maxScale)
		self.image = Art.Sprite(sprite, r[3], r[4], self.base.visual, {
			Name = "Item",
			Position = UDim2.fromOffset(r[1], r[2]),
			Size = if r[3] == self.w and r[4] == self.h then UDim2.fromScale(1, 1) else UDim2.fromOffset(r[3], r[4]),
			ZIndex = z,
			ScaleType = Enum.ScaleType.Fit,
		})
	elseif catalogId then
		-- No art for this item: a neutral kind glyph, never its name in the slot
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
