-- One small card above the lobby's Enter button, in the same rope-panel style:
-- the "take these into the run?" check before deploying (GDD Q155), the party
-- invite picker and the server menu. Show(spec) replaces whatever is open.
--
-- spec = {
--   title = "...",
--   lines = { "...", ... },                               -- plain text lines
--   rows = { { text, thumbnail?, action?, onPress? } },   -- e.g. players to invite
--   buttons = { { label, primary?, onPress } },           -- footer buttons
-- }

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TextService = game:GetService("TextService")

local Signal = require(ReplicatedStorage.Shared.Core.Signal)
local Layout = require(script.Parent.Layout)
local Widgets = require(script.Parent.Widgets)

local LobbyPopups = {}
LobbyPopups.__index = LobbyPopups

local WIDTH = 440
local PAD = 18
local TITLE_HEIGHT = 34
local LINE_HEIGHT = 22
local ROW_HEIGHT = 40
local BUTTON_HEIGHT = 40
local MAX_LIST_HEIGHT = 230
local LINE_SIZE = 15

-- The height a wrapped line of popup text needs at the list's width.
local function lineHeight(text: string): number
	local width = WIDTH - PAD * 2 - 8
	local ok, size = pcall(function()
		return TextService:GetTextSize(text, LINE_SIZE, Layout.Font("body"), Vector2.new(width, math.huge))
	end)
	return if ok then math.max(LINE_HEIGHT - 6, math.ceil(size.Y)) else LINE_HEIGHT - 6
end

local function pill(parent: Instance, label: string, primary: boolean, colors, props)
	local button = Widgets.Make("TextButton", {
		Name = label,
		Text = label,
		AutoButtonColor = true,
		BackgroundColor3 = Color3.fromHex(colors.row),
		Font = Layout.Font("bold"),
		TextSize = 16,
		TextColor3 = if primary then Layout.Color("gold") else Layout.Color("text"),
		ZIndex = 13,
	}, parent)
	for key, value in props do
		(button :: any)[key] = value
	end
	Widgets.Make("UICorner", { CornerRadius = UDim.new(0, 8) }, button)
	Widgets.Make("UIStroke", {
		ApplyStrokeMode = Enum.ApplyStrokeMode.Border,
		Color = if primary then Layout.Color("gold") else Color3.fromHex(colors.rowStroke),
		Thickness = if primary then 2 else 1.5,
	}, button)
	return button
end

function LobbyPopups.new(parent: Instance, layout)
	local self = setmetatable({ layout = layout, colors = layout.lobby.colors, Closed = Signal.new() }, LobbyPopups)
	self.card = nil
	self.parent = parent
	return self
end

function LobbyPopups:IsOpen(): boolean
	return self.card ~= nil
end

function LobbyPopups:Hide()
	if self.card then
		self.card:Destroy()
		self.card = nil
		self.Closed:Fire()
	end
end

function LobbyPopups:Show(spec)
	self:Hide()
	local lobby = self.layout.lobby
	local lines = spec.lines or {}
	local rows = spec.rows or {}
	local buttons = spec.buttons or {}
	local linesHeight = 0
	for _, line in lines do
		linesHeight += lineHeight(line) + 6
	end
	local listHeight = math.min(MAX_LIST_HEIGHT, linesHeight + #rows * (ROW_HEIGHT + 6))
	local height = PAD + TITLE_HEIGHT + 8 + listHeight + (if #buttons > 0 then 12 + BUTTON_HEIGHT else 0) + PAD
	local enter = lobby.enter
	local card = Widgets.Panel({
		fill = "slate",
		fillTransparency = 0.04,
		frame = "frame_panel_large_hollow",
		sliceScale = 0.4,
	}, {
		Name = "LobbyPopup",
		AnchorPoint = Vector2.new(0.5, 1),
		-- Just above the Enter button, centred on it.
		Position = UDim2.new(enter.pos[1], enter.pos[2], enter.pos[3], enter.pos[4] - enter.size[2] - 14),
		Size = UDim2.fromOffset(WIDTH, height),
		ZIndex = 10,
	}, self.parent)
	self.card = card
	for _, child in card:GetDescendants() do
		if child:IsA("GuiObject") then
			-- Fill 10, rope 12: the card's content sits above both.
			child.ZIndex += 9
		end
	end

	Widgets.Text({ font = "bold", textSize = 19, color = "gold" }, {
		Name = "Title",
		Text = spec.title,
		Position = UDim2.fromOffset(PAD, PAD),
		Size = UDim2.new(1, -PAD * 2 - 30, 0, TITLE_HEIGHT),
		ZIndex = 13,
	}, card)
	local close = Widgets.Make("Frame", {
		Name = "Close",
		BackgroundTransparency = 1,
		AnchorPoint = Vector2.new(1, 0),
		Position = UDim2.new(1, -PAD + 4, 0, PAD + 4),
		Size = UDim2.fromOffset(24, 24),
		ZIndex = 13,
	}, card)
	Widgets.Sprite("icon_x", { Size = UDim2.fromScale(1, 1), ZIndex = 14 }, close)
	local closeButton = Widgets.Make("TextButton", {
		Name = "CloseButton",
		Text = "",
		BackgroundTransparency = 1,
		Size = UDim2.fromScale(1, 1),
		ZIndex = 15,
	}, close)
	closeButton.Activated:Connect(function()
		self:Hide()
	end)

	local list = Widgets.Make("ScrollingFrame", {
		Name = "List",
		BackgroundTransparency = 1,
		BorderSizePixel = 0,
		Position = UDim2.fromOffset(PAD, PAD + TITLE_HEIGHT + 8),
		Size = UDim2.new(1, -PAD * 2, 0, listHeight),
		CanvasSize = UDim2.new(),
		AutomaticCanvasSize = Enum.AutomaticSize.Y,
		ScrollBarThickness = 6,
		ScrollBarImageColor3 = Color3.fromHex(self.colors.scroll),
		ZIndex = 13,
	}, card)
	Widgets.Make("UIListLayout", { Padding = UDim.new(0, 6), SortOrder = Enum.SortOrder.LayoutOrder }, list)
	local order = 0
	for _, line in lines do
		order += 1
		Widgets.Text({ font = "body", textSize = LINE_SIZE, color = "text" }, {
			Name = "Line" .. order,
			Text = line,
			LayoutOrder = order,
			Size = UDim2.new(1, -8, 0, lineHeight(line)),
			TextWrapped = true,
			TextTruncate = Enum.TextTruncate.None,
			ZIndex = 13,
		}, list)
	end
	for _, row in rows do
		order += 1
		local frame = Widgets.Make("Frame", {
			Name = "Row" .. order,
			BackgroundColor3 = Color3.fromHex(self.colors.row),
			BorderSizePixel = 0,
			LayoutOrder = order,
			Size = UDim2.new(1, -8, 0, ROW_HEIGHT),
			ZIndex = 13,
		}, list)
		Widgets.Make("UICorner", { CornerRadius = UDim.new(0, 8) }, frame)
		local x = 10
		if row.thumbnail ~= nil then
			local headshot = Widgets.Make("ImageLabel", {
				Name = "Headshot",
				BackgroundColor3 = Color3.new(0.12, 0.12, 0.12),
				Image = row.thumbnail,
				Position = UDim2.fromOffset(4, 4),
				Size = UDim2.fromOffset(ROW_HEIGHT - 8, ROW_HEIGHT - 8),
				ZIndex = 14,
			}, frame)
			Widgets.Make("UICorner", { CornerRadius = UDim.new(0, 6) }, headshot)
			x = ROW_HEIGHT + 4
		end
		Widgets.Text({ font = "bold", textSize = 15, color = "text" }, {
			Name = "Text",
			Text = row.text,
			Position = UDim2.fromOffset(x, 0),
			Size = UDim2.new(1, -x - 110, 1, 0),
			ZIndex = 14,
		}, frame)
		if row.action then
			pill(frame, row.action, true, self.colors, {
				AnchorPoint = Vector2.new(1, 0.5),
				Position = UDim2.new(1, -6, 0.5, 0),
				Size = UDim2.fromOffset(96, ROW_HEIGHT - 10),
				TextSize = 14,
				ZIndex = 14,
			}).Activated:Connect(row.onPress)
		end
	end

	local count = #buttons
	local gap = 12
	local width = (WIDTH - PAD * 2 - gap * (count - 1)) / math.max(1, count)
	for index, entry in buttons do
		pill(card, entry.label, entry.primary == true, self.colors, {
			Position = UDim2.new(0, PAD + (index - 1) * (width + gap), 1, -PAD - BUTTON_HEIGHT),
			Size = UDim2.fromOffset(width, BUTTON_HEIGHT),
		}).Activated:Connect(entry.onPress)
	end
	return card
end

return LobbyPopups
