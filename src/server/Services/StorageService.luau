-- Storage chests (GDD §6.1, Q39). Every chest is public: anyone who can physically
-- reach it can take or store items, and walls block access until breached. Only
-- the lobby vault is safe. A destroyed or decayed chest spills its contents on the
-- ground. World place only.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local InventoryRules = require(script.Parent.Parent.Rules.Inventory.InventoryRules)
local ListingKeys = require(script.Parent.Parent.Rules.Net.ListingKeys)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local StructureCatalog = require(script.Parent.Parent.Rules.Building.StructureCatalog)
local BuildingService = require(script.Parent.BuildingService)
local DropService = require(script.Parent.DropService)
local InteractionService = require(script.Parent.InteractionService)
local InventoryService = require(script.Parent.InventoryService)

local StorageService = {}

StorageService.REACH = 10

local chests = {}

-- In reach and in sight, from where the server knows the player is
-- (InteractionService.CanReach): walls block a chest until they are breached.
local function canReach(player: Player, chest): boolean
	return InteractionService.CanReach(player, chest.record.part, StorageService.REACH)
end

local function send(player: Player, id: string, chest)
	Remotes.Get("ChestOpened"):FireClient(player, id, ListingKeys.View(chest.slots, false))
end

-- Merging adds up the stacks' carried counts, so a chest never launders
-- carried-in materials into doublable ones (GDD §53).
local function store(chest, item): boolean
	return InventoryRules.Store(chest.slots, item, StructureCatalog.CHEST_SLOTS)
end

-- (chestId, index, key): the entry `key` names (ListingKeys), so a stale index
-- never takes a different item.
local function take(player: Player, id: any, index: any, key: any)
	local chest = type(id) == "string" and chests[id]
	if not chest or not canReach(player, chest) then
		return false, "TooFar"
	end
	local found, problem = ListingKeys.Resolve(chest.slots, index, key)
	if found == nil then
		return false, problem
	end
	index = found
	local entry = chest.slots[index]
	local copy = DropService.PrepareClaim(player, entry)
	local remaining, carried = InventoryService.Add(player, copy)
	if remaining > 0 and (copy.instanceId or remaining == entry.quantity) then
		return false, "NoRoom"
	end
	if remaining > 0 then
		-- What stays in the chest keeps its share of the carried units.
		entry.quantity = remaining
		InventoryRules.SetCarried(entry, carried)
	else
		table.remove(chest.slots, index)
	end
	DropService.FinishClaim(player, copy, entry.ownerId)
	send(player, id, chest)
	return true, nil
end

local function put(player: Player, id: any, area: any, index: any)
	local chest = type(id) == "string" and chests[id]
	if not chest or not canReach(player, chest) then
		return false, "TooFar"
	end
	if type(area) ~= "string" or type(index) ~= "number" then
		return false, "BadRequest"
	end
	local item = InventoryService.TakeAt(player, area, index)
	if item == nil then
		return false, "Empty"
	end
	if not store(chest, item) then
		InventoryService.Add(player, item)
		return false, "ChestFull"
	end
	DropService.Release(player, item, "BaseStored")
	send(player, id, chest)
	return true, nil
end

local function register(record)
	local chest = { record = record, slots = {} }
	chests[record.id] = chest
	local prompt = Instance.new("ProximityPrompt")
	prompt.ActionText = "Open"
	prompt.ObjectText = "Storage chest"
	prompt.HoldDuration = 0
	prompt.MaxActivationDistance = 8
	prompt.Parent = record.part
	prompt.Triggered:Connect(function(player)
		if canReach(player, chest) then
			send(player, record.id, chest)
		end
	end)
end

function StorageService.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	BuildingService.Placed:Connect(function(record)
		if record.pieceId == "Chest" then
			register(record)
		end
	end)
	BuildingService.Removing:Connect(function(record)
		local chest = chests[record.id]
		if chest == nil then
			return
		end
		chests[record.id] = nil
		for _, item in chest.slots do
			DropService.Spawn(item, record.position)
		end
	end)
	Remotes.Handle("ChestTake", take)
	Remotes.Handle("ChestPut", put)
end

return StorageService
