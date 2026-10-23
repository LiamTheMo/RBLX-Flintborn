-- Storage chests (GDD §6.1, Q39). Opening a chest shows its contents next to your
-- carried items: take from the chest or store from your inventory. Chests are
-- public, so anything stored can be taken by anyone who reaches it. World only.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Rarity = require(ReplicatedStorage.Shared.Items.Rarity)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local InventoryController = require(script.Parent.InventoryController)

local StorageController = {}

local player = Players.LocalPlayer
local ui = {}
local openChestId = nil
local contents = {}

local function make(className: string, props, parent)
	local instance = Instance.new(className)
	for key, value in props do
		instance[key] = value
	end
	instance.Parent = parent
	return instance
end

local function invoke(name: string, ...)
	local ok, success, reason = pcall(Remotes.Get(name).InvokeServer, Remotes.Get(name), ...)
	if not ok then
		return false, "Request failed"
	end
	return success, reason
end

local function clear(frame)
	for _, child in frame:GetChildren() do
		if not child:IsA("UIListLayout") then
			child:Destroy()
		end
	end
end

local function row(parent, text: string, color: Color3, onClick)
	local b = make("TextButton", {
		Text = text,
		Size = UDim2.new(1, 0, 0, 26),
		BackgroundColor3 = Color3.fromRGB(46, 38, 30),
		TextColor3 = color,
		TextXAlignment = Enum.TextXAlignment.Left,
		TextTruncate = Enum.TextTruncate.AtEnd,
		Font = Enum.Font.GothamMedium,
		TextSize = 13,
	}, parent)
	make("UICorner", { CornerRadius = UDim.new(0, 6) }, b)
	b.Activated:Connect(onClick)
end

local function label(entry): string
	return (entry.permanent and "★ " or "") .. entry.name .. (entry.quantity and (" ×" .. entry.quantity) or "")
end

local function render()
	if openChestId == nil then
		return
	end
	clear(ui.chest)
	clear(ui.mine)
	for _, entry in contents do
		row(ui.chest, "Take: " .. label(entry), Rarity.Colors[entry.rarity] or Color3.new(1, 1, 1), function()
			local ok, reason = invoke("ChestTake", openChestId, entry.index)
			if not ok then
				ui.status.Text = "Could not take that (" .. tostring(reason) .. ")"
			end
		end)
	end
	for _, slot in InventoryController.Snapshot.slots do
		if slot.area ~= "armor" then
			local def = ItemCatalog.Get(slot.catalogId)
			local entry =
				{ name = def and def.name or slot.catalogId, quantity = slot.quantity, permanent = slot.permanent }
			local color = Rarity.Colors[def and def.rarity or "Common"] or Color3.new(1, 1, 1)
			row(ui.mine, "Store: " .. label(entry), color, function()
				local ok, reason = invoke("ChestPut", openChestId, slot.area, slot.index)
				if not ok then
					ui.status.Text = "Could not store that (" .. tostring(reason) .. ")"
				end
			end)
		end
	end
	ui.panel.Visible = true
end

local function column(parent, x: number, title: string)
	make("TextLabel", {
		Text = title,
		Position = UDim2.new(x, 4, 0, 34),
		Size = UDim2.new(0.5, -8, 0, 20),
		BackgroundTransparency = 1,
		TextXAlignment = Enum.TextXAlignment.Left,
		TextColor3 = Color3.fromRGB(255, 220, 170),
		Font = Enum.Font.GothamBold,
		TextSize = 13,
	}, parent)
	local list = make("ScrollingFrame", {
		Position = UDim2.new(x, 4, 0, 58),
		Size = UDim2.new(0.5, -8, 1, -90),
		BackgroundTransparency = 1,
		AutomaticCanvasSize = Enum.AutomaticSize.Y,
		CanvasSize = UDim2.new(),
		ScrollBarThickness = 6,
	}, parent)
	make("UIListLayout", { Padding = UDim.new(0, 3) }, list)
	return list
end

local function build()
	local gui = make("ScreenGui", { Name = "Storage", ResetOnSpawn = false }, player:WaitForChild("PlayerGui"))
	-- Sized to the screen (up to 520×360), so the ✕ stays reachable on phones.
	ui.panel = make("Frame", {
		AnchorPoint = Vector2.new(0.5, 0.5),
		Position = UDim2.fromScale(0.5, 0.5),
		Size = UDim2.new(0.9, 0, 1, -24),
		BackgroundColor3 = Color3.fromRGB(24, 20, 17),
		Active = true,
		Visible = false,
	}, gui)
	make("UICorner", { CornerRadius = UDim.new(0, 8) }, ui.panel)
	make("UISizeConstraint", { MaxSize = Vector2.new(520, 360), MinSize = Vector2.new(300, 200) }, ui.panel)
	make("TextLabel", {
		Text = "Storage chest — public: anyone who reaches it can take items",
		Position = UDim2.fromOffset(10, 6),
		Size = UDim2.new(1, -50, 0, 24),
		BackgroundTransparency = 1,
		TextXAlignment = Enum.TextXAlignment.Left,
		TextTruncate = Enum.TextTruncate.AtEnd,
		TextColor3 = Color3.fromRGB(255, 214, 150),
		Font = Enum.Font.GothamBold,
		TextSize = 14,
	}, ui.panel)
	local close = make("TextButton", {
		Text = "✕",
		AnchorPoint = Vector2.new(1, 0),
		Position = UDim2.new(1, -6, 0, 6),
		Size = UDim2.fromOffset(28, 24),
		BackgroundColor3 = Color3.fromRGB(70, 56, 40),
		TextColor3 = Color3.fromRGB(245, 236, 222),
		Font = Enum.Font.GothamBold,
		TextSize = 14,
	}, ui.panel)
	close.Activated:Connect(function()
		ui.panel.Visible = false
		openChestId = nil
	end)
	ui.chest = column(ui.panel, 0, "In the chest")
	ui.mine = column(ui.panel, 0.5, "Carried")
	ui.status = make("TextLabel", {
		Text = "",
		AnchorPoint = Vector2.new(0, 1),
		Position = UDim2.new(0, 10, 1, -6),
		Size = UDim2.new(1, -20, 0, 22),
		BackgroundTransparency = 1,
		TextXAlignment = Enum.TextXAlignment.Left,
		TextColor3 = Color3.fromRGB(220, 210, 196),
		Font = Enum.Font.Gotham,
		TextSize = 13,
	}, ui.panel)
end

function StorageController.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	build()
	Remotes.Get("ChestOpened").OnClientEvent:Connect(function(chestId, entries)
		openChestId = chestId
		contents = entries
		ui.status.Text = ""
		render()
	end)
	InventoryController.Changed:Connect(function()
		if openChestId and ui.panel.Visible then
			render()
		end
	end)
	-- Walking away or ending the run closes the chest view.
	player:GetAttributeChangedSignal("SessionState"):Connect(function()
		ui.panel.Visible = false
		openChestId = nil
	end)
end

return StorageController
