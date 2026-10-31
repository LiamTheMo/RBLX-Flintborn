-- Harvestable resource nodes (GDD §4.1, §7.6, §51, §53, §54). Uses map parts
-- tagged "ResourceNode" (attribute NodeType) when present; otherwise scatters
-- placeholder nodes over each map zone from its pool, on dry ground in a fitting
-- habitat (clay by water, frost shrubs up high, cave nodes inside Emberhollow),
-- until the real map arrives. Scattered nodes take their look from NodeModels
-- (an invisible upright hitbox with the model welded on, ModelBuilder) or, for a
-- type without a model yet, NodeCatalog.Looks; authored nodes keep their own.
-- Nodes are hit with the attack input (GDD §5.1): CombatService hands a swing
-- that hit no player or creature to Hit, which picks the closest active node in
-- front by its hitbox surface (HarvestRules). Each hit is validated for range,
-- cadence, tool and node state; ores and gems need their pickaxe tier, plants are
-- gathered by hand. Every hit drops its material on the ground beside the node
-- (the hitter's for 10 s, DropService) and takes as much from the node's health;
-- depleted nodes regrow after their tier's time. The hitbox carries NodeType,
-- NodeLabel, NodeAction and Active for the client's hover plaque. World only.

local CollectionService = game:GetService("CollectionService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local ModifierRules = require(ReplicatedStorage.Shared.Progression.ModifierRules)
local BiomeCatalog = require(ReplicatedStorage.Shared.World.BiomeCatalog)
local HarvestRules = require(ReplicatedStorage.Shared.Resources.HarvestRules)
local IslandLayout = require(ReplicatedStorage.Shared.World.IslandLayout)
local NodeCatalog = require(ReplicatedStorage.Shared.Resources.NodeCatalog)
local ModelBuilder = require(ReplicatedStorage.Shared.Visuals.ModelBuilder)
local NodeModels = require(ReplicatedStorage.Shared.Visuals.NodeModels)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local WorldState = require(ReplicatedStorage.Shared.World.WorldState)
local CombatService = require(script.Parent.CombatService)
local DropService = require(script.Parent.DropService)
local InventoryService = require(script.Parent.InventoryService)
local ModifierService = require(script.Parent.ModifierService)
local ProgressionService = require(script.Parent.ProgressionService)
local WorldAdmissionService = require(script.Parent.WorldAdmissionService)

local ResourceService = {}

ResourceService.TAG = "ResourceNode"
ResourceService.DEFAULT_MAP_RADIUS = 2048

local nodes = {}
local lastHit = {}
local rng = Random.new()

local function rootOf(player: Player)
	local character = player.Character
	return character and character:FindFirstChild("HumanoidRootPart")
end

local function setActive(node, active: boolean)
	node.active = active
	node.part:SetAttribute("Active", active)
	if node.look then
		-- A modelled node's hitbox stays invisible; its look shows or hides.
		ModelBuilder.SetVisible(node.look, active)
	else
		node.part.Transparency = if active then 0 else 1
	end
	node.part.CanCollide = active
	-- A depleted node is gone: no invisible blocker for rays or spatial queries.
	node.part.CanQuery = active
end

-- A drop's colour: the look of the node that gives that material.
local looksByMaterial = {}
for nodeType, def in NodeCatalog.Nodes do
	local look = NodeCatalog.Looks[nodeType]
	if look and looksByMaterial[def.material] == nil then
		looksByMaterial[def.material] = look.color
	end
end
local BONUS_COLORS = {
	Flint = Color3.fromRGB(70, 70, 76),
	Resin = Color3.fromRGB(214, 150, 40),
}
local function colorOf(stack): Color3?
	return BONUS_COLORS[stack.catalogId] or looksByMaterial[stack.catalogId]
end

-- A ground point just outside the node, scattered over the half facing `from`.
local function dropPoint(node, from: Vector3): Vector3
	local part = node.part
	-- World-axis extents, so a tree's rotated cylinder counts as standing up.
	local rotated = part.CFrame:VectorToWorldSpace(part.Size)
	local size = Vector3.new(math.abs(rotated.X), math.abs(rotated.Y), math.abs(rotated.Z))
	local toward = (from - part.Position) * Vector3.new(1, 0, 1)
	local facing = if toward.Magnitude > 0.1 then math.atan2(toward.Z, toward.X) else rng:NextNumber(0, math.pi * 2)
	local angle = facing + rng:NextNumber(-math.pi / 2, math.pi / 2)
	local reach = math.max(size.X, size.Z) / 2 + rng:NextNumber(1, 2.5)
	local point = part.Position + Vector3.new(math.cos(angle) * reach, 0, math.sin(angle) * reach)
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	-- Land on the ground, never on a player, a creature or another (non-colliding)
	-- drop, or the drop would hang in the air out of reach.
	params.RespectCanCollide = true
	local ignore = { part }
	for _, name in { "ResourceNodes", "EventEnemies" } do
		local folder = workspace:FindFirstChild(name)
		if folder then
			table.insert(ignore, folder)
		end
	end
	for _, other in Players:GetPlayers() do
		if other.Character then
			table.insert(ignore, other.Character)
		end
	end
	params.FilterDescendantsInstances = ignore
	local top = part.Position.Y + size.Y
	local hit = workspace:Raycast(Vector3.new(point.X, top, point.Z), Vector3.new(0, -(size.Y + 20), 0), params)
	return if hit then hit.Position else Vector3.new(point.X, part.Position.Y - size.Y / 2, point.Z)
end

local function harvest(player: Player, node)
	if not node.active or not WorldAdmissionService.IsAtRisk(player) then
		return
	end
	-- Range is to the hitbox's surface, so a big node is reached at its side.
	local root = rootOf(player)
	if
		root == nil
		or HarvestRules.SurfaceDistance(root.Position, node.center, node.half) > NodeCatalog.HARVEST_RANGE
	then
		return
	end
	local now = os.clock()
	if not HarvestRules.CadenceReady(lastHit[player], now) then
		return
	end
	lastHit[player] = now

	local def = NodeCatalog.Nodes[node.nodeType]
	local tool = InventoryService.EquippedTool(player)
	-- Mastery's level-based chance of one extra drop that costs no health (GDD §53).
	local hit =
		NodeCatalog.Hit(node.nodeType, node.health, tool, ModifierService.Sum(player, def.mastery .. "Yield"), rng)
	if hit == nil then
		-- Ores and gems below their pickaxe gate give nothing (GDD §51).
		InventoryService.Notify(player, NodeCatalog.GateNotice(node.nodeType, tool) or "You can't gather that.")
		return
	end
	-- The Bounty perk still adds to the material dropped.
	local material = hit.stacks[1]
	material.quantity = ModifierRules.RollYield(material.quantity, ModifierService.Get(player, "DropQuantity"), rng)
	node.health = hit.health
	ProgressionService.GrantXp(player, "Harvest", "Gathering")
	ProgressionService.GrantMastery(player, def.mastery, 1)
	-- The material, plus Resin from trees and Flint from rocks, lands beside the
	-- node on the hitter's side.
	for _, stack in hit.stacks do
		DropService.Spawn(stack, dropPoint(node, root.Position), { ownerId = player.UserId, color = colorOf(stack) })
	end
	-- The hitter's hit marker confirms the gather ("+2 Wood").
	Remotes.Get("CombatFeedback"):FireClient(player, "Harvest", material.quantity, node.center, material.catalogId)
	if hit.depleted then
		setActive(node, false)
		task.delay(NodeCatalog.RegrowSeconds(node.nodeType), function()
			node.health = NodeCatalog.Health(node.nodeType)
			setActive(node, true)
		end)
	end
end

-- Makes `part` a node. `look` is the decoration of a modelled node (hidden while
-- it regrows); without one the part itself is the look.
local function register(part: BasePart, nodeType: string, look: { BasePart }?)
	local def = NodeCatalog.Nodes[nodeType]
	if def == nil then
		warn("[ResourceService] Unknown node type " .. tostring(nodeType))
		return
	end
	-- What the client's hover plaque shows: "Mine" over "Iron Deposit · Copper
	-- Pickaxe+", so the gate shows before the first swing.
	part:SetAttribute("NodeType", nodeType)
	part:SetAttribute("NodeLabel", HarvestRules.Label(nodeType))
	part:SetAttribute("NodeAction", HarvestRules.Action(nodeType))
	part:SetAttribute("Active", true)
	-- Nodes are anchored, so their box is measured once.
	local frame = part.CFrame
	table.insert(nodes, {
		part = part,
		nodeType = nodeType,
		health = def.health,
		active = true,
		look = look,
		center = part.Position,
		half = HarvestRules.WorldHalf(frame.RightVector, frame.UpVector, frame.LookVector, part.Size),
	})
end

-- A modelled node: an invisible upright hitbox standing on `position` with the
-- model welded on in a "Look" model. Returns the hitbox, or nil without a model.
local function makeModelled(folder: Folder, nodeType: string, position: Vector3): BasePart?
	local entry = NodeModels.Get(nodeType)
	if entry == nil or entry.hitbox == nil or entry.recipe == nil then
		return nil
	end
	local box = entry.hitbox
	local size = Vector3.new(box[1] or box.x, box[2] or box.y, box[3] or box.z)
	local hitbox = Instance.new("Part")
	hitbox.Name = nodeType
	hitbox.Anchored = true
	hitbox.Size = size
	hitbox.Transparency = 1
	hitbox.CanCollide = true
	hitbox.CanQuery = true
	hitbox.CanTouch = false
	hitbox.CastShadow = false
	hitbox.CFrame = CFrame.new(position + Vector3.new(0, size.Y / 2, 0))
	local model = Instance.new("Model")
	model.Name = HarvestRules.LOOK_MODEL
	local look = ModelBuilder.Decorate(hitbox, entry.recipe, { parent = model })
	model.Parent = hitbox
	hitbox.Parent = folder
	register(hitbox, nodeType, look)
	return hitbox
end

local function makeNode(folder: Folder, nodeType: string, position: Vector3)
	if makeModelled(folder, nodeType, position) then
		return
	end
	local look = NodeCatalog.Looks[nodeType]
	if look == nil then
		warn("[ResourceService] No look for node type " .. nodeType)
		return
	end
	local part = Instance.new("Part")
	part.Name = nodeType
	part.Anchored = true
	part.Shape = look.shape
	part.Size = look.size
	part.Color = look.color
	part.Material = look.material or Enum.Material.SmoothPlastic
	part.CFrame = if look.shape == Enum.PartType.Cylinder
		then CFrame.new(position + Vector3.new(0, look.size.Y / 2, 0)) * CFrame.Angles(0, 0, math.rad(90))
		else CFrame.new(position + Vector3.new(0, look.size.Y / 2, 0))
	if look.shape == Enum.PartType.Cylinder then
		part.Size = Vector3.new(look.size.Y, look.size.X, look.size.Z)
	end
	part.Parent = folder
	register(part, nodeType)
end

-- Terrain right under a chosen spot (from just above it, so the cave roof is
-- never hit); nil over water.
local function settle(position: Vector3): Vector3?
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Include
	params.FilterDescendantsInstances = { workspace.Terrain }
	local hit = workspace:Raycast(position + Vector3.new(0, 10, 0), Vector3.new(0, -40, 0), params)
	if hit and hit.Material ~= Enum.Material.Water then
		return hit.Position
	end
	return nil
end

-- The node type's preferred habitat in this zone, some of the time (BiomeCatalog).
local function habitatFor(zoneId: string, nodeType: string): string?
	local prefer = BiomeCatalog.NodeHabitats[nodeType]
	if prefer == nil or rng:NextNumber() >= prefer.share then
		return nil
	end
	for _, habitat in prefer.habitats do
		if BiomeCatalog.HasHabitat(zoneId, habitat) then
			return habitat
		end
	end
	return nil
end

-- A spot on the generated island: dry ground in the zone, out of camps and
-- structures (IslandLayout).
local function generatedSpot(zoneId: string, nodeType: string): Vector3?
	local habitat = habitatFor(zoneId, nodeType)
	local point = habitat and IslandLayout.RandomPointIn(zoneId, rng, habitat)
		or IslandLayout.RandomPointIn(zoneId, rng)
	return point and settle(point)
end

-- A spot on another map: the zone's envelope scaled to the map, found by raycast.
local function authoredSpot(zoneId: string, scale: number): Vector3?
	local bounds = BiomeCatalog.Bounds(zoneId)
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	params.FilterDescendantsInstances = { workspace:FindFirstChild("ResourceNodes") }
	for _ = 1, 12 do
		local x, z = rng:NextNumber(bounds.minX, bounds.maxX), rng:NextNumber(bounds.minZ, bounds.maxZ)
		if BiomeCatalog.ZoneAt(x, z) == zoneId then
			local hit = workspace:Raycast(Vector3.new(x * scale, 1000, z * scale), Vector3.new(0, -2000, 0), params)
			if hit and hit.Material ~= Enum.Material.Water and hit.Position.Y > -50 then
				return hit.Position
			end
		end
	end
	return nil
end

-- Each zone's resource pool goes into that zone (GDD §51, §54), so ores follow
-- danger: copper and iron in Low zones, silver, cobalt and gems in Medium ones,
-- mithril only in Extreme ones. A map without the generated island scales the
-- zones to its own radius.
local function scatter()
	local folder = Instance.new("Folder")
	folder.Name = "ResourceNodes"
	folder.Parent = workspace
	local generated = WorldState.IsGenerated()
	local radius = workspace:GetAttribute("FlintbornMapRadius") or ResourceService.DEFAULT_MAP_RADIUS
	local scale = radius / BiomeCatalog.MAP_RADIUS
	for _, zoneId in BiomeCatalog.ZONE_IDS do
		for nodeType, count in BiomeCatalog.Zones[zoneId].resources do
			for _ = 1, count do
				local position = if generated then generatedSpot(zoneId, nodeType) else authoredSpot(zoneId, scale)
				if position then
					makeNode(folder, nodeType, position)
				end
			end
		end
	end
end

-- A swing from `origin` along `flatAim` (CombatService, after players and
-- creatures): harvests the closest active node in front within `reach` (the held
-- item's, HarvestRules.Reach) of its surface that `canSee(part)` allows. True
-- when a node took the swing, even when it gave nothing (cadence, a pickaxe
-- gate), so the swing never falls through to a structure behind the node.
function ResourceService.Hit(
	player: Player,
	origin: Vector3,
	flatAim: Vector3,
	reach: number,
	canSee: ((BasePart) -> boolean)?
): boolean
	local visible = if canSee
		then function(node)
			return canSee(node.part)
		end
		else nil
	local node = HarvestRules.Pick(origin, flatAim, HarvestRules.Reach(reach), nodes, visible)
	if node == nil then
		return false
	end
	harvest(player, node)
	return true
end

function ResourceService.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	-- The attack input harvests through CombatService (a hook: no require cycle).
	CombatService.HarvestHit = ResourceService.Hit
	-- Nodes sit on the map's ground, so placement waits for the map.
	task.spawn(function()
		WorldState.WaitUntilReady()
		local tagged = CollectionService:GetTagged(ResourceService.TAG)
		if #tagged > 0 then
			for _, part in tagged do
				if part:IsA("BasePart") then
					register(part, part:GetAttribute("NodeType"))
				end
			end
		else
			scatter()
		end
	end)
	Players.PlayerRemoving:Connect(function(player)
		lastHit[player] = nil
	end)
end

return ResourceService
