-- The authoritative run inventory (GDD §22.1.1, §56): a fixed 6-slot hotbar and 50-slot
-- backpack held in server memory while a player is in a run. Every gain, loss,
-- move and equip goes through here and is replicated to the owner as a snapshot.
-- World place only.

local HttpService = game:GetService("HttpService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local InventoryRules = require(ReplicatedStorage.Shared.Inventory.InventoryRules)
local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Signal = require(ReplicatedStorage.Shared.Core.Signal)
local ProfileService = require(script.Parent.ProfileService)
local WorldAdmissionService = require(script.Parent.WorldAdmissionService)

local InventoryService = {}

-- Fires (player) after any change to a run inventory is published.
InventoryService.Changed = Signal.new()

local entries = {}

local function snapshot(entry)
	local slots = {}
	for _, area in { InventoryRules.Hotbar, InventoryRules.Backpack } do
		for index = 1, InventoryRules.Size(area) do
			local item = entry.inventory[area][index]
			if item then
				table.insert(slots, {
					area = area,
					index = index,
					catalogId = item.catalogId,
					quantity = item.quantity,
					instanceId = item.instanceId,
					qualityRoll = item.qualityRoll,
					permanent = item.permanent,
				})
			end
		end
	end
	for index, slot in InventoryRules.ArmorSlots do
		local item = entry.inventory.armor[slot]
		if item then
			table.insert(slots, {
				area = "armor",
				index = index,
				slot = slot,
				catalogId = item.catalogId,
				instanceId = item.instanceId,
				qualityRoll = item.qualityRoll,
				permanent = item.permanent,
			})
		end
	end
	return { slots = slots, equipped = entry.equipped }
end

function InventoryService.Publish(player: Player)
	local entry = entries[player]
	if entry and player.Parent then
		Remotes.Get("InventoryChanged"):FireClient(player, snapshot(entry))
		local equipped = entry.equipped and entry.inventory.hotbar[entry.equipped]
		player:SetAttribute("EquippedItem", equipped and equipped.catalogId or nil)
		InventoryService.Changed:Fire(player)
	end
end

function InventoryService.Notify(player: Player, message: string)
	if player.Parent then
		Remotes.Get("Notify"):FireClient(player, message)
	end
end

function InventoryService.Get(player: Player)
	local entry = entries[player]
	return entry and entry.inventory or nil
end

-- Adds a stack or unique instance. Returns how much did not fit and how many of
-- those units are carried in (InventoryRules.Add), so a partly taken drop, body
-- or chest stack keeps its share of the carried tag (GDD §53).
function InventoryService.Add(player: Player, item): (number, number)
	local entry = entries[player]
	if entry == nil then
		return item.quantity or 1, InventoryRules.Carried(item)
	end
	local remaining, carried = InventoryRules.Add(entry.inventory, item)
	InventoryService.Publish(player)
	return remaining, carried
end

function InventoryService.Count(player: Player, catalogId: string): number
	local inventory = InventoryService.Get(player)
	return inventory and InventoryRules.Count(inventory, catalogId) or 0
end

-- Removes stackable items, all or nothing, carried units first. Returns (ok, how
-- many of the removed units were carried in).
function InventoryService.RemoveAll(player: Player, costs: { [string]: number }): (boolean, number)
	local inventory = InventoryService.Get(player)
	if inventory == nil then
		return false, 0
	end
	local ok, carried = InventoryRules.RemoveAll(inventory, costs)
	if not ok then
		return false, 0
	end
	InventoryService.Publish(player)
	return true, carried
end

-- Removes stackable items, all or nothing, and returns them as stacks (or nil).
function InventoryService.TakeAll(player: Player, costs: { [string]: number })
	local inventory = InventoryService.Get(player)
	local taken = inventory and InventoryRules.TakeAll(inventory, costs)
	if taken then
		InventoryService.Publish(player)
	end
	return taken
end

-- Removes and returns the entry in a hotbar or backpack slot, unequipping it.
function InventoryService.TakeAt(player: Player, area: string, index: number)
	local entry = entries[player]
	local item = entry and InventoryRules.TakeAt(entry.inventory, area, index)
	if item == nil then
		return nil
	end
	if area == InventoryRules.Hotbar and entry.equipped == index then
		entry.equipped = nil
	end
	InventoryService.Publish(player)
	return item
end

-- The item in the equipped hotbar slot, or nil.
function InventoryService.Equipped(player: Player)
	local entry = entries[player]
	return entry and entry.equipped and entry.inventory.hotbar[entry.equipped] or nil
end

-- The equipped item's tool definition ({kind, tier}) or nil for bare hands.
function InventoryService.EquippedTool(player: Player)
	local item = InventoryService.Equipped(player)
	local def = item and ItemCatalog.Get(item.catalogId)
	return def and def.tool or nil
end

-- Worn armor as {tier, slot, qualityRoll} pieces for the EHP calculation.
function InventoryService.ArmorPieces(player: Player)
	local inventory = InventoryService.Get(player)
	local pieces = {}
	if inventory then
		for _, slot in InventoryRules.ArmorSlots do
			local item = inventory.armor[slot]
			local def = item and ItemCatalog.Get(item.catalogId)
			if def and def.armor then
				table.insert(pieces, { tier = def.armor.tier, slot = def.armor.slot, qualityRoll = item.qualityRoll })
			end
		end
	end
	return pieces
end

-- Every carried item as a flat list (departure and extraction).
function InventoryService.Items(player: Player)
	local inventory = InventoryService.Get(player)
	return inventory and InventoryRules.Items(inventory) or {}
end

-- Items that do not fit the run inventory (a lobby backpack over 59 entries,
-- Permanent items, trades, crash recovery or maintenance escrow on top) stay in
-- the lobby backpack instead of entering the run. Nothing is ever deleted here.
local function keepInLobby(player: Player, leftovers)
	local ok, err = ProfileService.RunOperation(
		player,
		"overflow:" .. HttpService:GenerateGUID(false),
		"RunOverflow",
		function(profile)
			for _, item in leftovers do
				if item.instanceId then
					item.location = "LobbyBackpack"
				end
				-- The next Play tags what it takes from the lobby afresh (GDD §53).
				item.carried = nil
				table.insert(profile.lobbyBackpack.slots, item)
			end
		end
	)
	if not ok then
		warn(("[InventoryService] Could not return %d items for %s: %s"):format(#leftovers, player.Name, tostring(err)))
		return
	end
	-- Saved at once: the consumed loadout is already saved out of the profile and
	-- these items are in no run checkpoint, so a crash before the save loses them.
	task.spawn(ProfileService.SaveNow, player)
	InventoryService.Notify(
		player,
		("%d item stack(s) did not fit and stayed in your lobby backpack."):format(#leftovers)
	)
end

local function startRun(player: Player, _character, items)
	local inventory, leftovers = InventoryRules.FromItems(items or {})
	entries[player] = { inventory = inventory, equipped = nil }
	if #leftovers > 0 then
		keepInLobby(player, leftovers)
	end
	InventoryService.Publish(player)
end

local function move(player: Player, fromArea: any, fromIndex: any, toArea: any, toIndex: any)
	local entry = entries[player]
	if entry == nil then
		return false, "NotInRun"
	end
	if type(fromArea) ~= "string" or type(toArea) ~= "string" then
		return false, "BadRequest"
	end
	if type(fromIndex) ~= "number" or type(toIndex) ~= "number" then
		return false, "BadRequest"
	end
	if not InventoryRules.Move(entry.inventory, fromArea, fromIndex, toArea, toIndex) then
		return false, "InvalidMove"
	end
	-- Keep the equipped slot pointing at whatever is now there.
	InventoryService.Publish(player)
	return true, nil
end

local function equip(player: Player, index: any)
	local entry = entries[player]
	if entry == nil then
		return false, "NotInRun"
	end
	if index == nil then
		entry.equipped = nil
	elseif type(index) == "number" and index % 1 == 0 and index >= 1 and index <= InventoryRules.Size("hotbar") then
		entry.equipped = if entry.equipped == index then nil else index
	else
		return false, "BadRequest"
	end
	InventoryService.Publish(player)
	return true, nil
end

function InventoryService.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	WorldAdmissionService.RunStarted:Connect(startRun)
	WorldAdmissionService.RunEnded:Connect(function(player)
		entries[player] = nil
		if player.Parent then
			Remotes.Get("InventoryChanged"):FireClient(player, { slots = {}, equipped = nil })
		end
	end)
	-- No PlayerRemoving cleanup here: an at-risk departure fires ActiveDeparture
	-- (which still needs the inventory) and then RunEnded, which clears it.
	Remotes.Handle("MoveItem", move)
	Remotes.Handle("EquipArmor", function(player, area, index)
		local entry = entries[player]
		if entry == nil or type(area) ~= "string" or type(index) ~= "number" then
			return false, "BadRequest"
		end
		if not InventoryRules.EquipArmor(entry.inventory, area, index) then
			return false, "NotArmor"
		end
		InventoryService.Publish(player)
		return true, nil
	end)
	Remotes.Handle("UnequipArmor", function(player, slot)
		local entry = entries[player]
		if entry == nil or type(slot) ~= "string" then
			return false, "BadRequest"
		end
		if not InventoryRules.UnequipArmor(entry.inventory, slot) then
			return false, "NoRoom"
		end
		InventoryService.Publish(player)
		return true, nil
	end)
	Remotes.Handle("EquipSlot", equip)
end

return InventoryService
