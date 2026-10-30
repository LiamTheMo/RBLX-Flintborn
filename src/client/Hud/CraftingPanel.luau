-- The parchment recipe window (art/reference/ui/parchment/09_crafting.png, spec
-- docs/ui/CraftingScreen.md), in two modes:
--   "crafting" (CraftingController, runs): recipes by category, the chosen one's
--     stats and what it needs against what you carry, the batch stepper, CRAFT
--     and Craft all; on the right the running smelt with Stop, and the stations
--     within reach.
--   "forge" (ForgeController, lobby): the Ancestral Forge's recipes with vault
--     counts and locks; on the right the vault gear a Permanent conversion can
--     use, its rules, and a confirmation before anything is spent.
-- The view only draws and reports; the controllers build the entries and send
-- the requests.
--
-- An entry: {id, output (catalogId), name, quantity, category, inputs = {{id,
-- name, owned, needed}} (per unit), can (how many the inputs pay for), here
-- (usable here), where (station / time text), timed, locked, lockText, verb,
-- sources = {{id, name, detail}} (forge Permanent conversions)}.
--
-- Positions are the reference sheet's own pixels (the window art was cut at
-- ORIGIN), so they read straight off the image.

local GuiService = game:GetService("GuiService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local ItemInfo = require(ReplicatedStorage.Shared.Items.ItemInfo)
local ItemSlot = require(script.Parent.ItemSlot)
local Layout = require(script.Parent.Layout)
local Parchment = require(script.Parent.Parchment)
local Widgets = require(script.Parent.Widgets)

local CraftingPanel = {}
CraftingPanel.__index = CraftingPanel

CraftingPanel.SIZE = { 1629, 742 }
local ORIGIN = { 23, 58 }

-- The largest batch the stepper offers.
CraftingPanel.MAX_BATCH = 50

local ROW_PITCH = 77
local ROW_HEIGHT = 70
local CHIPS = { { 827, 102 }, { 938, 110 }, { 1057, 103 } }
local STAT_GLYPHS = { sword = "pm_glyph_sword", hammer = "pm_glyph_hammer", weight = "pm_glyph_weight" }

local function at(x: number, y: number, w: number, h: number)
	return { x - ORIGIN[1], y - ORIGIN[2], w, h }
end

local function place(object: GuiObject, r)
	object.Position = UDim2.fromOffset(r[1], r[2])
	object.Size = UDim2.fromOffset(r[3], r[4])
end

-- opts: mode ("crafting" | "forge"), categories ({{id, label, glyph}}), title
-- (written over the art when it has none), window (sprite), name (ScreenGui).
function CraftingPanel.new(parent: Instance?, handlers, opts)
	local self = setmetatable({}, CraftingPanel)
	self.handlers = handlers
	self.mode = opts.mode
	self.categories = opts.categories
	self.glyphs = {}
	for _, category in opts.categories do
		self.glyphs[category.id] = category.glyph
	end
	self.screen = Parchment.Screen(opts.name, CraftingPanel.SIZE, 20, parent)
	local window = self.screen.window
	self.window = window
	self.entries = {}
	self.category = nil
	self.query = ""
	self.count = 1

	Widgets.Sprite(opts.window, { Name = "Art", Size = UDim2.fromScale(1, 1), ZIndex = 1 }, window)
	if opts.title then
		Parchment.Text(opts.title, at(198, 92, 600, 64), window, { size = 44, scaled = true, name = "Title" })
	end
	local close = Widgets.Make("TextButton", {
		Name = "Close",
		Text = "",
		AutoButtonColor = false,
		BackgroundTransparency = 1,
		Position = UDim2.fromOffset(1538 - ORIGIN[1], 70 - ORIGIN[2]),
		Size = UDim2.fromOffset(100, 94),
		ZIndex = 10,
	}, window)
	close.Activated:Connect(function()
		handlers.onClose()
	end)
	self.close = close
	self:_left(window)
	self:_middle(window)
	if self.mode == "forge" then
		self:_sources(window)
	else
		self:_queue(window)
	end
	self:_confirmCard(window)
	return self
end

-- An entry's own icon (once uploaded) or its category glyph.
function CraftingPanel:_art(entry, props, parent: Instance): GuiObject
	local icon = ItemSlot.IconFor(entry.output)
	if icon then
		return Widgets.Sprite(icon, props, parent)
	end
	props.ImageColor3 = Layout.Color("ink")
	return Widgets.Sprite(self.glyphs[entry.category] or "pm_glyph_bench", props, parent)
end

function CraftingPanel:_left(window: Instance)
	Widgets.Sprite("pm_search_box", {
		Name = "Search",
		Position = UDim2.fromOffset(82 - ORIGIN[1], 178 - ORIGIN[2]),
		Size = UDim2.fromOffset(393, 44),
		ZIndex = 3,
	}, window, Parchment.SliceFor("pm_search_box", { 0, 0, 393, 44 }))
	local box = Widgets.Make("TextBox", {
		Name = "Query",
		BackgroundTransparency = 1,
		ClearTextOnFocus = false,
		Font = Layout.Font("serif"),
		PlaceholderColor3 = Layout.Color("inkSoft"),
		PlaceholderText = "Search recipes...",
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
	place(box, at(126, 180, 340, 40))
	box:GetPropertyChangedSignal("Text"):Connect(function()
		self.query = box.Text
		-- A recipe the search hides leaves the card too.
		self:SelectCategory(self.category)
	end)
	self.search = box

	self.tabs = {}
	local width = 393 / #self.categories
	for index, category in self.categories do
		local holder = Widgets.Make("Frame", { Name = category.id, BackgroundTransparency = 1, ZIndex = 3 }, window)
		place(holder, at(82 + (index - 1) * width, 235, width - 3, 60))
		local slice = Parchment.SliceFor("pm_ctab", { 0, 0, width - 3, 60 })
		local on =
			Widgets.Sprite("pm_ctab_selected", { Name = "On", Size = UDim2.fromScale(1, 1), ZIndex = 3 }, holder, slice)
		local off = Widgets.Sprite("pm_ctab", { Name = "Off", Size = UDim2.fromScale(1, 1), ZIndex = 3 }, holder, slice)
		Widgets.Sprite(category.glyph, {
			Name = "Glyph",
			AnchorPoint = Vector2.new(0.5, 0.5),
			Position = UDim2.fromScale(0.5, 0.5),
			Size = UDim2.fromOffset(40, 32),
			ImageColor3 = Layout.Color("ink"),
			ScaleType = Enum.ScaleType.Fit,
			ZIndex = 4,
		}, holder)
		local button = Parchment.Pressable(holder, off, function()
			-- The chosen tab again shows every recipe.
			self:SelectCategory(if self.category == category.id then nil else category.id)
		end)
		self.tabs[category.id] = { on = on, off = off, button = button }
	end

	local list = Widgets.Make("ScrollingFrame", {
		Name = "Recipes",
		BackgroundTransparency = 1,
		BorderSizePixel = 0,
		CanvasSize = UDim2.new(),
		AutomaticCanvasSize = Enum.AutomaticSize.Y,
		ScrollingDirection = Enum.ScrollingDirection.Y,
		ScrollBarThickness = 6,
		ScrollBarImageColor3 = Layout.Color("paperEdge"),
		ZIndex = 3,
	}, window) :: ScrollingFrame
	place(list, at(78, 305, 410, 462))
	Widgets.Make("UIListLayout", {
		Padding = UDim.new(0, ROW_PITCH - ROW_HEIGHT),
		SortOrder = Enum.SortOrder.LayoutOrder,
	}, list)
	Widgets.Make("UIPadding", { PaddingLeft = UDim.new(0, 2), PaddingTop = UDim.new(0, 2) }, list)
	self.list = list
	self.rows = {}
end

function CraftingPanel:_middle(window: Instance)
	local card = {}
	card.art = Widgets.Make("Frame", { Name = "Picture", BackgroundTransparency = 1, ZIndex = 3 }, window)
	place(card.art, at(560, 230, 250, 360))
	card.name =
		Parchment.Text("", at(827, 230, 334, 58), window, { size = 42, scaled = true, minSize = 18, name = "Name" })
	card.chips = {}
	for index, chip in CHIPS do
		local frame = Widgets.Make("Frame", { Name = "Chip" .. index, BackgroundTransparency = 1, ZIndex = 3 }, window)
		place(frame, at(chip[1], 295, chip[2], 68))
		Widgets.Sprite(
			"pm_stat_chip_tall",
			{ Name = "Art", Size = UDim2.fromScale(1, 1), ZIndex = 3 },
			frame,
			Parchment.SliceFor("pm_stat_chip_tall", { 0, 0, chip[2], 68 })
		)
		local glyph = Widgets.Make("Frame", { Name = "GlyphHolder", BackgroundTransparency = 1, ZIndex = 4 }, frame)
		place(glyph, { 8, 18, 32, 32 })
		local text = Parchment.Text("", { 10, 4, chip[2] - 20, 60 }, frame, {
			size = 20,
			align = "Center",
			scaled = true,
			wrap = true,
			minSize = 11,
			z = 4,
		})
		table.insert(card.chips, { frame = frame, glyph = glyph, text = text, width = chip[2] })
	end
	Parchment.Divider(at(826, 386, 332, 28), window)
	Parchment.Text("REQUIRES", at(827, 414, 140, 28), window, { size = 20 })
	card.where = Parchment.Text("", at(960, 414, 198, 28), window, {
		size = 16,
		color = "inkSoft",
		align = "Right",
		scaled = true,
		minSize = 10,
		name = "Where",
	})
	card.needs = Widgets.Make("Frame", { Name = "Needs", BackgroundTransparency = 1, ZIndex = 3 }, window)
	place(card.needs, at(828, 447, 332, 154))
	Parchment.Divider(at(535, 620, 622, 28), window)
	card.minus = Parchment.Button("pm_stepper_minus", at(535, 670, 60, 61), window, function()
		self:_step(-1)
	end, { name = "Minus", pad = 4 })
	card.field = Widgets.Sprite("pm_stepper_field", {
		Name = "Field",
		Position = UDim2.fromOffset(595 - ORIGIN[1], 672 - ORIGIN[2]),
		Size = UDim2.fromOffset(73, 58),
		ZIndex = 3,
	}, window, Parchment.SliceFor("pm_stepper_field", { 0, 0, 73, 58 }))
	card.countText = Parchment.Text("1", at(597, 672, 69, 58), window, { size = 32, align = "Center", scaled = true })
	card.plus = Parchment.Button("pm_stepper_plus", at(667, 670, 60, 61), window, function()
		self:_step(1)
	end, { name = "Plus", pad = 4 })
	card.craft = Parchment.Button("pm_button_craft", at(754, 655, 280, 92), window, function()
		self:_go(self.count)
	end, { name = "Craft", label = "CRAFT", color = "cream", size = 38, inset = 64 })
	card.all = Parchment.Button("pm_button_paper", at(1041, 672, 125, 60), window, function()
		local entry = self:_chosen()
		if entry then
			self:_go(math.max(1, entry.can or 0))
		end
	end, { name = "CraftAll", label = "Craft all", size = 22, inset = 12 })
	card.status = Parchment.Text("", at(535, 745, 622, 22), window, {
		size = 16,
		color = "leather",
		scaled = true,
		minSize = 10,
		name = "Status",
	})
	-- The forge has no batches: its button takes the stepper's place.
	if self.mode == "forge" then
		card.minus.holder.Visible = false
		card.plus.holder.Visible = false
		card.field.Visible = false
		card.countText.Visible = false
		card.all.holder.Visible = false
		card.craft.holder.Position = UDim2.fromOffset(706 - ORIGIN[1], 655 - ORIGIN[2])
	end
	self.card = card
end

-- Crafting: the running smelt and the stations within reach.
function CraftingPanel:_queue(window: Instance)
	local right = {}
	Parchment.Text("SMELTING", at(1218, 180, 250, 38), window, { size = 24 })
	right.slots = Parchment.Text("", at(1480, 180, 112, 38), window, { size = 24, align = "Right" })
	right.job = Widgets.Make("Frame", { Name = "Job", BackgroundTransparency = 1, ZIndex = 3 }, window)
	place(right.job, at(1205, 230, 400, 94))
	Widgets.Sprite(
		"pm_queue_row",
		{ Name = "Art", Size = UDim2.fromScale(1, 1), ZIndex = 3 },
		right.job,
		Parchment.SliceFor("pm_queue_row", { 0, 0, 400, 94 })
	)
	right.jobArt = Widgets.Make("Frame", { Name = "Picture", BackgroundTransparency = 1, ZIndex = 4 }, right.job)
	place(right.jobArt, { 14, 17, 60, 60 })
	right.jobName = Parchment.Text(
		"",
		{ 95, 12, 165, 30 },
		right.job,
		{ size = 21, scaled = true, minSize = 11, z = 4 }
	)
	right.jobCount = Parchment.Text("", { 258, 12, 74, 30 }, right.job, { size = 19, align = "Right", z = 4 })
	local track = Widgets.Make("Frame", {
		Name = "Track",
		BackgroundColor3 = Layout.Color("sliderTrack"),
		BorderSizePixel = 0,
		ZIndex = 4,
	}, right.job)
	place(track, { 97, 50, 160, 18 })
	Widgets.Make("UICorner", { CornerRadius = UDim.new(0.5, 0) }, track)
	right.jobFill = Widgets.Fill("sliderFill", { Size = UDim2.fromScale(0, 1), ZIndex = 5 }, track)
	right.jobLeft = Parchment.Text("", { 258, 44, 74, 30 }, right.job, { size = 19, align = "Right", z = 4 })
	-- The row's ✕ is painted on its art; this is its touch area.
	local stop = Widgets.Make("TextButton", {
		Name = "Stop",
		Text = "",
		AutoButtonColor = false,
		BackgroundTransparency = 1,
		Position = UDim2.fromOffset(338, 18),
		Size = UDim2.fromOffset(60, 58),
		ZIndex = 6,
	}, right.job)
	stop.Activated:Connect(function()
		self.handlers.onStop()
	end)
	right.stop = stop
	-- Nothing smelting: the empty slot opens the smelting tab.
	right.empty = Parchment.Button("pm_queue_empty", at(1205, 230, 400, 92), window, function()
		if self.handlers.onEmpty then
			self.handlers.onEmpty()
		end
	end, { name = "Empty" })
	Parchment.Text("STATIONS NEARBY", at(1218, 348, 380, 34), window, { size = 22 })
	right.stations = {}
	right.hint = Parchment.Text("", at(1218, 608, 380, 150), window, {
		size = 17,
		wrap = true,
		color = "inkSoft",
		name = "Hint",
	})
	right.hint.TextYAlignment = Enum.TextYAlignment.Top
	self.right = right
end

-- Crafting: the station rows (built once, from the controller's list).
function CraftingPanel:SetStations(stations: { string })
	local right = self.right
	for index, station in stations do
		local y = 392 + (index - 1) * 52
		local on = Widgets.Sprite("pm_check_on", {
			Name = station .. "On",
			Position = UDim2.fromOffset(1222 - ORIGIN[1], y - ORIGIN[2]),
			Size = UDim2.fromOffset(38, 38),
			ZIndex = 3,
		}, self.window)
		local off = Widgets.Sprite("pm_check_off", {
			Name = station .. "Off",
			Position = UDim2.fromOffset(1224 - ORIGIN[1], y + 2 - ORIGIN[2]),
			Size = UDim2.fromOffset(34, 35),
			ZIndex = 3,
		}, self.window)
		local label = Parchment.Text(station, at(1276, y, 300, 38), self.window, { size = 21 })
		Parchment.Rule(at(1215, y + 45, 380, 2), self.window, "rule")
		right.stations[station] = { on = on, off = off, label = label }
	end
end

-- Forge: the vault gear a Permanent conversion can use, and its rules.
function CraftingPanel:_sources(window: Instance)
	local right = {}
	right.title = Parchment.Text("", at(1218, 180, 380, 38), window, { size = 24, name = "SourcesTitle" })
	local list = Widgets.Make("ScrollingFrame", {
		Name = "Sources",
		BackgroundTransparency = 1,
		BorderSizePixel = 0,
		CanvasSize = UDim2.new(),
		AutomaticCanvasSize = Enum.AutomaticSize.Y,
		ScrollingDirection = Enum.ScrollingDirection.Y,
		ScrollBarThickness = 6,
		ScrollBarImageColor3 = Layout.Color("paperEdge"),
		ZIndex = 3,
	}, window) :: ScrollingFrame
	place(list, at(1203, 228, 406, 240))
	Widgets.Make("UIListLayout", { Padding = UDim.new(0, 7), SortOrder = Enum.SortOrder.LayoutOrder }, list)
	right.list = list
	right.rows = {}
	right.notes = Parchment.Text("", at(1218, 480, 380, 270), window, {
		size = 17,
		wrap = true,
		color = "inkSoft",
		name = "Notes",
	})
	right.notes.TextYAlignment = Enum.TextYAlignment.Top
	self.right = right
end

-- A confirmation over the middle card (forge conversions), armed after a delay.
function CraftingPanel:_confirmCard(window: Instance)
	-- While the question is open the rest of the window takes no presses, so
	-- the recipe and piece it names cannot change under it.
	self.confirmScrim = Widgets.Make("TextButton", {
		Name = "ConfirmScrim",
		Active = true,
		AutoButtonColor = false,
		BackgroundColor3 = Layout.Color("veil"),
		BackgroundTransparency = 0.75,
		BorderSizePixel = 0,
		Selectable = false,
		Size = UDim2.fromScale(1, 1),
		Text = "",
		Visible = false,
		ZIndex = 11,
	}, window)
	local card = Widgets.Make("Frame", {
		Name = "Confirm",
		Active = true,
		BackgroundColor3 = Layout.Color("paper"),
		BorderSizePixel = 0,
		Visible = false,
		ZIndex = 12,
	}, window)
	place(card, at(512, 176, 664, 590))
	Widgets.Make("UICorner", { CornerRadius = UDim.new(0, 10) }, card)
	Widgets.Make("UIStroke", { Color = Layout.Color("paperEdge"), Thickness = 2 }, card)
	self.confirmText = Parchment.Text("", { 30, 26, 604, 400 }, card, {
		size = 22,
		wrap = true,
		scaled = true,
		minSize = 12,
		z = 13,
	})
	self.confirmText.TextYAlignment = Enum.TextYAlignment.Top
	self.confirmYes = Parchment.Button("pm_button_craft", { 30, 470, 300, 92 }, card, function()
		local fn = self.confirmFn
		if fn and self.confirmArmed then
			self:HideConfirm()
			fn()
		end
	end, { name = "Yes", label = "", color = "cream", size = 30, inset = 64, z = 13 })
	self.confirmNo = Parchment.Button("pm_button_paper", { 400, 486, 220, 60 }, card, function()
		self:HideConfirm()
	end, { name = "No", label = "Cancel", size = 22, inset = 12, z = 13 })
	self.confirmCard = card
end

function CraftingPanel:_chosen()
	for _, entry in self.entries do
		if entry.id == self.selected then
			return entry
		end
	end
	return nil
end

function CraftingPanel:_visible()
	local shown = {}
	for _, entry in self.entries do
		if (self.category == nil or entry.category == self.category) and ItemInfo.Matches(entry.name, self.query) then
			table.insert(shown, entry)
		end
	end
	return shown
end

function CraftingPanel:_drawList()
	local focused = nil
	local focus = GuiService.SelectedObject
	for _, row in self.rows do
		if focus and focus:IsDescendantOf(row.holder) then
			focused = row.entry.id
		end
		row.holder:Destroy()
	end
	self.rows = {}
	for order, entry in self:_visible() do
		local holder = Widgets.Make("Frame", {
			Name = entry.id,
			BackgroundTransparency = 1,
			LayoutOrder = order,
			Size = UDim2.fromOffset(401, ROW_HEIGHT),
			ZIndex = 4,
		}, self.list)
		local chosen = entry.id == self.selected
		local rowArt = Widgets.Sprite(if chosen then "pm_recipe_row_selected" else "pm_recipe_row", {
			Name = "Art",
			Size = UDim2.fromScale(1, 1),
			ZIndex = 4,
		}, holder, Parchment.SliceFor("pm_recipe_row", { 0, 0, 401, ROW_HEIGHT }))
		self:_art(entry, {
			Name = "Picture",
			AnchorPoint = Vector2.new(0.5, 0.5),
			Position = UDim2.fromOffset(52, ROW_HEIGHT / 2),
			Size = UDim2.fromOffset(46, 40),
			ScaleType = Enum.ScaleType.Fit,
			ZIndex = 5,
		}, holder)
		local label = (if entry.locked then "🔒 " else "")
			.. entry.name
			.. (if (entry.quantity or 1) > 1 then (" ×%d"):format(entry.quantity) else "")
		local can = entry.can or 0
		-- Clear of the count badge by the chevron.
		Parchment.Text(label, { 104, 4, 208, ROW_HEIGHT - 8 }, holder, {
			size = 22,
			scaled = true,
			minSize = 12,
			color = if can > 0 and entry.here and not entry.locked then "ink" else "inkSoft",
			z = 5,
		})
		-- How many the inputs pay for, by the chevron.
		if can > 0 and not entry.locked then
			local badge = Widgets.Make("Frame", {
				Name = "Can",
				AnchorPoint = Vector2.new(1, 0.5),
				BackgroundColor3 = Layout.Color(if entry.here then "badge" else "questOpen"),
				BorderSizePixel = 0,
				Position = UDim2.fromOffset(354, ROW_HEIGHT / 2),
				Size = UDim2.fromOffset(34, 24),
				ZIndex = 5,
			}, holder)
			Widgets.Make("UICorner", { CornerRadius = UDim.new(0, 5) }, badge)
			Parchment.Text(if can >= CraftingPanel.MAX_BATCH then "50+" else tostring(can), { 0, 0, 34, 24 }, badge, {
				size = 16,
				color = "cream",
				align = "Center",
				scaled = true,
				minSize = 9,
				z = 6,
			})
		end
		local press = Parchment.Pressable(holder, rowArt, function()
			self:Select(entry.id)
		end)
		table.insert(self.rows, { holder = holder, entry = entry })
		if entry.id == focused then
			GuiService.SelectedObject = press
		end
	end
end

function CraftingPanel:_drawChips(entry)
	local stats = ItemInfo.Stats({ catalogId = entry.output })
	for index, chip in self.card.chips do
		local stat = stats[index]
		chip.frame.Visible = stat ~= nil
		for _, child in chip.glyph:GetChildren() do
			child:Destroy()
		end
		if stat then
			chip.text.Text = stat.text
			local glyph = stat.glyph and STAT_GLYPHS[stat.glyph]
			if glyph then
				Widgets.Sprite(glyph, {
					Name = "Glyph",
					Size = UDim2.fromScale(1, 1),
					ImageColor3 = Layout.Color("ink"),
					ZIndex = 4,
				}, chip.glyph)
				chip.text.Position = UDim2.fromOffset(42, 4)
				chip.text.Size = UDim2.fromOffset(chip.width - 50, 60)
			else
				chip.text.Position = UDim2.fromOffset(10, 4)
				chip.text.Size = UDim2.fromOffset(chip.width - 20, 60)
			end
		end
	end
end

-- What it needs: one card per input, have (green or red) / need. True when
-- every input is covered.
function CraftingPanel:_drawNeeds(entry, count: number): boolean
	local needs = self.card.needs
	for _, child in needs:GetChildren() do
		child:Destroy()
	end
	local inputs = entry.inputs or {}
	local enough = true
	local width = math.min(102, (332 - (#inputs - 1) * 9) / math.max(#inputs, 1))
	for index, input in inputs do
		local need = input.needed * count
		local have = input.owned
		enough = enough and have >= need
		local holder = Widgets.Make("Frame", { Name = input.id, BackgroundTransparency = 1, ZIndex = 3 }, needs)
		place(holder, { (index - 1) * (width + 9), 0, width, 152 })
		Widgets.Sprite(
			"pm_req_card",
			{ Name = "Art", Size = UDim2.fromScale(1, 1), ZIndex = 3 },
			holder,
			Parchment.SliceFor("pm_req_card", { 0, 0, width, 152 })
		)
		local icon = ItemSlot.IconFor(input.id)
		if icon then
			Widgets.Sprite(icon, {
				Name = "Icon",
				AnchorPoint = Vector2.new(0.5, 0),
				Position = UDim2.new(0.5, 0, 0, 14),
				Size = UDim2.fromOffset(64, 64),
				ZIndex = 4,
			}, holder)
		end
		Parchment.Text(input.name, { 6, if icon then 80 else 22, width - 12, if icon then 28 else 70 }, holder, {
			size = 19,
			align = "Center",
			scaled = true,
			wrap = true,
			minSize = 10,
			z = 4,
		})
		local counts = Widgets.Text({ font = "serif", textSize = 21, color = "ink" }, {
			Name = "Counts",
			Position = UDim2.fromOffset(4, 108),
			Size = UDim2.fromOffset(width - 8, 32),
			RichText = true,
			Text = ('<font color="#%s">%d</font> / %d'):format(
				Layout.Color(if have >= need then "haveEnough" else "haveShort"):ToHex(),
				have,
				need
			),
			TextScaled = true,
			TextStrokeTransparency = 1,
			TextXAlignment = Enum.TextXAlignment.Center,
			ZIndex = 4,
		}, holder)
		Widgets.TextCap(counts, 21, 10)
	end
	return enough
end

function CraftingPanel:_drawCard()
	local card = self.card
	local entry = self:_chosen()
	for _, child in card.art:GetChildren() do
		child:Destroy()
	end
	if entry == nil then
		card.name.Text = if #self.entries == 0
			then "Loading…"
			elseif #self:_visible() == 0 then "Nothing matches"
			else "Choose a recipe"
		card.where.Text = ""
		for _, chip in card.chips do
			chip.frame.Visible = false
		end
		self:_drawNeeds({ inputs = {} }, 1)
		card.craft.SetEnabled(false)
		card.all.SetEnabled(false)
		card.minus.SetEnabled(false)
		card.plus.SetEnabled(false)
		self:_drawSources(nil)
		return
	end
	local icon = ItemSlot.IconFor(entry.output)
	self:_art(entry, {
		Name = "Big",
		AnchorPoint = Vector2.new(0.5, 0.5),
		Position = UDim2.fromScale(0.5, 0.5),
		-- A category glyph stands in faintly, at a size it stays sharp.
		Size = if icon then UDim2.fromOffset(220, 220) else UDim2.fromOffset(140, 140),
		ScaleType = Enum.ScaleType.Fit,
		ImageTransparency = if icon then 0 else 0.35,
		ZIndex = 3,
	}, card.art)
	card.name.Text = entry.name .. (if (entry.quantity or 1) > 1 then (" ×%d"):format(entry.quantity) else "")
	self:_drawChips(entry)
	card.where.Text = if entry.locked then (entry.lockText or "Locked") else (entry.where or "")
	card.where.TextColor3 = Layout.Color(if entry.here and not entry.locked then "inkSoft" else "leather")
	local count = if entry.timed then self.count else 1
	local enough = self:_drawNeeds(entry, count)
	card.countText.Text = tostring(count)
	if self.mode ~= "forge" then
		-- The stepper is for batches, which only smelting has.
		for _, part in { card.minus.holder, card.plus.holder, card.field, card.countText } do
			part.Visible = entry.timed == true
		end
	end
	card.minus.SetEnabled(entry.timed == true and self.count > 1)
	card.plus.SetEnabled(entry.timed == true and self.count < CraftingPanel.MAX_BATCH)
	card.craft.label.Text = if entry.locked then "LOCKED" else (entry.verb or "CRAFT")
	self:_resolveSource(entry)
	local sourceNeeded = entry.sources ~= nil
	local ready = enough
		and entry.here ~= false
		and not entry.locked
		and not self.busy
		-- One smelt at a time: the furnace is busy until the running job ends.
		and not (entry.timed and self.job ~= nil)
		and (not sourceNeeded or self.source ~= nil)
	card.craft.SetEnabled(ready)
	if self.mode ~= "forge" then
		card.all.holder.Visible = entry.timed == true
		card.all.SetEnabled(entry.here ~= false and (entry.can or 0) > 0 and not self.busy and self.job == nil)
	end
	self:_drawSources(entry)
end

-- Keeps the chosen source valid for `entry`; the only candidate is chosen for
-- the player.
function CraftingPanel:_resolveSource(entry)
	local sources = entry.sources
	if sources == nil then
		self.source = nil
		return
	end
	for _, source in sources do
		if source.id == self.source then
			return
		end
	end
	self.source = if #sources == 1 then sources[1].id else nil
end

-- Forge: the source rows for a Permanent conversion, or what the Forge does.
function CraftingPanel:_drawSources(entry)
	if self.mode ~= "forge" then
		return
	end
	local right = self.right
	local focusedSource = nil
	local focus = GuiService.SelectedObject
	for _, row in right.rows do
		if focus and focus:IsDescendantOf(row) then
			focusedSource = row.Name
		end
		row:Destroy()
	end
	right.rows = {}
	local sources = entry and entry.sources
	if sources == nil then
		right.title.Text = "THE FORGE"
		right.notes.Text = "Forged gear goes to your lobby backpack; its materials come from your vault.\n\n"
			.. "A Permanent version of a weapon, tool or armour piece stays with you when you die. "
			.. "Choose a Permanent recipe to convert gear from your vault."
		return
	end
	right.title.Text = "FROM YOUR VAULT"
	for order, source in sources do
		local holder = Widgets.Make("Frame", {
			Name = source.id,
			BackgroundTransparency = 1,
			LayoutOrder = order,
			Size = UDim2.fromOffset(396, 66),
			ZIndex = 4,
		}, right.list)
		local rowArt = Widgets.Sprite(if source.id == self.source then "pm_recipe_row_selected" else "pm_recipe_row", {
			Name = "Art",
			Size = UDim2.fromScale(1, 1),
			ZIndex = 4,
		}, holder, Parchment.SliceFor("pm_recipe_row", { 0, 0, 396, 66 }))
		Parchment.Text(source.name, { 22, 4, 230, 58 }, holder, { size = 21, scaled = true, minSize = 11, z = 5 })
		Parchment.Text(source.detail or "", { 250, 4, 92, 58 }, holder, {
			size = 17,
			color = "inkSoft",
			align = "Right",
			scaled = true,
			minSize = 10,
			z = 5,
		})
		local press = Parchment.Pressable(holder, rowArt, function()
			self.source = source.id
			self:_drawCard()
		end)
		if focusedSource == source.id then
			GuiService.SelectedObject = press
		end
		table.insert(right.rows, holder)
	end
	right.notes.Text = if #sources == 0
		then "Vault an ordinary one of these to convert it."
		else "Choose the piece to convert. The ordinary item is consumed; its quality roll is kept exactly. "
			.. "Permanent items stay with you when you die; dropping one lets whoever picks it up own it."
end

function CraftingPanel:_step(delta: number)
	self.count = math.clamp(self.count + delta, 1, CraftingPanel.MAX_BATCH)
	self:_drawCard()
end

function CraftingPanel:_go(count: number)
	local entry = self:_chosen()
	if entry then
		self.handlers.onCraft(entry, if entry.timed then count else nil, self.source)
	end
end

function CraftingPanel:SelectCategory(id: string?)
	self.category = id
	for name, tab in self.tabs do
		tab.on.Visible = name == id
		tab.off.Visible = name ~= id
	end
	local shown = self:_visible()
	local keep = false
	for _, entry in shown do
		keep = keep or entry.id == self.selected
	end
	if not keep then
		self.selected = if shown[1] then shown[1].id else nil
		self.count = 1
		self.source = nil
	end
	self:_drawList()
	self:_drawCard()
end

function CraftingPanel:Select(id: string)
	if id ~= self.selected then
		self.count = 1
		self.source = nil
		self.card.status.Text = ""
		self:HideConfirm()
	end
	self.selected = id
	self:_drawList()
	self:_drawCard()
end

-- The entries, in list order (redrawn in place; the choice is kept).
function CraftingPanel:SetEntries(entries)
	self.entries = entries
	self:SelectCategory(self.category)
end

-- Crafting: which stations are within reach ({[station] = true}).
function CraftingPanel:SetNearby(nearby)
	for station, entry in self.right.stations or {} do
		local on = nearby[station] == true
		entry.on.Visible = on
		entry.off.Visible = not on
		entry.label.TextColor3 = Layout.Color(if on then "ink" else "inkSoft")
	end
end

-- Crafting: the running smelt {entry, count, done, progress (0-1), left (s)} or nil.
function CraftingPanel:SetJob(job)
	local right = self.right
	local changed = (self.job == nil) ~= (job == nil)
	self.job = job
	if changed then
		self:_drawCard()
	end
	right.job.Visible = job ~= nil
	right.empty.holder.Visible = job == nil
	right.slots.Text = if job then "1/1" else "0/1"
	if job then
		if right.jobRecipe ~= job.entry.id then
			right.jobRecipe = job.entry.id
			for _, child in right.jobArt:GetChildren() do
				child:Destroy()
			end
			self:_art(job.entry, {
				Name = "Picture",
				Size = UDim2.fromScale(1, 1),
				ScaleType = Enum.ScaleType.Fit,
				ZIndex = 4,
			}, right.jobArt)
		end
		right.jobName.Text = job.entry.name
		right.jobCount.Text = ("%d / %d"):format(job.done, job.count)
		right.jobFill.Size = UDim2.fromScale(math.clamp(job.progress, 0, 1), 1)
		local left = math.max(0, math.ceil(job.left))
		right.jobLeft.Text = ("%02d:%02d"):format(left // 60, left % 60)
	else
		right.jobRecipe = nil
	end
end

function CraftingPanel:SetHint(text: string)
	if self.right.hint then
		self.right.hint.Text = text
	end
end

function CraftingPanel:SetStatus(text: string?)
	self.card.status.Text = text or ""
end

-- While a request is on its way, the main button stays dimmed.
function CraftingPanel:SetBusy(busy: boolean)
	self.busy = busy
	self:_drawCard()
end

-- Asks before something that cannot be undone; the confirm button arms after
-- `delay` seconds so the text gets read.
function CraftingPanel:Confirm(text: string, yes: string, delay: number, onYes)
	self.confirmFn = onYes
	self.confirmArmed = false
	self.confirmText.Text = text
	self.confirmYes.label.Text = "READ FIRST…"
	self.confirmYes.SetEnabled(false)
	self.confirmCard.Visible = true
	self.confirmScrim.Visible = true
	-- A gamepad's focus moves into the question, on Cancel.
	if GuiService.SelectedObject ~= nil then
		GuiService.SelectedObject = self.confirmNo.button
	end
	local fn = onYes
	task.delay(delay, function()
		if self.confirmFn == fn and self.confirmCard.Visible then
			self.confirmArmed = true
			self.confirmYes.label.Text = yes
			self.confirmYes.SetEnabled(true)
		end
	end)
end

function CraftingPanel:HideConfirm()
	local wasOpen = self.confirmCard.Visible
	self.confirmFn = nil
	self.confirmArmed = false
	self.confirmCard.Visible = false
	self.confirmScrim.Visible = false
	local focus = GuiService.SelectedObject
	if wasOpen and focus and focus:IsDescendantOf(self.confirmCard) then
		GuiService.SelectedObject = self.card.craft.button
	end
end

function CraftingPanel:IsConfirming(): boolean
	return self.confirmCard.Visible
end

return CraftingPanel
