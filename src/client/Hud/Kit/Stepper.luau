-- A quantity stepper (sheet 09; M06): − and + buttons around a value box.
-- At a limit the button is disabled. An optional "All" button sets the max.
--
--   Kit.Stepper.new(footer, { rect = { 120, 10, 160, 48 }, min = 1, max = 10, value = 1, onChange = set })

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local KitModel = require(ReplicatedStorage.Shared.UI.KitModel)
local Art = require(script.Parent.Art)
local Button = require(script.Parent.Button)
local Core = require(script.Parent.Core)
local IconButton = require(script.Parent.IconButton)

local Stepper = {}
Stepper.__index = Stepper

-- props: rect | size, min, max, value, step (1), allLabel (adds a button that
-- sets the max), buttons ("paper" default | "leather": the M06 leather − / +),
-- valueSize, onChange(value), zIndex, name.
function Stepper.new(parent: Instance, props)
	local w, h = Core.Size(props, 160, 48)
	local base = Core.Root(parent, "Stepper", "field.value", props, w, h)
	local self = setmetatable({
		root = base.root,
		base = base,
		min = props.min or 1,
		max = props.max or 99,
		step = props.step or 1,
		onChange = props.onChange,
	}, Stepper)
	local bw = h
	local allW = if props.allLabel then 70 else 0
	local fieldW = w - bw * 2 - 16 - (if allW > 0 then allW + 8 else 0)
	local leather = props.buttons == "leather"
	self.minus = IconButton.new(base.visual, {
		name = "Minus",
		variant = if leather then "leather" else "minus",
		icon = if leather then "minus" else nil,
		rect = { 0, 0, bw, h },
		zIndex = base.z + 1,
		onPress = function()
			self:_change(self.value - self.step)
		end,
	})
	local field = Core.Make("Frame", {
		Name = "Field",
		BackgroundTransparency = 1,
		Position = UDim2.fromOffset(bw + 8, 0),
		Size = UDim2.fromOffset(fieldW, h),
		ZIndex = base.z,
	}, base.visual)
	Art.Plate(field, "field.value", fieldW, h, { z = base.z })
	self.label = Core.Label(field, {
		name = "Value",
		text = "",
		role = "itemTitle",
		size = props.valueSize,
		align = "Center",
		scaled = true,
		rect = { 4, 2, fieldW - 8, h - 6 },
		z = base.z + 1,
	})
	self.plus = IconButton.new(base.visual, {
		name = "Plus",
		variant = if leather then "leather" else "plus",
		icon = if leather then "plus" else nil,
		rect = { bw + 16 + fieldW, 0, bw, h },
		zIndex = base.z + 1,
		onPress = function()
			self:_change(self.value + self.step)
		end,
	})
	if props.allLabel then
		self.all = Button.new(base.visual, {
			name = "All",
			variant = "secondary",
			sizeClass = "s",
			label = props.allLabel,
			rect = { w - allW, 0, allW, h },
			zIndex = base.z + 1,
			onPress = function()
				self:_change(self.max)
			end,
		})
	end
	self:SetValue(props.value or self.min)
	return self
end

function Stepper:_change(value: number)
	local v = KitModel.Snap(value, self.min, math.max(self.min, self.max), self.step)
	if v ~= self.value then
		self:SetValue(v)
		if self.onChange then
			self.onChange(v)
		end
	end
end

-- Shows `value` (clamped) without calling onChange; buttons at a limit disable.
function Stepper:SetValue(value: number)
	self.value = KitModel.Snap(value, self.min, math.max(self.min, self.max), self.step)
	self.root:SetAttribute("KitValue", self.value)
	self.label.Text = tostring(self.value)
	self.minus:SetEnabled(self.value > self.min)
	self.plus:SetEnabled(self.value < self.max)
	if self.all then
		self.all:SetEnabled(self.value < self.max)
	end
end

-- Changes the limits (materials owned changed) and re-clamps.
function Stepper:SetRange(min: number, max: number)
	self.min, self.max = min, max
	self:SetValue(self.value)
end

function Stepper:Destroy()
	self.minus:Destroy()
	self.plus:Destroy()
	if self.all then
		self.all:Destroy()
	end
	self.base.maid:Clean()
end

return Stepper
