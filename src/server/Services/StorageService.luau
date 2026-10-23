-- Storage chests (GDD §6.1, Q39). Every chest is public: anyone who can physically
-- reach it can take or store items, and walls block access until breached. Only
-- the lobby vault is safe. A destroyed or decayed chest spills its contents on the
-- ground. World place only.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
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

local chests = {}

local function view(chest)
	local entries = {}
	for index, item in chest.slots do
		local def = ItemCatalog.Get(item.catalogId)
		table.insert(entries, {
			index = index,
			name = def and def.name or item.catalogId,
			rarity = def and def.rarity or "Common",
			quantity = item.quantity,
			permanent = item.permanent,
		})
	end
	return entries
end

-- In reach and in sight: the first thing between the player's head and the chest
-- must be the chest itself.
local function canReach(player: Player, chest): boolean
	local character = player.Character
	local head = character and character:FindFirstChild("Head")
	local humanoid = character and character:FindFirstChildOfClass("Humanoid")
	if head == nil or humanoid == nil or humanoid.Health <= 0 or DownedService.IsDowned(player) then
		return false
	end
	if not WorldAdmissionService.IsAtRisk(player) then
		return false
	end
	local part = chest.record.part
	if (part.Position - head.Position).Magnitude > StorageService.REACH then
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

local function store(chest, item): boolean
	local cap = ItemCatalog.StackCap(item.catalogId)
	if item.instanceId == nil and cap then
		for _, slot in chest.slots do
			if slot.instanceId == nil and slot.catalogId == item.catalogId and slot.quantity + item.quantity <= cap then
				slot.quantity += item.quantity
				return true
			end
		end
	end
	if #chest.slots >= StructureCatalog.CHEST_SLOTS then
		return false
	end
	table.insert(chest.slots, item)
	return true
end

local function take(player: Player, id: any, index: any)
	local chest = type(id) == "string" and chests[id]
	if not chest or not canReach(player, chest) then
		return false, "TooFar"
	end
	local entry = type(index) == "number" and chest.slots[index]
	if not entry then
		return false, "Empty"
	end
	local copy = DropService.PrepareClaim(player, entry)
	local remaining = InventoryService.Add(player, copy)
	if remaining > 0 and (copy.instanceId or remaining == entry.quantity) then
		return false, "NoRoom"
	end
	if remaining > 0 then
		entry.quantity = remaining
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
	Remotes.Get("ChestTake").OnServerInvoke = take
	Remotes.Get("ChestPut").OnServerInvoke = put
end

return StorageService
