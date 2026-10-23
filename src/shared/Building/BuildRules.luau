-- Pure building rules (GDD §6.2, §3.1, §22.4, Q39, Q144–146, Q159). Pieces rotate in
-- 90° steps, so every footprint is an axis-aligned box. Totems stop decay for
-- their own tribe's structures only; they never stop raids. A structure that
-- loses cover gets one 240–360 s deadline and is then removed outright; regaining
-- cover clears it. Uncovered structures can be claimed by another tribe's totem,
-- never while a totem of their owner still covers them. Server-generated
-- structures are never claimable and never decay.

local GameConstants = require(script.Parent.Parent.GameConstants)
local StructureCatalog = require(script.Parent.StructureCatalog)

local BuildRules = {}

BuildRules.GRID = 4
BuildRules.REACH = 24
BuildRules.AURA_RADIUS = GameConstants.PORTAL_NO_BUILD_METERS * GameConstants.STUDS_PER_METER

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

-- Seconds left until a crop planted at `plantedAt` is ripe.
function BuildRules.CropRemaining(crop, plantedAt: number, now: number): number
	return math.max(0, plantedAt + crop.seconds - now)
end

return BuildRules
