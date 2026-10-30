-- Lobby vault and lobby backpack (GDD §10.3, §25.2, §53) in the Inventory window
-- (Hud/Screens/InventoryWindow, docs/ui/InventoryScreen.md). The Backpack tile,
-- the Backpack key (B by default, Y on a gamepad, GDD §46) or Open(tab) opens
-- it on the Backpack or the Vault tab. Choose a slot to see it in the detail
-- card: STORE puts a backpack item in the vault, TAKE brings a vault entry out
-- (a vault material in the amount picked with the stepper) and it deploys with
-- the backpack on the next Play. STORE ALL vaults the whole backpack; SORT cycles
-- the order. A material deposit the vault cannot hold in full asks first how
-- much it would delete (GDD §53). The latest extraction receipt arrives as an
-- "Items Received" toast that opens the full receipt. Lobby place only.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
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

local function invoke(name: string, ...)
	local ok, success, reason, detail = pcall(Remotes.Get(name).InvokeServer, Remotes.Get(name), ...)
	if not ok then
		return false, "Request failed"
	end
	return success, reason, detail
end

local function notify(kind: string, title: string, text: string?)
	Kit.Toast.Show({ kind = kind, title = title, text = text, duration = if kind == "warn" then 5 else 3 })
end

local function refused(reason: any)
	notify("warn", "Not possible", (Reasons.Text(reason):gsub("^%l", string.upper)) .. ".")
end

local function nameOf(entry): string
	local def = ItemCatalog.Get(entry.catalogId)
	return entry.name or (def and def.name) or entry.catalogId
end

-- The entry behind a cell id: {kind, index?, entry}, or nil.
local function entryFor(id: string?)
	if id == nil or view == nil then
		return nil
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
	local cells = {}
	for index, entry in list do
		table.insert(cells, {
			id = prefix .. (if prefix == "m" then entry.catalogId else index),
			name = nameOf(entry),
			item = {
				catalogId = entry.catalogId,
				quantity = entry.quantity,
				permanent = entry.permanent,
				qualityRoll = entry.qualityRoll,
			},
		})
	end
	return sorted(cells)
end

-- Empty slots up to `capacity` after the filled ones.
local function padded(cells, capacity: number, prefix: string)
	for index = #cells + 1, capacity do
		table.insert(cells, { id = prefix .. index })
	end
	return cells
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
		return cells[1] and cells[1].id
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
				then "Your lobby backpack goes with you on Play. Choose an item to store it in your vault."
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
		detail.actions = { { id = "store", label = "Store", enabled = not busy } }
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
		window:SetSections({
			{
				id = "backpack",
				cells = padded(cellsOf(view.backpack, "b"), view.backpackCapacity, "be"),
				emptyText = "Your lobby backpack is empty.",
			},
		})
		window:SetToolbar({
			{ id = "sort", label = "Sort: " .. VaultController.SORTS[sortIndex] },
			{ id = "storeAll", label = "Store All", enabled = #view.backpack > 0 },
		})
	else
		window:SetSections({
			{
				id = "items",
				title = ("Items %d/%d"):format(#view.items, view.itemCapacity),
				cells = padded(cellsOf(view.items, "i"), view.itemCapacity, "ie"),
			},
			{
				id = "materials",
				title = "Materials",
				cells = cellsOf(view.materials, "m"),
				emptyText = "No materials stored yet.",
			},
		})
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
-- material deliveries the vault had no room for (once per opening).
local function refresh(opening: boolean?)
	local latest = invoke("VaultSnapshot")
	if type(latest) ~= "table" then
		notify("warn", "Still loading", "Your data is still loading. Try again in a moment.")
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

-- Deposits backpack slot `index`. A material the vault cannot hold in full asks
-- first how much would be deleted (GDD §53); "deposit anyway" goes through only
-- while that slot still holds the same stack.
local function deposit(index: number)
	local item = view and view.backpack[index]
	if item == nil then
		return
	end
	local name = nameOf(item)
	local overflow = nil
	hold(function()
		local ok, reason, lost = invoke("VaultDeposit", index)
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
				local latest = invoke("VaultSnapshot")
				local now = type(latest) == "table" and latest.backpack[index] or nil
				if type(now) ~= "table" or now.catalogId ~= item.catalogId or now.quantity ~= item.quantity then
					notify("warn", "Nothing stored", "Your backpack changed, so nothing was deposited.")
					return
				end
				local stored, why = invoke("VaultDeposit", index, item.catalogId, overflow)
				if stored then
					notify("info", "Stored", name .. " is in your vault.")
				else
					refused(why)
				end
			end)
		end,
	})
end

local function withdraw(choice)
	local name = nameOf(choice.entry)
	hold(function()
		local ok, reason
		if choice.kind == "item" then
			ok, reason = invoke("VaultWithdrawItem", choice.index)
		else
			local take = math.clamp(amount, 1, choice.entry.quantity or 1)
			ok, reason = invoke("VaultWithdrawMaterial", choice.entry.catalogId, take)
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
			local ok, reason = invoke("VaultDeposit", index)
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

local function onAction(id: string)
	local choice = entryFor(selected)
	if choice == nil or busy then
		return
	end
	if id == "store" and choice.kind == "backpack" then
		deposit(choice.index)
	elseif id == "take" and choice.kind ~= "backpack" then
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
	})
	VaultController.window = window
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
