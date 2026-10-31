-- Shared plumbing for kit components: instance creation, placement props, the
-- root/visual frame pair every component has, text labels in the kit's type
-- roles, text measurement and a small signal.
--
-- Every component root is a transparent Frame placed by its props (rect or
-- size + layoutOrder) carrying KitComponent / KitRole / KitState attributes. Its
-- art and text sit in a "Visual" frame centred in the root with a UIScale, so
-- hover and press scale about the centre without moving layout.

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TextService = game:GetService("TextService")

local KitModel = require(ReplicatedStorage.Shared.UI.KitModel)
local Widgets = require(script.Parent.Parent.Widgets)
local Scale = require(script.Parent.Scale)
local Tokens = require(script.Parent.Tokens)

local Core = {}

Core.Maid = KitModel.Maid

function Core.Make(className: string, props, parent: Instance?): any
	local object = Instance.new(className)
	if props then
		for key, value in props do
			(object :: any)[key] = value
		end
	end
	object.Parent = parent
	return object
end

-- The design size {w, h} a component is built at: props.rect, props.size, or
-- the defaults.
function Core.Size(props, defaultW: number, defaultH: number): (number, number)
	local rect = props.rect
	if rect then
		return rect[3], rect[4]
	end
	local size = props.size
	if type(size) == "table" then
		return size[1] or defaultW, size[2] or defaultH
	elseif type(size) == "number" then
		return size, size
	end
	return defaultW, defaultH
end

-- Places `object` from placement props: rect = {x, y, w, h} in the parent's
-- design px, or size = {w, h} with layoutOrder for a child of a layout, plus
-- optional position (UDim2) and anchorPoint (Vector2) for edge-pinned parts.
function Core.Place(object: GuiObject, props, w: number, h: number)
	object.Size = UDim2.fromOffset(w, h)
	if props.rect then
		object.Position = UDim2.fromOffset(props.rect[1], props.rect[2])
	end
	if props.position then
		object.Position = props.position
	end
	if props.anchorPoint then
		object.AnchorPoint = props.anchorPoint
	end
	if props.layoutOrder then
		object.LayoutOrder = props.layoutOrder
	end
	if props.visible == false then
		object.Visible = false
	end
end

export type Base = {
	root: Frame,
	visual: Frame,
	scale: UIScale,
	maid: any,
	w: number,
	h: number,
	z: number,
}

-- A component's root and visual frames. `kind` is the KitComponent attribute.
function Core.Root(parent: Instance?, kind: string, role: string, props, w: number, h: number): Base
	local z = props.zIndex or 4
	local root = Core.Make("Frame", {
		Name = props.name or kind,
		BackgroundTransparency = 1,
		BorderSizePixel = 0,
		ZIndex = z,
	}, nil)
	Core.Place(root, props, w, h)
	root:SetAttribute("KitComponent", kind)
	root:SetAttribute("KitRole", role)
	root:SetAttribute("KitState", "normal")
	local visual = Core.Make("Frame", {
		Name = "Visual",
		AnchorPoint = Vector2.new(0.5, 0.5),
		BackgroundTransparency = 1,
		Position = UDim2.fromScale(0.5, 0.5),
		Size = UDim2.fromScale(1, 1),
		ZIndex = z,
	}, root)
	local scale = Core.Make("UIScale", { Name = "Motion", Scale = 1 }, visual)
	root.Parent = parent
	local maid = KitModel.Maid()
	maid:Give(root)
	return { root = root, visual = visual, scale = scale, maid = maid, w = w, h = h, z = z }
end

local phoneRoles: { [string]: boolean } = {}
for _, role in Tokens.Data.phoneText.roles do
	phoneRoles[role] = true
end

-- The text boost for `role` on a short touch screen (a landscape phone, where
-- windows and the HUD draw small): body and label roles grow by phoneText.scale
-- so they stay readable; titles keep their size. 1 elsewhere.
function Core.TextBoost(role: string): number
	if not phoneRoles[role] then
		return 1
	end
	return if Scale.IsSmallTouch() then Tokens.Data.phoneText.scale else 1
end

-- Boosted labels and their unboosted sizes, so a change of form factor (a
-- rotated or resized screen, a keyboard attached) re-applies the boost.
local boosted: { [Instance]: number } = setmetatable({}, { __mode = "k" }) :: any
local function track(label: Instance, role: string, size: number)
	if phoneRoles[role] then
		boosted[label] = size
	end
end
Scale.OnFormFactorChanged(function()
	for label, size in boosted do
		if label.Parent then
			local role = label:GetAttribute("KitTextRole");
			(label :: any).TextSize = size * Core.TextBoost(role or "body")
		end
	end
end)

-- Applies a text role (font, size, colour) to a label.
function Core.Style(label: TextLabel | TextButton | TextBox, role: string, colorKey: string?)
	local style = Tokens.TextStyle(role)
	label.FontFace = style.face
	label.TextSize = style.size * Core.TextBoost(role)
	label:SetAttribute("KitTextRole", role)
	track(label, role, style.size)
	label.TextColor3 = Tokens.Color(colorKey or style.color)
	return style
end

local ALIGN_X =
	{ Left = Enum.TextXAlignment.Left, Center = Enum.TextXAlignment.Center, Right = Enum.TextXAlignment.Right }
local ALIGN_Y =
	{ Top = Enum.TextYAlignment.Top, Center = Enum.TextYAlignment.Center, Bottom = Enum.TextYAlignment.Bottom }

-- A TextLabel in a type role. opts: text, role, rect {x, y, w, h} (or size and
-- position), align ("Left" | "Center" | "Right"), yAlign, wrap, scaled (shrink
-- to fit, never past the role size), color (token), caps, rich, outline (true
-- for a paper outline, or a colour token), outlineThickness, z, name.
function Core.Label(parent: Instance, opts): TextLabel
	local role = opts.role or "body"
	local label = Core.Make("TextLabel", {
		Name = opts.name or "Text",
		BackgroundTransparency = 1,
		BorderSizePixel = 0,
		TextStrokeTransparency = 1,
		TextXAlignment = ALIGN_X[opts.align or "Left"],
		TextYAlignment = ALIGN_Y[opts.yAlign or "Center"],
		TextWrapped = opts.wrap == true,
		TextTruncate = if opts.wrap then Enum.TextTruncate.None else Enum.TextTruncate.AtEnd,
		RichText = opts.rich == true,
		ZIndex = opts.z or 5,
	}, nil)
	local style = Core.Style(label, role, opts.color)
	if opts.size then
		label.TextSize = opts.size * Core.TextBoost(role)
		track(label, role, opts.size)
	end
	if opts.outline then
		-- Text over the world: a thin outline (paper behind ink, ink behind
		-- cream) keeps it readable on any background.
		Core.Make("UIStroke", {
			Name = "Outline",
			ApplyStrokeMode = Enum.ApplyStrokeMode.Contextual,
			Color = Tokens.Color(if opts.outline == true then "paper" else opts.outline),
			Thickness = opts.outlineThickness or 1,
			Transparency = 0.1,
		}, label)
	end
	local caps = if opts.caps ~= nil then opts.caps else style.caps
	label:SetAttribute("KitCaps", caps)
	label.Text = if caps and not opts.rich then string.upper(opts.text or "") else (opts.text or "")
	local rect = opts.rect
	if rect then
		label.Position = UDim2.fromOffset(rect[1], rect[2])
		label.Size = UDim2.fromOffset(rect[3], rect[4])
	end
	if opts.scaled then
		label.TextScaled = true
		Widgets.TextCap(label, label.TextSize, Tokens.Space("minTextPx", 9))
	end
	label.Parent = parent
	return label :: TextLabel
end

-- Sets a label's text, upper-cased when its role is in capitals.
function Core.SetText(label: TextLabel, text: string)
	label.Text = if label:GetAttribute("KitCaps") and not label.RichText then string.upper(text) else text
end

-- The width in design px of `text` in a type role (at `size`, or the role's).
function Core.TextWidth(text: string, role: string, size: number?): number
	local style = Tokens.TextStyle(role)
	local spec = Tokens.Data.fonts[style.font]
	local px = (size or style.size) * Core.TextBoost(role)
	local shown = if style.caps then string.upper(text) else text
	local legacy = (Enum.Font :: any)[spec.legacy] or Enum.Font.Merriweather
	local ok, bounds = pcall(TextService.GetTextSize, TextService, shown, px, legacy, Vector2.new(10000, 10000))
	local width = if ok and bounds then bounds.X else #shown * px * 0.6
	return width * (Tokens.Data.weightWidth[spec.weight] or 1)
end

-- A tiny signal for component events (Opened, Closed).
local Signal = {}
Signal.__index = Signal

function Core.Signal()
	return setmetatable({ handlers = {} }, Signal)
end

function Signal:Connect(fn)
	local handlers = self.handlers
	handlers[fn] = true
	return {
		Connected = true,
		Disconnect = function(connection)
			connection.Connected = false
			handlers[fn] = nil
		end,
	}
end

function Signal:Fire(...)
	for fn in table.clone(self.handlers) do
		task.spawn(fn, ...)
	end
end

function Signal:Destroy()
	table.clear(self.handlers)
end

return Core
