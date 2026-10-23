-- Small persistent indicator of the player's profile save state, driven by the
-- SaveStatus attribute the server sets. Uses words plus a symbol, never colour alone.

local Players = game:GetService("Players")

local SaveStatusController = {}

local STATUS_ATTRIBUTE = "SaveStatus"

local LABELS = {
	Loading = "… Loading data",
	Saved = "✓ Saved",
	Saving = "… Saving",
	Pending = "! Save pending",
	LeaseLost = "✕ Data in use on another server",
	Error = "✕ Data error",
}

local label

local function refresh()
	local status = Players.LocalPlayer:GetAttribute(STATUS_ATTRIBUTE)
	label.Text = LABELS[status] or ""
	label.Visible = status ~= nil
end

function SaveStatusController.Start()
	local player = Players.LocalPlayer
	local gui = Instance.new("ScreenGui")
	gui.Name = "SaveStatus"
	gui.ResetOnSpawn = false
	gui.IgnoreGuiInset = false
	gui.DisplayOrder = 10

	label = Instance.new("TextLabel")
	label.Name = "Status"
	-- Bottom-right above the settings button: the XP bar owns the bottom-left.
	label.AnchorPoint = Vector2.new(1, 1)
	label.Position = UDim2.new(1, -12, 1, -84)
	label.Size = UDim2.fromOffset(0, 24)
	label.AutomaticSize = Enum.AutomaticSize.X
	label.BackgroundTransparency = 0.4
	label.BackgroundColor3 = Color3.fromRGB(20, 18, 16)
	label.TextColor3 = Color3.fromRGB(240, 232, 220)
	label.TextXAlignment = Enum.TextXAlignment.Left
	label.Font = Enum.Font.GothamMedium
	label.TextSize = 14
	label.Parent = gui

	local padding = Instance.new("UIPadding")
	padding.PaddingLeft = UDim.new(0, 8)
	padding.PaddingRight = UDim.new(0, 8)
	padding.Parent = label

	gui.Parent = player:WaitForChild("PlayerGui")
	player:GetAttributeChangedSignal(STATUS_ATTRIBUTE):Connect(refresh)
	refresh()
end

return SaveStatusController
