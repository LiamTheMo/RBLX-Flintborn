-- Text buttons (sheet 03): "primary" leather (EQUIP, APPLY, CLAIM), "secondary"
-- parchment (RESET, CANCEL), "play" the notched leather plaque (PLAY, CLOSE in
-- Party) and "playSecondary" its parchment twin. An optional icon sits left
-- of the label (lk_glyph_play / lk_glyph_check_white are white for leather).
-- States: normal, hover, pressed, disabled, busy (label "…", not interactive).
--
--   Kit.Button.new(card, { rect = { 14, 450, 270, 61 }, label = "Equip", onPress = equip })
--   local invite = Kit.Button.new(row, { size = { 108, 42 }, label = "Invite", sizeClass = "s" })
--   -- D18, an invite pending: invite:SetVariant("secondary"); invite:SetLabel("Invited"); invite:SetEnabled(false)

local Art = require(script.Parent.Art)
local Core = require(script.Parent.Core)
local Interact = require(script.Parent.Interact)
local Text = require(script.Parent.Text)
local Tokens = require(script.Parent.Tokens)

local Button = {}
Button.__index = Button

local ROLE = {
	primary = "button.primary",
	secondary = "button.secondary",
	play = "button.play",
	playSecondary = "button.playSecondary",
	flat = "button.flat",
}

-- Height and text role per size class.
Button.SIZES = {
	s = { h = 42, role = "buttonS" },
	m = { h = 58, role = "button" },
	l = { h = 76, role = "buttonL" },
}

local function onLeather(variant: string): boolean
	return variant == "primary" or variant == "play"
end

-- props: rect | size, label, variant, sizeClass ("s" | "m" | "l"), icon,
-- textRole, textSize, onPress, zIndex, name.
function Button.new(parent: Instance, props)
	local variant = props.variant or "primary"
	local class = Button.SIZES[props.sizeClass or "m"] or Button.SIZES.m
	local w, h = Core.Size(props, 220, class.h)
	local base = Core.Root(parent, "Button", ROLE[variant] or ROLE.primary, props, w, h)
	local self = setmetatable({ root = base.root, base = base, variant = variant, w = w, h = h }, Button)
	self.plate = Art.Plate(base.visual, ROLE[variant] or ROLE.primary, w, h, { z = base.z })
	local role = props.textRole or class.role
	local label = props.label or ""
	-- Text clear of the plate's rivets, centred with its icon.
	local iconSize = if props.icon then math.floor(h * 0.5) else 0
	local gap = if props.icon then 12 else 0
	local textW = math.min(Text.Width(label, role, props.textSize), w - 2 * math.max(16, h * 0.35) - iconSize - gap)
	local groupW = iconSize + gap + textW
	local left = (w - groupW) / 2
	if props.icon then
		self.icon = Art.Icon(base.visual, props.icon, { left, (h - iconSize) / 2, iconSize, iconSize }, {
			z = base.z + 2,
			name = "Icon",
		})
	end
	self.label = Core.Label(base.visual, {
		name = "Label",
		text = label,
		role = role,
		size = props.textSize,
		align = "Center",
		scaled = true,
		rect = { left + iconSize + gap, 0, textW, h - 3 },
		z = base.z + 2,
	})
	self.text = label
	self.control = Interact.attach(base, {
		onPress = function()
			if props.onPress then
				props.onPress(self)
			end
		end,
		render = function(state)
			self:_render(state)
		end,
	})
	return self
end

function Button:_render(state: string)
	self.plate:Show(state)
	local leather = onLeather(self.variant)
	local color = if leather then "cream" else "ink"
	if state == "disabled" or state == "locked" then
		color = if leather then "paperDisabled" else "inkSoft"
	end
	self.label.TextColor3 = Tokens.Color(color)
	local shown = if state == "busy" then "…" else self.text
	Core.SetText(self.label, shown)
	if self.icon and self.icon:IsA("ImageLabel") then
		(self.icon :: ImageLabel).ImageTransparency = if state == "disabled" then 0.35 else 0
	end
end

function Button:SetLabel(text: string)
	self.text = text
	self.control:Refresh()
end

-- Switches between primary / secondary / play looks (an invite turned "Invited").
function Button:SetVariant(variant: string)
	self.variant = variant
	self.plate:SetRole(ROLE[variant] or ROLE.primary)
	self.root:SetAttribute("KitRole", ROLE[variant] or ROLE.primary)
	self.control:Refresh()
end

function Button:SetEnabled(enabled: boolean)
	self.control:SetEnabled(enabled)
end

function Button:SetBusy(busy: boolean)
	self.control:SetBusy(busy)
end

function Button:Destroy()
	self.base.maid:Clean()
end

return Button
