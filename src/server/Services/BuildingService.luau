-- Base building, totems, decay and raiding (GDD §6, Q34–41, Q144–146, Q159).
-- Everything here is world state: bases outlive their builders' sessions and
-- vanish when the world empties. Totems stop decay for their own tribe only and
-- never stop raids. Uncovered structures get one 240–360 s lifetime and are then
-- removed outright. Any at-risk player can damage another tribe's structures
-- with ordinary weapons and tools. World place only.

local CollectionService = game:GetService("CollectionService")
local HttpService = game:GetService("HttpService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local BuildRules = require(ReplicatedStorage.Shared.Building.BuildRules)
local DamageRules = require(ReplicatedStorage.Shared.Combat.DamageRules)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Signal = require(ReplicatedStorage.Shared.Core.Signal)
local StructureCatalog = require(ReplicatedStorage.Shared.Building.StructureCatalog)
local DownedService = require(script.Parent.DownedService)
local ExtractionService = require(script.Parent.ExtractionService)
local InventoryService = require(script.Parent.InventoryService)
local SafeZoneService = require(script.Parent.SafeZoneService)
local TribeService = require(script.Parent.TribeService)
local WorldAdmissionService = require(script.Parent.WorldAdmissionService)

local BuildingService = {}

BuildingService.STRUCTURE_TAG = "Structure"
BuildingService.GENERATED_TAG = "GeneratedStructure"
BuildingService.NO_BUILD_TAG = "NoBuildZone"
BuildingService.MAX_PIECES_PER_OWNER = 300
BuildingService.HIT_ALLOWANCE = 2

-- Fires (record) after a piece is placed and (record) just before it is removed.
BuildingService.Placed = Signal.new()
BuildingService.Removing = Signal.new()

local TIER_LOOK = {
	Wood = { Enum.Material.WoodPlanks, Color3.fromRGB(140, 100, 62) },
	Stone = { Enum.Material.Slate, Color3.fromRGB(130, 128, 122) },
	Iron = { Enum.Material.DiamondPlate, Color3.fromRGB(150, 156, 164) },
}

local records = {}
local byPart = {}
local rng = Random.new()

local function now(): number
	return workspace:GetServerTimeNow()
end

-- Structures belong to a tribe, or to a solo player until they join one.
function BuildingService.OwnerKey(player: Player): string
	return TribeService.TribeIdOf(player) or ("solo:" .. player.UserId)
end

function BuildingService.Get(part: Instance?)
	return part and byPart[part] or nil
end

local function totems()
	local list = {}
	for _, record in records do
		if record.isTotem then
			table.insert(list, record)
		end
	end
	return list
end

local function canAct(player: Player): boolean
	local humanoid = player.Character and player.Character:FindFirstChildOfClass("Humanoid")
	return WorldAdmissionService.IsAtRisk(player)
		and humanoid ~= nil
		and humanoid.Health > 0
		and not DownedService.IsDowned(player)
end

local function auras()
	local list = ExtractionService.Auras()
	for _, zone in CollectionService:GetTagged(BuildingService.NO_BUILD_TAG) do
		if zone:IsA("BasePart") then
			table.insert(list, { center = zone.Position, radius = zone:GetAttribute("Radius") or zone.Size.X / 2 })
		end
	end
	return list
end

local function publish(record)
	local part = record.part
	part:SetAttribute("HP", math.ceil(record.hp))
	part:SetAttribute("MaxHP", record.maxHp)
	part:SetAttribute("DecayAt", record.decayDeadline)
	if record.isTotem then
		part:SetAttribute("TotemLevel", record.level)
		part:SetAttribute("TotemRadius", record.radius)
	end
end

-- Re-applies cover to every structure after anything that changes it.
local function reconcileAll()
	local standing = totems()
	local at = now()
	for _, record in records do
		local before = record.decayDeadline
		BuildRules.Reconcile(record, standing, at, rng)
		if record.decayDeadline ~= before then
			publish(record)
		end
	end
end

local function remove(record, reason: string)
	if records[record.id] == nil then
		return
	end
	BuildingService.Removing:Fire(record, reason)
	records[record.id] = nil
	byPart[record.part] = nil
	record.part:Destroy()
	if record.isTotem then
		reconcileAll()
	end
end

local function countFor(ownerKey: string): number
	local count = 0
	for _, record in records do
		if record.ownerKey == ownerKey then
			count += 1
		end
	end
	return count
end

local function overlapsStructures(center: Vector3, half: Vector3): boolean
	-- Shrunk slightly so neighbouring pieces can sit flush against each other.
	local size = half * 2 - Vector3.new(0.5, 0.5, 0.5)
	for _, part in workspace:GetPartBoundsInBox(CFrame.new(center), size) do
		if CollectionService:HasTag(part, BuildingService.STRUCTURE_TAG) then
			return true
		end
		if CollectionService:HasTag(part, BuildingService.GENERATED_TAG) then
			return true
		end
	end
	return false
end

local function makePart(pieceId: string, tier: string, center: Vector3, half: Vector3)
	local part = Instance.new("Part")
	part.Name = pieceId
	part.Anchored = true
	part.Size = half * 2
	part.CFrame = CFrame.new(center)
	local look = TIER_LOOK[tier] or TIER_LOOK.Wood
	part.Material, part.Color = look[1], look[2]
	if pieceId == "Totem" then
		part.Material = Enum.Material.Wood
		part.Color = Color3.fromRGB(176, 120, 60)
	elseif pieceId == "Trap" then
		part.Color = Color3.fromRGB(110, 70, 40)
	elseif pieceId == "Planter" then
		part.Color = Color3.fromRGB(92, 64, 40)
	end
	part:SetAttribute("Piece", pieceId)
	part:SetAttribute("Tier", tier)
	CollectionService:AddTag(part, BuildingService.STRUCTURE_TAG)
	if pieceId == "Workbench" then
		CollectionService:AddTag(part, "Workbench")
	end
	return part
end

local function ownerName(player: Player, ownerKey: string): string
	return if string.sub(ownerKey, 1, 5) == "solo:" then player.DisplayName else (player.DisplayName .. "'s tribe")
end

local function canManage(player: Player, record): boolean
	return canAct(player) and BuildingService.OwnerKey(player) == record.ownerKey
end

local function setupDoor(record)
	local prompt = Instance.new("ProximityPrompt")
	prompt.ActionText = "Open"
	prompt.ObjectText = "Door"
	prompt.HoldDuration = 0
	prompt.MaxActivationDistance = 8
	prompt.Parent = record.part
	prompt.Triggered:Connect(function(player)
		-- Only the owning tribe can open its doors; raiders must break them.
		if not canManage(player, record) then
			return
		end
		local open = not record.part:GetAttribute("Open")
		record.part:SetAttribute("Open", open)
		record.part.CanCollide = not open
		record.part.Transparency = if open then 0.7 else 0
		prompt.ActionText = if open then "Close" else "Open"
	end)
end

local function costText(cost): string
	local parts = {}
	for catalogId, quantity in cost do
		table.insert(parts, ("%s %d"):format(catalogId, quantity))
	end
	table.sort(parts)
	return table.concat(parts, ", ")
end

local function setupTotem(record)
	local prompt = Instance.new("ProximityPrompt")
	prompt.ObjectText = "Tribe totem"
	prompt.HoldDuration = 1
	prompt.MaxActivationDistance = 10
	prompt.Parent = record.part
	local function refreshPrompt()
		local cost = BuildRules.UpgradeCost(record.level)
		prompt.Enabled = cost ~= nil
		prompt.ActionText = if cost then ("Upgrade (%s)"):format(costText(cost)) else "Max level"
	end
	refreshPrompt()
	prompt.Triggered:Connect(function(player)
		local cost = BuildRules.UpgradeCost(record.level)
		if cost == nil or not canManage(player, record) or records[record.id] == nil then
			return
		end
		if not InventoryService.RemoveAll(player, cost) then
			InventoryService.Notify(player, "Not enough materials to upgrade the totem.")
			return
		end
		local level = BuildRules.TotemLevel(record.level + 1)
		local healthRatio = record.hp / record.maxHp
		record.level += 1
		record.radius = level.radius
		record.maxHp = level.hp
		record.hp = level.hp * healthRatio
		publish(record)
		refreshPrompt()
		BuildRules.Claim(records, record, totems())
		reconcileAll()
		InventoryService.Notify(player, ("Totem upgraded to level %d."):format(record.level))
	end)
end

-- Validates and places one piece; `pay` charges for it last (materials or an item).
local function placePiece(player: Player, pieceId: any, tier: any, position: any, steps: any, pay)
	local piece, stats = StructureCatalog.Get(pieceId, tier)
	if piece == nil or stats == nil or typeof(position) ~= "Vector3" then
		return false, "BadRequest"
	end
	if type(steps) ~= "number" or steps % 1 ~= 0 or steps < 0 or steps > 3 then
		return false, "BadRequest"
	end
	if not canAct(player) then
		return false, "NotInRun"
	end
	local root = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
	local base = BuildRules.Snap(position)
	if root == nil or (base - root.Position).Magnitude > BuildRules.REACH then
		return false, "TooFar"
	end
	local half = BuildRules.HalfExtents(piece.size, steps)
	local center = base + Vector3.new(0, half.Y, 0)
	if BuildRules.OverlapsAura(center, half, auras()) then
		return false, "NoBuildZone"
	end
	if SafeZoneService.Contains(center) then
		return false, "SafeZone"
	end
	if overlapsStructures(center, half) then
		return false, "Blocked"
	end
	local ownerKey = BuildingService.OwnerKey(player)
	if countFor(ownerKey) >= BuildingService.MAX_PIECES_PER_OWNER then
		return false, "PieceLimit"
	end
	if not pay(stats) then
		return false, "MissingMaterials"
	end

	local isTotem = pieceId == "Totem"
	local level = isTotem and BuildRules.TotemLevel(1) or nil
	local record = {
		id = HttpService:GenerateGUID(false),
		pieceId = pieceId,
		tier = tier,
		material = stats.material,
		hp = level and level.hp or stats.hp,
		maxHp = level and level.hp or stats.hp,
		ownerKey = ownerKey,
		position = center,
		half = half,
		isTotem = isTotem,
		level = isTotem and 1 or nil,
		radius = level and level.radius or nil,
		part = makePart(pieceId, tier, center, half),
	}
	record.part:SetAttribute("Owner", ownerName(player, ownerKey))
	records[record.id] = record
	byPart[record.part] = record
	if pieceId == "Door" then
		setupDoor(record)
	elseif isTotem then
		setupTotem(record)
	end
	record.part.Parent = workspace
	if isTotem then
		-- A new totem claims structures nobody's totem still covers (§42.2 #1).
		BuildRules.Claim(records, record, totems())
	end
	reconcileAll()
	publish(record)
	BuildingService.Placed:Fire(record, player)
	return true, nil
end

local function build(player: Player, pieceId: any, tier: any, position: any, steps: any)
	return placePiece(player, pieceId, tier, position, steps, function(stats)
		return InventoryService.RemoveAll(player, stats.cost)
	end)
end

-- Places a piece paid for by a carried placeable item (the craftable workbench).
function BuildingService.PlaceFromItem(player: Player, pieceId: string, position: Vector3, catalogId: string)
	return placePiece(player, pieceId, "Wood", position, 0, function()
		return InventoryService.RemoveAll(player, { [catalogId] = 1 })
	end)
end

-- Melee hits on structures, called by CombatService when no player was hit.
-- Returns true when a structure took damage.
function BuildingService.Hit(player: Player, origin: Vector3, aim: Vector3, reach: number, rawDamage: number)
	local ownerKey = BuildingService.OwnerKey(player)
	if SafeZoneService.Contains(origin) then
		return false
	end
	local best, bestDistance = nil, math.huge
	for part in byPart do
		local record = byPart[part]
		local distance = BuildRules.HorizontalDistance(origin, record.position, record.half)
		local offset = record.position - origin
		if
			record.ownerKey ~= ownerKey
			and distance <= reach + BuildingService.HIT_ALLOWANCE
			and distance < bestDistance
			and math.abs(offset.Y) <= record.half.Y + 6
			and (distance < 1 or DamageRules.WithinArc(aim, Vector3.new(offset.X, 0, offset.Z), 120))
		then
			best, bestDistance = record, distance
		end
	end
	if best == nil then
		return false
	end
	local tool = InventoryService.EquippedTool(player)
	best.hp -= BuildRules.StructureDamage(rawDamage, tool and tool.kind, best.material)
	Remotes.Get("CombatFeedback"):FireClient(player, "Hit", math.round(rawDamage))
	if best.hp <= 0 then
		remove(best, "Destroyed")
	else
		publish(best)
	end
	return true
end

-- Removes every player-built structure with any part inside `radius` of
-- `center` (the Guardian clearing its arena, §3.1). Returns how many went.
function BuildingService.ClearWithin(center: Vector3, radius: number): number
	local doomed = {}
	for _, record in records do
		if BuildRules.HorizontalDistance(center, record.position, record.half) <= radius then
			table.insert(doomed, record)
		end
	end
	for _, record in doomed do
		remove(record, "Guardian")
	end
	return #doomed
end

-- Building information the client needs for previews.
local function info()
	local list = {}
	for _, aura in auras() do
		table.insert(list, { center = aura.center, radius = aura.radius })
	end
	return { auras = list, reach = BuildRules.REACH }
end

function BuildingService.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	-- Map ruins are never claimable (Q39).
	for _, part in CollectionService:GetTagged(BuildingService.GENERATED_TAG) do
		part:SetAttribute("Generated", true)
	end
	Remotes.Get("Build").OnServerInvoke = build
	Remotes.Get("BuildInfo").OnServerInvoke = info
	task.spawn(function()
		while true do
			task.wait(1)
			local at = now()
			for _, record in records do
				if record.decayDeadline and record.decayDeadline <= at then
					remove(record, "Decayed")
				end
			end
		end
	end)
	-- A player's departure never removes their base (Q37): structures are only
	-- removed by damage, decay or the world closing.
end

return BuildingService
