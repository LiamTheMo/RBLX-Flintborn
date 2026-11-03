-- The shared list window for the screens with no mockup of their own (Market,
-- Trade, Progress; spec docs/ui/ListWindows.md, ARCHITECTURE §4.8), built only
-- from the UI kit so they read as the same game as the lobby windows: the
-- banner header (icon, title, rule, close) with optional Coins / Gems pills,
-- an optional category tab column on the left (as the Inventory's), and a
-- scrolling page the controller fills with section headers, text lines, soft
-- cards (item art or an icon, title, wrapping detail, an optional bar, a price
-- with its coin or gem, buttons, a round check), cards with their own quantity
-- (a slider and a stepper, the live total, one button), button rows, a text
-- field and paired offer panels of slots. A status line runs along the bottom; questions
-- go to a Kit.ConfirmDialog (press-and-hold where a delay guarded them).
--
-- Display only: controllers redraw the page (Begin … Finish) and decide what
-- every press does. Positions are design px in the window (SIZE). A page taller
-- than its area ends between two rows (the list's bottom edge never cuts a
-- line of text); the rail shows there is more. A gamepad lands on the selected
-- tab, else the first enabled button (SetDefaultSelection overrides it).
--
--   local window = ListWindow.new(playerGui, { name = "FlintbornMarket", title = "Market", icon = "market",
--       tabs = { { id = "Buy", label = "Buy", icon = "market" } }, onTab = show, onClose = close })
--   window:Begin()
--   window:Section("Tools")
--   window:Row({ key = "Axe", title = "Stone Axe", icon = "StoneAxe", value = "40", valueIcon = "coin",
--       buttons = { { label = "Buy", key = "Buy", onPress = buy } } })
--   window:Finish()

local GuiService = game:GetService("GuiService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local HudModel = require(ReplicatedStorage.Shared.UI.HudModel)
local Kit = require(script.Parent.Kit)
local NoticeCard = require(script.Parent.NoticeCard)

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

-- How many lines `text` wraps to in `width` design px (NoticeCard.Lines, with a
-- little slack for the engine's own wrapping and a space never under 0.28 of
-- the text size).
function ListWindow.Lines(text: string, role: string, size: number?, width: number): number
	return NoticeCard.Lines(text, role, width * 0.95, size, (size or 16) * 0.28)
end

local function lineHeight(size: number): number
	return math.ceil(size * 1.32)
end

local function buttonWidth(label: string): number
	return Kit.Button.Width(label, 104, 44)
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
	-- The page's quantity rows by key (QuantityRow handles), for flows and verifiers.
	self.quantities = {}
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
	end
	local pageW = W - PAD - pageX
	self.pageRect = { pageX, TOP, pageW, PAGE_BOTTOM - TOP }
	self.bottoms = {}
	self:_makeScroll(self.pageRect[4])
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
	self:_applyDefault()
	return self
end

-- The page's scroll list at `height` (at most the page area), keeping the rows
-- and the scroll position of the one it replaces.
function ListWindow:_makeScroll(height: number)
	local old = self.scroll
	local r = self.pageRect
	self.scroll = Kit.Scroll.new(self.visual, {
		name = "List",
		rect = { r[1], r[2], r[3], height },
		gap = 8,
		padBottom = 10,
		zIndex = Z,
	})
	self.scrollH = height
	local list = self.scroll:Content()
	if old then
		local oldList = self.list
		for _, child in oldList:GetChildren() do
			if child:IsA("GuiObject") then
				child.Parent = list
			end
		end
		list.CanvasPosition = oldList.CanvasPosition
		old.root:Destroy()
	end
	self.list = list
end

-- The list's height for the page drawn: the whole area, or (when the page is
-- taller) down to the end of the last row that fits whole.
function ListWindow:_snapHeight(): number
	local area = self.pageRect[4]
	if self.height + 14 <= area then
		return area
	end
	local best = 0
	for _, bottom in self.bottoms do
		-- 2 px of list padding above the first row, 4 px of air under the last.
		if 2 + bottom + 4 <= area then
			best = math.max(best, 2 + bottom + 4)
		end
	end
	-- Very tall rows: keep the whole area rather than a short list.
	return if best >= area * 0.6 then best else area
end

-- The control a gamepad lands on when the window opens (nil: the selected
-- tab, else the first enabled button, else the close button).
function ListWindow:SetDefaultSelection(object: GuiObject?)
	self.defaultOverride = object
	self:_applyDefault()
end

function ListWindow:_applyDefault()
	local default = self.defaultOverride
	if default == nil and self.tabGroup then
		local tab = self.tabs[self.tabGroup:Selected() or ""]
		default = tab and tab.control.hit
	end
	if default == nil then
		for _, entry in self.buttons do
			if entry.button.control.flags.enabled ~= false then
				default = entry.button.control.hit
				break
			end
		end
	end
	self.screen:SetDefaultSelection(default or self.close.control.hit)
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
		self:_applyDefault()
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
	table.clear(self.quantities)
	for _, child in self.list:GetChildren() do
		if child:IsA("GuiObject") then
			child:Destroy()
		end
	end
	self.order = 0
	self.height = 0
	table.clear(self.bottoms)
end

-- After a redraw: the focused button again (same row and key), else the first
-- one, else the first tab or the close button.
function ListWindow:Finish()
	local height = self:_snapHeight()
	if height ~= self.scrollH then
		self:_makeScroll(height)
	end
	self.scroll:SetContentHeight(self.height)
	-- The engine measures the canvas itself (AutomaticCanvasSize); this floor
	-- is the same sum, for where nothing measures (captures).
	self.list.CanvasSize = UDim2.fromOffset(0, self.height + 14)
	self:_applyDefault()
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
	table.insert(self.bottoms, self.height)
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
			Kit.Icon.new(
				c,
				{ name = "ValueIcon", rect = { x, (h - 30) / 2, 30, 30 }, icon = spec.valueIcon, zIndex = Z + 1 }
			)
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

-- The quantity row's layout, design px in the card: the title at `top`, the
-- detail `detailGap` under it, then `gap` and the control line (`lineH`), which
-- holds a slider, a stepper, the total and the action button, `bottom` above
-- the card's edge (126 tall with a one-line detail: a Line, a Section and three
-- rows fill the Market's page). On a 667 × 375 phone (window scale 0.448) a
-- control's touch pad is 98 px: the slider ends `sliderGap` before the stepper
-- (its band reaches 15 px past the track, the stepper's − pad 27 px), and a row
-- with no control line is at least `minH` tall, so its button's pad clears the
-- pads of a control line above it. No two pads overlap, in a row or across rows.
local QROW = {
	top = 12,
	detailGap = 2,
	gap = 8,
	lineH = 44,
	bottom = 12,
	stepperW = 160,
	stepperGap = 6,
	sliderGap = 48,
	sliderH = 34,
	totalGap = 24,
	minH = 114,
}

-- One soft card with its own quantity (the Market's Sell rows): item art, the
-- title and a wrapping detail, and under them a line of controls: a Kit.Slider
-- and a Kit.Stepper (− value +) kept in step, the live total (a coin or gem and
-- each × quantity) and one action button. With only one to choose (max <= min)
-- there is no control line: the total sits by the button, as a Row's price.
-- spec: key, title, detail?, icon? (catalogId) / glyph?, min (1), max, value
-- (default max), each, currency ("coins" | "gems"), action = {label, key?,
-- enabled?, onPress(quantity, button)}, onChange?(quantity). The quantity is
-- clamped to min..max here. The slider stays out of gamepad selection (the
-- stepper's − and + do its job). Returns a handle: root, Quantity(),
-- SetQuantity(n), slider?, stepper?, button.
function ListWindow:QuantityRow(spec)
	local w = self.contentW
	local key = spec.key or spec.title
	local min = spec.min or 1
	local max = math.max(min, math.floor(spec.max or min))
	local quantity = math.clamp(math.floor(spec.value or max), min, max)
	local each = spec.each or 0
	local choose = max > min
	local action = spec.action
	local buttonW = buttonWidth(action.label)
	local textX = 18 + ICON + 16
	local buttonX = w - 18 - buttonW
	local totalRight = buttonX - 16
	-- The total's room fits a five-digit total, or the largest this row can
	-- show (measured with the phone boost), so the stepper never moves and
	-- lines up from row to row; the coin moves with the number, beside the
	-- button.
	local function valueWidth(text: string): number
		return math.ceil(Kit.Text.Width(text, "value", 19)) + 6
	end
	local totalW = 30 + math.max(valueWidth("00,000"), valueWidth(HudModel.Thousands(each * max)))
	local textW = if choose then w - textX - 22 else totalRight - totalW - 16 - textX
	local hasDetail = spec.detail ~= nil and spec.detail ~= ""
	local detailH = if hasDetail
		then ListWindow.Lines(spec.detail, "body", DETAIL_SIZE, textW) * lineHeight(DETAIL_SIZE)
		else 0
	local head = TITLE_H + (if hasDetail then QROW.detailGap + detailH else 0)
	local h, lineY, titleY
	if choose then
		h = QROW.top + head + QROW.gap + QROW.lineH + QROW.bottom
		lineY = h - QROW.bottom - QROW.lineH / 2
		titleY = QROW.top
	else
		h = math.max(QROW.minH, head + 28)
		lineY = h / 2
		titleY = (h - head) / 2
	end
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
	local artRect = { 18, (h - ICON) / 2, ICON, ICON }
	if spec.icon then
		Kit.ItemIcon.new(c, { name = "Icon", rect = artRect, itemId = spec.icon, icon = spec.glyph, zIndex = Z + 1 })
	elseif spec.glyph then
		Kit.Icon.new(c, { name = "Icon", rect = artRect, icon = spec.glyph, zIndex = Z + 1 })
	end
	Kit.Text.new(c, {
		name = "Title",
		rect = { textX, titleY, textW, TITLE_H },
		text = spec.title,
		role = "rowTitle",
		textSize = 20,
		scaled = true,
		zIndex = Z + 1,
	})
	if hasDetail then
		Kit.Text.new(c, {
			name = "Detail",
			rect = { textX, titleY + TITLE_H + QROW.detailGap, textW, detailH },
			text = spec.detail,
			role = "body",
			textSize = DETAIL_SIZE,
			wrap = true,
			yAlign = "Top",
			zIndex = Z + 1,
		})
	end
	local handle = { root = card.root }
	handle.button = self:_button(c, key, {
		label = action.label,
		key = action.key,
		enabled = action.enabled,
		onPress = function()
			action.onPress(quantity, handle.button)
		end,
	}, { buttonX, lineY - BUTTON_H / 2, buttonW, BUTTON_H })
	local totalIcon = Kit.Icon.new(c, {
		name = "TotalIcon",
		rect = { 0, lineY - 15, 30, 30 },
		icon = if spec.currency == "gems" then "gem" else "coin",
		zIndex = Z + 1,
	})
	local totalText = Kit.Text.new(c, {
		name = "Total",
		rect = { 0, lineY - 20, 48, 40 },
		text = "",
		role = "value",
		textSize = 19,
		align = "Right",
		scaled = true,
		zIndex = Z + 1,
	})
	local function layoutTotal()
		local value = HudModel.Thousands(each * quantity)
		totalText:SetText(value)
		local vw = valueWidth(value)
		totalText.root.Position = UDim2.fromOffset(totalRight - vw, lineY - 20)
		totalText.root.Size = UDim2.fromOffset(vw, 40)
		totalIcon.root.Position = UDim2.fromOffset(totalRight - vw - 30, lineY - 15)
		card.root:SetAttribute("KitValue", quantity)
	end
	local stepper, slider
	local function set(value: number, from: string?)
		local before = quantity
		quantity = math.clamp(math.floor(value + 0.5), min, max)
		if stepper and from ~= "stepper" then
			stepper:SetValue(quantity)
		end
		if slider and from ~= "slider" then
			slider:SetValue(quantity)
		end
		layoutTotal()
		if quantity ~= before and spec.onChange then
			spec.onChange(quantity)
		end
	end
	if choose then
		local stepperX = totalRight - totalW - QROW.totalGap - QROW.stepperW
		stepper = Kit.Stepper.new(c, {
			name = "Quantity",
			rect = { stepperX, lineY - QROW.lineH / 2, QROW.stepperW, QROW.lineH },
			min = min,
			max = max,
			value = quantity,
			gap = QROW.stepperGap,
			zIndex = Z + 1,
			onChange = function(value)
				set(value, "stepper")
			end,
		})
		self.parts:Give(stepper)
		slider = Kit.Slider.new(c, {
			name = "Slider",
			rect = { textX, lineY - QROW.sliderH / 2, stepperX - QROW.sliderGap - textX, QROW.sliderH },
			min = min,
			max = max,
			step = 1,
			value = quantity,
			valueBox = false,
			selectable = false,
			touchBand = true,
			zIndex = Z + 1,
			onChange = function(value)
				set(value, "slider")
			end,
		})
		self.parts:Give(slider)
	end
	layoutTotal()
	handle.slider = slider
	handle.stepper = stepper
	handle.Quantity = function(): number
		return quantity
	end
	handle.SetQuantity = function(value: number)
		set(value)
	end
	self.quantities[key] = handle
	return handle
end

-- A player row (portrait, name, level and an action button), as the Party
-- window's invite list: {key, userId, name, level?, action? = {label, key?,
-- onPress, enabled?}}.
function ListWindow:Player(spec)
	local order = self:_next(64)
	local row = Kit.PlayerRow.new(self.list, {
		size = { self.contentW - 8, 64 },
		layoutOrder = order,
		userId = spec.userId,
		name = spec.name,
		level = spec.level,
		action = spec.action and {
			label = spec.action.label,
			enabled = spec.action.enabled,
			onPress = function()
				spec.action.onPress()
			end,
		},
		zIndex = Z,
	})
	self.parts:Give(row)
	-- `name` is the player's; the instance takes the row's key.
	row.root.Name = spec.key
	if row.action then
		row.action.root.Name = spec.action.key or spec.action.label
		table.insert(self.buttons, { id = spec.key .. "/" .. row.action.root.Name, button = row.action })
	end
	return row.root
end

-- A row of buttons, right-aligned: {{label, key, enabled, onPress, kind, width?}}.
function ListWindow:Buttons(specs)
	local holder = self:_holder("Buttons", BUTTON_H + 6)
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

-- A text field with a label before it (Kit.TextField: the value box with a
-- TextBox, its touch pad grown to 44 screen px). onSubmit(text) runs when focus
-- leaves with Enter and text typed (or on any focus loss, even empty, when
-- `always`); `submit` adds a button that submits typed text. Returns the TextBox.
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
	local field = Kit.TextField.new(holder, {
		name = "Field",
		rect = fieldRect,
		placeholder = placeholder,
		textSize = 19,
		clearButton = false,
		zIndex = Z + 1,
	})
	self.parts:Give(field)
	local box = field.box :: TextBox
	box.Name = "Box"
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
-- {{itemId?, name, quantity?, permanent?}}, gems, state = "open" | "locked" |
-- "confirmed", emptyText?}. Items are slots (a Permanent one with the star art)
-- with their names under them; Gems a pill.
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
			slot:SetItem({ itemId = item.itemId, quantity = item.quantity, permanent = item.permanent == true })
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

ListWindow.QUANTITY_SIZE = { 620, 480 }

-- The quantity body's layout, design px in the dialog body (ConfirmDialog's
-- body box: 44 in from the sides, 104 down). The stepper's and the slider's
-- touch pads (44 screen px each at a phone's dialog scale) must not overlap,
-- hence the gap between them.
local QTY = { icon = 64, stepperY = 74, stepperW = 330, stepperH = 48, sliderY = 174, sliderH = 34, totalY = 222 }

-- Asks how many before a purchase (the Buy tab; Sell rows carry their own
-- quantity, QuantityRow): the item's picture and name, a line under it (the
-- price each, what one buys), a stepper (− value + Max) and
-- a slider kept in step, and the live total with its coin, over Cancel and the
-- confirm button. opts: title, itemId? (catalogId: its art) / glyph? (icon id),
-- name, detail?, min (1), max, value (1), each (price per one), currency
-- ("coins" | "gems"), confirmLabel, onConfirm(quantity). The quantity is
-- clamped to min..max here; the server checks it again. Returns the handle.
function ListWindow:Quantity(opts)
	self:HideConfirm()
	local min = opts.min or 1
	local max = math.max(min, math.floor(opts.max or min))
	local quantity = math.clamp(math.floor(opts.value or min), min, max)
	local each = opts.each or 0
	local handle
	local stepper, slider, totalLabel, totalIcon, totalText
	local bodyW = 0
	local function layoutTotal()
		local value = HudModel.Thousands(each * quantity)
		totalText:SetText(value)
		local tw = Kit.Text.Width("Total", "rowTitle", 20)
		local vw = Kit.Text.Width(value, "value", 22)
		local group = tw + 14 + 30 + 6 + vw
		local x = math.max(0, (bodyW - group) / 2)
		totalLabel.root.Position = UDim2.fromOffset(x, QTY.totalY)
		totalLabel.root.Size = UDim2.fromOffset(tw + 4, 40)
		totalIcon.root.Position = UDim2.fromOffset(x + tw + 14, QTY.totalY + 5)
		totalText.root.Position = UDim2.fromOffset(x + tw + 14 + 36, QTY.totalY)
		totalText.root.Size = UDim2.fromOffset(math.max(40, vw + 8), 40)
	end
	local function set(value: number, from: string?)
		quantity = math.clamp(math.floor(value + 0.5), min, max)
		if from ~= "stepper" then
			stepper:SetValue(quantity)
		end
		if from ~= "slider" then
			slider:SetValue(quantity)
		end
		layoutTotal()
	end
	local function build(body: Frame, bw: number, _bh: number)
		bodyW = bw
		local iconRect = { 0, 0, QTY.icon, QTY.icon }
		if opts.itemId then
			Kit.ItemIcon.new(
				body,
				{ name = "Icon", rect = iconRect, itemId = opts.itemId, icon = opts.glyph, zIndex = Z + 20 }
			)
		elseif opts.glyph then
			Kit.Icon.new(body, { name = "Icon", rect = iconRect, icon = opts.glyph, zIndex = Z + 20 })
		end
		local textX = QTY.icon + 16
		Kit.Text.new(body, {
			name = "Name",
			rect = { textX, 2, bw - textX, 30 },
			text = opts.name or "",
			role = "rowTitle",
			textSize = 20,
			scaled = true,
			zIndex = Z + 20,
		})
		if opts.detail then
			Kit.Text.new(body, {
				name = "Detail",
				rect = { textX, 34, bw - textX, 28 },
				text = opts.detail,
				role = "bodySoft",
				textSize = 16,
				scaled = true,
				zIndex = Z + 20,
			})
		end
		stepper = Kit.Stepper.new(body, {
			name = "Quantity",
			rect = { (bw - QTY.stepperW) / 2, QTY.stepperY, QTY.stepperW, QTY.stepperH },
			min = min,
			max = max,
			value = quantity,
			allLabel = "Max",
			zIndex = Z + 20,
			onChange = function(value)
				set(value, "stepper")
			end,
		})
		slider = Kit.Slider.new(body, {
			name = "Slider",
			rect = { 12, QTY.sliderY, bw - 24, QTY.sliderH },
			min = min,
			max = max,
			step = 1,
			value = quantity,
			valueBox = false,
			touchBand = true,
			zIndex = Z + 20,
			onChange = function(value)
				set(value, "slider")
			end,
		})
		-- One to choose from: nothing to drag.
		slider:SetEnabled(max > min)
		totalLabel = Kit.Text.new(body, {
			name = "TotalLabel",
			rect = { 0, QTY.totalY, 80, 40 },
			text = "Total",
			role = "rowTitle",
			textSize = 20,
			zIndex = Z + 20,
		})
		totalIcon = Kit.Icon.new(body, {
			name = "TotalIcon",
			rect = { 0, QTY.totalY + 5, 30, 30 },
			icon = if opts.currency == "gems" then "gem" else "coin",
			zIndex = Z + 20,
		})
		totalText = Kit.Text.new(body, {
			name = "Total",
			rect = { 0, QTY.totalY, 80, 40 },
			text = "",
			role = "value",
			textSize = 22,
			zIndex = Z + 20,
		})
		layoutTotal()
	end
	handle = Kit.ConfirmDialog.Show({
		title = opts.title or opts.confirmLabel or "",
		build = build,
		size = ListWindow.QUANTITY_SIZE,
		confirmLabel = opts.confirmLabel or "Confirm",
		onConfirm = function(dialog)
			dialog:SetBusy(true)
			local chosen = quantity
			task.spawn(function()
				opts.onConfirm(chosen)
				handle.Close()
			end)
		end,
	})
	handle.Quantity = function(): number
		return quantity
	end
	handle.SetQuantity = function(value: number)
		set(value)
	end
	handle.stepper = stepper
	handle.slider = slider
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
