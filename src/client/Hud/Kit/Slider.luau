-- A slider (M03): dark track with the yellow fill up to the knob, a
-- parchment knob with leather corners, and the value in a small paper box to
-- its right. Every slider has this one look. Dragging (mouse or touch) or a
-- press on the track sets the value, snapped to `step`; with a gamepad, left /
-- right step it while it is selected.
--
-- In a scrolling list a touch first waits to see which way it goes
-- (KitModel.DragAxis, DRAG_SLOP screen px): sideways, the slider takes the drag
-- and the list stops scrolling until the finger lifts; up or down, the list
-- scrolls and the value stays; a tap sets the value where it lands. The mouse
-- drags at once (the wheel scrolls the list).
--
--   Kit.Slider.new(page, { rect = { 0, 40, 375, 34 }, min = 10, max = 100, step = 1, value = 50,
--       format = function(v) return ("%.1f"):format(v / 50) end, onChange = set })

local ContextActionService = game:GetService("ContextActionService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local KitModel = require(ReplicatedStorage.Shared.UI.KitModel)
local Art = require(script.Parent.Art)
local Core = require(script.Parent.Core)
local Interact = require(script.Parent.Interact)
local Motion = require(script.Parent.Motion)
local Tokens = require(script.Parent.Tokens)

local Slider = {}
Slider.__index = Slider

Slider.TRACK_H = 14
Slider.BOX_W = 74
-- The knob: the square parchment button with leather corners (sheet 03,
-- lk_button_square_paper, 60 × 58) drawn whole at its own aspect, never
-- 9-sliced or stretched, so its rim and corners keep their shape. It stands
-- KNOB_OVER px past the track above and below (14 + 2 × 8 = 30 tall); a
-- slider shorter than that keeps the knob inside its own height.
Slider.KNOB_ASPECT = 60 / 58
Slider.KNOB_OVER = 8
-- Screen px a touch in a scrolling list moves before it counts as a drag.
Slider.DRAG_SLOP = 10

local count = 0

-- props: rect | size, min, max, step, value, valueBox (true), boxWidth (74),
-- format(value) -> string, onChange(value), zIndex, name, selectable (true:
-- false keeps it out of gamepad selection, where a stepper beside it does the
-- job), touchBand (false: true grows the drag band to touchMin screen px tall
-- on touch screens, whatever the window's scale; the layout must leave room).
-- `knob` and `track` are still accepted for older callers but no longer change
-- the look: every slider draws the same track and knob.
function Slider.new(parent: Instance, props)
	local w, h = Core.Size(props, 375, 34)
	local base = Core.Root(parent, "Slider", "slider.track", props, w, h)
	local self = setmetatable({
		root = base.root,
		base = base,
		min = props.min or 0,
		max = props.max or 1,
		step = props.step,
		format = props.format,
		onChange = props.onChange,
	}, Slider)
	local boxW = if props.valueBox == false then 0 else (props.boxWidth or Slider.BOX_W)
	local trackW = w - (if boxW > 0 then boxW + 16 else 0)
	local th = Slider.TRACK_H
	local kh = math.min(th + Slider.KNOB_OVER * 2, h)
	local kw = math.floor(kh * Slider.KNOB_ASPECT + 0.5)
	self.trackW = trackW
	self.inset = kw / 2
	local trackRect = { 0, (h - th) / 2, trackW, th }
	self.track = Core.Make("Frame", {
		Name = "Track",
		BackgroundTransparency = 1,
		Position = UDim2.fromOffset(trackRect[1], trackRect[2]),
		Size = UDim2.fromOffset(trackW, th),
		ZIndex = base.z,
	}, base.visual)
	Art.Plate(self.track, "slider.track", trackW, th, { z = base.z })
	-- The full-length fill behind a clipping frame as wide as the value: cut at
	-- the knob, never squeezed.
	self.fill = Core.Make("Frame", {
		Name = "Fill",
		BackgroundTransparency = 1,
		ClipsDescendants = true,
		Position = UDim2.fromOffset(1, 1),
		Size = UDim2.fromOffset(trackW - 2, th - 2),
		ZIndex = base.z + 1,
	}, self.track)
	local fillPlate = Core.Make("Frame", {
		Name = "Plate",
		BackgroundTransparency = 1,
		Size = UDim2.fromOffset(trackW - 2, th - 2),
		ZIndex = base.z + 1,
	}, self.fill)
	Art.Plate(fillPlate, "slider.fill", trackW - 2, th - 2, { z = base.z + 1 })
	self.knob = Core.Make("Frame", {
		Name = "Knob",
		AnchorPoint = Vector2.new(0.5, 0.5),
		BackgroundTransparency = 1,
		Position = UDim2.fromOffset(0, h / 2),
		Size = UDim2.fromOffset(kw, kh),
		ZIndex = base.z + 3,
	}, base.visual)
	self.knobScale = Core.Make("UIScale", { Scale = 1 }, self.knob)
	self.knobPlate = Art.Plate(self.knob, "slider.knob", kw, kh, { z = base.z + 3 })
	if boxW > 0 then
		local box = Core.Make("Frame", {
			Name = "ValueBox",
			BackgroundTransparency = 1,
			Position = UDim2.fromOffset(w - boxW, (h - 32) / 2),
			Size = UDim2.fromOffset(boxW, 32),
			ZIndex = base.z,
		}, base.visual)
		Art.Plate(box, "field.value", boxW, 32, { z = base.z })
		self.valueLabel = Core.Label(box, {
			name = "Value",
			text = "",
			role = "value",
			align = "Center",
			scaled = true,
			rect = { 4, 0, boxW - 8, 31 },
			z = base.z + 1,
		})
	end
	-- The drag band covers the track and reaches above and below it for fingers.
	local band = math.max(kh, Tokens.Space("touchMin", 44))
	local hit = Core.Make("TextButton", {
		Name = "Hit",
		AutoButtonColor = false,
		BackgroundTransparency = 1,
		Position = UDim2.fromOffset(-kw / 2, (h - band) / 2),
		Size = UDim2.fromOffset(trackW + kw, band),
		Text = "",
		ZIndex = base.z + 8,
	}, base.root)
	self.hit = hit
	self.control = Interact.attach(base, {
		hit = hit,
		pressScale = false,
		selectable = props.selectable,
		render = function(state)
			self.knobPlate:Show(state)
			local grow = state == "pressed" or state == "hover" or state == "focused"
			Motion.Play(self.knobScale, "knob", { Scale = if grow then 1.1 else 1 })
		end,
	})
	local maid = base.maid
	if props.touchBand then
		-- On touch screens the band grows to touchMin screen px tall at the
		-- slider's real scale (as Interact grows other controls' pads).
		local function fitTouch()
			local shown = base.root.AbsoluteSize
			if not UserInputService.TouchEnabled or shown.X <= 0 or w <= 0 then
				return
			end
			local tall = math.max(band, Tokens.Space("touchMin", 44) / (shown.X / w))
			hit.Position = UDim2.fromOffset(-kw / 2, (h - tall) / 2)
			hit.Size = UDim2.fromOffset(trackW + kw, tall)
		end
		maid:Give(base.root:GetPropertyChangedSignal("AbsoluteSize"):Connect(fitTouch))
		fitTouch()
	end
	local dragging: InputObject? = nil
	-- A touch in a scrolling list that has not yet shown which way it goes, and
	-- the list whose scrolling is held off while this slider drags.
	local pending: { input: InputObject, x: number, y: number, list: ScrollingFrame, canvas: Vector2 }? = nil
	local held: ScrollingFrame? = nil
	local function release()
		if held then
			held.ScrollingEnabled = true
			held = nil
		end
	end
	maid:Give(release)
	maid:Give(hit.InputBegan:Connect(function(input: InputObject)
		local kind = input.UserInputType
		if self.control.flags.enabled == false then
			return
		end
		if kind == Enum.UserInputType.Touch then
			local list = hit:FindFirstAncestorWhichIsA("ScrollingFrame")
			if list and list.ScrollingEnabled then
				pending = {
					input = input,
					x = input.Position.X,
					y = input.Position.Y,
					list = list,
					canvas = list.CanvasPosition,
				}
				return
			end
		end
		if kind == Enum.UserInputType.MouseButton1 or kind == Enum.UserInputType.Touch then
			dragging = input
			self:_fromScreenX(input.Position.X)
		end
	end))
	maid:Give(UserInputService.InputChanged:Connect(function(input: InputObject)
		local wait = pending
		if wait and input == wait.input then
			local axis = KitModel.DragAxis(input.Position.X - wait.x, input.Position.Y - wait.y, Slider.DRAG_SLOP)
			if axis == "x" then
				-- Sideways: the slider takes the drag; the list stays where it was.
				pending = nil
				release()
				held = wait.list
				wait.list.ScrollingEnabled = false
				wait.list.CanvasPosition = wait.canvas
				dragging = input
				self:_fromScreenX(input.Position.X)
			elseif axis == "y" then
				-- Up or down: the list scrolls and the value stays.
				pending = nil
				self.control:_endPress()
			end
			return
		end
		if dragging == nil then
			return
		end
		if
			input.UserInputType == Enum.UserInputType.MouseMovement
			or (input.UserInputType == Enum.UserInputType.Touch and input == dragging)
		then
			self:_fromScreenX(input.Position.X)
		end
	end))
	maid:Give(UserInputService.InputEnded:Connect(function(input: InputObject)
		local wait = pending
		if wait and input == wait.input then
			-- A tap: the value goes where it landed.
			pending = nil
			self:_fromScreenX(input.Position.X)
		end
		if dragging and (input == dragging or input.UserInputType == Enum.UserInputType.MouseButton1) then
			dragging = nil
			release()
		end
	end))
	-- Gamepad: left / right step the value while selected, bound above the
	-- selection navigation and sunk; up / down still move between controls.
	count += 1
	local action = "KitSliderStep" .. count
	local function onStep(_, state, input)
		if state ~= Enum.UserInputState.Begin then
			return Enum.ContextActionResult.Sink
		end
		local key = input.KeyCode
		if key == Enum.KeyCode.DPadRight or key == Enum.KeyCode.Right then
			self:_nudge(1)
		elseif key == Enum.KeyCode.DPadLeft or key == Enum.KeyCode.Left then
			self:_nudge(-1)
		end
		return Enum.ContextActionResult.Sink
	end
	maid:Give(hit.SelectionGained:Connect(function()
		ContextActionService:BindActionAtPriority(
			action,
			onStep,
			false,
			Enum.ContextActionPriority.High.Value + 50,
			Enum.KeyCode.DPadLeft,
			Enum.KeyCode.DPadRight,
			Enum.KeyCode.Left,
			Enum.KeyCode.Right
		)
	end))
	local function unbind()
		ContextActionService:UnbindAction(action)
	end
	maid:Give(hit.SelectionLost:Connect(unbind))
	maid:Give(unbind)
	self:SetValue(props.value or self.min)
	return self
end

function Slider:_fromScreenX(screenX: number)
	local left = self.track.AbsolutePosition.X
	local width = self.track.AbsoluteSize.X
	if width <= 0 then
		return
	end
	local k = width / self.trackW
	local fraction = math.clamp((screenX - left - self.inset * k) / (width - self.inset * 2 * k), 0, 1)
	self:_change(self.min + (self.max - self.min) * fraction)
end

function Slider:_nudge(direction: number)
	local step = self.step or (self.max - self.min) / 20
	self:_change(self.value + direction * step)
end

function Slider:_change(raw: number)
	local value = KitModel.Snap(raw, self.min, self.max, self.step)
	if value ~= self.value then
		self:SetValue(value)
		if self.onChange then
			self.onChange(value)
		end
	end
end

-- Shows `value` (clamped and snapped) without calling onChange.
function Slider:SetValue(value: number)
	self.value = KitModel.Snap(value, self.min, self.max, self.step)
	self.root:SetAttribute("KitValue", self.value)
	local fraction = KitModel.Fraction(self.value, self.min, self.max)
	local x = self.inset + (self.trackW - self.inset * 2) * fraction
	self.knob.Position = UDim2.new(0, x, 0.5, 0)
	self.fill.Size = UDim2.fromOffset(math.max(0, x - 1), self.fill.Size.Y.Offset)
	if self.valueLabel then
		local text
		if self.format then
			text = self.format(self.value)
		elseif self.step and self.step >= 1 then
			text = ("%d"):format(self.value)
		else
			text = ("%.1f"):format(self.value)
		end
		self.valueLabel.Text = text
	end
end

function Slider:SetEnabled(enabled: boolean)
	self.control:SetEnabled(enabled)
end

function Slider:Destroy()
	self.base.maid:Clean()
end

return Slider
