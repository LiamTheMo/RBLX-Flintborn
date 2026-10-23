-- One-off important notices from the server (GDD §34.1): e.g. "Server crashed —
-- your items were recovered". Shown in the lobby and the world menu until
-- dismissed, with words, not colour alone.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Theme = require(script.Parent.Parent.Ui.Theme)

local NoticeController = {}

local player = Players.LocalPlayer
local make = Theme.Make
local ui = {}

local function build()
	local gui = make(
		"ScreenGui",
		{ Name = "Notice", ResetOnSpawn = false, DisplayOrder = 30 },
		player:WaitForChild("PlayerGui")
	)
	ui.card = make("TextButton", {
		AnchorPoint = Vector2.new(0.5, 0),
		Position = UDim2.new(0.5, 0, 0, 90),
		Size = UDim2.fromOffset(460, 0),
		AutomaticSize = Enum.AutomaticSize.Y,
		BackgroundColor3 = Color3.fromRGB(20, 50, 40),
		AutoButtonColor = false,
		Text = "",
		Visible = false,
	}, gui)
	make("UICorner", { CornerRadius = UDim.new(0, 8) }, ui.card)
	make("UIPadding", {
		PaddingTop = UDim.new(0, 10),
		PaddingBottom = UDim.new(0, 10),
		PaddingLeft = UDim.new(0, 12),
		PaddingRight = UDim.new(0, 12),
	}, ui.card)
	make("UIListLayout", { Padding = UDim.new(0, 4), SortOrder = Enum.SortOrder.LayoutOrder }, ui.card)
	ui.title = make("TextLabel", {
		Size = UDim2.new(1, 0, 0, 22),
		BackgroundTransparency = 1,
		TextXAlignment = Enum.TextXAlignment.Left,
		TextColor3 = Color3.fromRGB(200, 255, 220),
		Font = Theme.Fonts.Bold,
		TextSize = Theme.TextSize.Heading,
		LayoutOrder = 1,
	}, ui.card)
	ui.text = make("TextLabel", {
		Size = UDim2.new(1, 0, 0, 0),
		AutomaticSize = Enum.AutomaticSize.Y,
		BackgroundTransparency = 1,
		TextXAlignment = Enum.TextXAlignment.Left,
		TextWrapped = true,
		TextColor3 = Theme.Colors.Text,
		Font = Theme.Fonts.Body,
		TextSize = Theme.TextSize.Body,
		LayoutOrder = 2,
	}, ui.card)
	make("TextLabel", {
		Size = UDim2.new(1, 0, 0, 16),
		BackgroundTransparency = 1,
		TextXAlignment = Enum.TextXAlignment.Left,
		Text = "(tap to dismiss)",
		TextColor3 = Theme.Colors.Text,
		Font = Theme.Fonts.Body,
		TextSize = Theme.TextSize.Small,
		LayoutOrder = 3,
	}, ui.card)
	ui.card.Activated:Connect(function()
		ui.card.Visible = false
	end)
end

function NoticeController.Start()
	build()
	Remotes.Get("Notice").OnClientEvent:Connect(function(notice)
		ui.title.Text = notice.title
		ui.text.Text = notice.text
		ui.card.Visible = true
	end)
end

return NoticeController
