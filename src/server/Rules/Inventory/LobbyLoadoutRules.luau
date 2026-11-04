-- The lobby loadout: besides the lobby backpack (a list of up to
-- GameConstants.BACKPACK_SLOTS entries), the player keeps a 6-slot lobby hotbar
-- and three worn-armour slots, like a run's. They do not count towards the
-- backpack's slots. On Deploy every entry goes into transit tagged with its place
-- (`loadoutSlot`, InventoryRules.LoadoutPlace), so the run starts with the same
-- hotbar and worn armour (InventoryRules.FromLoadout); a rollback puts each back.
--
-- Stored on `profile.lobbyBackpack` as `hotbar` ({["1".."6"] = item}: string keys,
-- so the saved table is never an array with holes) and `armor` ({Head = item, ...}).
-- Profiles saved before these existed have neither: they read as empty, and the
-- lobby arranges them once (Arrange) so tools stay on the hotbar as before.
-- Pure functions over a profile, run inside ProfileService operations.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local GameConstants = require(ReplicatedStorage.Shared.GameConstants)
local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local InventoryRules = require(ReplicatedStorage.Shared.Inventory.InventoryRules)

local LobbyLoadoutRules = {}

LobbyLoadoutRules.Backpack = "backpack"
LobbyLoadoutRules.Hotbar = "hotbar"
LobbyLoadoutRules.Armor = "armor"
LobbyLoadoutRules.HOTBAR_SLOTS = GameConstants.HOTBAR_SLOTS
LobbyLoadoutRules.ARMOR_SLOTS = InventoryRules.ArmorSlots
LobbyLoadoutRules.BACKPACK_SLOTS = GameConstants.BACKPACK_SLOTS

local function hotbarOf(profile)
	local map = profile.lobbyBackpack.hotbar
	return if type(map) == "table" then map else {}
end

local function armorOf(profile)
	local map = profile.lobbyBackpack.armor
	return if type(map) == "table" then map else {}
end

-- The lobby hotbar's item in slot `index` (1–6), or nil.
function LobbyLoadoutRules.HotbarAt(profile, index: number)
	return hotbarOf(profile)[tostring(index)]
end

-- The worn piece in armour slot `slot` ("Head", "Chest", "Legs"), or nil.
function LobbyLoadoutRules.ArmorAt(profile, slot: string)
	return armorOf(profile)[slot]
end

-- The armour slot an item is worn in, or nil when it is not armour.
function LobbyLoadoutRules.ArmorSlotOf(item): string?
	local def = type(item) == "table" and ItemCatalog.Get(item.catalogId)
	return def and def.armor and def.armor.slot or nil
end

-- Whether this profile has its hotbar and armour yet (Arrange has run).
function LobbyLoadoutRules.Arranged(profile): boolean
	return type(profile.lobbyBackpack.hotbar) == "table" and type(profile.lobbyBackpack.armor) == "table"
end

-- First arrangement of a profile from before the lobby hotbar: the backpack items
-- a run would have put on its hotbar (ItemCatalog.PrefersHotbar, in backpack
-- order) move to the lobby hotbar, so the next run starts as runs did. Armour stays
-- in the backpack. Does nothing once arranged.
function LobbyLoadoutRules.Arrange(profile)
	if LobbyLoadoutRules.Arranged(profile) then
		return
	end
	local hotbar = {}
	local slots = profile.lobbyBackpack.slots
	local free = 1
	local index = 1
	while index <= #slots and free <= LobbyLoadoutRules.HOTBAR_SLOTS do
		local item = slots[index]
		if type(item) == "table" and ItemCatalog.PrefersHotbar(item.catalogId) then
			hotbar[tostring(free)] = table.remove(slots, index)
			free += 1
		else
			index += 1
		end
	end
	profile.lobbyBackpack.hotbar = hotbar
	profile.lobbyBackpack.armor = {}
end

-- Gives the profile empty hotbar and armour maps where it has none, moving nothing
-- (unlike Arrange, so backpack indices stay put).
local function ensureMaps(profile)
	if type(profile.lobbyBackpack.hotbar) ~= "table" then
		profile.lobbyBackpack.hotbar = {}
	end
	if type(profile.lobbyBackpack.armor) ~= "table" then
		profile.lobbyBackpack.armor = {}
	end
end

local function validKey(profile, area: string, key: any, forTarget: boolean): boolean
	if area == LobbyLoadoutRules.Backpack then
		if key == nil then
			-- Only a target may be "the end of the backpack".
			return forTarget
		end
		return type(key) == "number" and key % 1 == 0 and key >= 1 and key <= #profile.lobbyBackpack.slots
	elseif area == LobbyLoadoutRules.Hotbar then
		return type(key) == "number" and key % 1 == 0 and key >= 1 and key <= LobbyLoadoutRules.HOTBAR_SLOTS
	elseif area == LobbyLoadoutRules.Armor then
		return type(key) == "string" and table.find(LobbyLoadoutRules.ARMOR_SLOTS, key) ~= nil
	end
	return false
end

local function get(profile, area: string, key: any)
	if key == nil then
		return nil
	elseif area == LobbyLoadoutRules.Backpack then
		return profile.lobbyBackpack.slots[key]
	elseif area == LobbyLoadoutRules.Hotbar then
		return hotbarOf(profile)[tostring(key)]
	end
	return armorOf(profile)[key]
end

-- Sets a hotbar or armour place (never the backpack, whose list shifts).
local function put(profile, area: string, key: any, item)
	if area == LobbyLoadoutRules.Hotbar then
		profile.lobbyBackpack.hotbar[tostring(key)] = item
	else
		profile.lobbyBackpack.armor[key] = item
	end
end

-- Moves the item at (fromArea, fromKey) to (toArea, toKey), swapping with what is
-- there. Areas: "backpack" (key: list index; a nil target key puts it at the end),
-- "hotbar" (1–6) and "armor" (an armour slot name). Armour goes only onto its own
-- armour slot, and a worn piece swaps only with a piece for the same slot. A move
-- from the hotbar or armour to the end of the backpack needs a free backpack slot.
-- Returns (ok, reason).
function LobbyLoadoutRules.Move(profile, fromArea: any, fromKey: any, toArea: any, toKey: any): (boolean, string?)
	if not validKey(profile, fromArea, fromKey, false) or not validKey(profile, toArea, toKey, true) then
		return false, "BadRequest"
	end
	if fromArea == toArea and fromKey == toKey then
		return false, "InvalidMove"
	end
	local item = get(profile, fromArea, fromKey)
	if item == nil then
		return false, "Empty"
	end
	if toArea == LobbyLoadoutRules.Armor and LobbyLoadoutRules.ArmorSlotOf(item) ~= toKey then
		return false, if LobbyLoadoutRules.ArmorSlotOf(item) then "WrongArmorSlot" else "NotArmor"
	end
	local occupant = get(profile, toArea, toKey)
	local wornOut = fromArea == LobbyLoadoutRules.Armor
	if occupant ~= nil and wornOut and LobbyLoadoutRules.ArmorSlotOf(occupant) ~= fromKey then
		return false, "SlotTaken"
	end
	ensureMaps(profile)
	local slots = profile.lobbyBackpack.slots
	local backpack = LobbyLoadoutRules.Backpack
	if fromArea == backpack and toArea == backpack then
		if toKey == nil then
			table.insert(slots, table.remove(slots, fromKey))
		else
			slots[fromKey], slots[toKey] = slots[toKey], slots[fromKey]
		end
	elseif fromArea == backpack then
		if occupant ~= nil then
			slots[fromKey] = occupant
		else
			table.remove(slots, fromKey)
		end
		put(profile, toArea, toKey, item)
	elseif toArea == backpack then
		if toKey == nil then
			if #slots >= LobbyLoadoutRules.BACKPACK_SLOTS then
				return false, "BackpackFull"
			end
			table.insert(slots, item)
		else
			slots[toKey] = item
		end
		put(profile, fromArea, fromKey, occupant)
	else
		put(profile, toArea, toKey, item)
		put(profile, fromArea, fromKey, occupant)
	end
	return true, nil
end

-- Every lobby item as Deploy would carry it: the backpack's untagged, then the
-- hotbar's and the worn armour's tagged with their place (copies, for previews).
function LobbyLoadoutRules.Items(profile): { any }
	local items = {}
	for _, item in profile.lobbyBackpack.slots do
		table.insert(items, item)
	end
	for index = 1, LobbyLoadoutRules.HOTBAR_SLOTS do
		local item = LobbyLoadoutRules.HotbarAt(profile, index)
		if item then
			local copy = table.clone(item)
			copy.loadoutSlot = InventoryRules.LoadoutTag(LobbyLoadoutRules.Hotbar, index)
			table.insert(items, copy)
		end
	end
	for _, slot in LobbyLoadoutRules.ARMOR_SLOTS do
		local item = LobbyLoadoutRules.ArmorAt(profile, slot)
		if item then
			local copy = table.clone(item)
			copy.loadoutSlot = InventoryRules.LoadoutTag(LobbyLoadoutRules.Armor, slot)
			table.insert(items, copy)
		end
	end
	return items
end

-- Takes the hotbar and worn armour out of the profile for Deploy, each item tagged
-- with its place. Returns the tagged items.
function LobbyLoadoutRules.TakePlaced(profile): { any }
	local taken = {}
	for _, item in LobbyLoadoutRules.Items(profile) do
		if item.loadoutSlot ~= nil then
			table.insert(taken, item)
		end
	end
	if LobbyLoadoutRules.Arranged(profile) then
		profile.lobbyBackpack.hotbar = {}
		profile.lobbyBackpack.armor = {}
	end
	return taken
end

-- Puts an item that comes back from transit where it was: a tagged item to its
-- hotbar slot or armour slot when that is free, anything else to the end of the
-- backpack (as rollbacks always have, whatever its size). The tag is removed.
function LobbyLoadoutRules.Return(profile, item)
	local area, key = InventoryRules.LoadoutPlace(item.loadoutSlot)
	item.loadoutSlot = nil
	if area ~= nil then
		ensureMaps(profile)
		local fits = get(profile, area, key) == nil
			and (area ~= LobbyLoadoutRules.Armor or LobbyLoadoutRules.ArmorSlotOf(item) == key)
		if fits then
			put(profile, area, key, item)
			return
		end
	end
	table.insert(profile.lobbyBackpack.slots, item)
end

return LobbyLoadoutRules
