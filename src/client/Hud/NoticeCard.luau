-- A parchment notice card (the small cornered card on art/reference/ui/
-- parchment/11_panel_layouts.png, sprite pm_card): a title, wrapping text and
-- optional buttons, growing with its text. Used for server notices, trade
-- invites, the run's short toasts and the extraction receipt, in the shared
-- top-centre column (Theme.TopStack) or a gui of their own. Sizes are screen
-- pixels; the player's UI scale applies to the gui holding it.

local Layout = require(script.Parent.Layout)
local Parchment = require(script.Parent.Parchment)
local Widgets = require(script.Parent.Widgets)

local NoticeCard = {}
NoticeCard.__index = NoticeCard

-- The card art's corners drawn at half size suit a card this small.
local SLICE = 0.5
local PAD_X, PAD_TOP, PAD_BOTTOM = 34, 18, 16

-- opts: name, width, layoutOrder, title? (nil for text only), onPress? (the
-- whole card dismisses or acts when pressed; omit when it has buttons).
function NoticeCard.new(parent: Instance, opts)
	local self = setmetatable({}, NoticeCard)
	local frame = Widgets.Make("Frame", {
		Name = opts.name or "Notice",
		AutomaticSize = Enum.AutomaticSize.Y,
		BackgroundTransparency = 1,
		LayoutOrder = opts.layoutOrder or 0,
		Size = UDim2.fromOffset(opts.width or 440, 0),
		Visible = false,
		ZIndex = 1,
	}, parent) :: Frame
	self.frame = frame
	Widgets.Sprite("pm_card", { Name = "Art", Size = UDim2.fromScale(1, 1), ZIndex = 1 }, frame, SLICE)
	local body = Widgets.Make("Frame", {
		Name = "Body",
		AutomaticSize = Enum.AutomaticSize.Y,
		BackgroundTransparency = 1,
		Size = UDim2.fromScale(1, 0),
		ZIndex = 2,
	}, frame)
	Widgets.Make("UIPadding", {
		PaddingLeft = UDim.new(0, PAD_X),
		PaddingRight = UDim.new(0, PAD_X - 12),
		PaddingTop = UDim.new(0, PAD_TOP),
		PaddingBottom = UDim.new(0, PAD_BOTTOM),
	}, body)
	Widgets.Make("UIListLayout", { Padding = UDim.new(0, 6), SortOrder = Enum.SortOrder.LayoutOrder }, body)
	self.body = body
	local function textLine(name: string, size: number, color: string, order: number): TextLabel
		local label = Parchment.Text("", { 0, 0, 0, 0 }, body, { size = size, color = color, name = name, z = 3 })
		label.AutomaticSize = Enum.AutomaticSize.Y
		label.LayoutOrder = order
		label.Size = UDim2.new(1, 0, 0, size + 2)
		label.TextWrapped = true
		label.TextTruncate = Enum.TextTruncate.None
		return label
	end
	self.title = textLine("Title", 22, "ink", 1)
	self.title.Visible = opts.title ~= nil
	self.title.Text = opts.title or ""
	self.text = textLine("Text", 18, "inkSoft", 2)
	self.buttons = nil
	if opts.onPress then
		local button = Widgets.Make("TextButton", {
			Name = "Press",
			AutoButtonColor = false,
			BackgroundTransparency = 1,
			Size = UDim2.fromScale(1, 1),
			Text = "",
			ZIndex = 5,
		}, frame)
		button.Activated:Connect(opts.onPress)
	end
	return self
end

-- A button under the text: kind "leather" (default) or "paper".
function NoticeCard:AddButton(label: string, kind: string?, onPress)
	if self.buttons == nil then
		self.buttons = Widgets.Make("Frame", {
			Name = "Buttons",
			BackgroundTransparency = 1,
			LayoutOrder = 3,
			Size = UDim2.new(1, 0, 0, 46),
			ZIndex = 3,
		}, self.body)
		Widgets.Make("UIListLayout", {
			FillDirection = Enum.FillDirection.Horizontal,
			Padding = UDim.new(0, 10),
			SortOrder = Enum.SortOrder.LayoutOrder,
		}, self.buttons)
	end
	local count = #self.buttons:GetChildren()
	local paper = kind == "paper"
	local made = Parchment.Button(
		if paper then "pm_button_paper" else "pm_button_claim",
		{ 0, 0, 150, 44 },
		self.buttons,
		onPress,
		{
			name = label,
			label = label,
			color = if paper then "ink" else "cream",
			size = 19,
			inset = 14,
			z = 3,
		}
	)
	made.holder.LayoutOrder = count
	return made
end

function NoticeCard:Show(text: string, title: string?)
	if title then
		self.title.Text = title
		self.title.Visible = true
	end
	self.text.Text = text
	self.frame.Visible = true
end

function NoticeCard:Hide()
	self.frame.Visible = false
end

function NoticeCard:IsShown(): boolean
	return self.frame.Visible
end

-- The colour of the title (e.g. "haveShort" for a warning).
function NoticeCard:SetTone(colorKey: string)
	self.title.TextColor3 = Layout.Color(colorKey)
end

return NoticeCard
