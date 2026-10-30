-- Lobby vault and lobby backpack (GDD §10.3, §25.2, §53) in the parchment
-- Inventory & Vault window (Hud/InventoryPanel). The Inventory and Vault tiles,
-- or the Backpack key (B by default, GDD §46), open it: the lobby backpack on
-- the left, the vault's items and materials on the right. Choose a slot, then
-- STORE (or →) puts a backpack item in the vault and TAKE (or ←) brings a vault
-- entry out; a vault material comes out in the amount picked (1, 10, 100 or all)
-- and deploys with the backpack. STORE ALL vaults the whole backpack. A material
-- deposit the vault cannot hold in full asks first how much it would delete
-- (GDD §53). The latest extraction receipt shows on arrival. Lobby place only.

local ContextActionService = game:GetService("ContextActionService")
local GuiService = game:GetService("GuiService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local InventoryPanel = require(script.Parent.Parent.Hud.InventoryPanel)
local NoticeCard = require(script.Parent.Parent.Hud.NoticeCard)
local Binds = require(script.Parent.Parent.Ui.Binds)
local Reasons = require(script.Parent.Parent.Ui.Reasons)
local Theme = require(script.Parent.Parent.Ui.Theme)

local VaultController = {}

-- Amounts the picker offers for a vault material; false means the whole stack.
VaultController.MATERIAL_STEPS = { 1, 10, 100, false }
VaultController.STEP_LABELS = { "×1", "×10", "×100", "All" }
-- Orders the sort button cycles through.
VaultController.SORTS = { "Saved", "Name", "Count" }

local player = Players.LocalPlayer
local ui = {}
local panel = nil
local view = nil
-- The chosen slot: {paneId = "left" | "right", id}; ids are "b<index>" for the
-- backpack, "i<index>" for vault items and "m<catalogId>" for vault materials.
local selected = nil
local stepIndex = 2
local sortIndex = 1
local busy = false

local CLOSE_ACTION = "FlintbornVaultClose"

local function invoke(name: string, ...)
	local ok, success, reason, detail = pcall(Remotes.Get(name).InvokeServer, Remotes.Get(name), ...)
	if not ok then
		return false, "Request failed"
	end
	return success, reason, detail
end

local function asItem(entry)
	local def = ItemCatalog.Get(entry.catalogId)
	return {
		catalogId = entry.catalogId,
		name = entry.name or (def and def.name) or entry.catalogId,
		quantity = entry.quantity,
		rarity = entry.rarity or (def and def.rarity),
		permanent = entry.permanent,
		qualityRoll = entry.qualityRoll,
	}
end

-- Entries in the picked order (each keeps its own id).
local function sorted(entries)
	local mode = VaultController.SORTS[sortIndex]
	if mode == "Name" then
		table.sort(entries, function(a, b)
			return a.item.name < b.item.name
		end)
	elseif mode == "Count" then
		table.sort(entries, function(a, b)
			return (a.item.quantity or 1) > (b.item.quantity or 1)
		end)
	end
	return entries
end

local function chosen()
	if selected == nil or view == nil then
		return nil
	end
	local kind, key = string.sub(selected.id, 1, 1), string.sub(selected.id, 2)
	if kind == "b" then
		local entry = view.backpack[tonumber(key)]
		return entry and { kind = "backpack", index = tonumber(key), entry = entry }
	elseif kind == "i" then
		local entry = view.items[tonumber(key)]
		return entry and { kind = "item", index = tonumber(key), entry = entry }
	end
	for _, material in view.materials do
		if material.catalogId == key then
			return { kind = "material", entry = material }
		end
	end
	return nil
end

local refresh

local function report(ok: boolean, reason: any, done: string)
	panel:SetStatus(if ok then done else ("Not possible: " .. Reasons.Text(reason)))
end

-- Deposits backpack slot `index`. A material the vault cannot hold in full asks
-- first how much would be deleted (GDD §53); "deposit anyway" only goes through
-- while that slot still holds the same stack.
local showChoice

-- Runs a request with every button held off until the new snapshot is drawn,
-- so a second tap cannot act on a slot that has since moved.
local function hold(fn)
	if busy then
		return
	end
	busy = true
	showChoice()
	fn()
	busy = false
	showChoice()
end

local function deposit(index: number)
	local item = view and view.backpack[index]
	if item == nil or busy then
		return
	end
	busy = true
	showChoice()
	local ok, reason, lost = invoke("VaultDeposit", index)
	busy = false
	showChoice()
	if not ok and reason == "VaultWouldOverflow" and type(lost) == "number" then
		panel:Confirm(
			("Your vault is nearly full: %d %s would be deleted. Deposit anyway?"):format(lost, item.name),
			"DEPOSIT",
			function()
				hold(function()
					local latest = invoke("VaultSnapshot")
					local now = type(latest) == "table" and latest.backpack[index] or nil
					if type(now) ~= "table" or now.catalogId ~= item.catalogId or now.quantity ~= item.quantity then
						panel:SetStatus("Your backpack changed; nothing was deposited.")
						refresh()
						return
					end
					local stored, why = invoke("VaultDeposit", index, item.catalogId, lost)
					report(stored, why, "Stored " .. item.name .. ".")
					selected = nil
					refresh()
				end)
			end
		)
		return
	end
	hold(function()
		report(ok, reason, "Stored " .. item.name .. ".")
		selected = nil
		refresh()
	end)
end

local function withdraw()
	local choice = chosen()
	if choice == nil then
		return
	end
	hold(function()
		local ok, reason
		if choice.kind == "item" then
			ok, reason = invoke("VaultWithdrawItem", choice.index)
		elseif choice.kind == "material" then
			local step = VaultController.MATERIAL_STEPS[stepIndex]
			local amount = if step then math.min(step, choice.entry.quantity) else choice.entry.quantity
			ok, reason = invoke("VaultWithdrawMaterial", choice.entry.catalogId, amount)
		end
		report(ok, reason, "Moved to your backpack; it goes with you on Play.")
		if ok then
			selected = nil
		end
		refresh()
	end)
end

-- STORE ALL: every backpack slot, last first so earlier indices stay put. A
-- material that would overflow is left for its own confirmation.
-- Refusals that apply to every slot alike: STORE ALL stops at the first.
local STOP_ALL = { InTrade = true, InTransit = true, NotInLobby = true, Rejected = true }

local function storeAll()
	if view == nil then
		return
	end
	hold(function()
		local stored, held, refusal = 0, 0, nil
		for index = #view.backpack, 1, -1 do
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
		selected = nil
		local parts = { ("Stored %d."):format(stored) }
		if held > 0 then
			table.insert(parts, ("%d would overflow the vault: store those one by one."):format(held))
		end
		if refusal then
			table.insert(parts, "Some could not be stored: " .. Reasons.Text(refusal))
		end
		panel:SetStatus(table.concat(parts, " "))
		refresh()
	end)
end

-- Shows the detail strip, buttons and picker for the current choice.
function showChoice()
	local choice = chosen()
	if choice == nil then
		selected = nil
	end
	panel:Select(selected)
	panel:SetDetail(choice and asItem(choice.entry), "Choose an item to store or take.")
	local fromVault = choice ~= nil and choice.kind ~= "backpack" and not busy
	local fromBackpack = choice ~= nil and choice.kind == "backpack" and not busy
	panel:SetActions({
		{ "TAKE", fromVault, withdraw },
		{
			"STORE",
			fromBackpack,
			function()
				deposit(choice.index)
			end,
		},
	})
	panel:SetMiddle({
		fromBackpack,
		function()
			deposit(choice.index)
		end,
	}, { fromVault, withdraw }, { "STORE\nALL", view ~= nil and #view.backpack > 0 and not busy, storeAll })
	if choice and choice.kind == "material" then
		panel:SetAmounts(VaultController.STEP_LABELS, stepIndex, function(index)
			stepIndex = index
			showChoice()
		end)
	else
		panel:SetAmounts(nil)
	end
end

-- Fetches and draws the vault. `opening`: also tells of deliveries the vault had
-- no room for (shown once per opening, so it never hides an action's result).
function refresh(opening: boolean?)
	local latest = invoke("VaultSnapshot")
	if type(latest) ~= "table" then
		panel:SetStatus("Your data is still loading.")
		return
	end
	view = latest
	local left, right = {}, {}
	for index, entry in view.backpack do
		table.insert(left, { id = "b" .. index, item = asItem(entry) })
	end
	for index, entry in view.items do
		table.insert(right, { id = "i" .. index, item = asItem(entry) })
	end
	local materials = {}
	for _, material in view.materials do
		table.insert(materials, { id = "m" .. material.catalogId, item = asItem(material) })
	end
	panel:SetHeader("left", ("INVENTORY %d/%d"):format(#view.backpack, view.backpackCapacity))
	panel:SetHeader("right", "VAULT", "pm_icon_chest", { #view.items, view.itemCapacity })
	panel:SetPane("left", { { entries = sorted(left) } })
	panel:SetPane("right", {
		{ header = "Items", entries = sorted(right) },
		{ header = "Materials", entries = sorted(materials) },
	})
	-- Material deposits the vault had no room for (GDD §53), shown for a day.
	if opening and view.overflow and #view.overflow > 0 then
		local parts = {}
		for _, lost in view.overflow do
			table.insert(parts, ("%s ×%d"):format(lost.name, lost.quantity))
		end
		panel:SetStatus("Vault full: deleted " .. table.concat(parts, ", ") .. ".")
	end
	showChoice()
end

local function close()
	ContextActionService:UnbindAction(CLOSE_ACTION)
	panel:HideConfirm()
	local focus = GuiService.SelectedObject
	if focus and focus:IsDescendantOf(panel.screen.gui) then
		GuiService.SelectedObject = nil
	end
	panel.screen:SetOpen(false)
end

local function build()
	panel = InventoryPanel.new(player:WaitForChild("PlayerGui"), {
		onClose = close,
		onSlot = function(paneId: string, entry)
			if selected and selected.paneId == paneId and selected.id == entry.id then
				selected = nil
			else
				selected = { paneId = paneId, id = entry.id }
			end
			panel:HideConfirm()
			showChoice()
		end,
		onSort = function()
			sortIndex = sortIndex % #VaultController.SORTS + 1
			panel:SetStatus("Sorted by " .. string.lower(VaultController.SORTS[sortIndex]) .. ".")
			refresh()
		end,
	})
	panel:SetTitle("INVENTORY & VAULT")
	panel.screen:Watch()

	-- In the shared top-centre column with the other banners.
	ui.receipt = NoticeCard.new(Theme.TopStack(), {
		name = "Receipt",
		width = 480,
		layoutOrder = Theme.TopOrder.Receipt,
		title = "Extraction receipt",
		onPress = function()
			ui.receipt:Hide()
		end,
	})
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
	ui.receipt:Show(table.concat(lines, "\n") .. "\n\nTap to dismiss.")
end

-- Opens or closes the window (the Backpack key, the Inventory and Vault tiles).
function VaultController.Toggle()
	if panel.screen:IsOpen() then
		close()
		return
	end
	selected = nil
	panel:SetStatus("")
	panel:HideConfirm()
	panel.screen:SetOpen(true)
	ContextActionService:BindAction(CLOSE_ACTION, function(_, state)
		if state == Enum.UserInputState.Begin then
			if panel:IsConfirming() then
				panel:HideConfirm()
			else
				close()
			end
		end
		return Enum.ContextActionResult.Sink
	end, false, Enum.KeyCode.ButtonB)
	if GuiService.SelectedObject ~= nil or UserInputService.GamepadEnabled then
		GuiService.SelectedObject = panel.tabs.All.button
	end
	task.spawn(refresh, true)
end

function VaultController.IsOpen(): boolean
	return panel ~= nil and panel.screen:IsOpen()
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
