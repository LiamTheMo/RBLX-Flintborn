-- The Settings window (art/reference/ui/lobby/03_settings.png, spec
-- docs/ui/SettingsScreen.md), built only from the Kit: four large tabs down the
-- left (Gameplay, Audio, Graphics, Controls; the accessibility settings live in
-- Graphics and Audio, ARCHITECTURE D1), each a page of section headers,
-- sliders with value boxes, checkboxes with a description, a dropdown and key
-- caps, with RESET and APPLY under the page. Only settings that work are shown
-- (D2). The view only draws and reports; SettingsController keeps the draft,
-- saves on APPLY and feeds values back with SetValues and SetKeys.
--
-- Positions are design px from the window outline's top-left; the mockup
-- draws it at (287, 150), so screen x = 287 + x and y = 150 + y.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Keybinds = require(ReplicatedStorage.Shared.Settings.Keybinds)
local SettingsRules = require(ReplicatedStorage.Shared.Settings.SettingsRules)
local Kit = require(script.Parent.Parent.Kit)

local SettingsWindow = {}
SettingsWindow.__index = SettingsWindow

-- The mockup's window outline (287, 150, 1098 × 656).
SettingsWindow.SIZE = { 1098, 656 }

-- Tab icons: the kit's flat glyphs, dark on parchment and white on the
-- selected leather tab, as the mockup draws its gamepad, speaker, monitor and
-- gears (the kit's gamepad, speaker and monitor are stand-in drawings, D19).
SettingsWindow.TABS = {
	{ id = "Gameplay", icon = "gamepad" },
	{ id = "Audio", icon = "speaker" },
	{ id = "Graphics", icon = "monitor" },
	{ id = "Controls", icon = "gears" },
}

-- What RESET puts back on each tab: its settings and its keys.
SettingsWindow.TAB_SETTINGS = {
	Gameplay = { "cameraSensitivity", "musicVolume", "effectsVolume", "showDamage", "showNames", "invertCamera" },
	Audio = { "musicVolume", "effectsVolume", "subtitles" },
	Graphics = { "graphicsQuality", "uiScale", "colourBlindMode", "reducedMotion" },
	Controls = {},
}
SettingsWindow.TAB_KEYS = {
	Gameplay = { "Interact", "Backpack", "Map", "Sprint" },
	Controls = "all",
}

-- Movement stays with Roblox (Keybinds.IsAllowed): shown, never rebindable.
SettingsWindow.FIXED_KEYS = {
	{ "Move Forward", "W" },
	{ "Move Backward", "S" },
	{ "Move Left", "A" },
	{ "Move Right", "D" },
	{ "Jump", "Space" },
}

-- The Gameplay page's KEY BINDS rows after the fixed ones (the mockup's rows;
-- Crouch is gone from the game, D21).
SettingsWindow.GAMEPLAY_KEYS = {
	{ "Interact", "Interact" },
	{ "Open Backpack", "Backpack" },
	{ "Open Map", "Map" },
	{ "Sprint", "Sprint" },
}

-- Key names spelled out as the mockup writes them.
local KEY_TEXT = {
	LeftShift = "Left Shift",
	RightShift = "Right Shift",
	LeftControl = "Left Ctrl",
	RightControl = "Right Ctrl",
	LeftAlt = "Left Alt",
	RightAlt = "Right Alt",
}

-- A key as its cap shows it ("E", "Left Shift", "1", "Space").
function SettingsWindow.KeyText(key: string?): string
	if key == nil or key == "" then
		return "—"
	end
	return KEY_TEXT[key] or Keybinds.Display(key)
end

-- The title label's place (its ink lands at 422, 188 on screen).
local HEADER = { titleX = 132, titleY = 29.5 }

-- Columns (window px). The left column holds the page's settings, the right
-- one KEY BINDS (Gameplay) or the page's notes.
local LEFT_X = 301
local LEFT_W = 384
local LABEL_X = 309
local RIGHT_X = 731
local RIGHT_W = 330
local HEADER_Y = 108
local HEADER_H = 42
-- Slider rows: track centres 68 px apart (mockup 358, 426, 494 on screen).
local SLIDER_Y = { 208, 276, 344 }
local SLIDER_W = 376
local CHECK_PITCH = 56
-- Key rows: 36 px apart from y 162, caps 101 × 27 at x 950.
local KEY_Y = 162
local KEY_PITCH = 36
local KEY_X = 950
local KEY_W = 101
local KEY_H = 27

local function volume(value: number): string
	return ("%d"):format(value)
end

local function sensitivity(value: number): string
	return ("%.1f"):format(SettingsRules.MouseSensitivity(value))
end

local function times(value: number): string
	return ("%.1f×"):format(value)
end

-- handlers: onApply(), onReset(tab), onChange(key, value), onRebind(id),
-- onReplayTutorial(), onTab(tab), onClosed() (the window closed by any route).
function SettingsWindow.new(parent: Instance?, handlers)
	local self = setmetatable({}, SettingsWindow)
	self.handlers = handlers
	-- setting key -> setters (a setting can show on more than one page)
	self.setters = {}
	-- action id -> key caps
	self.keycaps = {}
	self.pages = {}
	self.tabs = {}
	self.dropdowns = {}
	-- page id -> its selectable controls in reading order (gamepad)
	self.controls = {}
	-- "Page.settingKey" -> the control showing it (scenes and verifiers)
	self.fields = {}
	self.notes = {}
	self.values = SettingsRules.Resolve(nil)

	local screen = Kit.Screen.new("FlintbornSettings", {
		size = SettingsWindow.SIZE,
		parent = parent,
		onClose = function()
			self:CloseDropdowns()
			if handlers.onClosed then
				handlers.onClosed()
			end
		end,
	})
	self.screen = screen
	-- Escape / B close an open dropdown list before the window.
	screen.Back = function(target)
		if not self:CloseDropdowns() then
			target:Close()
		end
	end
	screen.window.SelectionGroup = true
	-- The banner header as M03 draws it (spec: the dark gear 337, 172, 63 × 65;
	-- SETTINGS cap 34 px from x 422; the rule at y 237 from x 317 to 1290;
	-- close 1304, 169, 61 × 57).
	local window = Kit.Window.new(screen, {
		title = "Settings",
		icon = "ink:gears",
		iconRect = { 50, 22, 63, 65 },
		titleSize = 44,
		titleRect = { HEADER.titleX, HEADER.titleY, 600, 54 },
		ruleRect = { 30, 87, 973, 2 },
		closeRect = { 1017, 19, 61, 57 },
	})
	self.window = window
	self.close = window.close
	local visual = window.base.visual
	self.visual = visual

	local tabs = {}
	for index, tab in SettingsWindow.TABS do
		local item = Kit.Tab.new(visual, {
			id = tab.id,
			name = tab.id,
			-- Mockup tabs 316–549 × 80, tops 259, 353, 446, 539.
			rect = { 29, 109 + (index - 1) * 93.33, 234, 80 },
			label = tab.id,
			icon = "ink:" .. tab.icon,
			selectedIcon = "white:" .. tab.icon,
			iconSize = 46,
			iconX = 22,
			labelX = 92,
			variant = "large",
			zIndex = 8,
		})
		self.tabs[tab.id] = item
		table.insert(tabs, item)
		self.pages[tab.id] = Kit.Core.Make("Frame", {
			Name = "Page_" .. tab.id,
			BackgroundTransparency = 1,
			Size = UDim2.fromScale(1, 1),
			Visible = false,
			ZIndex = 6,
		}, visual)
		self.controls[tab.id] = {}
	end
	self.tabGroup = Kit.TabGroup.new(tabs, function(id)
		self:SelectTab(id)
	end)

	-- Rule.Column: 1 px at x 564 on screen.
	Kit.Divider.new(visual, {
		name = "TabDivider",
		rect = { 277, 109, 1, 442 },
		variant = "ink",
		color = "rule",
		thickness = 1,
		zIndex = 7,
	})
	self:_gameplay(self.pages.Gameplay)
	self:_audio(self.pages.Audio)
	self:_graphics(self.pages.Graphics)
	self:_controlsPage(self.pages.Controls)

	-- The rule above the buttons, the plant sketch and RESET / APPLY.
	Kit.Divider.new(visual, {
		name = "BottomRule",
		rect = { 115, 567, 948, 2 },
		variant = "ink",
		color = "inkSoft",
		zIndex = 7,
	})
	Kit.Icon.new(visual, { name = "Sketch", rect = { 70, 522, 44, 118 }, icon = "lk_emblem_leaf", zIndex = 7 })
	self.reset = Kit.Button.new(visual, {
		name = "Reset",
		rect = { 551, 581, 232, 55 },
		label = "Reset",
		variant = "secondary",
		icon = "ink:refresh",
		iconSize = 30,
		iconGap = 14,
		-- Width-matched to the mockup's RESET (65 px; Merriweather Bold is wider).
		textSize = 20.5,
		zIndex = 8,
		onPress = function()
			self:CloseDropdowns()
			handlers.onReset(self.tab)
		end,
	})
	self.apply = Kit.Button.new(visual, {
		name = "Apply",
		rect = { 797, 580, 261, 56 },
		label = "Apply",
		zIndex = 8,
		onPress = function()
			self:CloseDropdowns()
			handlers.onApply()
		end,
	})
	screen:SetDefaultSelection(self.tabs.Gameplay.control.hit)
	self:SetDirty(false)
	self:SelectTab("Gameplay")
	return self
end

-- Registers a setter for `key` so SetValues reaches every control showing it.
function SettingsWindow:_bind(key: string, setter)
	self.setters[key] = self.setters[key] or {}
	table.insert(self.setters[key], setter)
end

function SettingsWindow:_change(key: string, value)
	self.values[key] = value
	for _, setter in self.setters[key] or {} do
		setter(value)
	end
	self.handlers.onChange(key, value)
end

function SettingsWindow:_control(page: Instance, component, key: string?)
	local id = page.Name:sub(6)
	table.insert(self.controls[id], component.control.hit)
	if key then
		self.fields[id .. "." .. key] = component
	end
end

-- A section header with its rule (GAMEPLAY, KEY BINDS) and the line-art emblem
-- the mockup draws beside it.
-- The heading is the spec's size (cap 16–17 px); its rule is Rule.Heading
-- (#C49061, 2 px), 40 px under the header's top.
local function header(page: Instance, x: number, w: number, text: string, emblem: { any }?, y: number?)
	local top = y or HEADER_Y
	-- A Kit.Text heading rather than a SectionHeader: the header sizes its label
	-- to a measured width that comes out short for Merriweather Bold at 22 px
	-- and cuts the word off ("GAMEP…").
	Kit.Text.new(page, {
		name = "Header",
		rect = { x, top, w, HEADER_H - 6 },
		text = text,
		role = "sectionHeader",
		textSize = 22,
		zIndex = 7,
	})
	Kit.Divider.new(page, {
		name = "HeaderRule",
		rect = { x, top + 40, w, 2 },
		variant = "ink",
		color = "rule",
		zIndex = 7,
	})
	if emblem then
		Kit.Icon.new(page, { name = "Emblem", rect = emblem[2], icon = emblem[1], zIndex = 7 })
	end
end

local function leftHeader(page: Instance, text: string)
	header(page, LEFT_X, 263, text, { "campfire", { 594, 104, 54, 54 } })
end

local function rightHeader(page: Instance, text: string)
	header(page, RIGHT_X, 188, text, { "lk_emblem_rune", { 966, 92, 26, 70 } })
end

-- A row label in the mockup's book weight (Merriweather Regular, 17 px).
local function rowLabel(page: Instance, text: string, rect: { number }, name: string?, size: number?)
	return Kit.Core.Label(page, {
		name = name or "Label",
		text = text,
		role = "rowLabel",
		size = size or 16,
		scaled = true,
		rect = rect,
		z = 7,
	})
end

-- A labelled slider row whose track is centred on window y `cy`.
function SettingsWindow:_slider(page: Instance, cy: number, label: string, key: string, format)
	local setting = SettingsRules.Get(key) :: any
	rowLabel(page, label, { LABEL_X, cy - 44, LEFT_W - 20, 26 }, label)
	local slider = Kit.Slider.new(page, {
		name = key,
		rect = { LABEL_X, cy - 16, SLIDER_W, 32 },
		min = setting.min,
		max = setting.max,
		step = setting.step,
		value = self.values[key],
		format = format,
		zIndex = 7,
		onChange = function(value)
			self:_change(key, value)
		end,
	})
	self:_bind(key, function(value)
		slider:SetValue(value)
	end)
	self:_control(page, slider, key)
	return slider
end

-- A checkbox row with its description; the box's top is at window y `top`.
function SettingsWindow:_check(page: Instance, top: number, label: string, description: string, key: string)
	local box = Kit.Checkbox.new(page, {
		name = key,
		rect = { LABEL_X + 2, top - 2, LEFT_W - 24, 40 },
		label = label,
		description = description,
		checked = self.values[key] == true,
		variant = "gold",
		boxSize = 33,
		textSize = 17,
		descriptionSize = 14,
		zIndex = 7,
		onToggle = function(checked)
			self:_change(key, checked)
		end,
	})
	self:_bind(key, function(value)
		box:SetChecked(value == true)
	end)
	self:_control(page, box, key)
	return box
end

-- The thin rule between a page's sliders and its checkboxes (Rule.Section, 1 px).
local function sectionRule(page: Instance, y: number)
	Kit.Divider.new(page, {
		name = "SectionRule",
		rect = { LEFT_X - 1, y, 385, 1 },
		variant = "ink",
		color = "rule",
		thickness = 1,
		zIndex = 7,
	})
end

-- The right column's notes: a header and wrapped text.
local function notes(page: Instance, title: string, text: string, y: number?, h: number?)
	rightHeader(page, title)
	return Kit.Text.new(page, {
		name = "Notes",
		rect = { RIGHT_X + 12, y or 162, RIGHT_W - 12, h or 380 },
		text = text,
		role = "bodySoft",
		wrap = true,
		yAlign = "Top",
		zIndex = 7,
	})
end

-- A key row: label, a hairline under it and one cap. `id` is the rebindable action
-- (nil for the fixed movement keys, whose caps take no presses).
function SettingsWindow:_keyRow(parent: Instance, page: Instance, y: number, label: string, id: string?, fixed: string?)
	local x = if parent == page then 744 else 10
	local capX = if parent == page then KEY_X else LEFT_W - 22 - KEY_W
	rowLabel(parent, label, { x, y, capX - x - 14, KEY_H }, "Label_" .. (id or label), 15)
	-- Rule.Key: a faint 1 px line under the label, 31 px below the row's top.
	Kit.Divider.new(parent, {
		name = "Rule",
		rect = { x - 1, y + 31, capX - x - 6, 1 },
		variant = "hairline",
		thickness = 1,
		zIndex = 6,
	})
	local cap = Kit.KeyCap.new(parent, {
		name = "Key_" .. (id or label),
		rect = { capX, y, KEY_W, KEY_H },
		text = if fixed then SettingsWindow.KeyText(fixed) else "",
		variant = "flat",
		zIndex = 7,
		onPress = if id
			then function()
				self.handlers.onRebind(id)
			end
			else nil,
	})
	if id then
		self.keycaps[id] = self.keycaps[id] or {}
		table.insert(self.keycaps[id], cap)
		self:_control(page, cap)
	end
	return cap
end

function SettingsWindow:_gameplay(page: Instance)
	leftHeader(page, "Gameplay")
	self:_slider(page, SLIDER_Y[1], "Camera Sensitivity", "cameraSensitivity", sensitivity)
	self:_slider(page, SLIDER_Y[2], "Music Volume", "musicVolume", volume)
	self:_slider(page, SLIDER_Y[3], "Effects Volume", "effectsVolume", volume)
	sectionRule(page, 377)
	self:_check(page, 392, "Show Damage Numbers", "Numbers pop up over what you hit", "showDamage")
	self:_check(page, 392 + CHECK_PITCH, "Show Names", "Name tags above other players", "showNames")
	self:_check(page, 392 + CHECK_PITCH * 2, "Invert Camera", "Moving up looks down", "invertCamera")
	self:_divider(page)

	rightHeader(page, "Key Binds")
	local row = 0
	for _, fixed in SettingsWindow.FIXED_KEYS do
		self:_keyRow(page, page, KEY_Y + row * KEY_PITCH, fixed[1], nil, fixed[2])
		row += 1
	end
	for _, entry in SettingsWindow.GAMEPLAY_KEYS do
		self:_keyRow(page, page, KEY_Y + row * KEY_PITCH, entry[1], entry[2])
		row += 1
	end
	self.notes.Gameplay = Kit.Text.new(page, {
		name = "KeyNote",
		rect = { 744, KEY_Y + row * KEY_PITCH, 307, KEY_H },
		text = "",
		role = "small",
		scaled = true,
		zIndex = 7,
	})
end

function SettingsWindow:_audio(page: Instance)
	leftHeader(page, "Audio")
	self:_slider(page, SLIDER_Y[1], "Music Volume", "musicVolume", volume)
	self:_slider(page, SLIDER_Y[2], "Effects Volume", "effectsVolume", volume)
	sectionRule(page, 309)
	self:_check(page, 324, "Subtitles", "Show alert sounds as text on screen", "subtitles")
	self:_divider(page)
	notes(
		page,
		"About Sound",
		"Music sets the volume of music tracks, and Effects every other sound: combat, tools, "
			.. "alerts and the world around you.\n\nSubtitles write alert sounds (storms, "
			.. "bosses, extraction) on screen as well."
	)
end

function SettingsWindow:_graphics(page: Instance)
	leftHeader(page, "Graphics")
	local setting = SettingsRules.Get("graphicsQuality") :: any
	rowLabel(page, "Graphics Quality", { LABEL_X, 176, 130, 43 }, "Graphics Quality")
	local dropdown = Kit.Dropdown.new(page, {
		name = "graphicsQuality",
		rect = { 447, 176, 236, 43 },
		options = setting.options,
		value = self.values.graphicsQuality,
		layer = page :: GuiObject,
		zIndex = 9,
		onSelect = function(option)
			self:_change("graphicsQuality", option)
		end,
	})
	table.insert(self.dropdowns, dropdown)
	self:_bind("graphicsQuality", function(value)
		dropdown:SetValue(value)
	end)
	self:_control(page, dropdown, "graphicsQuality")
	self:_slider(page, SLIDER_Y[2], "UI Scale", "uiScale", times)
	sectionRule(page, 309)
	self:_check(page, 324, "Colour-blind Palette", "Rarity colours that are easier to tell apart", "colourBlindMode")
	self:_check(page, 324 + CHECK_PITCH, "Reduced Motion", "Menus and effects move less", "reducedMotion")
	self:_divider(page)
	notes(
		page,
		"About Quality",
		"Low: a quarter of the particles and no shadows, the smoothest on older phones.\n\n"
			.. "Medium: most particles, shadows on.\n\nHigh: everything on.\n\n"
			.. "UI Scale sizes every menu and the HUD."
	)
end

function SettingsWindow:_controlsPage(page: Instance)
	leftHeader(page, "Controls")
	local count = #SettingsWindow.FIXED_KEYS + #Keybinds.Actions
	local list = Kit.Scroll.new(page, {
		name = "Keys",
		rect = { LEFT_X, 160, LEFT_W, 390 },
		gap = 0,
		padBottom = 8,
		contentHeight = count * KEY_PITCH + 10,
		zIndex = 7,
	})
	self.keyList = list
	local content = list:Content()
	local order = 0
	local function row(): Frame
		order += 1
		return Kit.Core.Make("Frame", {
			Name = "Row" .. order,
			BackgroundTransparency = 1,
			LayoutOrder = order,
			Size = UDim2.fromOffset(LEFT_W - 20, KEY_PITCH),
			ZIndex = 7,
		}, content)
	end
	for _, fixed in SettingsWindow.FIXED_KEYS do
		self:_keyRow(row(), page, 4, fixed[1], nil, fixed[2])
	end
	for _, action in Keybinds.Actions do
		self:_keyRow(row(), page, 4, action.label, action.id)
	end
	self:_divider(page)

	rightHeader(page, "Tutorial")
	Kit.Text.new(page, {
		name = "TutorialText",
		rect = { RIGHT_X + 12, 162, RIGHT_W - 12, 66 },
		text = "Walk through the first steps again: gathering, crafting and getting out alive.",
		role = "bodySoft",
		wrap = true,
		yAlign = "Top",
		zIndex = 7,
	})
	local replay = Kit.Button.new(page, {
		name = "ReplayTutorial",
		rect = { RIGHT_X + 12, 236, 260, 55 },
		label = "Replay Tutorial",
		variant = "secondary",
		textSize = 20,
		zIndex = 7,
		onPress = function()
			self.handlers.onReplayTutorial()
		end,
	})
	self:_control(page, replay, "replayTutorial")
	header(page, RIGHT_X, 263, "Changing Keys", nil, 310)
	self.notes.Controls = Kit.Text.new(page, {
		name = "KeyNote",
		rect = { RIGHT_X + 12, 364, RIGHT_W - 12, 180 },
		text = "",
		role = "bodySoft",
		wrap = true,
		yAlign = "Top",
		zIndex = 7,
	})
end

-- The column divider between a page's two columns.
function SettingsWindow:_divider(page: Instance)
	-- Rule.Column: 2 px at x 993 on screen.
	Kit.Divider.new(page, {
		name = "ColumnDivider",
		rect = { 706, 109, 2, 442 },
		variant = "ink",
		color = "rule",
		zIndex = 7,
	})
end

-- Gamepad order on the open page: tabs up and down the left; right from a tab
-- into the page; the page's controls top to bottom, then RESET and APPLY.
function SettingsWindow:_linkGamepad(id: string)
	local list = table.clone(self.controls[id])
	table.insert(list, self.reset.control.hit)
	table.insert(list, self.apply.control.hit)
	local tabHit = self.tabs[id].control.hit
	for index, hit in list do
		hit.NextSelectionUp = list[index - 1]
		hit.NextSelectionDown = list[index + 1]
		hit.NextSelectionLeft = tabHit
	end
	self.apply.control.hit.NextSelectionLeft = self.reset.control.hit
	self.reset.control.hit.NextSelectionRight = self.apply.control.hit
	for index, tab in SettingsWindow.TABS do
		local hit = self.tabs[tab.id].control.hit
		hit.NextSelectionRight = list[1]
		local previous = SettingsWindow.TABS[index - 1]
		local following = SettingsWindow.TABS[index + 1]
		hit.NextSelectionUp = if previous then self.tabs[previous.id].control.hit else nil
		hit.NextSelectionDown = if following then self.tabs[following.id].control.hit else self.reset.control.hit
	end
end

function SettingsWindow:SelectTab(id: string)
	self.tab = id
	self.tabGroup:Select(id)
	for name, page in self.pages do
		page.Visible = name == id
	end
	self:CloseDropdowns()
	self:_linkGamepad(id)
	if self.handlers.onTab then
		self.handlers.onTab(id)
	end
end

-- Shows `values` (every SettingsRules key) on every page.
function SettingsWindow:SetValues(values)
	for key, value in values do
		self.values[key] = value
		for _, setter in self.setters[key] or {} do
			setter(value)
		end
	end
end

-- Shows each action's key; `capturing` is the action waiting for a key press.
-- `canRebind` is false without a keyboard. `note` is the last rebind's result.
function SettingsWindow:SetKeys(map, capturing: string?, note: string?, canRebind: boolean)
	for id, caps in self.keycaps do
		for _, cap in caps do
			cap:SetEnabled(canRebind)
			cap:SetCapturing(capturing == id)
			if capturing ~= id then
				cap:SetText(SettingsWindow.KeyText(map[id]))
			end
		end
	end
	local hint = if not canRebind
		then "Connect a keyboard to change keys. Gamepad buttons are fixed."
		elseif capturing then ("Press the new key for %s, or Escape to cancel."):format(
			Keybinds.Get(capturing).label
		)
		else "Click a key, then press the new one. A key another action uses swaps with it. Gamepad buttons are fixed."
	self.notes.Controls:SetText(if note and note ~= "" then note .. "\n\n" .. hint else hint)
	self.notes.Gameplay:SetText(
		if capturing
			then "Press a key, or Escape to cancel."
			elseif note and note ~= "" then note
			elseif canRebind then "Click a key to change it."
			else "Connect a keyboard to change keys."
	)
end

-- Closes an open dropdown list; true when one was open (Escape / B close the
-- list before the window).
function SettingsWindow:CloseDropdowns(): boolean
	local any = false
	for _, dropdown in self.dropdowns do
		if dropdown:IsOpen() then
			dropdown:SetOpen(false)
			any = true
		end
	end
	return any
end

-- APPLY is lit only while there is something to save.
function SettingsWindow:SetDirty(dirty: boolean)
	self.apply:SetEnabled(dirty)
end

function SettingsWindow:Destroy()
	self.screen:Destroy()
end

return SettingsWindow
