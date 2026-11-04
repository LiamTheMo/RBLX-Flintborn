-- Pure display rules for the Inventory window (docs/ui/InventoryScreen.md): which
-- cells each tab shows, in which sections, and what the category column and the
-- search let through. No Instances here, so the headless specs, the window and
-- its two controllers (VaultController in the lobby, InventoryController in a
-- run) share one definition.
--
-- The rule: the first tab (Backpack) shows everything the player has, so its
-- All category lists every item, whatever its kind; the second tab (Vault in the
-- lobby, Equipped in a run) shows one place on its own. Item slots come first
-- and empty slots only fill out the last row (at least one empty row while there
-- is room), so no section hides behind a wall of empty slots.

local GameConstants = require(script.Parent.Parent.GameConstants)
local ItemCatalog = require(script.Parent.Parent.Items.ItemCatalog)
local ItemInfo = require(script.Parent.Parent.Items.ItemInfo)

local InventoryModel = {}

InventoryModel.COLUMNS = 6
InventoryModel.ARMOR_SLOTS = { "Head", "Chest", "Legs" }

export type Item = { catalogId: string, quantity: number?, permanent: boolean?, qualityRoll: number? }
export type Cell = { id: string, item: Item?, name: string?, hotkey: string?, caption: string? }
export type Section = { id: string, title: string?, cells: { Cell }, emptyText: string? }

-- How many cells a place with `filled` items and room for `capacity` shows: the
-- items, then empties to the end of the row, or a whole empty row when the
-- items end a row, never more than the capacity.
function InventoryModel.ShownCount(filled: number, capacity: number): number
	local columns = InventoryModel.COLUMNS
	return math.max(filled, math.min(capacity, (filled // columns + 1) * columns))
end

-- The name a cell shows and searches by.
function InventoryModel.CellName(cell: Cell): string
	if cell.name then
		return cell.name
	end
	local def = cell.item and ItemCatalog.Get(cell.item.catalogId)
	return def and def.name or (cell.item and cell.item.catalogId) or ""
end

-- Whether `category` and `query` filter anything (All with no search does not).
function InventoryModel.Filtering(category: string, query: string?): boolean
	return category ~= "All" or (query or "") ~= ""
end

-- Whether a cell shows under `category` and `query`: everything (empty slots
-- too) under All with no search; otherwise only items of that category whose
-- name matches.
function InventoryModel.Visible(cell: Cell, category: string, query: string?): boolean
	if not InventoryModel.Filtering(category, query) then
		return true
	end
	return cell.item ~= nil
		and ItemInfo.InCategory(cell.item.catalogId, category)
		and ItemInfo.Matches(InventoryModel.CellName(cell), query)
end

local function itemOf(entry): Item
	return {
		catalogId = entry.catalogId,
		quantity = entry.quantity,
		permanent = entry.permanent,
		qualityRoll = entry.qualityRoll,
	}
end

local function nameOf(entry): string
	local def = ItemCatalog.Get(entry.catalogId)
	return entry.name or (def and def.name) or entry.catalogId
end

-- Lobby ---------------------------------------------------------------------------------------

-- The cells of one list of a vault snapshot: "b<index>" (backpack), "i<index>"
-- (vault item) or "m<catalogId>" (vault material).
function InventoryModel.LobbyCells(list, prefix: string): { Cell }
	local cells = {}
	for index, entry in list or {} do
		table.insert(cells, {
			id = prefix .. (if prefix == "m" then entry.catalogId else tostring(index)),
			name = nameOf(entry),
			item = itemOf(entry),
		})
	end
	return cells
end

-- `cells` followed by empty cells "<emptyPrefix><n>" up to ShownCount.
function InventoryModel.Padded(cells: { Cell }, capacity: number, emptyPrefix: string): { Cell }
	for index = #cells + 1, InventoryModel.ShownCount(#cells, capacity) do
		table.insert(cells, { id = emptyPrefix .. index })
	end
	return cells
end

local function identity(cells)
	return cells
end

-- The lobby hotbar and worn-armour sections of a VaultSnapshot view ("hotbar:i",
-- "armor:i" cells, as in a run; the snapshot's slots are `false` when empty).
-- `hotkey(i)` names hotbar slot i's key.
function InventoryModel.LobbyEquipped(view, hotkey: ((index: number) -> string?)?): { Section }
	local hotbar = {}
	for index = 1, GameConstants.HOTBAR_SLOTS do
		local entry = view.hotbar and view.hotbar[index]
		table.insert(hotbar, {
			id = InventoryModel.RunCellId("hotbar", index),
			name = if entry then nameOf(entry) else nil,
			item = if entry then itemOf(entry) else nil,
			hotkey = if hotkey then hotkey(index) else nil,
		})
	end
	local armor = {}
	for index, name in InventoryModel.ARMOR_SLOTS do
		local entry = view.armor and view.armor[index]
		table.insert(armor, {
			id = InventoryModel.RunCellId("armor", index),
			name = if entry then nameOf(entry) else nil,
			item = if entry then itemOf(entry) else nil,
			caption = name,
		})
	end
	return {
		{ id = "hotbar", title = "Hotbar", cells = hotbar },
		{ id = "armor", title = "Armour", cells = armor },
	}
end

-- The sections of the lobby window's tab `tab` ("Backpack" or "Vault") for a
-- VaultSnapshot view. `sort(cells)` orders each list (the Sort button). The
-- Backpack tab shows the lobby backpack, the lobby hotbar and worn armour (which
-- go into the run as they are and take no backpack slots), and then the whole
-- vault: everything the player owns.
function InventoryModel.LobbySections(
	view,
	tab: string,
	sort: ((cells: { Cell }) -> { Cell })?,
	hotkey: ((index: number) -> string?)?
): { Section }
	local order = sort or identity
	local backpack = order(InventoryModel.LobbyCells(view.backpack, "b"))
	local items = order(InventoryModel.LobbyCells(view.items, "i"))
	local materials = order(InventoryModel.LobbyCells(view.materials, "m"))
	local itemCount = ("%d/%d"):format(#view.items, view.itemCapacity)
	if tab == "Vault" then
		return {
			{
				id = "items",
				title = "Items " .. itemCount,
				cells = InventoryModel.Padded(items, view.itemCapacity, "ie"),
			},
			{ id = "materials", title = "Materials", cells = materials, emptyText = "No materials stored yet." },
		}
	end
	local equipped = InventoryModel.LobbyEquipped(view, hotkey)
	return {
		{
			id = "backpack",
			title = ("Backpack %d/%d"):format(#view.backpack, view.backpackCapacity),
			cells = InventoryModel.Padded(backpack, view.backpackCapacity, "be"),
		},
		equipped[1],
		equipped[2],
		{
			id = "vaultItems",
			title = "Vault Items " .. itemCount,
			cells = items,
			emptyText = "No items in your vault.",
		},
		{
			id = "vaultMaterials",
			title = "Vault Materials",
			cells = materials,
			emptyText = "No materials in your vault.",
		},
	}
end

-- Run -----------------------------------------------------------------------------------------

-- The id of a run inventory cell ("backpack:3", "hotbar:1", "armor:2").
function InventoryModel.RunCellId(area: string, index: number): string
	return area .. ":" .. index
end

-- The sections of the run window's tab `tab` ("Backpack" or "Equipped") for an
-- InventoryChanged snapshot's slots ({area, index, catalogId, ...}). `hotkey(i)`
-- names hotbar slot i's key. The Backpack tab shows the backpack (its items,
-- then the first empty slots to the end of the row), then the hotbar and the
-- worn armour: everything the player carries. The Equipped tab shows the last
-- two alone.
function InventoryModel.RunSections(slots, tab: string, hotkey: ((index: number) -> string?)?): { Section }
	local byArea = { backpack = {}, hotbar = {}, armor = {} }
	for _, slot in slots or {} do
		local area = byArea[slot.area]
		if area and type(slot.index) == "number" then
			area[slot.index] = slot
		end
	end
	local hotbar = {}
	for index = 1, GameConstants.HOTBAR_SLOTS do
		local slot = byArea.hotbar[index]
		table.insert(hotbar, {
			id = InventoryModel.RunCellId("hotbar", index),
			item = slot and itemOf(slot),
			hotkey = if hotkey then hotkey(index) else nil,
		})
	end
	local armor = {}
	for index, name in InventoryModel.ARMOR_SLOTS do
		local slot = byArea.armor[index]
		table.insert(
			armor,
			{ id = InventoryModel.RunCellId("armor", index), item = slot and itemOf(slot), caption = name }
		)
	end
	local equipped = {
		{ id = "hotbar", title = "Hotbar", cells = hotbar },
		{ id = "armor", title = "Armour", cells = armor },
	}
	if tab == "Equipped" then
		return equipped
	end
	local capacity = GameConstants.BACKPACK_SLOTS
	local filled, empty = {}, {}
	for index = 1, capacity do
		local slot = byArea.backpack[index]
		local cell = { id = InventoryModel.RunCellId("backpack", index), item = slot and itemOf(slot) }
		table.insert(if slot then filled else empty, cell)
	end
	local held = #filled
	local cells = table.clone(filled)
	for index = 1, InventoryModel.ShownCount(held, capacity) - held do
		table.insert(cells, empty[index])
	end
	return {
		{ id = "backpack", title = ("Backpack %d/%d"):format(held, capacity), cells = cells },
		equipped[1],
		equipped[2],
	}
end

return InventoryModel
