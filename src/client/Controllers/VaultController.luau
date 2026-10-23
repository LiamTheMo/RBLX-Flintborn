-- Lobby vault and lobby backpack (GDD §10.3, §25.2). G (or DPadRight) opens the
-- panel: click a backpack item to deposit it, a vault item to withdraw it, or a
-- material to withdraw 10. The latest extraction receipt shows on arrival.
-- Lobby place only.

local ContextActionService = game:GetService("ContextActionService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Rarity = require(ReplicatedStorage.Shared.Items.Rarity)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)

local VaultController = {}

VaultController.MATERIAL_STEP = 10

local player = Players.LocalPlayer
local ui = {}

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

local function itemText(item): string
	return (item.permanent and "★ " or "") .. item.name .. (item.quantity and (" ×" .. item.quantity) or "")
end

local refresh

local function act(name: string, ...)
	local ok, reason = invoke(name, ...)
	ui.status.Text = if ok then "Done." else ("Not possible: " .. tostring(reason))
	refresh()
end

function refresh()
	local view = invoke("VaultSnapshot")
	if type(view) ~= "table" then
		ui.status.Text = "Your data is still loading."
		return
	end
	clear(ui.backpack)
	clear(ui.items)
	clear(ui.materials)
	ui.backpackTitle.Text = ("Backpack: goes with you on Play (%d/%d) · click to vault"):format(
		#view.backpack,
		view.backpackCapacity
	)
	ui.itemsTitle.Text = ("Vault: safe forever (%d/%d) · click to withdraw"):format(#view.items, view.itemCapacity)
	for index, item in view.backpack do
		row(ui.backpack, itemText(item), Rarity.Colors[item.rarity] or Color3.new(1, 1, 1), function()
			act("VaultDeposit", index)
		end)
	end
	for index, item in view.items do
		row(ui.items, itemText(item), Rarity.Colors[item.rarity] or Color3.new(1, 1, 1), function()
			act("VaultWithdrawItem", index)
		end)
	end
	for _, material in view.materials do
		local text = ("%s ×%d — withdraw %d"):format(
			material.name,
			material.quantity,
			math.min(VaultController.MATERIAL_STEP, material.quantity)
		)
		row(ui.materials, text, Color3.fromRGB(230, 220, 200), function()
			act("VaultWithdrawMaterial", material.catalogId, math.min(VaultController.MATERIAL_STEP, material.quantity))
		end)
	end
end

local function column(parent, x: number, title: string)
	local label = make("TextLabel", {
		Text = title,
		Position = UDim2.new(x, 4, 0, 34),
		Size = UDim2.new(1 / 3, -8, 0, 20),
		BackgroundTransparency = 1,
		TextXAlignment = Enum.TextXAlignment.Left,
		TextTruncate = Enum.TextTruncate.AtEnd,
		TextColor3 = Color3.fromRGB(255, 220, 170),
		Font = Enum.Font.GothamBold,
		TextSize = 13,
	}, parent)
	local list = make("ScrollingFrame", {
		Position = UDim2.new(x, 4, 0, 58),
		Size = UDim2.new(1 / 3, -8, 1, -90),
		BackgroundTransparency = 1,
		AutomaticCanvasSize = Enum.AutomaticSize.Y,
		CanvasSize = UDim2.new(),
		ScrollBarThickness = 6,
	}, parent)
	make("UIListLayout", { Padding = UDim.new(0, 3) }, list)
	return label, list
end

local function build()
	local gui = make("ScreenGui", { Name = "Vault", ResetOnSpawn = false }, player:WaitForChild("PlayerGui"))
	ui.panel = make("Frame", {
		AnchorPoint = Vector2.new(0.5, 0.5),
		Position = UDim2.fromScale(0.45, 0.5),
		Size = UDim2.new(0.6, 0, 0, 420),
		BackgroundColor3 = Color3.fromRGB(24, 20, 17),
		Visible = false,
	}, gui)
	make("UICorner", { CornerRadius = UDim.new(0, 8) }, ui.panel)
	make("UISizeConstraint", { MaxSize = Vector2.new(820, 420), MinSize = Vector2.new(480, 300) }, ui.panel)
	make("TextLabel", {
		Text = "Secure Vault",
		Position = UDim2.fromOffset(10, 6),
		Size = UDim2.new(1, -50, 0, 24),
		BackgroundTransparency = 1,
		TextXAlignment = Enum.TextXAlignment.Left,
		TextColor3 = Color3.fromRGB(255, 214, 150),
		Font = Enum.Font.GothamBlack,
		TextSize = 18,
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
	end)
	ui.backpackTitle, ui.backpack = column(ui.panel, 0, "Lobby backpack")
	ui.itemsTitle, ui.items = column(ui.panel, 1 / 3, "Vault items")
	local _, materials = column(ui.panel, 2 / 3, "Vault materials — click to withdraw")
	ui.materials = materials
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

	ui.receipt = make("TextButton", {
		AnchorPoint = Vector2.new(0.5, 0),
		Position = UDim2.new(0.5, 0, 0, 16),
		Size = UDim2.fromOffset(460, 0),
		AutomaticSize = Enum.AutomaticSize.Y,
		BackgroundColor3 = Color3.fromRGB(16, 38, 30),
		BackgroundTransparency = 0.05,
		TextColor3 = Color3.fromRGB(210, 255, 226),
		TextWrapped = true,
		Font = Enum.Font.GothamMedium,
		TextSize = 14,
		Visible = false,
	}, gui)
	make("UICorner", { CornerRadius = UDim.new(0, 8) }, ui.receipt)
	make("UIPadding", { PaddingTop = UDim.new(0, 8), PaddingBottom = UDim.new(0, 8) }, ui.receipt)
	ui.receipt.Activated:Connect(function()
		ui.receipt.Visible = false
	end)
end

local function listOf(map): string
	local parts = {}
	for catalogId, quantity in map do
		local def = ItemCatalog.Get(catalogId)
		table.insert(parts, ("%s ×%d"):format(def and def.name or catalogId, quantity))
	end
	table.sort(parts)
	return if #parts > 0 then table.concat(parts, ", ") else "nothing"
end

local function showReceipt(receipt)
	local lines = {
		("Extracted at %s%s"):format(
			receipt.portal or "a portal",
			receipt.multiplier > 1 and " — Center bonus ×2 materials" or ""
		),
		"Banked to vault: " .. listOf(receipt.vaulted),
		"Lobby backpack: " .. listOf(receipt.toBackpack),
	}
	if (receipt.runGeneralXPEarned or 0) > 0 or (receipt.runMasteryXPEarned or 0) > 0 then
		-- Base XP was credited as it was earned; the Center bonus is the extra (§25.4.1).
		table.insert(
			lines,
			("Run XP (already credited): %d · mastery %d"):format(
				receipt.runGeneralXPEarned,
				receipt.runMasteryXPEarned
			)
		)
		if (receipt.centerBonusGeneralXP or 0) > 0 or (receipt.centerBonusMasteryXP or 0) > 0 then
			table.insert(
				lines,
				("Center bonus: +%d XP · +%d mastery XP"):format(
					receipt.centerBonusGeneralXP,
					receipt.centerBonusMasteryXP
				)
			)
		end
	end
	if next(receipt.deleted) then
		table.insert(lines, "Deleted (no room): " .. listOf(receipt.deleted))
	end
	table.insert(lines, "(click to dismiss)")
	ui.receipt.Text = table.concat(lines, "\n")
	ui.receipt.Visible = true
end

function VaultController.Start()
	if not PlaceConfig.IsLobby() then
		return
	end
	build()
	Remotes.Get("ExtractionReceipt").OnClientEvent:Connect(showReceipt)
	ContextActionService:BindAction("FlintbornVault", function(_, state)
		if state == Enum.UserInputState.Begin then
			ui.panel.Visible = not ui.panel.Visible
			if ui.panel.Visible then
				ui.status.Text = ""
				refresh()
			end
		end
		return Enum.ContextActionResult.Pass
	end, false, Enum.KeyCode.G, Enum.KeyCode.DPadRight)
end

return VaultController
