-- The kit's design tokens (src/shared/UI/KitTokens.json): colours, fonts, text
-- roles, spacing, motion, display orders and sound ids. Components read every
-- colour and size through here, never as literals.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Tokens = {}

local data = require(ReplicatedStorage.Shared.UI.KitTokens) :: any
Tokens.Data = data

local colorCache: { [string]: Color3 } = {}

-- A colour token as a Color3 (an unknown key reads as the ink colour, so a typo
-- shows as dark text rather than an error).
function Tokens.Color(key: string): Color3
	local cached = colorCache[key]
	if cached then
		return cached
	end
	local hex = data.colors[key] or data.colors.ink
	local color = Color3.fromHex(hex)
	colorCache[key] = color
	return color
end

-- The grey tint (0-1) a state applies to borrowed art.
function Tokens.Tint(key: string): Color3
	local v = data.tints[key] or 1
	return Color3.new(v, v, v)
end

-- Multiplies two colours (a tint over a fill).
function Tokens.Multiply(a: Color3, b: Color3): Color3
	return Color3.new(a.R * b.R, a.G * b.G, a.B * b.B)
end

local fontCache: { [string]: Font } = {}

-- The FontFace of a font token (display, heading, body, hand). Roblox picks the
-- nearest weight a family has, so Heavy falls back to Bold by itself.
function Tokens.Font(key: string): Font
	if fontCache[key] then
		return fontCache[key]
	end
	local spec = data.fonts[key] or data.fonts.body
	local weight = (Enum.FontWeight :: any)[spec.weight] or Enum.FontWeight.Regular
	local face = Font.new("rbxasset://fonts/families/" .. spec.family .. ".json", weight)
	fontCache[key] = face
	return face
end

export type TextStyle = { face: Font, font: string, size: number, color: string, caps: boolean }

-- A text role's face, size (design px), colour token and caps flag.
function Tokens.TextStyle(role: string): TextStyle
	local spec = data.text[role] or data.text.body
	return {
		face = Tokens.Font(spec.font),
		font = spec.font,
		size = spec.size,
		color = spec.color,
		caps = spec.caps == true,
	}
end

-- A spacing token (design px), or `default` when it is missing.
function Tokens.Space(key: string, default: number?): number
	return data.space[key] or default or 0
end

function Tokens.Scale(key: string): number
	return data.scale[key] or 1
end

local tweenCache: { [string]: TweenInfo } = {}

-- A motion token as a TweenInfo.
function Tokens.Motion(key: string): TweenInfo
	if tweenCache[key] then
		return tweenCache[key]
	end
	local spec = data.motion[key] or data.motion.hover
	local info = TweenInfo.new(
		spec.time,
		(Enum.EasingStyle :: any)[spec.style] or Enum.EasingStyle.Quad,
		(Enum.EasingDirection :: any)[spec.direction] or Enum.EasingDirection.Out
	)
	tweenCache[key] = info
	return info
end

function Tokens.MotionTime(key: string): number
	local spec = data.motion[key]
	return spec and spec.time or 0
end

-- A ScreenGui DisplayOrder.
function Tokens.Order(key: string): number
	return data.order[key] or 1
end

-- The veil colour and transparency behind a modal window.
function Tokens.Veil(): (Color3, number)
	return Tokens.Color(data.veil.color), data.veil.transparency
end

function Tokens.Sound(key: string): string
	return data.sounds[key] or ""
end

return Tokens
