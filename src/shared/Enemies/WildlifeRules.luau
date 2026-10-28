-- Roaming wildlife (GDD §54, owner decisions 2026-10-28). Light density: each
-- map zone keeps a few small groups of its regular creatures, chosen by weight
-- from the zone's spawn table and placed in their habitat (IslandLayout); about
-- 40–60 roaming creatures island-wide under a hard cap. A group that is killed or
-- despawned comes back about three minutes later somewhere away from every player
-- and outside safe zones. When the cap is full, groups no player has been near for
-- a while make room. Creature events (EventCatalog) are separate. Counts and
-- timings are placeholders.

local WildlifeRules = {}

-- The world's habitat tags (IslandLayout.RandomPointIn ignores unknown ones).
WildlifeRules.HABITATS = {
	"Beach",
	"Meadow",
	"Grassland",
	"Forest",
	"Jungle",
	"River",
	"Lakeshore",
	"Marsh",
	"Rocky",
	"Highland",
	"Cave",
	"Clearing",
}

-- A dead or despawned group's slot refills after this long.
WildlifeRules.RESPAWN_SECONDS = 180
-- Groups never appear this close (horizontally) to any player.
WildlifeRules.PLAYER_CLEARANCE = 150
-- Roaming creatures alive at once, island-wide.
WildlifeRules.MAX_CREATURES = 60
-- How often the spawner looks at its slots, and how long a failed spawn waits.
WildlifeRules.TICK_SECONDS = 5
WildlifeRules.RETRY_SECONDS = 20
WildlifeRules.PLACEMENT_ATTEMPTS = 8
-- Members spread this far (studs) around the group's spot.
WildlifeRules.GROUP_SPREAD = 8
-- A group with no player within FAR_RADIUS for FAR_IDLE_SECONDS may be despawned
-- to make room under the cap (performance).
WildlifeRules.FAR_RADIUS = 400
WildlifeRules.FAR_IDLE_SECONDS = 300
-- Wildlife with no player this close stands still (NpcService skips its AI).
WildlifeRules.SLEEP_RADIUS = 300

local function spawn(enemy: string, weight: number, min: number, max: number, habitat: string?)
	return { enemy = enemy, weight = weight, min = min, max = max, habitat = habitat }
end

-- zoneId -> {groups = slots kept filled, spawns = {{enemy, weight, min, max, habitat?}}}.
-- Low (Outer Rim): Rimlands, Pinewood Wilds, Mosswick Forest, Riverlands. Medium
-- (Inner Ring): Timberwatch, Fallen Temple, Emberhollow Caves. Extreme (Center
-- Crater): Frostpeak Ridge, Crater Lake, Shattered Keep.
WildlifeRules.Zones = {
	Rimlands = {
		groups = 3,
		spawns = {
			spawn("IslandDodo", 3, 2, 3, "Beach"),
			spawn("MeadowRabbit", 2, 1, 2, "Grassland"),
			spawn("PlainsBison", 2, 1, 3, "Grassland"),
			spawn("ForestStag", 1, 2, 3, "Meadow"),
		},
	},
	PinewoodWilds = {
		groups = 3,
		spawns = {
			spawn("WildBoar", 3, 1, 3, "Forest"),
			spawn("ForestStag", 2, 2, 3, "Clearing"),
			spawn("MeadowRabbit", 1, 1, 2, "Meadow"),
			spawn("IslandDodo", 1, 2, 3, "Forest"),
		},
	},
	MosswickForest = {
		groups = 2,
		spawns = {
			spawn("ForestTapir", 2, 1, 2, "Forest"),
			spawn("WildBoar", 2, 1, 3, "Forest"),
			spawn("ForestStag", 2, 2, 3, "Clearing"),
			spawn("MeadowRabbit", 1, 1, 2, "Clearing"),
		},
	},
	Riverlands = {
		groups = 3,
		spawns = {
			spawn("RiverCapybara", 3, 2, 3, "River"),
			spawn("RiverCrocodile", 2, 1, 2, "River"),
			spawn("RiverCrocodile", 1, 1, 2, "Marsh"),
			spawn("PlainsBison", 2, 1, 3, "Grassland"),
			spawn("MeadowRabbit", 1, 1, 2, "Grassland"),
		},
	},
	Timberwatch = {
		groups = 3,
		spawns = {
			spawn("GreyWolf", 3, 2, 3, "Forest"),
			spawn("BrownBear", 2, 1, 1, "Forest"),
			spawn("ForestTapir", 1, 1, 2, "Forest"),
		},
	},
	FallenTemple = {
		groups = 2,
		spawns = {
			spawn("Skeleton", 3, 2, 3),
			spawn("GreyWolf", 1, 2, 3, "Rocky"),
		},
	},
	EmberhollowCaves = {
		groups = 2,
		spawns = {
			spawn("EmberWisp", 3, 1, 3, "Cave"),
			spawn("BrownBear", 1, 1, 1, "Rocky"),
		},
	},
	FrostpeakRidge = {
		groups = 3,
		spawns = {
			spawn("HighlandGoat", 3, 2, 3, "Highland"),
			spawn("HighlandGoat", 1, 2, 3, "Rocky"),
			spawn("GreyWolf", 1, 2, 3, "Rocky"),
			spawn("BrownBear", 1, 1, 1, "Clearing"),
		},
	},
	CraterLake = {
		groups = 2,
		spawns = {
			spawn("RiverCrocodile", 3, 1, 2, "Lakeshore"),
			spawn("RiverCapybara", 3, 2, 3, "Lakeshore"),
		},
	},
	ShatteredKeep = {
		groups = 2,
		spawns = {
			spawn("KeepSkeleton", 1, 2, 3),
		},
	},
}

-- One weighted pick from a zone's spawn table.
function WildlifeRules.Pick(spawns, rng)
	local total = 0
	for _, entry in spawns do
		total += entry.weight
	end
	local roll = rng:NextNumber() * total
	for _, entry in spawns do
		roll -= entry.weight
		if roll < 0 then
			return entry
		end
	end
	return spawns[#spawns]
end

function WildlifeRules.GroupSize(entry, rng): number
	return rng:NextInteger(entry.min, entry.max)
end

-- The zone of every slot the spawner keeps filled, in a stable order.
function WildlifeRules.Slots(): { string }
	local zoneIds = {}
	for zoneId in WildlifeRules.Zones do
		table.insert(zoneIds, zoneId)
	end
	table.sort(zoneIds)
	local slots = {}
	for _, zoneId in zoneIds do
		for _ = 1, WildlifeRules.Zones[zoneId].groups do
			table.insert(slots, zoneId)
		end
	end
	return slots
end

-- Creatures alive on average with every slot filled.
function WildlifeRules.ExpectedCreatures(): number
	local total = 0
	for _, zone in WildlifeRules.Zones do
		local weight, size = 0, 0
		for _, entry in zone.spawns do
			weight += entry.weight
			size += entry.weight * (entry.min + entry.max) / 2
		end
		total += zone.groups * size / weight
	end
	return total
end

local function flatDistance(a: Vector3, b: Vector3): number
	local dx, dz = a.X - b.X, a.Z - b.Z
	return math.sqrt(dx * dx + dz * dz)
end

-- True when `position` is at least `radius` (horizontally) from every player.
function WildlifeRules.ClearOfPlayers(position: Vector3, playerPositions, radius: number?): boolean
	local clearance = radius or WildlifeRules.PLAYER_CLEARANCE
	for _, other in playerPositions do
		if flatDistance(position, other) < clearance then
			return false
		end
	end
	return true
end

-- True when any of `positions` is within `radius` of any of `others`.
function WildlifeRules.AnyNear(positions, others, radius: number): boolean
	for _, position in positions do
		for _, other in others do
			if flatDistance(position, other) <= radius then
				return true
			end
		end
	end
	return false
end

-- Whether `count` more creatures fit under the cap with `alive` already out.
function WildlifeRules.HasRoom(alive: number, count: number): boolean
	return alive + count <= WildlifeRules.MAX_CREATURES
end

-- Of `groups` ({lastNear}), the one nobody has been near for longest, if that
-- is at least FAR_IDLE_SECONDS; it may be despawned to make room.
function WildlifeRules.MostIdle(groups, now: number)
	local best, bestIdle = nil, WildlifeRules.FAR_IDLE_SECONDS
	for _, group in groups do
		local idle = now - group.lastNear
		if idle >= bestIdle then
			best, bestIdle = group, idle
		end
	end
	return best
end

return WildlifeRules
