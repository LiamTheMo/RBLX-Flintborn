-- The parchment menu kit (art/reference/ui/parchment): a full-screen menu window
-- that fits itself to the screen, and the controls its screens are built from —
-- serif ink text, section headers, rules, sprite buttons with hover and press,
-- leather/paper tabs, sliders, checkboxes, dropdowns and keycaps. Every rectangle
-- is {x, y, w, h} in the window's reference pixels (the window art's own size);
-- the window's UIScale maps them to the screen. Sprites without an uploaded id
-- fall back to Widgets' warm paper plates, so a screen reads before upload.

local ContextActionService = game:GetService("ContextActionService")
local GuiService = game:GetService("GuiService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local HudModel = require(ReplicatedStorage.Shared.UI.HudModel)
local UiAssets = require(ReplicatedStorage.Shared.UI.UiAssets)
local Layout = require(script.Parent.Layout)
local Widgets = require(script.Parent.Widgets)

local Parchment = {}

-- Image tints for a sprite button's states (no separate hover art for these).
Parchment.HOVER = Color3.new(0.93, 0.93, 0.93)
Parchment.PRESSED = Color3.new(0.8, 0.8, 0.8)
Parchment.DISABLED = Color3.new(0.72, 0.72, 0.72)
-- Space kept between the window and the screen's edges, in screen pixels.
Parchment.MARGIN = 8
-- The window never draws smaller than this (phones) or larger than this.
Parchment.MIN_SCALE = 0.3
Parchment.MAX_SCALE = 1.4

local SERIF = "serif"

local function rect(r): (UDim2, UDim2)
	return UDim2.fromOffset(r[1], r[2]), UDim2.fromOffset(r[3], r[4])
end

-- The 9-slice corner scale for sprite `name` drawn at `r`'s size, so its corners
-- shrink with a small box instead of overlapping (nil when it does not slice).
local function sliceFor(name: string, r): number?
	local sprite = UiAssets.sprite(name)
	if sprite == nil or type(sprite.slice) ~= "table" then
		return nil
	end
	return HudModel.SliceScale(sprite.w, sprite.h, r[3], r[4])
end
Parchment.SliceFor = sliceFor

local function assign(object: Instance, props)
	if props then
		for key, value in props do
			(object :: any)[key] = value
		end
	end
	return object
end

-- Ink text in the serif face. opts: size, color, align ("Left" | "Center" |
-- "Right"), scaled (shrink to fit, down to minSize), wrap, z.
function Parchment.Text(text: string, r, parent: Instance, opts): TextLabel
	opts = opts or {}
	local size = opts.size or 24
	local position, extent = rect(r)
	local label = Widgets.Text({ font = SERIF, textSize = size, color = opts.color or "ink" }, {
		Name = opts.name or "Text",
		Text = text,
		Position = position,
		Size = extent,
		TextStrokeTransparency = 1,
		TextXAlignment = (Enum.TextXAlignment :: any)[opts.align or "Left"],
		TextWrapped = opts.wrap == true,
		TextTruncate = if opts.wrap then Enum.TextTruncate.None else Enum.TextTruncate.AtEnd,
		ZIndex = opts.z or 4,
	}, parent)
	if opts.scaled then
		label.TextScaled = true
		Widgets.Make("UITextSizeConstraint", { MaxTextSize = size, MinTextSize = opts.minSize or 12 }, label)
	end
	return label
end

-- A thin ruled line (row separators, header underlines).
function Parchment.Rule(r, parent: Instance, colorKey: string?, z: number?): Frame
	local position, extent = rect(r)
	return Widgets.Make("Frame", {
		Name = "Rule",
		BackgroundColor3 = Layout.Color(colorKey or "line"),
		BorderSizePixel = 0,
		Position = position,
		Size = extent,
		ZIndex = z or 3,
	}, parent) :: Frame
end

-- A section header: the small diamond mark, capital ink text and a rule under it.
-- `r` spans the whole header from the mark to the rule's right end; the rule
-- starts at `ruleX` when given (clear of a column divider beside the mark).
function Parchment.Header(text: string, r, parent: Instance, ruleX: number?): TextLabel
	local x, y, w, h = r[1], r[2], r[3], r[4]
	Widgets.Sprite("pm_glyph_diamond", {
		Name = "Mark",
		Position = UDim2.fromOffset(x, y + h / 2 - 15),
		Size = UDim2.fromOffset(26, 28),
		ImageColor3 = Layout.Color("headerRule"),
		ZIndex = 4,
	}, parent)
	local label = Parchment.Text(string.upper(text), { x + 41, y, w - 41, h }, parent, { size = 29, name = "Header" })
	local from = ruleX or x
	Parchment.Rule({ from, y + h + 2, x + w - from, 2 }, parent, "headerRule")
	return label
end

-- A divider: two ruled lines with the mountain mark between them, centred in `r`.
function Parchment.Divider(r, parent: Instance, colorKey: string?)
	local color = colorKey or "headerRule"
	local x, y, w, h = r[1], r[2], r[3], r[4]
	local markW, markH, gap = 44, 27, 14
	local mid = x + w / 2
	local lineY = y + h / 2 - 1.5
	local left = Parchment.Rule({ x, lineY, w / 2 - markW / 2 - gap, 3 }, parent, color, 4)
	local right = Parchment.Rule({ mid + markW / 2 + gap, lineY, w / 2 - markW / 2 - gap, 3 }, parent, color, 4)
	for _, line in { left, right } do
		Widgets.Make("UICorner", { CornerRadius = UDim.new(0.5, 0) }, line)
	end
	Widgets.Sprite("pm_glyph_mountain", {
		Name = "Mark",
		AnchorPoint = Vector2.new(0.5, 0.5),
		Position = UDim2.fromOffset(mid, y + h / 2 - 2),
		Size = UDim2.fromOffset(markW, markH),
		ImageColor3 = Layout.Color(color),
		ZIndex = 4,
	}, parent)
end

-- A transparent button over `holder` that tints `art` for hover and press.
-- Returns the button and a function that sets whether it is enabled.
local function pressable(holder: GuiObject, art: GuiObject?, onPress, pad: number?)
	pad = pad or 0
	local button = Widgets.Make("TextButton", {
		Name = "Press",
		Text = "",
		AutoButtonColor = false,
		BackgroundTransparency = 1,
		Position = UDim2.fromOffset(-pad, -pad),
		Size = UDim2.new(1, pad * 2, 1, pad * 2),
		ZIndex = holder.ZIndex + 3,
	}, holder) :: TextButton
	local enabled = true
	local hovering = false
	-- A stand-in Frame (art not uploaded yet) darkens its own fill instead.
	local baseFill = if art and art:IsA("Frame") then art.BackgroundColor3 else nil
	local function tint(color: Color3)
		if art == nil then
			return
		end
		if baseFill then
			(art :: Frame).BackgroundColor3 =
				Color3.new(baseFill.R * color.R, baseFill.G * color.G, baseFill.B * color.B)
		elseif art:IsA("ImageLabel") then
			(art :: ImageLabel).ImageColor3 = color
		else
			for _, child in art:GetChildren() do
				if child:IsA("ImageLabel") then
					child.ImageColor3 = color
				end
			end
		end
	end
	local function rest()
		tint(if not enabled then Parchment.DISABLED elseif hovering then Parchment.HOVER else Color3.new(1, 1, 1))
	end
	local function focus(on: boolean)
		hovering = on
		rest()
	end
	button.MouseEnter:Connect(function()
		focus(true)
	end)
	button.MouseLeave:Connect(function()
		focus(false)
	end)
	button.SelectionGained:Connect(function()
		focus(true)
	end)
	button.SelectionLost:Connect(function()
		focus(false)
	end)
	button.MouseButton1Down:Connect(function()
		if enabled then
			tint(Parchment.PRESSED)
		end
	end)
	button.InputEnded:Connect(function(input: InputObject)
		-- Touch has no hover: a lifted finger returns the button to rest.
		if input.UserInputType == Enum.UserInputType.Touch then
			hovering = false
		end
		rest()
	end)
	button.Activated:Connect(function()
		if enabled then
			onPress()
		end
	end)
	return button,
		function(on: boolean)
			enabled = on
			-- A disabled control is skipped by gamepad selection.
			button.Selectable = on
			rest()
		end
end
Parchment.Pressable = pressable

-- A sprite button at `r`. opts: label (centred text), color, size, pad (extra
-- touch room), z. Returns {holder, art, button, label, SetEnabled}.
function Parchment.Button(sprite: string, r, parent: Instance, onPress, opts)
	opts = opts or {}
	local position, extent = rect(r)
	local holder = Widgets.Make("Frame", {
		Name = opts.name or sprite,
		BackgroundTransparency = 1,
		Position = position,
		Size = extent,
		ZIndex = opts.z or 4,
	}, parent) :: Frame
	local art = Widgets.Sprite(
		sprite,
		{ Name = "Art", Size = UDim2.fromScale(1, 1), ZIndex = holder.ZIndex },
		holder,
		sliceFor(sprite, r)
	)
	local label = nil
	if opts.label then
		-- Clear of the art's sliced corners, which scale with the button's height.
		local inset = opts.inset or math.max(12, r[4] * 0.4)
		label = Parchment.Text(opts.label, { inset, 0, r[3] - inset * 2, r[4] }, holder, {
			size = opts.size or 24,
			color = opts.color or "ink",
			align = "Center",
			scaled = true,
			z = holder.ZIndex + 1,
		})
	end
	local button, setEnabled = pressable(holder, art, onPress, opts.pad)
	return { holder = holder, art = art, button = button, label = label, SetEnabled = setEnabled }
end

-- A tab in the window's left column: leather when selected, paper otherwise,
-- with a white glyph tinted to match and a label. Returns {holder, SetSelected}.
function Parchment.Tab(r, parent: Instance, label: string, glyph: string, onPress)
	local position, extent = rect(r)
	local holder = Widgets.Make("Frame", {
		Name = label,
		BackgroundTransparency = 1,
		Position = position,
		Size = extent,
		ZIndex = 4,
	}, parent) :: Frame
	local paper = Widgets.Sprite("pm_tab_paper", { Name = "Paper", Size = UDim2.fromScale(1, 1), ZIndex = 4 }, holder)
	-- The leather plate's art runs a few pixels larger than the paper one.
	local leather = Widgets.Sprite("pm_tab_leather", {
		Name = "Leather",
		Position = UDim2.fromOffset(-2, -4),
		Size = UDim2.new(1, 4, 1, 4),
		ZIndex = 4,
		Visible = false,
	}, holder)
	local mark = UiAssets.sprite(glyph)
	local w, h = if mark then mark.w else 56, if mark then mark.h else 56
	local icon = Widgets.Sprite(glyph, {
		Name = "Glyph",
		AnchorPoint = Vector2.new(0.5, 0.5),
		Position = UDim2.fromOffset(63, r[4] / 2),
		Size = UDim2.fromOffset(w, h),
		ZIndex = 5,
	}, holder)
	local text = Parchment.Text(label, { 110, 0, r[3] - 150, r[4] }, holder, { size = 25, scaled = true, z = 5 })
	local selected = false
	local function show()
		paper.Visible = not selected
		leather.Visible = selected
		local color = Layout.Color(if selected then "cream" else "ink")
		text.TextColor3 = color
		if icon:IsA("ImageLabel") then
			(icon :: ImageLabel).ImageColor3 = color
		end
	end
	local button = pressable(holder, nil, onPress)
	button.MouseEnter:Connect(function()
		if not selected and paper:IsA("ImageLabel") then
			(paper :: ImageLabel).ImageColor3 = Parchment.HOVER
		end
	end)
	button.MouseLeave:Connect(function()
		if paper:IsA("ImageLabel") then
			(paper :: ImageLabel).ImageColor3 = Color3.new(1, 1, 1)
		end
	end)
	show()
	return {
		holder = holder,
		button = button,
		SetSelected = function(on: boolean)
			selected = on
			show()
		end,
	}
end

local sliders = 0

-- A horizontal slider: a dark rounded track, a gold fill and the brass knob.
-- `r` is the track. Dragging (mouse or touch) or clicking the track calls
-- onChange(value) with a value snapped to `step`. Returns {Set, holder}.
function Parchment.Slider(r, parent: Instance, min: number, max: number, step: number, onChange)
	local position, extent = rect(r)
	local holder = Widgets.Make("Frame", {
		Name = "Slider",
		BackgroundTransparency = 1,
		Position = position,
		Size = extent,
		ZIndex = 4,
	}, parent) :: Frame
	local radius = UDim.new(0.5, 0)
	local track = Widgets.Make("Frame", {
		Name = "Track",
		BackgroundColor3 = Layout.Color("sliderTrack"),
		BorderSizePixel = 0,
		Size = UDim2.fromScale(1, 1),
		ZIndex = 4,
	}, holder)
	Widgets.Make("UICorner", { CornerRadius = radius }, track)
	Widgets.Make("UIStroke", { Color = Layout.Color("paperEdge"), Thickness = 1.5 }, track)
	local fill = Widgets.Fill("sliderFill", { Size = UDim2.fromScale(0.5, 1), ZIndex = 5 }, holder)
	local knobSize = r[4] * 1.9
	local knob = Widgets.Sprite("pm_slider_knob", {
		Name = "Knob",
		AnchorPoint = Vector2.new(0.5, 0.5),
		Position = UDim2.fromScale(0.5, 0.5),
		Size = UDim2.fromOffset(knobSize, knobSize),
		ZIndex = 6,
	}, holder)
	local value = min
	-- The knob centre travels between the track's rounded ends.
	local inset = r[4] / 2
	local function place(fraction: number)
		local x = inset + (r[3] - inset * 2) * fraction
		knob.Position = UDim2.new(0, x, 0.5, 0)
		fill.Size = UDim2.new(0, math.max(r[4], x + inset * 0.5), 1, 0)
	end
	local function set(v: number)
		value = math.clamp(v, min, max)
		place(if max > min then (value - min) / (max - min) else 0)
	end
	-- The drag band reaches well above and below the thin track, for fingers.
	local band = math.max(knobSize, 56)
	local hit = Widgets.Make("TextButton", {
		Name = "Drag",
		Text = "",
		AutoButtonColor = false,
		BackgroundTransparency = 1,
		Position = UDim2.fromOffset(-knobSize / 2, -band / 2 + r[4] / 2),
		Size = UDim2.new(1, knobSize, 0, band),
		ZIndex = 7,
	}, holder) :: TextButton
	local dragging: InputObject? = nil
	local function from(screenX: number)
		local left = track.AbsolutePosition.X
		local width = track.AbsoluteSize.X
		if width <= 0 then
			return
		end
		local scale = width / r[3]
		local fraction = math.clamp((screenX - left - inset * scale) / (width - inset * 2 * scale), 0, 1)
		local raw = min + (max - min) * fraction
		local snapped = math.clamp(math.round(raw / step) * step, min, max)
		snapped = math.round(snapped * 1000) / 1000
		if snapped ~= value then
			set(snapped)
			onChange(snapped)
		end
	end
	hit.InputBegan:Connect(function(input: InputObject)
		local kind = input.UserInputType
		if kind == Enum.UserInputType.MouseButton1 or kind == Enum.UserInputType.Touch then
			dragging = input
			from(input.Position.X)
		end
	end)
	UserInputService.InputChanged:Connect(function(input: InputObject)
		if dragging == nil then
			return
		end
		if
			input.UserInputType == Enum.UserInputType.MouseMovement
			or (input.UserInputType == Enum.UserInputType.Touch and input == dragging)
		then
			from(input.Position.X)
		end
	end)
	UserInputService.InputEnded:Connect(function(input: InputObject)
		if dragging and (input == dragging or input.UserInputType == Enum.UserInputType.MouseButton1) then
			dragging = nil
		end
	end)
	-- Gamepad: while the slider is selected, left and right step the value. They
	-- are bound above the selection navigation and sunk, so focus stays put; up
	-- and down still move between controls.
	sliders += 1
	local stepAction = "FlintbornSliderStep" .. sliders
	local function nudge(delta: number)
		local nextValue = math.round(math.clamp(value + delta, min, max) * 1000) / 1000
		if nextValue ~= value then
			set(nextValue)
			onChange(nextValue)
		end
	end
	-- The stick steps once per push (it must come back near the middle before
	-- the next), and left/right navigation points back at the slider itself.
	local stickLatched = false
	local function onStep(_, state, input)
		local key = input.KeyCode
		if key == Enum.KeyCode.Thumbstick1 then
			local x = input.Position.X
			if math.abs(x) < 0.3 then
				stickLatched = false
			elseif math.abs(x) > 0.6 and not stickLatched then
				stickLatched = true
				nudge(if x > 0 then step else -step)
			end
			-- Up and down still move between controls.
			return if math.abs(input.Position.Y) > math.abs(x)
				then Enum.ContextActionResult.Pass
				else Enum.ContextActionResult.Sink
		end
		if state == Enum.UserInputState.Begin then
			if key == Enum.KeyCode.DPadRight or key == Enum.KeyCode.Right then
				nudge(step)
			elseif key == Enum.KeyCode.DPadLeft or key == Enum.KeyCode.Left then
				nudge(-step)
			end
		end
		return Enum.ContextActionResult.Sink
	end
	hit.SelectionGained:Connect(function()
		knob.Size = UDim2.fromOffset(knobSize * 1.1, knobSize * 1.1)
		hit.NextSelectionLeft = hit
		hit.NextSelectionRight = hit
		ContextActionService:BindActionAtPriority(
			stepAction,
			onStep,
			false,
			Enum.ContextActionPriority.High.Value + 50,
			Enum.KeyCode.DPadLeft,
			Enum.KeyCode.DPadRight,
			Enum.KeyCode.Left,
			Enum.KeyCode.Right,
			Enum.KeyCode.Thumbstick1
		)
	end)
	hit.SelectionLost:Connect(function()
		knob.Size = UDim2.fromOffset(knobSize, knobSize)
		hit.NextSelectionLeft = nil
		hit.NextSelectionRight = nil
		stickLatched = false
		ContextActionService:UnbindAction(stepAction)
	end)
	set(min)
	return { holder = holder, button = hit, Set = set }
end

-- A checkbox (ticked or empty art) with its label to the right. `r` covers the
-- box and label together, which is the whole touch area. Returns {Set}.
function Parchment.Checkbox(r, parent: Instance, label: string, onToggle)
	local position, extent = rect(r)
	local holder = Widgets.Make("Frame", {
		Name = label,
		BackgroundTransparency = 1,
		Position = position,
		Size = extent,
		ZIndex = 4,
	}, parent) :: Frame
	local box = r[4]
	local function art(name: string): GuiObject
		local sprite = UiAssets.sprite(name)
		local w, h = if sprite then sprite.w else 54, if sprite then sprite.h else 54
		local k = math.min(1, box / math.max(w, h))
		return Widgets.Sprite(name, {
			Name = name,
			AnchorPoint = Vector2.new(0.5, 0.5),
			Position = UDim2.fromOffset(box / 2, r[4] / 2),
			Size = UDim2.fromOffset(w * k, h * k),
			ZIndex = 5,
		}, holder)
	end
	local on = art("pm_check_on")
	local off = art("pm_check_off")
	Parchment.Text(label, { box + 26, 0, r[3] - box - 26, r[4] }, holder, { size = 20.5, scaled = true, z = 5 })
	local checked = false
	local function set(value: boolean)
		checked = value
		on.Visible = value
		off.Visible = not value
	end
	local button = pressable(holder, nil, function()
		set(not checked)
		onToggle(checked)
	end, 6)
	set(false)
	return { holder = holder, button = button, Set = set }
end

-- A dropdown: the paper box with its arrow, the chosen option's name, and a list
-- of options that opens on press (above the box when `openUp`). Returns {Set, Close}.
-- `layer` (optional) is the page holding the dropdown: it rises with the
-- dropdown while the list is open, so the list beats everything on the window.
function Parchment.Dropdown(r, parent: Instance, options: { string }, onSelect, openUp: boolean?, layer: GuiObject?)
	local position, extent = rect(r)
	local holder = Widgets.Make("Frame", {
		Name = "Dropdown",
		BackgroundTransparency = 1,
		Position = position,
		Size = extent,
		ZIndex = 4,
	}, parent) :: Frame
	local art = Widgets.Sprite(
		"pm_dropdown",
		{ Name = "Art", Size = UDim2.fromScale(1, 1), ZIndex = 4 },
		holder,
		sliceFor("pm_dropdown", r)
	)
	local text = Parchment.Text("", { 30, 0, r[3] - 100, r[4] }, holder, { size = 25, z = 5 })
	-- While open, the whole dropdown rises above its neighbours (the list must
	-- draw and take presses over them), and a press anywhere else closes it.
	local catcher = Widgets.Make("TextButton", {
		Name = "Outside",
		Text = "",
		AutoButtonColor = false,
		BackgroundTransparency = 1,
		Position = UDim2.fromOffset(-4000, -4000),
		Size = UDim2.new(1, 8000, 1, 8000),
		Selectable = false,
		Visible = false,
		ZIndex = 19,
	}, holder) :: TextButton
	local rowHeight = 48
	local listHeight = rowHeight * #options + 12
	local list = Widgets.Make("Frame", {
		Name = "Options",
		BackgroundColor3 = Layout.Color("paper"),
		BorderSizePixel = 0,
		Position = if openUp then UDim2.fromOffset(6, -listHeight - 4) else UDim2.fromOffset(6, r[4] + 4),
		Size = UDim2.fromOffset(r[3] - 12, listHeight),
		Visible = false,
		ZIndex = 20,
	}, holder) :: Frame
	Widgets.Make("UICorner", { CornerRadius = UDim.new(0, 8) }, list)
	Widgets.Make("UIStroke", { Color = Layout.Color("paperEdge"), Thickness = 2 }, list)
	local layerZ = if layer then layer.ZIndex else nil
	local function open(on: boolean)
		list.Visible = on
		catcher.Visible = on
		holder.ZIndex = if on then 15 else 4
		if layer and layerZ then
			layer.ZIndex = if on then 30 else layerZ
		end
	end
	catcher.Activated:Connect(function()
		open(false)
	end)
	local chosen = options[1]
	local rows = {}
	local function set(value: string)
		chosen = value
		text.Text = value
		for name, row in rows do
			row.BackgroundTransparency = if name == value then 0.75 else 1
		end
	end
	for index, option in options do
		local row = Widgets.Make("TextButton", {
			Name = option,
			Text = "",
			AutoButtonColor = false,
			BackgroundColor3 = Layout.Color("leather"),
			BackgroundTransparency = 1,
			BorderSizePixel = 0,
			Position = UDim2.fromOffset(6, 6 + (index - 1) * rowHeight),
			Size = UDim2.new(1, -12, 0, rowHeight),
			ZIndex = 21,
		}, list) :: TextButton
		Widgets.Make("UICorner", { CornerRadius = UDim.new(0, 6) }, row)
		Parchment.Text(option, { 18, 0, r[3] - 60, rowHeight }, row, { size = 24, z = 22 })
		rows[option] = row
		row.MouseEnter:Connect(function()
			row.BackgroundTransparency = 0.85
		end)
		row.MouseLeave:Connect(function()
			row.BackgroundTransparency = if option == chosen then 0.75 else 1
		end)
		row.Activated:Connect(function()
			open(false)
			if option ~= chosen then
				set(option)
				onSelect(option)
			end
		end)
	end
	local button = pressable(holder, art, function()
		open(not list.Visible)
	end)
	set(chosen)
	return {
		holder = holder,
		button = button,
		Set = set,
		Close = function()
			open(false)
		end,
		IsOpen = function(): boolean
			return list.Visible
		end,
	}
end

-- A keycap's width for its text: single keys square-ish, words wider.
function Parchment.KeyWidth(text: string): number
	local widths = { 60, 76, 94, 106, 116 }
	local n = utf8.len(text) or #text
	return widths[n] or (116 + (n - 5) * 13)
end

-- A keycap with `text` at `r`; pressable when `onPress` is given. Returns
-- {holder, label, SetText, SetEnabled}.
function Parchment.Keycap(text: string, r, parent: Instance, onPress)
	local position, extent = rect(r)
	local holder = Widgets.Make("Frame", {
		Name = "Key",
		BackgroundTransparency = 1,
		Position = position,
		Size = extent,
		ZIndex = 4,
	}, parent) :: Frame
	-- The cap art has a few transparent pixels round it: drawn that much larger so
	-- the visible cap fills the box.
	local art = Widgets.Sprite("pm_keycap", {
		Name = "Art",
		Position = UDim2.fromOffset(-3, -3),
		Size = UDim2.new(1, 6, 1, 6),
		ZIndex = 4,
	}, holder, 0.66)
	-- The label follows the cap when SetKeys widens it for a longer key name; it
	-- sits a little high, above the cap's thicker bottom edge.
	local label = Parchment.Text(text, { 6, 3, r[3] - 12, r[4] - 9 }, holder, {
		size = 21,
		align = "Center",
		scaled = true,
		minSize = 10,
		z = 5,
	})
	label.Size = UDim2.new(1, -12, 1, -9)
	local result = { holder = holder, art = art, label = label }
	function result.SetText(value: string)
		label.Text = value
	end
	if onPress then
		local button, setEnabled = pressable(holder, art, onPress, 4)
		result.button = button
		result.SetEnabled = setEnabled
	end
	return result
end

-- A full-screen menu: a dark veil over the game and a centred window sized to its
-- art (`size` = {w, h} reference pixels), scaled to fit the screen below the
-- Roblox top bar. The ScreenGui is marked "FitsItself", so Settings' UI-scale
-- pass leaves it alone (Fit applies the player's UI scale itself).
export type Screen = {
	gui: ScreenGui,
	veil: Frame,
	window: Frame,
	scale: UIScale,
	size: { number },
	Fit: (self: Screen, width: number, height: number, topInset: number?, userScale: number?) -> (),
	Watch: (self: Screen) -> (),
	SetOpen: (self: Screen, open: boolean) -> (),
	IsOpen: (self: Screen) -> boolean,
}

local ScreenMethods = {}
ScreenMethods.__index = ScreenMethods

function Parchment.Screen(name: string, size: { number }, displayOrder: number?, parent: Instance?): Screen
	local gui = Instance.new("ScreenGui")
	gui.Name = name
	gui.ResetOnSpawn = false
	gui.DisplayOrder = displayOrder or 20
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	gui.IgnoreGuiInset = true
	gui.Enabled = false
	gui:SetAttribute("FitsItself", true)
	pcall(function()
		gui.ScreenInsets = Enum.ScreenInsets.DeviceSafeInsets
	end)
	local veil = Widgets.Make("Frame", {
		Name = "Veil",
		Active = true,
		BackgroundColor3 = Layout.Color("veil"),
		BackgroundTransparency = 0.45,
		BorderSizePixel = 0,
		-- Past the safe-area edges too, so a notch's strip is veiled as well.
		Position = UDim2.fromOffset(-400, -400),
		Size = UDim2.new(1, 800, 1, 800),
		ZIndex = 0,
	}, gui) :: Frame
	local window = Widgets.Make("Frame", {
		Name = "Window",
		Active = true,
		AnchorPoint = Vector2.new(0.5, 0.5),
		BackgroundTransparency = 1,
		Position = UDim2.fromScale(0.5, 0.5),
		Size = UDim2.fromOffset(size[1], size[2]),
		ZIndex = 1,
	}, gui) :: Frame
	local scale = Widgets.Make("UIScale", { Scale = 1 }, window) :: UIScale
	gui.Parent = parent
	return setmetatable({ gui = gui, veil = veil, window = window, scale = scale, size = size }, ScreenMethods) :: any
end

-- Scales and centres the window on a `width` × `height` screen (screen pixels)
-- whose top `topInset` pixels belong to the Roblox top bar.
function ScreenMethods:Fit(width: number, height: number, topInset: number?, userScale: number?)
	local top = topInset or 0
	local margin = Parchment.MARGIN
	local roomW, roomH = width - margin * 2, height - top - margin * 2
	-- A window already shrunk to fit (phones) is never shrunk further by a UI
	-- scale below 1; that would only make its text unreadable.
	local fit = math.min(roomW / self.size[1], roomH / self.size[2])
	if fit < 1 then
		userScale = math.max(userScale or 1, 1)
	end
	local scale =
		HudModel.HudScale(roomW, roomH, self.size[1], self.size[2], Parchment.MIN_SCALE, Parchment.MAX_SCALE, userScale)
	self.scale.Scale = scale
	self.window.Position = UDim2.fromOffset(width / 2, top + margin + roomH / 2)
end

-- Keeps the window fitted as the screen, top bar or the player's UI scale change.
function ScreenMethods:Watch()
	local gui = self.gui
	local player = Players.LocalPlayer
	local function fit()
		local inset = 0
		local ok, value = pcall(function()
			return GuiService.TopbarInset.Max.Y
		end)
		inset = if ok and type(value) == "number" then value else GuiService:GetGuiInset().Y
		local size = gui.AbsoluteSize
		self:Fit(size.X, size.Y, math.max(0, inset - gui.AbsolutePosition.Y), player:GetAttribute("UiScale"))
	end
	gui:GetPropertyChangedSignal("AbsoluteSize"):Connect(fit)
	pcall(function()
		GuiService:GetPropertyChangedSignal("TopbarInset"):Connect(fit)
	end)
	player:GetAttributeChangedSignal("UiScale"):Connect(function()
		task.defer(fit)
	end)
	fit()
end

function ScreenMethods:SetOpen(open: boolean)
	self.gui.Enabled = open
end

function ScreenMethods:IsOpen(): boolean
	return self.gui.Enabled
end

return Parchment
