-- A confirm dialog (sheet 13): the dialog frame with its close ✕, a title over
-- an ornate rule, a body (wrapped text, or rows built by `build(body)`), and
-- CANCEL (parchment) and CONFIRM (leather) buttons. Kit.ConfirmDialog.Show puts
-- it in the KitDialog gui above the open window (Kit.Modal "dialog" layer:
-- Escape / B cancel). `holdSeconds` makes CONFIRM a press-and-hold with a
-- filling bar (rebirth). Kit.ConfirmDialog.new draws one in place.
--
--   local dialog = Kit.ConfirmDialog.Show({ title = "Take these into the run?", text = "Everything except ★ Permanent items can be lost.",
--       confirmLabel = "Enter", onConfirm = deploy })
--   dialog.SetBusy(true)

local Art = require(script.Parent.Art)
local Bar = require(script.Parent.Bar)
local Button = require(script.Parent.Button)
local Core = require(script.Parent.Core)
local Divider = require(script.Parent.Divider)
local IconButton = require(script.Parent.IconButton)
local Screen = require(script.Parent.Screen)
local Tokens = require(script.Parent.Tokens)

local ConfirmDialog = {}
ConfirmDialog.__index = ConfirmDialog

ConfirmDialog.SIZE = { 560, 330 }

-- props: rect | size, title, text, build(body: Frame, w, h), confirmLabel,
-- cancelLabel, danger, holdSeconds, onConfirm, onCancel, zIndex, name.
function ConfirmDialog.new(parent: Instance, props)
	local w, h = Core.Size(props, ConfirmDialog.SIZE[1], ConfirmDialog.SIZE[2])
	local base = Core.Root(parent, "ConfirmDialog", "dialog.frame", props, w, h)
	local z = base.z
	local self = setmetatable({ root = base.root, base = base, props = props, closed = false }, ConfirmDialog)
	Art.Plate(base.visual, "dialog.frame", w, h, { z = z })
	self.closeButton = IconButton.new(base.visual, {
		name = "Close",
		variant = "close",
		rect = { w - 64, 12, 50, 50 },
		zIndex = z + 4,
		onPress = function()
			self:_cancel()
		end,
	})
	Core.Label(base.visual, {
		name = "Title",
		text = props.title or "",
		role = "detailTitle",
		size = 32,
		caps = true,
		align = "Center",
		scaled = true,
		rect = { 84, 24, w - 168, 44 },
		z = z + 1,
	})
	Divider.new(base.visual, { name = "Rule", rect = { 60, 72, w - 120, 26 }, variant = "ornate", zIndex = z + 1 })
	local buttonH = 58
	local bodyRect = { 44, 104, w - 88, h - 104 - buttonH - 40 }
	self.body = Core.Make("Frame", {
		Name = "Body",
		BackgroundTransparency = 1,
		Position = UDim2.fromOffset(bodyRect[1], bodyRect[2]),
		Size = UDim2.fromOffset(bodyRect[3], bodyRect[4]),
		ZIndex = z + 1,
	}, base.visual)
	if props.build then
		props.build(self.body, bodyRect[3], bodyRect[4])
	elseif props.text then
		Core.Label(self.body, {
			name = "Text",
			text = props.text,
			role = "body",
			size = 18,
			align = "Center",
			wrap = true,
			rect = { 0, 0, bodyRect[3], bodyRect[4] },
			z = z + 1,
		})
	end
	local bw = math.min(220, (w - 88 - 24) / 2)
	local y = h - buttonH - 34
	self.cancel = Button.new(base.visual, {
		name = "Cancel",
		variant = "secondary",
		label = props.cancelLabel or "Cancel",
		rect = { w / 2 - 12 - bw, y, bw, buttonH },
		zIndex = z + 2,
		onPress = function()
			self:_cancel()
		end,
	})
	local hold = props.holdSeconds
	self.confirm = Button.new(base.visual, {
		name = "Confirm",
		variant = "primary",
		label = props.confirmLabel or "Confirm",
		icon = if props.danger then nil else "check_white",
		rect = { w / 2 + 12, y, bw, buttonH },
		zIndex = z + 2,
		onPress = if hold
			then nil
			else function()
				self:_confirm()
			end,
	})
	if hold then
		self:_holdToConfirm(hold, bw, buttonH)
	end
	self.defaultSelection = self.confirm.control.hit
	return self
end

-- Press-and-hold: a fill runs along the confirm button's foot while it is
-- held; letting go early resets it.
function ConfirmDialog:_holdToConfirm(seconds: number, bw: number, bh: number)
	local button = self.confirm
	local bar = Bar.new(button.base.visual, {
		name = "Hold",
		rect = { 18, bh - 16, bw - 36, 10 },
		fill = "orange",
		frame = "none",
		zIndex = button.base.z + 3,
	})
	self.holdBar = bar
	local holding = 0
	local hit = button.control.hit
	local maid = self.base.maid
	maid:Give(hit.InputBegan:Connect(function(input: InputObject)
		local kind = input.UserInputType
		if
			kind ~= Enum.UserInputType.MouseButton1
			and kind ~= Enum.UserInputType.Touch
			and input.KeyCode ~= Enum.KeyCode.ButtonA
		then
			return
		end
		holding += 1
		local serial = holding
		local started = os.clock()
		task.spawn(function()
			while holding == serial and not self.closed do
				local t = (os.clock() - started) / seconds
				bar:Set(t, true)
				if t >= 1 then
					holding += 1
					self:_confirm()
					return
				end
				task.wait()
			end
		end)
	end))
	maid:Give(hit.InputEnded:Connect(function()
		holding += 1
		bar:Set(0, true)
	end))
	maid:Give(hit.MouseLeave:Connect(function()
		holding += 1
		bar:Set(0, true)
	end))
end

function ConfirmDialog:_confirm()
	if self.closed or self.busy then
		return
	end
	if self.props.onConfirm then
		self.props.onConfirm(self)
	end
	if not self.busy and self.onDone then
		self.onDone()
	end
end

function ConfirmDialog:_cancel()
	if self.closed then
		return
	end
	if self.props.onCancel then
		self.props.onCancel(self)
	end
	if self.onDone then
		self.onDone()
	end
end

-- While busy both buttons show their busy state (a request in flight).
function ConfirmDialog:SetBusy(busy: boolean)
	self.busy = busy
	self.confirm:SetBusy(busy)
	self.cancel:SetEnabled(not busy)
end

function ConfirmDialog:Destroy()
	self.closed = true
	self.closeButton:Destroy()
	self.cancel:Destroy()
	self.confirm:Destroy()
	if self.holdBar then
		self.holdBar:Destroy()
	end
	self.base.maid:Clean()
end

-- Shows a dialog over everything (one at a time on the dialog layer).
-- Returns {Close, SetBusy, dialog}.
function ConfirmDialog.Show(props)
	local size = props.size or ConfirmDialog.SIZE
	local screen = Screen.new("KitDialog", { size = size, layer = "dialog", blur = false })
	local dialogProps = table.clone(props)
	dialogProps.size = size
	dialogProps.rect = nil
	local dialog = ConfirmDialog.new(screen.window, dialogProps)
	screen:SetDefaultSelection(dialog.defaultSelection)
	screen:Watch()
	local handle = { dialog = dialog, screen = screen }
	local function close()
		if dialog.closed then
			return
		end
		dialog.closed = true
		screen:Close()
		task.delay(Tokens.MotionTime("windowClose") + 0.05, function()
			dialog:Destroy()
			screen:Destroy()
		end)
	end
	dialog.onDone = close
	-- Closed from outside (a new window replaces everything): tidy up too.
	screen.Closed:Connect(close)
	-- Escape / B and the window's close: cancel.
	screen.Back = function()
		dialog:_cancel()
	end
	handle.Close = close
	handle.SetBusy = function(busy: boolean)
		dialog:SetBusy(busy)
	end
	screen:Open()
	return handle
end

return ConfirmDialog
