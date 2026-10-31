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

-- props: rect | size (430 × 84), kind, title, text, icon, actions ({{label,
-- onPress, variant}}; two fit beside the text, e.g. Accept (primary) and
-- Decline (secondary)), actionWidth (96), hideClose (no ✕: the actions answer
-- it), onPress, onClose, zIndex, name.
function Toast.new(parent: Instance, props)
	local w, h = Core.Size(props, Tokens.Space("toastW", 430), Tokens.Space("toastH", 84))
	local base = Core.Root(parent, "Toast", "toast.frame", props, w, h)
	base.root:SetAttribute("KitVariant", props.kind or "info")
	local self = setmetatable({ root = base.root, base = base, onClose = props.onClose, actions = {} }, Toast)
	self.plate = Art.Plate(base.visual, "toast.frame", w, h, { z = base.z })
	local s = math.floor(h * 0.62)
	Art.Icon(base.visual, props.icon or Toast.ICONS[props.kind or "info"] or "exclamation", { 22, (h - s) / 2, s, s }, {
		z = base.z + 1,
		name = "Emblem",
	})
	local x = 22 + s + 14
	local right = w - (if props.hideClose then 20 else 44)
	for index, action in props.actions or {} do
		local bw = props.actionWidth or 96
		table.insert(
			self.actions,
			Button.new(base.visual, {
				name = "Action" .. index,
				sizeClass = "s",
				label = action.label,
				variant = action.variant or "primary",
				rect = { right - bw, (h - 40) / 2, bw, 40 },
				zIndex = base.z + 2,
				onPress = action.onPress,
			})
		)
		right -= bw + 8
	end
	local hasText = props.text ~= nil
	self.title = Core.Label(base.visual, {
		name = "Title",
		text = props.title or "",
		role = "itemTitle",
		caps = true,
		size = 22,
		scaled = true,
		rect = if hasText then { x, h * 0.16, right - x, h * 0.4 } else { x, 0, right - x, h },
		z = base.z + 1,
	})
	if hasText then
		self.text = Core.Label(base.visual, {
			name = "Line",
			text = props.text,
			role = "body",
			scaled = true,
			rect = { x, h * 0.54, right - x, h * 0.32 },
			z = base.z + 1,
		})
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

-- Shows a toast. props as Toast.new plus duration (seconds, default 4).
-- Returns a handle with Close().
function Toast.Show(props)
	local parent = host()
	if relayout then
		relayout()
	end
	order += 1
	local w, h = Tokens.Space("toastW", 430), Tokens.Space("toastH", 84)
	-- A CanvasGroup so the whole card fades as one.
	local slot = Core.Make("CanvasGroup", {
		Name = "Toast" .. order,
		BackgroundTransparency = 1,
		GroupTransparency = 1,
		LayoutOrder = order,
		Size = UDim2.fromOffset(w, h),
	}, parent)
	local handle = {}
	local card
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
		Motion.Play(card.root, "toastOut", { Position = UDim2.fromOffset(0, -Tokens.Space("toastSlide", 24)) })
		Motion.Play(slot, "toastOut", { GroupTransparency = 1 }, function()
			card:Destroy()
			slot:Destroy()
		end)
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
	card.root.Position = UDim2.fromOffset(0, -Tokens.Space("toastSlide", 24))
	Motion.Play(card.root, "toastIn", { Position = UDim2.fromOffset(0, 0) })
	Motion.Play(slot, "toastIn", { GroupTransparency = 0 })
	for _, old in KitModel.PushToast(shown, handle, Tokens.Space("toastMax", 3)) do
		old.Close()
	end
	task.delay(props.duration or 4, handle.Close)
	return handle
end

return Toast
