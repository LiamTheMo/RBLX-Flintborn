-- A progress ring (sheet 19): the empty track, the full ring's fill revealed
-- clockwise from the top for the fraction, and an optional centre label.
-- Each half of the fill is clipped to its side of the ring and wiped by a
-- hard-edged UIGradient turned with the value (no rotated images).
--
--   local ring = Kit.Ring.new(card, { rect = { 0, 0, 80, 80 }, value = 0.35, text = "35%" })
--   ring:Set(0.6)

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local HudModel = require(ReplicatedStorage.Shared.UI.HudModel)
local Art = require(script.Parent.Art)
local Core = require(script.Parent.Core)

local Ring = {}
Ring.__index = Ring

-- Opaque before the gradient's middle, clear after it.
local WIPE = NumberSequence.new({
	NumberSequenceKeypoint.new(0, 0),
	NumberSequenceKeypoint.new(0.499, 0),
	NumberSequenceKeypoint.new(0.5, 1),
	NumberSequenceKeypoint.new(1, 1),
})

-- props: rect | size, value (0-1), text, textRole ("value"), textSize, zIndex, name.
function Ring.new(parent: Instance, props)
	local w, h = Core.Size(props, 80, 80)
	local base = Core.Root(parent, "Ring", "ring.track", props, w, h)
	local self = setmetatable({ root = base.root, base = base, halves = {} }, Ring)
	Art.Plate(base.visual, "ring.track", w, h, { z = base.z })
	local sprite = Art.ROLES["ring.fill"].sprite
	-- Before upload only the track's stand-in draws.
	for index, side in if Art.HasArt(sprite) then { "Right", "Left" } else {} do
		local clip = Core.Make("Frame", {
			Name = side .. "Half",
			BackgroundTransparency = 1,
			ClipsDescendants = true,
			Position = UDim2.fromOffset(if side == "Right" then w / 2 else 0, 0),
			Size = UDim2.fromOffset(w / 2, h),
			ZIndex = base.z + 1,
		}, base.visual)
		local image = Art.Sprite(sprite, w, h, clip, {
			Name = "Fill",
			Position = UDim2.fromOffset(if side == "Right" then -w / 2 else 0, 0),
			ZIndex = base.z + 1,
		})
		local gradient = Core.Make("UIGradient", { Transparency = WIPE }, image)
		self.halves[index] = { clip = clip, gradient = gradient }
	end
	if props.text then
		self.label = Core.Label(base.visual, {
			name = "Label",
			text = props.text,
			role = props.textRole or "value",
			size = props.textSize,
			align = "Center",
			scaled = true,
			rect = { w * 0.2, h * 0.3, w * 0.6, h * 0.4 },
			z = base.z + 2,
		})
	end
	self:Set(props.value or 0)
	return self
end

-- Shows `fraction` (0-1) of the ring filled, clockwise from the top.
function Ring:Set(fraction: number)
	local f = HudModel.Clamp01(fraction)
	self.root:SetAttribute("KitValue", f)
	local right, left = self.halves[1], self.halves[2]
	if right == nil then
		return
	end
	-- The opaque side of each wipe turns clockwise with the value.
	right.gradient.Rotation = math.min(f * 360, 180)
	right.clip.Visible = f > 0
	left.gradient.Rotation = math.max(180, f * 360)
	left.clip.Visible = f > 0.5
end

function Ring:SetText(text: string)
	if self.label then
		self.label.Text = text
	end
end

function Ring:Destroy()
	self.base.maid:Clean()
end

return Ring
