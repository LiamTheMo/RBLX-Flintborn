-- The parchment Settings window (art/reference/ui/parchment/10_settings.png,
-- spec docs/ui/SettingsScreen.md): five tabs down the left (Gameplay, Audio,
-- Graphics, Controls, Accessibility), each a page of sliders, checkboxes, a
-- dropdown and keycaps, with RESET and APPLY under the page. The Gameplay page is
-- the reference layout. The view only draws and reports; SettingsController keeps
-- the draft, saves on APPLY and feeds values back with SetValues and SetKeys.
--
-- Positions are the reference sheet's own pixels (the window art was cut at
-- ORIGIN), so they read straight off the image.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Keybinds = require(ReplicatedStorage.Shared.Settings.Keybinds)
local SettingsRules = require(ReplicatedStorage.Shared.Settings.SettingsRules)
local Layout = require(script.Parent.Layout)
local Parchment = require(script.Parent.Parchment)
local Widgets = require(script.Parent.Widgets)

local SettingsPanel = {}
SettingsPanel.__index = SettingsPanel

-- The window art's size and where its top-left sits on the reference sheet.
SettingsPanel.SIZE = { 1630, 706 }
local ORIGIN = { 21, 58 }

SettingsPanel.TABS = {
	{ id = "Gameplay", glyph = "pm_glyph_gear" },
	{ id = "Audio", glyph = "pm_glyph_sound" },
	{ id = "Graphics", glyph = "pm_glyph_monitor" },
	{ id = "Controls", glyph = "pm_glyph_gamepad" },
	{ id = "Accessibility", glyph = "pm_glyph_person" },
}

-- What RESET puts back on each tab: its settings and its keys.
SettingsPanel.TAB_SETTINGS = {
	Gameplay = {
		"musicVolume",
		"effectsVolume",
		"cameraSensitivity",
		"showDamage",
		"showNames",
		"invertCamera",
		"graphicsQuality",
	},
	Audio = { "musicVolume", "effectsVolume", "subtitles" },
	Graphics = { "graphicsQuality", "uiScale" },
	Controls = {},
	Accessibility = { "colourBlindMode", "reducedMotion", "subtitles", "uiScale" },
}
SettingsPanel.TAB_KEYS = {
	Gameplay = { "Backpack", "Interact", "Sprint", "Map" },
	Controls = "all",
}

-- Labels shown for keys that read badly as KeyCode names.
local KEY_TEXT = {
	LeftShift = "SHIFT",
	RightShift = "R SHIFT",
	LeftControl = "CTRL",
	RightControl = "R CTRL",
	LeftAlt = "ALT",
	RightAlt = "ALT",
}

-- A key as its keycap shows it (TAB, SHIFT, 1, E).
function SettingsPanel.KeyText(key: string?): string
	if key == nil or key == "" then
		return "—"
	end
	return KEY_TEXT[key] or string.upper(Keybinds.Display(key))
end

-- Reference-sheet rectangle → window rectangle.
local function at(x: number, y: number, w: number, h: number)
	return { x - ORIGIN[1], y - ORIGIN[2], w, h }
end

-- Content columns (reference x) and rows.
local LEFT = { mark = 448, label = 491, slider = 683, sliderWidth = 260, value = 966, right = 1021 }
local RIGHT = { mark = 1060, label = 1123, key = 1279, right = 1558 }
local HEADER_Y = 220
-- The right column's header rules start clear of the column divider.
local RIGHT_RULE = 1100 - ORIGIN[1]
local SLIDER_ROWS = { 303, 360, 418 }
local CHECK_ROWS = { 480, 531, 585 }
local KEY_ROWS = { 300, 367, 436, 507, 578 }

local function percent(value: number): string
	return string.format("%d", value)
end

local function times(value: number): string
	return string.format("%.1f×", value)
end

function SettingsPanel.new(parent: Instance?, handlers)
	local self = setmetatable({}, SettingsPanel)
	self.handlers = handlers
	self.screen = Parchment.Screen("FlintbornSettings", SettingsPanel.SIZE, 20, parent)
	local window = self.screen.window
	self.window = window
	-- setting key -> list of setters (a setting can show on more than one page)
	self.setters = {}
	-- action id -> list of keycaps
	self.keycaps = {}
	self.pages = {}
	self.tabs = {}
	self.notes = {}
	self.dropdowns = {}
	self.values = SettingsRules.Resolve(nil)

	Widgets.Sprite("pm_window_settings", {
		Name = "Art",
		Size = UDim2.fromScale(1, 1),
		ZIndex = 1,
	}, window)

	-- The close button is painted into the window art; this is its touch area.
	local close = Widgets.Make("TextButton", {
		Name = "Close",
		Text = "",
		AutoButtonColor = false,
		BackgroundTransparency = 1,
		Position = UDim2.fromOffset(1504 - ORIGIN[1], 96 - ORIGIN[2]),
		Size = UDim2.fromOffset(94, 90),
		ZIndex = 10,
	}, window)
	close.Activated:Connect(function()
		handlers.onClose()
	end)
	self.close = close

	for index, tab in SettingsPanel.TABS do
		local y = 193.5 + (index - 1) * 100.5
		self.tabs[tab.id] = Parchment.Tab(at(86, y, 316, 100), window, tab.id, tab.glyph, function()
			self:SelectTab(tab.id)
		end)
		local page = Widgets.Make("Frame", {
			Name = "Page_" .. tab.id,
			BackgroundTransparency = 1,
			Size = UDim2.fromScale(1, 1),
			Visible = false,
			ZIndex = 2,
		}, window)
		self.pages[tab.id] = page
	end

	self:_gameplay(self.pages.Gameplay)
	self:_audio(self.pages.Audio)
	self:_graphics(self.pages.Graphics)
	self:_controls(self.pages.Controls)
	self:_accessibility(self.pages.Accessibility)

	self.reset = Parchment.Button("pm_button_reset", at(1077, 634, 212, 77), window, function()
		handlers.onReset(self.tab)
	end, { name = "Reset" })
	self.apply = Parchment.Button("pm_button_apply", at(1307, 627, 276, 89), window, function()
		handlers.onApply()
	end, { name = "Apply" })
	self:SetDirty(false)
	self:SelectTab("Gameplay")
	return self
end

-- Registers a setter for `key` so SetValues reaches every widget showing it.
function SettingsPanel:_bind(key: string, setter)
	self.setters[key] = self.setters[key] or {}
	table.insert(self.setters[key], setter)
end

function SettingsPanel:_change(key: string, value)
	self.values[key] = value
	for _, setter in self.setters[key] or {} do
		setter(value)
	end
	self.handlers.onChange(key, value)
end

-- A labelled slider row centred on reference y `cy`.
function SettingsPanel:_slider(page: Instance, cy: number, label: string, key: string, format)
	local setting = SettingsRules.Get(key)
	Parchment.Text(label, at(LEFT.label, cy - 20, LEFT.slider - LEFT.label - 4, 40), page, {
		size = 19.5,
		scaled = true,
	})
	local value = Parchment.Text("", at(LEFT.value, cy - 20, LEFT.right - LEFT.value, 40), page, { size = 21 })
	local slider
	slider = Parchment.Slider(
		at(LEFT.slider, cy - 10, LEFT.sliderWidth, 20),
		page,
		setting.min,
		setting.max,
		setting.step or 1,
		function(v)
			value.Text = format(v)
			self:_change(key, v)
		end
	)
	self:_bind(key, function(v)
		slider.Set(v)
		value.Text = format(v)
	end)
end

function SettingsPanel:_check(page: Instance, cy: number, label: string, key: string)
	local box
	box = Parchment.Checkbox(at(LEFT.label - 1, cy - 21, 470, 42), page, label, function(on)
		self:_change(key, on)
	end)
	self:_bind(key, box.Set)
end

function SettingsPanel:_quality(page: Instance, cy: number, openUp: boolean)
	local setting = SettingsRules.Get("graphicsQuality")
	Parchment.Text("Graphics Quality", at(LEFT.label, cy - 20, 210, 40), page, { size = 20, scaled = true })
	local dropdown = Parchment.Dropdown(at(713, cy - 32, 304, 64), page, setting.options, function(option)
		self:_change("graphicsQuality", option)
	end, openUp)
	self:_bind("graphicsQuality", dropdown.Set)
	table.insert(self.dropdowns, dropdown)
end

-- A ruled line under a left-column row.
local function leftRule(page: Instance, y: number)
	Parchment.Rule(at(461, y, LEFT.right - 2 - 461, 2), page, "rule")
end

local function rightRule(page: Instance, y: number)
	Parchment.Rule(at(1100, y, 450, 2), page, "rule")
end

-- The right column's notes: a header and wrapped text.
local function notes(page: Instance, title: string, text: string)
	Parchment.Header(title, at(RIGHT.mark, HEADER_Y, RIGHT.right - RIGHT.mark, 34), page, RIGHT_RULE)
	Parchment.Text(text, at(1100, 280, 458, 330), page, { size = 21, wrap = true, color = "inkSoft" }).TextYAlignment =
		Enum.TextYAlignment.Top
end

local function divider(page: Instance)
	Parchment.Rule(at(1061, 264, 2, 352), page, "headerRule")
end

-- A key row: label and one rebindable keycap at reference y `cy`.
function SettingsPanel:_keyRow(page: Instance, cy: number, label: string, id: string, x: number, labelWidth: number)
	Parchment.Text(label, at(x, cy - 20, labelWidth, 40), page, { size = 21, scaled = true })
	local key = Parchment.Keycap("", at(x + labelWidth + 6, cy - 24, 60, 48), page, function()
		self.handlers.onRebind(id)
	end)
	key.left = x + labelWidth + 6
	self.keycaps[id] = self.keycaps[id] or {}
	table.insert(self.keycaps[id], key)
end

function SettingsPanel:_gameplay(page: Instance)
	Parchment.Header("Gameplay", at(LEFT.mark, HEADER_Y, LEFT.right - LEFT.mark, 34), page)
	self:_slider(page, SLIDER_ROWS[1], "Music", "musicVolume", percent)
	self:_slider(page, SLIDER_ROWS[2], "Effects", "effectsVolume", percent)
	self:_slider(page, SLIDER_ROWS[3], "Camera Sensitivity", "cameraSensitivity", percent)
	for _, y in { 330, 388, 448 } do
		leftRule(page, y)
	end
	self:_check(page, CHECK_ROWS[1], "Show Damage", "showDamage")
	self:_check(page, CHECK_ROWS[2], "Show Names", "showNames")
	self:_check(page, CHECK_ROWS[3], "Invert Camera", "invertCamera")
	for _, y in { 505, 558, 612 } do
		leftRule(page, y)
	end
	self:_quality(page, 663, true)
	divider(page)

	Parchment.Header("Key Bindings", at(RIGHT.mark, HEADER_Y, RIGHT.right - RIGHT.mark, 34), page, RIGHT_RULE)
	-- Movement stays on W A S D (Roblox's own); it is shown, not rebindable.
	Parchment.Text("Move", at(RIGHT.label, KEY_ROWS[1] - 20, 150, 40), page, { size = 21 })
	for index, letter in { "W", "A", "S", "D" } do
		Parchment.Keycap(letter, at(RIGHT.key + (index - 1) * 59.7, KEY_ROWS[1] - 24, 48, 48), page)
	end
	local rows = { { "Inventory", "Backpack" }, { "Interact", "Interact" }, { "Sprint", "Sprint" }, { "Map", "Map" } }
	for index, row in rows do
		self:_keyRow(page, KEY_ROWS[index + 1], row[1], row[2], RIGHT.label, RIGHT.key - 6 - RIGHT.label)
	end
	for _, y in { 333, 402, 471, 542, 612 } do
		rightRule(page, y)
	end
	self.notes.Gameplay = Parchment.Text("", at(1100, 615, 458, 18), page, { size = 15, color = "leather" })
end

function SettingsPanel:_audio(page: Instance)
	Parchment.Header("Audio", at(LEFT.mark, HEADER_Y, LEFT.right - LEFT.mark, 34), page)
	self:_slider(page, SLIDER_ROWS[1], "Music", "musicVolume", percent)
	self:_slider(page, SLIDER_ROWS[2], "Effects", "effectsVolume", percent)
	leftRule(page, 330)
	leftRule(page, 388)
	self:_check(page, 418, "Subtitles for alert sounds", "subtitles")
	leftRule(page, 448)
	divider(page)
	notes(
		page,
		"About Sound",
		"Music sets the volume of music tracks, and Effects every other sound: combat, tools, "
			.. "alerts and the world around you.\n\nSubtitles write alert sounds (storms, "
			.. "bosses, extraction) on screen as well."
	)
end

function SettingsPanel:_graphics(page: Instance)
	Parchment.Header("Graphics", at(LEFT.mark, HEADER_Y, LEFT.right - LEFT.mark, 34), page)
	self:_quality(page, SLIDER_ROWS[1], false)
	leftRule(page, 340)
	self:_slider(page, 375, "UI Scale", "uiScale", times)
	leftRule(page, 405)
	divider(page)
	notes(
		page,
		"Quality",
		"Low: a quarter of the particles and no shadows, the smoothest on older phones.\n\n"
			.. "Medium: most particles, shadows on.\n\nHigh: everything on.\n\n"
			.. "UI Scale sizes every menu and the HUD."
	)
end

function SettingsPanel:_controls(page: Instance)
	Parchment.Header("Controls", at(LEFT.mark, HEADER_Y, RIGHT.right - LEFT.mark, 34), page)
	local list = Widgets.Make("ScrollingFrame", {
		Name = "Keys",
		BackgroundTransparency = 1,
		BorderSizePixel = 0,
		Position = UDim2.fromOffset(453 - ORIGIN[1], 266 - ORIGIN[2]),
		Size = UDim2.fromOffset(1110, 350),
		CanvasSize = UDim2.new(),
		AutomaticCanvasSize = Enum.AutomaticSize.Y,
		ScrollingDirection = Enum.ScrollingDirection.Y,
		ScrollBarThickness = 8,
		ScrollBarImageColor3 = Layout.Color("paperEdge"),
		ZIndex = 3,
	}, page) :: ScrollingFrame
	Widgets.Make("UIGridLayout", {
		CellSize = UDim2.fromOffset(540, 57),
		CellPadding = UDim2.fromOffset(20, 0),
		FillDirection = Enum.FillDirection.Horizontal,
		SortOrder = Enum.SortOrder.LayoutOrder,
	}, list)
	for order, action in Keybinds.Actions do
		local cell = Widgets.Make("Frame", {
			Name = action.id,
			BackgroundTransparency = 1,
			LayoutOrder = order,
			ZIndex = 3,
		}, list)
		Parchment.Text(action.label, { 14, 8, 300, 40 }, cell, { size = 22, scaled = true })
		local key = Parchment.Keycap("", { 330, 4, 60, 48 }, cell, function()
			self.handlers.onRebind(action.id)
		end)
		key.left = 330
		self.keycaps[action.id] = self.keycaps[action.id] or {}
		table.insert(self.keycaps[action.id], key)
		Parchment.Rule({ 8, 55, 524, 2 }, cell, "rule")
	end
	self.notes.Controls = Parchment.Text("", at(453, 626, 600, 84), page, {
		size = 19,
		wrap = true,
		color = "inkSoft",
	})
	self.notes.Controls.TextYAlignment = Enum.TextYAlignment.Top
end

function SettingsPanel:_accessibility(page: Instance)
	Parchment.Header("Accessibility", at(LEFT.mark, HEADER_Y, LEFT.right - LEFT.mark, 34), page)
	self:_check(page, 303, "Colour-blind palette", "colourBlindMode")
	leftRule(page, 330)
	self:_check(page, 360, "Reduced motion", "reducedMotion")
	leftRule(page, 388)
	self:_check(page, 418, "Subtitles for alert sounds", "subtitles")
	leftRule(page, 448)
	self:_slider(page, 478, "UI Scale", "uiScale", times)
	leftRule(page, 505)
	divider(page)
	Parchment.Header("Tutorial", at(RIGHT.mark, HEADER_Y, RIGHT.right - RIGHT.mark, 34), page, RIGHT_RULE)
	Parchment.Text(
		"Walk through the first steps again: gathering, crafting and getting out alive.",
		at(1100, 280, 458, 90),
		page,
		{ size = 21, wrap = true, color = "inkSoft" }
	).TextYAlignment =
		Enum.TextYAlignment.Top
	Parchment.Button("pm_button_parchment", at(1100, 385, 330, 76), page, function()
		self.handlers.onReplayTutorial()
	end, { label = "REPLAY TUTORIAL", size = 21, name = "ReplayTutorial" })
end

function SettingsPanel:SelectTab(id: string)
	self.tab = id
	for name, tab in self.tabs do
		tab.SetSelected(name == id)
		self.pages[name].Visible = name == id
	end
	for _, dropdown in self.dropdowns do
		dropdown.Close()
	end
	if self.handlers.onTab then
		self.handlers.onTab(id)
	end
end

-- Shows `values` (every SettingsRules key) on every page.
function SettingsPanel:SetValues(values)
	for key, value in values do
		self.values[key] = value
		for _, setter in self.setters[key] or {} do
			setter(value)
		end
	end
end

-- Shows each action's key; `capturing` is the action waiting for a key press.
-- `canRebind` is false without a keyboard. `note` replaces the hint lines.
function SettingsPanel:SetKeys(map, capturing: string?, note: string?, canRebind: boolean)
	for id, caps in self.keycaps do
		local text = if capturing == id then "…" else SettingsPanel.KeyText(map[id])
		for _, cap in caps do
			cap.SetText(text)
			local width = Parchment.KeyWidth(text)
			cap.holder.Size = UDim2.fromOffset(width, 48)
			if cap.SetEnabled then
				cap.SetEnabled(canRebind)
			end
		end
	end
	local hint = if not canRebind
		then "Connect a keyboard to change keys. Gamepad buttons are fixed."
		elseif capturing then ("Press the new key for %s, or click it again to cancel."):format(
			Keybinds.Get(capturing).label
		)
		else "Click a key, then press the new one. A key another action uses swaps with it."
	self.notes.Controls.Text = if note and note ~= "" then note .. "\n" .. hint else hint
	self.notes.Gameplay.Text = if capturing then "Press a key, or click it again to cancel." else note or ""
end

-- Closes an open dropdown list; true when one was open (gamepad B closes the
-- list before the window).
function SettingsPanel:CloseDropdowns(): boolean
	local any = false
	for _, dropdown in self.dropdowns do
		if dropdown.IsOpen() then
			dropdown.Close()
			any = true
		end
	end
	return any
end

-- APPLY is bright only while there is something to save.
function SettingsPanel:SetDirty(dirty: boolean)
	self.apply.SetEnabled(dirty)
end

function SettingsPanel:Destroy()
	self.screen.gui:Destroy()
end

return SettingsPanel
