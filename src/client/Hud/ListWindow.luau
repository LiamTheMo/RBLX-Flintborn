-- The shared list window for the screens with no mockup of their own (Market,
-- Trade, Progress; spec docs/ui/ListWindows.md, ARCHITECTURE §4.8), built only
-- from the UI kit so they read as the same game as the lobby windows: the
-- banner header (icon, title, rule, close) with optional Coins / Gems pills,
-- an optional category tab column on the left (as the Inventory's), and a
-- scrolling page the controller fills with section headers, text lines, soft
-- cards (item art or an icon, title, wrapping detail, an optional bar, a price
-- with its coin or gem, buttons, a round check), button rows, a text field and
-- paired offer panels of slots. A status line runs along the bottom; questions
-- go to a Kit.ConfirmDialog (press-and-hold where a delay guarded them).
--
-- Display only: controllers redraw the page (Begin … Finish) and decide what
-- every press does. Positions are design px in the window (SIZE).
--
--   local window = ListWindow.new(playerGui, { name = "FlintbornMarket", title = "Market", icon = "market",
--       tabs = { { id = "Shop", label = "Shop", icon = "market" } }, onTab = show, onClose = close })
--   window:Begin()
--   window:Section("Tools")
--   window:Row({ key = "Axe", title = "Stone Axe", icon = "StoneAxe", value = "40", valueIcon = "coin",
--       buttons = { { label = "Buy", key = "Buy", onPress = buy } } })
--   window:Finish()

local GuiService = game:GetService("GuiService")

local Kit = require(script.Parent.Kit)

local ListWindow = {}
ListWindow.__index = ListWindow

ListWindow.SIZE = { 1180, 690 }
ListWindow.ROW_HEIGHT = 84

local W, H = ListWindow.SIZE[1], ListWindow.SIZE[2]
local Z = 8
local PAD = 24
local TOP = 108
local STATUS_H = 34
local PAGE_BOTTOM = H - PAD - STATUS_H - 12
-- The category column (Inventory's: icon at 16, label at 73, rows 54 high).
local TAB_W, TAB_H, TAB_PITCH = 232, 54, 64
local TAB_TOP = 114
local COLUMN_RIGHT = PAD + TAB_W + 18
-- Scroll rail and its gap (Kit.Scroll) plus a little air for the cards.
local RAIL = 20 + 4
local BUTTON_H = 42
local ICON = 60
local TITLE_H = 26
local DETAIL_SIZE = 16
local LINE_SIZE = 17
local BAR_H = 18
local SLOT, SLOT_PITCH, CAPTION_H = 80, 92, 20

-- Text tones a controller can ask for, as kit colour tokens.
local TONES = {
	ink = "inkLabel",
	soft = "inkSoft",
	good = "toggleOn",
	warn = "short",
	gold = "leather",
}

local function tone(name: string?): string
	return TONES[name or "ink"] or name or "inkLabel"
end

-- How many lines `text` wraps to in `width` design px (greedy, by words, with
-- the kit's measured widths; a little slack for the engine's own wrapping).
function ListWindow.Lines(text: string, role: string, size: number?, width: number): number
	local limit = width * 0.95
	local space = math.max(Kit.Text.Width(" ", role, size), (size or 16) * 0.28)
	local total = 0
	for paragraph in (text .. "\n"):gmatch("(.-)\n") do
		local count, used = 1, 0
		for word in paragraph:gmatch("%S+") do
			local ww = Kit.Text.Width(word, role, size)
			if used > 0 and used + space + ww > limit then
				count += 1
				used = ww
			else
				used = if used > 0 then used + space + ww else ww
			end
		end
		total += count
	end
	return math.max(total, 1)
end

local function lineHeight(size: number): number
	return math.ceil(size * 1.32)
end

local function buttonWidth(label: string): number
	return math.max(104, math.ceil(Kit.Text.Width(label, "buttonS")) + 44)
end

-- opts: name, title, icon (header icon id), tabs ({{id, label, icon}}),
-- onTab(id), onClose(), parent (the window's ScreenGui parent).
function ListWindow.new(parent: Instance?, opts)
	local self = setmetatable({}, ListWindow)
	self.opts = opts
	self.order = 0
	self.height = 0
	self.tabs = {}
	self.parts = Kit.Core.Maid()
	self.buttons = {}
	self.screen = Kit.Screen.new(opts.name, { size = ListWindow.SIZE, parent = parent })
	self.frame = Kit.Window.new(self.screen, {
		title = opts.title or "",
		icon = opts.icon,
		clasps = "right",
		claspYs = { 0.18, 0.9 },
		onClose = function()
			if opts.onClose then
				opts.onClose()
			else
				self:Close()
			end
		end,
	})
	local v = self.frame.base.visual
	self.visual = v
	self.window = self.screen.window
	self.close = self.frame.close

	local pageX = PAD
	if opts.tabs and #opts.tabs > 0 then
		local built = {}
		for index, def in opts.tabs do
			local y = TAB_TOP + (index - 1) * TAB_PITCH
			local tab = Kit.Tab.new(v, {
				id = def.id,
				name = def.id,
				rect = { PAD, y, TAB_W, TAB_H },
				label = def.label,
				icon = def.icon,
				iconX = 16,
				labelX = 73,
				variant = "category",
				zIndex = Z,
			})
			self.tabs[def.id] = tab
			table.insert(built, tab)
			if index < #opts.tabs then
				Kit.Divider.new(v, {
					name = "TabRule" .. index,
					rect = { PAD + 3, y + TAB_H + 1, TAB_W - 28, 2 },
					variant = "hairline",
					zIndex = Z - 1,
				})
			end
		end
		self.tabGroup = Kit.TabGroup.new(built, function(id)
			if opts.onTab then
				opts.onTab(id)
			end
		end)
		Kit.Divider.new(v, {
			name = "ColumnRule",
			rect = { COLUMN_RIGHT - 2, TOP + 2, 2, PAGE_BOTTOM - TOP - 4 },
			variant = "hairline",
			zIndex = Z - 1,
		})
		pageX = COLUMN_RIGHT + 14
		self.screen:SetDefaultSelection(built[1].control.hit)
	end
	local pageW = W - PAD - pageX
	self.pageRect = { pageX, TOP, pageW, PAGE_BOTTOM - TOP }
	self.scroll = Kit.Scroll.new(v, {
		name = "List",
		rect = self.pageRect,
		gap = 8,
		padBottom = 10,
		zIndex = Z,
	})
	self.list = self.scroll:Content()
	self.contentW = pageW - RAIL
	self.status = Kit.Text.new(v, {
		name = "Status",
		rect = { pageX, H - PAD - STATUS_H, pageW, STATUS_H },
		text = "",
		role = "bodySoft",
		textSize = 17,
		scaled = true,
		zIndex = Z,
	})
	self.screen:Watch()
	return self
end

-- Header -----------------------------------------------------------------------------------

-- Highlights tab `id` (scripted: onTab is not called). A new tab starts at the
-- top of its page.
function ListWindow:SetTab(id: string?)
	if self.tabGroup and id then
		if self.tabGroup:Selected() ~= id then
			self.list.CanvasPosition = Vector2.new(0, 0)
		end
		self.tabGroup:Select(id)
	end
end

function ListWindow:SetTitle(text: string)
	self.frame:SetTitle(text)
end

-- The line along the bottom; tone as Line's.
function ListWindow:SetStatus(text: string?, toneName: string?)
	self.status:SetText(text or "")
	self.status:SetColor(if toneName then tone(toneName) else "inkSoft")
end

-- Coins and Gems pills in the header, left of the close button.
function ListWindow:SetCurrencies(coins: number, gems: number)
	if self.pills == nil then
		local right = W - 22 - 60 - 24
		self.pills = {
			gems = Kit.CurrencyPill.new(self.visual, {
				name = "Gems",
				rect = { right - 128, 26, 128, 46 },
				currency = "gems",
				value = gems,
				zIndex = Z,
			}),
			coins = Kit.CurrencyPill.new(self.visual, {
				name = "Coins",
				rect = { right - 128 - 12 - 140, 26, 140, 46 },
				currency = "coins",
				value = coins,
				zIndex = Z,
			}),
		}
		return
	end
	self.pills.coins:SetValue(coins)
	self.pills.gems:SetValue(gems)
end

-- The page ---------------------------------------------------------------------------------

-- Clears the page before a controller redraws it. Remembers which button had
-- the gamepad's focus so Finish() can give it back.
function ListWindow:Begin()
	local focus = GuiService.SelectedObject
	self.focusKey = nil
	self.hadFocus = focus ~= nil and focus:IsDescendantOf(self.screen.gui)
	if self.hadFocus then
		for _, entry in self.buttons do
			if entry.button.control.hit == focus then
				self.focusKey = entry.id
			end
		end
	end
	self.parts:Clean()
	self.parts = Kit.Core.Maid()
	table.clear(self.buttons)
	for _, child in self.list:GetChildren() do
		if child:IsA("GuiObject") then
			child:Destroy()
		end
	end
	self.order = 0
	self.height = 0
end

-- After a redraw: the focused button again (same row and key), else the first
-- one, else the first tab or the close button.
function ListWindow:Finish()
	self.scroll:SetContentHeight(self.height)
	local first, match = nil, nil
	for _, entry in self.buttons do
		if entry.button.control.flags.enabled ~= false then
			first = first or entry.button.control.hit
			if entry.id == self.focusKey then
				match = entry.button.control.hit
			end
		end
	end
	if not self.hadFocus or (GuiService.SelectedObject and GuiService.SelectedObject.Parent) then
		return
	end
	GuiService.SelectedObject = match or first or self.close.control.hit
end

function ListWindow:_next(height: number): number
	self.order += 1
	self.height += height + (if self.order > 1 then 8 else 0)
	return self.order
end

-- A layout-only holder in the list (transparent; the kit parts draw).
function ListWindow:_holder(name: string, height: number): Frame
	local order = self:_next(height)
	return Kit.Core.Make("Frame", {
		Name = name,
		BackgroundTransparency = 1,
		LayoutOrder = order,
		Size = UDim2.fromOffset(self.contentW, height),
		ZIndex = Z,
	}, self.list)
end

-- Remembers a button so Finish can give its focus back after a redraw.
function ListWindow:_button(parent: Instance, rowKey: string, spec, rect)
	local button = Kit.Button.new(parent, {
		name = spec.key or spec.label,
		rect = rect,
		label = spec.label,
		variant = if spec.kind == "paper" then "secondary" else "primary",
		sizeClass = "s",
		zIndex = Z + 2,
		onPress = function()
			spec.onPress()
		end,
	})
	button:SetEnabled(spec.enabled ~= false)
	self.parts:Give(button)
	table.insert(self.buttons, { id = rowKey .. "/" .. (spec.key or spec.label), button = button })
	return button
end

-- A section header (capitals, an optional icon, the ink rule).
function ListWindow:Section(text: string, icon: string?)
	local holder = self:_holder("Section" .. text, 46)
	self.parts:Give(Kit.SectionHeader.new(holder, {
		name = "Header",
		rect = { 4, 8, self.contentW - 8, 34 },
		text = text,
		icon = icon,
		zIndex = Z + 1,
	}))
end

-- A wrapping paragraph. tone: "ink", "soft" (default), "good", "warn", "gold".
-- Returns its TextLabel (a countdown rewrites it).
function ListWindow:Line(text: string, toneName: string?, size: number?): TextLabel
	local px = size or LINE_SIZE
	local width = self.contentW - 12
	local height = ListWindow.Lines(text, "body", px, width) * lineHeight(px) + 4
	local holder = self:_holder("Line" .. (self.order + 1), height)
	local label = Kit.Text.new(holder, {
		name = "Text",
		rect = { 6, 0, width, height },
		text = text,
		role = "body",
		textSize = px,
		color = tone(toneName or "soft"),
		wrap = true,
		yAlign = "Top",
		zIndex = Z + 1,
	})
	return label.root
end

-- One soft card. spec: key (stable name), title, tone? (title tone), detail?
-- (wraps), icon? (item catalogId: its art) and/or glyph? (icon id: shown when
-- there is no item art), bar? ({value = 0-1, fill?}), value? (text) with
-- valueIcon? ("coin" | "gem" | another icon id), buttons? ({{label, key,
-- enabled, onPress, kind = "paper" | "leather"}}), done? (true: a ticked ring;
-- false with no buttons: an empty ring). Returns the card's root.
function ListWindow:Row(spec)
	local w = self.contentW
	local key = spec.key or spec.title
	local buttons = spec.buttons or {}
	local hasArt = spec.icon ~= nil or spec.glyph ~= nil
	local textX = if hasArt then 18 + ICON + 16 else 22
	-- The right side, from the edge inwards: buttons, a ring, the value.
	local right = 18
	local widths = {}
	for index, button in buttons do
		widths[index] = buttonWidth(button.label)
		right += widths[index] + (if index > 1 then 10 else 0)
	end
	local ring = spec.done == true or (spec.done == false and #buttons == 0)
	if ring then
		right += (if #buttons > 0 then 12 else 0) + 34
	end
	local valueW = 0
	if spec.value then
		valueW = math.ceil(Kit.Text.Width(spec.value, "value", 19)) + 6 + (if spec.valueIcon then 36 else 0)
		right += valueW + 16
	end
	local textW = w - textX - right - 12
	local hasDetail = spec.detail ~= nil and spec.detail ~= ""
	local detailH = if hasDetail
		then ListWindow.Lines(spec.detail, "body", DETAIL_SIZE, textW) * lineHeight(DETAIL_SIZE)
		else 0
	local content = TITLE_H + (if hasDetail then 4 + detailH else 0) + (if spec.bar then 10 + BAR_H else 0)
	local h = math.max(ListWindow.ROW_HEIGHT, content + 28)
	local order = self:_next(h)
	local card = Kit.Panel.new(self.list, {
		name = key,
		size = { w, h },
		layoutOrder = order,
		variant = "inset",
		pad = 0,
		zIndex = Z,
	})
	self.parts:Give(card)
	local c = card:Content()
	if hasArt then
		local rect = { 18, (h - ICON) / 2, ICON, ICON }
		if spec.icon then
			Kit.ItemIcon.new(c, { name = "Icon", rect = rect, itemId = spec.icon, icon = spec.glyph, zIndex = Z + 1 })
		else
			Kit.Icon.new(c, { name = "Icon", rect = rect, icon = spec.glyph, zIndex = Z + 1 })
		end
	end
	local y = (h - content) / 2
	Kit.Text.new(c, {
		name = "Title",
		rect = { textX, y, textW, TITLE_H },
		text = spec.title,
		role = "rowTitle",
		textSize = 20,
		color = tone(spec.tone),
		scaled = true,
		zIndex = Z + 1,
	})
	y += TITLE_H
	if hasDetail then
		Kit.Text.new(c, {
			name = "Detail",
			rect = { textX, y + 4, textW, detailH },
			text = spec.detail,
			role = "body",
			textSize = DETAIL_SIZE,
			wrap = true,
			yAlign = "Top",
			zIndex = Z + 1,
		})
		y += 4 + detailH
	end
	if spec.bar then
		Kit.Bar.new(c, {
			name = "Bar",
			rect = { textX, y + 10, math.min(textW, 420), BAR_H },
			fill = spec.bar.fill or "xp",
			frame = "track",
			value = spec.bar.value,
			zIndex = Z + 1,
		})
	end
	local x = w - 18
	for index = #buttons, 1, -1 do
		local bw = widths[index]
		x -= bw
		self:_button(c, key, buttons[index], { x, (h - BUTTON_H) / 2, bw, BUTTON_H })
		x -= 10
	end
	if #buttons > 0 then
		x += 10
	end
	if ring then
		x -= (if #buttons > 0 then 12 else 0) + 34
		Kit.Checkbox.new(c, {
			name = "Done",
			rect = { x, (h - 34) / 2, 34, 34 },
			variant = "ring",
			readOnly = true,
			checked = spec.done == true,
			zIndex = Z + 1,
		})
	end
	if spec.value then
		x -= 16 + valueW
		local textLeft = x
		if spec.valueIcon then
			Kit.Icon.new(c, { name = "ValueIcon", rect = { x, (h - 30) / 2, 30, 30 }, icon = spec.valueIcon, zIndex = Z + 1 })
			textLeft += 36
		end
		Kit.Text.new(c, {
			name = "Value",
			rect = { textLeft, 0, valueW - (textLeft - x), h },
			text = spec.value,
			role = "value",
			textSize = 19,
			zIndex = Z + 1,
		})
	end
	return card.root
end

-- A row of buttons, right-aligned: {{label, key, enabled, onPress, kind, width?}}.
function ListWindow:Buttons(specs)
	local holder = self:_holder("Buttons" .. (self.order + 1), BUTTON_H + 6)
	local x = self.contentW - 4
	for index = #specs, 1, -1 do
		local spec = specs[index]
		local bw = math.max(spec.width or 0, buttonWidth(spec.label))
		x -= bw
		self:_button(holder, "Buttons", spec, { x, 3, bw, BUTTON_H })
		x -= 12
	end
	return holder
end

-- A text field with a label before it (the stepper's value field art with a
-- TextBox on it). onSubmit(text) runs when focus leaves with Enter and text
-- typed (or on any focus loss, even empty, when `always`); `submit` adds a
-- button that submits typed text.
function ListWindow:Input(label: string, placeholder: string, onSubmit, always: boolean?, submit: string?): TextBox
	local holder = self:_holder("Input" .. (self.order + 1), 60)
	Kit.Text.new(holder, {
		name = "Label",
		rect = { 6, 0, 260, 60 },
		text = label,
		role = "rowTitle",
		textSize = 20,
		zIndex = Z + 1,
	})
	local fieldRect = { 276, 6, 340, 48 }
	self.parts:Give(Kit.Picture.new(holder, { name = "Field", rect = fieldRect, role = "field.value", zIndex = Z + 1 }))
	local box = Kit.Core.Make("TextBox", {
		Name = "Box",
		BackgroundTransparency = 1,
		ClearTextOnFocus = false,
		PlaceholderText = placeholder,
		Position = UDim2.fromOffset(fieldRect[1] + 16, fieldRect[2]),
		Size = UDim2.fromOffset(fieldRect[3] - 32, fieldRect[4]),
		Text = "",
		TextTruncate = Enum.TextTruncate.AtEnd,
		TextXAlignment = Enum.TextXAlignment.Left,
		ZIndex = Z + 3,
	}, holder) :: TextBox
	Kit.Core.Style(box, "rowLabel", "ink")
	box.TextSize = 19
	box.PlaceholderColor3 = Kit.Tokens.Color("placeholder")
	self.parts:Give(box.FocusLost:Connect(function(enter)
		if always or (enter and box.Text ~= "") then
			onSubmit(box.Text)
		end
	end))
	if submit then
		self:_button(holder, "Input", {
			label = submit,
			key = "Submit",
			onPress = function()
				if box.Text ~= "" then
					onSubmit(box.Text)
				end
			end,
		}, { fieldRect[1] + fieldRect[3] + 14, 9, buttonWidth(submit), BUTTON_H })
	end
	return box
end

-- Two offer panels side by side (a trade). Each side: {title, icon?, items =
-- {{itemId?, name, quantity?}}, gems, state = "open" | "locked" | "confirmed",
-- emptyText?}. Items are slots with their names under them; Gems a pill.
function ListWindow:Pair(left, right)
	local gap = 14
	local pw = math.floor((self.contentW - gap) / 2)
	local perRow = math.max(1, math.floor((pw - 32 + (SLOT_PITCH - SLOT)) / SLOT_PITCH))
	local function bodyHeight(side): number
		local rows = math.ceil(#side.items / perRow)
		local h = rows * (SLOT + CAPTION_H + 8)
		if #side.items == 0 then
			h = 34
		end
		if (side.gems or 0) > 0 then
			h += 56
		end
		return h
	end
	local h = 12 + 36 + 12 + math.max(bodyHeight(left), bodyHeight(right)) + 16
	local holder = self:_holder("Pair", h)
	for index, side in { left, right } do
		local panel = Kit.Panel.new(holder, {
			name = if index == 1 then "Left" else "Right",
			rect = { (index - 1) * (pw + gap), 0, pw, h },
			variant = "inset",
			title = side.title,
			icon = side.icon,
			zIndex = Z,
		})
		self.parts:Give(panel)
		local v = panel.base.visual
		local state = side.state or "open"
		local badge = Kit.Badge.new(v, {
			name = "State",
			variant = if state == "open" then "notReady" else "ready",
			text = if state == "confirmed" then "Confirmed" elseif state == "locked" then "Locked" else "Not locked",
			rect = { 0, 12, 0, 32 },
			zIndex = Z + 3,
		})
		badge.root.AnchorPoint = Vector2.new(1, 0)
		badge.root.Position = UDim2.fromOffset(pw - 18, 12)
		self.parts:Give(badge)
		local c = panel:Content()
		if #side.items == 0 then
			Kit.Text.new(c, {
				name = "Empty",
				rect = { 4, 0, pw - 40, 34 },
				text = side.emptyText or "Nothing yet.",
				role = "muted",
				zIndex = Z + 1,
			})
		end
		for i, item in side.items do
			local col, row = (i - 1) % perRow, (i - 1) // perRow
			local x, y = col * SLOT_PITCH, row * (SLOT + CAPTION_H + 8)
			local slot = Kit.Slot.new(c, {
				name = "Item" .. i,
				rect = { x, y, SLOT, SLOT },
				zIndex = Z + 1,
			})
			slot:SetItem({ itemId = item.itemId, quantity = item.quantity })
			self.parts:Give(slot)
			Kit.Text.new(c, {
				name = "Name" .. i,
				rect = { x - 4, y + SLOT + 1, SLOT + 8, CAPTION_H },
				text = item.name,
				role = "small",
				align = "Center",
				scaled = true,
				zIndex = Z + 1,
			})
		end
		if (side.gems or 0) > 0 then
			local pill = Kit.CurrencyPill.new(c, {
				name = "Gems",
				rect = { 0, panel.contentRect[4] - 48, 150, 46 },
				currency = "gems",
				value = side.gems,
				zIndex = Z + 1,
			})
			self.parts:Give(pill)
		end
	end
	return holder
end

-- Questions -------------------------------------------------------------------------------

-- Asks before something that cannot be undone, in a Kit.ConfirmDialog over the
-- window. `delay` > 0 makes the confirm button a press-and-hold of that many
-- seconds (the old "read first" guard). opts: title, rows ({{label, text}}:
-- labelled paragraphs instead of `text`), size, danger.
function ListWindow:Confirm(text: string, yes: string, delay: number, onYes, opts)
	opts = opts or {}
	self:HideConfirm()
	local handle
	local function build(body: Frame, bw: number, bh: number)
		local y = 0
		for index, row in opts.rows or {} do
			Kit.Text.new(body, {
				name = "Label" .. index,
				rect = { 0, y, bw, 24 },
				text = row.label,
				role = "sectionHeader",
				textSize = 17,
				zIndex = Z + 20,
			})
			y += 24
			local lines = ListWindow.Lines(row.text, "body", 16, bw)
			local th = lines * lineHeight(16)
			Kit.Text.new(body, {
				name = "Text" .. index,
				rect = { 0, y, bw, th },
				text = row.text,
				role = "body",
				textSize = 16,
				wrap = true,
				yAlign = "Top",
				zIndex = Z + 20,
			})
			y += th + 8
		end
		if y > bh then
			body.ClipsDescendants = true
		end
	end
	handle = Kit.ConfirmDialog.Show({
		title = opts.title or yes,
		text = if opts.rows then nil else text,
		build = if opts.rows then build else nil,
		size = opts.size,
		danger = opts.danger,
		confirmLabel = yes,
		holdSeconds = if delay > 0 then delay else nil,
		onConfirm = function(dialog)
			dialog:SetBusy(true)
			task.spawn(function()
				onYes()
				handle.Close()
			end)
		end,
	})
	self.confirm = handle
	return handle
end

function ListWindow:HideConfirm()
	local handle = self.confirm
	self.confirm = nil
	if handle and not handle.dialog.closed then
		handle.Close()
	end
end

function ListWindow:IsConfirming(): boolean
	return self.confirm ~= nil and not self.confirm.dialog.closed
end

-- Opening and closing ------------------------------------------------------------------------

function ListWindow:Open(gamepad: boolean?)
	self:HideConfirm()
	self.screen:Open(gamepad)
end

function ListWindow:Close()
	self:HideConfirm()
	self.screen:Close()
end

function ListWindow:IsOpen(): boolean
	return self.screen:IsOpen()
end

return ListWindow
