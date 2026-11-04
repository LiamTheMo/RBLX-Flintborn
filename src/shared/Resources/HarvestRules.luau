-- Click harvesting (GDD §4.1, §5.1, §7.6, §53): the attack input also chops,
-- mines and gathers. A swing with whatever is held picks the closest active node
-- in front of the player, measured to the node hitbox's surface (a big rock or a
-- tall tree is reached at its side, not its centre), inside the same 120° arc
-- creatures and structures use. The server picks with these rules and still
-- validates range, cadence, tool gates and node state (ResourceService); the
-- client uses them only for the hover plaque and its own swing pacing.
--
-- Target priority for one swing (CombatService): players and creatures always
-- come first, so a tool never ignores a fight. After that, gathering gear (axes,
-- pickaxes, empty hands) prefers the node in front over a structure, and weapons
-- prefer the structure (raiding, GDD Q38). A node only beats a structure when the
-- held tool can actually gather it and it is the nearer of the two (Choose), so a
-- gated ore beside a wall never shields the wall from a raider's pickaxe. Inside a
-- safe zone nothing takes damage (§3.2), so a swing can only gather, as the old
-- node prompt allowed. A held bow or siege item does not swing, so it never gathers.
-- Pure: plain numbers and Vector3-like values (X, Y, Z, Magnitude, Dot).

local DamageRules = require(script.Parent.Parent.Combat.DamageRules)
local NodeCatalog = require(script.Parent.NodeCatalog)

local HarvestRules = {}

-- Full cone a swing reaches nodes in, as for creatures and structures.
HarvestRules.ARC = 120
-- Latency slack added to the swing's reach (the same as for players).
HarvestRules.REACH_ALLOWANCE = DamageRules.REACH_ALLOWANCE
-- Within this horizontal distance of a node's side it is hit whatever the aim.
HarvestRules.TOUCH_DISTANCE = 1
-- The hover plaque sits this far above the lower of the node's top and the
-- player's root, so a tall tree's plaque stays at eye level.
HarvestRules.LABEL_ABOVE_ROOT = 3
HarvestRules.LABEL_ABOVE_TOP = 1
-- A modelled node's look: a Model of this name under its invisible hitbox (the
-- client outlines it, not the hitbox).
HarvestRules.LOOK_MODEL = "Look"
-- The client paces node swings this much above the server's harvest cadence, so
-- network jitter never makes an honest swing arrive early.
HarvestRules.SWING_SLACK = 0.05

-- How far (to the node's surface) a swing with `weaponReach` harvests: the
-- weapon's reach plus slack, never past the harvest range.
function HarvestRules.Reach(weaponReach: number): number
	return math.min(weaponReach + HarvestRules.REACH_ALLOWANCE, NodeCatalog.HARVEST_RANGE)
end

-- World-axis half extents of a box of `size` whose rotation has these unit
-- columns (CFrame.RightVector, UpVector, LookVector).
function HarvestRules.WorldHalf(right, up, look, size)
	local function axis(r: number, u: number, l: number): number
		return (math.abs(r) * size.X + math.abs(u) * size.Y + math.abs(l) * size.Z) / 2
	end
	return Vector3.new(axis(right.X, up.X, look.X), axis(right.Y, up.Y, look.Y), axis(right.Z, up.Z, look.Z))
end

local function clearance(value: number, center: number, half: number): number
	return math.max(math.abs(value - center) - half, 0)
end

-- Distance from `point` to the surface of the box at `center` with half extents
-- `half` (0 inside it).
function HarvestRules.SurfaceDistance(point, center, half): number
	local dx = clearance(point.X, center.X, half.X)
	local dy = clearance(point.Y, center.Y, half.Y)
	local dz = clearance(point.Z, center.Z, half.Z)
	return math.sqrt(dx * dx + dy * dy + dz * dz)
end

-- Horizontal distance from `point` to the box's footprint.
function HarvestRules.FlatDistance(point, center, half): number
	local dx = clearance(point.X, center.X, half.X)
	local dz = clearance(point.Z, center.Z, half.Z)
	return math.sqrt(dx * dx + dz * dz)
end

-- True when the box lies in front of `origin` along `flatAim`: touching it, or
-- its centre or the closest point of its footprint inside the arc.
function HarvestRules.InArc(origin, flatAim, center, half, arc: number?): boolean
	local degrees = arc or HarvestRules.ARC
	if HarvestRules.FlatDistance(origin, center, half) < HarvestRules.TOUCH_DISTANCE then
		return true
	end
	if DamageRules.WithinArc(flatAim, Vector3.new(center.X - origin.X, 0, center.Z - origin.Z), degrees) then
		return true
	end
	local nearX = math.clamp(origin.X, center.X - half.X, center.X + half.X)
	local nearZ = math.clamp(origin.Z, center.Z - half.Z, center.Z + half.Z)
	return DamageRules.WithinArc(flatAim, Vector3.new(nearX - origin.X, 0, nearZ - origin.Z), degrees)
end

-- The closest candidate ({center, half, active}) a swing from `origin` along
-- `flatAim` reaches within `reach` studs of its surface, and that distance.
-- Inactive (depleted) candidates are skipped; `canSee(candidate)` is asked last,
-- only for one that would win, since it costs a raycast.
function HarvestRules.Pick(origin, flatAim, reach: number, candidates, canSee: ((any) -> boolean)?): (any, number)
	local best, bestDistance = nil, math.huge
	for _, candidate in candidates do
		if candidate.active == false then
			continue
		end
		local distance = HarvestRules.SurfaceDistance(origin, candidate.center, candidate.half)
		if
			distance <= reach
			and distance < bestDistance
			and HarvestRules.InArc(origin, flatAim, candidate.center, candidate.half)
			and (canSee == nil or canSee(candidate))
		then
			best, bestDistance = candidate, distance
		end
	end
	return best, bestDistance
end

-- Seconds between the client's swings: the item's cooldown, slowed to just above
-- the harvest cadence while a node is in front (and no fight is) so no swing is
-- wasted.
function HarvestRules.SwingInterval(cooldown: number, atNode: boolean): number
	return if atNode then math.max(cooldown, NodeCatalog.HARVEST_INTERVAL + HarvestRules.SWING_SLACK) else cooldown
end

-- True when a creature or player whose body is `flatDistance` studs away
-- (horizontally, to its side) along `offset` is one a swing with `reach` would
-- hit (the client's guess: a fight in front keeps the item's own pace).
function HarvestRules.FightInFront(flatAim, offset, flatDistance: number, reach: number): boolean
	return flatDistance <= reach + HarvestRules.REACH_ALLOWANCE
		and (
			flatDistance < HarvestRules.TOUCH_DISTANCE
			or DamageRules.WithinArc(flatAim, Vector3.new(offset.X, 0, offset.Z), HarvestRules.ARC)
		)
end

-- World height of the hover plaque for a node centred at `centerY` with half
-- height `halfY`, seen by a player whose root is at `rootY`.
function HarvestRules.LabelHeight(centerY: number, halfY: number, rootY: number): number
	return math.min(centerY + halfY + HarvestRules.LABEL_ABOVE_TOP, rootY + HarvestRules.LABEL_ABOVE_ROOT)
end

-- The touch attack button's icon for the held tool kind (nil: a weapon or hands).
function HarvestRules.AttackIcon(toolKind: string?): string
	if toolKind == "Axe" then
		return "stone_axe"
	elseif toolKind == "Pickaxe" then
		return "pickaxe"
	end
	return "spear"
end

return HarvestRules
