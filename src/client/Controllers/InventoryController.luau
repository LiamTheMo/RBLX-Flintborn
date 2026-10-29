-- Hotbar (6 slots, keys 1–6) and backpack (50 slots) for the run inventory
-- (GDD §25.4, §25.4.1). Tapping a hotbar slot (or pressing its key) equips a tool or weapon, uses a
-- consumable, places a workbench, readies a Fire Bomb (the attack input or touch
-- Attack button then throws it) or sets a Breaching Charge on the wall or door in
-- the crosshair (with none in reach it is held instead, and the attack input sets
-- it once one is). The Backpack key opens the parchment inventory window
-- (Hud/InventoryPanel): the backpack on the left, the hotbar and worn armour on
-- the right. Choose a slot, then another to move or swap (no precise dragging);
-- the arrows send the chosen item to the hotbar or back to the backpack, WEAR /
-- TAKE OFF handle armour and DROP drops it. Server snapshots are the only truth.
-- World place only. With the new HUD (HudMode) its own hotbar strip draws the
-- slots; the old strip here shows only with the legacy HUD.

local ContextActionService = game:GetService("ContextActionService")
local GuiService = game:GetService("GuiService")
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
local InventoryPanel = require(script.Parent.Parent.Hud.InventoryPanel)
local NoticeCard = require(script.Parent.Parent.Hud.NoticeCard)
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
local slotButtons = { hotbar = {} }
local ARMOR_SLOTS = { "Head", "Chest", "Legs" }
-- The chosen slot in the inventory window: {area, index}.
local selected = nil
local panel = nil
local dropSelected

local CLOSE_ACTION = "FlintbornBackpackClose"

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
	ui.toast:Show(message)
	local shown = message
	task.delay(2.5, function()
		if ui.toast.text.Text == shown then
			ui.toast:Hide()
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

local function sameSlot(a, b): boolean
	return a ~= nil and b ~= nil and a.area == b.area and a.index == b.index
end

-- The first empty slot of `area`, or nil.
local function firstEmpty(area: string, count: number): number?
	for index = 1, count do
		if slotAt(area, index) == nil then
			return index
		end
	end
	return nil
end

local function move(from, area: string, index: number)
	local ok, reason = invoke("MoveItem", from.area, from.index, area, index)
	if not ok then
		toast("Can't move that (" .. Reasons.Text(reason) .. ")")
	end
end

local function wear(from)
	local ok, reason = invoke("EquipArmor", from.area, from.index)
	if not ok then
		toast("Can't wear that (" .. Reasons.Text(reason) .. ")")
	end
end

local function takeOff(index: number)
	local ok, reason = invoke("UnequipArmor", ARMOR_SLOTS[index])
	if not ok then
		toast("No room to take that off (" .. Reasons.Text(reason) .. ")")
	end
end

local function isArmor(slot): boolean
	local def = slot and ItemCatalog.Get(slot.catalogId)
	return def ~= nil and def.family == ItemCatalog.Families.Armor
end

-- A slot pressed in the inventory window: the first press chooses it, a press on
-- another slot moves or swaps the chosen item there (an armour slot wears it, a
-- worn piece pressed onto the backpack or hotbar comes off), the same slot again
-- lets go.
local function onSlot(area: string, index: number)
	local target = { area = area, index = index }
	local from = selected
	if from == nil then
		if slotAt(area, index) then
			selected = target
		end
		InventoryController.Render()
		return
	end
	selected = nil
	if not sameSlot(from, target) then
		if area == "armor" then
			if from.area ~= "armor" then
				wear(from)
			end
		elseif from.area == "armor" then
			takeOff(from.index)
		else
			move(from, area, index)
		end
	end
	InventoryController.Render()
end

-- Kept for the old on-screen hotbar strip (shown without the new HUD).
local function onSlotClicked(area: string, index: number)
	if area == "hotbar" and not (panel and panel.screen:IsOpen()) then
		activateHotbar(index)
	else
		onSlot(area, index)
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
	-- Hotbar slots show the key that selects them (rebindable, so kept current).
	local keyLabel = make("TextLabel", {
		Text = Binds.Label("Hotbar" .. index),
		Size = UDim2.fromOffset(40, 14),
		BackgroundTransparency = 1,
		TextXAlignment = Enum.TextXAlignment.Left,
		TextColor3 = Color3.fromRGB(200, 190, 170),
		Font = Enum.Font.GothamBold,
		TextSize = 11,
	}, button)
	button.Activated:Connect(function()
		onSlotClicked(area, index)
	end)
	slotButtons[area][index] = { button = button, stroke = stroke, label = label, keyLabel = keyLabel }
end

local function panelItem(slot)
	if slot == nil then
		return nil
	end
	local def = ItemCatalog.Get(slot.catalogId)
	return {
		catalogId = slot.catalogId,
		name = def and def.name or slot.catalogId,
		quantity = slot.quantity,
		rarity = def and def.rarity or "Common",
		permanent = slot.permanent,
		qualityRoll = slot.qualityRoll,
	}
end

local function id(area: string, index: number): string
	return area .. ":" .. index
end

-- The detail strip, arrows and action for the chosen slot.
local function showChoice()
	local choice = selected
	local slot = choice and slotAt(choice.area, choice.index)
	if choice and slot == nil then
		selected, choice = nil, nil
	end
	panel:Select(
		choice
			and { paneId = if choice.area == "backpack" then "left" else "right", id = id(choice.area, choice.index) },
		InventoryController.Snapshot.equipped
			and { paneId = "right", id = id("hotbar", InventoryController.Snapshot.equipped) }
	)
	panel:SetDetail(panelItem(slot), "Choose a slot, then another to move or swap.")
	local def = slot and ItemCatalog.Get(slot.catalogId)
	local action = nil
	if choice and choice.area == "hotbar" then
		local using = def and def.family == ItemCatalog.Families.Consumable
		local held = InventoryController.Snapshot.equipped == choice.index
		action = {
			if using then "USE" elseif held then "PUT AWAY" else "EQUIP",
			true,
			function()
				task.spawn(activateHotbar, choice.index)
			end,
		}
	elseif choice and choice.area == "armor" then
		action = {
			"TAKE OFF",
			true,
			function()
				selected = nil
				takeOff(choice.index)
				InventoryController.Render()
			end,
		}
	elseif choice and isArmor(slot) then
		action = {
			"WEAR",
			true,
			function()
				selected = nil
				wear(choice)
				InventoryController.Render()
			end,
		}
	end
	panel:SetActions({ nil, action })
	-- → puts a backpack item on the hotbar (armour on its slot); ← brings a hotbar
	-- or worn item back to the backpack.
	local toRight = choice ~= nil and choice.area == "backpack"
	local toLeft = choice ~= nil and choice.area ~= "backpack"
	panel:SetMiddle({
		toRight,
		function()
			selected = nil
			if isArmor(slot) then
				wear(choice)
			else
				local free = firstEmpty("hotbar", GameConstants.HOTBAR_SLOTS)
				if free then
					move(choice, "hotbar", free)
				else
					toast("Your hotbar is full.")
				end
			end
			InventoryController.Render()
		end,
	}, {
		toLeft,
		function()
			selected = nil
			if choice.area == "armor" then
				takeOff(choice.index)
			else
				local free = firstEmpty("backpack", GameConstants.BACKPACK_SLOTS)
				if free then
					move(choice, "backpack", free)
				else
					toast("Your backpack is full.")
				end
			end
			InventoryController.Render()
		end,
	}, {
		("DROP\n(%s)"):format(Binds.Label("Drop")),
		-- The window's DROP takes only the chosen slot, and worn armour comes
		-- off first (the server drops from the hotbar and backpack only).
		slot ~= nil and choice ~= nil and choice.area ~= "armor",
		function()
			dropSelected()
		end,
	})
end

function InventoryController.Render()
	local equipped = InventoryController.Snapshot.equipped
	for index, parts in slotButtons.hotbar do
		local slot = slotAt("hotbar", index)
		if slot then
			local text, rarity = describe(slot)
			parts.label.Text = text .. "\n" .. rarity
			parts.stroke.Color = Rarity.Colors[rarity] or Color3.fromRGB(70, 60, 50)
		else
			parts.label.Text = ""
			parts.stroke.Color = Color3.fromRGB(70, 60, 50)
		end
		local isEquipped = equipped == index
		parts.stroke.Thickness = if isEquipped then 4 else 2
		parts.button.BackgroundColor3 = isEquipped and Color3.fromRGB(78, 62, 40) or Color3.fromRGB(36, 31, 26)
	end
	if panel == nil or not panel.screen:IsOpen() then
		return
	end
	local backpack, hotbar, armor = {}, {}, {}
	local used = 0
	for index = 1, GameConstants.BACKPACK_SLOTS do
		local slot = slotAt("backpack", index)
		used += if slot then 1 else 0
		table.insert(backpack, { id = id("backpack", index), area = "backpack", index = index, item = panelItem(slot) })
	end
	for index = 1, GameConstants.HOTBAR_SLOTS do
		table.insert(hotbar, {
			id = id("hotbar", index),
			area = "hotbar",
			index = index,
			item = panelItem(slotAt("hotbar", index)),
			key = Binds.Label("Hotbar" .. index),
		})
	end
	for index, name in ARMOR_SLOTS do
		table.insert(armor, {
			id = id("armor", index),
			area = "armor",
			index = index,
			item = panelItem(slotAt("armor", index)),
			key = name,
		})
	end
	panel:SetHeader("left", ("BACKPACK %d/%d"):format(used, GameConstants.BACKPACK_SLOTS))
	panel:SetPane("left", { { entries = backpack } }, "dim")
	panel:SetPane("right", { { header = "Hotbar", entries = hotbar }, { header = "Armour", entries = armor } }, "dim")
	showChoice()
end

-- Drops the selected slot, or else the equipped hotbar item (the Drop key, L1 or the window's DROP).
function dropSelected()
	local target = selected
		or (
			InventoryController.Snapshot.equipped and { area = "hotbar", index = InventoryController.Snapshot.equipped }
		)
	selected = nil
	if target then
		local ok, reason = invoke("DropItem", target.area, target.index)
		if not ok then
			toast("Can't drop that (" .. Reasons.Text(reason) .. ")")
		end
	else
		toast("Select a slot (or equip an item) to drop it.")
	end
	InventoryController.Render()
end

local function closeBackpack()
	ContextActionService:UnbindAction(CLOSE_ACTION)
	selected = nil
	local focus = GuiService.SelectedObject
	if focus and focus:IsDescendantOf(panel.screen.gui) then
		GuiService.SelectedObject = nil
	end
	panel.screen:SetOpen(false)
	InventoryController.Render()
	InventoryController.BackpackToggled:Fire(false)
end

local function build()
	local gui = make("ScreenGui", { Name = "Inventory", ResetOnSpawn = false }, player:WaitForChild("PlayerGui"))
	ui.root = make("Frame", { Size = UDim2.fromScale(1, 1), BackgroundTransparency = 1, Visible = false }, gui)

	-- The old hotbar strip, for the legacy HUD only (the new HUD draws its own).
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
		toggle.Text = ("Backpack (%s)"):format(Binds.Label("Backpack"))
		for index, parts in slotButtons.hotbar do
			parts.keyLabel.Text = Binds.Label("Hotbar" .. index)
		end
		InventoryController.Render()
	end
	relabel()
	Binds.Changed:Connect(relabel)

	ui.toast = NoticeCard.new(Theme.TopStack(), { name = "Toast", width = 420, layoutOrder = Theme.TopOrder.Toast })

	-- The backpack window: backpack on the left, hotbar and armour on the right.
	panel = InventoryPanel.new(player:WaitForChild("PlayerGui"), {
		onClose = closeBackpack,
		onSlot = function(_, entry)
			onSlot(entry.area, entry.index)
		end,
	})
	panel:SetTitle("INVENTORY")
	panel:SetHeader("right", "EQUIPMENT", "pm_cat_all", nil)
	panel:SetSortVisible(false)
	panel.screen:Watch()
end

InventoryController.ActivateHotbar = activateHotbar

function InventoryController.ToggleBackpack()
	if panel.screen:IsOpen() then
		closeBackpack()
		return
	end
	selected = nil
	panel.screen:SetOpen(true)
	ContextActionService:BindAction(CLOSE_ACTION, function(_, state)
		if state == Enum.UserInputState.Begin then
			closeBackpack()
		end
		return Enum.ContextActionResult.Sink
	end, false, Enum.KeyCode.ButtonB)
	if GuiService.SelectedObject ~= nil or UserInputService.GamepadEnabled then
		GuiService.SelectedObject = panel.tabs.All.button
	end
	InventoryController.Render()
	InventoryController.BackpackToggled:Fire(true)
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
		-- Leaving the run closes the window over the emptied inventory.
		if not inRun and panel.screen:IsOpen() then
			closeBackpack()
		end
	end)
	InventoryController.Render()
end

return InventoryController
