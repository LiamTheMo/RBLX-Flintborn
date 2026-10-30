-- What the recipe window (Hud/Screens/RecipeWindow) shows, as pure functions
-- for the client and specs. One entry shape serves both modes:
--   forge     the Ancestral Forge (ForgeSnapshot: vault-only counts, a batch
--             count per request up to the snapshot's maxCount, Permanent
--             conversions take exactly one source item)
--   crafting  field crafting in a run (Recipes, carried counts, stations; only
--             timed recipes (smelting) take a count, CraftingRules.BatchCount)
--
-- entry = {id, kind ("Special" | "Permanent" | "Craft"), category, name, output,
--   quantity, inputs {{catalogId, name, owned, needed}}, locked, requirement,
--   maxCount, batch, verb, here, station, timed, seconds, sources?}

local CraftingRules = require(script.Parent.Parent.Crafting.CraftingRules)
local ForgeRecipes = require(script.Parent.Parent.Crafting.ForgeRecipes)
local ItemCatalog = require(script.Parent.Parent.Items.ItemCatalog)
local ItemInfo = require(script.Parent.Parent.Items.ItemInfo)

local RecipeModel = {}

RecipeModel.ALL = "All"

-- Codes the shared Reasons table does not word (forge refusals).
RecipeModel.REASONS = {
	MissingMaterials = "your vault doesn't hold enough materials for that",
	Locked = "you haven't unlocked that recipe yet",
	WrongSource = "that item can't be converted by this recipe",
	InTrade = "finish your trade first",
	InTransit = "your items are still on their way",
	UnknownRecipe = "that recipe no longer exists",
	BadRequest = "the request was not understood",
}

function RecipeModel.NameOf(catalogId: string?): string
	local def = ItemCatalog.Get(catalogId)
	return def and def.name or tostring(catalogId)
end

-- The kit icon that depicts an item while it has no art of its own
-- (Kit.ItemIcon's `icon`), or nil: ItemInfo.Icon, the one source.
function RecipeModel.Icon(catalogId: string?): string?
	return ItemInfo.Icon(catalogId)
end

-- The item's stat line from ItemInfo.StatRows, at most `max` rows
-- ("Harvest Power 5 per hit · Tool Tier 3").
function RecipeModel.StatLine(catalogId: string?, max: number?): string
	if catalogId == nil then
		return ""
	end
	local parts = {}
	for _, row in ItemInfo.StatRows({ catalogId = catalogId }) do
		if #parts < (max or 2) then
			table.insert(parts, row.label .. " " .. row.value)
		end
	end
	return table.concat(parts, " · ")
end

local function displayName(name: string, quantity: number?): string
	return if quantity and quantity > 1 then ("%s ×%d"):format(name, quantity) else name
end

-- The one-line row subtitle: what unlocks a locked recipe, else what it makes.
function RecipeModel.Subtitle(entry): string
	if entry.locked then
		return if entry.requirement ~= "" then entry.requirement else "Locked"
	end
	if entry.kind == "Permanent" then
		return "Permanent: kept when you die"
	end
	local line = RecipeModel.StatLine(entry.output, 1)
	if entry.kind == "Craft" then
		local where = if entry.station then entry.station else "By hand"
		if entry.timed then
			where ..= (" · %s s each"):format(tostring(entry.seconds))
		end
		return if line ~= "" and not entry.timed then where .. " · " .. line else where
	end
	return if line ~= "" then line else RecipeModel.NameOf(entry.output)
end

-- The centre column's description: authored text (ItemInfo, D10) or a line
-- derived from the item's stats and how it is made.
function RecipeModel.Description(entry): string
	if entry.kind == "Permanent" then
		return ("Makes one %s from your vault Permanent: it stays yours when you die."):format(
			RecipeModel.NameOf(entry.output)
		)
	end
	local text = ItemInfo.Description(entry.output)
	local line = RecipeModel.StatLine(entry.output)
	local tail
	if entry.kind == "Craft" then
		tail = if entry.timed
			then ("Smelts one every %s s at a %s."):format(tostring(entry.seconds), entry.station or "Furnace")
			elseif entry.station then ("Made at a %s."):format(entry.station)
			else "Made by hand, anywhere."
	else
		tail = if (entry.quantity or 1) > 1
			then ("Makes %d per forge, from your vault."):format(entry.quantity)
			else "Forged at default quality from your vault."
	end
	if text then
		return text
	end
	return if line ~= "" then line .. ". " .. tail else tail
end

-- Why the main button cannot act on `entry` × `count` right now, or nil.
function RecipeModel.Blocker(entry, count: number): string?
	if entry == nil then
		return "Choose a recipe."
	end
	if entry.locked then
		return if entry.requirement ~= "" then entry.requirement else "This recipe is locked."
	end
	if entry.here == false then
		return ("Stand next to a %s to make this."):format(entry.station or "station")
	end
	if entry.kind == "Permanent" and #(entry.sources or {}) == 0 then
		return ("You have no %s in your vault to convert."):format(RecipeModel.NameOf(entry.output))
	end
	for _, cost in RecipeModel.Cost(entry, count) do
		if cost.short then
			return ("You need %d %s (you have %d)."):format(cost.need, cost.name, cost.owned)
		end
	end
	if count > math.max(entry.maxCount or 0, 1) then
		return "That amount isn't allowed."
	end
	return nil
end

-- What `count` crafts of `entry` cost: {catalogId, name, owned, need, short}.
function RecipeModel.Cost(entry, count: number)
	local cost = {}
	for _, input in entry.inputs do
		local need = input.needed * math.max(count, 1)
		table.insert(cost, {
			catalogId = input.catalogId,
			name = input.name,
			owned = input.owned,
			need = need,
			short = input.owned < need,
		})
	end
	return cost
end

-- The stepper's bounds for `entry`: shown, and its max (at least 1).
function RecipeModel.Quantity(entry): (boolean, number)
	if entry == nil or not entry.batch or entry.locked then
		return false, 1
	end
	return true, math.max(1, entry.maxCount or 1)
end

function RecipeModel.Clamp(entry, count: number?): number
	local _, max = RecipeModel.Quantity(entry)
	return math.clamp(math.floor(count or 1), 1, max)
end

-- The catalog ids the selected recipe consumes (rows to highlight).
function RecipeModel.Needed(entry): { [string]: boolean }
	local set = {}
	for _, input in (entry and entry.inputs) or {} do
		set[input.catalogId] = true
	end
	return set
end

-- Recipes in `category` (RecipeModel.ALL for every one).
function RecipeModel.Filter(entries, category: string?)
	if category == nil or category == RecipeModel.ALL then
		return entries
	end
	local list = {}
	for _, entry in entries do
		if entry.category == category then
			table.insert(list, entry)
		end
	end
	return list
end

-- Forge -----------------------------------------------------------------------

local function rollText(roll: number?): string
	return if roll and roll ~= 0 then ("%+.1f%%"):format(roll * 100) else ""
end

-- Entries from a ForgeSnapshot view: special recipes first, then Permanent
-- conversions for gear the vault holds, then the other conversions (each group
-- in the server's order).
function RecipeModel.ForgeEntries(view)
	local entries, order = {}, {}
	local maxBatch = (view and view.maxBatch) or 1
	for index, recipe in (view and view.recipes) or {} do
		local permanent = recipe.kind == ForgeRecipes.Kinds.Permanent
		local inputs, can = {}, if permanent then 1 else maxBatch
		for _, input in recipe.inputs or {} do
			table.insert(inputs, {
				catalogId = input.catalogId,
				name = input.name,
				owned = input.owned or 0,
				needed = input.needed or 1,
			})
			if (input.needed or 0) > 0 then
				can = math.min(can, (input.owned or 0) // input.needed)
			end
		end
		local sources = nil
		if permanent then
			sources = {}
			for _, source in recipe.sources or {} do
				table.insert(sources, {
					id = source.instanceId,
					name = source.name,
					qualityRoll = source.qualityRoll,
					detail = rollText(source.qualityRoll),
				})
			end
		end
		local entry = {
			id = recipe.id,
			kind = recipe.kind,
			category = recipe.category,
			name = displayName(recipe.name, recipe.quantity),
			output = recipe.output,
			quantity = recipe.quantity or 1,
			inputs = inputs,
			locked = recipe.unlocked == false,
			requirement = recipe.requirement or "",
			maxCount = if type(recipe.maxCount) == "number" then recipe.maxCount else can,
			batch = not permanent and maxBatch > 1,
			verb = if permanent then "Convert" else "Forge",
			here = true,
			sources = sources,
		}
		entry.subtitle = RecipeModel.Subtitle(entry)
		table.insert(entries, entry)
		order[entry] = index
	end
	local function group(entry): number
		if entry.kind ~= ForgeRecipes.Kinds.Permanent then
			return 1
		end
		return if #entry.sources > 0 then 2 else 3
	end
	table.sort(entries, function(a, b)
		local ga, gb = group(a), group(b)
		if ga ~= gb then
			return ga < gb
		end
		return order[a] < order[b]
	end)
	return entries
end

-- YOUR MATERIALS in the forge: every distinct input the vault holds (> 0),
-- sorted by name.
function RecipeModel.Materials(entries)
	local seen, list = {}, {}
	for _, entry in entries do
		for _, input in entry.inputs do
			if not seen[input.catalogId] and input.owned > 0 then
				seen[input.catalogId] = true
				table.insert(list, { catalogId = input.catalogId, name = input.name, quantity = input.owned })
			end
		end
	end
	table.sort(list, function(a, b)
		return a.name < b.name
	end)
	return list
end

-- The status line after a forge: (title, text).
function RecipeModel.ForgeReceipt(entry, receipt, count: number): (string, string)
	local name = RecipeModel.NameOf(entry.output)
	if entry.kind == "Permanent" then
		return "Converted", ("Your %s is now Permanent. It is in your vault."):format(name)
	end
	local made = (entry.quantity or 1) * count
	local output = type(receipt) == "table" and receipt.output
	if type(output) == "table" and type(output.quantity) == "number" then
		made = output.quantity
	end
	return "Forged", ("%s ×%d is in your lobby backpack."):format(name, made)
end

-- The confirmation for a Permanent conversion of `source`, naming the exact item.
function RecipeModel.ConversionText(entry, source): string
	local spend = {}
	for _, input in entry.inputs do
		table.insert(spend, ("%s ×%d"):format(input.name, input.needed))
	end
	local roll = source and rollText(source.qualityRoll) or ""
	return (
		"Convert this %s%s into a Permanent item? Spends from your vault: %s. "
		.. "Permanent items stay with you when you die. Dropping one lets whoever picks it up own it, "
		.. "and trading transfers it. The ordinary version is consumed. This cannot be undone."
	):format(
		source and source.name or RecipeModel.NameOf(entry.output),
		if roll ~= "" then (" (quality %s, kept exactly)"):format(roll) else "",
		table.concat(spend, ", ")
	)
end

-- Field crafting ----------------------------------------------------------------

-- An entry for a field recipe. `count(catalogId)` is what the player carries;
-- `nearby` is the set of station kinds in reach.
function RecipeModel.CraftEntry(recipe, count: (string) -> number, nearby)
	local inputs = {}
	local can = CraftingRules.MAX_BATCH
	for catalogId, amount in recipe.inputs do
		local owned = count(catalogId)
		can = math.min(can, owned // amount)
		table.insert(
			inputs,
			{ catalogId = catalogId, name = RecipeModel.NameOf(catalogId), owned = owned, needed = amount }
		)
	end
	table.sort(inputs, function(a, b)
		return a.name < b.name
	end)
	local timed = CraftingRules.IsTimed(recipe)
	local station = CraftingRules.StationFor(recipe)
	local here = CraftingRules.AvailableHere(recipe, nearby)
	local entry = {
		id = recipe.id,
		kind = "Craft",
		category = CraftingRules.Category(recipe),
		name = displayName(RecipeModel.NameOf(recipe.output), recipe.quantity),
		output = recipe.output,
		quantity = recipe.quantity or 1,
		inputs = inputs,
		locked = false,
		requirement = "",
		-- Only timed recipes take a count (CraftingRules.BatchCount).
		maxCount = if timed then can else math.min(can, 1),
		batch = timed,
		timed = timed,
		seconds = recipe.seconds,
		station = station,
		here = here,
		verb = if not here and station then "Need " .. station elseif timed then "Smelt" else "Craft",
	}
	entry.subtitle = RecipeModel.Subtitle(entry)
	return entry
end

function RecipeModel.CraftEntries(list, count: (string) -> number, nearby)
	local entries = {}
	for _, recipe in list do
		table.insert(entries, RecipeModel.CraftEntry(recipe, count, nearby))
	end
	return entries
end

-- YOUR MATERIALS in a run: the carried materials (inventory snapshot slots),
-- summed per item and sorted by name.
function RecipeModel.Carried(slots)
	local totals, list = {}, {}
	for _, slot in slots or {} do
		local id = slot.catalogId
		if id and slot.quantity and ItemCatalog.IsMaterial(id) then
			if totals[id] == nil then
				totals[id] = { catalogId = id, name = RecipeModel.NameOf(id), quantity = 0 }
				table.insert(list, totals[id])
			end
			totals[id].quantity += slot.quantity
		end
	end
	table.sort(list, function(a, b)
		return a.name < b.name
	end)
	return list
end

-- "Workbench, Furnace" from the set of stations in reach, in menu order.
function RecipeModel.StationsText(nearby): string
	local names = {}
	for _, station in CraftingRules.STATIONS do
		if nearby and nearby[station] then
			table.insert(names, station)
		end
	end
	return if #names > 0 then table.concat(names, ", ") else "None in reach"
end

-- The smelting job line: "Iron Bar 2 / 5 · 7 s left".
function RecipeModel.JobText(name: string, done: number, count: number, left: number): string
	return ("%s %d / %d · %d s left"):format(name, done, count, math.ceil(math.max(left, 0)))
end

return RecipeModel
