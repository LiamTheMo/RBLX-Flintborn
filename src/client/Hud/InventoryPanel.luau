-- The parchment Inventory & Vault window (art/reference/ui/parchment/
-- 08_inventory_vault.png, spec docs/ui/InventoryScreen.md). One window serves
-- both places: the lobby's backpack and vault (VaultController) and the run's
-- backpack, hotbar and armour (InventoryController). Two panes of item slots,
-- category tabs down the left (All, Tools, Materials, Food), a search box, the
-- move arrows and a square button between the panes, and a detail strip with
-- the chosen item's stats and two action buttons. The view only draws and
-- reports; its controller fills the panes and decides what each press does.
--
-- Positions are the reference sheet's own pixels (the window art was cut at
-- ORIGIN), so they read straight off the image.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local ItemInfo = require(ReplicatedStorage.Shared.Items.ItemInfo)
local UiAssets = require(ReplicatedStorage.Shared.UI.UiAssets)
local ItemSlot = require(script.Parent.ItemSlot)
local Layout = require(script.Parent.Layout)
local Parchment = require(script.Parent.Parchment)
local Widgets = require(script.Parent.Widgets)

local InventoryPanel = {}
InventoryPanel.__index = InventoryPanel

InventoryPanel.SIZE = { 1494, 786 }
local ORIGIN = { 148, 6 }

-- Category tabs: {id, icon sprite, reference rect}.
InventoryPanel.TABS = {
	{ id = "All", icon = "pm_cat_all", rect = { 48, 114, 122, 124 } },
	{ id = "Tools", icon = "pm_cat_tools", rect = { 44, 250, 120, 124 } },
	{ id = "Materials", icon = "pm_cat_materials", rect = { 44, 380, 120, 124 } },
	{ id = "Food", icon = "pm_cat_food", rect = { 44, 510, 120, 124 } },
}

local CELL = UDim2.fromOffset(ItemSlot.SIZE[1], ItemSlot.SIZE[2])
local CELL_GAP = UDim2.fromOffset(7.6, 9.5)
local CHIP_X = { 408, 526, 640 }
local GLYPHS = { sword = "pm_glyph_sword", hammer = "pm_glyph_hammer", weight = "pm_glyph_weight" }

local function at(x: number, y: number, w: number, h: number)
	return { x - ORIGIN[1], y - ORIGIN[2], w, h }
end

local function place(object: GuiObject, r)
	object.Position = UDim2.fromOffset(r[1], r[2])
	object.Size = UDim2.fromOffset(r[3], r[4])
end

local function natural(name: string, fallback: { number }): (number, number)
	local sprite = UiAssets.sprite(name)
	if sprite then
		return sprite.w, sprite.h
	end
	return fallback[1], fallback[2]
end

-- handlers: onClose(), onSlot(paneId, entry), onTab(id), and whatever the
-- controller wires to the buttons through SetMiddle / SetActions.
function InventoryPanel.new(parent: Instance?, handlers)
	local self = setmetatable({}, InventoryPanel)
	self.handlers = handlers
	self.screen = Parchment.Screen("FlintbornInventory", InventoryPanel.SIZE, 20, parent)
	local window = self.screen.window
	self.window = window
	self.category = "All"
	self.query = ""
	self.filterMode = "hide"
	self.panes = {}

	Widgets.Sprite("pm_window_inventory", { Name = "Art", Size = UDim2.fromScale(1, 1), ZIndex = 1 }, window)
	self.title = Parchment.Text("", at(560, 30, 550, 58), window, {
		size = 40,
		color = "cream",
		align = "Center",
		scaled = true,
		name = "Title",
	})
	local close = Widgets.Make("TextButton", {
		Name = "Close",
		Text = "",
		AutoButtonColor = false,
		BackgroundTransparency = 1,
		Position = UDim2.fromOffset(1556 - ORIGIN[1], 46 - ORIGIN[2]),
		Size = UDim2.fromOffset(80, 76),
		ZIndex = 10,
	}, window)
	close.Activated:Connect(function()
		handlers.onClose()
	end)
	self.close = close

	self:_tabs(window)
	self:_pane("left", window, at(206, 194, 626, 418))
	self:_pane("right", window, at(956, 194, 626, 418))
	self:_header(window)
	self:_middle(window)
	self:_detail(window)
	self:SelectTab("All")
	return self
end

function InventoryPanel:_tabs(window: Instance)
	self.tabs = {}
	for _, tab in InventoryPanel.TABS do
		local r = tab.rect
		local holder = Widgets.Make("Frame", { Name = tab.id, BackgroundTransparency = 1, ZIndex = 2 }, window)
		place(holder, at(r[1] - 2, r[2] - 2, r[3] + 4, r[4] + 4))
		local selW, selH = natural("pm_side_tab_selected", { r[3] + 4, r[4] + 4 })
		local w, h = natural("pm_side_tab", { r[3] + 4, r[4] + 4 })
		local on = Widgets.Sprite("pm_side_tab_selected", {
			Name = "On",
			Size = UDim2.fromOffset(selW, selH),
			ZIndex = 2,
		}, holder)
		local off = Widgets.Sprite("pm_side_tab", { Name = "Off", Size = UDim2.fromOffset(w, h), ZIndex = 2 }, holder)
		local iconW, iconH = natural(tab.icon, { 80, 80 })
		local k = 78 / math.max(iconW, iconH)
		Widgets.Sprite(tab.icon, {
			Name = "Icon",
			AnchorPoint = Vector2.new(0.5, 0.5),
			Position = UDim2.fromOffset((r[3] + 4) / 2, (r[4] + 4) / 2),
			Size = UDim2.fromOffset(iconW * k, iconH * k),
			ZIndex = 3,
		}, holder)
		local button = Parchment.Pressable(holder, off, function()
			self:SelectTab(tab.id)
		end)
		self.tabs[tab.id] = { on = on, off = off, button = button }
	end
end

-- A pane: a scrolling column of sections, each an optional header and a grid.
function InventoryPanel:_pane(id: string, window: Instance, r)
	local scroller = Widgets.Make("ScrollingFrame", {
		Name = if id == "left" then "Left" else "Right",
		BackgroundTransparency = 1,
		BorderSizePixel = 0,
		CanvasSize = UDim2.new(),
		AutomaticCanvasSize = Enum.AutomaticSize.Y,
		ScrollingDirection = Enum.ScrollingDirection.Y,
		ScrollBarThickness = 6,
		ScrollBarImageColor3 = Layout.Color("paperEdge"),
		ZIndex = 3,
	}, window) :: ScrollingFrame
	place(scroller, r)
	Widgets.Make("UIListLayout", { Padding = UDim.new(0, 6), SortOrder = Enum.SortOrder.LayoutOrder }, scroller)
	Widgets.Make("UIPadding", {
		PaddingLeft = UDim.new(0, 8),
		PaddingTop = UDim.new(0, 6),
		PaddingBottom = UDim.new(0, 6),
	}, scroller)
	self.panes[id] = { scroller = scroller, slots = {}, sections = {} }
end

function InventoryPanel:_header(window: Instance)
	local left, right = {}, {}
	left.title = Parchment.Text("", at(219, 136, 270, 48), window, { size = 33, scaled = true, name = "LeftTitle" })
	-- Search: the box art with a TextBox over its blank part.
	Widgets.Sprite("pm_search_box", {
		Name = "Search",
		Position = UDim2.fromOffset(497 - ORIGIN[1], 141 - ORIGIN[2]),
		Size = UDim2.fromOffset(226, 42),
		ZIndex = 3,
	}, window, Parchment.SliceFor("pm_search_box", { 0, 0, 226, 42 }))
	local box = Widgets.Make("TextBox", {
		Name = "Query",
		BackgroundTransparency = 1,
		ClearTextOnFocus = false,
		Font = Layout.Font("serif"),
		PlaceholderColor3 = Layout.Color("inkSoft"),
		PlaceholderText = "Search...",
		Text = "",
		TextColor3 = Layout.Color("ink"),
		TextSize = 20,
		TextXAlignment = Enum.TextXAlignment.Left,
		ZIndex = 4,
	}, window) :: TextBox
	local face = Layout.FontFace("serif")
	if face then
		box.FontFace = face
	end
	place(box, at(543, 143, 172, 38))
	box:GetPropertyChangedSignal("Text"):Connect(function()
		self.query = box.Text
		self:_refilter()
	end)
	self.search = box
	-- Sort: cycles the order the controller lists items in.
	self.sort = Parchment.Button("pm_sort_button", at(737, 141, 77, 42), window, function()
		if self.handlers.onSort then
			self.handlers.onSort()
		end
	end, { name = "Sort" })
	right.icon = Widgets.Sprite("pm_icon_chest", {
		Name = "RightIcon",
		Position = UDim2.fromOffset(968 - ORIGIN[1], 136 - ORIGIN[2]),
		Size = UDim2.fromOffset(66, 53),
		ZIndex = 3,
	}, window)
	right.title = Parchment.Text("", at(1047, 136, 220, 48), window, { size = 33, scaled = true, name = "RightTitle" })
	-- Capacity: a gold bar and its count.
	local track = Widgets.Make("Frame", {
		Name = "Capacity",
		BackgroundColor3 = Layout.Color("sliderTrack"),
		BorderSizePixel = 0,
		ZIndex = 3,
	}, window)
	place(track, at(1272, 152, 194, 23))
	Widgets.Make("UICorner", { CornerRadius = UDim.new(0.5, 0) }, track)
	Widgets.Make("UIStroke", { Color = Layout.Color("ink"), Thickness = 1.5 }, track)
	right.fill = Widgets.Fill("sliderFill", { Size = UDim2.fromScale(0.5, 1), ZIndex = 4 }, track)
	right.track = track
	right.count = Parchment.Text("", at(1478, 143, 112, 40), window, { size = 23, scaled = true, minSize = 12 })
	self.headers = { left = left, right = right }
end

function InventoryPanel:_middle(window: Instance)
	Widgets.Sprite("pm_glyph_mountain", {
		Name = "Mark",
		Position = UDim2.fromOffset(870 - ORIGIN[1], 178 - ORIGIN[2]),
		Size = UDim2.fromOffset(44, 27),
		ImageColor3 = Layout.Color("line2"),
		ZIndex = 3,
	}, window)
	for _, y in { 216, 458 } do
		local dash = Parchment.Rule(at(890, y, 3, 44), window, "line2", 3)
		Widgets.Make("UICorner", { CornerRadius = UDim.new(0.5, 0) }, dash)
	end
	local middle = {}
	middle.right = Parchment.Button("pm_arrow_right", at(851, 276, 82, 71), window, function()
		if self.middle.rightFn then
			self.middle.rightFn()
		end
	end, { name = "MoveRight", pad = 4 })
	middle.left = Parchment.Button("pm_arrow_left", at(851, 375, 82, 70), window, function()
		if self.middle.leftFn then
			self.middle.leftFn()
		end
	end, { name = "MoveLeft", pad = 4 })
	middle.square = Parchment.Button("pm_button_square", at(836, 516, 112, 89), window, function()
		if self.middle.squareFn then
			self.middle.squareFn()
		end
	end, { name = "Square", label = "", color = "cream", size = 21, inset = 12 })
	middle.square.label.TextWrapped = true
	middle.square.label.TextTruncate = Enum.TextTruncate.None
	self.middle = middle
	-- The lower half of the dashed column, under the detail strip's own mark.
	Widgets.Sprite("pm_glyph_mountain", {
		Name = "Mark2",
		Position = UDim2.fromOffset(870 - ORIGIN[1], 677 - ORIGIN[2]),
		Size = UDim2.fromOffset(44, 27),
		ImageColor3 = Layout.Color("line2"),
		ZIndex = 3,
	}, window)
end

function InventoryPanel:_detail(window: Instance)
	local detail = {}
	detail.slot = ItemSlot.new(window, {
		Name = "Chosen",
		Position = UDim2.fromOffset(240 - ORIGIN[1], 637 - ORIGIN[2]),
		Size = UDim2.fromOffset(142, 119),
	})
	detail.slot.button.Active = false
	detail.slot.button.Selectable = false
	detail.name = Parchment.Text("", at(407, 638, 440, 50), window, { size = 32, scaled = true, minSize = 16 })
	detail.chips = {}
	for index, x in CHIP_X do
		local chip = Widgets.Make("Frame", { Name = "Chip" .. index, BackgroundTransparency = 1, ZIndex = 3 }, window)
		place(chip, at(x, 698, 104, 43))
		Widgets.Sprite(
			"pm_stat_chip",
			{ Name = "Art", Size = UDim2.fromScale(1, 1), ZIndex = 3 },
			chip,
			Parchment.SliceFor("pm_stat_chip", { 0, 0, 104, 43 })
		)
		local glyph = Widgets.Make("Frame", { Name = "GlyphHolder", BackgroundTransparency = 1, ZIndex = 4 }, chip)
		place(glyph, { 8, 6, 30, 31 })
		local text = Parchment.Text("", { 12, 0, 86, 43 }, chip, { size = 19, align = "Center", scaled = true, z = 4 })
		table.insert(detail.chips, { frame = chip, glyph = glyph, text = text })
	end
	detail.status = Parchment.Text("", at(408, 745, 680, 26), window, {
		size = 17,
		color = "leather",
		scaled = true,
		minSize = 11,
		name = "Status",
	})
	-- Amount picker (vault materials): ×1, ×10, ×100, All.
	detail.amounts = {}
	for index = 1, 4 do
		local chip = Parchment.Button("pm_stat_chip", at(766 + (index - 1) * 74, 698, 68, 43), window, function()
			if self.amountFn then
				self.amountFn(index)
			end
		end, { name = "Amount" .. index, label = "", size = 18 })
		local ring = Widgets.Make("UIStroke", {
			Color = Layout.Color("selectGlow"),
			Thickness = 3,
			ApplyStrokeMode = Enum.ApplyStrokeMode.Border,
			Enabled = false,
		}, chip.holder)
		Widgets.Make("UICorner", { CornerRadius = UDim.new(0, 9) }, chip.holder)
		chip.holder.Visible = false
		table.insert(detail.amounts, { button = chip, ring = ring })
	end
	detail.actions = {}
	for index, x in { 1104, 1348 } do
		local action = Parchment.Button("pm_button_action", at(x, 655, 222, 76), window, function()
			local fn = self.actionFns and self.actionFns[index]
			if fn then
				fn()
			end
		end, { name = "Action" .. index, label = "", color = "cream", size = 28 })
		table.insert(detail.actions, action)
	end
	-- "Deposit anyway?" card over the detail strip.
	local card = Widgets.Make("Frame", {
		Name = "Confirm",
		Active = true,
		BackgroundColor3 = Layout.Color("paper"),
		BorderSizePixel = 0,
		Visible = false,
		ZIndex = 12,
	}, window)
	place(card, at(214, 628, 1372, 142))
	Widgets.Make("UICorner", { CornerRadius = UDim.new(0, 10) }, card)
	Widgets.Make("UIStroke", { Color = Layout.Color("paperEdge"), Thickness = 2 }, card)
	detail.confirmText = Parchment.Text("", { 26, 16, 840, 110 }, card, {
		size = 24,
		wrap = true,
		scaled = true,
		minSize = 14,
		z = 13,
	})
	detail.confirmYes = Parchment.Button("pm_button_action", { 890, 33, 222, 76 }, card, function()
		local fn = self.confirmFn
		self:HideConfirm()
		if fn then
			fn()
		end
	end, { name = "Yes", label = "", color = "cream", size = 24, z = 13 })
	detail.confirmNo = Parchment.Button("pm_button_action", { 1134, 33, 222, 76 }, card, function()
		self:HideConfirm()
	end, { name = "No", label = "CANCEL", color = "cream", size = 24, z = 13 })
	detail.card = card
	self.detail = detail
end

-- The sort button is for lists the controller can reorder (not the run's slots).
function InventoryPanel:SetSortVisible(visible: boolean)
	self.sort.holder.Visible = visible
end

function InventoryPanel:SetTitle(text: string)
	self.title.Text = text
end

-- Pane headers: title text; for the right pane an icon sprite and a capacity
-- {used, total} (nil hides the bar).
function InventoryPanel:SetHeader(paneId: string, title: string, icon: string?, capacity)
	local header = self.headers[paneId]
	header.title.Text = title
	if paneId == "right" then
		if icon and header.icon.Name ~= icon then
			local position, size = header.icon.Position, header.icon.Size
			header.icon:Destroy()
			header.icon =
				Widgets.Sprite(icon, { Name = "RightIcon", Position = position, Size = size, ZIndex = 3 }, self.window)
		end
		header.track.Visible = capacity ~= nil
		header.count.Visible = capacity ~= nil
		if capacity then
			local fraction = if capacity[2] > 0 then math.clamp(capacity[1] / capacity[2], 0, 1) else 0
			header.fill.Visible = fraction > 0
			header.fill.Size = UDim2.fromScale(math.max(fraction, 0.06), 1)
			header.count.Text = ("%d/%d"):format(capacity[1], capacity[2])
		end
	end
end

-- Fills a pane. `sections` = {{header?, entries = {{id, item?, key?}}}}; an entry
-- without an item is an empty slot (kept in place). `filterMode` "hide" drops
-- entries that do not match the tab or search, "dim" greys them in place.
function InventoryPanel:SetPane(paneId: string, sections, filterMode: string?)
	local pane = self.panes[paneId]
	pane.filterMode = filterMode or "hide"
	for _, child in pane.scroller:GetChildren() do
		if child:IsA("GuiObject") then
			child:Destroy()
		end
	end
	pane.slots = {}
	for order, section in sections do
		if section.header then
			Widgets.Text({ font = "serif", textSize = 20, color = "inkSoft" }, {
				Name = "Header" .. order,
				LayoutOrder = order * 2 - 1,
				Text = string.upper(section.header),
				Size = UDim2.new(1, -16, 0, 26),
				TextStrokeTransparency = 1,
				ZIndex = 4,
			}, pane.scroller)
		end
		-- Sized from its rows (six slots to a row), so sections stack cleanly.
		local rows = math.max(1, math.ceil(#section.entries / 6))
		local height = rows * CELL.Y.Offset + (rows - 1) * CELL_GAP.Y.Offset
		local grid = Widgets.Make("Frame", {
			Name = "Grid" .. order,
			BackgroundTransparency = 1,
			LayoutOrder = order * 2,
			Size = UDim2.new(1, -10, 0, height),
			ZIndex = 3,
		}, pane.scroller)
		Widgets.Make("UIGridLayout", {
			CellSize = CELL,
			CellPadding = CELL_GAP,
			SortOrder = Enum.SortOrder.LayoutOrder,
		}, grid)
		for index, entry in section.entries do
			local slot = ItemSlot.new(grid, { Name = tostring(entry.id), LayoutOrder = index }, function()
				self.handlers.onSlot(paneId, entry)
			end)
			slot:Set(entry.item)
			slot:SetKey(entry.key)
			table.insert(pane.slots, { slot = slot, entry = entry })
		end
	end
	self:_refilter()
	self:_reselect()
end

function InventoryPanel:_refilter()
	for _, pane in self.panes do
		for _, cell in pane.slots do
			local item = cell.entry.item
			local match = item == nil
				or (ItemInfo.InCategory(item.catalogId, self.category) and ItemInfo.Matches(item.name, self.query))
			if pane.filterMode == "dim" then
				cell.slot.holder.Visible = true
				cell.slot:SetDimmed(item ~= nil and not match)
			else
				cell.slot.holder.Visible = item ~= nil and match
				cell.slot:SetDimmed(false)
			end
		end
	end
end

function InventoryPanel:SelectTab(id: string)
	self.category = id
	for name, tab in self.tabs do
		tab.on.Visible = name == id
		tab.off.Visible = name ~= id
	end
	self:_refilter()
	if self.handlers.onTab then
		self.handlers.onTab(id)
	end
end

-- Rings the chosen slot ({paneId, id} or nil) and, in the run, the equipped one.
function InventoryPanel:Select(choice, equipped)
	self.selected = choice
	self.equipped = equipped
	self:_reselect()
end

function InventoryPanel:_reselect()
	local choice, equipped = self.selected, self.equipped
	for paneId, pane in self.panes do
		for _, cell in pane.slots do
			local on = choice ~= nil and choice.paneId == paneId and choice.id == cell.entry.id
			local worn = equipped ~= nil and equipped.paneId == paneId and equipped.id == cell.entry.id
			cell.slot:SetSelected(on, worn)
		end
	end
end

-- The detail strip: the chosen item (or nil with a hint) and its stat chips.
function InventoryPanel:SetDetail(item, hint: string?)
	local detail = self.detail
	detail.slot:Set(item)
	detail.name.Text = if item then item.name or item.catalogId else (hint or "")
	detail.name.TextColor3 = Layout.Color(if item then "ink" else "inkSoft")
	local chips = if item then ItemInfo.Stats(item) else {}
	for index, chip in detail.chips do
		local stat = chips[index]
		chip.frame.Visible = stat ~= nil
		for _, child in chip.glyph:GetChildren() do
			child:Destroy()
		end
		if stat then
			chip.text.Text = stat.text
			local glyph = stat.glyph and GLYPHS[stat.glyph]
			if glyph then
				Widgets.Sprite(glyph, {
					Name = "Glyph",
					Size = UDim2.fromScale(1, 1),
					ImageColor3 = Layout.Color("ink"),
					ZIndex = 4,
				}, chip.glyph)
				chip.text.Position = UDim2.fromOffset(38, 0)
				chip.text.Size = UDim2.fromOffset(60, 43)
			else
				chip.text.Position = UDim2.fromOffset(10, 0)
				chip.text.Size = UDim2.fromOffset(84, 43)
			end
		end
	end
end

-- The two action buttons: {{label, enabled, fn}?, {label, enabled, fn}?}; a
-- missing one is hidden.
function InventoryPanel:SetActions(actions)
	self.actionFns = {}
	for index, button in self.detail.actions do
		local action = actions[index]
		button.holder.Visible = action ~= nil
		if action then
			button.label.Text = action[1]
			button.SetEnabled(action[2])
			self.actionFns[index] = action[3]
		end
	end
end

-- Middle column: right arrow, left arrow, square button. Each {enabled, fn} (the
-- square also a label as its first field); nil hides it.
function InventoryPanel:SetMiddle(right, left, square)
	local middle = self.middle
	middle.right.holder.Visible = right ~= nil
	middle.left.holder.Visible = left ~= nil
	middle.square.holder.Visible = square ~= nil
	if right then
		middle.right.SetEnabled(right[1])
		middle.rightFn = right[2]
	end
	if left then
		middle.left.SetEnabled(left[1])
		middle.leftFn = left[2]
	end
	if square then
		middle.square.label.Text = square[1]
		middle.square.SetEnabled(square[2])
		middle.squareFn = square[3]
	end
end

-- The amount picker: `labels` (nil hides it), the picked index and onPick(index).
function InventoryPanel:SetAmounts(labels: { string }?, picked: number?, onPick)
	self.amountFn = onPick
	for index, amount in self.detail.amounts do
		local label = labels and labels[index]
		amount.button.holder.Visible = label ~= nil
		if label then
			amount.button.label.Text = label
			amount.ring.Enabled = index == picked
		end
	end
end

function InventoryPanel:SetStatus(text: string)
	self.detail.status.Text = text
end

-- Asks before something that cannot be undone; `yes` names the confirm button.
function InventoryPanel:Confirm(text: string, yes: string, onYes)
	self.confirmFn = onYes
	self.detail.confirmText.Text = text
	self.detail.confirmYes.label.Text = yes
	self.detail.card.Visible = true
end

function InventoryPanel:HideConfirm()
	self.confirmFn = nil
	self.detail.card.Visible = false
end

function InventoryPanel:IsConfirming(): boolean
	return self.detail.card.Visible
end

return InventoryPanel
