-- Pure event director rules (GDD §7.1, Q42, Q140–143), driven by an injected
-- Random so specs can seed it. Every category rolls on its own each tick: ~25% to
-- trigger, then rarities are tried highest first with explicit weights, falling
-- back to Common when the category has one and skipping when it does not.

local GameConstants = require(script.Parent.Parent.GameConstants)

local EventRules = {}

EventRules.TRIGGER_CHANCE = GameConstants.EVENT_CATEGORY_TRIGGER_CHANCE
EventRules.TICK_SECONDS = GameConstants.EVENT_CHECK_SECONDS

-- Tried in this order after a category triggers (placeholder weights).
EventRules.WATERFALL = {
	{ "Secret", 0.001 },
	{ "Mythic", 0.005 },
	{ "Legendary", 0.015 },
	{ "Epic", 0.05 },
	{ "Rare", 0.12 },
	{ "Uncommon", 0.25 },
}

-- Budget per server (placeholders): event NPCs alive and large-footprint events.
EventRules.MAX_EVENT_NPCS = 40
EventRules.MAX_LARGE_EVENTS = 6
EventRules.LARGE_FOOTPRINT = 80

-- Biome rings as fractions of the map radius until the island exists (v0.15).
EventRules.BIOMES = {
	Center = { 0, 0.3 },
	InnerRing = { 0.3, 0.65 },
	OuterRim = { 0.65, 0.95 },
	Any = { 0, 0.95 },
}

local function has(entries, rarity: string): boolean
	for _, entry in entries do
		if entry.rarity == rarity then
			return true
		end
	end
	return false
end

local function pick(entries, rarity: string, rng)
	local matching = {}
	for _, entry in entries do
		if entry.rarity == rarity then
			table.insert(matching, entry)
		end
	end
	if #matching == 0 then
		return nil
	end
	return matching[rng:NextInteger(1, #matching)]
end

-- One category's roll for one tick: an entry, or nil.
function EventRules.RollCategory(entries, rng)
	if #entries == 0 or rng:NextNumber() >= EventRules.TRIGGER_CHANCE then
		return nil
	end
	for _, step in EventRules.WATERFALL do
		local rarity, weight = step[1], step[2]
		-- Rarities a category does not have are not rolled.
		if has(entries, rarity) and rng:NextNumber() < weight then
			return pick(entries, rarity, rng)
		end
	end
	return pick(entries, "Common", rng)
end

-- Every category rolls independently, so several events can start in one tick.
function EventRules.RollTick(catalog, categories, rng)
	local results = {}
	for _, category in categories do
		local entry = EventRules.RollCategory(catalog[category] or {}, rng)
		if entry then
			table.insert(results, entry)
		end
	end
	return results
end

-- True when a footprint at `position` overlaps none of the active ones.
function EventRules.Separated(position: Vector3, radius: number, active): boolean
	for _, other in active do
		local dx, dz = position.X - other.position.X, position.Z - other.position.Z
		if math.sqrt(dx * dx + dz * dz) < radius + other.radius then
			return false
		end
	end
	return true
end

-- Whether another event of `entry` fits the performance budget.
function EventRules.WithinBudget(entry, activeLarge: number, activeNpcs: number, npcCount: number): boolean
	if entry.footprint >= EventRules.LARGE_FOOTPRINT and activeLarge >= EventRules.MAX_LARGE_EVENTS then
		return false
	end
	return activeNpcs + npcCount <= EventRules.MAX_EVENT_NPCS
end

function EventRules.NpcCount(group): number
	local count = 0
	for _, member in group or {} do
		count += member.count
	end
	return count
end

-- Rolls a loot table into {catalogId, quantity} stacks. `luck` (the Fortune
-- perk) raises each row's chance relatively, never above certain.
function EventRules.RollLoot(loot, rng, luck: number?)
	local items = {}
	for _, row in loot or {} do
		local catalogId, low, high, chance = row[1], row[2], row[3], row[4]
		if rng:NextNumber() < math.min(1, chance * (1 + (luck or 0))) then
			table.insert(items, { catalogId = catalogId, quantity = rng:NextInteger(low, high) })
		end
	end
	return items
end

-- A random distance from the centre inside a biome ring, as a fraction of the map.
function EventRules.BiomeDistance(biome: string, rng): number
	local ring = EventRules.BIOMES[biome] or EventRules.BIOMES.Any
	local low, high = ring[1], ring[2]
	-- Uniform over the ring's area, not its radius.
	return math.sqrt(rng:NextNumber() * (high * high - low * low) + low * low)
end

-- Claims a one-time reward exactly once (§7.6): rare nodes never regrow.
function EventRules.Claim(site): boolean
	if site.claimed then
		return false
	end
	site.claimed = true
	return true
end

-- True when a channel that began at `startedAt` has run its full length.
function EventRules.ChannelComplete(startedAt: number?, now: number, seconds: number): boolean
	return startedAt ~= nil and now - startedAt >= seconds - 0.25
end

return EventRules
