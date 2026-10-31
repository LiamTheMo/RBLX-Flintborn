-- The recipe window (art/reference/ui/lobby/06_forge.png, docs/ui/ForgeScreen.md,
-- ARCHITECTURE §4.6), built only from the Kit. One layout, two modes:
--   "forge"     the Ancestral Forge in the lobby (ForgeController): vault-only
--               counts, a batch QUANTITY for special recipes, Permanent
--               conversions confirmed with a press-and-hold dialog
--   "crafting"  field crafting in a run (CraftingController): carried counts,
--               stations in reach, a QUANTITY (with All) for smelting only, and
--               the running smelt with its Stop button
-- Display only: data comes in through setters (RecipeModel entries) and presses
-- go out through callbacks. Layout numbers are design px inside the 1102 × 682
-- window (mockup position minus the window's 285, 132).
--
--   local window = RecipeWindow.new({ mode = "forge", name = "FlintbornForge", title = "Ancestral Forge",
--       subtitle = "Turn raw materials into tools for the island.", icon = "anvil_hammer",
--       categories = { { id = "Tools", label = "Tools" } }, onForge = function(entry, count) end })
--   window:SetEntries(RecipeModel.ForgeEntries(view), materials)
--   window:Open()

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local GuiService = game:GetService("GuiService")

local KitModel = require(ReplicatedStorage.Shared.UI.KitModel)
local RecipeModel = require(ReplicatedStorage.Shared.UI.RecipeModel)
local Kit = require(script.Parent.Parent.Kit)

local RecipeWindow = {}
RecipeWindow.__index = RecipeWindow

-- How long a Permanent conversion's CONVERT is held before it fires.
RecipeWindow.CONVERT_HOLD = 1.5

RecipeWindow.SIZE = { 1102, 680 }

-- Window-local layout (design px). Kit plates draw their visible edge on their
-- rect, so these are the mockup's bounds less the window's 285, 132.
local L = {
	-- The anvil art has a margin: this rect puts its ink on the mockup's 101 × 95.
	icon = { 50, 8, 107, 97 },
	title = { 184, 17, 560, 64 },
	titleSizes = { 46, 40 },
	subtitle = { 184, 72, 600, 30 },
	subtitleSize = 24,
	close = { 1004, 26, 63, 61 },
	topRule = { 37, 116, 1028, 2 },
	-- The column rules: left (faint, fading out), centre-left, centre-right.
	columnRules = { { 34, 118, 2, 518 }, { 371, 118, 2, 537 }, { 760, 118, 2, 547 } },
	clasps = { 0.242, 0.895 },
	recipesHead = { 58, 128, 140, 30 },
	headSize = 19,
	dropdown = { 196, 124, 160, 38 },
	-- The rail sits in the gutter between the rows and the column rule.
	recipeList = { 38, 161, 333, 456 },
	recipeRow = { 301, 69 },
	recipeGap = 7,
	rowIcon = { 12, 2, 66, 64 },
	rowTextX = 101,
	rowTitleSize = 18,
	rowSubtitleSize = 15,
	-- Phones and touch tablets: the handwritten row notes at 9 screen px or
	-- more at the window's phone scale (0.46–0.51 below the top bar).
	rowSubtitlePhone = 20,
	-- ...with a smaller icon there, so a two-line note has the room it needs.
	rowIconPhone = { 6, 10, 50, 48 },
	rowTextXPhone = 70,
	-- A row note too long for one line wraps onto two under a raised title.
	rowTwoLine = { titleY = 1, titleH = 25, subtitleY = 24, subtitleH = 45 },
	-- The Permanent mark on a conversion's icon corner (as a slot's star).
	rowMark = { 60, 2, 20, 20 },
	-- Room the lock takes at a locked row's right.
	rowLockRoom = 34,
	name = { 418, 128, 330, 38 },
	nameSize = 30,
	-- The item art has a margin: this rect puts its ink on the mockup's 243 × 233.
	picture = { 464, 167, 254, 255 },
	description = { 400, 416, 324, 56 },
	descriptionSize = 21,
	descriptionLine = 0.86,
	divider1 = { 389, 469, 356, 16 },
	requiresHead = { 401, 482, 200, 30 },
	smallHeadSize = 16,
	cards = { 395, 512, 347, 66 },
	cardGap = 8,
	cardIcon = { 14, 10, 54, 48 },
	cardTextX = 84,
	divider2 = { 388, 583, 371, 16 },
	quantityHead = { 391, 616, 100, 30 },
	stepper = { 493, 610, 158, 44 },
	stepperValueSize = 32,
	button = { 673, 599, 260, 66 },
	buttonSize = 25,
	buttonIcon = 39,
	buttonIconGap = 23,
	materialsHead = { 782, 129, 260, 30 },
	materialsSize = 19,
	materialList = { 763, 164, 312, 398 },
	materialRow = { 278, 59 },
	materialGap = 8,
	materialIcon = { 13, 7, 53, 46 },
	materialTextX = 84,
	materialTitleSize = 18,
	materialValueSize = 20,
	-- Crafting mode: the stepper carries All, so the button narrows; the right
	-- column keeps room for the smelt and the stations in reach.
	craft = {
		stepper = { 483, 610, 222, 44 },
		button = { 713, 599, 220, 66 },
		materialList = { 763, 164, 312, 262 },
		smeltHead = { 782, 446, 276, 26 },
		job = { 782, 472, 276, 24 },
		bar = { 782, 502, 190, 20 },
		stop = { 984, 492, 74, 40 },
		stationsHead = { 782, 538, 276, 26 },
		stations = { 782, 564, 276, 24 },
	},
}

local function hex(color: Color3): string
	return ("#%02X%02X%02X"):format(
		math.floor(color.R * 255 + 0.5),
		math.floor(color.G * 255 + 0.5),
		math.floor(color.B * 255 + 0.5)
	)
end

local function label(parent: Instance, props, size: number?)
	if size then
		props.textSize = size
	end
	return Kit.Text.new(parent, props)
end

-- A Kit.Scroll's content height: rows, gaps and its top and bottom padding.
local function listHeight(count: number, rowH: number, gap: number): number
	return if count > 0 then count * rowH + (count - 1) * gap + 14 else 0
end

-- Dims the big item picture for a locked recipe, as ListRow dims its icon.
local function dimIcon(icon, dim: boolean)
	local image = icon and icon.image
	if image == nil then
		return
	end
	if image:IsA("ImageLabel") then
		(image :: ImageLabel).ImageTransparency = if dim then 0.4 else 0
	elseif image:IsA("TextLabel") then
		(image :: TextLabel).TextTransparency = if dim then 0.4 else 0
	end
end

-- props: mode, name, title, subtitle, icon, categories ({{id, label}}),
-- onForge(entry, count), onStop(), parent.
function RecipeWindow.new(props)
	local mode = props.mode or "forge"
	local self = setmetatable({
		mode = mode,
		props = props,
		entries = {},
		byId = {},
		filtered = {},
		rows = {},
		materialRows = {},
		materials = {},
		cards = {},
		category = RecipeModel.ALL,
		selectedId = nil,
		count = 1,
		busy = false,
		phone = Kit.Scale.IsSmallTouch(),
		maid = KitModel.Maid(),
	}, RecipeWindow)
	local screen = Kit.Screen.new(props.name or "FlintbornRecipes", { size = RecipeWindow.SIZE, parent = props.parent })
	self.screen = screen
	-- The header as the mockup places it: the anvil, the small-caps title (D13)
	-- and the handwritten subtitle, the close button; the full-width rule
	-- under them is drawn below in the column rules' colour.
	local window = Kit.Window.new(screen, {
		title = props.title or "Ancestral Forge",
		subtitle = props.subtitle,
		icon = props.icon or "anvil_hammer",
		iconRect = L.icon,
		titleRect = L.title,
		smallCaps = true,
		smallCapsSizes = L.titleSizes,
		subtitleRect = L.subtitle,
		subtitleSize = L.subtitleSize,
		closeRect = L.close,
		rule = false,
		clasps = true,
		claspYs = L.clasps,
	})
	self.window = window
	local v = window.base.visual
	local z = window.base.z + 3
	self.visual = v
	Kit.Divider.new(v, { name = "TopRule", rect = L.topRule, variant = "ink", color = "rule", zIndex = z })
	for index, rect in L.columnRules do
		Kit.Divider.new(v, {
			name = "ColumnRule" .. index,
			rect = rect,
			variant = if index == 1 then "hairline" else "ink",
			color = if index == 1 then nil else "rule",
			fade = index == 1,
			zIndex = z,
		})
	end

	-- RECIPES -------------------------------------------------------------------
	label(
		v,
		{ name = "RecipesHead", rect = L.recipesHead, text = "Recipes", role = "sectionHeader", zIndex = z },
		L.headSize
	)
	local options, labelToId, idToLabel = { RecipeModel.ALL }, { [RecipeModel.ALL] = RecipeModel.ALL }, {}
	idToLabel[RecipeModel.ALL] = RecipeModel.ALL
	for _, category in props.categories or {} do
		table.insert(options, category.label)
		labelToId[category.label] = category.id
		idToLabel[category.id] = category.label
	end
	self.idToLabel = idToLabel
	self.dropdown = Kit.Dropdown.new(v, {
		name = "Category",
		rect = L.dropdown,
		options = options,
		value = RecipeModel.ALL,
		zIndex = z + 6,
		onSelect = function(value)
			self:SetCategory(labelToId[value] or RecipeModel.ALL)
		end,
	})
	self.recipeList = Kit.Scroll.new(v, {
		name = "Recipes",
		rect = L.recipeList,
		gap = L.recipeGap,
		railOverlay = true,
		zIndex = z,
	})

	-- The chosen recipe ------------------------------------------------------------
	self.nameText = label(v, {
		name = "RecipeName",
		rect = L.name,
		text = "",
		role = "itemTitle",
		caps = true,
		zIndex = z,
	}, L.nameSize)
	self.picture = Kit.ItemIcon.new(v, { name = "Picture", rect = L.picture, zIndex = z })
	self.description = label(v, {
		name = "Description",
		rect = L.description,
		text = "",
		role = "subtitleHand",
		color = "ink",
		align = "Center",
		wrap = true,
		zIndex = z,
	}, L.descriptionSize)
	-- The mockup's two lines sit 25 px apart.
	self.description.root.LineHeight = L.descriptionLine
	Kit.Divider.new(v, { name = "Divider1", rect = L.divider1, variant = "rule", zIndex = z })
	label(v, {
		name = "RequiresHead",
		rect = L.requiresHead,
		text = "Requires",
		role = "sectionHeader",
		zIndex = z,
	}, L.smallHeadSize)
	self.cardHolder = Kit.Core.Make("Frame", {
		Name = "Requires",
		BackgroundTransparency = 1,
		Position = UDim2.fromOffset(L.cards[1], L.cards[2]),
		Size = UDim2.fromOffset(L.cards[3], L.cards[4]),
		ZIndex = z,
	}, v)
	Kit.Divider.new(v, { name = "Divider2", rect = L.divider2, variant = "rule", zIndex = z })
	self.quantityHead = label(v, {
		name = "QuantityHead",
		rect = L.quantityHead,
		text = "Quantity",
		role = "sectionHeader",
		zIndex = z,
	}, L.smallHeadSize)
	local crafting = mode == "crafting"
	self.stepper = Kit.Stepper.new(v, {
		name = "Quantity",
		rect = if crafting then L.craft.stepper else L.stepper,
		min = 1,
		max = 1,
		value = 1,
		allLabel = if crafting then "All" else nil,
		buttons = "leather",
		valueSize = L.stepperValueSize,
		zIndex = z,
		onChange = function(value)
			self.count = value
			self:_renderCost()
		end,
	})
	self.button = Kit.Button.new(v, {
		name = "Forge",
		rect = if crafting then L.craft.button else L.button,
		label = if crafting then "Craft" else "Forge",
		icon = if crafting then "white:hammer" else "white:anvil",
		iconSize = L.buttonIcon,
		iconGap = L.buttonIconGap,
		textSize = L.buttonSize,
		zIndex = z + 1,
		onPress = function()
			self:_press()
		end,
	})

	-- YOUR MATERIALS -------------------------------------------------------------------
	label(v, {
		name = "MaterialsHead",
		rect = L.materialsHead,
		text = "Your Materials",
		role = "sectionHeader",
		zIndex = z,
	}, L.materialsSize)
	self.materialList = Kit.Scroll.new(v, {
		name = "Materials",
		rect = if crafting then L.craft.materialList else L.materialList,
		gap = L.materialGap,
		railOverlay = true,
		zIndex = z,
	})
	if crafting then
		self:_buildCraftingExtras(v, z)
	end

	-- Gamepad: rows lead right to the main button and it leads back to the
	-- chosen row (set as rows are built); until there are rows, close is first.
	screen:SetDefaultSelection(window.close.control.hit)
	self:_renderDetail()
	-- Phone and desktop row text follows the screen and the input devices.
	self.maid:Give(Kit.Scale.OnFormFactorChanged(function()
		local phone = Kit.Scale.IsSmallTouch()
		if phone ~= self.phone then
			self.phone = phone
			for id, row in self.rows do
				row:Destroy()
				self.rows[id] = nil
			end
			self:_renderList()
		end
	end))
	return self
end

function RecipeWindow:_buildCraftingExtras(v, z: number)
	local c = L.craft
	label(v, { name = "SmeltHead", rect = c.smeltHead, text = "Smelting", role = "sectionHeader", zIndex = z }, 18)
	self.jobText = label(v, { name = "Job", rect = c.job, text = "", role = "bodySoft", zIndex = z })
	self.jobBar = Kit.Bar.new(v, { name = "JobBar", rect = c.bar, fill = "orange", frame = "track", zIndex = z })
	self.stop = Kit.Button.new(v, {
		name = "Stop",
		rect = c.stop,
		label = "Stop",
		variant = "secondary",
		sizeClass = "s",
		zIndex = z,
		onPress = function()
			if self.props.onStop then
				self.props.onStop()
			end
		end,
	})
	label(v, {
		name = "StationsHead",
		rect = c.stationsHead,
		text = "Stations nearby",
		role = "sectionHeader",
		zIndex = z,
	}, 18)
	self.stationsText = label(v, { name = "Stations", rect = c.stations, text = "", role = "body", zIndex = z })
	self:SetJob(nil)
end

-- Opening and closing ------------------------------------------------------------------

function RecipeWindow:Open()
	self.screen:Open(Kit.Input.IsGamepad())
end

function RecipeWindow:Close()
	self.screen:Close()
end

function RecipeWindow:IsOpen(): boolean
	return self.screen:IsOpen()
end

-- Keeps the window fitted to the screen (ARCHITECTURE §1.1).
function RecipeWindow:Watch()
	self.screen:Watch()
end

-- The window title in faux small caps (D13).
function RecipeWindow:SetTitle(text: string)
	self.window:SetTitle(text)
end

-- Data --------------------------------------------------------------------------------

-- Replaces the recipes (and YOUR MATERIALS); the chosen recipe, category and
-- quantity stay where they still apply.
function RecipeWindow:SetEntries(entries, materials)
	self.entries = entries or {}
	self.byId = {}
	for _, entry in self.entries do
		self.byId[entry.id] = entry
	end
	if materials then
		self.materials = materials
	end
	self:_renderList()
	self:_renderMaterials()
end

function RecipeWindow:SetCategory(id: string)
	self.category = id
	self.dropdown:SetValue(self.idToLabel[id] or RecipeModel.ALL)
	self:_renderList()
end

-- Chooses a recipe; the quantity starts again at 1. A recipe chosen by code
-- (not by pressing its row) is scrolled into view.
function RecipeWindow:Select(id: string?, pressed: boolean?)
	if id ~= self.selectedId then
		self.count = 1
		local row = id and self.rows[id]
		if row and not pressed then
			self.recipeList:ScrollToRow(row.root, { center = true })
		end
	end
	self.selectedId = id
	for rowId, row in self.rows do
		row:SetSelected(rowId == id)
	end
	self:_renderDetail()
	self:_renderMaterials()
end

function RecipeWindow:Selected()
	return self.selectedId and self.byId[self.selectedId]
end

function RecipeWindow:Count(): number
	return self.count
end

-- While a request is in flight the main button shows its busy state.
function RecipeWindow:SetBusy(busy: boolean)
	self.busy = busy
	self:_renderButton()
end

-- Feedback after a request: a toast (kind "info" or "warn").
function RecipeWindow:SetStatus(title: string, text: string?, kind: string?)
	if title == "" then
		return
	end
	Kit.Toast.Show({ kind = kind or "info", title = title, text = text, duration = 4 })
end

-- Crafting: the running smelt ({name, done, count, progress, left}) or nil.
function RecipeWindow:SetJob(job)
	if self.jobText == nil then
		return
	end
	if job == nil then
		self.jobText:SetText("Nothing smelting")
		self.jobBar:Set(0, true)
		self.stop:SetEnabled(false)
		return
	end
	self.jobText:SetText(RecipeModel.JobText(job.name, job.done, job.count, job.left))
	self.jobBar:Set(job.progress)
	self.stop:SetEnabled(true)
end

-- Crafting: which stations are in reach ("Workbench, Furnace").
function RecipeWindow:SetStations(text: string)
	if self.stationsText then
		self.stationsText:SetText(text)
	end
end

-- Rendering ---------------------------------------------------------------------------------

function RecipeWindow:_rowFor(entry)
	local row = self.rows[entry.id]
	if row then
		return row
	end
	local function choose()
		self:Select(entry.id, true)
	end
	row = Kit.ListRow.new(self.recipeList:Content(), {
		name = entry.id,
		size = L.recipeRow,
		variant = "soft",
		itemId = entry.output,
		iconRect = if self.phone then L.rowIconPhone else L.rowIcon,
		textX = if self.phone then L.rowTextXPhone else L.rowTextX,
		title = entry.name,
		titleSize = L.rowTitleSize,
		-- The mockup's row descriptions are handwritten notes (D13).
		subtitle = entry.subtitle or "",
		subtitleHand = true,
		subtitleSize = if self.phone then L.rowSubtitlePhone else L.rowSubtitleSize,
		onPress = choose,
		-- A locked recipe is still chosen, so its unlock text shows.
		onLocked = choose,
	})
	-- A Permanent conversion: the star mark on the icon's corner.
	if entry.kind == "Permanent" then
		Kit.Icon.new(row.base.visual, {
			name = "PermanentMark",
			rect = L.rowMark,
			icon = "star",
			zIndex = row.base.z + 3,
		})
	end
	row.titleRect = { row.title.Position, row.title.Size }
	row.subtitleRect = { row.subtitle.Position, row.subtitle.Size }
	-- Gamepad: right goes to the main button.
	row.control.hit.NextSelectionRight = self.button.control.hit
	self.rows[entry.id] = row
	return row
end

-- One line for a note that fits, else two under a raised title. A locked
-- row's lines stop short of its lock.
function RecipeWindow:_fitSubtitle(row, text: string, locked: boolean)
	local subtitle = row.subtitle
	local size = if self.phone then L.rowSubtitlePhone else L.rowSubtitleSize
	local width = row.subtitleRect[2].X.Offset - (if locked then L.rowLockRoom else 0)
	local wide = Kit.Text.Width(text, "subtitleHand", size) > width
	local two = L.rowTwoLine
	subtitle.TextWrapped = wide
	if wide then
		row.title.Position = UDim2.fromOffset(row.titleRect[1].X.Offset, two.titleY)
		row.title.Size = UDim2.fromOffset(width, two.titleH)
		subtitle.Position = UDim2.fromOffset(row.subtitleRect[1].X.Offset, two.subtitleY)
		subtitle.Size = UDim2.fromOffset(width, two.subtitleH)
		subtitle.TextYAlignment = Enum.TextYAlignment.Top
		subtitle.LineHeight = 0.85
	else
		row.title.Position, row.title.Size = row.titleRect[1], row.titleRect[2]
		subtitle.Position = row.subtitleRect[1]
		subtitle.Size = UDim2.fromOffset(width, row.subtitleRect[2].Y.Offset)
		subtitle.TextYAlignment = Enum.TextYAlignment.Center
		subtitle.LineHeight = 1
	end
end

function RecipeWindow:_renderList()
	local list = RecipeModel.Filter(self.entries, self.category)
	self.filtered = list
	-- Gamepad selection on a recipe row that this render removes moves to the
	-- chosen row instead of being lost.
	local selected = GuiService.SelectedObject
	local onRow = false
	for _, row in self.rows do
		onRow = onRow or row.control.hit == selected
	end
	local used = {}
	for index, entry in list do
		local row = self:_rowFor(entry)
		used[entry.id] = true
		row.root.LayoutOrder = index
		row:SetTitle(entry.name)
		row:SetSubtitle(entry.subtitle or "")
		self:_fitSubtitle(row, entry.subtitle or "", entry.locked == true)
		row:SetState(if entry.locked then "locked" else "normal")
	end
	for id, row in self.rows do
		if not used[id] then
			row:Destroy()
			self.rows[id] = nil
		end
	end
	self.recipeList:SetContentHeight(listHeight(#list, L.recipeRow[2], L.recipeGap))
	-- Keep the chosen recipe when it is still listed, else take the first.
	local keep = self.selectedId and used[self.selectedId]
	local first = list[1]
	self:Select(if keep then self.selectedId elseif first then first.id else nil)
	local selectedRow = self.selectedId and self.rows[self.selectedId]
	local default = if selectedRow then selectedRow.control.hit else self.window.close.control.hit
	self.screen:SetDefaultSelection(default)
	self.button.control.hit.NextSelectionLeft = if selectedRow then selectedRow.control.hit else nil
	if self.screen:IsOpen() and selectedRow then
		local now = GuiService.SelectedObject
		local lost = onRow and (now == nil or now.Parent == nil or not now:IsDescendantOf(self.screen.gui))
		-- The rows arrived after the window opened on a gamepad: leave the ✕
		-- for the chosen recipe.
		local early = now == self.window.close.control.hit and Kit.Input.IsGamepad()
		if lost or early then
			GuiService.SelectedObject = default
		end
	end
end

function RecipeWindow:_renderMaterials()
	local needed = RecipeModel.Needed(self:Selected())
	local used = {}
	local size = L.materialRow
	for index, material in self.materials do
		local row = self.materialRows[material.catalogId]
		if row == nil then
			local catalogId = material.catalogId
			row = Kit.ListRow.new(self.materialList:Content(), {
				name = catalogId,
				size = size,
				variant = "soft",
				itemId = catalogId,
				iconRect = L.materialIcon,
				textX = L.materialTextX,
				title = material.name,
				titleSize = L.materialTitleSize,
				value = tostring(material.quantity),
				valueSize = L.materialValueSize,
				-- Selectable (gamepad reaches the counts); a press picks the
				-- first listed recipe that uses it.
				onPress = function()
					self:_pickUsing(catalogId)
				end,
			})
			-- Gamepad: left goes back to the main button.
			row.control.hit.NextSelectionLeft = self.button.control.hit
			self.materialRows[catalogId] = row
		end
		used[material.catalogId] = true
		row.root.LayoutOrder = index
		row:SetValue(tostring(material.quantity))
		row:SetSelected(needed[material.catalogId] == true)
	end
	for id, row in self.materialRows do
		if not used[id] then
			row:Destroy()
			self.materialRows[id] = nil
		end
	end
	self.materialList:SetContentHeight(listHeight(#self.materials, size[2], L.materialGap))
end

-- Chooses the first listed recipe that needs `catalogId` (a material row's
-- press); nothing changes when none does.
function RecipeWindow:_pickUsing(catalogId: string)
	for _, entry in self.filtered do
		for _, input in entry.inputs or {} do
			if input.catalogId == catalogId then
				self:Select(entry.id)
				return
			end
		end
	end
end

function RecipeWindow:_renderDetail()
	local entry = self:Selected()
	if entry == nil then
		self.nameText:SetText("")
		self.picture:SetItem(nil)
		self.description:SetText(if #self.entries == 0 then "" else "Nothing here yet.")
	else
		self.nameText:SetText(RecipeModel.NameOf(entry.output))
		self.picture:SetItem(entry.output)
		dimIcon(self.picture, entry.locked)
		local blocked = entry.locked or (entry.kind == "Permanent" and #(entry.sources or {}) == 0)
		self.description:SetText(
			if blocked then RecipeModel.Blocker(entry, 1) or "" else RecipeModel.Description(entry)
		)
	end
	local shown, max = RecipeModel.Quantity(entry)
	self.count = RecipeModel.Clamp(entry, self.count)
	self.quantityHead.root.Visible = shown
	self.stepper.root.Visible = shown
	self.stepper:SetRange(1, max)
	self.stepper:SetValue(self.count)
	self:_renderCost()
end

-- REQUIRES for the current quantity, and the main button.
function RecipeWindow:_renderCost()
	for _, card in self.cards do
		card:Destroy()
	end
	self.cards = {}
	local entry = self:Selected()
	if entry then
		local cost = RecipeModel.Cost(entry, self.count)
		if #cost <= 2 then
			self:_wideCards(cost)
		else
			self:_compactCards(cost)
		end
	end
	self:_renderButton()
end

local function countText(cost): string
	local have = tostring(cost.owned)
	if cost.short then
		have = ('<font color="%s">%s</font>'):format(hex(Kit.Tokens.Color("short")), have)
	end
	return ("%s / %d"):format(have, cost.need)
end

-- One or two inputs: the mockup's cards (icon, name, have / need).
function RecipeWindow:_wideCards(cost)
	local h = L.cards[4]
	local w = (L.cards[3] - L.cardGap) / 2
	for index, item in cost do
		local card = Kit.Panel.new(self.cardHolder, {
			name = item.catalogId,
			rect = { (index - 1) * (w + L.cardGap), 0, w, h },
			variant = "inset",
			pad = 0,
		})
		local c = card.base.visual
		local z = card.base.z + 1
		Kit.ItemIcon.new(c, { rect = L.cardIcon, itemId = item.catalogId, zIndex = z })
		-- hudSmall: Merriweather Bold at 15, shrinking to fit a long name.
		label(c, {
			name = "Name",
			rect = { L.cardTextX, 12, w - L.cardTextX - 6, 24 },
			text = item.name,
			role = "hudSmall",
			color = "inkLabel",
			scaled = true,
			zIndex = z,
		})
		label(c, {
			name = "Count",
			rect = { L.cardTextX, 35, w - L.cardTextX - 6, 28 },
			text = countText(item),
			role = "count",
			rich = true,
			zIndex = z,
		}, 20)
		card.root:SetAttribute("KitState", if item.short then "short" else "normal")
		table.insert(self.cards, card)
	end
end

-- Three or more inputs: compact cards in two rows.
function RecipeWindow:_compactCards(cost)
	local columns = math.ceil(#cost / 2)
	local gap = 6
	local w = (L.cards[3] - gap * (columns - 1)) / columns
	local h = (L.cards[4] - 4) / 2
	for index, item in cost do
		local column, line = (index - 1) % columns, (index - 1) // columns
		local card = Kit.Panel.new(self.cardHolder, {
			name = item.catalogId,
			rect = { column * (w + gap), line * (h + 4), w, h },
			variant = "inset",
			pad = 0,
		})
		local c = card.base.visual
		local z = card.base.z + 1
		Kit.ItemIcon.new(c, { rect = { 4, 2, h - 4, h - 4 }, itemId = item.catalogId, zIndex = z })
		local countW = math.ceil(Kit.Text.Width(("%d / %d"):format(item.owned, item.need), "count", 13)) + 4
		label(c, {
			name = "Name",
			rect = { h + 2, 0, w - h - countW - 8, h },
			text = item.name,
			role = "small",
			color = "inkLabel",
			zIndex = z,
		}, 12)
		label(c, {
			name = "Count",
			rect = { w - countW - 6, 0, countW, h },
			text = countText(item),
			role = "count",
			align = "Right",
			rich = true,
			zIndex = z,
		}, 13)
		card.root:SetAttribute("KitState", if item.short then "short" else "normal")
		table.insert(self.cards, card)
	end
end

function RecipeWindow:_renderButton()
	local entry = self:Selected()
	local button = self.button
	local verb = if entry then entry.verb else (if self.mode == "crafting" then "Craft" else "Forge")
	if entry and entry.locked then
		verb = "Locked"
	end
	if button.text ~= verb then
		button:SetLabel(verb)
	end
	local blocker = RecipeModel.Blocker(entry, self.count)
	self.blocker = blocker
	button.root:SetAttribute("Blocker", blocker or "")
	button:SetBusy(self.busy)
	button:SetEnabled(blocker == nil)
end

function RecipeWindow:_press()
	local entry = self:Selected()
	if entry == nil or self.busy or RecipeModel.Blocker(entry, self.count) then
		return
	end
	if self.props.onForge then
		self.props.onForge(entry, self.count)
	end
end

-- A Permanent conversion: names the exact item (pick one when the vault holds
-- several) and the Permanent rules; CONVERT is press-and-hold. `onConfirm`
-- gets the chosen source's instance id.
function RecipeWindow:ConfirmConversion(entry, onConfirm: (string) -> ())
	local sources = entry.sources or {}
	if #sources == 0 then
		return nil
	end
	local chosen = sources[1]
	local many = #sources > 1
	local text
	local rows = {}
	local handle = Kit.ConfirmDialog.Show({
		title = "Make it Permanent?",
		size = if many then { 700, 540 } else { 640, 420 },
		confirmLabel = "Convert",
		holdSeconds = RecipeWindow.CONVERT_HOLD,
		build = function(body, w, h)
			local listH = if many then math.min(#sources, 3) * 44 else 0
			text = label(body, {
				name = "Text",
				rect = { 0, 0, w, h - listH - (if many then 8 else 0) },
				text = RecipeModel.ConversionText(entry, chosen),
				role = "body",
				align = "Center",
				yAlign = "Top",
				wrap = true,
			}, 16)
			if many then
				local list = Kit.Scroll.new(body, { name = "Sources", rect = { 0, h - listH, w, listH }, gap = 4 })
				for index, source in sources do
					local row = Kit.ListRow.new(list:Content(), {
						name = source.id,
						size = { w - 24, 40 },
						layoutOrder = index,
						variant = "option",
						title = source.name,
						value = if source.detail ~= "" then source.detail else "standard",
						onPress = function()
							chosen = source
							text:SetText(RecipeModel.ConversionText(entry, chosen))
							for _, other in rows do
								other:SetSelected(other == rows[index])
							end
						end,
					})
					rows[index] = row
				end
				list:SetContentHeight(#sources * 44)
				rows[1]:SetSelected(true)
			end
		end,
		onConfirm = function()
			onConfirm(chosen.id)
		end,
	})
	self.confirm = handle
	return handle
end

function RecipeWindow:Destroy()
	self.maid:Clean()
	self.screen:Destroy()
end

return RecipeWindow
