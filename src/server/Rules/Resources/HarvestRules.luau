-- Server half of Shared.Resources.HarvestRules: what only the server uses. Everything in
-- ReplicatedStorage is downloaded to every player, so the shared module keeps
-- only what clients need; this one clones it and adds the rest, and server code
-- requires this module.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local NodeCatalog = require(script.Parent.NodeCatalog)
local SharedHarvestRules = require(ReplicatedStorage.Shared.Resources.HarvestRules)

local HarvestRules = table.clone(SharedHarvestRules)

HarvestRules.TARGETS = {
	-- Gathering gear and empty hands: the node before a structure.
	Gathering = { "Player", "Npc", "Node", "Structure" },
	-- Weapons: the structure before a node.
	Weapon = { "Player", "Npc", "Structure", "Node" },
	-- Inside a safe zone only gathering is allowed.
	Safe = { "Node" },
}

-- The kinds of target one swing tries, in order. `isWeapon` is true for a held
-- weapon (not a tool or empty hands).
function HarvestRules.TargetOrder(isWeapon: boolean, inSafeZone: boolean): { string }
	if inSafeZone then
		return HarvestRules.TARGETS.Safe
	end
	return if isWeapon then HarvestRules.TARGETS.Weapon else HarvestRules.TARGETS.Gathering
end

-- What one swing does among nodes (server). `canHarvest(candidate)` says whether
-- the held tool can gather it (NodeCatalog.CanHarvest); `structureDistance` is the
-- horizontal distance to the structure this swing would otherwise hit (nil: none).
-- Returns (node to harvest?, gated node?): the closest node the tool can gather,
-- when it is nearer than the structure; otherwise, only when no structure takes
-- the swing, the node in front the tool cannot gather, for its gate notice.
function HarvestRules.Choose(
	origin,
	flatAim,
	reach: number,
	candidates,
	canHarvest: (any) -> boolean,
	canSee: ((any) -> boolean)?,
	structureDistance: number?
): (any, any)
	local node = HarvestRules.Pick(origin, flatAim, reach, candidates, function(candidate)
		return canHarvest(candidate) and (canSee == nil or canSee(candidate))
	end)
	if
		node
		and (structureDistance == nil or HarvestRules.FlatDistance(origin, node.center, node.half) < structureDistance)
	then
		return node, nil
	end
	if structureDistance ~= nil then
		return nil, nil
	end
	local gated = HarvestRules.Pick(origin, flatAim, reach, candidates, canSee)
	if gated and not canHarvest(gated) then
		return nil, gated
	end
	return nil, nil
end

-- True when a player who last harvested at `lastAt` may harvest again at `now`
-- (strict: no jitter slack, so a scripted client gains no yield).
function HarvestRules.CadenceReady(lastAt: number?, now: number): boolean
	return lastAt == nil or now - lastAt >= NodeCatalog.HARVEST_INTERVAL
end

-- "IronDeposit" -> "Iron Deposit".
function HarvestRules.DisplayName(nodeType: string): string
	return (nodeType:gsub("(%l)(%u)", "%1 %2"))
end

-- The verb a swing does to the node: Mine, Chop or Gather.
function HarvestRules.Action(nodeType: string): string
	local def = NodeCatalog.Nodes[nodeType]
	if def and (def.minRank or def.tool == "Pickaxe") then
		return "Mine"
	elseif def and def.tool == "Axe" then
		return "Chop"
	end
	return "Gather"
end

-- "Copper Pickaxe+" for a gated ore or gem, nil for anything bare hands gather.
function HarvestRules.GateLabel(nodeType: string): string?
	local def = NodeCatalog.Nodes[nodeType]
	if def and def.minRank then
		return NodeCatalog.PickaxeName(def.minRank) .. "+"
	end
	return nil
end

-- The plaque's object line: "Iron Deposit · Copper Pickaxe+" so the gate shows
-- before the first swing.
function HarvestRules.Label(nodeType: string): string
	local gate = HarvestRules.GateLabel(nodeType)
	local name = HarvestRules.DisplayName(nodeType)
	return if gate then ("%s · %s"):format(name, gate) else name
end

return HarvestRules
