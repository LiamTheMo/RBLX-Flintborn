-- Hotbar (6 slots, keys 1–6) and backpack (50 slots) for the run inventory
-- (GDD §25.4, §25.4.1). Tapping a hotbar slot (or pressing its key) equips a tool or weapon, uses a
-- consumable, places a workbench, readies a Fire Bomb (the attack input or touch
-- Attack button then throws it) or sets a Breaching Charge on the wall or door in
-- the crosshair (with none in reach it is held instead, and the attack input sets
-- it once one is). The Backpack key (B, Y on a gamepad) opens the Inventory
-- window (Hud/Screens/InventoryWindow) on two tabs: Backpack, and Equipped (the
-- hotbar and worn armour). Choose a slot to see it in the detail card: EQUIP puts
-- a backpack item on the hotbar (WEAR for armour), USE / EQUIP / PUT AWAY act on
-- a hotbar slot as its key does, TAKE OFF removes worn armour, MOVE then any
-- other slot moves or swaps it there (no precise dragging), and DROP drops it.
-- Server snapshots are the only truth. World place only. With the new HUD
-- (HudMode) its own hotbar strip draws the slots; the old strip here shows only
-- with the legacy HUD.

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local GameConstants = require(ReplicatedStorage.Shared.GameConstants)
local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local ItemInfo = require(ReplicatedStorage.Shared.Items.ItemInfo)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Rarity = require(ReplicatedStorage.Shared.Items.Rarity)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local SiegeRules = require(ReplicatedStorage.Shared.Combat.SiegeRules)
local Signal = require(ReplicatedStorage.Shared.Core.Signal)
local HudMode = require(script.Parent.Parent.Hud.HudMode)
local Kit = require(script.Parent.Parent.Hud.Kit)
local InventoryWindow = require(script.Parent.Parent.Hud.Screens.InventoryWindow)
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
-- The chosen slot in the inventory window: {area, index}; `moving` is the slot
-- MOVE picked up, waiting for the slot to put it in.
local selected = nil
local moving = nil
local tab = "Backpack"
local window = nil
local busy = false
local dropSelected

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

-- A short notice in the kit's toast column (server notices, refusals).
local function toast(message: string, kind: string?)
	Kit.Toast.Show({
		kind = kind or "info",
		title = if kind == "warn" then "Not possible" else "Inventory",
		text = message,
		duration = 3,
	})
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
	local text = name .. (slot.quantity and (" ×" .. slot.quantity) or "") .. (slot.permanent and " (Permanent)" or "")
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
			toast("Can't use that now: " .. Reasons.Text(reason), "warn")
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
		toast("Can't move that (" .. Reasons.Text(reason) .. ")", "warn")
	end
end

local function wear(from)
	local ok, reason = invoke("EquipArmor", from.area, from.index)
	if not ok then
		toast("Can't wear that (" .. Reasons.Text(reason) .. ")", "warn")
	end
end

local function takeOff(index: number)
	local ok, reason = invoke("UnequipArmor", ARMOR_SLOTS[index])
	if not ok then
		toast("No room to take that off (" .. Reasons.Text(reason) .. ")", "warn")
	end
end

local function isArmor(slot): boolean
	local def = slot and ItemCatalog.Get(slot.catalogId)
	return def ~= nil and def.family == ItemCatalog.Families.Armor
end

local onWindowSlot

-- Kept for the old on-screen hotbar strip (shown without the new HUD): a tap
-- uses the slot, or with the window open picks it there.
local function onSlotClicked(area: string, index: number)
	if area == "hotbar" and not (window and window:IsOpen()) then
		task.spawn(activateHotbar, index)
	else
		onWindowSlot(area .. ":" .. index)
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

local function itemOf(slot)
	return slot
		and {
			catalogId = slot.catalogId,
			quantity = slot.quantity,
			permanent = slot.permanent,
			qualityRoll = slot.qualityRoll,
		}
end

local function cellId(area: string, index: number): string
	return area .. ":" .. index
end

local function parseCell(id: string): (string?, number?)
	local area, index = string.match(id, "^(%a+):(%d+)$")
	return area, tonumber(index)
end

-- Runs a window action with every button held ("…") until the server answers;
-- the snapshot that follows redraws the window.
local function run(fn)
	if busy then
		return
	end
	busy = true
	if window then
		window:SetBusy(true)
	end
	task.spawn(function()
		local ok, err = pcall(fn)
		busy = false
		if window then
			window:SetBusy(false)
		end
		InventoryController.Render()
		if not ok then
			warn("InventoryController: " .. tostring(err))
		end
	end)
end

-- Moves (or swaps) the picked-up slot `from` onto `target`: onto an armour slot
-- it is worn, a worn piece put elsewhere comes off.
local function place(from, target)
	if sameSlot(from, target) then
		return
	end
	run(function()
		if target.area == "armor" then
			if from.area ~= "armor" then
				wear(from)
			end
		elseif from.area == "armor" then
			takeOff(from.index)
		else
			move(from, target.area, target.index)
		end
	end)
end

-- A slot pressed in the window: while MOVE holds an item it goes there;
-- otherwise a filled slot is chosen and an empty one clears the choice.
function onWindowSlot(id: string)
	local area, index = parseCell(id)
	if area == nil or index == nil then
		return
	end
	local target = { area = area, index = index }
	if moving then
		local from = moving
		moving = nil
		selected = target
		place(from, target)
		InventoryController.Render()
		return
	end
	selected = if slotAt(area, index) then target else nil
	InventoryController.Render()
end

-- The card's actions for the chosen slot: the main one first, then MOVE and DROP.
local function actionsFor(choice, slot)
	local def = ItemCatalog.Get(slot.catalogId)
	local main
	if choice.area == "hotbar" then
		local using = def and def.family == ItemCatalog.Families.Consumable
		local held = InventoryController.Snapshot.equipped == choice.index
		main = {
			id = "activate",
			label = if using
				then "Use"
				elseif def and def.placeable then "Place"
				elseif held then "Put Away"
				else "Equip",
		}
	elseif choice.area == "armor" then
		main = { id = "takeOff", label = "Take Off" }
	elseif isArmor(slot) then
		main = { id = "wear", label = "Wear" }
	else
		main = { id = "toHotbar", label = "Equip" }
	end
	local actions = { main, { id = "move", label = "Move" } }
	-- The server drops from the hotbar and backpack only: worn armour comes off first.
	if choice.area ~= "armor" then
		table.insert(actions, { id = "drop", label = ("Drop (%s)"):format(Binds.Label("Drop")) })
	end
	return actions
end

local function showDetail()
	local choice = selected
	local slot = choice and slotAt(choice.area, choice.index)
	if choice and slot == nil then
		selected, choice = nil, nil
	end
	window:SetSelected(if choice then cellId(choice.area, choice.index) else nil)
	if moving then
		local from = slotAt(moving.area, moving.index)
		local def = from and ItemCatalog.Get(from.catalogId)
		window:SetDetail({
			catalogId = from and from.catalogId,
			name = def and def.name or "",
			text = "Choose the slot to move it to: an empty one, or another item to swap with.",
			rows = {},
			actions = { { id = "cancelMove", label = "Cancel Move", variant = "secondary" } },
		})
		return
	end
	if slot == nil then
		window:SetDetail({
			hint = if tab == "Backpack"
				then "Choose an item to equip, move or drop it."
				else "Your hotbar (keys 1–6) and worn armour. Choose a slot to use, move or take it off.",
		})
		return
	end
	local item = itemOf(slot)
	local def = ItemCatalog.Get(slot.catalogId)
	window:SetDetail({
		catalogId = slot.catalogId,
		name = def and def.name or slot.catalogId,
		text = ItemInfo.Text(item),
		rows = ItemInfo.StatRows(item),
		actions = actionsFor(choice, slot),
	})
end

local function onAction(id: string)
	if id == "cancelMove" then
		moving = nil
		InventoryController.Render()
		return
	end
	local choice = selected
	local slot = choice and slotAt(choice.area, choice.index)
	if choice == nil or slot == nil or busy then
		return
	end
	if id == "activate" then
		run(function()
			activateHotbar(choice.index)
		end)
	elseif id == "takeOff" then
		run(function()
			takeOff(choice.index)
		end)
	elseif id == "wear" then
		run(function()
			wear(choice)
		end)
	elseif id == "toHotbar" then
		local free = firstEmpty("hotbar", GameConstants.HOTBAR_SLOTS)
		if free == nil then
			toast("Your hotbar is full: MOVE the item onto a hotbar slot to swap.", "warn")
			return
		end
		selected = { area = "hotbar", index = free }
		run(function()
			move(choice, "hotbar", free)
		end)
	elseif id == "move" then
		moving = choice
		InventoryController.Render()
	elseif id == "drop" then
		run(function()
			dropSelected()
		end)
	end
end

-- Redraws the window from the latest snapshot.
local function renderWindow()
	local backpack, hotbar, armor = {}, {}, {}
	for index = 1, GameConstants.BACKPACK_SLOTS do
		local slot = slotAt("backpack", index)
		table.insert(backpack, { id = cellId("backpack", index), item = itemOf(slot) })
	end
	for index = 1, GameConstants.HOTBAR_SLOTS do
		table.insert(hotbar, {
			id = cellId("hotbar", index),
			item = itemOf(slotAt("hotbar", index)),
			hotkey = Binds.Label("Hotbar" .. index),
		})
	end
	for index, name in ARMOR_SLOTS do
		table.insert(armor, { id = cellId("armor", index), item = itemOf(slotAt("armor", index)), caption = name })
	end
	window:SelectTab(tab)
	if tab == "Backpack" then
		window:SetSections({ { id = "backpack", cells = backpack } })
	else
		window:SetSections({
			{ id = "hotbar", title = "Hotbar", cells = hotbar },
			{ id = "armor", title = "Armour", cells = armor },
		})
	end
	showDetail()
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
	if window and window:IsOpen() then
		renderWindow()
	end
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
			toast("Can't drop that (" .. Reasons.Text(reason) .. ")", "warn")
		end
	else
		toast("Select a slot (or equip an item) to drop it.")
	end
	InventoryController.Render()
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

	-- The Inventory window: Backpack, and Equipped (hotbar and armour).
	window = InventoryWindow.new({
		tabs = {
			{ id = "Backpack", label = "Backpack", icon = "backpack", iconSelected = "backpack_white" },
			{ id = "Equipped", label = "Equipped", icon = "hatchet" },
		},
		onTab = function(id)
			tab = id
			selected, moving = nil, nil
			InventoryController.Render()
		end,
		onSlot = onWindowSlot,
		onAction = onAction,
		onClose = function()
			selected, moving = nil, nil
			InventoryController.BackpackToggled:Fire(false)
		end,
	})
	InventoryController.window = window
end

InventoryController.ActivateHotbar = activateHotbar

-- Opens the window on `tabId` ("Backpack" or "Equipped"; the last tab
-- otherwise). `gamepad` moves gamepad selection into it.
function InventoryController.Open(tabId: string?, gamepad: boolean?)
	if window == nil or window:IsOpen() then
		return
	end
	if tabId == "Backpack" or tabId == "Equipped" then
		tab = tabId
	end
	selected, moving = nil, nil
	-- Drawn once open; a gamepad then lands on the first slot (InventoryWindow).
	window:Open(gamepad or Kit.Input.IsGamepad())
	InventoryController.Render()
	InventoryController.BackpackToggled:Fire(true)
end

function InventoryController.IsOpen(): boolean
	return window ~= nil and window:IsOpen()
end

-- Opens or closes the window (the Backpack key, the HUD's backpack button).
function InventoryController.ToggleBackpack(gamepad: boolean?)
	if InventoryController.IsOpen() then
		window:Close()
	else
		InventoryController.Open(nil, gamepad)
	end
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
	Binds.Bind("Backpack", function(_, state, input)
		if state == Enum.UserInputState.Begin then
			InventoryController.ToggleBackpack(input ~= nil and input.KeyCode == Enum.KeyCode.ButtonY)
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
	Remotes.Get("Notify").OnClientEvent:Connect(function(message)
		toast(tostring(message))
	end)
	player:GetAttributeChangedSignal("SessionState"):Connect(function()
		local inRun = player:GetAttribute("SessionState") == "ActiveRun"
		ui.root.Visible = inRun
		bindKeys(inRun)
		-- Leaving the run closes the window over the emptied inventory.
		if not inRun and InventoryController.IsOpen() then
			window:Close()
		end
	end)
	InventoryController.Render()
end

return InventoryController
