-- Square and round buttons carrying an icon or glyph (sheets 02, 03, 06, 07, 15).
--
-- Variants: "close" (leather ✕, four states of art), "paper" / "leather" /
-- "small" squares with a glyph (+ − ✓ ✕ arrows), "round" (round paper frame),
-- "hud" (HUD square), "tile" (HUD menu tile with a menu icon), and buttons whose
-- art carries its glyph: "settings", "invite", "plus", "minus", "dropdown".
-- Tiles and squares grow to 1.03 on hover. States: normal, hover, pressed,
-- disabled, selected (gold glow).
--
--   Kit.IconButton.new(grid, { size = { 86, 86 }, variant = "tile", icon = "backpack", onPress = open })
--   Kit.IconButton.new(row, { rect = r, variant = "paper", icon = "plus", onPress = add })

local Art = require(script.Parent.Art)
local Badge = require(script.Parent.Badge)
local Core = require(script.Parent.Core)
local Interact = require(script.Parent.Interact)

local IconButton = {}
IconButton.__index = IconButton

-- Variants whose art already carries the glyph.
local BAKED = { close = true, settings = true, invite = true, plus = true, minus = true, dropdown = true }

-- Icon size as a share of the plate, per variant.
local ICON_SHARE = { tile = 0.72, hud = 0.62, round = 0.55, paper = 0.55, leather = 0.55, small = 0.55 }

-- props: rect | size, variant, icon (id), tint (token), onPress, badge
-- (Kit.Badge props, e.g. { variant = "dot" }), zIndex, name.
function IconButton.new(parent: Instance, props)
	local variant = props.variant or "paper"
	local role = "iconButton." .. variant
	if Art.ROLES[role] == nil then
		role = "iconButton.paper"
	end
	local nw, nh = Art.SizeOf(Art.ROLES[role].sprite)
	local w, h = Core.Size(props, nw or 60, nh or 58)
	local base = Core.Root(parent, "IconButton", role, props, w, h)
	local self = setmetatable({ root = base.root, base = base, variant = variant, w = w, h = h }, IconButton)
	self.plate = Art.Plate(base.visual, role, w, h, { z = base.z })
	if props.icon and not BAKED[variant] then
		local share = ICON_SHARE[variant] or 0.55
		local s = math.floor(math.min(w, h) * share)
		self.icon = Art.Icon(base.visual, props.icon, { (w - s) / 2, (h - s) / 2, s, s }, {
			z = base.z + 2,
			tint = props.tint or (if variant == "leather" then "cream" else nil),
			name = "Icon",
		})
	end
	if props.badge then
		local badgeProps = table.clone(props.badge)
		badgeProps.zIndex = base.z + 5
		badgeProps.anchor = badgeProps.anchor or "topRight"
		self.badge = Badge.new(base.visual, badgeProps)
	end
	self.control = Interact.attach(base, {
		hoverScale = variant ~= "close",
		onPress = function()
			if props.onPress then
				props.onPress(self)
			end
		end,
		render = function(state)
			self.plate:Show(state)
			if self.icon and self.icon:IsA("ImageLabel") then
				local disabled = state == "disabled" or state == "locked"
				local icon = self.icon :: ImageLabel
				icon.ImageTransparency = if disabled then 0.45 else 0
			end
		end,
	})
	return self
end

function IconButton:SetEnabled(enabled: boolean)
	self.control:SetEnabled(enabled)
end

function IconButton:SetSelected(selected: boolean)
	self.control:SetSelected(selected)
end

function IconButton:Destroy()
	if self.badge then
		self.badge:Destroy()
	end
	self.base.maid:Clean()
end

return IconButton
