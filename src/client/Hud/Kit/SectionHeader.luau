-- A section header (M04 "YOUR PARTY 1/8", M06 "RECIPES"): an optional icon,
-- capital heading text, an optional count beside it and the rule at its foot.
--
--   Kit.SectionHeader.new(column, { rect = { 16, 10, 330, 34 }, text = "Your Party", icon = "party", count = "1/8" })

local Art = require(script.Parent.Art)
local Core = require(script.Parent.Core)
local Divider = require(script.Parent.Divider)
local Scale = require(script.Parent.Scale)
local Text = require(script.Parent.Text)
local Tokens = require(script.Parent.Tokens)

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
	self.x, self.w, self.h = x, w, h
	self.size = props.textSize
	self.countGap = props.countGap or 22
	-- Never truncated (STYLE_GUIDE §4.6): the label keeps its (phone-boosted)
	-- size when the text fits the width, else it shrinks to fit (`_fit`).
	self.label = Core.Label(base.visual, {
		name = "Label",
		text = props.text,
		role = "sectionHeader",
		size = self.size,
		rect = { x, 0, w - x, h - 6 },
		z = base.z + 1,
	})
	self.label.TextTruncate = Enum.TextTruncate.None
	if props.count then
		self.count = Core.Label(base.visual, {
			name = "Count",
			text = props.count,
			role = "sectionHeader",
			size = self.size,
			rect = { x, 0, 120, h - 6 },
			z = base.z + 1,
		})
		self.count.TextTruncate = Enum.TextTruncate.None
	end
	self:_fit()
	-- The phone boost changes with the form factor: fit again after it.
	base.maid:Give(Scale.OnFormFactorChanged(function()
		task.defer(function()
			if self.label.Parent then
				self:_fit()
			end
		end)
	end))
	if props.rule ~= false then
		local variant = if type(props.rule) == "string" then props.rule else "ink"
		local native = variant == "ink" or variant == "hairline"
		local rect = props.ruleRect or (if native then { 0, h - 3, w, 2 } else { 0, h - 9, w, 16 })
		self.rule = Divider.new(base.visual, { name = "Rule", rect = rect, variant = variant, zIndex = base.z })
	end
	return self
end

-- Sizes the label (and the count after it) to the header's width: the role
-- size (or textSize), boosted on phones, or smaller when that does not fit.
-- The width is measured with a little room to spare (the heavy face runs a
-- touch wider than measured), so the text is never cut.
function SectionHeader:_fit()
	local style = Tokens.TextStyle("sectionHeader")
	local size = self.size or style.size
	local shown = size * Core.TextBoost("sectionHeader", size)
	local room = self.w - self.x
	local textW = Text.Width(self.label.Text, "sectionHeader", self.size) * 1.04
	local countW = 0
	if self.count and self.count.Text ~= "" then
		countW = Text.Width(self.count.Text, "sectionHeader", self.size) * 1.04 + self.countGap
	end
	local k = math.min(1, room / math.max(textW + 2 + countW, 1), (self.h - 6) / math.max(shown, 1))
	self.label.TextSize = shown * k
	self.label.Size = UDim2.fromOffset(math.min(room, math.ceil(textW * k) + 4), self.h - 6)
	if self.count then
		self.count.TextSize = shown * k
		-- A right-aligned count was pinned to the header's end by its owner (the
		-- event card's timer): it keeps its place.
		if self.count.TextXAlignment ~= Enum.TextXAlignment.Right then
			self.count.Position = UDim2.fromOffset(self.x + (textW + self.countGap) * k, 0)
		end
	end
end

function SectionHeader:SetText(text: string)
	Core.SetText(self.label, text)
	self:_fit()
end

function SectionHeader:SetCount(text: string)
	if self.count then
		Core.SetText(self.count, text)
		self:_fit()
	end
end

function SectionHeader:Destroy()
	self.base.maid:Clean()
end

return SectionHeader
