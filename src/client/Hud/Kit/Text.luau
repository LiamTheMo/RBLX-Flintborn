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

-- The width of `text` in a role, in design px.
Text.Width = Core.TextWidth

-- props: rect | size (+ layoutOrder), text, role, align, yAlign, wrap, scaled,
-- color (token), caps (overrides the role), smallCaps, zIndex, name.
function Text.new(parent: Instance, props)
	local w, h = Core.Size(props, 100, 24)
	local label = Core.Label(parent, {
		text = if props.smallCaps then Text.SmallCaps(props.text or "", props.role) else props.text,
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
		rect = { 0, 0, w, h },
	})
	Core.Place(label, props, w, h)
	label:SetAttribute("KitComponent", "Text")
	label:SetAttribute("KitRole", "text." .. (props.role or "body"))
	label:SetAttribute("KitState", "normal")
	return setmetatable({ root = label, role = props.role or "body", smallCaps = props.smallCaps }, Text)
end

function Text:SetText(text: string)
	if self.smallCaps then
		self.root.Text = Text.SmallCaps(text, self.role)
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
