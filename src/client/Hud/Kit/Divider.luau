-- Rules and dividers (sheets 09, 14): "rule" a thin line with diamond ends,
-- "ornate" a line with a centre diamond (dialog titles), "diamond" a heavier
-- rule, "vertical" a column divider. The art keeps its natural thickness,
-- centred on the rect's mid-line. "ink" (a thin dark line: section headers,
-- title underlines) and "hairline" (a faint line between list rows) are the
-- plain rules most mockup screens draw.
--
--   Kit.Divider.new(body, { rect = { 0, 300, 400, 16 }, variant = "ornate" })

local Art = require(script.Parent.Art)
local Core = require(script.Parent.Core)
local Tokens = require(script.Parent.Tokens)

local Divider = {}
Divider.__index = Divider

local ROLE = {
	rule = "divider.rule",
	header = "divider.rule",
	ornate = "divider.ornate",
	diamond = "divider.diamond",
	vertical = "divider.vertical",
	ink = "divider.ink",
	hairline = "divider.hairline",
}

-- props: rect | size, variant ("rule" | "ornate" | "diamond" | "vertical" |
-- "header" | "ink" | "hairline"), and for ink and hairline: thickness (px,
-- default 2), color (token), fade (true: the ends taper, as the M02 title rule).
-- A vertical ink or hairline rule is a rect taller than it is wide.
function Divider.new(parent: Instance, props)
	local variant = props.variant or "rule"
	local role = ROLE[variant] or ROLE.rule
	local w, h = Core.Size(props, 300, 16)
	local base = Core.Root(parent, "Divider", role, props, w, h)
	if Art.ROLES[role].native then
		-- A plain line centred in the rect.
		local vertical = h > w
		local thick = props.thickness or 2
		local line = Core.Make("Frame", {
			Name = "Line",
			AnchorPoint = Vector2.new(0.5, 0.5),
			BackgroundColor3 = Tokens.Color(props.color or Art.ROLES[role].fill),
			BorderSizePixel = 0,
			Position = UDim2.fromScale(0.5, 0.5),
			Size = if vertical then UDim2.new(0, thick, 1, 0) else UDim2.new(1, 0, 0, thick),
			ZIndex = base.z,
		}, base.visual)
		if props.fade then
			Core.Make("UIGradient", {
				Rotation = if vertical then 90 else 0,
				Transparency = NumberSequence.new({
					NumberSequenceKeypoint.new(0, 1),
					NumberSequenceKeypoint.new(0.04, 0),
					NumberSequenceKeypoint.new(0.96, 0),
					NumberSequenceKeypoint.new(1, 1),
				}),
			}, line)
		end
		return setmetatable({ root = base.root, base = base, line = line }, Divider)
	end
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
