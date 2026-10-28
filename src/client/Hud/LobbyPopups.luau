-- One small parchment card above the lobby's Enter button: the "take these into
-- the run?" check before deploying (GDD Q155), the party invite picker and the
-- server menu. Show(spec) replaces whatever is open. Styled from the "lobby.popup"
-- layout entry: the leather-cornered paper panel, leather (primary) and paper
-- buttons with their hover and pressed art.
--
-- spec = {
--   title = "...",
--   lines = { "...", ... },                               -- plain text lines
--   rows = { { text, thumbnail?, action?, onPress? } },   -- e.g. players to invite
--   buttons = { { label, primary?, onPress } },           -- footer buttons
-- }

local ContextActionService = game:GetService("ContextActionService")
local GuiService = game:GetService("GuiService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TextService = game:GetService("TextService")

local Signal = require(ReplicatedStorage.Shared.Core.Signal)
local UiAssets = require(ReplicatedStorage.Shared.UI.UiAssets)
local Layout = require(script.Parent.Layout)
local SpriteLoader = require(script.Parent.SpriteLoader)
local Widgets = require(script.Parent.Widgets)

local LobbyPopups = {}
LobbyPopups.__index = LobbyPopups

local TITLE_HEIGHT = 34
local ROW_HEIGHT = 52
local MAX_LIST_HEIGHT = 230
-- List room a card keeps before growing on a phone (about three lines).
local MIN_LIST_HEIGHT = 66
local CLOSE_SIZE = 44
local BASE_Z = 10
-- Below this screen scale (phones) the card is drawn larger, up to MAX_GROW.
local SMALL_SCREEN = 0.75
local MAX_GROW = 1.5
local CLOSE_ACTION = "FlintbornLobbyPopupClose"

-- The height a wrapped line of popup text needs at `width`. Measured with the
-- family's classic (regular) font without yielding; the bold face runs wider, so
-- the width is narrowed to leave it room.
local function lineHeight(entry, text: string, width: number): number
	local ok, size = pcall(function()
		return TextService:GetTextSize(
			text,
			entry.textSize,
			Layout.Font(entry.font),
			Vector2.new(width * 0.88, math.huge)
		)
	end)
	return if ok then math.max(entry.textSize, math.ceil(size.Y)) else entry.textSize + 4
end

-- A footer or row button on the leather (primary) or paper art, swapping to its
-- hover and pressed art when those are uploaded.
local function button(cfg, parent: Instance, label: string, primary: boolean, props, onPress)
	local base = if primary then "pm_button_leather" else "pm_button_parchment"
	local holder = Widgets.Make("Frame", { Name = label, BackgroundTransparency = 1 }, parent)
	for key, value in props do
		(holder :: any)[key] = value
	end
	local z = holder.ZIndex
	local face = Widgets.Sprite(base, {
		Name = "Art",
		Size = UDim2.fromScale(1, 1),
		ZIndex = z,
	}, holder, cfg.sliceScale)
	local text = Widgets.Text(cfg, {
		Name = "Label",
		Text = label,
		Size = UDim2.new(1, -24, 1, 0),
		Position = UDim2.fromOffset(12, 0),
		TextColor3 = Layout.Color(if primary then "cream" else "ink"),
		TextStrokeTransparency = 1,
		TextXAlignment = Enum.TextXAlignment.Center,
		TextScaled = true,
		ZIndex = z + 1,
	}, holder)
	Widgets.Make("UITextSizeConstraint", { MaxTextSize = cfg.textSize, MinTextSize = 11 }, text)
	local hit = Widgets.Make("TextButton", {
		Name = "Press",
		Text = "",
		AutoButtonColor = false,
		BackgroundTransparency = 1,
		Size = UDim2.fromScale(1, 1),
		ZIndex = z + 2,
	}, holder)
	local restColor = if face:IsA("Frame") then face.BackgroundColor3 else nil
	local function show(state: string?)
		local name = if state then base .. "_" .. state else base
		local id = UiAssets.image(name)
		if face:IsA("ImageLabel") then
			if id then
				-- The state art is a few pixels off the base size: its own slice centre.
				face.Image = id
				face.SliceCenter = UiAssets.sliceCenter(name) or face.SliceCenter
				face.ImageColor3 = Color3.new(1, 1, 1)
				SpriteLoader.Track(face)
			else
				-- No state art uploaded: darken the base art when pressed.
				face.ImageColor3 = if state == "pressed" then Color3.new(0.85, 0.85, 0.85) else Color3.new(1, 1, 1)
			end
		elseif restColor then
			-- Paper stand-in: lighten on hover, darken on press.
			local frame = face :: Frame
			frame.BackgroundColor3 = if state == "hover"
				then restColor:Lerp(Color3.new(1, 1, 1), 0.15)
				elseif state == "pressed" then restColor:Lerp(Color3.new(0, 0, 0), 0.15)
				else restColor
		end
	end
	hit.MouseEnter:Connect(function()
		show("hover")
	end)
	hit.SelectionGained:Connect(function()
		show("hover")
	end)
	hit.MouseLeave:Connect(function()
		show(nil)
	end)
	hit.SelectionLost:Connect(function()
		show(nil)
	end)
	hit.MouseButton1Down:Connect(function()
		show("pressed")
	end)
	hit.MouseButton1Up:Connect(function()
		show("hover")
	end)
	hit.InputEnded:Connect(function(input: InputObject)
		-- Touch has no hover: a lifted finger returns the button to rest.
		if input.UserInputType == Enum.UserInputType.Touch then
			show(nil)
		end
	end)
	hit.Activated:Connect(onPress)
	return holder, hit
end

function LobbyPopups.new(parent: Instance, layout)
	local self = setmetatable({ layout = layout, Closed = Signal.new() }, LobbyPopups)
	self.card = nil
	self.parent = parent
	-- The screen in reference pixels: its height, where the top bar ends, and the
	-- scale it is drawn at (LobbyHudController keeps these current).
	self.screenHeight = layout.reference.height
	self.topLimit = 0
	self.screenScale = 1
	return self
end

function LobbyPopups:SetScreen(height: number, topLimit: number, screenScale: number)
	self.screenHeight = height
	self.topLimit = topLimit
	self.screenScale = screenScale
end

function LobbyPopups:IsOpen(): boolean
	return self.card ~= nil
end

function LobbyPopups:Hide()
	if self.card then
		ContextActionService:UnbindAction(CLOSE_ACTION)
		local selected = GuiService.SelectedObject
		if selected and selected:IsDescendantOf(self.card) then
			-- Gamepad focus returns to where it was before the card opened.
			GuiService.SelectedObject = if self.returnTo and self.returnTo.Parent then self.returnTo else nil
		end
		self.card:Destroy()
		self.card = nil
		self.returnTo = nil
		self.Closed:Fire()
	end
end

function LobbyPopups:Show(spec)
	self:Hide()
	local lobby = self.layout.lobby
	local cfg = lobby.popup
	local pad = cfg.pad
	local width = cfg.width
	local inner = width - pad * 2
	local lines = spec.lines or {}
	local rows = spec.rows or {}
	local buttons = spec.buttons or {}
	local heights = {}
	local listHeight = 0
	for index, line in lines do
		heights[index] = lineHeight(cfg.line, line, inner - 8)
		listHeight += heights[index] + 6
	end
	listHeight = math.min(MAX_LIST_HEIGHT, listHeight + #rows * (ROW_HEIGHT + 6))
	local footer = if #buttons > 0 then 14 + cfg.button.height else 0
	local chrome = pad + TITLE_HEIGHT + 10 + footer + pad
	local enter = lobby.enter
	-- On phones the card is drawn larger so its text and buttons stay usable; it
	-- always ends below the top bar, scrolling its list when space runs out.
	local grow = if self.screenScale < SMALL_SCREEN then math.min(MAX_GROW, SMALL_SCREEN / self.screenScale) else 1
	local room = self.screenHeight + enter.pos[4] - enter.size[2] + 4 - (self.topLimit + 8)
	-- The list keeps room for about three lines before the card grows: on a
	-- very short screen what the card says matters more than its size.
	local wanted = math.min(listHeight, MIN_LIST_HEIGHT)
	grow = math.max(1, math.min(grow, room / (chrome + wanted)))
	listHeight = math.max(0, math.min(listHeight, room / grow - chrome))
	if (chrome + listHeight) * grow > room then
		grow = math.max(0.5, room / (chrome + listHeight))
	end
	local height = chrome + listHeight
	local card = Widgets.Make("Frame", {
		Name = "LobbyPopup",
		Active = true,
		BackgroundTransparency = 1,
		AnchorPoint = Vector2.new(0.5, 1),
		-- Just above the Enter button, centred on it.
		Position = UDim2.new(enter.pos[1], enter.pos[2], enter.pos[3], enter.pos[4] - enter.size[2] + 4),
		Size = UDim2.fromOffset(width, height),
		ZIndex = BASE_Z,
		-- Gamepad selection stays inside the card while it is open.
		SelectionGroup = true,
		SelectionBehaviorUp = Enum.SelectionBehavior.Stop,
		SelectionBehaviorDown = Enum.SelectionBehavior.Stop,
		SelectionBehaviorLeft = Enum.SelectionBehavior.Stop,
		SelectionBehaviorRight = Enum.SelectionBehavior.Stop,
	}, self.parent)
	Widgets.Make("UIScale", { Scale = grow }, card)
	self.card = card
	Widgets.Sprite(cfg.sprite, {
		Name = "Panel",
		Size = UDim2.fromScale(1, 1),
		ZIndex = BASE_Z,
	}, card, cfg.sliceScale)

	Widgets.Text(cfg.title, {
		Name = "Title",
		Text = spec.title,
		Position = UDim2.fromOffset(pad, pad - 4),
		Size = UDim2.new(1, -pad * 2 - CLOSE_SIZE - 6, 0, TITLE_HEIGHT),
		TextStrokeTransparency = 1,
		TextScaled = true,
		ZIndex = BASE_Z + 3,
	}, card)
	Widgets.Make(
		"UITextSizeConstraint",
		{ MaxTextSize = cfg.title.textSize, MinTextSize = 14 },
		card:FindFirstChild("Title")
	)
	local close = Widgets.Make("Frame", {
		Name = "Close",
		BackgroundTransparency = 1,
		AnchorPoint = Vector2.new(1, 0),
		Position = UDim2.new(1, -pad + 6, 0, pad - 4),
		Size = UDim2.fromOffset(CLOSE_SIZE, CLOSE_SIZE),
		ZIndex = BASE_Z + 3,
	}, card)
	Widgets.Sprite(cfg.close, { Size = UDim2.fromScale(1, 1), ZIndex = BASE_Z + 3 }, close)
	local closeButton = Widgets.Make("TextButton", {
		Name = "CloseButton",
		Text = "",
		BackgroundTransparency = 1,
		-- A touch area a little past the art, clear of the list below.
		Position = UDim2.fromOffset(-8, -8),
		Size = UDim2.new(1, 16, 1, 8),
		ZIndex = BASE_Z + 4,
	}, close)
	closeButton.Activated:Connect(function()
		self:Hide()
	end)

	local list = Widgets.Make("ScrollingFrame", {
		Name = "List",
		BackgroundTransparency = 1,
		BorderSizePixel = 0,
		Position = UDim2.fromOffset(pad, pad + TITLE_HEIGHT + 6),
		Size = UDim2.new(1, -pad * 2, 0, listHeight),
		CanvasSize = UDim2.new(),
		AutomaticCanvasSize = Enum.AutomaticSize.Y,
		ScrollBarThickness = 6,
		ScrollBarImageColor3 = Layout.Color("thumb"),
		ZIndex = BASE_Z + 3,
	}, card)
	Widgets.Make("UIListLayout", { Padding = UDim.new(0, 6), SortOrder = Enum.SortOrder.LayoutOrder }, list)
	local order = 0
	for index, line in lines do
		order += 1
		Widgets.Text(cfg.line, {
			Name = "Line" .. order,
			Text = line,
			LayoutOrder = order,
			Size = UDim2.new(1, -8, 0, heights[index]),
			TextStrokeTransparency = 1,
			TextWrapped = true,
			TextTruncate = Enum.TextTruncate.None,
			ZIndex = BASE_Z + 3,
		}, list)
	end
	for _, row in rows do
		order += 1
		local frame = Widgets.Make("Frame", {
			Name = "Row" .. order,
			BackgroundColor3 = Layout.Color("paper"),
			BorderSizePixel = 0,
			LayoutOrder = order,
			Size = UDim2.new(1, -8, 0, ROW_HEIGHT),
			ZIndex = BASE_Z + 3,
		}, list)
		Widgets.Make("UICorner", { CornerRadius = UDim.new(0, 8) }, frame)
		Widgets.Make("UIStroke", { Color = Layout.Color("line"), Thickness = 1.5 }, frame)
		local x = 12
		if row.thumbnail ~= nil then
			local headshot = Widgets.Make("ImageLabel", {
				Name = "Headshot",
				BackgroundColor3 = Layout.Color("photo"),
				Image = row.thumbnail,
				Position = UDim2.fromOffset(5, 5),
				Size = UDim2.fromOffset(ROW_HEIGHT - 10, ROW_HEIGHT - 10),
				ZIndex = BASE_Z + 4,
			}, frame)
			Widgets.Make("UICorner", { CornerRadius = UDim.new(0, 6) }, headshot)
			x = ROW_HEIGHT + 4
		end
		Widgets.Text(cfg.row, {
			Name = "Text",
			Text = row.text,
			Position = UDim2.fromOffset(x, 0),
			Size = UDim2.new(1, -x - 116, 1, 0),
			TextStrokeTransparency = 1,
			ZIndex = BASE_Z + 4,
		}, frame)
		if row.action then
			button(cfg.button, frame, row.action, true, {
				AnchorPoint = Vector2.new(1, 0.5),
				Position = UDim2.new(1, -4, 0.5, 0),
				Size = UDim2.fromOffset(108, ROW_HEIGHT - 6),
				ZIndex = BASE_Z + 4,
			}, row.onPress)
		end
	end

	local count = #buttons
	local gap = 12
	local buttonWidth = (inner - gap * (count - 1)) / math.max(1, count)
	local first = nil
	for index, entry in buttons do
		local _, press = button(cfg.button, card, entry.label, entry.primary == true, {
			Position = UDim2.new(0, pad + (index - 1) * (buttonWidth + gap), 1, -pad - cfg.button.height),
			Size = UDim2.fromOffset(buttonWidth, cfg.button.height),
			ZIndex = BASE_Z + 3,
		}, entry.onPress)
		first = first or press
	end

	-- Gamepad: B closes the card, and a player already navigating with the
	-- gamepad lands on its first button (or the close button).
	ContextActionService:BindAction(CLOSE_ACTION, function(_, state)
		if state == Enum.UserInputState.Begin then
			self:Hide()
		end
		return Enum.ContextActionResult.Sink
	end, false, Enum.KeyCode.ButtonB)
	local selected = GuiService.SelectedObject
	if selected ~= nil then
		self.returnTo = selected
		GuiService.SelectedObject = first or closeButton
	end
	return card
end

return LobbyPopups
