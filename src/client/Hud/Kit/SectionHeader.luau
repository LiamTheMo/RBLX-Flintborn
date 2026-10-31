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

-- props: rect | size, text, icon (an icon id; "ink:people" for the mockups'
-- flat glyphs), iconRect {x, y, w, h}, count, countGap (22), textSize,
-- textX, rule (true | false | a Divider variant; default "ink"), ruleRect
-- {x, y, w, h}, zIndex, name.
function SectionHeader.new(parent: Instance, props)
	local w, h = Core.Size(props, 300, 34)
	local base = Core.Root(parent, "SectionHeader", "header.section", props, w, h)
	local self = setmetatable({ root = base.root, base = base }, SectionHeader)
	local x = 0
	if props.icon then
		local s = math.floor(h * 0.95)
		local rect = props.iconRect or { 0, (h - s) / 2 - 3, s, s }
		self.icon = Art.Icon(base.visual, props.icon, rect, { z = base.z + 1, name = "Icon" })
		x = rect[1] + rect[3] + 10
	end
	x = props.textX or x
	local size = props.textSize
	local textW = Text.Width(props.text or "", "sectionHeader", size)
	self.label = Core.Label(base.visual, {
		name = "Label",
		text = props.text,
		role = "sectionHeader",
		size = size,
		-- The whole width is the label's, so a heavy face never truncates.
		rect = { x, 0, if props.count then math.min(textW * 1.06 + 8, w - x) else w - x, h - 6 },
		z = base.z + 1,
	})
	if props.count then
		self.count = Core.Label(base.visual, {
			name = "Count",
			text = props.count,
			role = "sectionHeader",
			size = size,
			rect = { x + textW * 1.04 + (props.countGap or 22), 0, 120, h - 6 },
			z = base.z + 1,
		})
	end
	if props.rule ~= false then
		local variant = if type(props.rule) == "string" then props.rule else "ink"
		local native = variant == "ink" or variant == "hairline"
		local rect = props.ruleRect or (if native then { 0, h - 3, w, 2 } else { 0, h - 9, w, 16 })
		self.rule = Divider.new(base.visual, { name = "Rule", rect = rect, variant = variant, zIndex = base.z })
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
