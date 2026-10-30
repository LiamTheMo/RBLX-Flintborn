-- The HUD currency pill (sheet 07; M01): plaque, coin or gem icon and the
-- amount with thousands separators, counting up when it changes. Pressable
-- when onPress is given (opens the Shop).
--
--   local coins = Kit.CurrencyPill.new(top, { rect = { 0, 0, 112, 46 }, currency = "coins", value = 2450, onPress = shop })
--   coins:SetValue(2600)

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local HudModel = require(ReplicatedStorage.Shared.UI.HudModel)
local Art = require(script.Parent.Art)
local Core = require(script.Parent.Core)
local Interact = require(script.Parent.Interact)
local Motion = require(script.Parent.Motion)

local CurrencyPill = {}
CurrencyPill.__index = CurrencyPill

CurrencyPill.ICONS = { coins = "coin", gems = "gem" }

-- props: rect | size, currency ("coins" | "gems"), value, textSize, iconSize,
-- onPress, zIndex, name.
function CurrencyPill.new(parent: Instance, props)
	local w, h = Core.Size(props, 112, 46)
	local base = Core.Root(parent, "CurrencyPill", "currency.pill", props, w, h)
	local self = setmetatable({ root = base.root, base = base, value = 0 }, CurrencyPill)
	self.plate = Art.Plate(base.visual, "currency.pill", w, h, { z = base.z })
	local s = props.iconSize or math.floor(h * 0.66)
	Art.Icon(base.visual, CurrencyPill.ICONS[props.currency or "coins"] or "coin", { 10, (h - s) / 2, s, s }, {
		z = base.z + 1,
		name = "Icon",
	})
	self.label = Core.Label(base.visual, {
		name = "Value",
		text = "",
		role = "currency",
		size = props.textSize,
		align = "Center",
		scaled = true,
		rect = { 10 + s + 4, 0, w - s - 24, h - 2 },
		z = base.z + 1,
	})
	self.counter = Core.Make("NumberValue", { Name = "Count", Value = 0 }, base.root)
	base.maid:Give(self.counter:GetPropertyChangedSignal("Value"):Connect(function()
		self.label.Text = HudModel.Thousands(self.counter.Value)
	end))
	if props.onPress then
		self.control = Interact.attach(base, {
			hoverScale = true,
			onPress = function()
				props.onPress(self)
			end,
			render = function(state)
				self.plate:Show(state)
			end,
		})
	end
	self:SetValue(props.value or 0, true)
	return self
end

-- Shows `value`, counting up (or down) unless `instant`.
function CurrencyPill:SetValue(value: number, instant: boolean?)
	self.value = value
	self.root:SetAttribute("KitValue", value)
	if instant then
		Motion.Set(self.counter, { Value = value })
		self.label.Text = HudModel.Thousands(value)
	else
		Motion.Play(self.counter, "count", { Value = value })
	end
end

function CurrencyPill:Destroy()
	self.base.maid:Clean()
end

return CurrencyPill
