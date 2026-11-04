-- Server half of Shared.Resources.NodeCatalog: what only the server uses. Everything in
-- ReplicatedStorage is downloaded to every player, so the shared module keeps
-- only what clients need; this one clones it and adds the rest, and server code
-- requires this module.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local GameConstants = require(ReplicatedStorage.Shared.GameConstants)
local SharedNodeCatalog = require(ReplicatedStorage.Shared.Resources.NodeCatalog)

local NodeCatalog = table.clone(SharedNodeCatalog)

local REGROW = GameConstants.NODE_REGROW_SECONDS

-- Placeholder looks until the real models arrive: every node type has its own
-- shape, colour and material so ores read apart at a glance.
local P = Enum.PartType
local M = Enum.Material

local function look(shape, material, size: Vector3, r: number, g: number, b: number)
	return { size = size, color = Color3.fromRGB(r, g, b), shape = shape, material = material }
end

local SHRUB = Vector3.new(3, 3, 3)
local MUSHROOMS = Vector3.new(2, 2, 2)
NodeCatalog.Looks = {
	Tree = look(P.Cylinder, M.Wood, Vector3.new(3, 14, 3), 110, 78, 46),
	Rock = look(P.Block, M.Rock, Vector3.new(6, 4, 6), 128, 126, 120),
	FiberPlant = look(P.Block, M.Grass, Vector3.new(2, 3, 2), 130, 170, 80),
	HerbShrub = look(P.Ball, M.Grass, Vector3.new(3, 2, 3), 70, 140, 90),
	RedberryBush = look(P.Ball, M.Grass, SHRUB, 150, 50, 80),
	SweetberryBush = look(P.Ball, M.Grass, SHRUB, 200, 120, 160),
	CopperDeposit = look(P.Block, M.Slate, Vector3.new(5, 4, 5), 184, 115, 72),
	IronDeposit = look(P.Block, M.CorrodedMetal, Vector3.new(5, 4, 5), 112, 96, 90),
	SilverDeposit = look(P.Block, M.Metal, Vector3.new(5, 5, 5), 196, 200, 206),
	CobaltDeposit = look(P.Block, M.Slate, Vector3.new(5, 5, 5), 70, 96, 180),
	MithrilDeposit = look(P.Block, M.Foil, Vector3.new(5, 6, 5), 150, 210, 220),
	ObsidianOutcrop = look(P.Block, M.Glass, Vector3.new(5, 4, 5), 30, 26, 40),
	JadeVein = look(P.Block, M.Glass, Vector3.new(4, 5, 4), 70, 190, 130),
	ClayDeposit = look(P.Block, M.Mud, Vector3.new(5, 2, 5), 176, 112, 82),
	AmethystGeode = look(P.Ball, M.Glass, Vector3.new(4, 4, 4), 150, 90, 200),
	StarstoneOutcrop = look(P.Block, M.Neon, Vector3.new(4, 5, 4), 240, 228, 160),
	StormglassCluster = look(P.Block, M.Glass, Vector3.new(3, 6, 3), 90, 160, 215),
	CaveMushroomPatch = look(P.Ball, M.SmoothPlastic, MUSHROOMS, 214, 204, 184),
	RedcapMushroomPatch = look(P.Ball, M.SmoothPlastic, MUSHROOMS, 190, 40, 40),
	ChestnutMushroomPatch = look(P.Ball, M.SmoothPlastic, MUSHROOMS, 140, 90, 50),
	ThornShrub = look(P.Ball, M.Grass, SHRUB, 92, 110, 58),
	FrostShrub = look(P.Ball, M.Ice, SHRUB, 190, 222, 240),
	JuniperShrub = look(P.Ball, M.Grass, SHRUB, 60, 100, 110),
	ElderberryShrub = look(P.Ball, M.Grass, SHRUB, 72, 50, 92),
	RaspberryBush = look(P.Ball, M.Grass, SHRUB, 214, 64, 96),
	HazelShrub = look(P.Ball, M.Grass, SHRUB, 150, 130, 70),
}

-- True when `tool` can gather `nodeType` at all (ores need their pickaxe tier).
function NodeCatalog.CanHarvest(nodeType: string, tool): boolean
	return NodeCatalog.YieldFor(nodeType, tool) > 0
end

-- A fresh node's health.
function NodeCatalog.Health(nodeType: string): number
	local node = NodeCatalog.Nodes[nodeType]
	return node and node.health or 0
end

-- Seconds until a depleted node regrows.
function NodeCatalog.RegrowSeconds(nodeType: string): number
	local node = NodeCatalog.Nodes[nodeType]
	return node and node.regrow or REGROW.Basic
end

-- The extra stacks one successful hit gives: the per-hit `bonus` roll and, when
-- the hit depletes the node, its `finishBonus`.
function NodeCatalog.Extras(nodeType: string, depletes: boolean, rng)
	local node = NodeCatalog.Nodes[nodeType]
	local extras = {}
	if node == nil then
		return extras
	end
	if node.bonus and rng:NextNumber() < node.bonus.chance then
		table.insert(extras, { catalogId = node.bonus.catalogId, quantity = node.bonus.quantity or 1 })
	end
	if depletes and node.finishBonus then
		table.insert(extras, { catalogId = node.finishBonus.catalogId, quantity = node.finishBonus.quantity or 1 })
	end
	return extras
end

-- One hit on `nodeType` with `health` left (GDD §53). Returns nil when `tool`
-- cannot gather it; otherwise the stacks to drop on the ground (the material
-- first, then any Flint or Resin), the health the hit removed and the health
-- left. The last hit only drops what is left. `extraChance` is gathering
-- mastery's chance of one extra material, which does not use health.
function NodeCatalog.Hit(nodeType: string, health: number, tool, extraChance: number?, rng)
	local node = NodeCatalog.Nodes[nodeType]
	local amount = math.min(NodeCatalog.YieldFor(nodeType, tool), health)
	if node == nil or amount <= 0 then
		return nil
	end
	local left = health - amount
	local extra = if rng:NextNumber() < (extraChance or 0) then 1 else 0
	local stacks = { { catalogId = node.material, quantity = amount + extra } }
	for _, bonus in NodeCatalog.Extras(nodeType, left <= 0, rng) do
		table.insert(stacks, bonus)
	end
	return { stacks = stacks, removed = amount, health = left, depleted = left <= 0 }
end

return NodeCatalog
