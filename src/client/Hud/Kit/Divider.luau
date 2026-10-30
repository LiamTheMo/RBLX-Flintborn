-- Rules and dividers (sheets 09, 14): "rule" a thin line with diamond ends,
-- "ornate" a line with a centre diamond (dialog titles), "diamond" a heavier
-- rule, "vertical" a column divider. The art keeps its natural thickness,
-- centred on the rect's mid-line.
--
--   Kit.Divider.new(body, { rect = { 0, 300, 400, 16 }, variant = "ornate" })

local Art = require(script.Parent.Art)
local Core = require(script.Parent.Core)

local Divider = {}
Divider.__index = Divider

local ROLE = {
	rule = "divider.rule",
	header = "divider.rule",
	ornate = "divider.ornate",
	diamond = "divider.diamond",
	vertical = "divider.vertical",
}

-- props: rect | size, variant ("rule" | "ornate" | "diamond" | "vertical" | "header").
function Divider.new(parent: Instance, props)
	local variant = props.variant or "rule"
	local role = ROLE[variant] or ROLE.rule
	local w, h = Core.Size(props, 300, 16)
	local base = Core.Root(parent, "Divider", role, props, w, h)
	local sprite = Art.ROLES[role].sprite
	local nw, nh = Art.SizeOf(sprite)
	local vertical = variant == "vertical"
	local thick = if vertical then (nw or 18) else (nh or 15)
	local rect = if vertical then { (w - thick) / 2, 0, thick, h } else { 0, (h - thick) / 2, w, thick }
	local plate = Art.Plate(base.visual, role, rect[3], rect[4], { rect = rect, z = base.z })
	if variant == "ornate" then
		-- The centre diamond is not sliced: stretch the whole rule.
		for _, child in plate.holder:GetChildren() do
			if child:IsA("ImageLabel") then
				child.ScaleType = Enum.ScaleType.Stretch
			end
		end
	end
	return setmetatable({ root = base.root, base = base, plate = plate }, Divider)
end

function Divider:Destroy()
	self.base.maid:Clean()
end

return Divider
