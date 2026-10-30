-- A role drawn as a picture (the HUD player card, the leaf emblem, the party
-- panel frame, the painted island map), so screens name roles, never sprites.
--
--   Kit.Picture.new(page, { rect = { 0, 0, 480, 480 }, role = "map.island" })

local Art = require(script.Parent.Art)
local Core = require(script.Parent.Core)
local Tokens = require(script.Parent.Tokens)

local Picture = {}
Picture.__index = Picture

-- props: rect | size, role, tint (colour token), exact (false: the sprite at
-- the rect, transparent margin inside), zIndex, name.
function Picture.new(parent: Instance, props)
	local nw, nh = Art.SizeOf(Art.ROLES[props.role] and Art.ROLES[props.role].sprite)
	local w, h = Core.Size(props, nw or 100, nh or 100)
	local base = Core.Root(parent, "Picture", props.role, props, w, h)
	local self = setmetatable({ root = base.root, base = base }, Picture)
	self.plate = Art.Plate(base.visual, props.role, w, h, {
		z = base.z,
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
