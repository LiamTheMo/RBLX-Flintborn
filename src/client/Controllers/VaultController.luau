-- Lobby vault and lobby backpack (GDD §10.3, §25.2, §53). The Vault button on the
-- navigation bar opens the panel: click a backpack item to deposit it or a vault
-- item to withdraw it. A vault material withdraws the amount picked above the
-- materials list (1, 10, 100 or all) into the backpack, to deploy with it. A
-- material deposit the vault cannot hold in full asks first how much it would
-- delete (GDD §53). The latest extraction receipt shows on arrival. The Backpack key (Tab by default,
-- GDD §46) opens and closes the panel, as it opens the backpack in a run.
-- Lobby place only.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Rarity = require(ReplicatedStorage.Shared.Items.Rarity)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Theme = require(script.Parent.Parent.Ui.Theme)
local Reasons = require(script.Parent.Parent.Ui.Reasons)
local Binds = require(script.Parent.Parent.Ui.Binds)

local VaultController = {}

-- Amounts a click on a vault material withdraws; false means the whole stack.
VaultController.MATERIAL_STEPS = { 1, 10, 100, false }

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
	local ok, success, reason, detail = pcall(Remotes.Get(name).InvokeServer, Remotes.Get(name), ...)
	if not ok then
		return false, "Request failed"
	end
	return success, reason, detail
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
	if onClick then
		b.Activated:Connect(onClick)
	else
		b.AutoButtonColor = false
	end
end

local function itemText(item): string
	return (item.permanent and "★ " or "") .. item.name .. (item.quantity and (" ×" .. item.quantity) or "")
end

local refresh

-- The picked withdrawal amount (an entry of MATERIAL_STEPS; false = all).
local materialStep: number | boolean = 10

local function act(name: string, ...)
	local ok, reason = invoke(name, ...)
	ui.status.Text = if ok then "Done." else ("Not possible: " .. Reasons.Text(reason))
	refresh()
end

-- The deposit waiting for "deposit anyway": {index, catalogId, quantity}.
local pendingDeposit = nil

local function hideConfirm()
	pendingDeposit = nil
	ui.confirm.Visible = false
end

-- Deposits a backpack slot. When the vault cannot hold all of a material, asks
-- first how much would be deleted.
local function deposit(index: number, item)
	hideConfirm()
	local ok, reason, lost = invoke("VaultDeposit", index)
	if not ok and reason == "VaultWouldOverflow" and type(lost) == "number" then
		pendingDeposit = { index = index, catalogId = item.catalogId, quantity = item.quantity }
		ui.confirmText.Text = ("Your vault is nearly full: %d %s would be deleted. Deposit anyway?"):format(
			lost,
			item.name
		)
		ui.confirm.Visible = true
		ui.status.Text = ""
		return
	end
	ui.status.Text = if ok then "Done." else ("Not possible: " .. Reasons.Text(reason))
	refresh()
end

-- "Deposit anyway": only while that slot still holds the same stack.
local function confirmDeposit()
	local pending = pendingDeposit
	hideConfirm()
	local view = pending and invoke("VaultSnapshot")
	local item = type(view) == "table" and view.backpack[pending.index]
	if item == nil or item.catalogId ~= pending.catalogId or item.quantity ~= pending.quantity then
		ui.status.Text = "Your backpack changed; nothing was deposited."
		refresh()
		return
	end
	act("VaultDeposit", pending.index, true)
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
			deposit(index, item)
		end)
	end
	for index, item in view.items do
		row(ui.items, itemText(item), Rarity.Colors[item.rarity] or Color3.new(1, 1, 1), function()
			act("VaultWithdrawItem", index)
		end)
	end
	-- Withdrawn materials join the backpack and deploy with it (GDD §53).
	for _, material in view.materials do
		local amount = if materialStep then math.min(materialStep, material.quantity) else material.quantity
		row(
			ui.materials,
			("%s ×%d — take %d"):format(material.name, material.quantity, amount),
			Color3.fromRGB(230, 220, 200),
			function()
				act("VaultWithdrawMaterial", material.catalogId, amount)
			end
		)
	end
	for _, lost in view.overflow or {} do
		row(
			ui.materials,
			("Vault full — deleted %s ×%d"):format(lost.name, lost.quantity),
			Color3.fromRGB(235, 120, 100),
			nil
		)
	end
end

local function column(parent, x: number, title: string, listTop: number?)
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
	local top = listTop or 58
	local list = make("ScrollingFrame", {
		Position = UDim2.new(x, 4, 0, top),
		Size = UDim2.new(1 / 3, -8, 1, -(top + 32)),
		BackgroundTransparency = 1,
		AutomaticCanvasSize = Enum.AutomaticSize.Y,
		CanvasSize = UDim2.new(),
		ScrollBarThickness = 6,
	}, parent)
	make("UIListLayout", { Padding = UDim.new(0, 3) }, list)
	return label, list
end

-- The 1 / 10 / 100 / All picker above the vault materials list.
local function buildSteps(parent, x: number, y: number)
	local bar = make("Frame", {
		Position = UDim2.new(x, 4, 0, y),
		Size = UDim2.new(1 / 3, -8, 0, 24),
		BackgroundTransparency = 1,
	}, parent)
	make("UIListLayout", {
		FillDirection = Enum.FillDirection.Horizontal,
		Padding = UDim.new(0, 4),
		SortOrder = Enum.SortOrder.LayoutOrder,
	}, bar)
	local buttons = {}
	local function paint()
		for step, button in buttons do
			local picked = step == materialStep
			button.BackgroundColor3 = if picked then Color3.fromRGB(120, 90, 50) else Color3.fromRGB(46, 38, 30)
		end
	end
	for order, step in VaultController.MATERIAL_STEPS do
		local button = make("TextButton", {
			Text = if step then ("×%d"):format(step) else "All",
			LayoutOrder = order,
			Size = UDim2.new(0.25, -3, 1, 0),
			TextColor3 = Color3.fromRGB(245, 236, 222),
			Font = Enum.Font.GothamBold,
			TextSize = 13,
		}, bar)
		make("UICorner", { CornerRadius = UDim.new(0, 6) }, button)
		buttons[step] = button
		button.Activated:Connect(function()
			materialStep = step
			paint()
			refresh()
		end)
	end
	paint()
end

local function build()
	-- Above the always-open lobby panel.
	local gui =
		make("ScreenGui", { Name = "Vault", ResetOnSpawn = false, DisplayOrder = 2 }, player:WaitForChild("PlayerGui"))
	-- Never taller than the screen, so the close button stays reachable on phones.
	ui.panel = make("Frame", {
		AnchorPoint = Vector2.new(0.5, 0.5),
		Position = UDim2.fromScale(0.45, 0.5),
		Size = UDim2.new(0.6, 0, 1, -24),
		BackgroundColor3 = Color3.fromRGB(24, 20, 17),
		Active = true,
		Visible = false,
	}, gui)
	make("UICorner", { CornerRadius = UDim.new(0, 8) }, ui.panel)
	make("UISizeConstraint", { MaxSize = Vector2.new(820, 420), MinSize = Vector2.new(480, 240) }, ui.panel)
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
		hideConfirm()
	end)
	ui.backpackTitle, ui.backpack = column(ui.panel, 0, "Lobby backpack")
	ui.itemsTitle, ui.items = column(ui.panel, 1 / 3, "Vault items")
	local _, materials = column(ui.panel, 2 / 3, "Vault materials · click to take", 86)
	ui.materials = materials
	buildSteps(ui.panel, 2 / 3, 58)
	-- "N would be deleted — deposit anyway?" above the status line.
	ui.confirm = make("Frame", {
		AnchorPoint = Vector2.new(0, 1),
		Position = UDim2.new(0, 10, 1, -32),
		Size = UDim2.new(1, -20, 0, 30),
		BackgroundColor3 = Color3.fromRGB(70, 34, 28),
		Visible = false,
		ZIndex = 3,
	}, ui.panel)
	make("UICorner", { CornerRadius = UDim.new(0, 6) }, ui.confirm)
	ui.confirmText = make("TextLabel", {
		Text = "",
		Position = UDim2.fromOffset(8, 0),
		Size = UDim2.new(1, -196, 1, 0),
		BackgroundTransparency = 1,
		TextXAlignment = Enum.TextXAlignment.Left,
		TextTruncate = Enum.TextTruncate.AtEnd,
		TextColor3 = Color3.fromRGB(255, 214, 200),
		Font = Enum.Font.GothamMedium,
		TextSize = 13,
		ZIndex = 3,
	}, ui.confirm)
	for order, choice in { { "Deposit anyway", confirmDeposit }, { "Cancel", hideConfirm } } do
		local button = make("TextButton", {
			Text = choice[1],
			AnchorPoint = Vector2.new(1, 0.5),
			Position = UDim2.new(1, if order == 1 then -76 else -4, 0.5, 0),
			Size = UDim2.fromOffset(if order == 1 then 110 else 68, 24),
			BackgroundColor3 = if order == 1 then Color3.fromRGB(150, 60, 44) else Color3.fromRGB(70, 56, 40),
			TextColor3 = Color3.fromRGB(245, 236, 222),
			Font = Enum.Font.GothamBold,
			TextSize = 13,
			ZIndex = 3,
		}, ui.confirm)
		make("UICorner", { CornerRadius = UDim.new(0, 6) }, button)
		button.Activated:Connect(choice[2])
	end
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

	-- In the shared top-centre column with the other banners.
	ui.receipt = make("TextButton", {
		Size = UDim2.fromOffset(460, 0),
		LayoutOrder = Theme.TopOrder.Receipt,
		AutomaticSize = Enum.AutomaticSize.Y,
		BackgroundColor3 = Color3.fromRGB(16, 38, 30),
		BackgroundTransparency = 0.05,
		TextColor3 = Color3.fromRGB(210, 255, 226),
		TextWrapped = true,
		Font = Enum.Font.GothamMedium,
		TextSize = 14,
		Visible = false,
	}, Theme.TopStack())
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
	if receipt.carriedIn and next(receipt.carriedIn) then
		-- What the player brought into the run settles once (GDD §53).
		table.insert(lines, "Brought in, not doubled: " .. listOf(receipt.carriedIn))
	end
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

-- Opens or closes this panel (keys, and the on-screen navigation bar).
function VaultController.Toggle()
	ui.panel.Visible = not ui.panel.Visible
	hideConfirm()
	if ui.panel.Visible then
		ui.status.Text = ""
		refresh()
	end
end

function VaultController.IsOpen(): boolean
	return ui.panel ~= nil and ui.panel.Visible
end

function VaultController.Start()
	if not PlaceConfig.IsLobby() then
		return
	end
	build()
	Remotes.Get("ExtractionReceipt").OnClientEvent:Connect(showReceipt)
	Binds.Bind("Backpack", function(_, state)
		if state == Enum.UserInputState.Begin then
			VaultController.Toggle()
		end
		return Enum.ContextActionResult.Sink
	end)
end

return VaultController
