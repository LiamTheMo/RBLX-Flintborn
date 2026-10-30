-- A checkbox with its label and an optional grey description under it (sheet
-- 09; M03). "box" is the paper box with a dark tick; "gold" tints the ticked box
-- gold as M03 draws it; "tile" is the quest objective's check tile (sheet 12).
-- The whole row is the touch area.
--
--   Kit.Checkbox.new(page, { rect = { 0, 200, 360, 50 }, label = "Show Damage Numbers",
--       description = "Numbers pop up over what you hit", checked = true, onToggle = set })

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local KitModel = require(ReplicatedStorage.Shared.UI.KitModel)
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
	ring = { "check.ringOff", "check.ringOn" },
}

-- props: rect | size, label, description, checked, variant ("box" | "gold" |
-- "tile" | "ring": the quest objective's round check), boxSize (default: row
-- height, at most 36), boxX (px), textSize, descriptionSize, readOnly (shows
-- the value, takes no input: objectives), onToggle(checked), zIndex, name.
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
		Position = UDim2.fromOffset(props.boxX or 0, top),
		Size = UDim2.fromOffset(box, box),
		ZIndex = base.z + 1,
	}, base.visual)
	self.off = Art.Plate(holder, roles[1], box, box, { z = base.z + 1 })
	self.on = Art.Plate(holder, roles[2], box, box, {
		z = base.z + 1,
		tint = if variant == "gold" then Tokens.Color("checkTint") else nil,
	})
	if variant == "ring" then
		-- The ring's done state carries a check mark over the filled ring.
		local m = math.floor(box * 0.6)
		Art.Plate(self.on.holder, "mark.check", m, m, { z = base.z + 2, rect = { (box - m) / 2, (box - m) / 2, m, m } })
	end
	local x = if props.label then (props.boxX or 0) + box + 18 else 0
	if props.label then
		self.label = Core.Label(base.visual, {
			name = "Label",
			text = props.label,
			role = "rowLabel",
			size = props.textSize,
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
			size = props.descriptionSize,
			scaled = true,
			rect = { x, box * 0.6, w - x, h - box * 0.6 },
			z = base.z + 1,
		})
	end
	local function render(state)
		self.off.holder.Visible = not self.checked
		self.on.holder.Visible = self.checked
		self.off:Show(state)
		self.on:Show(state)
		if self.label then
			self.label.TextColor3 = Tokens.Color(if state == "disabled" then "muted" else "inkLabel")
		end
	end
	if props.readOnly then
		self.control = Checkbox._static(base, render)
	else
		self.control = Interact.attach(base, {
			pressScale = false,
			onPress = function()
				self:SetChecked(not self.checked)
				if props.onToggle then
					props.onToggle(self.checked)
				end
			end,
			render = render,
		})
	end
	return self
end

-- A read-only checkbox's stand-in controller: it draws (DebugState still
-- works) but takes no input and is not selectable.
function Checkbox._static(base, render)
	local flags = { enabled = true }
	local control = { flags = flags }
	function control:Refresh()
		local state = KitModel.ResolveState(flags, base.root:GetAttribute("DebugState"))
		base.root:SetAttribute("KitState", state)
		render(state)
	end
	function control:SetEnabled(enabled: boolean)
		flags.enabled = enabled
		control:Refresh()
	end
	base.maid:Give(base.root:GetAttributeChangedSignal("DebugState"):Connect(function()
		control:Refresh()
	end))
	control:Refresh()
	return control
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
