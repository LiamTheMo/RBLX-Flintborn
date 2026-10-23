-- Pure building rules (GDD §6.2, §3.1, §22.4, Q39, Q144–146, Q159). Pieces rotate in
-- 90° steps, so every footprint is an axis-aligned box. Totems stop decay for
-- their own tribe's structures only; they never stop raids. A structure that
-- loses cover gets one 240–360 s deadline and is then removed outright; regaining
-- cover clears it. Uncovered structures can be claimed by another tribe's totem,
-- never while a totem of their owner still covers them. Server-generated
-- structures are never claimable and never decay. A piece must stand in the open:
-- no more than GROUND_ALLOWANCE studs sunk into the ground, visible from the
-- builder, and with no part of its footprint in a safe zone; each owner may keep
-- at most MAX_TOTEMS_PER_OWNER totems.

local GameConstants = require(script.Parent.Parent.GameConstants)
local StructureCatalog = require(script.Parent.StructureCatalog)

local BuildRules = {}

BuildRules.GRID = 4
BuildRules.REACH = 24
BuildRules.AURA_RADIUS = GameConstants.PORTAL_NO_BUILD_METERS * GameConstants.STUDS_PER_METER
BuildRules.MAX_TOTEMS_PER_OWNER = 3
-- How far a piece may sit into the ground (slopes and tile steps).
BuildRules.GROUND_ALLOWANCE = 1
-- Clearance boxes shrink by this on each side so flush neighbours do not collide.
BuildRules.CLEARANCE_INSET = 0.25
-- A line-of-sight ray may stop this close to the target point (grazing its ground).
BuildRules.SIGHT_TOLERANCE = 2

function BuildRules.Snap(position: Vector3): Vector3
	local grid = BuildRules.GRID
	return Vector3.new(
		math.round(position.X / grid) * grid,
		math.round(position.Y * 2) / 2,
		math.round(position.Z / grid) * grid
	)
end

-- Half-size of a footprint after `steps` quarter turns.
function BuildRules.HalfExtents(size: Vector3, steps: number): Vector3
	if steps % 2 == 1 then
		return Vector3.new(size.Z / 2, size.Y / 2, size.X / 2)
	end
	return Vector3.new(size.X / 2, size.Y / 2, size.Z / 2)
end

-- Horizontal distance from `point` to the nearest part of the footprint.
function BuildRules.HorizontalDistance(point: Vector3, center: Vector3, half: Vector3): number
	local dx = math.max(math.abs(point.X - center.X) - half.X, 0)
	local dz = math.max(math.abs(point.Z - center.Z) - half.Z, 0)
	return math.sqrt(dx * dx + dz * dz)
end

-- True when any part of the footprint enters a no-build aura (not just its centre).
function BuildRules.OverlapsAura(center: Vector3, half: Vector3, auras): boolean
	for _, aura in auras do
		if BuildRules.HorizontalDistance(aura.center, center, half) < aura.radius then
			return true
		end
	end
	return false
end

-- The box that must be free of world geometry for a piece at `center`: the whole
-- piece above its bottom GROUND_ALLOWANCE studs. Returns (boxCenter, boxSize).
function BuildRules.ClearanceBox(center: Vector3, half: Vector3): (Vector3, Vector3)
	local inset = BuildRules.CLEARANCE_INSET
	local top = center.Y + half.Y - inset
	local bottom = math.min(center.Y - half.Y + math.min(BuildRules.GROUND_ALLOWANCE, half.Y), top - 0.2)
	return Vector3.new(center.X, (top + bottom) / 2, center.Z),
		Vector3.new(math.max(half.X - inset, 0.05) * 2, top - bottom, math.max(half.Z - inset, 0.05) * 2)
end

-- Sample points covering a footprint box: centre, 8 corners and 6 face centres,
-- so a zone touching any corner of the piece is found, not just its centre.
function BuildRules.FootprintPoints(center: Vector3, half: Vector3)
	local points = { center }
	for _, x in { -1, 1 } do
		for _, y in { -1, 1 } do
			for _, z in { -1, 1 } do
				table.insert(points, center + Vector3.new(half.X * x, half.Y * y, half.Z * z))
			end
		end
	end
	for _, sign in { -1, 1 } do
		table.insert(points, center + Vector3.new(half.X * sign, 0, 0))
		table.insert(points, center + Vector3.new(0, half.Y * sign, 0))
		table.insert(points, center + Vector3.new(0, 0, half.Z * sign))
	end
	return points
end

-- True when `point` lies inside the axis-aligned box.
function BuildRules.BoxContains(center: Vector3, half: Vector3, point: Vector3): boolean
	return math.abs(point.X - center.X) <= half.X
		and math.abs(point.Y - center.Y) <= half.Y
		and math.abs(point.Z - center.Z) <= half.Z
end

-- A sight ray from the builder that stopped at `hitDistance` (nil: nothing hit)
-- on its way to a target `targetDistance` away still sees the target.
function BuildRules.InSight(hitDistance: number?, targetDistance: number): boolean
	return hitDistance == nil or hitDistance >= targetDistance - BuildRules.SIGHT_TOLERANCE
end

-- The owner key of a player who is in no tribe.
function BuildRules.SoloKey(userId: number): string
	return "solo:" .. userId
end

-- True when a player (current owner key `playerKey`, `userId`) controls a structure
-- owned by `ownerKey`: it is their current key's, or their own solo key still owns
-- it (a solo builder who later joined a tribe keeps their doors and totems). Pieces
-- built for a tribe stay the tribe's: a member who leaves or is kicked loses them.
function BuildRules.Controls(playerKey: string, userId: number, ownerKey: string): boolean
	return ownerKey == playerKey or ownerKey == BuildRules.SoloKey(userId)
end

-- True when `ownerKey` already has the maximum number of totems.
function BuildRules.TotemLimitReached(totems, ownerKey: string): boolean
	local count = 0
	for _, totem in totems do
		if totem.ownerKey == ownerKey then
			count += 1
		end
	end
	return count >= BuildRules.MAX_TOTEMS_PER_OWNER
end

-- Structures whose cover a change to `totem` (placed, upgraded, removed) can affect.
function BuildRules.WithinTotem(structures, totem)
	local list = {}
	for _, structure in structures do
		local dx, dz = structure.position.X - totem.position.X, structure.position.Z - totem.position.Z
		if math.sqrt(dx * dx + dz * dz) <= totem.radius then
			table.insert(list, structure)
		end
	end
	return list
end

function BuildRules.Covers(totem, position: Vector3): boolean
	local dx, dz = position.X - totem.position.X, position.Z - totem.position.Z
	return totem.hp > 0 and math.sqrt(dx * dx + dz * dz) <= totem.radius
end

-- A standing totem of the structure's own owner that covers it, if any.
function BuildRules.CoveringTotem(structure, totems)
	if structure.generated or structure.ownerKey == nil then
		return nil
	end
	for _, totem in totems do
		if totem.ownerKey == structure.ownerKey and BuildRules.Covers(totem, structure.position) then
			return totem
		end
	end
	return nil
end

function BuildRules.DecayDeadline(now: number, rng): number
	return now + rng:NextInteger(GameConstants.UNCLAIMED_DECAY_MIN_SECONDS, GameConstants.UNCLAIMED_DECAY_MAX_SECONDS)
end

-- Updates one structure's decay deadline from current cover. A deadline already
-- running is never re-rolled (no repeated resets); only cover clears it.
function BuildRules.Reconcile(structure, totems, now: number, rng)
	if structure.generated or structure.isTotem then
		structure.decayDeadline = nil
		return
	end
	if BuildRules.CoveringTotem(structure, totems) then
		structure.decayDeadline = nil
	elseif structure.decayDeadline == nil then
		structure.decayDeadline = BuildRules.DecayDeadline(now, rng)
	end
end

-- Claims structures inside `totem` that no totem of their owner still covers.
-- Returns the structures that changed owner.
function BuildRules.Claim(structures, totem, totems)
	local claimed = {}
	for _, structure in structures do
		local claimable = not structure.generated
			and not structure.isTotem
			and structure.ownerKey ~= totem.ownerKey
			and BuildRules.Covers(totem, structure.position)
			and BuildRules.CoveringTotem(structure, totems) == nil
		if claimable then
			structure.ownerKey = totem.ownerKey
			table.insert(claimed, structure)
		end
	end
	return claimed
end

function BuildRules.TotemLevel(level: number)
	return StructureCatalog.TotemLevels[level]
end

-- The cost of upgrading from `level` to the next level, or nil at max.
function BuildRules.UpgradeCost(level: number)
	local nextLevel = StructureCatalog.TotemLevels[level + 1]
	return nextLevel and nextLevel.cost or nil
end

-- Raw weapon damage against a structure; a matching tool hits 1.5× (axe vs wood,
-- pickaxe vs stone and iron).
function BuildRules.StructureDamage(rawDamage: number, toolKind: string?, material: string): number
	local matches = (toolKind == "Axe" and material == "Wood")
		or (toolKind == "Pickaxe" and (material == "Stone" or material == "Iron"))
	return rawDamage * (if matches then 1.5 else 1)
end

-- Crop harvests grant XP and Farming mastery at most this often per player, so a
-- field of planters does not scale progression with its size.
BuildRules.CROP_CREDIT_WINDOW = 60
BuildRules.CROP_CREDITS_PER_WINDOW = 6

-- Spends one harvest credit from `ledger` ({since, count}); false when the
-- window's credits are used up (the crop itself is still harvested).
function BuildRules.TakeCropCredit(ledger, now: number): boolean
	if ledger.since == nil or now - ledger.since >= BuildRules.CROP_CREDIT_WINDOW then
		ledger.since, ledger.count = now, 0
	end
	if ledger.count >= BuildRules.CROP_CREDITS_PER_WINDOW then
		return false
	end
	ledger.count += 1
	return true
end

-- Seconds left until a crop planted at `plantedAt` is ripe.
function BuildRules.CropRemaining(crop, plantedAt: number, now: number): number
	return math.max(0, plantedAt + crop.seconds - now)
end

return BuildRules
