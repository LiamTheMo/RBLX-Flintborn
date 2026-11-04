-- Lobby vault and lobby backpack (GDD §10.3, §25.2, §53) in the Inventory window
-- (Hud/Screens/InventoryWindow, docs/ui/InventoryScreen.md). The Backpack tile,
-- the Backpack key (B by default, Y on a gamepad, GDD §46) or Open(tab) opens
-- it on the Backpack tab (everything the player owns: the lobby backpack, then
-- the vault's items and materials) or the Vault tab (the vault alone;
-- InventoryModel.LobbySections). Choose a slot to see it in the detail
-- card: STORE puts a backpack item in the vault, TAKE brings a vault entry out
-- (a stack or vault material in the amount picked with the stepper) and it deploys with
-- the backpack on the next Play. STORE ALL vaults the whole backpack; SORT cycles
-- the order. A material deposit the vault cannot hold in full asks first how
-- much it would delete (GDD §53). The latest extraction receipt arrives as an
-- "Items Received" toast that opens the full receipt. Lobby place only.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local InventoryModel = require(ReplicatedStorage.Shared.UI.InventoryModel)
local InventoryRules = require(ReplicatedStorage.Shared.Inventory.InventoryRules)
local ItemInfo = require(ReplicatedStorage.Shared.Items.ItemInfo)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Signal = require(ReplicatedStorage.Shared.Core.Signal)
local Kit = require(script.Parent.Parent.Hud.Kit)
local InventoryWindow = require(script.Parent.Parent.Hud.Screens.InventoryWindow)
local Binds = require(script.Parent.Parent.Ui.Binds)
local Reasons = require(script.Parent.Parent.Ui.Reasons)

local VaultController = {}

-- Fires (view) whenever a fresh snapshot of the backpack and vault arrives, so
-- the HUD hotbar and the Play window can refresh their preview.
VaultController.Changed = Signal.new()

VaultController.TABS = { "Backpack", "Vault" }
-- Orders the sort button cycles through.
VaultController.SORTS = { "Saved", "Name", "Count" }

local window = nil
local view = nil
local tab = "Backpack"
-- The chosen cell: "b<index>" (backpack), "i<index>" (vault item) or
-- "m<catalogId>" (vault material).
local selected: string? = nil
local amount = 10
local sortIndex = 1
local busy = false

local function notify(kind: string, title: string, text: string?)
	Kit.Toast.Show({ kind = kind, title = title, text = text, duration = if kind == "warn" then 5 else 3 })
end

local function refused(reason: any)
	notify("warn", "Not possible", Reasons.Sentence(reason))
end

local function nameOf(entry): string
	local def = ItemCatalog.Get(entry.catalogId)
	return entry.name or (def and def.name) or entry.catalogId
end

-- The armour slot ("Head", "Chest", "Legs") an entry is worn in, or nil.
local function armorSlotOf(entry): string?
	local def = entry and ItemCatalog.Get(entry.catalogId)
	return def and def.armor and def.armor.slot or nil
end

local ARMOR_SLOTS = InventoryModel.ARMOR_SLOTS

-- The entry behind a cell id: {kind, index?, entry}, or nil. Kinds: "backpack",
-- "item" (vault), "material" (vault), "hotbar" and "armor" (the lobby loadout).
local function entryFor(id: string?)
	if id == nil or view == nil then
		return nil
	end
	local area, number = string.match(id, "^(%a+):(%d+)$")
	if area == "hotbar" or area == "armor" then
		local index = tonumber(number) :: number
		local list = if area == "hotbar" then view.hotbar else view.armor
		local entry = list and list[index]
		return if entry then { kind = area, index = index, entry = entry } else nil
	end
	local kind, key = string.sub(id, 1, 1), string.sub(id, 2)
	if kind == "b" then
		local entry = view.backpack[tonumber(key)]
		return entry and { kind = "backpack", index = tonumber(key), entry = entry }
	elseif kind == "i" then
		local entry = view.items[tonumber(key)]
		return entry and { kind = "item", index = tonumber(key), entry = entry }
	elseif kind == "m" then
		for _, material in view.materials do
			if material.catalogId == key then
				return { kind = "material", entry = material }
			end
		end
	end
	return nil
end

-- Cells in the picked order (each keeps its own id).
local function sorted(cells)
	local mode = VaultController.SORTS[sortIndex]
	if mode == "Name" then
		table.sort(cells, function(a, b)
			return a.name < b.name
		end)
	elseif mode == "Count" then
		table.sort(cells, function(a, b)
			return (a.item.quantity or 1) > (b.item.quantity or 1)
		end)
	end
	return cells
end

local function cellsOf(list, prefix: string)
	return sorted(InventoryModel.LobbyCells(list, prefix))
end

local function vaultFull(): boolean
	return view ~= nil and #view.items >= view.itemCapacity
end

-- The first item of the open tab, or nil.
local function firstId(): string?
	if view == nil then
		return nil
	end
	if tab == "Backpack" then
		local cells = cellsOf(view.backpack, "b")
		if cells[1] then
			return cells[1].id
		end
	end
	local cells = cellsOf(view.items, "i")
	if cells[1] == nil then
		cells = cellsOf(view.materials, "m")
	end
	return cells[1] and cells[1].id
end

local render

local function showDetail()
	local choice = entryFor(selected)
	window:SetSelected(if choice then selected else nil)
	if choice == nil then
		window:SetDetail({
			hint = if tab == "Backpack"
				then "Everything you own. Drag items to your hotbar, armour or vault, or choose one."
				else "Your vault keeps items safe. Choose one to take it into your backpack.",
		})
		return
	end
	local entry = choice.entry
	local item = { catalogId = entry.catalogId, quantity = entry.quantity, permanent = entry.permanent }
	item.qualityRoll = entry.qualityRoll
	local detail = {
		catalogId = entry.catalogId,
		name = nameOf(entry),
		text = ItemInfo.Text(item),
		rows = ItemInfo.StatRows(item),
		item = item,
	}
	if choice.kind == "backpack" then
		-- A stack picks how many to store, the same way TAKE picks how many to take.
		local quantity = if entry.instanceId then 1 else (entry.quantity or 1)
		if quantity > 1 then
			detail.amount = { min = 1, max = quantity, value = math.clamp(amount, 1, quantity), allLabel = "All" }
		end
		detail.actions = {
			{ id = "store", label = "Store", enabled = not busy },
			{
				id = "equip",
				label = if armorSlotOf(entry) then "Wear" else "Equip",
				variant = "secondary",
				enabled = not busy,
			},
		}
	elseif choice.kind == "hotbar" or choice.kind == "armor" then
		detail.text = (detail.text or "")
			.. (if choice.kind == "hotbar" then "\nOn your hotbar for the next run." else "\nWorn on the next run.")
		detail.actions = { { id = "unequip", label = "Unequip", enabled = not busy } }
	elseif choice.kind == "item" then
		detail.actions = { { id = "take", label = "Take", enabled = not busy } }
	else
		local quantity = entry.quantity or 1
		detail.amount = { min = 1, max = quantity, value = math.clamp(amount, 1, quantity), allLabel = "All" }
		detail.actions = { { id = "take", label = "Take", enabled = not busy } }
	end
	window:SetDetail(detail)
end

function render()
	if window == nil or view == nil then
		return
	end
	window:SelectTab(tab)
	window:SetTabLabel("Vault", ("Vault %d/%d"):format(#view.items, view.itemCapacity))
	if tab == "Backpack" then
		window:SetSections(InventoryModel.LobbySections(view, tab, sorted, function(index)
			return Binds.Label("Hotbar" .. index)
		end))
		window:SetToolbar({
			{ id = "sort", label = "Sort: " .. VaultController.SORTS[sortIndex] },
			{ id = "storeAll", label = "Store All", enabled = #view.backpack > 0 },
		})
	else
		window:SetSections(InventoryModel.LobbySections(view, tab, sorted))
		local tools = { { id = "sort", label = "Sort: " .. VaultController.SORTS[sortIndex] } }
		if vaultFull() then
			-- Vault upgrades are sold in the Market's Offers tab.
			table.insert(tools, { id = "upgrade", label = "More Space" })
		end
		window:SetToolbar(tools)
	end
	if entryFor(selected) == nil then
		selected = firstId()
	end
	showDetail()
end

-- Fetches the backpack and vault and draws them. `opening`: also tells of
-- material deliveries the vault had no room for (once per opening). `quiet`:
-- says nothing when the data is not loaded yet (the background read at start).
local function refresh(opening: boolean?, quiet: boolean?)
	local latest = Remotes.Invoke("VaultSnapshot")
	if type(latest) ~= "table" then
		if not quiet then
			notify("warn", "Still loading", "Your data is still loading. Try again in a moment.")
		end
		return
	end
	view = latest
	render()
	VaultController.Changed:Fire(view)
	if opening and view.overflow and #view.overflow > 0 then
		local parts = {}
		for _, lost in view.overflow do
			table.insert(parts, ("%s ×%d"):format(lost.name, lost.quantity))
		end
		notify("warn", "Vault full", "Deleted " .. table.concat(parts, ", ") .. ".")
	end
end

-- Runs a request with every action held (buttons read "…") until the new
-- snapshot is drawn, so a second press cannot act on a slot that has moved.
local function hold(fn)
	if busy then
		return
	end
	busy = true
	window:SetBusy(true)
	local ok, err = pcall(fn)
	busy = false
	window:SetBusy(false)
	refresh()
	if not ok then
		warn("VaultController: " .. tostring(err))
	end
end

-- Deposits backpack slot `index` (`quantity`, else the amount picked with the
-- stepper when it holds a stack). A material the vault cannot hold in full asks
-- first how much would be deleted (GDD §53); "deposit anyway" goes through only
-- while that slot still holds the same stack.
local function deposit(index: number, quantity: number?)
	local item = view and view.backpack[index]
	if item == nil then
		return
	end
	local name = nameOf(item)
	local owned = if item.instanceId then 1 else (item.quantity or 1)
	local store = math.clamp(quantity or amount, 1, owned)
	local overflow = nil
	hold(function()
		local ok, reason, lost = Remotes.Invoke("VaultDeposit", index, nil, nil, store)
		if ok then
			notify("info", "Stored", name .. " is safe in your vault.")
		elseif reason == "VaultWouldOverflow" and type(lost) == "number" then
			overflow = lost
		else
			refused(reason)
		end
	end)
	if overflow == nil then
		return
	end
	Kit.ConfirmDialog.Show({
		title = "Vault Nearly Full",
		text = ("Your vault can't hold all of it: %d %s would be deleted. Deposit anyway?"):format(overflow, name),
		confirmLabel = "Deposit",
		danger = true,
		onConfirm = function()
			hold(function()
				local latest = Remotes.Invoke("VaultSnapshot")
				local now = type(latest) == "table" and latest.backpack[index] or nil
				if type(now) ~= "table" or now.catalogId ~= item.catalogId or now.quantity ~= item.quantity then
					notify("warn", "Nothing stored", "Your backpack changed, so nothing was deposited.")
					return
				end
				local stored, why = Remotes.Invoke("VaultDeposit", index, item.catalogId, overflow, store)
				if stored then
					notify("info", "Stored", name .. " is in your vault.")
				else
					refused(why)
				end
			end)
		end,
	})
end

local function withdraw(choice, quantity: number?)
	local name = nameOf(choice.entry)
	hold(function()
		local ok, reason
		if choice.kind == "item" then
			ok, reason = Remotes.Invoke("VaultWithdrawItem", choice.index)
		else
			local take = math.clamp(quantity or amount, 1, choice.entry.quantity or 1)
			ok, reason = Remotes.Invoke("VaultWithdrawMaterial", choice.entry.catalogId, take)
		end
		if ok then
			notify("info", "In your backpack", name .. " goes with you on Play.")
		else
			refused(reason)
		end
	end)
end

-- STORE ALL: every backpack slot, last first so earlier indices stay put. A
-- material that would overflow is left for its own confirmation; refusals that
-- apply to every slot alike stop it at the first.
local STOP_ALL = { InTrade = true, InTransit = true, NotInLobby = true, Rejected = true }

local function storeAll()
	if view == nil then
		return
	end
	local count = #view.backpack
	hold(function()
		local stored, held, refusal = 0, 0, nil
		for index = count, 1, -1 do
			local ok, reason = Remotes.Invoke("VaultDeposit", index)
			if ok then
				stored += 1
			elseif reason == "VaultWouldOverflow" then
				held += 1
			else
				refusal = refusal or reason
				if STOP_ALL[reason] then
					break
				end
			end
		end
		local parts = { ("Stored %d."):format(stored) }
		if held > 0 then
			table.insert(parts, ("%d would overflow the vault: store those one by one."):format(held))
		end
		if refusal then
			table.insert(parts, "Some could not be stored: " .. Reasons.Text(refusal) .. ".")
		end
		notify(if refusal or held > 0 then "warn" else "info", "Store All", table.concat(parts, " "))
	end)
end

-- The lobby loadout (backpack, hotbar, worn armour) -------------------------------

-- A cell as a place: {area, key?, index?, entry?}. Areas "backpack" (key: list
-- index, nil for the end), "hotbar", "armor" (index: slot number), "vault"
-- (index, nil for an empty cell) and "material" (entry).
local function placeOf(id: string)
	if view == nil then
		return nil
	end
	local choice = entryFor(id)
	if choice then
		if choice.kind == "backpack" then
			return { area = "backpack", key = choice.index, entry = choice.entry }
		elseif choice.kind == "item" then
			return { area = "vault", index = choice.index, entry = choice.entry }
		elseif choice.kind == "material" then
			return { area = "material", entry = choice.entry }
		end
		return { area = choice.kind, index = choice.index, entry = choice.entry }
	end
	local area, number = string.match(id, "^(%a+):(%d+)$")
	if area == "hotbar" or area == "armor" then
		return { area = area, index = tonumber(number) }
	elseif string.sub(id, 1, 2) == "be" then
		return { area = "backpack" }
	elseif string.sub(id, 1, 2) == "ie" then
		return { area = "vault" }
	end
	return nil
end

local LOADOUT = { backpack = true, hotbar = true, armor = true }

-- The key LobbyMove takes for a place: a backpack index (nil: the end), a hotbar
-- slot number or an armour slot name.
local function keyOf(place)
	if place.area == "armor" then
		return ARMOR_SLOTS[place.index]
	elseif place.area == "hotbar" then
		return place.index
	end
	return place.key
end

local function backpackFull(): boolean
	return view ~= nil and #view.backpack >= (view.backpackCapacity or 50)
end

-- Whether all of a stack fits into the stacks of its type in `list` (the backpack
-- or the vault's items), so moving it there takes no slot (InventoryRules.Land).
local function mergesInto(list, entry): boolean
	return type(entry.quantity) == "number" and InventoryRules.TopUpRoom(list, entry.catalogId) >= entry.quantity
end

-- Whether the item in cell `fromId` can be dropped on cell `toId`: anything between
-- the backpack, hotbar and worn armour (armour on its own slot only; a worn piece
-- swaps only with a piece for the same slot); backpack items into the vault, and
-- vault items and materials into the backpack.
function VaultController.CanDrop(fromId: string, toId: string): boolean
	if fromId == toId then
		return false
	end
	local from, to = placeOf(fromId), placeOf(toId)
	if from == nil or to == nil or from.entry == nil then
		return false
	end
	if LOADOUT[from.area] and LOADOUT[to.area] then
		if to.area == "armor" then
			return armorSlotOf(from.entry) == ARMOR_SLOTS[to.index]
		end
		if from.area == "armor" and to.entry and armorSlotOf(to.entry) ~= ARMOR_SLOTS[from.index] then
			return false
		end
		-- The hotbar and armour take no backpack slots: the end of the backpack needs
		-- a free one, unless the backpack's stack of that type takes it all.
		if
			to.area == "backpack"
			and to.key == nil
			and from.area ~= "backpack"
			and backpackFull()
			and not mergesInto(view.backpack, from.entry)
		then
			return false
		end
		return true
	end
	if from.area == "backpack" and (to.area == "vault" or to.area == "material") then
		return ItemCatalog.IsMaterial(from.entry.catalogId) or not vaultFull() or mergesInto(view.items, from.entry)
	end
	return (from.area == "vault" or from.area == "material") and to.area == "backpack"
end

-- Moves between the backpack, hotbar and worn armour (LobbyMove).
local function relocate(from, to)
	hold(function()
		local ok, reason = Remotes.Invoke("LobbyMove", from.area, keyOf(from), to.area, keyOf(to))
		if not ok then
			refused(reason)
		end
	end)
end

function VaultController.Drop(fromId: string, toId: string)
	if busy or not VaultController.CanDrop(fromId, toId) then
		return
	end
	local from, to = placeOf(fromId), placeOf(toId)
	if from == nil or to == nil then
		return
	end
	selected = nil
	if LOADOUT[from.area] and LOADOUT[to.area] then
		relocate(from, to)
	elseif from.area == "backpack" then
		-- The whole slot goes in.
		deposit(from.key, if from.entry.instanceId then 1 else from.entry.quantity)
	elseif from.area == "vault" then
		withdraw({ kind = "item", index = from.index, entry = from.entry })
	else
		withdraw({ kind = "material", entry = from.entry }, from.entry.quantity)
	end
end

-- EQUIP / WEAR on a backpack item: onto the first free hotbar slot, or worn.
local function equip(choice)
	local slot = armorSlotOf(choice.entry)
	local to
	if slot then
		to = { area = "armor", index = table.find(ARMOR_SLOTS, slot) }
	else
		for index = 1, #(view.hotbar or {}) do
			if not view.hotbar[index] then
				to = { area = "hotbar", index = index }
				break
			end
		end
		if to == nil then
			notify("warn", "Hotbar full", "Drag the item onto a hotbar slot to swap it.")
			return
		end
	end
	relocate({ area = "backpack", key = choice.index }, to)
end

local function onAction(id: string)
	local choice = entryFor(selected)
	if choice == nil or busy then
		return
	end
	if id == "store" and choice.kind == "backpack" then
		deposit(choice.index)
	elseif id == "equip" and choice.kind == "backpack" then
		equip(choice)
	elseif id == "unequip" and (choice.kind == "hotbar" or choice.kind == "armor") then
		if backpackFull() and not mergesInto(view.backpack, choice.entry) then
			refused("BackpackFull")
			return
		end
		relocate({ area = choice.kind, index = choice.index }, { area = "backpack" })
	elseif id == "take" and (choice.kind == "item" or choice.kind == "material") then
		withdraw(choice)
	end
end

local function onToolbar(id: string)
	if busy then
		return
	end
	if id == "storeAll" then
		storeAll()
	elseif id == "sort" then
		sortIndex = sortIndex % #VaultController.SORTS + 1
		render()
	elseif id == "upgrade" then
		window:Close()
		local WalletController = require(script.Parent.WalletController) :: any
		WalletController.Open("Offers")
	end
end

local function build()
	window = InventoryWindow.new({
		tabs = {
			{ id = "Backpack", label = "Backpack", icon = "backpack", iconSelected = "backpack_white" },
			{ id = "Vault", label = "Vault", icon = "chest" },
		},
		onTab = function(id)
			tab = id
			selected = nil
			render()
		end,
		onSlot = function(id)
			if entryFor(id) == nil then
				return
			end
			selected = id
			showDetail()
		end,
		onAction = onAction,
		onAmount = function(value)
			amount = value
		end,
		onToolbar = onToolbar,
		drag = { group = "lobby", canDrop = VaultController.CanDrop, onDrop = VaultController.Drop },
	})
	VaultController.window = window
end

local function listOf(map): string
	local parts = {}
	for catalogId, quantity in map do
		table.insert(parts, ("%s ×%d"):format(ItemCatalog.NameOf(catalogId), quantity))
	end
	table.sort(parts)
	return if #parts > 0 then table.concat(parts, ", ") else "nothing"
end

-- The receipt's lines (GDD §25.4.1, §53).
local function receiptLines(receipt): { string }
	local lines = {
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
				receipt.runGeneralXPEarned or 0,
				receipt.runMasteryXPEarned or 0
			)
		)
		if (receipt.centerBonusGeneralXP or 0) > 0 or (receipt.centerBonusMasteryXP or 0) > 0 then
			table.insert(
				lines,
				("Center bonus: +%d XP · +%d mastery XP"):format(
					receipt.centerBonusGeneralXP or 0,
					receipt.centerBonusMasteryXP or 0
				)
			)
		end
	end
	if receipt.deleted and next(receipt.deleted) then
		table.insert(lines, "Deleted (no room): " .. listOf(receipt.deleted))
	end
	return lines
end

local function showReceipt(receipt)
	local where = ("Extracted at %s%s"):format(
		receipt.portal or "a portal",
		if (receipt.multiplier or 1) > 1 then " · Center bonus ×2 materials" else ""
	)
	Kit.Toast.Show({
		kind = "item",
		title = "Items Received",
		text = where,
		duration = 10,
		onPress = function()
			Kit.ConfirmDialog.Show({
				title = "Extraction Receipt",
				size = { 620, 400 },
				build = function(body, w, h)
					local lines = receiptLines(receipt)
					table.insert(lines, 1, where)
					Kit.Text.new(body, {
						name = "Receipt",
						rect = { 0, 0, w, h },
						text = table.concat(lines, "\n"),
						role = "body",
						wrap = true,
						yAlign = "Top",
					})
				end,
				confirmLabel = "Open Vault",
				cancelLabel = "Close",
				onConfirm = function()
					VaultController.Open("Vault")
				end,
			})
		end,
	})
end

-- Opens the window on `tabId` ("Backpack" or "Vault"; the last tab otherwise).
-- `gamepad` moves gamepad selection into it.
function VaultController.Open(tabId: string?, gamepad: boolean?)
	if window == nil then
		return
	end
	if tabId and table.find(VaultController.TABS, tabId) and tabId ~= tab then
		tab = tabId
		selected = nil
	end
	if view then
		render()
	end
	window:Open(gamepad)
	task.spawn(refresh, true)
end

-- Opens or closes the window (the Backpack key, the HUD's Backpack tile).
function VaultController.Toggle()
	if VaultController.IsOpen() then
		window:Close()
	else
		VaultController.Open()
	end
end

function VaultController.IsOpen(): boolean
	return window ~= nil and window:IsOpen()
end

function VaultController.Start()
	if not PlaceConfig.IsLobby() then
		return
	end
	build()
	-- Read once in the background, so the HUD hotbar can drag before the window
	-- is first opened; a few tries while the profile loads.
	task.spawn(function()
		for _ = 1, 5 do
			refresh(false, true)
			if view then
				return
			end
			task.wait(3)
		end
	end)
	Remotes.Get("ExtractionReceipt").OnClientEvent:Connect(showReceipt)
	Binds.Bind("Backpack", function(_, state, input)
		if state == Enum.UserInputState.Begin then
			if VaultController.IsOpen() then
				window:Close()
			else
				VaultController.Open(nil, input ~= nil and input.KeyCode == Enum.KeyCode.ButtonY)
			end
		end
		return Enum.ContextActionResult.Sink
	end)
end

return VaultController
