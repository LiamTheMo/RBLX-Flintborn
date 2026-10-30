-- A window: the parchment frame with leather corners (lk_window_frame, 9-sliced
-- to any size), optional side clasps, a header and the close button.
--
-- Headers (design px from the window's top-left):
--   "banner"   (M02, M03, M06, M07) icon at 40, 14 (76 px), title at x 140 in
--              windowTitle, optional handwritten subtitle under it, the
--              underline rule at y 88 from x 127 to the close button.
--   "plaque"   (M05) the title on a paper plaque at the top left.
--   "centered" (M04) the title centred with ornament icons either side and a
--              full-width rule.
--
--   local window = Kit.Window.new(screen, { title = "Inventory", icon = "backpack", clasps = "right" })
--   local body = window:Body() -- the area under the header, inset by windowPad

local Art = require(script.Parent.Art)
local Core = require(script.Parent.Core)
local Divider = require(script.Parent.Divider)
local IconButton = require(script.Parent.IconButton)
local Text = require(script.Parent.Text)
local Tokens = require(script.Parent.Tokens)

local Window = {}
Window.__index = Window

export type Props = {
	title: string,
	icon: string?,
	subtitle: string?,
	header: string?,
	smallCaps: boolean?,
	clasps: (boolean | string)?,
	claspYs: { number }?,
	ornaments: { string }?,
	showClose: boolean?,
	onClose: (() -> ())?,
	rect: { number }?,
	size: { number }?,
	zIndex: number?,
}

-- `target` is a Kit.Screen (the window fills it and closes it) or a GuiObject
-- (then props.rect or props.size places the window).
function Window.new(target, props: Props)
	local parent, w, h, screen
	if type(target) == "table" and target.window then
		screen = target
		parent = target.window
		w, h = target.size[1], target.size[2]
	else
		parent = target
		w, h = Core.Size(props, 1000, 640)
	end
	local base = Core.Root(parent, "Window", "window.frame", props, w, h)
	local z = base.z
	local self = setmetatable({
		root = base.root,
		base = base,
		screen = screen,
		w = w,
		h = h,
		header = props.header or "banner",
	}, Window)
	self.frame = Art.Plate(base.visual, "window.frame", w, h, { z = z })

	-- Side clasps sit across the frame edge, centred on it.
	local clasps = props.clasps
	if clasps then
		local cw, ch = Art.SizeOf("lk_clasp_left")
		cw, ch = cw or 22, ch or 52
		local sides = if clasps == "left"
			then { "left" }
			elseif clasps == "right" then { "right" }
			else { "left", "right" }
		for _, side in sides do
			for index, fy in props.claspYs or { 0.2, 0.86 } do
				local x = if side == "left" then -cw / 2 + 3 else w - cw / 2 - 3
				local role = if side == "left" then "window.claspLeft" else "window.claspRight"
				local holder = Core.Make("Frame", {
					Name = "Clasp" .. side .. index,
					BackgroundTransparency = 1,
					Position = UDim2.fromOffset(x, h * fy - ch / 2),
					Size = UDim2.fromOffset(cw, ch),
					ZIndex = z + 1,
				}, base.visual)
				Art.Plate(holder, role, cw, ch, { z = z + 1 })
			end
		end
	end

	local closeSize = Tokens.Space("closeButton", 60)
	local closeInset = Tokens.Space("closeInset", 22)
	if props.showClose ~= false then
		self.close = IconButton.new(base.visual, {
			name = "Close",
			variant = "close",
			rect = { w - closeInset - closeSize, closeInset - 4, closeSize, closeSize },
			zIndex = z + 4,
			onPress = function()
				if props.onClose then
					props.onClose()
				elseif screen then
					screen:Close()
				end
			end,
		})
		if screen and screen.defaultSelection == nil then
			screen:SetDefaultSelection(self.close.control.hit)
		end
	end

	local header = self.header
	local titleZ = z + 3
	local bodyTop = Tokens.Space("windowHeaderH", 100)
	if header == "plaque" then
		local tw = Text.Width(props.title, "windowTitle") + 80
		local plaqueRect = { 44, 24, math.max(220, tw), 86 }
		local plaque = Core.Make("Frame", {
			Name = "TitlePlaque",
			BackgroundTransparency = 1,
			Position = UDim2.fromOffset(plaqueRect[1], plaqueRect[2]),
			Size = UDim2.fromOffset(plaqueRect[3], plaqueRect[4]),
			ZIndex = z + 2,
		}, base.visual)
		Art.Plate(plaque, "window.plaque", plaqueRect[3], plaqueRect[4], { z = z + 2 })
		self.title = Text.new(plaque, {
			name = "Title",
			rect = { 0, 0, plaqueRect[3], plaqueRect[4] - 4 },
			text = props.title,
			role = "windowTitle",
			align = "Center",
			zIndex = titleZ,
		})
		bodyTop = plaqueRect[2] + plaqueRect[4] + 10
	elseif header == "centered" then
		local tw = Text.Width(props.title, "windowTitle")
		local cx = w / 2
		self.title = Text.new(base.visual, {
			name = "Title",
			rect = { cx - tw / 2 - 10, 18, tw + 20, 60 },
			text = props.title,
			role = "windowTitle",
			align = "Center",
			zIndex = titleZ,
		})
		local ornaments = props.ornaments or { props.icon or "tree", props.icon or "tree" }
		local size = 56
		for index, id in ornaments do
			local x = if index == 1 then cx - tw / 2 - 20 - size else cx + tw / 2 + 20
			Art.Icon(base.visual, id, { x, 20, size, size }, { z = titleZ, name = "Ornament" .. index })
		end
		self.rule = Divider.new(base.visual, {
			name = "TitleRule",
			rect = { 60, 74, w - 120, 16 },
			variant = "rule",
			zIndex = z + 2,
		})
	else
		local iconSize = Tokens.Space("windowIcon", 76)
		local titleX = if props.icon then Tokens.Space("windowTitleX", 140) else 44
		if props.icon then
			self.icon = Art.Icon(
				base.visual,
				props.icon,
				{ 40, 12, iconSize, iconSize },
				{ z = titleZ, name = "HeaderIcon" }
			)
		end
		local titleW = w - titleX - closeInset - closeSize - 20
		local hasSub = props.subtitle ~= nil
		self.title = Text.new(base.visual, {
			name = "Title",
			rect = { titleX, if hasSub then 14 else 24, titleW, if hasSub then 50 else 54 },
			text = props.title,
			role = "windowTitle",
			smallCaps = props.smallCaps,
			caps = if props.smallCaps then false else nil,
			zIndex = titleZ,
		})
		if hasSub then
			self.subtitle = Text.new(base.visual, {
				name = "Subtitle",
				rect = { titleX + 2, 62, titleW, 26 },
				text = props.subtitle :: string,
				role = "subtitleHand",
				zIndex = titleZ,
			})
		end
		local ruleX = titleX - 13
		self.rule = Divider.new(base.visual, {
			name = "TitleRule",
			rect = { ruleX, 80, w - ruleX - closeInset - closeSize - 8, 16 },
			variant = "header",
			zIndex = z + 2,
		})
	end

	local pad = Tokens.Space("windowPad", 24)
	self.body = Core.Make("Frame", {
		Name = "Body",
		BackgroundTransparency = 1,
		Position = UDim2.fromOffset(pad, bodyTop),
		Size = UDim2.fromOffset(w - pad * 2, h - bodyTop - pad),
		ZIndex = z + 2,
	}, base.visual)
	self.bodyRect = { pad, bodyTop, w - pad * 2, h - bodyTop - pad }
	return self
end

-- The content frame under the header ({x, y, w, h} in self.bodyRect).
function Window:Body(): Frame
	return self.body
end

function Window:SetTitle(text: string)
	self.title:SetText(text)
end

function Window:Destroy()
	if self.close then
		self.close:Destroy()
	end
	self.base.maid:Clean()
end

return Window
