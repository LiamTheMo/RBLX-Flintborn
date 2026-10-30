-- A checkbox with its label and an optional grey description under it (sheet
-- 09; M03). "box" is the paper box with a dark tick; "gold" tints the ticked box
-- gold as M03 draws it; "tile" is the quest objective's check tile (sheet 12).
-- The whole row is the touch area.
--
--   Kit.Checkbox.new(page, { rect = { 0, 200, 360, 50 }, label = "Show Damage Numbers",
--       description = "Numbers pop up over what you hit", checked = true, onToggle = set })

local Art = require(script.Parent.Art)
local Core = require(script.Parent.Core)
local Interact = require(script.Parent.Interact)
local Tokens = require(script.Parent.Tokens)

local Checkbox = {}
Checkbox.__index = Checkbox

local ROLES = {
	box = { "checkbox.off", "checkbox.on" },
	gold = { "checkbox.off", "checkbox.on" },
	tile = { "check.tileOff", "check.tileOn" },
}

-- props: rect | size, label, description, checked, variant ("box" | "gold" |
-- "tile"), boxSize (default: row height, at most 36), onToggle(checked),
-- zIndex, name.
function Checkbox.new(parent: Instance, props)
	local variant = props.variant or "box"
	local roles = ROLES[variant] or ROLES.box
	local w, h = Core.Size(props, 320, 40)
	local base = Core.Root(parent, "Checkbox", roles[1], props, w, h)
	local self =
		setmetatable({ root = base.root, base = base, checked = props.checked == true, roles = roles }, Checkbox)
	local box = props.boxSize or math.min(h, 36)
	local top = if props.description then 2 else (h - box) / 2
	local holder = Core.Make("Frame", {
		Name = "Box",
		BackgroundTransparency = 1,
		Position = UDim2.fromOffset(0, top),
		Size = UDim2.fromOffset(box, box),
		ZIndex = base.z + 1,
	}, base.visual)
	self.off = Art.Plate(holder, roles[1], box, box, { z = base.z + 1 })
	self.on = Art.Plate(holder, roles[2], box, box, {
		z = base.z + 1,
		tint = if variant == "gold" then Tokens.Color("checkTint") else nil,
	})
	local x = if props.label then box + 18 else 0
	if props.label then
		self.label = Core.Label(base.visual, {
			name = "Label",
			text = props.label,
			role = "rowLabel",
			scaled = true,
			rect = { x, 0, w - x, if props.description then box * 0.6 else h },
			z = base.z + 1,
		})
	end
	if props.description then
		self.description = Core.Label(base.visual, {
			name = "Description",
			text = props.description,
			role = "small",
			scaled = true,
			rect = { x, box * 0.6, w - x, h - box * 0.6 },
			z = base.z + 1,
		})
	end
	self.control = Interact.attach(base, {
		pressScale = false,
		onPress = function()
			self:SetChecked(not self.checked)
			if props.onToggle then
				props.onToggle(self.checked)
			end
		end,
		render = function(state)
			self.off.holder.Visible = not self.checked
			self.on.holder.Visible = self.checked
			self.off:Show(state)
			self.on:Show(state)
			if self.label then
				self.label.TextColor3 = Tokens.Color(if state == "disabled" then "muted" else "inkLabel")
			end
		end,
	})
	return self
end

function Checkbox:SetChecked(checked: boolean)
	self.checked = checked == true
	self.root:SetAttribute("KitChecked", self.checked)
	self.control:Refresh()
end

function Checkbox:SetEnabled(enabled: boolean)
	self.control:SetEnabled(enabled)
end

function Checkbox:Destroy()
	self.base.maid:Clean()
end

return Checkbox
