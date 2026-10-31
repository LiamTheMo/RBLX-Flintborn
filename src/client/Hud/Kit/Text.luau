-- Text in the kit's type roles (ARCHITECTURE §3.4): Merriweather Heavy, Bold and
-- Regular and Patrick Hand, sizes in design px, colours from tokens. Scaled
-- text keeps to its role size in layout px and never drops below 9 screen px
-- (Widgets.TextCap). Every word on screen is a live label, never baked art.
--
--   Kit.Text.new(body, { rect = { 0, 0, 300, 30 }, text = "Stone Axe", role = "itemTitle" })
--   Kit.Text.new(head, { rect = r, text = "Ancestral Forge", role = "windowTitle", smallCaps = true })

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local KitModel = require(ReplicatedStorage.Shared.UI.KitModel)
local Core = require(script.Parent.Core)
local Tokens = require(script.Parent.Tokens)

local Text = {}
Text.__index = Text

-- RichText fake small caps for a role: initials at the role size, the rest at
-- `ratio` of it (M06 "ANCESTRAL FORGE": 46 / 40).
function Text.SmallCaps(text: string, role: string?, ratio: number?): string
	local size = Tokens.TextStyle(role or "windowTitle").size
	return KitModel.SmallCaps(text, size, math.floor(size * (ratio or 40 / 46) + 0.5))
end

-- Small caps from props: smallCapsSizes {initials, rest}, else the role size
-- (or textSize) and 40 / 46 of it.
function Text._smallCaps(text: string, props): string
	local sizes = props.smallCapsSizes
	if sizes then
		return KitModel.SmallCaps(text, sizes[1], sizes[2])
	end
	local size = props.textSize or Tokens.TextStyle(props.role or "windowTitle").size
	return KitModel.SmallCaps(text, size, math.floor(size * 40 / 46 + 0.5))
end

-- The width of `text` in a role, in design px.
Text.Width = Core.TextWidth

-- props: rect | size (+ layoutOrder), text, role, textSize (overrides the
-- role's size), align, yAlign, wrap, scaled, color (token), caps (overrides the
-- role), smallCaps, smallCapsSizes ({initials, rest} px), outline (true for a
-- paper outline, or a colour token: text over the world), outlineThickness,
-- zIndex, name.
function Text.new(parent: Instance, props)
	local w, h = Core.Size(props, 100, 24)
	local label = Core.Label(parent, {
		text = if props.smallCaps then Text._smallCaps(props.text or "", props) else props.text,
		size = props.textSize,
		role = props.role or "body",
		align = props.align,
		yAlign = props.yAlign,
		wrap = props.wrap,
		scaled = props.scaled,
		color = props.color,
		caps = props.caps,
		rich = props.smallCaps == true or props.rich == true,
		z = props.zIndex,
		name = props.name,
		outline = props.outline,
		outlineThickness = props.outlineThickness,
		rect = { 0, 0, w, h },
	})
	Core.Place(label, props, w, h)
	label:SetAttribute("KitComponent", "Text")
	label:SetAttribute("KitRole", "text." .. (props.role or "body"))
	label:SetAttribute("KitState", "normal")
	return setmetatable({
		root = label,
		role = props.role or "body",
		smallCaps = props.smallCaps,
		smallCapsSizes = props.smallCapsSizes,
		textSize = props.textSize,
	}, Text)
end

function Text:SetText(text: string)
	if self.smallCaps then
		self.root.Text = Text._smallCaps(text, self)
	else
		Core.SetText(self.root, text)
	end
end

function Text:SetColor(token: string)
	self.root.TextColor3 = Tokens.Color(token)
end

function Text:Destroy()
	self.root:Destroy()
end

return Text
