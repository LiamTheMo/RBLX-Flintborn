-- Hotbar (6 slots, keys 1–6) and backpack (50 slots) for the run inventory
-- (GDD §25.4, §25.4.1). Tapping a hotbar slot (or pressing its key) equips a tool or weapon, uses a
-- consumable, places a workbench, readies a Fire Bomb (the attack input or touch
-- Attack button then throws it) or sets a Breaching Charge on the wall or door in
-- the crosshair (with none in reach it is held instead, and the attack input sets
-- it once one is). In the backpack, tap one slot then another
-- to move or swap (no precise dragging). Server snapshots are the only truth.
-- World place only. With the new HUD (HudMode) its own hotbar strip draws the
-- slots, so this strip only shows while the backpack is open (to move items
-- between hotbar and backpack), and the Backpack button lives in the nav bar.

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local GameConstants = require(ReplicatedStorage.Shared.GameConstants)
local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Rarity = require(ReplicatedStorage.Shared.Items.Rarity)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local SiegeRules = require(ReplicatedStorage.Shared.Combat.SiegeRules)
local Signal = require(ReplicatedStorage.Shared.Core.Signal)
local HudMode = require(script.Parent.Parent.Hud.HudMode)
local Theme = require(script.Parent.Parent.Ui.Theme)
local Binds = require(script.Parent.Parent.Ui.Binds)
local Reasons = require(script.Parent.Parent.Ui.Reasons)

local InventoryController = {}

-- Fires (snapshot) whenever the server sends a new inventory.
InventoryController.Changed = Signal.new()
InventoryController.Snapshot = { slots = {}, equipped = nil }
-- Fires (open) when the backpack opens or closes.
InventoryController.BackpackToggled = Signal.new()

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

-- Where the player aims, as a direction from the head: through the mouse on
-- desktop, otherwise through the centre of the screen (touch and gamepad aim with
-- the camera). Nil without a character.
local function aimDirection(): Vector3?
	local character = player.Character
	local head = character and character:FindFirstChild("Head")
	local camera = workspace.CurrentCamera
	if head == nil or camera == nil then
		return nil
	end
	local screen = if Theme.UsingMouse() then UserInputService:GetMouseLocation() else camera.ViewportSize / 2
	local ray = camera:ViewportPointToRay(screen.X, screen.Y)
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	params.FilterDescendantsInstances = { character }
	local hit = workspace:Raycast(ray.Origin, ray.Direction * 200, params)
	local direction = (if hit then hit.Position else ray.Origin + ray.Direction * 200) - head.Position
	return if direction.Magnitude > 0.5 then direction.Unit else camera.CFrame.LookVector
end

-- Fire Bombs are equipped (the attack input throws them); a Breaching Charge is
-- set on the targeted wall or door at once. The server checks everything.
local function activateSiege(index: number, kind: string)
	if kind == "Placed" then
		local ok, reason = invoke("PlaceCharge", index, aimDirection())
		if ok then
			toast(SiegeRules.Message("ChargeSet"))
		elseif reason == "NoTarget" and InventoryController.Snapshot.equipped ~= index then
			-- Nothing in reach: hold it, so the attack input (or Attack button) sets it.
			invoke("EquipSlot", index)
			toast(SiegeRules.Message("ChargeReady"))
		else
			toast(SiegeRules.Message(reason))
		end
		return
	end
	local equipping = InventoryController.Snapshot.equipped ~= index
	local ok, reason = invoke("EquipSlot", index)
	if not ok then
		toast("Can't equip that (" .. tostring(reason) .. ")")
	elseif equipping then
		toast(SiegeRules.Message("BombReady"))
	end
end

-- Uses hotbar slot `index` as its key does: equip, use, place or ready it. The
-- HUD hotbar's taps call this too (yields on the server call).
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
			toast("Can't use that now: " .. Reasons.Text(reason))
		end
	elseif def and def.siege then
		activateSiege(index, def.siege.kind)
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
	local keyLabel = nil
	if area == "hotbar" or area == "armor" then
		-- Hotbar slots show the key that selects them (rebindable, so kept current).
		keyLabel = make("TextLabel", {
			Text = area == "armor" and ARMOR_SLOTS[index] or Binds.Label("Hotbar" .. index),
			Size = UDim2.fromOffset(40, 14),
			BackgroundTransparency = 1,
			TextXAlignment = Enum.TextXAlignment.Left,
			TextColor3 = Color3.fromRGB(200, 190, 170),
			Font = Enum.Font.GothamBold,
			TextSize = 11,
		}, button)
	end
	button.Activated:Connect(function()
		onSlotClicked(area, index)
	end)
	slotButtons[area][index] = {
		button = button,
		stroke = stroke,
		label = label,
		keyLabel = if area == "hotbar" then keyLabel else nil,
	}
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
		then ("Tap another slot to move or swap, an armor slot to wear it, or Drop (%s) to drop it."):format(
			Binds.Label("Drop")
		)
		else ""
end

-- Drops the selected slot, or else the equipped hotbar item (the Drop key, L1 or the Drop button).
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
		Name = "Hotbar",
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
	ui.hotbar = hotbar
	hotbar.Visible = not HudMode.ReplacesLegacy()

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
	-- Touch players have no Drop key: this drops the selected (or equipped) item.
	local drop = make("TextButton", {
		Text = "Drop",
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
		Text = "Backpack",
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
	-- The new HUD's hotbar spans this spot; the nav bar keeps a Backpack button.
	toggle.Visible = not HudMode.ReplacesLegacy()
	-- Button and slot captions name the player's current keys.
	local function relabel()
		drop.Text = ("Drop (%s)"):format(Binds.Label("Drop"))
		toggle.Text = ("Backpack (%s)"):format(Binds.Label("Backpack"))
		for index, parts in slotButtons.hotbar do
			if parts.keyLabel then
				parts.keyLabel.Text = Binds.Label("Hotbar" .. index)
			end
		end
	end
	relabel()
	Binds.Changed:Connect(relabel)

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

InventoryController.ActivateHotbar = activateHotbar

function InventoryController.ToggleBackpack()
	ui.backpack.Visible = not ui.backpack.Visible
	ui.armorRow.Visible = ui.backpack.Visible
	if HudMode.ReplacesLegacy() then
		ui.hotbar.Visible = ui.backpack.Visible
	end
	selected = nil
	InventoryController.Render()
	InventoryController.BackpackToggled:Fire(ui.backpack.Visible)
end

local function bindKeys(active: boolean)
	if not active then
		for index = 1, GameConstants.HOTBAR_SLOTS do
			Binds.Unbind("Hotbar" .. index)
		end
		Binds.Unbind("Backpack")
		Binds.Unbind("Drop")
		return
	end
	for index = 1, GameConstants.HOTBAR_SLOTS do
		Binds.Bind("Hotbar" .. index, function(_, state)
			if state == Enum.UserInputState.Begin then
				-- Spawned: activating calls the server, and a handler that yields
				-- counts as sinking the key, so the HUD hotbar would never see it.
				task.spawn(activateHotbar, index)
			end
			return Enum.ContextActionResult.Pass
		end)
	end
	Binds.Bind("Backpack", function(_, state)
		if state == Enum.UserInputState.Begin then
			InventoryController.ToggleBackpack()
		end
		return Enum.ContextActionResult.Sink
	end)
	-- Drop takes the selected slot, or else the equipped hotbar item.
	Binds.Bind("Drop", function(_, state)
		if state == Enum.UserInputState.Begin then
			dropSelected()
		end
		return Enum.ContextActionResult.Pass
	end)
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
