-- Base building, totems, decay and raiding (GDD §6, Q34–41, Q144–146, Q159).
-- Everything here is world state: bases outlive their builders' sessions and
-- vanish when the world empties. Totems stop decay for their own tribe only and
-- never stop raids. Uncovered structures get one 240–360 s lifetime and are then
-- removed outright. Any at-risk player can damage another tribe's structures
-- with ordinary weapons and tools. A piece must stand in the open (not sunk into
-- the ground or other world geometry), within the builder's sight, with no corner
-- in a safe zone or no-build aura (portals, the Guardian arena mid-encounter);
-- each owner keeps at most three totems. The original builder keeps control of
-- pieces their solo key still owns after joining a tribe. World place only.

local CollectionService = game:GetService("CollectionService")
local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local BuildRules = require(ReplicatedStorage.Shared.Building.BuildRules)
local CraftingRules = require(ReplicatedStorage.Shared.Crafting.CraftingRules)
local DamageRules = require(ReplicatedStorage.Shared.Combat.DamageRules)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Signal = require(ReplicatedStorage.Shared.Core.Signal)
local StructureCatalog = require(ReplicatedStorage.Shared.Building.StructureCatalog)
local AntiExploitService = require(script.Parent.AntiExploitService)
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
BuildingService.FOLDER_NAME = "PlayerStructures"
-- Extra slack between the live and the last validated root position for reach.
BuildingService.VALIDATED_SLACK = 8
-- Folders whose contents block placement even when they do not collide.
BuildingService.BLOCKING_FOLDERS = { "EventEnemies", "Bosses", "WorldEvents", "ResourceNodes", "GuardianArena" }

-- Fires (record) after a piece is placed and (record) just before it is removed.
BuildingService.Placed = Signal.new()
BuildingService.Removing = Signal.new()

local TIER_LOOK = {
	Wood = { Enum.Material.WoodPlanks, Color3.fromRGB(140, 100, 62) },
	Stone = { Enum.Material.Slate, Color3.fromRGB(130, 128, 122) },
	Copper = { Enum.Material.Metal, Color3.fromRGB(184, 115, 72) },
	Iron = { Enum.Material.DiamondPlate, Color3.fromRGB(150, 156, 164) },
	Silver = { Enum.Material.Metal, Color3.fromRGB(205, 208, 214) },
	Cobalt = { Enum.Material.Metal, Color3.fromRGB(70, 96, 180) },
	Mithril = { Enum.Material.Foil, Color3.fromRGB(160, 215, 225) },
	Adamantine = { Enum.Material.DiamondPlate, Color3.fromRGB(60, 70, 64) },
}

local records = {}
local byPart = {}
local totemSet = {}
local auraSources = {}
local folder = nil
local rng = Random.new()

local function structureFolder(): Folder
	if folder == nil or folder.Parent == nil then
		folder = Instance.new("Folder")
		folder.Name = BuildingService.FOLDER_NAME
		folder.Parent = workspace
	end
	return folder
end

local function now(): number
	return workspace:GetServerTimeNow()
end

-- Structures belong to a tribe, or to a solo player until they join one.
function BuildingService.OwnerKey(player: Player): string
	return TribeService.TribeIdOf(player) or BuildRules.SoloKey(player.UserId)
end

function BuildingService.Get(part: Instance?)
	return part and byPart[part] or nil
end

-- True when `player` controls `record`: their owner key owns it, or their solo key
-- still does (a solo builder who later joined a tribe keeps their doors and
-- totems). A member who left or was kicked keeps nothing they built for the tribe.
function BuildingService.IsOwnedBy(player: Player, record): boolean
	return BuildRules.Controls(BuildingService.OwnerKey(player), player.UserId, record.ownerKey)
end

local function totems()
	local list = {}
	for record in totemSet do
		table.insert(list, record)
	end
	return list
end

-- Standing totems as {position, radius, ownerKey} (event placement keeps clear).
function BuildingService.Totems()
	local list = {}
	for record in totemSet do
		table.insert(list, { position = record.position, radius = record.radius, ownerKey = record.ownerKey })
	end
	return list
end

-- Registers `source() -> {center, radius}?`, an extra no-build aura (the Guardian
-- arena while an encounter runs).
function BuildingService.AddAuraSource(source)
	table.insert(auraSources, source)
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
	for _, source in auraSources do
		local aura = source()
		if aura then
			table.insert(list, aura)
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

local function reconcile(record, standing, at: number)
	local before = record.decayDeadline
	BuildRules.Reconcile(record, standing, at, rng)
	if record.decayDeadline ~= before then
		publish(record)
	end
end

-- Re-applies cover to the structures a change to `totem` can affect: only those
-- inside its radius, not every record in the world.
local function reconcileNear(totem)
	local standing = totems()
	local at = now()
	for _, record in BuildRules.WithinTotem(records, totem) do
		reconcile(record, standing, at)
	end
end

local function remove(record, reason: string)
	if records[record.id] == nil then
		return
	end
	BuildingService.Removing:Fire(record, reason)
	records[record.id] = nil
	byPart[record.part] = nil
	totemSet[record] = nil
	record.part:Destroy()
	if record.isTotem then
		reconcileNear(record)
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

local function isBody(part: BasePart): boolean
	local model = part:FindFirstAncestorOfClass("Model")
	return model ~= nil
		and (Players:GetPlayerFromCharacter(model) ~= nil or model:FindFirstChildOfClass("Humanoid") ~= nil)
end

-- World geometry a piece may not overlap: anything solid (ground tiles, rocks,
-- trees, ruins), characters and NPC bodies, resource nodes, event models and
-- drops. Non-colliding markers and zone volumes do not count; structures are
-- checked by overlapsStructures.
local function blocksPlacement(part: BasePart): boolean
	if part:IsA("Terrain") or CollectionService:HasTag(part, BuildingService.STRUCTURE_TAG) then
		return false
	end
	if part.CanCollide or part.Name == "DroppedItem" or CollectionService:HasTag(part, "ResourceNode") then
		return true
	end
	if isBody(part) then
		return true
	end
	for _, name in BuildingService.BLOCKING_FOLDERS do
		local container = workspace:FindFirstChild(name)
		if container and part:IsDescendantOf(container) then
			return true
		end
	end
	return false
end

-- True when solid terrain fills any voxel whose centre lies in the box.
local function terrainInside(boxCenter: Vector3, boxSize: Vector3): boolean
	local low, high = boxCenter - boxSize / 2, boxCenter + boxSize / 2
	local region = Region3.new(low, high):ExpandToGrid(4)
	local materials, occupancies = workspace.Terrain:ReadVoxels(region, 4)
	local size = materials.Size
	local origin = region.CFrame.Position - region.Size / 2
	for x = 1, size.X do
		for y = 1, size.Y do
			local voxelY = origin.Y + (y - 0.5) * 4
			if voxelY >= low.Y and voxelY <= high.Y then
				for z = 1, size.Z do
					local material = materials[x][y][z]
					if
						material ~= Enum.Material.Air
						and material ~= Enum.Material.Water
						and occupancies[x][y][z] > 0.5
					then
						return true
					end
				end
			end
		end
	end
	return false
end

-- A piece must stand in the open: nothing solid may fill it above its bottom
-- GROUND_ALLOWANCE studs (no totems buried in the ground or inside rocks).
local function overlapsWorld(center: Vector3, half: Vector3): boolean
	local boxCenter, boxSize = BuildRules.ClearanceBox(center, half)
	for _, part in workspace:GetPartBoundsInBox(CFrame.new(boxCenter), boxSize) do
		if blocksPlacement(part) then
			return true
		end
	end
	return terrainInside(boxCenter, boxSize)
end

-- The builder must see the spot: nothing solid between their head and the base.
local function inSight(head: BasePart, base: Vector3, half: Vector3): boolean
	local target = base + Vector3.new(0, math.min(0.5, half.Y), 0)
	local ignore = {}
	for _, other in Players:GetPlayers() do
		if other.Character then
			table.insert(ignore, other.Character)
		end
	end
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	params.FilterDescendantsInstances = ignore
	params.RespectCanCollide = true
	params.IgnoreWater = true
	local offset = target - head.Position
	local hit = workspace:Raycast(head.Position, offset, params)
	return BuildRules.InSight(hit and (hit.Position - head.Position).Magnitude, offset.Magnitude)
end

local function makePart(pieceId: string, tier: string, material: string, center: Vector3, half: Vector3)
	local part = Instance.new("Part")
	part.Name = pieceId
	part.Anchored = true
	part.Size = half * 2
	part.CFrame = CFrame.new(center)
	-- Tiered pieces look like their tier; single-tier pieces like what they are
	-- built from (a stone furnace, an iron anvil).
	local look = TIER_LOOK[material] or TIER_LOOK[tier] or TIER_LOOK.Wood
	part.Material, part.Color = look[1], look[2]
	if pieceId == "Totem" then
		part.Material = Enum.Material.Wood
		part.Color = Color3.fromRGB(176, 120, 60)
	elseif pieceId == "Trap" then
		part.Color = Color3.fromRGB(110, 70, 40)
	elseif pieceId == "Planter" then
		part.Color = Color3.fromRGB(92, 64, 40)
	elseif pieceId == "Anvil" then
		part.Color = Color3.fromRGB(70, 72, 78)
	elseif pieceId == "Cauldron" then
		part.Material = Enum.Material.Metal
		part.Color = Color3.fromRGB(46, 44, 42)
	end
	part:SetAttribute("Piece", pieceId)
	part:SetAttribute("Tier", tier)
	CollectionService:AddTag(part, BuildingService.STRUCTURE_TAG)
	if CraftingRules.IsStation(pieceId) then
		-- Crafting stations (CraftingService): Workbench, Furnace, Anvil, Cauldron.
		CollectionService:AddTag(part, pieceId)
	end
	return part
end

local function ownerName(player: Player, ownerKey: string): string
	return if string.sub(ownerKey, 1, 5) == "solo:" then player.DisplayName else (player.DisplayName .. "'s tribe")
end

local function canManage(player: Player, record): boolean
	return canAct(player) and BuildingService.IsOwnedBy(player, record)
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
		BuildRules.Claim(BuildRules.WithinTotem(records, record), record, totems())
		reconcileNear(record)
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
	local head = player.Character and player.Character:FindFirstChild("Head")
	local base = BuildRules.Snap(position)
	if root == nil or head == nil or (base - root.Position).Magnitude > BuildRules.REACH then
		return false, "TooFar"
	end
	-- Reach also holds from where the server last validated the player.
	local validated = AntiExploitService.ValidatedPosition(player)
	if validated and (base - validated).Magnitude > BuildRules.REACH + BuildingService.VALIDATED_SLACK then
		return false, "TooFar"
	end
	local half = BuildRules.HalfExtents(piece.size, steps)
	local center = base + Vector3.new(0, half.Y, 0)
	if BuildRules.OverlapsAura(center, half, auras()) then
		return false, "NoBuildZone"
	end
	if SafeZoneService.OverlapsBox(center, half) then
		return false, "SafeZone"
	end
	if overlapsStructures(center, half) or overlapsWorld(center, half) then
		return false, "Blocked"
	end
	if not inSight(head, base, half) then
		return false, "NoLineOfSight"
	end
	local ownerKey = BuildingService.OwnerKey(player)
	if countFor(ownerKey) >= BuildingService.MAX_PIECES_PER_OWNER then
		return false, "PieceLimit"
	end
	if pieceId == "Totem" and BuildRules.TotemLimitReached(totems(), ownerKey) then
		return false, "TotemLimit"
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
		part = makePart(pieceId, tier, stats.material, center, half),
	}
	record.part:SetAttribute("Owner", ownerName(player, ownerKey))
	records[record.id] = record
	byPart[record.part] = record
	if pieceId == "Door" then
		setupDoor(record)
	elseif isTotem then
		setupTotem(record)
	end
	record.part.Parent = structureFolder()
	if isTotem then
		totemSet[record] = true
		-- A new totem claims structures nobody's totem still covers (§42.2 #1).
		BuildRules.Claim(BuildRules.WithinTotem(records, record), record, totems())
		reconcileNear(record)
	else
		reconcile(record, totems(), now())
	end
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
-- Only pieces near the swing are considered (a spatial query, not every piece in
-- the world); `canSee(part)` (optional) rejects pieces behind walls. Returns true
-- when a structure took damage.
function BuildingService.Hit(
	player: Player,
	origin: Vector3,
	aim: Vector3,
	reach: number,
	rawDamage: number,
	canSee: ((BasePart) -> boolean)?
)
	if SafeZoneService.Contains(origin) then
		return false
	end
	local params = OverlapParams.new()
	params.FilterType = Enum.RaycastFilterType.Include
	params.FilterDescendantsInstances = { structureFolder() }
	-- Bounding boxes up to half.Y + 6 above or below the swing still count.
	local radius = reach + BuildingService.HIT_ALLOWANCE + 6
	local best, bestDistance = nil, math.huge
	for _, part in workspace:GetPartBoundsInRadius(origin, radius, params) do
		local record = byPart[part]
		if record == nil or BuildingService.IsOwnedBy(player, record) then
			continue
		end
		local distance = BuildRules.HorizontalDistance(origin, record.position, record.half)
		local offset = record.position - origin
		if
			distance <= reach + BuildingService.HIT_ALLOWANCE
			and distance < bestDistance
			and math.abs(offset.Y) <= record.half.Y + 6
			and (distance < 1 or DamageRules.WithinArc(aim, Vector3.new(offset.X, 0, offset.Z), 120))
			and (canSee == nil or canSee(part))
		then
			best, bestDistance = record, distance
		end
	end
	if best == nil then
		return false
	end
	local tool = InventoryService.EquippedTool(player)
	best.hp -= BuildRules.StructureDamage(rawDamage, tool and tool.kind, best.material)
	Remotes.Get("CombatFeedback"):FireClient(player, "Hit", math.round(rawDamage), best.part.Position)
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
	structureFolder()
	Remotes.Handle("Build", build)
	Remotes.Handle("BuildInfo", info)
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
