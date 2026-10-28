-- Pure event director rules (GDD §7.1, §51, Q42, Q140–143), driven by an injected
-- Random so specs can seed it. Every category rolls on its own each tick: ~25% to
-- trigger, then every non-Common entry rolls its own rarity weight, so event types
-- never compete with others of their category or rarity (owner decision, GDD §51)
-- and several may start at once. Common is the fallback when nothing rarer hits;
-- a category without one skips.

local GameConstants = require(script.Parent.Parent.GameConstants)
local Rarity = require(script.Parent.Parent.Items.Rarity)

local EventRules = {}

EventRules.TRIGGER_CHANCE = GameConstants.EVENT_CATEGORY_TRIGGER_CHANCE
EventRules.TICK_SECONDS = GameConstants.EVENT_CHECK_SECONDS

-- Each entry's chance once its category triggers, by rarity (placeholder weights).
-- An entry of a rarity listed here starts as often as the whole rarity used to.
EventRules.RARITY_WEIGHTS = {
	Secret = 0.001,
	Mythic = 0.005,
	Legendary = 0.015,
	Epic = 0.05,
	Rare = 0.12,
	Uncommon = 0.25,
}

-- Budget per server (placeholders): event NPCs alive and large-footprint events.
EventRules.MAX_EVENT_NPCS = 40
EventRules.MAX_LARGE_EVENTS = 6
EventRules.LARGE_FOOTPRINT = 80

-- Regions as fractions of the map radius (Shattered Crater: crater 300, inner ring
-- 750, outer rim 1,200 studs; v0.15).
EventRules.BIOMES = {
	Center = { 0.03, 0.22 },
	InnerRing = { 0.28, 0.6 },
	OuterRim = { 0.65, 0.9 },
	Any = { 0.03, 0.9 },
}

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

-- Rarest first, keeping catalog order within a rarity.
local function byRarity(list)
	local order = {}
	for index, entry in list do
		order[entry] = index
	end
	table.sort(list, function(a, b)
		local ra, rb = Rarity.Index(a.rarity) or 0, Rarity.Index(b.rarity) or 0
		if ra ~= rb then
			return ra > rb
		end
		return order[a] < order[b]
	end)
	return list
end

-- One category's roll for one tick: the entries that start, rarest first (empty
-- when the category does not trigger or has no Common to fall back on).
function EventRules.RollCategory(entries, rng)
	local results = {}
	if #entries == 0 or rng:NextNumber() >= EventRules.TRIGGER_CHANCE then
		return results
	end
	for _, entry in entries do
		-- Every non-Common type rolls on its own; unlisted rarities never roll.
		local weight = EventRules.RARITY_WEIGHTS[entry.rarity]
		if weight and rng:NextNumber() < weight then
			table.insert(results, entry)
		end
	end
	if #results == 0 then
		local common = pick(entries, "Common", rng)
		if common then
			table.insert(results, common)
		end
	end
	return byRarity(results)
end

-- Every category rolls independently, so several events can start in one tick.
-- Rarest first across categories, so the budget favours them when it runs short.
function EventRules.RollTick(catalog, categories, rng)
	local results = {}
	for _, category in categories do
		for _, entry in EventRules.RollCategory(catalog[category] or {}, rng) do
			table.insert(results, entry)
		end
	end
	return byRarity(results)
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

-- True when a footprint at `position` stays outside every zone {center, radius}
-- (extraction auras, safe zones, the Guardian arena, totem cover).
function EventRules.ClearOf(position: Vector3, radius: number, zones): boolean
	for _, zone in zones do
		local dx, dz = position.X - zone.center.X, position.Z - zone.center.Z
		if math.sqrt(dx * dx + dz * dz) < radius + zone.radius then
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

-- Rolls a loot table into {catalogId, quantity} stacks. `luck` (the Fortune perk
-- and luck boosts) raises each row's chance relatively, never above certain.
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
