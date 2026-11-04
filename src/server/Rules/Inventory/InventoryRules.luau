-- Server half of Shared.Inventory.InventoryRules: what only the server uses. Everything in
-- ReplicatedStorage is downloaded to every player, so the shared module keeps
-- only what clients need; this one clones it and adds the rest, and server code
-- requires this module.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local GameConstants = require(ReplicatedStorage.Shared.GameConstants)
local ItemCatalog = require(script.Parent.Parent.Items.ItemCatalog)
local SharedInventoryRules = require(ReplicatedStorage.Shared.Inventory.InventoryRules)

type Inventory = SharedInventoryRules.Inventory

local InventoryRules = table.clone(SharedInventoryRules)

InventoryRules.Backpack = "backpack"

local SIZES = {
	hotbar = GameConstants.HOTBAR_SLOTS,
	backpack = GameConstants.BACKPACK_SLOTS,
}

function InventoryRules.Size(area: string): number?
	return SIZES[area]
end

function InventoryRules.At(inventory: Inventory, area: string, index: number)
	local slots = inventory[area]
	return slots and slots[index] or nil
end

local function isStack(entry): boolean
	return entry.instanceId == nil
end

-- Tags every material stack among `items` as carried in whole: what Play takes out
-- of the lobby (GDD §53). Unique items and other stackables are left as they are.
function InventoryRules.MarkCarried(items)
	for _, item in items do
		if type(item) == "table" and item.instanceId == nil and ItemCatalog.IsMaterial(item.catalogId) then
			InventoryRules.SetCarried(item, if type(item.quantity) == "number" then item.quantity else 0)
		end
	end
	return items
end

-- A whole slot number inside the area (rejects NaN, 0, negatives and fractions).
local function validSlot(area: string, index: any): boolean
	local size = SIZES[area]
	return size ~= nil and type(index) == "number" and index % 1 == 0 and index >= 1 and index <= size
end

-- (area, index) of the slot holding a stackable type, if any.
local function findStack(inventory: Inventory, catalogId: string)
	for _, area in { "hotbar", "backpack" } do
		for index = 1, SIZES[area] do
			local entry = inventory[area][index]
			if entry and isStack(entry) and entry.catalogId == catalogId then
				return area, index
			end
		end
	end
	return nil, nil
end

local function firstEmpty(inventory: Inventory, preferHotbar: boolean)
	local order = if preferHotbar then { "hotbar", "backpack" } else { "backpack", "hotbar" }
	for _, area in order do
		for index = 1, SIZES[area] do
			if inventory[area][index] == nil then
				return area, index
			end
		end
	end
	return nil, nil
end

function InventoryRules.Count(inventory: Inventory, catalogId: string): number
	local area, index = findStack(inventory, catalogId)
	return area and inventory[area][index].quantity or 0
end

-- Removes `quantity` of a stackable type, all or nothing. Carried units go first,
-- so the gathered rest stays eligible for the Center bonus (GDD §53). Returns
-- (ok, how many of the removed units were carried).
function InventoryRules.Remove(inventory: Inventory, catalogId: string, quantity: number): (boolean, number)
	local area, index = findStack(inventory, catalogId)
	if area == nil or quantity <= 0 then
		return false, 0
	end
	local stack = inventory[area][index]
	if stack.quantity < quantity then
		return false, 0
	end
	local carried = InventoryRules.Carried(stack)
	local used = math.min(carried, quantity)
	stack.quantity -= quantity
	if stack.quantity == 0 then
		inventory[area][index] = nil
	else
		InventoryRules.SetCarried(stack, carried - used)
	end
	return true, used
end

-- Removes several stackable types at once, all or nothing ({catalogId = quantity}).
-- Returns (ok, how many of the removed units were carried, over all types).
function InventoryRules.RemoveAll(inventory: Inventory, costs: { [string]: number }): (boolean, number)
	for catalogId, quantity in costs do
		if InventoryRules.Count(inventory, catalogId) < quantity then
			return false, 0
		end
	end
	local carried = 0
	for catalogId, quantity in costs do
		local _, used = InventoryRules.Remove(inventory, catalogId, quantity)
		carried += used
	end
	return true, carried
end

-- RemoveAll that hands back what it removed as stacks, so an interrupted ritual
-- can spill exactly its offering. Returns nil, changing nothing, when anything is
-- short.
function InventoryRules.TakeAll(inventory: Inventory, costs: { [string]: number })
	for catalogId, quantity in costs do
		if InventoryRules.Count(inventory, catalogId) < quantity then
			return nil
		end
	end
	local taken = {}
	for catalogId, quantity in costs do
		local _, used = InventoryRules.Remove(inventory, catalogId, quantity)
		local stack = { catalogId = catalogId, quantity = quantity }
		InventoryRules.SetCarried(stack, used)
		table.insert(taken, stack)
	end
	return taken
end

-- Removes and returns the entry in a hotbar or backpack slot, or nil.
function InventoryRules.TakeAt(inventory: Inventory, area: string, index: number)
	if not validSlot(area, index) then
		return nil
	end
	local entry = inventory[area][index]
	inventory[area][index] = nil
	return entry
end

-- Swaps two slots (either may be empty). Returns false for an invalid slot.
function InventoryRules.Move(inventory: Inventory, fromArea: string, fromIndex: number, toArea: string, toIndex: number)
	if not validSlot(fromArea, fromIndex) or not validSlot(toArea, toIndex) then
		return false
	end
	local moving = inventory[fromArea][fromIndex]
	if moving == nil then
		return false
	end
	inventory[fromArea][fromIndex] = inventory[toArea][toIndex]
	inventory[toArea][toIndex] = moving
	return true
end

-- Equips the armor piece at (area, index) into its slot. Any piece already worn
-- there swaps back into the same inventory slot.
function InventoryRules.EquipArmor(inventory: Inventory, area: string, index: number): boolean
	if not validSlot(area, index) then
		return false
	end
	local entry = inventory[area][index]
	local def = entry and ItemCatalog.Get(entry.catalogId)
	if def == nil or def.armor == nil then
		return false
	end
	local slot = def.armor.slot
	inventory[area][index] = inventory.armor[slot]
	inventory.armor[slot] = entry
	return true
end

-- Moves a worn piece back into the first empty slot (backpack first).
function InventoryRules.UnequipArmor(inventory: Inventory, slot: string): boolean
	local entry = inventory.armor[slot]
	if entry == nil then
		return false
	end
	local area, index = firstEmpty(inventory, false)
	if area == nil then
		return false
	end
	inventory[area][index] = entry
	inventory.armor[slot] = nil
	return true
end

-- Takes the worn piece in `slot` off into (area, index): onto an empty slot, or
-- swapped with a piece for the same armour slot, which is then worn. Returns
-- false for anything else (an invalid slot, nothing worn, or an item there that
-- cannot be worn in its place).
function InventoryRules.UnequipArmorTo(inventory: Inventory, slot: string, area: string, index: number): boolean
	local entry = inventory.armor[slot]
	if entry == nil or not validSlot(area, index) then
		return false
	end
	local occupant = inventory[area][index]
	if occupant ~= nil then
		local def = ItemCatalog.Get(occupant.catalogId)
		if def == nil or def.armor == nil or def.armor.slot ~= slot then
			return false
		end
	end
	inventory.armor[slot] = occupant
	inventory[area][index] = entry
	return true
end

-- Every entry as a flat list (for departure, extraction and display), worn armor included.
function InventoryRules.Items(inventory: Inventory)
	local items = {}
	for _, area in { "hotbar", "backpack" } do
		for index = 1, SIZES[area] do
			local entry = inventory[area][index]
			if entry then
				table.insert(items, entry)
			end
		end
	end
	for _, slot in InventoryRules.ArmorSlots do
		if inventory.armor[slot] then
			table.insert(items, inventory.armor[slot])
		end
	end
	return items
end

-- Puts an item into a list of container slots (a storage chest) holding at most
-- `maxSlots` entries: a stack joins an existing stack of its type when the whole
-- of it fits under the cap (adding up their carried counts), otherwise it takes a
-- slot of its own. Returns false when there is no room, changing nothing.
function InventoryRules.Store(slots, item, maxSlots: number): boolean
	local cap = ItemCatalog.StackCap(item.catalogId)
	if item.instanceId == nil and cap then
		for _, slot in slots do
			if slot.instanceId == nil and slot.catalogId == item.catalogId and slot.quantity + item.quantity <= cap then
				local carried = InventoryRules.Carried(slot) + InventoryRules.Carried(item)
				slot.quantity += item.quantity
				InventoryRules.SetCarried(slot, carried)
				return true
			end
		end
	end
	if #slots >= maxSlots then
		return false
	end
	table.insert(slots, item)
	return true
end

-- Merges the part-full stacks of one type in a list of slots (lists saved before
-- Land merged them), keeping the order of first appearance. Unique items stay as
-- they are. Returns how many entries were merged away.
function InventoryRules.Consolidate(slots): number
	if type(slots) ~= "table" then
		return 0
	end
	local before = #slots
	local merged = {}
	for _, item in slots do
		if type(item) == "table" and type(item.catalogId) == "string" then
			InventoryRules.Land(merged, item)
		else
			table.insert(merged, item)
		end
	end
	table.clear(slots)
	for index, item in merged do
		slots[index] = item
	end
	return before - #slots
end

function InventoryRules.LoadoutTag(area: string, key: any): string
	return area .. ":" .. tostring(key)
end

-- Builds an inventory from a flat list. Returns (inventory, items that did not fit);
-- every leftover keeps its full record (a stack's carried units included), so
-- callers can return it intact.
function InventoryRules.FromItems(items): (Inventory, { any })
	local inventory = InventoryRules.New()
	local leftovers = {}
	for _, item in items do
		local copy = table.clone(item)
		local remaining, carried = InventoryRules.Add(inventory, copy)
		if remaining > 0 then
			if copy.instanceId ~= nil or ItemCatalog.StackCap(copy.catalogId) == nil then
				table.insert(leftovers, copy)
			else
				local leftover = { catalogId = copy.catalogId, quantity = remaining }
				InventoryRules.SetCarried(leftover, carried)
				table.insert(leftovers, leftover)
			end
		end
	end
	return inventory, leftovers
end

return InventoryRules
