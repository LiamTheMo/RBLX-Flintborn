-- An on/off switch (sheet 09): the paper pill with its knob left, or the green
-- pill with the knob right.
--
--   Kit.Toggle.new(row, { rect = { 300, 8, 89, 49 }, on = true, onToggle = set })

local Art = require(script.Parent.Art)
local Core = require(script.Parent.Core)
local Interact = require(script.Parent.Interact)

local Toggle = {}
Toggle.__index = Toggle

-- props: rect | size (default 89 × 49), on, onToggle(on), zIndex, name.
function Toggle.new(parent: Instance, props)
	local w, h = Core.Size(props, 89, 49)
	local base = Core.Root(parent, "Toggle", "toggle.off", props, w, h)
	local self = setmetatable({ root = base.root, base = base, on = props.on == true }, Toggle)
	self.offPlate = Art.Plate(base.visual, "toggle.off", w, h, { z = base.z })
	self.onPlate = Art.Plate(base.visual, "toggle.on", w, h, { z = base.z })
	self.control = Interact.attach(base, {
		onPress = function()
			self:Set(not self.on)
			if props.onToggle then
				props.onToggle(self.on)
			end
		end,
		render = function(state)
			self.offPlate.holder.Visible = not self.on
			self.onPlate.holder.Visible = self.on
			self.offPlate:Show(state)
			self.onPlate:Show(state)
		end,
	})
	self:Set(self.on)
	return self
end

function Toggle:Set(on: boolean)
	self.on = on == true
	self.root:SetAttribute("KitChecked", self.on)
	self.root:SetAttribute("KitRole", if self.on then "toggle.on" else "toggle.off")
	self.control:Refresh()
end

function Toggle:SetEnabled(enabled: boolean)
	self.control:SetEnabled(enabled)
end

function Toggle:Destroy()
	self.base.maid:Clean()
end

return Toggle
