-- Storage chests (GDD §6.1, Q39). Every chest is public: anyone who can physically
-- reach it can take or store items, and walls block access until breached. Only
-- the lobby vault is safe. A destroyed or decayed chest spills its contents on the
-- ground. World place only.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local InventoryRules = require(ReplicatedStorage.Shared.Inventory.InventoryRules)
local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local ListingKeys = require(ReplicatedStorage.Shared.Net.ListingKeys)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local StructureCatalog = require(ReplicatedStorage.Shared.Building.StructureCatalog)
local BuildingService = require(script.Parent.BuildingService)
local DownedService = require(script.Parent.DownedService)
local DropService = require(script.Parent.DropService)
local InventoryService = require(script.Parent.InventoryService)
local WorldAdmissionService = require(script.Parent.WorldAdmissionService)

local StorageService = {}

StorageService.REACH = 10
-- How far the Head may be from the HumanoidRootPart on a real character.
StorageService.HEAD_OFFSET = 3.5

local chests = {}

local function view(chest)
	local entries = {}
	for index, item in chest.slots do
		local def = ItemCatalog.Get(item.catalogId)
		table.insert(entries, {
			index = index,
			key = ListingKeys.KeyOf(item),
			catalogId = item.catalogId,
			name = def and def.name or item.catalogId,
			rarity = def and def.rarity or "Common",
			quantity = item.quantity,
			permanent = item.permanent,
		})
	end
	return entries
end

-- In reach and in sight: reach is measured from the HumanoidRootPart, the head
-- must sit on the body (a client can move its own Head through a wall), and the
-- first thing between the head and the chest must be the chest itself.
local function canReach(player: Player, chest): boolean
	local character = player.Character
	local head = character and character:FindFirstChild("Head")
	local root = character and character:FindFirstChild("HumanoidRootPart")
	local humanoid = character and character:FindFirstChildOfClass("Humanoid")
	if head == nil or root == nil or humanoid == nil or humanoid.Health <= 0 or DownedService.IsDowned(player) then
		return false
	end
	if not WorldAdmissionService.IsAtRisk(player) then
		return false
	end
	if (head.Position - root.Position).Magnitude > StorageService.HEAD_OFFSET then
		return false
	end
	local part = chest.record.part
	if (part.Position - root.Position).Magnitude > StorageService.REACH then
		return false
	end
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	params.FilterDescendantsInstances = { character }
	local hit = workspace:Raycast(head.Position, part.Position - head.Position, params)
	return hit == nil or hit.Instance == part
end

local function send(player: Player, id: string, chest)
	Remotes.Get("ChestOpened"):FireClient(player, id, view(chest))
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
