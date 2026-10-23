-- Hotbar (9 slots, keys 1–9) and backpack (50 slots) for the run inventory
-- (GDD §25.4, §25.4.1). Tapping a hotbar slot equips a tool or weapon, uses a
-- consumable, or places a workbench. In the backpack, tap one slot then another
-- to move or swap (no precise dragging). Server snapshots are the only truth.
-- World place only.

local ContextActionService = game:GetService("ContextActionService")
local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local GameConstants = require(ReplicatedStorage.Shared.GameConstants)
local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Rarity = require(ReplicatedStorage.Shared.Items.Rarity)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Signal = require(ReplicatedStorage.Shared.Core.Signal)
local Theme = require(script.Parent.Parent.Ui.Theme)

local InventoryController = {}

-- Fires (snapshot) whenever the server sends a new inventory.
InventoryController.Changed = Signal.new()
InventoryController.Snapshot = { slots = {}, equipped = nil }

local player = Players.LocalPlayer
local ui = {}
local slotButtons = { hotbar = {}, backpack = {}, armor = {} }
local ARMOR_SLOTS = { "Head", "Chest", "Legs" }
local selected = nil

local function make(className: string, props, parent)
	local instance = Instance.new(className)
	for key, value in props do
		instance[key] = value
	end
	instance.Parent = parent
	return instance
end

-- Total quantity of a stackable item in the latest snapshot.
function InventoryController.Count(catalogId: string): number
	local total = 0
	for _, slot in InventoryController.Snapshot.slots do
		if slot.catalogId == catalogId and slot.quantity then
			total += slot.quantity
		end
	end
	return total
end

local function toast(message: string)
	ui.toast.Text = message
	ui.toast.Visible = true
	local shown = message
	task.delay(2.5, function()
		if ui.toast.Text == shown then
			ui.toast.Visible = false
		end
	end)
end

local function invoke(name: string, ...)
	local ok, success, reason = pcall(Remotes.Get(name).InvokeServer, Remotes.Get(name), ...)
	if not ok then
		return false, "Request failed"
	end
	return success, reason
end

local function describe(slot)
	local def = ItemCatalog.Get(slot.catalogId)
	local name = def and def.name or slot.catalogId
	local text = (slot.permanent and "★ " or "") .. name .. (slot.quantity and (" ×" .. slot.quantity) or "")
	if slot.qualityRoll and slot.qualityRoll ~= 0 then
		text ..= ("  (%+.1f%%)"):format(slot.qualityRoll * 100)
	end
	return text, def and def.rarity or "Common"
end

local function slotAt(area: string, index: number)
	for _, slot in InventoryController.Snapshot.slots do
		if slot.area == area and slot.index == index then
			return slot
		end
	end
	return nil
end

local function activateHotbar(index: number)
	local slot = slotAt("hotbar", index)
	if slot == nil then
		invoke("EquipSlot", nil)
		return
	end
	local def = ItemCatalog.Get(slot.catalogId)
	if def and def.family == ItemCatalog.Families.Consumable then
		local ok, reason = invoke("UseConsumable", HttpService:GenerateGUID(false), slot.catalogId)
		if not ok then
			toast("Can't use that now (" .. tostring(reason) .. ")")
		end
	elseif def and def.placeable == "ExtractionRune" then
		local ok, reason = invoke("PlaceRune", index)
		toast(ok and "Rune placed: 30 s to extract." or ("Can't place a rune here (" .. tostring(reason) .. ")"))
	elseif def and def.placeable then
		local ok, reason = invoke("PlaceItem", index)
		toast(ok and (def.name .. " placed.") or ("Can't place that here (" .. tostring(reason) .. ")"))
	else
		invoke("EquipSlot", index)
	end
end

local function onArmorClicked(index: number)
	if selected then
		local from = selected
		selected = nil
		local ok, reason = invoke("EquipArmor", from.area, from.index)
		if not ok then
			toast("Can't wear that (" .. tostring(reason) .. ")")
		end
		InventoryController.Render()
	elseif slotAt("armor", index) then
		local ok, reason = invoke("UnequipArmor", ARMOR_SLOTS[index])
		if not ok then
			toast("No room to take that off (" .. tostring(reason) .. ")")
		end
	end
end

local function onSlotClicked(area: string, index: number)
	if area == "armor" then
		onArmorClicked(index)
		return
	end
	if selected then
		local from = selected
		selected = nil
		if from.area ~= area or from.index ~= index then
			local ok, reason = invoke("MoveItem", from.area, from.index, area, index)
			if not ok then
				toast("Can't move that (" .. tostring(reason) .. ")")
			end
		end
		InventoryController.Render()
		return
	end
	if area == "hotbar" and not ui.backpack.Visible then
		activateHotbar(index)
	elseif slotAt(area, index) then
		selected = { area = area, index = index }
		InventoryController.Render()
	end
end

local function makeSlot(area: string, index: number, parent)
	local button = make("TextButton", {
		Text = "",
		BackgroundColor3 = Color3.fromRGB(36, 31, 26),
		AutoButtonColor = true,
		LayoutOrder = index,
	}, parent)
	make("UICorner", { CornerRadius = UDim.new(0, 6) }, button)
	-- Border mode: the default (Contextual) strokes the button's empty text instead.
	local stroke = make(
		"UIStroke",
		{ Thickness = 2, Color = Color3.fromRGB(70, 60, 50), ApplyStrokeMode = Enum.ApplyStrokeMode.Border },
		button
	)
	local label = make("TextLabel", {
		Size = UDim2.new(1, -6, 1, -6),
		Position = UDim2.fromOffset(3, 3),
		BackgroundTransparency = 1,
		TextColor3 = Color3.fromRGB(245, 236, 222),
		TextWrapped = true,
		Font = Enum.Font.GothamMedium,
		TextSize = 11,
	}, button)
	if area == "hotbar" or area == "armor" then
		make("TextLabel", {
			Text = area == "armor" and ARMOR_SLOTS[index] or tostring(index),
			Size = UDim2.fromOffset(area == "armor" and 40 or 14, 14),
			BackgroundTransparency = 1,
			TextColor3 = Color3.fromRGB(200, 190, 170),
			Font = Enum.Font.GothamBold,
			TextSize = 11,
		}, button)
	end
	button.Activated:Connect(function()
		onSlotClicked(area, index)
	end)
	slotButtons[area][index] = { button = button, stroke = stroke, label = label }
end

function InventoryController.Render()
	local equipped = InventoryController.Snapshot.equipped
	for area, buttons in slotButtons do
		for index, parts in buttons do
			local slot = slotAt(area, index)
			if slot then
				local text, rarity = describe(slot)
				parts.label.Text = text .. "\n" .. rarity
				parts.stroke.Color = Rarity.Colors[rarity] or Color3.fromRGB(70, 60, 50)
			else
				parts.label.Text = ""
				parts.stroke.Color = Color3.fromRGB(70, 60, 50)
			end
			local isSelected = selected and selected.area == area and selected.index == index
			local isEquipped = area == "hotbar" and equipped == index
			parts.stroke.Thickness = (isSelected or isEquipped) and 4 or 2
			parts.button.BackgroundColor3 = isEquipped and Color3.fromRGB(78, 62, 40) or Color3.fromRGB(36, 31, 26)
		end
	end
	ui.hint.Text = if selected
		then "Tap another slot to move or swap, an armor slot to wear it, or Drop (Q) to drop it."
		else ""
end

-- Drops the selected slot, or else the equipped hotbar item (Q, L1 or the Drop button).
local function dropSelected()
	local target = selected
		or (
			InventoryController.Snapshot.equipped and { area = "hotbar", index = InventoryController.Snapshot.equipped }
		)
	selected = nil
	if target then
		local ok, reason = invoke("DropItem", target.area, target.index)
		if not ok then
			toast("Can't drop that (" .. tostring(reason) .. ")")
		end
	else
		toast("Select a slot (or equip an item) to drop it.")
	end
	InventoryController.Render()
end

local function build()
	local gui = make("ScreenGui", { Name = "Inventory", ResetOnSpawn = false }, player:WaitForChild("PlayerGui"))
	ui.root = make("Frame", { Size = UDim2.fromScale(1, 1), BackgroundTransparency = 1, Visible = false }, gui)

	local hotbar = make("Frame", {
		AnchorPoint = Vector2.new(0.5, 1),
		Position = UDim2.new(0.5, 0, 1, -12),
		Size = UDim2.fromOffset(GameConstants.HOTBAR_SLOTS * 66, 62),
		BackgroundTransparency = 1,
		Active = true,
	}, ui.root)
	make("UIGridLayout", {
		CellSize = UDim2.fromOffset(60, 60),
		CellPadding = UDim2.fromOffset(6, 0),
		SortOrder = Enum.SortOrder.LayoutOrder,
	}, hotbar)
	for index = 1, GameConstants.HOTBAR_SLOTS do
		makeSlot("hotbar", index, hotbar)
	end

	ui.backpack = make("Frame", {
		AnchorPoint = Vector2.new(0.5, 1),
		Position = UDim2.new(0.5, 0, 1, -86),
		Size = UDim2.fromOffset(10 * 66 + 12, 5 * 66 + 12),
		BackgroundColor3 = Color3.fromRGB(24, 20, 17),
		BackgroundTransparency = 0.1,
		Active = true,
		Visible = false,
	}, ui.root)
	make("UICorner", { CornerRadius = UDim.new(0, 8) }, ui.backpack)
	make("UIPadding", { PaddingLeft = UDim.new(0, 6), PaddingTop = UDim.new(0, 6) }, ui.backpack)
	make("UIGridLayout", {
		CellSize = UDim2.fromOffset(60, 60),
		CellPadding = UDim2.fromOffset(6, 6),
		SortOrder = Enum.SortOrder.LayoutOrder,
	}, ui.backpack)
	for index = 1, GameConstants.BACKPACK_SLOTS do
		makeSlot("backpack", index, ui.backpack)
	end

	-- Worn armor (Head, Chest, Legs/Boots): select a piece, then tap its slot to wear it.
	-- A column beside the backpack (not above it), with the Drop button under it,
	-- so it stays on-screen on short phone screens.
	local side = make("Frame", {
		AnchorPoint = Vector2.new(1, 1),
		Position = UDim2.new(0.5, -(5 * 66 + 6) - 8, 1, -86),
		Size = UDim2.fromOffset(62, 3 * 66 + 36),
		BackgroundTransparency = 1,
		Active = true,
		Visible = false,
	}, ui.root)
	ui.armorRow = side
	local armorColumn = make("Frame", {
		Size = UDim2.fromOffset(62, 3 * 66),
		BackgroundTransparency = 1,
		Active = true,
	}, side)
	make("UIGridLayout", {
		CellSize = UDim2.fromOffset(60, 60),
		CellPadding = UDim2.fromOffset(0, 6),
		SortOrder = Enum.SortOrder.LayoutOrder,
	}, armorColumn)
	for index = 1, #ARMOR_SLOTS do
		makeSlot("armor", index, armorColumn)
	end
	-- Touch players have no Q key: this drops the selected (or equipped) item.
	local drop = make("TextButton", {
		Text = "Drop (Q)",
		AnchorPoint = Vector2.new(0, 1),
		Position = UDim2.fromScale(0, 1),
		Size = UDim2.fromOffset(62, 30),
		BackgroundColor3 = Color3.fromRGB(120, 50, 40),
		TextColor3 = Color3.fromRGB(245, 236, 222),
		Font = Enum.Font.GothamBold,
		TextSize = 12,
	}, side)
	make("UICorner", { CornerRadius = UDim.new(0, 6) }, drop)
	drop.Activated:Connect(dropSelected)

	-- Right of the hotbar, above the Craft button (the XP bar owns the bottom-left).
	local toggle = make("TextButton", {
		Text = "Backpack (B)",
		AnchorPoint = Vector2.new(0, 1),
		Position = UDim2.new(0.5, 8 + GameConstants.HOTBAR_SLOTS * 33, 1, -46),
		Size = UDim2.fromOffset(100, 30),
		BackgroundColor3 = Color3.fromRGB(70, 56, 40),
		TextColor3 = Color3.fromRGB(245, 236, 222),
		Font = Enum.Font.GothamBold,
		TextSize = 13,
	}, ui.root)
	make("UICorner", { CornerRadius = UDim.new(0, 6) }, toggle)
	toggle.Activated:Connect(function()
		InventoryController.ToggleBackpack()
	end)

	ui.hint = make("TextLabel", {
		AnchorPoint = Vector2.new(0.5, 1),
		Position = UDim2.new(0.5, 0, 1, -80),
		Size = UDim2.fromOffset(400, 18),
		BackgroundTransparency = 1,
		TextColor3 = Color3.fromRGB(240, 232, 220),
		Font = Enum.Font.Gotham,
		TextSize = 13,
	}, ui.root)
	ui.toast = make("TextLabel", {
		Size = UDim2.fromOffset(420, 34),
		LayoutOrder = Theme.TopOrder.Toast,
		BackgroundColor3 = Color3.fromRGB(30, 26, 22),
		BackgroundTransparency = 0.2,
		TextColor3 = Color3.fromRGB(255, 236, 210),
		Font = Enum.Font.GothamMedium,
		TextSize = 15,
		Visible = false,
	}, Theme.TopStack())
	make("UICorner", { CornerRadius = UDim.new(0, 8) }, ui.toast)
end

function InventoryController.ToggleBackpack()
	ui.backpack.Visible = not ui.backpack.Visible
	ui.armorRow.Visible = ui.backpack.Visible
	selected = nil
	InventoryController.Render()
end

local function bindKeys(active: boolean)
	if not active then
		ContextActionService:UnbindAction("FlintbornHotbar")
		ContextActionService:UnbindAction("FlintbornBackpack")
		ContextActionService:UnbindAction("FlintbornDrop")
		return
	end
	local keys = {
		Enum.KeyCode.One,
		Enum.KeyCode.Two,
		Enum.KeyCode.Three,
		Enum.KeyCode.Four,
		Enum.KeyCode.Five,
		Enum.KeyCode.Six,
		Enum.KeyCode.Seven,
		Enum.KeyCode.Eight,
		Enum.KeyCode.Nine,
	}
	ContextActionService:BindAction("FlintbornHotbar", function(_, state, input)
		if state == Enum.UserInputState.Begin then
			local index = table.find(keys, input.KeyCode)
			if index then
				activateHotbar(index)
			end
		end
		return Enum.ContextActionResult.Pass
	end, false, table.unpack(keys))
	ContextActionService:BindAction("FlintbornBackpack", function(_, state)
		if state == Enum.UserInputState.Begin then
			InventoryController.ToggleBackpack()
		end
		return Enum.ContextActionResult.Sink
	end, false, Enum.KeyCode.B, Enum.KeyCode.ButtonY)
	-- Q drops the selected slot, or else the equipped hotbar item.
	ContextActionService:BindAction("FlintbornDrop", function(_, state)
		if state == Enum.UserInputState.Begin then
			dropSelected()
		end
		return Enum.ContextActionResult.Pass
	end, false, Enum.KeyCode.Q, Enum.KeyCode.ButtonL1)
end

function InventoryController.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	build()
	Remotes.Get("InventoryChanged").OnClientEvent:Connect(function(snapshot)
		InventoryController.Snapshot = snapshot
		local inRun = #snapshot.slots > 0 or player:GetAttribute("SessionState") == "ActiveRun"
		ui.root.Visible = inRun
		bindKeys(inRun)
		InventoryController.Render()
		InventoryController.Changed:Fire(snapshot)
	end)
	Remotes.Get("Notify").OnClientEvent:Connect(toast)
	player:GetAttributeChangedSignal("SessionState"):Connect(function()
		local inRun = player:GetAttribute("SessionState") == "ActiveRun"
		ui.root.Visible = inRun
		bindKeys(inRun)
	end)
	InventoryController.Render()
end

return InventoryController
