-- Toasts (sheet 13 "Quest Complete" / "Item Received"): a banner plate with an
-- emblem icon, a title, an optional line and a ✕. Kit.Toast.Show stacks up to
-- three in the KitToasts gui at the top centre below the top bar (the oldest
-- goes first), slides each in 24 px with a fade and closes it after `duration`.
-- Kit.Toast.new draws one card in place (galleries, notice cards).
--
--   Kit.Toast.Show({ kind = "quest", title = "Quest Complete", text = "Gather Supplies", duration = 4 })

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local HudModel = require(ReplicatedStorage.Shared.UI.HudModel)
local KitModel = require(ReplicatedStorage.Shared.UI.KitModel)
local Art = require(script.Parent.Art)
local Button = require(script.Parent.Button)
local Core = require(script.Parent.Core)
local Modal = require(script.Parent.Modal)
local Motion = require(script.Parent.Motion)
local Scale = require(script.Parent.Scale)
local Tokens = require(script.Parent.Tokens)

local Toast = {}
Toast.__index = Toast

-- Emblem icon per kind.
Toast.ICONS = { quest = "scroll", item = "gift", info = "exclamation", warn = "warning" }

-- The line's text size (design px, the body role's 15; boosted on phones). It
-- never shrinks: a long line wraps to a second line and the card grows.
Toast.LINE_SIZE = 15
Toast.LINE_MAX = 2
-- The action buttons' height and the row they take under the text when the
-- line does not fit beside them.
Toast.ACTION_H = 40
Toast.ACTION_ROW = 48

-- The width (design px, at most `room`) that wraps `text` onto two lines of
-- about the same length: the word break that makes the longer line shortest,
-- so a second line never holds one orphaned word. A wrap at this width puts
-- the same words on the first line (every longer first line is wider).
function Toast.BalancedWidth(text: string, room: number): number
	local words = string.split(text, " ")
	local best = room
	for k = 1, #words - 1 do
		local first = table.concat(words, " ", 1, k)
		local second = table.concat(words, " ", k + 1)
		local wide = math.max(
			Core.TextWidth(first, "body", Toast.LINE_SIZE),
			Core.TextWidth(second, "body", Toast.LINE_SIZE)
		) * 1.04
		if wide < best then
			best = wide
		end
	end
	return math.min(room, math.ceil(best) + 2)
end

-- The card's layout for `props` at width `w` and base height `h0` (the toast
-- token height): where the text ends, whether the actions sit beside the text
-- or on a row under it, how many lines the line takes and the card's height.
function Toast.Layout(props, w: number, h0: number)
	local s = math.floor(h0 * 0.62)
	local x = 22 + s + 14
	local closeRight = w - (if props.hideClose then 20 else 44)
	local actions = props.actions or {}
	local bw = props.actionWidth or 96
	local actionsW = if #actions > 0 then #actions * bw + (#actions - 1) * 8 else 0
	local lineW = if props.text then Core.TextWidth(props.text, "body", Toast.LINE_SIZE) * 1.04 else 0
	local besideRight = closeRight - (if actionsW > 0 then actionsW + 8 else 0)
	local below = actionsW > 0
		and (props.actionsBelow == true or (props.actionsBelow == nil and lineW > besideRight - x))
	local right = if below then closeRight else besideRight
	local lines = if props.text and lineW > right - x then Toast.LINE_MAX else 1
	-- Two lines wrap at the balanced width, not the full room.
	local wrapW = if lines > 1 then Toast.BalancedWidth(props.text, right - x) else right - x
	local px = Toast.LINE_SIZE * Core.TextBoost("body", Toast.LINE_SIZE)
	local extra = (lines - 1) * math.ceil(px * 1.3)
	local textH = h0 + extra
	return {
		emblem = s,
		x = x,
		right = right,
		wrapW = wrapW,
		closeRight = closeRight,
		actionWidth = bw,
		below = below,
		lines = lines,
		textH = textH,
		h = textH + (if below then Toast.ACTION_ROW else 0),
	}
end

-- props: rect | size (430 × 84; the height is the card's least: a two-line
-- line and a row of actions add to it, see .h), kind, title, text, icon,
-- actions ({{label, onPress, variant}}: beside the text when the line fits
-- there at its size, else on a row under it, right-aligned, e.g. Accept
-- (primary) and Decline (secondary)), actionsBelow (true / false forces it),
-- actionWidth (96), hideClose (no ✕: the actions answer it), onPress,
-- onClose, zIndex, name.
function Toast.new(parent: Instance, props)
	local w, h0 = Core.Size(props, Tokens.Space("toastW", 430), Tokens.Space("toastH", 84))
	local layout = Toast.Layout(props, w, h0)
	local h = layout.h
	local placed = table.clone(props)
	if props.rect then
		placed.rect = { props.rect[1], props.rect[2], w, h }
	else
		placed.size = { w, h }
	end
	local base = Core.Root(parent, "Toast", "toast.frame", placed, w, h)
	base.root:SetAttribute("KitVariant", props.kind or "info")
	local self = setmetatable(
		{ root = base.root, base = base, onClose = props.onClose, actions = {}, w = w, h = h, layout = layout },
		Toast
	)
	self.plate = Art.Plate(base.visual, "toast.frame", w, h, { z = base.z })
	local s = layout.emblem
	local textH = layout.textH
	Art.Icon(
		base.visual,
		props.icon or Toast.ICONS[props.kind or "info"] or "exclamation",
		{ 22, (textH - s) / 2, s, s },
		{
			z = base.z + 1,
			name = "Emblem",
		}
	)
	local x = layout.x
	local right = layout.right
	-- Right to left: the first action is the rightmost.
	local actionRight = layout.closeRight
	local actionY = if layout.below then textH - 6 else (textH - Toast.ACTION_H) / 2
	for index, action in props.actions or {} do
		local bw = layout.actionWidth
		table.insert(
			self.actions,
			Button.new(base.visual, {
				name = "Action" .. index,
				sizeClass = "s",
				label = action.label,
				variant = action.variant or "primary",
				rect = { actionRight - bw, actionY, bw, Toast.ACTION_H },
				zIndex = base.z + 2,
				onPress = action.onPress,
			})
		)
		actionRight -= bw + 8
	end
	local hasText = props.text ~= nil
	self.title = Core.Label(base.visual, {
		name = "Title",
		text = props.title or "",
		role = "itemTitle",
		caps = true,
		size = 22,
		scaled = true,
		rect = if hasText then { x, h0 * 0.16, right - x, h0 * 0.4 } else { x, 0, right - x, textH },
		z = base.z + 1,
	})
	if hasText then
		-- At its size (never shrunk below it): a second line when it is long,
		-- "…" only past that.
		self.text = Core.Label(base.visual, {
			name = "Line",
			text = props.text,
			role = "body",
			size = Toast.LINE_SIZE,
			wrap = layout.lines > 1,
			rect = { x, h0 * 0.54, layout.wrapW, h0 * 0.32 + (textH - h0) },
			z = base.z + 1,
		})
		self.text.TextTruncate = Enum.TextTruncate.AtEnd
	end
	-- The ✕ mark is 22 px; its button pads it to touchMin.
	local c = 22
	local cx, cy = w - c / 2 - 18, 14 + c / 2
	local mark = Core.Make("Frame", {
		Name = "CloseMark",
		BackgroundTransparency = 1,
		Position = UDim2.fromOffset(cx - c / 2, cy - c / 2),
		Size = UDim2.fromOffset(c, c),
		Visible = not props.hideClose,
		ZIndex = base.z + 3,
	}, base.visual)
	Art.Plate(mark, "mark.cross", c, c, { z = base.z + 3 })
	self.close = Core.Make("TextButton", {
		Visible = not props.hideClose,
		Name = "Close",
		AutoButtonColor = false,
		AnchorPoint = Vector2.new(0.5, 0.5),
		BackgroundTransparency = 1,
		Position = UDim2.fromOffset(cx, cy),
		Size = UDim2.fromOffset(c, c),
		Text = "",
		ZIndex = base.z + 4,
	}, base.visual)
	-- The ✕'s hit area: at least touchMin SCREEN px at the toast's real scale.
	local function fitClose()
		local shown = base.root.AbsoluteSize.X
		local k = if shown > 0 then shown / w else 1
		local side = math.max(c, Tokens.Space("touchMin", 44) / k)
		self.close.Size = UDim2.fromOffset(side, side)
	end
	base.maid:Give(base.root:GetPropertyChangedSignal("AbsoluteSize"):Connect(fitClose))
	fitClose()
	base.maid:Give(self.close.Activated:Connect(function()
		if self.onClose then
			self.onClose(self)
		end
	end))
	if props.onPress then
		local body = Core.Make("TextButton", {
			Name = "Press",
			AutoButtonColor = false,
			BackgroundTransparency = 1,
			Size = UDim2.new(1, -60, 1, 0),
			Text = "",
			ZIndex = base.z + 2,
		}, base.visual)
		base.maid:Give(body.Activated:Connect(function()
			props.onPress(self)
		end))
	end
	return self
end

function Toast:Destroy()
	for _, action in self.actions do
		action:Destroy()
	end
	self.base.maid:Clean()
end

-- The managed column ----------------------------------------------------------------

local column: Frame? = nil
local relayout: (() -> ())? = nil
local columnScale = 1
local avoid: GuiObject? = nil

-- The column's top (screen px): below the top bar, below a part the column must
-- keep clear of (Toast.Avoid: the server notice card), and below the title
-- band of an open window, so toasts never cover a window's title.
function Toast.LaneTop(gui: GuiBase2d): number
	local y = Scale.WindowTop(gui) + 8
	if avoid and avoid.Parent and avoid.Visible then
		y = math.max(y, avoid.AbsolutePosition.Y + avoid.AbsoluteSize.Y + 8)
	end
	local top = Modal.Top()
	if top and top.holder and top.scale then
		-- Below the open window when one toast fits under it; else below its
		-- title and tab band (Screen.toastClear design px, default 180).
		local windowTop = top.holder.AbsolutePosition.Y
		local windowBottom = windowTop + top.holder.AbsoluteSize.Y
		local toastH = Tokens.Space("toastH", 84) * columnScale
		if gui.AbsoluteSize.Y - windowBottom >= toastH + 16 then
			return math.max(y, windowBottom + 8)
		end
		local clear = (top.toastClear or Tokens.Space("toastClear", 180)) * top.scale.Scale
		if windowTop + clear > y then
			y = windowTop + clear
		end
	end
	return y
end

-- Keeps the toast column below `object` (nil clears it), e.g. the notice card.
function Toast.Avoid(object: GuiObject?)
	avoid = object
	if relayout then
		relayout()
	end
end
local shown: { any } = {}

local function host(): Frame
	if column and column.Parent then
		return column
	end
	local gui = Core.Make("ScreenGui", {
		Name = "KitToasts",
		DisplayOrder = Tokens.Order("toasts"),
		IgnoreGuiInset = true,
		ResetOnSpawn = false,
		ZIndexBehavior = Enum.ZIndexBehavior.Sibling,
	}, Players.LocalPlayer:FindFirstChildOfClass("PlayerGui"))
	local root = Core.Make("Frame", {
		Name = "Column",
		AnchorPoint = Vector2.new(0.5, 0),
		BackgroundTransparency = 1,
		Position = UDim2.new(0.5, 0, 0, Scale.WindowTop(gui) + 8),
		Size = UDim2.fromOffset(Tokens.Space("toastW", 430), 600),
	}, gui)
	local scale = Core.Make("UIScale", {}, root)
	local function fit()
		local size = gui.AbsoluteSize
		local ref = Tokens.Data.reference
		local k = HudModel.HudScale(size.X, size.Y, ref.width, ref.height, Tokens.Scale("hudMin"), 1.2, nil)
		if Scale.IsSmallTouch() then
			k = math.max(k, Scale.PhoneFloor("overlay"))
		end
		scale.Scale = k
		columnScale = k
		root.Position = UDim2.new(0.5, 0, 0, Toast.LaneTop(gui))
	end
	gui:GetPropertyChangedSignal("AbsoluteSize"):Connect(fit)
	Modal.OnChanged(fit)
	Scale.OnFormFactorChanged(fit)
	relayout = fit
	fit()
	Core.Make("UIListLayout", {
		Padding = UDim.new(0, Tokens.Space("toastGap", 10)),
		SortOrder = Enum.SortOrder.LayoutOrder,
		HorizontalAlignment = Enum.HorizontalAlignment.Center,
	}, root)
	column = root
	return root
end

local order = 0

-- Every faded part of a card and the transparency it rests at: images, text,
-- strokes and filled frames. A toast fades part by part (no CanvasGroup: a
-- group draws its text through a texture, soft under the column's fractional
-- UIScale).
local FADE_PROPS = {
	ImageLabel = "ImageTransparency",
	TextLabel = "TextTransparency",
	UIStroke = "Transparency",
	Frame = "BackgroundTransparency",
}
function Toast.FadeParts(root: Instance): { { object: Instance, prop: string, rest: number } }
	local parts = {}
	for _, object in root:GetDescendants() do
		local prop = FADE_PROPS[object.ClassName]
		if prop then
			local rest = (object :: any)[prop]
			if type(rest) == "number" and rest < 1 then
				table.insert(parts, { object = object, prop = prop, rest = rest })
			end
		end
	end
	return parts
end

local function fade(parts, key: string, show: boolean)
	for _, part in parts do
		if part.object.Parent then
			Motion.Play(part.object, key, { [part.prop] = if show then part.rest else 1 })
		end
	end
end

-- Shows a toast. props as Toast.new plus duration (seconds, default 4).
-- Returns a handle with Close().
function Toast.Show(props)
	local parent = host()
	if relayout then
		relayout()
	end
	order += 1
	local w, h = Tokens.Space("toastW", 430), Tokens.Space("toastH", 84)
	local slot = Core.Make("Frame", {
		Name = "Toast" .. order,
		BackgroundTransparency = 1,
		LayoutOrder = order,
		Size = UDim2.fromOffset(w, h),
	}, parent)
	local handle = {}
	local card
	local parts
	local closed = false
	function handle.Close()
		if closed then
			return
		end
		closed = true
		local index = table.find(shown, handle)
		if index then
			table.remove(shown, index)
		end
		fade(parts, "toastOut", false)
		Motion.Play(
			card.root,
			"toastOut",
			{ Position = UDim2.fromOffset(0, -Tokens.Space("toastSlide", 24)) },
			function()
				card:Destroy()
				slot:Destroy()
			end
		)
	end
	local cardProps = table.clone(props)
	cardProps.rect = { 0, 0, w, h }
	cardProps.onClose = function()
		handle.Close()
		if props.onClose then
			props.onClose()
		end
	end
	card = Toast.new(slot, cardProps)
	handle.toast = card
	-- A long line or a row of actions makes the card taller.
	slot.Size = UDim2.fromOffset(w, card.h)
	parts = Toast.FadeParts(card.root)
	for _, part in parts do
		Motion.Set(part.object, { [part.prop] = 1 })
	end
	card.root.Position = UDim2.fromOffset(0, -Tokens.Space("toastSlide", 24))
	Motion.Play(card.root, "toastIn", { Position = UDim2.fromOffset(0, 0) })
	fade(parts, "toastIn", true)
	for _, old in KitModel.PushToast(shown, handle, Tokens.Space("toastMax", 3)) do
		old.Close()
	end
	task.delay(props.duration or 4, handle.Close)
	return handle
end

return Toast
