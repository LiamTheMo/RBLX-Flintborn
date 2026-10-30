-- A parchment list window for the screens with no reference sheet of their own
-- (Market, Progress, Trade): the generic window frame from the panel layouts
-- (art/reference/ui/parchment/11_panel_layouts.png, spec docs/ui/ListWindows.md),
-- the leather title plate, a close button, an optional tab column, and a
-- scrolling page the controller fills with sections, lines, rows, button rows,
-- input boxes and paired cards. A status line runs along the bottom and a
-- confirmation card can cover the page. The view only draws and reports;
-- controllers decide what every press does.
--
-- Positions are {x, y, w, h} in the window's own design pixels (SIZE).

local GuiService = game:GetService("GuiService")

local ItemSlot = require(script.Parent.ItemSlot)
local Layout = require(script.Parent.Layout)
local Parchment = require(script.Parent.Parchment)
local Widgets = require(script.Parent.Widgets)

local ListWindow = {}
ListWindow.__index = ListWindow

ListWindow.SIZE = { 1180, 720 }
ListWindow.ROW_HEIGHT = 84
local W, H = ListWindow.SIZE[1], ListWindow.SIZE[2]
local TOP, BOTTOM = 132, 664
local TAB_COLUMN = { 44, TOP, 304, BOTTOM - TOP }
local TAB_HEIGHT, TAB_PITCH = 80, 88
local BUTTON_W, BUTTON_H = 160, 54
-- Text tones a controller can ask for.
local TONES = { ink = "ink", soft = "inkSoft", good = "haveEnough", warn = "haveShort", gold = "headerRule" }

local function place(object: GuiObject, r)
	object.Position = UDim2.fromOffset(r[1], r[2])
	object.Size = UDim2.fromOffset(r[3], r[4])
end

local function tone(name: string?): string
	return TONES[name or "ink"] or name or "ink"
end

-- opts: name, title, tabs ({id, label, glyph}), onTab(id), onClose(), displayOrder.
function ListWindow.new(parent: Instance?, opts)
	local self = setmetatable({}, ListWindow)
	self.opts = opts
	self.screen = Parchment.Screen(opts.name, ListWindow.SIZE, opts.displayOrder or 20, parent)
	local window = self.screen.window
	self.window = window
	self.order = 0
	self.tabs = {}

	local chrome = Parchment.Window(window, opts.title or "", function()
		opts.onClose()
	end)
	self.title = chrome.title
	self.close = chrome.close
	-- Currencies or a short summary along the top edge, left of the X.
	self.corner = Widgets.Make("Frame", {
		Name = "Corner",
		AnchorPoint = Vector2.new(1, 0),
		BackgroundTransparency = 1,
		Position = UDim2.new(1, -120, 0, 58),
		Size = UDim2.fromOffset(W - Parchment.PLAQUE_X - 700, 48),
		ZIndex = 4,
	}, window)
	Widgets.Make("UIListLayout", {
		FillDirection = Enum.FillDirection.Horizontal,
		HorizontalAlignment = Enum.HorizontalAlignment.Right,
		Padding = UDim.new(0, 12),
		SortOrder = Enum.SortOrder.LayoutOrder,
		VerticalAlignment = Enum.VerticalAlignment.Center,
	}, self.corner)

	local pageRect = { 44, TOP, W - 88, BOTTOM - TOP }
	if opts.tabs and #opts.tabs > 0 then
		Parchment.Panel(TAB_COLUMN, window).Name = "TabColumn"
		for index, tab in opts.tabs do
			local y = TAB_COLUMN[2] + 16 + (index - 1) * TAB_PITCH
			self.tabs[tab.id] = Parchment.Tab({ 56, y, 280, TAB_HEIGHT }, window, tab.label, tab.glyph, function()
				opts.onTab(tab.id)
			end)
		end
		pageRect = { TAB_COLUMN[1] + TAB_COLUMN[3] + 14, TOP, W - 88 - TAB_COLUMN[3] - 14, BOTTOM - TOP }
	end
	Parchment.Panel(pageRect, window).Name = "Page"
	self.pageRect = pageRect
	local list = Widgets.Make("ScrollingFrame", {
		Name = "List",
		Active = true,
		AutomaticCanvasSize = Enum.AutomaticSize.Y,
		BackgroundTransparency = 1,
		BorderSizePixel = 0,
		CanvasSize = UDim2.new(),
		ScrollBarImageColor3 = Layout.Color("paperEdge"),
		ScrollBarThickness = 8,
		ScrollingDirection = Enum.ScrollingDirection.Y,
		ZIndex = 3,
	}, window) :: ScrollingFrame
	place(list, { pageRect[1] + 14, pageRect[2] + 14, pageRect[3] - 22, pageRect[4] - 28 })
	Widgets.Make("UIListLayout", { Padding = UDim.new(0, 8), SortOrder = Enum.SortOrder.LayoutOrder }, list)
	Widgets.Make("UIPadding", { PaddingRight = UDim.new(0, 16), PaddingTop = UDim.new(0, 2) }, list)
	self.list = list
	self.status = Parchment.Text("", { 70, BOTTOM + 4, W - 140, 34 }, window, {
		size = 21,
		color = "inkSoft",
		scaled = true,
		name = "Status",
	})
	self:_confirmCard(window)
	return self
end

-- Highlights tab `id` (nil for none).
function ListWindow:SetTab(id: string?)
	for tabId, tab in self.tabs do
		tab.SetSelected(tabId == id)
	end
end

function ListWindow:SetTitle(text: string)
	self.title.Text = text
end

function ListWindow:SetStatus(text: string?)
	self.status.Text = text or ""
end

-- The band left of the title: {{icon = sprite?, text}}, e.g. Coins and Gems.
function ListWindow:SetCorner(items)
	for _, child in self.corner:GetChildren() do
		if child:IsA("GuiObject") then
			child:Destroy()
		end
	end
	for index, item in items do
		if item.icon then
			Widgets.Sprite(item.icon, {
				Name = "Icon" .. index,
				LayoutOrder = index * 2 - 1,
				ScaleType = Enum.ScaleType.Fit,
				Size = UDim2.fromOffset(38, 38),
				ZIndex = 4,
			}, self.corner)
		end
		-- Sized for its digits (a wallet amount); a long amount shrinks to fit.
		local width = math.min(12 + #item.text * 15, 104)
		local label = Parchment.Text(
			item.text,
			{ 0, 0, width, 40 },
			self.corner,
			{ size = 26, name = "Text" .. index, scaled = true, minSize = 14 }
		)
		label.LayoutOrder = index * 2
	end
end

-- Clears the page before a controller redraws it. Remembers which button had
-- the gamepad's focus so Finish() can give it back.
function ListWindow:Begin()
	local focus = GuiService.SelectedObject
	self.focusName, self.focusRow = nil, nil
	self.hadFocus = focus ~= nil and focus:IsDescendantOf(self.window)
	if self.hadFocus and focus:IsDescendantOf(self.list) then
		-- The button's key and its row's: keys like "Buy" repeat on every row.
		local holder = focus.Parent
		self.focusName = holder and holder.Name
		self.focusRow = holder and holder.Parent and holder.Parent.Name
	end
	for _, child in self.list:GetChildren() do
		if child:IsA("GuiObject") then
			child:Destroy()
		end
	end
	self.order = 0
end

-- After a redraw: the focused button again (same key), else the first one.
function ListWindow:Finish()
	if not self.hadFocus or (GuiService.SelectedObject and GuiService.SelectedObject.Parent) then
		return
	end
	local first, match = nil, nil
	for _, object in self.list:GetDescendants() do
		if object:IsA("TextButton") and object.Selectable then
			first = first or object
			local holder = object.Parent
			if
				match == nil
				and self.focusName
				and holder
				and holder.Name == self.focusName
				and holder.Parent
				and holder.Parent.Name == self.focusRow
			then
				match = object
			end
		end
	end
	GuiService.SelectedObject = match or first or self.close
end

function ListWindow:_next(): number
	self.order += 1
	return self.order
end

function ListWindow:_holder(height: number, auto: boolean?): Frame
	return Widgets.Make("Frame", {
		Name = "Item" .. self.order,
		AutomaticSize = if auto then Enum.AutomaticSize.Y else Enum.AutomaticSize.None,
		BackgroundTransparency = 1,
		LayoutOrder = self:_next(),
		Size = UDim2.new(1, 0, 0, height),
		ZIndex = 4,
	}, self.list) :: Frame
end

-- A wrapping text label that grows with its text.
local function flowText(text: string, parent: Instance, position: UDim2, width: UDim, opts)
	local label = Parchment.Text(text, { 0, 0, 0, 0 }, parent, opts)
	label.AutomaticSize = Enum.AutomaticSize.Y
	label.Position = position
	label.Size = UDim2.new(width, UDim.new(0, opts.size or 20))
	label.TextWrapped = true
	label.TextTruncate = Enum.TextTruncate.None
	return label
end

-- A section header (diamond mark, capitals and a rule).
function ListWindow:Section(text: string)
	local holder = self:_holder(52)
	local width = self.list.AbsoluteSize.X
	width = if width > 0 then width / math.max(self.screen.scale.Scale, 0.01) - 16 else self.pageRect[3] - 40
	Parchment.Header(text, { 4, 6, width - 8, 36 }, holder)
end

-- A paragraph. tone: "ink" (default), "soft", "good", "warn", "gold".
function ListWindow:Line(text: string, toneName: string?, size: number?)
	local holder = self:_holder(0, true)
	flowText(text, holder, UDim2.fromOffset(6, 0), UDim.new(1, -12), {
		size = size or 20,
		color = tone(toneName or "soft"),
	})
	return holder:FindFirstChildWhichIsA("TextLabel")
end

local function addButton(parent: Instance, spec, r)
	local primary = spec.kind ~= "paper"
	local button = Parchment.Button(if primary then "pm_button_claim" else "pm_button_paper", r, parent, function()
		spec.onPress()
	end, {
		name = spec.key or spec.label,
		label = spec.label,
		color = if primary then "cream" else "ink",
		size = 20,
		-- Clear of the leather plate's end ornaments.
		inset = if primary then 26 else 16,
		z = 6,
	})
	local enabled = spec.enabled ~= false
	button.SetEnabled(enabled)
	-- The art's tint alone barely reads as off; the label fades too.
	if button.label and not enabled then
		button.label.TextTransparency = 0.45
	end
	return button
end

-- One paper row. spec: title, detail?, icon? (item catalogId) or glyph?
-- (sprite), value? (text) with valueIcon? (sprite), buttons? ({label,
-- enabled, onPress, kind = "paper"|"leather", key}), done? (a tick instead of
-- buttons), tone? (title tone), key? (stable name for focus).
function ListWindow:Row(spec)
	local holder = self:_holder(ListWindow.ROW_HEIGHT, true)
	holder.Name = spec.key or spec.title
	-- A plain rounded paper card (the quest row's art carries a scroll icon).
	Widgets.Sprite("pm_stat_chip_tall", {
		Name = "Art",
		Size = UDim2.fromScale(1, 1),
		ZIndex = 4,
	}, holder, 1)
	local textX = 20
	local iconName = spec.icon and ItemSlot.IconFor(spec.icon)
	local glyph = iconName or spec.glyph
	if glyph then
		local art = Widgets.Sprite(glyph, {
			Name = "Icon",
			Position = UDim2.fromOffset(16, 12),
			ScaleType = Enum.ScaleType.Fit,
			Size = UDim2.fromOffset(60, 60),
			ZIndex = 5,
		}, holder)
		if not iconName and art:IsA("ImageLabel") then
			(art :: ImageLabel).ImageColor3 = Layout.Color("inkSoft")
		end
		textX = 90
	end
	local buttons = spec.buttons or {}
	local right = 16 + #buttons * (BUTTON_W + 10)
	if spec.done then
		right = 70
		Widgets.Sprite("pm_check_green", {
			Name = "Done",
			AnchorPoint = Vector2.new(1, 0.5),
			Position = UDim2.new(1, -24, 0.5, 0),
			Size = UDim2.fromOffset(36, 36),
			ZIndex = 6,
		}, holder)
	end
	for index, button in buttons do
		local x = -(16 + index * (BUTTON_W + 10) - 10)
		local made = addButton(holder, button, { 0, 0, BUTTON_W, BUTTON_H })
		made.holder.AnchorPoint = Vector2.new(0, 0.5)
		made.holder.Position = UDim2.new(1, x, 0.5, 0)
	end
	if spec.value then
		local valueW = 150
		local value = Widgets.Make("Frame", {
			Name = "Value",
			AnchorPoint = Vector2.new(1, 0.5),
			BackgroundTransparency = 1,
			Position = UDim2.new(1, -right, 0.5, 0),
			Size = UDim2.fromOffset(valueW, 44),
			ZIndex = 5,
		}, holder)
		local textW = valueW
		if spec.valueIcon then
			Widgets.Sprite(spec.valueIcon, {
				Name = "Icon",
				AnchorPoint = Vector2.new(1, 0.5),
				Position = UDim2.new(1, 0, 0.5, 0),
				ScaleType = Enum.ScaleType.Fit,
				Size = UDim2.fromOffset(34, 34),
				ZIndex = 5,
			}, value)
			textW -= 40
		end
		Parchment.Text(spec.value, { 0, 0, textW, 44 }, value, {
			size = 24,
			align = "Right",
			scaled = true,
			name = "Amount",
			z = 5,
		})
		right += valueW + 12
	end
	-- Alone, the title sits in the middle of the card.
	local hasDetail = spec.detail ~= nil and spec.detail ~= ""
	-- Long names shrink to fit beside the buttons rather than lose their end.
	Parchment.Text(spec.title, { textX, if hasDetail then 10 else 27, 0, 30 }, holder, {
		size = 24,
		color = tone(spec.tone),
		name = "Title",
		scaled = true,
		minSize = 14,
		z = 5,
	}).Size =
		UDim2.new(1, -(textX + right), 0, 30)
	if hasDetail then
		local detail = flowText(spec.detail, holder, UDim2.fromOffset(textX, 42), UDim.new(1, -(textX + right)), {
			size = 18,
			color = "inkSoft",
			name = "Detail",
			z = 5,
		})
		Widgets.Make("UIPadding", { PaddingBottom = UDim.new(0, 12) }, detail)
	end
	return holder
end

-- A row of equal paper buttons: {{label, enabled, onPress, key}}.
function ListWindow:Buttons(specs)
	local holder = self:_holder(BUTTON_H + 4)
	Widgets.Make("UIListLayout", {
		FillDirection = Enum.FillDirection.Horizontal,
		HorizontalAlignment = Enum.HorizontalAlignment.Right,
		Padding = UDim.new(0, 10),
		SortOrder = Enum.SortOrder.LayoutOrder,
	}, holder)
	for index, spec in specs do
		local made = addButton(holder, spec, { 0, 0, spec.width or BUTTON_W, BUTTON_H })
		made.holder.LayoutOrder = index
	end
	return holder
end

-- A text box on a paper field with a label before it. onSubmit(text)
-- runs when focus leaves with Enter and text typed (or on any focus loss, even
-- empty, when `always`).
function ListWindow:Input(label: string, placeholder: string, onSubmit, always: boolean?): TextBox
	local holder = self:_holder(60)
	Parchment.Text(label, { 6, 8, 300, 44 }, holder, { size = 22, name = "Label", z = 5 })
	-- The stepper's plain paper field (the search box's magnifier would read
	-- as search).
	local field = Widgets.Sprite("pm_stepper_field", { Name = "Field", ZIndex = 5 }, holder, 1)
	place(field, { 316, 6, 320, 48 })
	local box = Widgets.Make("TextBox", {
		Name = "Box",
		BackgroundTransparency = 1,
		ClearTextOnFocus = false,
		Font = Enum.Font.Merriweather,
		PlaceholderColor3 = Layout.Color("inkSoft"),
		PlaceholderText = placeholder,
		Position = UDim2.fromOffset(332, 6),
		Size = UDim2.fromOffset(292, 48),
		Text = "",
		TextColor3 = Layout.Color("ink"),
		TextSize = 21,
		TextXAlignment = Enum.TextXAlignment.Left,
		ZIndex = 6,
	}, holder) :: TextBox
	box.FocusLost:Connect(function(enter)
		if always or (enter and box.Text ~= "") then
			onSubmit(box.Text)
		end
	end)
	return box
end

-- Two cards side by side (a trade's two offers): {title, lines, tone}.
function ListWindow:Pair(left, right)
	local holder = self:_holder(0, true)
	holder.Name = "Pair"
	for index, side in { left, right } do
		local card = Widgets.Sprite("pm_inset", {
			Name = if index == 1 then "Left" else "Right",
			AutomaticSize = Enum.AutomaticSize.Y,
			Position = UDim2.new((index - 1) * 0.5, if index == 1 then 0 else 6, 0, 0),
			Size = UDim2.new(0.5, -6, 0, 150),
			ZIndex = 4,
		}, holder, 0.6)
		Parchment.Text(side.title, { 20, 12, 0, 34 }, card, {
			size = 25,
			color = tone(side.tone or "gold"),
			name = "Title",
			z = 5,
		}).Size =
			UDim2.new(1, -40, 0, 34)
		local body = flowText(side.text, card, UDim2.fromOffset(20, 52), UDim.new(1, -40), {
			size = 20,
			color = "ink",
			name = "Body",
			z = 5,
		})
		Widgets.Make("UIPadding", { PaddingBottom = UDim.new(0, 16) }, body)
	end
	return holder
end

-- A confirmation over the page, its button armed after `delay` seconds.
function ListWindow:_confirmCard(window: Instance)
	local r = self.pageRect
	-- Under the question the window takes no presses: the tabs, close and the
	-- page's buttons stay out of reach until it is answered.
	self.confirmScrim = Widgets.Make("TextButton", {
		Name = "ConfirmScrim",
		Active = true,
		AutoButtonColor = false,
		BackgroundColor3 = Layout.Color("veil"),
		BackgroundTransparency = 0.8,
		BorderSizePixel = 0,
		Selectable = false,
		Size = UDim2.fromScale(1, 1),
		Text = "",
		Visible = false,
		ZIndex = 11,
	}, window)
	local card = Widgets.Sprite("pm_inset", { Name = "Confirm", Active = true, Visible = false, ZIndex = 12 }, window)
	place(card, r)
	if card:IsA("ImageLabel") then
		(card :: ImageLabel).ImageColor3 = Color3.fromRGB(255, 250, 240)
	end
	self.confirmText = Parchment.Text("", { 34, 30, r[3] - 68, r[4] - 150 }, card, {
		size = 23,
		wrap = true,
		scaled = true,
		minSize = 12,
		z = 13,
	})
	self.confirmText.TextYAlignment = Enum.TextYAlignment.Top
	self.confirmYes = Parchment.Button("pm_button_claim", { 34, r[4] - 104, 300, 78 }, card, function()
		local fn = self.confirmFn
		if fn and self.confirmArmed then
			self:HideConfirm()
			fn()
		end
	end, { name = "Yes", label = "", color = "cream", size = 28, inset = 40, z = 13 })
	self.confirmNo = Parchment.Button("pm_button_paper", { 360, r[4] - 95, 220, 60 }, card, function()
		self:HideConfirm()
	end, { name = "No", label = "Cancel", size = 22, inset = 12, z = 13 })
	self.confirmCard = card
end

-- Asks before something that cannot be undone; the confirm button arms after
-- `delay` seconds so the text gets read. Gamepad focus starts on Cancel.
function ListWindow:Confirm(text: string, yes: string, delay: number, onYes)
	self.confirmFn = onYes
	self.confirmArmed = false
	self.confirmText.Text = text
	self.confirmYes.label.Text = if delay > 0 then "READ FIRST…" else yes
	self.confirmYes.SetEnabled(delay <= 0)
	self.confirmArmed = delay <= 0
	self.confirmCard.Visible = true
	self.confirmScrim.Visible = true
	self.list.Visible = false
	if GuiService.SelectedObject ~= nil then
		GuiService.SelectedObject = self.confirmNo.button
	end
	if delay > 0 then
		local fn = onYes
		task.delay(delay, function()
			if self.confirmFn == fn and self.confirmCard.Visible then
				self.confirmArmed = true
				self.confirmYes.label.Text = yes
				self.confirmYes.SetEnabled(true)
			end
		end)
	end
end

function ListWindow:HideConfirm()
	local wasOpen = self.confirmCard.Visible
	self.confirmFn = nil
	self.confirmArmed = false
	self.confirmCard.Visible = false
	self.confirmScrim.Visible = false
	self.list.Visible = true
	local focus = GuiService.SelectedObject
	if wasOpen and focus and focus:IsDescendantOf(self.confirmCard) then
		GuiService.SelectedObject = self.close
	end
end

function ListWindow:IsConfirming(): boolean
	return self.confirmCard.Visible
end

-- Opens the window with gamepad focus on it when a gamepad is driving.
function ListWindow:Open(gamepad: boolean)
	self:HideConfirm()
	self.screen:SetOpen(true)
	if gamepad then
		GuiService.SelectedObject = self.close
	end
end

function ListWindow:Close()
	self:HideConfirm()
	local focus = GuiService.SelectedObject
	if focus and focus:IsDescendantOf(self.screen.gui) then
		GuiService.SelectedObject = nil
	end
	self.screen:SetOpen(false)
end

return ListWindow
