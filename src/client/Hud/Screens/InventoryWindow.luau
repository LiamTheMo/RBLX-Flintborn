-- The Inventory window (art/reference/ui/lobby/02_inventory.png,
-- docs/ui/InventoryScreen.md), built only from Kit parts: the banner header
-- with the backpack and the close button, two horizontal tabs (Backpack / Vault
-- in the lobby, Backpack / Equipped in a run) with a toolbar of extra buttons
-- beside them, the search box, the category column, a scrolling six-wide slot
-- grid in sections, and the detail card (big icon, name, description, stat rows,
-- an optional amount stepper or secondary buttons, and the main action).
--
-- Display only (ARCHITECTURE §2.1): controllers hand it data through setters and
-- hear presses through callbacks. It keeps the search and category filter
-- itself, since those only change what is drawn.
--
--   local window = InventoryWindow.new({ tabs = { { id = "Backpack", label = "Backpack", icon = "backpack" } },
--       onTab = showTab, onSlot = choose, onAction = act })
--   window:SetSections({ { id = "backpack", cells = cells } })
--   window:SetDetail({ catalogId = "StoneAxe", name = "Stone Axe", text = "...", rows = ItemInfo.StatRows(item),
--       actions = { { id = "store", label = "Store" } } })
--   window:Open()

local GuiService = game:GetService("GuiService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local ItemInfo = require(ReplicatedStorage.Shared.Items.ItemInfo)
local Kit = require(script.Parent.Parent.Kit)

local InventoryWindow = {}
InventoryWindow.__index = InventoryWindow

-- Design px (the mockup's window is 1187 × 652 at 243, 150).
InventoryWindow.SIZE = { 1187, 650 }

-- Category column icons: the closest kit art (KIT.md §8). The mockup's All is
-- a grid the kit lacks; the scroll (a list of everything) stands in, since
-- the chest read as the Vault.
InventoryWindow.CATEGORY_ICONS = {
	All = "scroll",
	Tools = "hammer",
	Materials = "stones",
	Food = "drumstick",
	Plants = "plant_fiber",
	Misc = "gift",
}

-- Slots 91 × 99 at a 99.6 × 107.33 pitch, the first at (250, 181).
local COLUMNS = 6
local CELL = { 91, 99 }
local PITCH = { 99.6, 107.33 }
-- The grid's scroll area: the slots start a few px in, so the selected glow
-- (3 px outside a slot) is not clipped, and the thin rail lands on the column
-- divider. Four rows show; more scroll.
local GRID = { 246, 176, 611, 429 }
local INSET = { 4, 3 }
local GRID_W = (COLUMNS - 1) * PITCH[1] + CELL[1]
local HEADER_H = 34
local CAPTION_H = 22
local SECTION_GAP = 12
local TAB_RECTS = { { 19, 108, 170, 58 }, { 198, 109, 165, 56 } }
-- Icon and label placement in each tab, measured from the mockup (the
-- backpack is tall, the chest wide).
local TAB_LAYOUT = { { iconX = 15, iconSize = 40, labelX = 65 }, { iconX = 19, iconSize = 44, labelX = 79 } }
-- Category rows (the mockup's spacing is uneven) and the rules under the
-- middle four.
local CATEGORY_YS = { 236, 297, 363, 426, 491, 555 }
local CATEGORY_RULES = { 354, 419, 483, 547 }
-- The detail card at the mockup's rect (the kit draws the inset art's border
-- on it); contents are placed from the card's corner.
local CARD_PAD = 0
local CARD = { 869 - CARD_PAD, 109 - CARD_PAD, 296 + CARD_PAD * 2, 520 + CARD_PAD * 2 }
local ROW_TOP, ROW_PITCH = 313, 41
-- A slot's rarity dot (bottom left, clear of the count, the Permanent star
-- and the hotkey badge; Uncommon and rarer) and the detail name's (any).
local SLOT_RARITY = { 9, CELL[2] - 21, 12, 12 }
local NAME_RARITY = 14

-- A rect in the card, from the mockup card's top-left corner.
local function inCard(x: number, y: number, w: number, h: number): { number }
	return { x + CARD_PAD, y + CARD_PAD, w, h }
end

export type Cell = {
	id: string,
	item: { catalogId: string, quantity: number?, permanent: boolean?, qualityRoll: number? }?,
	name: string?,
	hotkey: string?,
	caption: string?,
	state: string?,
}

export type Section = { id: string, title: string?, cells: { Cell }, emptyText: string? }

export type Action = { id: string, label: string, variant: string?, enabled: boolean? }

export type Detail = {
	hint: string?,
	catalogId: string?,
	name: string?,
	text: string?,
	item: any?,
	rows: { { icon: string, label: string, value: string } }?,
	actions: { Action }?,
	amount: { min: number, max: number, value: number, allLabel: string? }?,
}

-- props: tabs ({{id, label, icon, iconSelected?}}), onTab(id), onSlot(cellId),
-- onAction(actionId), onAmount(value), onToolbar(id), onClose(), name, parent.
function InventoryWindow.new(props)
	local w, h = InventoryWindow.SIZE[1], InventoryWindow.SIZE[2]
	local screen = Kit.Screen.new(props.name or "FlintbornInventory", { size = { w, h }, parent = props.parent })
	local self = setmetatable({
		props = props,
		screen = screen,
		tabDefs = props.tabs or {},
		tabs = {},
		toolbar = {},
		category = "All",
		query = "",
		sections = {},
		selectedId = nil,
		slots = {},
		slotCells = {},
		headers = {},
		captions = {},
		hints = {},
		busy = false,
	}, InventoryWindow)
	self.window = Kit.Window.new(screen, {
		title = "Inventory",
		icon = "backpack",
		clasps = "right",
		claspYs = { 0.18, 0.9 },
		-- The mockup's underline (370–1340 at y 235 on screen; the ends fade).
		ruleRect = { 113, 78, 995, 16 },
		-- Measured from the mockup: the backpack, the title's cap height (32 px)
		-- and the close button.
		iconRect = { 40, 15, 71, 77 },
		titleX = 138,
		titleSize = 44,
		closeRect = { 1103, 18, 60, 57 },
		onClose = function()
			screen:Close()
		end,
	})
	local v = self.window.base.visual
	self.visual = v

	self.search = Kit.SearchBox.new(v, {
		name = "Search",
		rect = { 23, 179, 215, 41 },
		placeholder = "Search items...",
		zIndex = 8,
		onChanged = function(text)
			self:_setQuery(text)
		end,
	})

	local categories = {}
	for index, id in ItemInfo.CATEGORIES do
		local y = CATEGORY_YS[index] or (CATEGORY_YS[#CATEGORY_YS] + (index - #CATEGORY_YS) * 64)
		table.insert(
			categories,
			Kit.Tab.new(v, {
				id = id,
				name = "Category" .. id,
				rect = { 24, y, 219, 54 },
				label = id,
				icon = InventoryWindow.CATEGORY_ICONS[id] or "chest",
				iconX = 16,
				labelX = 73,
				variant = "category",
				zIndex = 8,
			})
		)
	end
	for index, y in CATEGORY_RULES do
		Kit.Divider.new(
			v,
			{ name = "CategoryRule" .. index, rect = { 27, y - 8, 203, 16 }, variant = "hairline", zIndex = 7 }
		)
	end
	self.categories = Kit.TabGroup.new(categories, function(id)
		self.category = id
		self:_layout()
	end)
	self.categories:Select("All")

	self.grid = Kit.Scroll.new(v, {
		name = "Grid",
		rect = GRID,
		gap = false,
		padBottom = 8,
		rail = "thin",
		zIndex = 8,
	})
	self.content = self.grid:Content()
	Kit.Divider.new(v, { name = "GridDivider", rect = { 852, 111, 2, 516 }, variant = "hairline", zIndex = 7 })

	self:_buildCard()
	self:_buildTabs(self.tabDefs[1] and self.tabDefs[1].id)
	self:SetDetail(nil)
	screen:Watch()
	if props.onClose then
		screen.Closed:Connect(props.onClose)
	end
	return self
end

-- Tabs ------------------------------------------------------------------------------------

-- The tabs (Backpack / Vault or Backpack / Equipped); a selected tab shows its
-- cream icon on leather.
function InventoryWindow:_buildTabs(selectedId: string?)
	local built = {}
	for index, def in self.tabDefs do
		local word, count = string.match(def.label or "", "^(.-)%s+(%d+%s*/%s*%d+)$")
		if word then
			def.label, def.count = word, count
		end
		local tab = Kit.Tab.new(self.visual, {
			id = def.id,
			name = "Tab" .. def.id,
			rect = TAB_RECTS[index] or { 19 + (index - 1) * 179, 108, 170, 58 },
			label = def.label,
			icon = def.icon,
			selectedIcon = def.iconSelected,
			iconX = TAB_LAYOUT[index] and TAB_LAYOUT[index].iconX,
			iconSize = TAB_LAYOUT[index] and TAB_LAYOUT[index].iconSize,
			labelX = TAB_LAYOUT[index] and TAB_LAYOUT[index].labelX,
			variant = "horizontal",
			zIndex = 8,
		})
		self.tabs[def.id] = tab
		tab:SetCount(def.count)
		table.insert(built, tab)
	end
	self.tabGroup = Kit.TabGroup.new(built, function(id)
		self.tabId = id
		if self.props.onTab then
			self.props.onTab(id)
		end
	end)
	self:SelectTab(selectedId)
end

-- Shows tab `id` as selected (scripted; onTab is not called).
function InventoryWindow:SelectTab(id: string?)
	self.tabId = id
	if id then
		self.tabGroup:Select(id)
	end
end

-- Changes a tab's label (the vault's "Vault 23/25"). A trailing count goes on
-- the tab's count plaque, so every tab label keeps the same size.
function InventoryWindow:SetTabLabel(id: string, label: string)
	local word, count = string.match(label, "^(.-)%s+(%d+%s*/%s*%d+)$")
	local text = word or label
	for _, def in self.tabDefs do
		if def.id == id then
			def.label = text
			def.count = count
		end
	end
	local tab = self.tabs[id]
	if tab then
		tab:SetLabel(text)
		tab:SetCount(count)
	end
end

-- Buttons right of the tabs ({{id, label, enabled?}}), right-aligned.
function InventoryWindow:SetToolbar(buttons: { Action })
	for _, button in self.toolbar do
		button:Destroy()
	end
	self.toolbar = {}
	local right = 840
	for index = #buttons, 1, -1 do
		local spec = buttons[index]
		local bw = math.max(120, math.ceil(Kit.Text.Width(spec.label, "buttonS")) + 44)
		right -= bw
		local button = Kit.Button.new(self.visual, {
			name = "Tool" .. spec.id,
			rect = { right, 116, bw, 42 },
			label = spec.label,
			variant = spec.variant or "secondary",
			sizeClass = "s",
			zIndex = 8,
			onPress = function()
				if self.props.onToolbar then
					self.props.onToolbar(spec.id)
				end
			end,
		})
		button:SetEnabled(spec.enabled ~= false and not self.busy)
		self.toolbar[spec.id] = button
		right -= 10
	end
end

-- Filters ---------------------------------------------------------------------------------

function InventoryWindow:_setQuery(text: string)
	self.query = text or ""
	self:_layout()
end

-- Sets the search text and filters at once (the box itself waits for typing
-- to settle).
function InventoryWindow:SetQuery(text: string)
	self.search:SetText(text)
	self:_setQuery(text)
end

function InventoryWindow:SetCategory(id: string)
	self.category = id
	self.categories:Select(id)
	self:_layout()
end

-- The category and search text in force.
function InventoryWindow:Filter(): (string, string)
	return self.category, self.query
end

function InventoryWindow:_filtering(): boolean
	return self.category ~= "All" or self.query ~= ""
end

local function cellName(cell: Cell): string
	if cell.name then
		return cell.name
	end
	local def = cell.item and ItemCatalog.Get(cell.item.catalogId)
	return def and def.name or (cell.item and cell.item.catalogId) or ""
end

function InventoryWindow:_visible(cell: Cell): boolean
	if not self:_filtering() then
		return true
	end
	return cell.item ~= nil
		and ItemInfo.InCategory(cell.item.catalogId, self.category)
		and ItemInfo.Matches(cellName(cell), self.query)
end

-- Grid ------------------------------------------------------------------------------------

-- Replaces the grid's contents: sections of cells ({id, item?, name?, hotkey?,
-- caption?, state?}); an item-less cell is an empty slot.
function InventoryWindow:SetSections(sections: { Section })
	self.sections = sections
	self:_layout()
end

local function pooled(list, index: number, make)
	local entry = list[index]
	if entry == nil then
		entry = make()
		list[index] = entry
	end
	return entry
end

function InventoryWindow:_slot(index: number)
	return pooled(self.slots, index, function()
		local slot = Kit.Slot.new(self.content, {
			name = "Slot" .. index,
			rect = { 0, 0, CELL[1], CELL[2] },
			zIndex = 9,
			onPress = function()
				local cell = self.slotCells[index]
				if cell and self.props.onSlot then
					self.props.onSlot(cell.id)
				end
			end,
		})
		-- The item's rarity as a small dot (Kit rarity badge).
		slot.rarity = Kit.Badge.new(slot.root, {
			name = "Rarity",
			variant = "rarity",
			rect = SLOT_RARITY,
			zIndex = 14,
		})
		slot.rarity.root.Visible = false
		return slot
	end)
end

-- The catalog rarity of an item, or nil.
local function rarityOf(catalogId: string?): string?
	local def = ItemCatalog.Get(catalogId)
	return def and def.rarity
end

-- Lays the visible cells out in rows of six, section by section.
function InventoryWindow:_layout()
	local y = INSET[2]
	local used, headersUsed, captionsUsed, hintsUsed = 0, 0, 0, 0
	local firstHit = nil
	table.clear(self.slotCells)
	for _, section in self.sections do
		if section.title then
			headersUsed += 1
			local header = pooled(self.headers, headersUsed, function()
				return Kit.Text.new(self.content, {
					name = "Section" .. headersUsed,
					rect = { 0, 0, GRID_W, HEADER_H },
					text = "",
					role = "sectionHeader",
					zIndex = 9,
				})
			end)
			header:SetText(section.title)
			header.root.Name = "Section" .. section.id
			header.root.Position = UDim2.fromOffset(INSET[1] + 2, y)
			header.root.Visible = true
			y += HEADER_H + 6
		end
		local shown = {}
		for _, cell in section.cells do
			if self:_visible(cell) then
				table.insert(shown, cell)
			end
		end
		if #shown == 0 then
			hintsUsed += 1
			local hint = pooled(self.hints, hintsUsed, function()
				return Kit.Text.new(self.content, {
					name = "Hint" .. hintsUsed,
					rect = { 0, 0, GRID_W, 40 },
					text = "",
					role = "muted",
					zIndex = 9,
				})
			end)
			hint:SetText(
				if self:_filtering() then "Nothing here matches." else section.emptyText or "Nothing here yet."
			)
			hint.root.Position = UDim2.fromOffset(INSET[1] + 2, y)
			hint.root.Visible = true
			y += 40 + SECTION_GAP
			continue
		end
		local captioned = false
		for _, cell in shown do
			captioned = captioned or cell.caption ~= nil
		end
		local rowH = PITCH[2] + (if captioned then CAPTION_H else 0)
		for i, cell in shown do
			used += 1
			local col, row = (i - 1) % COLUMNS, (i - 1) // COLUMNS
			local x, cy = INSET[1] + col * PITCH[1], y + row * rowH
			local slot = self:_slot(used)
			self.slotCells[used] = cell
			slot.root.Name = "Slot" .. cell.id
			slot.root.Position = UDim2.fromOffset(x, cy)
			slot.root.Visible = true
			local item = cell.item
			slot:SetItem(item and {
				itemId = item.catalogId,
				quantity = item.quantity,
				permanent = item.permanent,
			})
			slot:SetHotkey(cell.hotkey)
			-- Common is the default and draws no dot (the mockup's slots stay
			-- clean); the detail card names every item's rarity.
			local rarity = item and rarityOf(item.catalogId)
			slot.rarity.root.Visible = rarity ~= nil and rarity ~= "Common"
			if rarity then
				slot.rarity:SetRarity(rarity)
			end
			slot:SetState(cell.state or "normal")
			slot:SetSelected(cell.id == self.selectedId)
			firstHit = firstHit or slot.control.hit
			if cell.caption then
				captionsUsed += 1
				local caption = pooled(self.captions, captionsUsed, function()
					return Kit.Text.new(self.content, {
						name = "Caption" .. captionsUsed,
						rect = { 0, 0, CELL[1], CAPTION_H },
						text = "",
						role = "small",
						align = "Center",
						zIndex = 9,
					})
				end)
				caption:SetText(cell.caption)
				caption.root.Position = UDim2.fromOffset(x, cy + CELL[2] + 1)
				caption.root.Visible = true
			end
		end
		local rows = (#shown + COLUMNS - 1) // COLUMNS
		y += rows * rowH - (PITCH[2] - CELL[2]) + SECTION_GAP
	end
	for index = used + 1, #self.slots do
		self.slots[index].root.Visible = false
	end
	for index = headersUsed + 1, #self.headers do
		self.headers[index].root.Visible = false
	end
	for index = captionsUsed + 1, #self.captions do
		self.captions[index].root.Visible = false
	end
	for index = hintsUsed + 1, #self.hints do
		self.hints[index].root.Visible = false
	end
	self.grid:SetContentHeight(y - SECTION_GAP + INSET[2])
	-- Gamepad selection lands on the first slot when the window opens.
	local default = firstHit or (self.tabs[self.tabId or ""] and self.tabs[self.tabId].control.hit)
	self.screen:SetDefaultSelection(default)
	-- The slots arrived after the window opened on a gamepad (the first
	-- read), or a redraw hid the selected slot: take the first slot rather
	-- than leaving the ✕ (or nothing) selected.
	if default and self.screen:IsOpen() and Kit.Input.IsGamepad() then
		local now = GuiService.SelectedObject
		local close = self.window.close.control.hit
		if now == nil or now == close or not now.Visible or not now:IsDescendantOf(self.screen.gui) then
			GuiService.SelectedObject = default
		end
	end
end

-- Marks cell `id` selected (nil clears it).
function InventoryWindow:SetSelected(id: string?)
	self.selectedId = id
	for index, cell in self.slotCells do
		local slot = self.slots[index]
		if slot then
			slot:SetSelected(cell.id == id)
		end
	end
end

-- The slot showing cell `id`, or nil (flows and verifiers).
function InventoryWindow:SlotFor(id: string)
	for index, cell in self.slotCells do
		if cell.id == id and self.slots[index].root.Visible then
			return self.slots[index]
		end
	end
	return nil
end

-- Detail card -------------------------------------------------------------------------------

function InventoryWindow:_buildCard()
	local card = Kit.Panel.new(self.visual, { name = "Detail", rect = CARD, variant = "inset", zIndex = 7 })
	self.card = card
	local c = card.base.visual
	self.cardVisual = c
	self.detailIcon = Kit.ItemIcon.new(c, { name = "DetailIcon", rect = inCard(73, 38, 152, 166), zIndex = 9 })
	self.detailName = Kit.Text.new(c, {
		name = "ItemName",
		rect = inCard(19, 216, 258, 34),
		text = "",
		role = "itemTitle",
		zIndex = 9,
	})
	-- The item's rarity dot just after its name.
	self.detailRarity = Kit.Badge.new(c, {
		name = "Rarity",
		variant = "rarity",
		rect = inCard(19, 216 + (34 - NAME_RARITY) / 2, NAME_RARITY, NAME_RARITY),
		zIndex = 9,
	})
	self.detailText = Kit.Text.new(c, {
		name = "ItemText",
		rect = inCard(19, 256, 258, 50),
		text = "",
		role = "bodySoft",
		wrap = true,
		yAlign = "Top",
		zIndex = 9,
	})
	self.detailRule = Kit.Divider.new(
		c,
		{ name = "TopRule", rect = inCard(19, ROW_TOP - 8, 258, 16), variant = "hairline", zIndex = 9 }
	)
	self.hint = Kit.Text.new(c, {
		name = "Hint",
		rect = inCard(24, 180, 248, 90),
		text = "",
		role = "muted",
		align = "Center",
		wrap = true,
		zIndex = 9,
	})
	self.rows = {}
	self.extras = {}
end

-- Shows an item in the card ({catalogId, name, text, item?, rows, actions,
-- amount?}), a hint ({hint}) or nothing (nil). The first action is the big
-- leather button; up to two more sit above it as parchment buttons, where the
-- amount stepper goes for a vault material.
function InventoryWindow:SetDetail(detail: Detail?)
	self.detail = detail
	local c = self.cardVisual
	for _, row in self.rows do
		row:Destroy()
	end
	for _, part in self.extras do
		part:Destroy()
	end
	self.rows, self.extras = {}, {}
	self.primary, self.amount = nil, nil
	self.secondary = {}
	local showing = detail ~= nil and detail.catalogId ~= nil
	self.detailIcon.root.Visible = showing
	self.detailName.root.Visible = showing
	self.detailRarity.root.Visible = false
	self.detailText.root.Visible = showing
	self.detailRule.root.Visible = showing
	self.hint.root.Visible = not showing
	self.hint:SetText(if detail and detail.hint then detail.hint else "Choose an item to see it here.")
	if not showing then
		return
	end
	local d = detail :: Detail
	self.detailIcon:SetItem(d.catalogId)
	self.detailName:SetText(d.name or "")
	local rarity = rarityOf(d.catalogId)
	if rarity then
		local nameW = math.min(Kit.Text.Width(d.name or "", "itemTitle"), 258 - NAME_RARITY - 8)
		local at = inCard(19 + nameW + 8, 216 + (34 - NAME_RARITY) / 2, NAME_RARITY, NAME_RARITY)
		self.detailRarity.root.Position = UDim2.fromOffset(at[1], at[2])
		self.detailRarity:SetRarity(rarity)
		self.detailRarity.root.Visible = true
	end
	self.detailText:SetText(d.text or "")
	local actions = d.actions or {}
	local extraRow = d.amount ~= nil or #actions > 1
	local maxRows = if extraRow then 2 else 3
	for index, stat in d.rows or {} do
		if index > maxRows then
			break
		end
		table.insert(
			self.rows,
			Kit.ListRow.new(c, {
				name = "Stat" .. index,
				rect = inCard(19, ROW_TOP + (index - 1) * ROW_PITCH, 258, 40),
				variant = "line",
				icon = stat.icon,
				iconRect = { 12, 10, 23, 23 },
				textX = 50,
				titleSize = 15,
				title = stat.label,
				value = stat.value,
				zIndex = 9,
			})
		)
	end
	local function press(id: string)
		return function()
			if self.props.onAction then
				self.props.onAction(id)
			end
		end
	end
	if d.amount then
		self.amount = Kit.Stepper.new(c, {
			name = "Amount",
			rect = inCard(19, 402, 258, 42),
			min = d.amount.min,
			max = d.amount.max,
			value = d.amount.value,
			allLabel = d.amount.allLabel,
			zIndex = 9,
			onChange = function(value)
				if self.props.onAmount then
					self.props.onAmount(value)
				end
			end,
		})
		table.insert(self.extras, self.amount)
	elseif #actions > 1 then
		local count = math.min(#actions - 1, 2)
		local bw = (258 - 12 * (count - 1)) / count
		for index = 2, count + 1 do
			local spec = actions[index]
			local button = Kit.Button.new(c, {
				name = "Action" .. spec.id,
				rect = inCard(19 + (index - 2) * (bw + 12), 402, bw, 42),
				label = spec.label,
				variant = spec.variant or "secondary",
				sizeClass = "s",
				zIndex = 9,
				onPress = press(spec.id),
			})
			button:SetEnabled(spec.enabled ~= false)
			self.secondary[spec.id] = button
			table.insert(self.extras, button)
		end
	end
	local main = actions[1]
	if main then
		self.primary = Kit.Button.new(c, {
			name = "Action" .. main.id,
			rect = inCard(14, 450, 270, 61),
			label = main.label,
			variant = main.variant or "primary",
			zIndex = 9,
			onPress = press(main.id),
		})
		self.primary:SetEnabled(main.enabled ~= false)
		table.insert(self.extras, self.primary)
	end
	self:SetBusy(self.busy)
end

-- The action button for `id` (flows and verifiers), or nil.
function InventoryWindow:ActionButton(id: string)
	for _, part in self.extras do
		if part.root and part.root.Name == "Action" .. id then
			return part
		end
	end
	return nil
end

-- Holds every action while a request runs (the buttons read "…").
function InventoryWindow:SetBusy(busy: boolean)
	self.busy = busy
	for _, part in self.extras do
		if part.SetBusy then
			part:SetBusy(busy)
		end
	end
	for _, button in self.toolbar do
		button:SetBusy(busy)
	end
end

-- Opening and closing -----------------------------------------------------------------------

function InventoryWindow:Open(gamepad: boolean?)
	self.screen:Open(gamepad)
end

function InventoryWindow:Close()
	self.screen:Close()
end

function InventoryWindow:IsOpen(): boolean
	return self.screen:IsOpen()
end

function InventoryWindow:Destroy()
	self.screen:Destroy()
end

return InventoryWindow
