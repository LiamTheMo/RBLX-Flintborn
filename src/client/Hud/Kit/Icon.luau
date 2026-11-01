-- An icon by id: lk_icon_<id> (menu, status and world icons, sheets 06, 11, 16,
-- 17) or lk_glyph_<id> (flat glyphs, sheet 03), fitted into its rect, and never
-- drawn larger than its art (MAX_SCALE design px per pixel of the art that draws
-- at that size, its high-resolution copy included: Art.Capped; a big box, the
-- Journal's illustration, centres it at that size). Before upload it is a glyph
-- in ink. Item art goes through Kit.ItemIcon.
--
--   Kit.Icon.new(row, { rect = { 8, 8, 40, 40 }, icon = "backpack" })
--   Kit.Icon.new(plate, { rect = r, icon = "play", tint = "cream" })

local Art = require(script.Parent.Art)
local Core = require(script.Parent.Core)

local Icon = {}
Icon.__index = Icon

-- The largest an icon is drawn: design px per pixel of its art (Art.Capped).
Icon.MAX_SCALE = 1

-- props: rect | size, icon (id), tint (colour token), zIndex, name, maxScale
-- (default MAX_SCALE; false draws the art at the full rect).
function Icon.new(parent: Instance, props)
	local w, h = Core.Size(props, 40, 40)
	local base = Core.Root(parent, "Icon", "icon." .. tostring(props.icon), props, w, h)
	local self = setmetatable({ root = base.root, base = base, w = w, h = h, tint = props.tint, image = nil }, Icon)
	self.maxScale = if props.maxScale == false then nil else props.maxScale or Icon.MAX_SCALE
	self:SetIcon(props.icon)
	return self
end

function Icon:SetIcon(id: string?)
	if self.image then
		self.image:Destroy()
		self.image = nil
	end
	self.id = id
	self.root:SetAttribute("KitRole", "icon." .. tostring(id))
	if id then
		self.image = Art.Icon(
			self.base.visual,
			id,
			{ 0, 0, self.w, self.h },
			{ tint = self.tint, z = self.base.z + 1, maxScale = self.maxScale }
		)
	end
end

function Icon:Destroy()
	self.base.maid:Clean()
end

return Icon
