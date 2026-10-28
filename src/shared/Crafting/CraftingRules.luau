-- Crafting stations, timed smelting and the crafting menu's grouping (GDD §16.8,
-- §51). A recipe with a station needs a built piece of that name within
-- STATION_RANGE studs; each station piece is tagged with its own name. Smelting
-- costs only time: a job makes `count` outputs one after another, each taking the
-- recipe's `seconds`, and takes each unit's inputs in the same server step that
-- grants its output, so a stopped job never owes or refunds anything. A job runs
-- only while its crafter stays alive, in the run and near the station it started
-- at, and each player runs one job at a time.

local ItemCatalog = require(script.Parent.Parent.Items.ItemCatalog)
local Tiers = require(script.Parent.Parent.Items.Tiers)
local Recipes = require(script.Parent.Recipes)

local CraftingRules = {}

-- Built pieces that serve as crafting stations, in menu order.
CraftingRules.STATIONS = { Recipes.Workbench, Recipes.Furnace, Recipes.Anvil, Recipes.Cauldron }
-- How close a crafter must stand to a station (studs, from the station's centre).
CraftingRules.STATION_RANGE = 12
-- Most units one smelting request may queue.
CraftingRules.MAX_BATCH = 50

local isStation = {}
for _, station in CraftingRules.STATIONS do
	isStation[station] = true
end

function CraftingRules.IsStation(pieceId: any): boolean
	return isStation[pieceId] == true
end

-- The station tag a recipe needs, or nil when it crafts anywhere.
function CraftingRules.StationFor(recipe): string?
	return if isStation[recipe.station] then recipe.station else nil
end

-- The refusal code for crafting away from `station` ("NeedsAnvil").
function CraftingRules.Refusal(station: string): string
	return "Needs" .. station
end

function CraftingRules.IsTimed(recipe): boolean
	return type(recipe.seconds) == "number" and recipe.seconds > 0
end

-- Validates a requested count: nil means 1, 0 asks to stop the running job, and
-- only timed recipes take more than one. Returns nil when the count is not allowed.
function CraftingRules.BatchCount(recipe, count: any): number?
	if count == nil then
		return 1
	end
	if type(count) ~= "number" or count % 1 ~= 0 or count < 0 then
		return nil
	end
	local most = if CraftingRules.IsTimed(recipe) then CraftingRules.MAX_BATCH else 1
	return if count <= most then count else nil
end

-- A recipe's inputs for `count` units.
function CraftingRules.BatchInputs(recipe, count: number)
	local inputs = {}
	for catalogId, amount in recipe.inputs do
		inputs[catalogId] = amount * count
	end
	return inputs
end

function CraftingRules.TotalSeconds(recipe, count: number): number
	return (recipe.seconds or 0) * count
end

-- A new smelting job; `station` is the station part it is bound to.
function CraftingRules.NewJob(recipe, count: number, now: number, station: any, character: any)
	return {
		recipe = recipe,
		count = count,
		done = 0,
		unitEndsAt = now + recipe.seconds,
		station = station,
		character = character,
	}
end

-- Why a running job must stop, or nil. `check` holds what the server sees now:
-- atRisk (still in the run), sameCharacter, alive, downed, stationStanding and
-- distance (studs from the station).
function CraftingRules.Interruption(check): string?
	if not check.atRisk then
		return "NotInRun"
	end
	if not check.sameCharacter or not check.alive then
		return "Died"
	end
	if check.downed then
		return "Downed"
	end
	if not check.stationStanding then
		return "StationGone"
	end
	if type(check.distance) ~= "number" or check.distance > CraftingRules.STATION_RANGE then
		return "MovedAway"
	end
	return nil
end

-- True when the job's current unit is finished.
function CraftingRules.UnitDue(job, now: number): boolean
	return job.done < job.count and now >= job.unitEndsAt
end

-- Records one finished unit and starts the next. True when the job is complete.
function CraftingRules.Advance(job): boolean
	job.done += 1
	if job.done >= job.count then
		return true
	end
	job.unitEndsAt += job.recipe.seconds
	return false
end

-- Overall progress (0–1) and seconds left on the current unit, from the values a
-- job publishes (done, count, unitEndsAt, seconds).
function CraftingRules.Progress(done: number, count: number, unitEndsAt: number, seconds: number, now: number)
	local left = math.clamp(unitEndsAt - now, 0, seconds)
	local unit = if seconds > 0 then 1 - left / seconds else 1
	return math.clamp((done + unit) / math.max(count, 1), 0, 1), left
end

-- Menu grouping ---------------------------------------------------------------

CraftingRules.CATEGORIES = {
	{ id = "Weapons", label = "Weapons" },
	{ id = "Tools", label = "Tools" },
	{ id = "Armor", label = "Armor" },
	{ id = "Bars", label = "Smelting" },
	{ id = "Consumables", label = "Food & potions" },
	{ id = "Other", label = "Siege & stations" },
}

local CATEGORY_OF_FAMILY = {
	[ItemCatalog.Families.Weapon] = "Weapons",
	[ItemCatalog.Families.Ammo] = "Weapons",
	[ItemCatalog.Families.Tool] = "Tools",
	[ItemCatalog.Families.Armor] = "Armor",
	[ItemCatalog.Families.Material] = "Bars",
	[ItemCatalog.Families.Consumable] = "Consumables",
}

local categoryIndex = {}
for index, category in CraftingRules.CATEGORIES do
	categoryIndex[category.id] = index
end

local tierOfMaterial = {}
local tierIndex = {}
for index, tier in Tiers.Ladder do
	tierOfMaterial[tier.material] = tier.id
	tierIndex[tier.id] = index
end

function CraftingRules.Category(recipe): string
	local def = ItemCatalog.Get(recipe.output)
	return def and CATEGORY_OF_FAMILY[def.family] or "Other"
end

-- The ladder tier a recipe belongs to (gear by its tier, bars by their metal), or nil.
function CraftingRules.Tier(recipe): string?
	local def = ItemCatalog.Get(recipe.output)
	return def and def.tier or tierOfMaterial[recipe.output]
end

-- The ladder tiers that have at least one recipe, in ladder order.
function CraftingRules.TiersIn(list): { string }
	local present = {}
	for _, recipe in list do
		local tier = CraftingRules.Tier(recipe)
		if tier then
			present[tier] = true
		end
	end
	local tiers = {}
	for _, tier in Tiers.Ladder do
		if present[tier.id] then
			table.insert(tiers, tier.id)
		end
	end
	return tiers
end

-- True when the recipe can be crafted with the stations in `nearby` (a set).
function CraftingRules.AvailableHere(recipe, nearby): boolean
	local station = CraftingRules.StationFor(recipe)
	return station == nil or nearby[station] == true
end

-- True when the recipe passes the menu's filter: {category?, tier?, hereOnly?}.
function CraftingRules.Matches(recipe, filter, nearby): boolean
	if filter.category and CraftingRules.Category(recipe) ~= filter.category then
		return false
	end
	if filter.tier and CraftingRules.Tier(recipe) ~= filter.tier then
		return false
	end
	return not filter.hereOnly or CraftingRules.AvailableHere(recipe, nearby)
end

-- The recipes grouped by category, then by tier up the ladder, keeping list order
-- within a tier.
function CraftingRules.Sorted(list)
	local position = {}
	for index, recipe in list do
		position[recipe] = index
	end
	local sorted = table.clone(list)
	table.sort(sorted, function(a, b)
		local ca, cb = categoryIndex[CraftingRules.Category(a)], categoryIndex[CraftingRules.Category(b)]
		if ca ~= cb then
			return ca < cb
		end
		local ta, tb = tierIndex[CraftingRules.Tier(a) or ""] or 0, tierIndex[CraftingRules.Tier(b) or ""] or 0
		if ta ~= tb then
			return ta < tb
		end
		return position[a] < position[b]
	end)
	return sorted
end

return CraftingRules
