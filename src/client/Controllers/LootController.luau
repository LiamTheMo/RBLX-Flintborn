-- Body looting (GDD §29.2) and the death summary (GDD §25.4). Interacting with a
-- body opens its contents; take items one by one while in range. After your own
-- death, a summary separates what dropped from what you kept. World place only.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Rarity = require(ReplicatedStorage.Shared.Items.Rarity)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)

local LootController = {}

local player = Players.LocalPlayer
local ui = {}
local openBodyId = nil

local function make(className: string, props, parent)
	local instance = Instance.new(className)
	for key, value in props do
		instance[key] = value
	end
	instance.Parent = parent
	return instance
end

local function render(bodyId: string, entries)
	openBodyId = bodyId
	for _, child in ui.list:GetChildren() do
		if not child:IsA("UIListLayout") then
			child:Destroy()
		end
	end
	if #entries == 0 then
		make("TextLabel", {
			Text = "Nothing left.",
			Size = UDim2.new(1, 0, 0, 24),
			BackgroundTransparency = 1,
			TextColor3 = Color3.fromRGB(220, 210, 196),
			Font = Enum.Font.Gotham,
			TextSize = 14,
		}, ui.list)
	end
	for _, entry in entries do
		local text = entry.name .. (entry.quantity and (" ×" .. entry.quantity) or "") .. "  · " .. entry.rarity
		local b = make("TextButton", {
			Text = "Take: " .. text,
			Size = UDim2.new(1, 0, 0, 30),
			BackgroundColor3 = Color3.fromRGB(46, 38, 30),
			TextColor3 = Rarity.Colors[entry.rarity] or Color3.fromRGB(240, 232, 220),
			TextXAlignment = Enum.TextXAlignment.Left,
			Font = Enum.Font.GothamMedium,
			TextSize = 13,
		}, ui.list)
		make("UICorner", { CornerRadius = UDim.new(0, 6) }, b)
		b.Activated:Connect(function()
			local ok, success, reason = pcall(function()
				return Remotes.Get("CorpseTake"):InvokeServer(openBodyId, entry.index)
			end)
			if not ok or not success then
				ui.title.Text = "Could not take that (" .. tostring(reason) .. ")"
			end
		end)
	end
	ui.panel.Visible = true
end

local function build()
	local gui = make("ScreenGui", { Name = "Loot", ResetOnSpawn = false }, player:WaitForChild("PlayerGui"))
	-- Sized to the screen (up to 340×320), so the ✕ stays reachable on phones.
	ui.panel = make("Frame", {
		AnchorPoint = Vector2.new(0.5, 0.5),
		Position = UDim2.fromScale(0.5, 0.5),
		Size = UDim2.new(0.9, 0, 1, -24),
		BackgroundColor3 = Color3.fromRGB(24, 20, 17),
		Active = true,
		Visible = false,
	}, gui)
	make("UICorner", { CornerRadius = UDim.new(0, 8) }, ui.panel)
	make("UISizeConstraint", { MaxSize = Vector2.new(340, 320), MinSize = Vector2.new(260, 200) }, ui.panel)
	make(
		"UIPadding",
		{ PaddingTop = UDim.new(0, 8), PaddingLeft = UDim.new(0, 8), PaddingRight = UDim.new(0, 8) },
		ui.panel
	)
	ui.title = make("TextLabel", {
		Text = "Body",
		Size = UDim2.new(1, -40, 0, 24),
		BackgroundTransparency = 1,
		TextXAlignment = Enum.TextXAlignment.Left,
		TextColor3 = Color3.fromRGB(255, 220, 170),
		Font = Enum.Font.GothamBold,
		TextSize = 15,
	}, ui.panel)
	local close = make("TextButton", {
		Text = "✕",
		AnchorPoint = Vector2.new(1, 0),
		Position = UDim2.new(1, 0, 0, 0),
		Size = UDim2.fromOffset(28, 24),
		BackgroundColor3 = Color3.fromRGB(70, 56, 40),
		TextColor3 = Color3.fromRGB(245, 236, 222),
		Font = Enum.Font.GothamBold,
		TextSize = 14,
	}, ui.panel)
	close.Activated:Connect(function()
		ui.panel.Visible = false
		openBodyId = nil
	end)
	ui.list = make("ScrollingFrame", {
		Position = UDim2.fromOffset(0, 30),
		Size = UDim2.new(1, 0, 1, -38),
		BackgroundTransparency = 1,
		AutomaticCanvasSize = Enum.AutomaticSize.Y,
		CanvasSize = UDim2.new(),
		ScrollBarThickness = 6,
	}, ui.panel)
	make("UIListLayout", { Padding = UDim.new(0, 4) }, ui.list)

	ui.summary = make("TextLabel", {
		AnchorPoint = Vector2.new(0.5, 0.5),
		Position = UDim2.fromScale(0.5, 0.35),
		Size = UDim2.fromOffset(460, 110),
		BackgroundColor3 = Color3.fromRGB(30, 22, 20),
		BackgroundTransparency = 0.1,
		Active = true,
		TextColor3 = Color3.fromRGB(255, 236, 220),
		TextWrapped = true,
		Font = Enum.Font.GothamBold,
		TextSize = 16,
		Visible = false,
	}, gui)
	make("UICorner", { CornerRadius = UDim.new(0, 8) }, ui.summary)
end

function LootController.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	build()
	Remotes.Get("CorpseOpened").OnClientEvent:Connect(render)
	Remotes.Get("DeathSummary").OnClientEvent:Connect(function(summary)
		ui.summary.Text = ("You died.\n✕ Dropped and lootable: %d item(s) in your body (10 minutes)\n✓ Safe in vault: unchanged\n✓ Permanent: %d kept\nReturning to the lobby…"):format(
			summary.dropped or 0,
			summary.kept or 0
		)
		ui.summary.Visible = true
	end)
end

return LootController
