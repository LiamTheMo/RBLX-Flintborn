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

Button.TONES = { bright = "leatherBright", primary = "leatherTint", dark = "leatherDark" }

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
-- textRole, textSize, iconSize (px, default half the height), iconGap (12),
-- contentOffset ({x, y}: moves icon and label together, e.g. up off a lip),
-- tone ("bright" | "primary" | "dark": the leather's shade),
-- onPress, zIndex, name. The play variant has no hover art: it lifts (scales
-- to 1.03) under the pointer.
function Button.new(parent: Instance, props)
	local variant = props.variant or "primary"
	local class = Button.SIZES[props.sizeClass or "m"] or Button.SIZES.m
	local w, h = Core.Size(props, 220, class.h)
	local base = Core.Root(parent, "Button", ROLE[variant] or ROLE.primary, props, w, h)
	local self = setmetatable({ root = base.root, base = base, variant = variant, w = w, h = h }, Button)
	self.plate = Art.Plate(base.visual, ROLE[variant] or ROLE.primary, w, h, { z = base.z })
	-- Leather tone: "bright" (the sprite's own: PLAY, APPLY), "primary"
	-- (default: EQUIP, CLAIM, Invite), "dark" (FORGE, Party CLOSE).
	self.plate.tone = Button.TONES[props.tone or "primary"]
	self.plate:Show("normal")
	self.textRole = props.textRole or class.role
	self.textSize = props.textSize
	self.iconId = props.icon
	self.iconSizeProp = props.iconSize
	self.iconGap = props.iconGap
	self.contentOffset = props.contentOffset
	self.label = Core.Label(base.visual, {
		name = "Label",
		text = props.label or "",
		role = self.textRole,
		size = props.textSize,
		align = "Center",
		scaled = true,
		rect = { 0, 0, w, h - 3 },
		z = base.z + 2,
	})
	self.text = props.label or ""
	self:_layout()
	self.control = Interact.attach(base, {
		hoverScale = variant == "play" or variant == "playSecondary",
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

-- Centres the icon and label together, clear of the plate's rivets.
function Button:_layout()
	local w, h = self.w, self.h
	local iconSize = if self.iconId then (self.iconSizeProp or math.floor(h * 0.5)) else 0
	local gap = if self.iconId then (self.iconGap or 12) else 0
	local room = w - 2 * math.max(16, h * 0.35) - iconSize - gap
	local textW = math.min(Text.Width(self.text, self.textRole, self.textSize) + 4, room)
	local left = (w - (iconSize + gap + textW)) / 2
	if self.iconId and self.icon == nil then
		self.icon = Art.Icon(self.base.visual, self.iconId, { 0, 0, iconSize, iconSize }, {
			z = self.base.z + 2,
			tint = if onLeather(self.variant) then nil else "ink",
			name = "Icon",
		})
	end
	local offset = self.contentOffset or { 0, 0 }
	if self.icon then
		self.icon.Position = UDim2.fromOffset(left + offset[1], (h - iconSize) / 2 + offset[2])
	end
	self.label.Position = UDim2.fromOffset(left + iconSize + gap + offset[1], offset[2])
	self.label.Size = UDim2.fromOffset(textW, h - 3)
end

function Button:_render(state: string)
	self.plate:Show(state)
	local leather = onLeather(self.variant)
	local color = if leather then "cream" else "ink"
	if state == "disabled" or state == "locked" then
		-- Only the primary plate stays leather when disabled; the notched
		-- plaque's disabled art is pale.
		color = if self.variant == "primary" then "paperDisabled" else "inkSoft"
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
	self:_layout()
	self.control:Refresh()
end

-- Switches between primary / secondary / play looks (an invite turned "Invited").
-- Sets the leather tone ("bright" | "primary" | "dark").
function Button:SetTone(tone: string)
	self.plate:SetTone(Button.TONES[tone] or Button.TONES.primary)
end

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
