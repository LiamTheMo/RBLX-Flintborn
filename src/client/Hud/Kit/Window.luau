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
	ornamentSize: number?,
	ornamentGap: number?,
	iconRect: { number }?,
	iconSize: number?,
	titleX: number?,
	titleY: number?,
	titleRect: { number }?,
	titleSize: number?,
	smallCapsSizes: { number }?,
	subtitleRect: { number }?,
	subtitleSize: number?,
	rule: (boolean | string)?,
	ruleVariant: string?,
	ruleRect: { number }?,
	ruleFade: boolean?,
	ruleColor: string?,
	closeRect: { number }?,
	plaqueRect: { number }?,
	bodyTop: number?,
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
				local x = if side == "left" then -cw / 2 else w - cw / 2
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
	local closeRect = props.closeRect or { w - closeInset - closeSize, closeInset - 4, closeSize, closeSize }
	if props.showClose ~= false then
		self.close = IconButton.new(base.visual, {
			name = "Close",
			variant = "close",
			rect = closeRect,
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
	local titleSize = props.titleSize
	local bodyTop = props.bodyTop or Tokens.Space("windowHeaderH", 100)
	-- The underline: props.rule false hides it, "full" spans the window,
	-- or a Divider variant ("ink" default; "rule" the diamond-ended art).
	local function underline(defaultRect)
		if props.rule == false then
			return
		end
		local variant = props.ruleVariant
			or (if type(props.rule) == "string" and props.rule ~= "full" then props.rule else "ink")
		local native = variant == "ink" or variant == "hairline"
		local rect = props.ruleRect
		if rect == nil then
			rect = if props.rule == "full" then { 40, defaultRect[2], w - 80, defaultRect[4] } else defaultRect
			if native then
				rect = { rect[1], rect[2] + rect[4] / 2 - 1, rect[3], 2 }
			end
		end
		self.rule = Divider.new(base.visual, {
			name = "TitleRule",
			rect = rect,
			variant = variant,
			fade = props.ruleFade ~= false,
			color = props.ruleColor,
			zIndex = z + 2,
		})
	end
	if header == "plaque" then
		local tw = Text.Width(props.title, "windowTitle", titleSize) + 80
		local plaqueRect = props.plaqueRect or { 44, 24, math.max(220, tw), 86 }
		local plaque = Core.Make("Frame", {
			Name = "TitlePlaque",
			BackgroundTransparency = 1,
			Position = UDim2.fromOffset(plaqueRect[1], plaqueRect[2]),
			Size = UDim2.fromOffset(plaqueRect[3], plaqueRect[4]),
			ZIndex = z + 2,
		}, base.visual)
		Art.Plate(plaque, "window.plaque", plaqueRect[3], plaqueRect[4], { z = z + 2 })
		self.plaque = plaque
		self.title = Text.new(plaque, {
			name = "Title",
			rect = props.titleRect or { 0, 0, plaqueRect[3], plaqueRect[4] - 4 },
			text = props.title,
			role = "windowTitle",
			textSize = titleSize,
			align = "Center",
			zIndex = titleZ,
		})
		if props.bodyTop == nil then
			bodyTop = plaqueRect[2] + plaqueRect[4] + 10
		end
	elseif header == "centered" then
		local tw = Text.Width(props.title, "windowTitle", titleSize)
		local cx = w / 2
		local ty = props.titleY or 18
		self.title = Text.new(base.visual, {
			name = "Title",
			-- Room to spare: the heavy face runs a little wider than measured.
			rect = props.titleRect or { cx - tw / 2 - 40, ty, tw + 80, 60 },
			text = props.title,
			role = "windowTitle",
			textSize = titleSize,
			align = "Center",
			zIndex = titleZ,
		})
		local ornaments = props.ornaments or { props.icon or "tree", props.icon or "tree" }
		local size = props.ornamentSize or 56
		local gap = props.ornamentGap or 20
		for index, id in ornaments do
			local x = if index == 1 then cx - tw / 2 - gap - size else cx + tw / 2 + gap
			Art.Icon(base.visual, id, { x, ty + 2, size, size }, { z = titleZ, name = "Ornament" .. index })
		end
		underline({ 60, ty + 56, w - 120, 16 })
	else
		local iconSize = props.iconSize or Tokens.Space("windowIcon", 76)
		local iconRect = props.iconRect or { 40, 12, iconSize, iconSize }
		local titleX = props.titleX or (if props.icon then Tokens.Space("windowTitleX", 140) else 44)
		if props.icon then
			self.icon = Art.Icon(base.visual, props.icon, iconRect, { z = titleZ, name = "HeaderIcon" })
		end
		local titleW = closeRect[1] - titleX - 20
		local hasSub = props.subtitle ~= nil
		self.title = Text.new(base.visual, {
			name = "Title",
			rect = props.titleRect or { titleX, if hasSub then 14 else 24, titleW, if hasSub then 50 else 54 },
			text = props.title,
			role = "windowTitle",
			textSize = titleSize,
			smallCaps = props.smallCaps,
			smallCapsSizes = props.smallCapsSizes,
			caps = if props.smallCaps then false else nil,
			zIndex = titleZ,
		})
		if hasSub then
			self.subtitle = Text.new(base.visual, {
				name = "Subtitle",
				rect = props.subtitleRect or { titleX + 2, 62, titleW, 26 },
				text = props.subtitle :: string,
				role = "subtitleHand",
				textSize = props.subtitleSize,
				zIndex = titleZ,
			})
		end
		local ruleX = titleX - 13
		underline({ ruleX, 80, closeRect[1] - 8 - ruleX, 16 })
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
