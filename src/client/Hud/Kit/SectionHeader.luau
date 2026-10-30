-- A section header (M04 "YOUR PARTY 1/8", M06 "RECIPES"): an optional icon,
-- capital heading text, an optional count beside it and the rule at its foot.
--
--   Kit.SectionHeader.new(column, { rect = { 16, 10, 330, 34 }, text = "Your Party", icon = "party", count = "1/8" })

local Art = require(script.Parent.Art)
local Core = require(script.Parent.Core)
local Divider = require(script.Parent.Divider)
local Text = require(script.Parent.Text)

local SectionHeader = {}
SectionHeader.__index = SectionHeader

-- props: rect | size, text, icon, count, rule (default true), zIndex, name.
function SectionHeader.new(parent: Instance, props)
	local w, h = Core.Size(props, 300, 34)
	local base = Core.Root(parent, "SectionHeader", "header.section", props, w, h)
	local self = setmetatable({ root = base.root, base = base }, SectionHeader)
	local x = 0
	if props.icon then
		local s = math.floor(h * 0.95)
		self.icon = Art.Icon(base.visual, props.icon, { 0, (h - s) / 2 - 3, s, s }, { z = base.z + 1, name = "Icon" })
		x = s + 10
	end
	local textW = Text.Width(props.text or "", "sectionHeader")
	self.label = Core.Label(base.visual, {
		name = "Label",
		text = props.text,
		role = "sectionHeader",
		rect = { x, 0, math.min(textW + 4, w - x), h - 6 },
		z = base.z + 1,
	})
	if props.count then
		self.count = Core.Label(base.visual, {
			name = "Count",
			text = props.count,
			role = "sectionHeader",
			rect = { x + textW + 22, 0, 120, h - 6 },
			z = base.z + 1,
		})
	end
	if props.rule ~= false then
		self.rule = Divider.new(base.visual, { name = "Rule", rect = { 0, h - 9, w, 16 }, variant = "header", zIndex = base.z })
	end
	return self
end

function SectionHeader:SetText(text: string)
	Core.SetText(self.label, text)
end

function SectionHeader:SetCount(text: string)
	if self.count then
		Core.SetText(self.count, text)
	end
end

function SectionHeader:Destroy()
	self.base.maid:Clean()
end

return SectionHeader
