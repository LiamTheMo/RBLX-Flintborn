-- Panels inside windows (sheets 01, 10, 12; M04 and M06 columns):
--   "inset"  thin rounded inset border on parchment (columns, detail card)
--   "card"   parchment card with leather corners
--   "plaque" paper title plaque with leather corners (M05 "Shattered Crater")
--   "plain"  no art (layout only)
-- An optional title draws a Kit.SectionHeader at the top; `scroll` puts a
-- Kit.Scroll under it. :Content() is where the panel's rows go.
--
--   local column = Kit.Panel.new(body, { rect = { 0, 0, 360, 450 }, title = "Your Party", icon = "party" })
--   Kit.ListRow.new(column:Content(), { size = { 330, 52 }, title = "LiamTheMo" })

local Art = require(script.Parent.Art)
local Core = require(script.Parent.Core)
local Scroll = require(script.Parent.Scroll)
local SectionHeader = require(script.Parent.SectionHeader)
local Text = require(script.Parent.Text)

local Panel = {}
Panel.__index = Panel

local ROLE = { inset = "panel.inset", card = "panel.card", plaque = "window.plaque", plain = nil }

-- props: rect | size, variant, title, icon, count, text (centred plaque text),
-- textRole, pad (content inset, default 16), scroll, zIndex, name.
function Panel.new(parent: Instance, props)
	local variant = props.variant or "inset"
	local role = ROLE[variant]
	local w, h = Core.Size(props, 360, 400)
	local base = Core.Root(parent, "Panel", role or "panel.plain", props, w, h)
	local self = setmetatable({ root = base.root, base = base, w = w, h = h }, Panel)
	if role then
		self.plate = Art.Plate(base.visual, role, w, h, { z = base.z })
	end
	local pad = props.pad or 16
	local top = pad
	if props.title then
		self.header = SectionHeader.new(base.visual, {
			name = "Header",
			rect = { pad, 12, w - pad * 2, 36 },
			text = props.title,
			icon = props.icon,
			count = props.count,
			zIndex = base.z + 1,
		})
		top = 12 + 36 + 10
	end
	if props.text then
		self.label = Text.new(base.visual, {
			name = "Label",
			rect = { pad, 0, w - pad * 2, h - 4 },
			text = props.text,
			role = props.textRole or "detailTitle",
			align = "Center",
			scaled = true,
			zIndex = base.z + 1,
		})
	end
	local rect = { pad, top, w - pad * 2, h - top - pad }
	if props.scroll then
		self.scroll = Scroll.new(base.visual, { rect = rect, zIndex = base.z + 1, contentHeight = props.contentHeight })
		self.content = self.scroll:Content()
	else
		self.content = Core.Make("Frame", {
			Name = "Content",
			BackgroundTransparency = 1,
			Position = UDim2.fromOffset(rect[1], rect[2]),
			Size = UDim2.fromOffset(rect[3], rect[4]),
			ZIndex = base.z + 1,
		}, base.visual)
	end
	self.contentRect = rect
	return self
end

function Panel:Content(): GuiObject
	return self.content
end

function Panel:Destroy()
	if self.scroll then
		self.scroll:Destroy()
	end
	self.base.maid:Clean()
end

return Panel
