-- Harvestable resource nodes (GDD §4.1, §7.6). Uses map parts tagged "ResourceNode"
-- (attribute NodeType) when present; otherwise scatters placeholder nodes across
-- the ground until the real map arrives (v0.15). Each hit is validated for range,
-- cadence, tool and node state; depleted nodes regrow after ~120 s. World only.

local CollectionService = game:GetService("CollectionService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local ModifierRules = require(ReplicatedStorage.Shared.Progression.ModifierRules)
local NodeCatalog = require(ReplicatedStorage.Shared.Resources.NodeCatalog)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local InventoryService = require(script.Parent.InventoryService)
local ModifierService = require(script.Parent.ModifierService)
local ProgressionService = require(script.Parent.ProgressionService)
local WorldAdmissionService = require(script.Parent.WorldAdmissionService)

local ResourceService = {}

ResourceService.TAG = "ResourceNode"
ResourceService.DEFAULT_MAP_RADIUS = 1000
-- Placeholder scatter counts per node type when the map has no tagged nodes.
ResourceService.SCATTER = {
	Tree = 60,
	Rock = 40,
	IronDeposit = 14,
	FiberPlant = 40,
	HerbShrub = 25,
	BerryBush = 20,
}

local LOOKS = {
	Tree = { size = Vector3.new(3, 14, 3), color = Color3.fromRGB(110, 78, 46), shape = Enum.PartType.Cylinder },
	Rock = { size = Vector3.new(6, 4, 6), color = Color3.fromRGB(128, 126, 120), shape = Enum.PartType.Block },
	IronDeposit = { size = Vector3.new(5, 4, 5), color = Color3.fromRGB(150, 112, 92), shape = Enum.PartType.Block },
	FiberPlant = { size = Vector3.new(2, 3, 2), color = Color3.fromRGB(130, 170, 80), shape = Enum.PartType.Block },
	HerbShrub = { size = Vector3.new(3, 2, 3), color = Color3.fromRGB(70, 140, 90), shape = Enum.PartType.Ball },
	BerryBush = { size = Vector3.new(3, 3, 3), color = Color3.fromRGB(150, 50, 80), shape = Enum.PartType.Ball },
}

local nodes = {}
local lastHit = {}
local rng = Random.new()

local function rootOf(player: Player)
	local character = player.Character
	return character and character:FindFirstChild("HumanoidRootPart")
end

local function setActive(node, active: boolean)
	node.active = active
	node.prompt.Enabled = active
	node.part.Transparency = if active then 0 else 1
	node.part.CanCollide = active
end

local function harvest(player: Player, node)
	if not node.active or not WorldAdmissionService.IsAtRisk(player) then
		return
	end
	local root = rootOf(player)
	if root == nil or (root.Position - node.part.Position).Magnitude > NodeCatalog.HARVEST_RANGE then
		return
	end
	local now = os.clock()
	if lastHit[player] and now - lastHit[player] < NodeCatalog.HARVEST_INTERVAL then
		return
	end
	lastHit[player] = now

	local def = NodeCatalog.Nodes[node.nodeType]
	local base = NodeCatalog.YieldFor(node.nodeType, InventoryService.EquippedTool(player))
	if base <= 0 then
		InventoryService.Notify(player, "You need a better tool for that.")
		return
	end
	-- Mastery (+1% per level) and the Bounty perk stack through one pipeline.
	local amount =
		ModifierRules.RollYield(base, ModifierService.Get(player, def.mastery .. "Yield", "DropQuantity"), rng)
	local remaining = InventoryService.Add(player, { catalogId = def.material, quantity = amount })
	if remaining >= amount then
		InventoryService.Notify(player, "No room for " .. def.material .. ".")
		return
	end
	ProgressionService.GrantXp(player, ProgressionService.XP.Harvest, "Gathering")
	ProgressionService.GrantMastery(player, def.mastery, 1)
	node.hitsLeft -= 1
	if node.hitsLeft <= 0 then
		setActive(node, false)
		task.delay(NodeCatalog.RESPAWN_SECONDS, function()
			node.hitsLeft = def.hits
			setActive(node, true)
		end)
	end
end

local function register(part: BasePart, nodeType: string)
	local def = NodeCatalog.Nodes[nodeType]
	if def == nil then
		warn("[ResourceService] Unknown node type " .. tostring(nodeType))
		return
	end
	local prompt = Instance.new("ProximityPrompt")
	prompt.ActionText = "Harvest"
	prompt.ObjectText = nodeType
	prompt.HoldDuration = 0
	prompt.MaxActivationDistance = NodeCatalog.HARVEST_RANGE - 2
	prompt.RequiresLineOfSight = false
	prompt.Parent = part
	local node = { part = part, nodeType = nodeType, hitsLeft = def.hits, prompt = prompt, active = true }
	prompt.Triggered:Connect(function(player)
		harvest(player, node)
	end)
	table.insert(nodes, node)
end

local function groundPoint(radius: number): Vector3?
	local angle = rng:NextNumber(0, math.pi * 2)
	local distance = radius * math.sqrt(rng:NextNumber())
	local origin = Vector3.new(math.cos(angle) * distance, 1000, math.sin(angle) * distance)
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	params.FilterDescendantsInstances = { workspace:FindFirstChild("ResourceNodes") }
	local hit = workspace:Raycast(origin, Vector3.new(0, -2000, 0), params)
	if hit and hit.Material ~= Enum.Material.Water and hit.Position.Y > -50 then
		return hit.Position
	end
	return nil
end

local function scatter()
	local folder = Instance.new("Folder")
	folder.Name = "ResourceNodes"
	folder.Parent = workspace
	local radius = workspace:GetAttribute("FlintbornMapRadius") or ResourceService.DEFAULT_MAP_RADIUS
	for nodeType, count in ResourceService.SCATTER do
		local look = LOOKS[nodeType]
		for _ = 1, count do
			local position = groundPoint(radius)
			if position then
				local part = Instance.new("Part")
				part.Name = nodeType
				part.Anchored = true
				part.Shape = look.shape
				part.Size = look.size
				part.Color = look.color
				part.CFrame = if look.shape == Enum.PartType.Cylinder
					then CFrame.new(position + Vector3.new(0, look.size.Y / 2, 0)) * CFrame.Angles(0, 0, math.rad(90))
					else CFrame.new(position + Vector3.new(0, look.size.Y / 2, 0))
				if look.shape == Enum.PartType.Cylinder then
					part.Size = Vector3.new(look.size.Y, look.size.X, look.size.Z)
				end
				part:SetAttribute("NodeType", nodeType)
				part.Parent = folder
				register(part, nodeType)
			end
		end
	end
end

function ResourceService.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
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
	Players.PlayerRemoving:Connect(function(player)
		lastHit[player] = nil
	end)
end

return ResourceService
