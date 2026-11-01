-- A role drawn as a picture (the HUD player card, the leaf emblem, the party
-- panel frame, the painted island map), so screens name roles, never sprites.
-- Where the picture is magnified, its sprite's high-resolution copy draws (the
-- island map's 2040 px tiles), at the same size.
--
--   Kit.Picture.new(page, { rect = { 0, 0, 480, 480 }, role = "map.island" })

local Art = require(script.Parent.Art)
local Core = require(script.Parent.Core)
local Tokens = require(script.Parent.Tokens)

local Picture = {}
Picture.__index = Picture

-- props: rect | size, role, tint (colour token), exact (false: the sprite at
-- the rect, transparent margin inside), zIndex, name, maxScale (a picture that
-- is not 9-sliced is drawn at no more than this many design px per pixel of its
-- sharpest art, centred: Art.Capped; default none).
function Picture.new(parent: Instance, props)
	local sprite = Art.ROLES[props.role] and Art.ROLES[props.role].sprite
	local nw, nh = Art.SizeOf(sprite)
	local w, h = Core.Size(props, nw or 100, nh or 100)
	local base = Core.Root(parent, "Picture", props.role, props, w, h)
	local self = setmetatable({ root = base.root, base = base }, Picture)
	local rect = nil
	if props.maxScale and sprite and Art.SliceScale(sprite, w, h) == nil then
		local capped = Art.Capped(sprite, { 0, 0, w, h }, props.maxScale)
		if capped[3] ~= w or capped[4] ~= h then
			rect = capped
		end
	end
	self.plate = Art.Plate(base.visual, props.role, if rect then rect[3] else w, if rect then rect[4] else h, {
		z = base.z,
		rect = rect,
		exact = props.exact,
		tint = if props.tint then Tokens.Color(props.tint) else nil,
	})
	return self
end

-- Draws the role in a state ("disabled" dims it).
function Picture:SetState(state: string)
	self.plate:Show(state)
	self.root:SetAttribute("KitState", state)
end

function Picture:Destroy()
	self.base.maid:Clean()
end

return Picture
