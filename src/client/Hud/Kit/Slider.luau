-- A slider (M03): dark track with the yellow fill up to the knob, a paper
-- knob, and the value in a small paper box to its right. Dragging (mouse or
-- touch) or a press on the track sets the value, snapped to `step`; with a
-- gamepad, left / right step it while it is selected.
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

local count = 0

-- props: rect | size, min, max, step, value, valueBox (true), format(value)
-- -> string, knob ("plate" | "round"), track ("dark" | "paper"),
-- onChange(value), zIndex, name.
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
	local knobRound = props.knob == "round"
	local kw, kh = if knobRound then 30 else 23, if knobRound then 30 else 26
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
	Art.Plate(
		self.track,
		if props.track == "paper" then "slider.trackPaper" else "slider.track",
		trackW,
		th,
		{ z = base.z }
	)
	self.fill = Core.Make("Frame", {
		Name = "Fill",
		BackgroundTransparency = 1,
		Position = UDim2.fromOffset(1, 1),
		Size = UDim2.fromOffset(trackW - 2, th - 2),
		ZIndex = base.z + 1,
	}, self.track)
	Art.Plate(self.fill, "slider.fill", trackW - 2, th - 2, { z = base.z + 1 })
	self.knob = Core.Make("Frame", {
		Name = "Knob",
		AnchorPoint = Vector2.new(0.5, 0.5),
		BackgroundTransparency = 1,
		Position = UDim2.fromOffset(0, h / 2),
		Size = UDim2.fromOffset(kw, kh),
		ZIndex = base.z + 3,
	}, base.visual)
	self.knobScale = Core.Make("UIScale", { Scale = 1 }, self.knob)
	self.knobPlate =
		Art.Plate(self.knob, if knobRound then "slider.knobRound" else "slider.knob", kw, kh, { z = base.z + 3 })
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
	self.control = Interact.attach(base, {
		hit = hit,
		pressScale = false,
		render = function(state)
			self.knobPlate:Show(state)
			local grow = state == "pressed" or state == "hover" or state == "focused"
			Motion.Play(self.knobScale, "knob", { Scale = if grow then 1.1 else 1 })
		end,
	})
	local maid = base.maid
	local dragging: InputObject? = nil
	maid:Give(hit.InputBegan:Connect(function(input: InputObject)
		local kind = input.UserInputType
		if self.control.flags.enabled == false then
			return
		end
		if kind == Enum.UserInputType.MouseButton1 or kind == Enum.UserInputType.Touch then
			dragging = input
			self:_fromScreenX(input.Position.X)
		end
	end))
	maid:Give(UserInputService.InputChanged:Connect(function(input: InputObject)
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
		if dragging and (input == dragging or input.UserInputType == Enum.UserInputType.MouseButton1) then
			dragging = nil
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
	self.fill.Size = UDim2.fromOffset(math.max(Slider.TRACK_H, x), Slider.TRACK_H - 2)
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
