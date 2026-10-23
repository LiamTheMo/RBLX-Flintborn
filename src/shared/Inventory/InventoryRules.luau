-- Fixed 9-slot hotbar and 50-slot backpack (GDD §22.1.1, Q108, Q126–128). Every
-- stackable type (materials, ammo, consumables) lives in ONE slot with one
-- quantity; tools, weapons and armor are unique instances in their own slots and
-- never merge. Three equipped armor slots (Head, Chest, Legs/Boots; Q101) hold
-- carried armor that counts toward EHP. Pure functions over an inventory table,
-- shared with specs.
--
-- A stack's optional `fromLobby` counts the units of it that were deployed from
-- the lobby, which the Center never doubles (GDD §9.3). The count travels with the
-- units through every move, split, merge, drop, body, chest and pickup, so handing
-- deployed materials to someone else never makes them doublable. Spending takes
-- gathered units first, and the count never exceeds the stack.

local GameConstants = require(script.Parent.Parent.GameConstants)
local ItemCatalog = require(script.Parent.Parent.Items.ItemCatalog)

local InventoryRules = {}

InventoryRules.Hotbar = "hotbar"
InventoryRules.Backpack = "backpack"

local SIZES = {
	hotbar = GameConstants.HOTBAR_SLOTS,
	backpack = GameConstants.BACKPACK_SLOTS,
}

export type Stack = { catalogId: string, quantity: number, fromLobby: number? }
export type Inventory = { hotbar: { [number]: any }, backpack: { [number]: any }, armor: { [string]: any } }

InventoryRules.ArmorSlots = { "Head", "Chest", "Legs" }

function InventoryRules.New(): Inventory
	return { hotbar = {}, backpack = {}, armor = {} }
end

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

-- Units of a stack that were deployed from the lobby: a whole number from 0 to its
-- quantity, whatever the stored field holds.
function InventoryRules.FromLobby(item): number
	local quantity, tagged = item.quantity, item.fromLobby
	if type(quantity) ~= "number" or type(tagged) ~= "number" or tagged ~= tagged or quantity ~= quantity then
		return 0
	end
	return math.floor(math.clamp(tagged, 0, math.max(quantity, 0)))
end

local function setFromLobby(stack, amount: number)
	stack.fromLobby = if amount > 0 then amount else nil
end

-- Tags every stack in `items` as wholly deployed from the lobby (a run's start).
function InventoryRules.MarkFromLobby(items)
	for _, item in items do
		if item.instanceId == nil then
			item.fromLobby = nil
			if type(item.quantity) == "number" and item.quantity > 0 then
				setFromLobby(item, item.quantity)
			end
		end
	end
	return items
end

-- Packs a deployed loadout into a run inventory, tagging every stack as lobby
-- units. Returns (inventory, leftovers). The single definition of what enters a
-- run, so crash recovery restores exactly what the run started with.
function InventoryRules.Deploy(items)
	return InventoryRules.FromItems(InventoryRules.MarkFromLobby(items))
end

-- Moves `amount` units of the stack `item` onto `stack`, deployed units first.
-- `item` is left as it was; KeepRemainder gives it what stays behind.
function InventoryRules.Merge(stack, item, amount: number)
	local tagged = InventoryRules.FromLobby(stack) + math.min(InventoryRules.FromLobby(item), amount)
	stack.quantity += amount
	setFromLobby(stack, math.min(tagged, stack.quantity))
end

-- Shrinks a stack to the `remaining` units that did not fit elsewhere, keeping
-- whatever deployed units Merge did not move.
function InventoryRules.KeepRemainder(item, remaining: number)
	local moved = (item.quantity or 0) - remaining
	local tagged = math.max(0, InventoryRules.FromLobby(item) - moved)
	item.quantity = remaining
	setFromLobby(item, math.min(tagged, remaining))
end

-- Adds a stack ({catalogId, quantity, fromLobby?}) or a unique instance record.
-- Returns how much did not fit (0 when everything was added; 1 for a unique item
-- that did not).
function InventoryRules.Add(inventory: Inventory, item): number
	local cap = ItemCatalog.StackCap(item.catalogId)
	if item.instanceId ~= nil or cap == nil then
		local area, index = firstEmpty(inventory, ItemCatalog.PrefersHotbar(item.catalogId))
		if area == nil then
			return 1
		end
		inventory[area][index] = item
		return 0
	end
	local quantity = item.quantity or 0
	if quantity <= 0 then
		return 0
	end
	local area, index = findStack(inventory, item.catalogId)
	if area == nil then
		area, index = firstEmpty(inventory, ItemCatalog.PrefersHotbar(item.catalogId))
		if area == nil then
			return quantity
		end
		inventory[area][index] = { catalogId = item.catalogId, quantity = 0 }
	end
	local stack = inventory[area][index]
	local added = math.min(quantity, cap - stack.quantity)
	InventoryRules.Merge(stack, item, added)
	return quantity - added
end

function InventoryRules.Count(inventory: Inventory, catalogId: string): number
	local area, index = findStack(inventory, catalogId)
	return area and inventory[area][index].quantity or 0
end

-- Removes `quantity` of a stackable type, all or nothing.
function InventoryRules.Remove(inventory: Inventory, catalogId: string, quantity: number): boolean
	local area, index = findStack(inventory, catalogId)
	if area == nil or quantity <= 0 then
		return false
	end
	local stack = inventory[area][index]
	if stack.quantity < quantity then
		return false
	end
	local tagged = InventoryRules.FromLobby(stack)
	stack.quantity -= quantity
	setFromLobby(stack, math.min(tagged, stack.quantity))
	if stack.quantity == 0 then
		inventory[area][index] = nil
	end
	return true
end

-- Removes several stackable types at once, all or nothing ({catalogId = quantity}).
function InventoryRules.RemoveAll(inventory: Inventory, costs: { [string]: number }): boolean
	for catalogId, quantity in costs do
		if InventoryRules.Count(inventory, catalogId) < quantity then
			return false
		end
	end
	for catalogId, quantity in costs do
		InventoryRules.Remove(inventory, catalogId, quantity)
	end
	return true
end

-- RemoveAll that hands back what it removed, as stacks keeping their deployed
-- units (gathered units go first), so an offering that spills again is still
-- tagged. Returns nil, changing nothing, when anything is short.
function InventoryRules.TakeAll(inventory: Inventory, costs: { [string]: number })
	for catalogId, quantity in costs do
		if InventoryRules.Count(inventory, catalogId) < quantity then
			return nil
		end
	end
	local taken = {}
	for catalogId, quantity in costs do
		local area, index = findStack(inventory, catalogId)
		local source = area and inventory[area][index]
		local stack = { catalogId = catalogId, quantity = quantity }
		if source then
			setFromLobby(stack, math.max(0, InventoryRules.FromLobby(source) - (source.quantity - quantity)))
		end
		InventoryRules.Remove(inventory, catalogId, quantity)
		table.insert(taken, stack)
	end
	return taken
end

function InventoryRules.FindInstance(inventory: Inventory, instanceId: string)
	for _, area in { "hotbar", "backpack" } do
		for index = 1, SIZES[area] do
			local entry = inventory[area][index]
			if entry and entry.instanceId == instanceId then
				return area, index
			end
		end
	end
	return nil, nil
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
-- of it fits under the cap, otherwise it takes a slot of its own. Returns false
-- when there is no room, changing nothing.
function InventoryRules.Store(slots, item, maxSlots: number): boolean
	local cap = ItemCatalog.StackCap(item.catalogId)
	if item.instanceId == nil and cap then
		for _, slot in slots do
			if slot.instanceId == nil and slot.catalogId == item.catalogId and slot.quantity + item.quantity <= cap then
				InventoryRules.Merge(slot, item, item.quantity)
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

-- Builds an inventory from a flat list. Returns (inventory, items that did not fit);
-- every leftover keeps its full record, so callers can return it intact.
function InventoryRules.FromItems(items): (Inventory, { any })
	local inventory = InventoryRules.New()
	local leftovers = {}
	for _, item in items do
		local copy = table.clone(item)
		local remaining = InventoryRules.Add(inventory, copy)
		if remaining > 0 then
			if copy.instanceId ~= nil or ItemCatalog.StackCap(copy.catalogId) == nil then
				table.insert(leftovers, copy)
			else
				local rest = { catalogId = copy.catalogId, quantity = copy.quantity, fromLobby = copy.fromLobby }
				InventoryRules.KeepRemainder(rest, remaining)
				table.insert(leftovers, rest)
			end
		end
	end
	return inventory, leftovers
end

return InventoryRules
