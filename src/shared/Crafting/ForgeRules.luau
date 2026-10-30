-- Pure Ancestral Forge rules (GDD §16.3–16.4, §15.3, §23.3). Counts come from the
-- vault only; a valid, fully funded request always succeeds (no random failure);
-- outputs have default quality. Every check runs before anything changes, and the
-- caller commits through the operation journal, so a retried nonce never
-- charges twice.

local ItemCatalog = require(script.Parent.Parent.Items.ItemCatalog)
local PermanentRules = require(script.Parent.Parent.Items.PermanentRules)
local Receipts = require(script.Parent.Parent.Data.Receipts)
local ExtractionRules = require(script.Parent.Parent.Extraction.ExtractionRules)
local ForgeRecipes = require(script.Parent.ForgeRecipes)
local TradeRules = require(script.Parent.Parent.Economy.TradeRules)
local Tiers = require(script.Parent.Parent.Items.Tiers)
local Validation = require(script.Parent.Parent.Data.Validation)

local ForgeRules = {}

-- Most crafts of one special recipe in a single request. A Permanent conversion
-- always takes exactly one source item, so its batch is 1.
ForgeRules.MAX_BATCH = 10

-- Permanent conversions are browsed by their source's tier, weakest first (power,
-- then ladder order); gear without a tier (the Guardian's Fang) comes last.
ForgeRules.LEGENDARY_TIER = "Legendary"
ForgeRules.TIER_ORDER = {}
do
	local ladder = table.clone(Tiers.Ladder)
	local position = {}
	for index, tier in ladder do
		position[tier] = index
	end
	table.sort(ladder, function(a, b)
		if a.power ~= b.power then
			return a.power < b.power
		end
		return position[a] < position[b]
	end)
	for _, tier in ladder do
		table.insert(ForgeRules.TIER_ORDER, tier.id)
	end
	table.insert(ForgeRules.TIER_ORDER, ForgeRules.LEGENDARY_TIER)
end
local tierRank = {}
for index, tierId in ForgeRules.TIER_ORDER do
	tierRank[tierId] = index
end

-- The browsing tier of a Permanent recipe's source, or nil for special recipes.
function ForgeRules.PermanentTier(recipe): string?
	if recipe.kind ~= ForgeRecipes.Kinds.Permanent then
		return nil
	end
	local def = ItemCatalog.Get(recipe.output)
	return def and def.tier or ForgeRules.LEGENDARY_TIER
end

-- Every Forge recipe, Permanent conversions sorted by tier and otherwise in
-- catalog order (weapons, tools, then armor within a tier).
local ordered = table.clone(ForgeRecipes.List)
do
	local listed = {}
	for index, recipe in ordered do
		listed[recipe] = index
	end
	table.sort(ordered, function(a, b)
		local ta, tb = ForgeRules.PermanentTier(a), ForgeRules.PermanentTier(b)
		local ra, rb = ta and tierRank[ta] or 0, tb and tierRank[tb] or 0
		if ra ~= rb then
			return ra < rb
		end
		return listed[a] < listed[b]
	end)
end
function ForgeRules.Ordered()
	return ordered
end

-- Vaulted quantity of a material. The lobby backpack never counts (§25.3).
function ForgeRules.Owned(profile, catalogId: string): number
	return profile.vault.materials[catalogId] or 0
end

-- How many crafts of `recipe` one request may ask for: up to MAX_BATCH (1 for a
-- Permanent conversion) and no more than the vault's materials pay for. 0 when
-- even one is short. Lobby backpack room is checked by Craft (BackpackFull).
function ForgeRules.MaxCount(profile, recipe): number
	local limit = if recipe.kind == ForgeRecipes.Kinds.Permanent then 1 else ForgeRules.MAX_BATCH
	for catalogId, quantity in recipe.inputs do
		limit = math.min(limit, math.floor(ForgeRules.Owned(profile, catalogId) / quantity))
	end
	return limit
end

function ForgeRules.RequirementsMet(profile, recipe): boolean
	local unlock = recipe.unlock
	if profile.metrics.extractions < (unlock.extractions or 0) then
		return false
	end
	-- Player level and Crafting mastery gates (Q15, Q77; v0.13).
	if profile.progression.level < (unlock.level or 0) then
		return false
	end
	local crafting = profile.progression.masteryTracks.Crafting
	if (crafting and crafting.level or 0) < (unlock.crafting or 0) then
		return false
	end
	for _, catalogId in unlock.discovered or {} do
		if not profile.recipes.discovered[catalogId] then
			return false
		end
	end
	return true
end

function ForgeRules.IsUnlocked(profile, recipeId: string): boolean
	return profile.recipes.unlocked[recipeId] ~= nil
end

-- Recipes whose requirements are now met but not yet recorded as unlocked.
function ForgeRules.PendingUnlocks(profile): { string }
	local pending = {}
	for _, recipe in ForgeRecipes.List do
		if not ForgeRules.IsUnlocked(profile, recipe.id) and ForgeRules.RequirementsMet(profile, recipe) then
			table.insert(pending, recipe.id)
		end
	end
	return pending
end

-- Records newly met unlocks once (§16.3: recipe knowledge is granted once).
function ForgeRules.RefreshUnlocks(profile, now: number): { string }
	local granted = ForgeRules.PendingUnlocks(profile)
	for _, recipeId in granted do
		profile.recipes.unlocked[recipeId] = { unlockSource = "Discovery", unlockedAt = now }
	end
	return granted
end

local function vaultIndexOf(profile, instanceId: any): number?
	for index, item in profile.vault.items do
		if item.instanceId == instanceId then
			return index
		end
	end
	return nil
end

-- Vaulted items a Permanent recipe could convert for this player.
function ForgeRules.Sources(profile, recipe, ownerId: number)
	local sources = {}
	for _, item in profile.vault.items do
		if item.catalogId == recipe.source and PermanentRules.CanConvert(item, ownerId) then
			table.insert(sources, item)
		end
	end
	return sources
end

local function backpackFits(profile, outputs): boolean
	local trial = table.clone(profile.lobbyBackpack.slots)
	for index, slot in trial do
		trial[index] = table.clone(slot)
	end
	for _, item in outputs do
		if ExtractionRules.AddToLobbyBackpack(trial, table.clone(item)) ~= 0 then
			return false
		end
	end
	return true
end

-- Applies one Forge request. `request` = {recipeId, sourceId?, count?, ownerId,
-- operationId, now, newId}. `count` (default 1) crafts are checked, charged and
-- granted together. Returns (receipt, nil) or (nil, reason) with the profile untouched.
function ForgeRules.Craft(profile, request)
	local recipe = ForgeRecipes.Get(request.recipeId)
	if recipe == nil then
		return nil, "UnknownRecipe"
	end
	local count = if request.count == nil then 1 else request.count
	if not Validation.IsQuantity(count, 1, ForgeRules.MAX_BATCH) then
		return nil, "BadQuantity"
	end
	if recipe.kind == ForgeRecipes.Kinds.Permanent and count ~= 1 then
		return nil, "BadQuantity"
	end
	if profile.transit ~= nil then
		return nil, "InTransit"
	end
	-- A trade that may still roll back could not reclaim consumed inputs.
	if TradeRules.IsSettling(profile) then
		return nil, TradeRules.SETTLING
	end
	if not ForgeRules.IsUnlocked(profile, recipe.id) then
		return nil, "Locked"
	end
	local spend = {}
	for catalogId, quantity in recipe.inputs do
		spend[catalogId] = quantity * count
		if ForgeRules.Owned(profile, catalogId) < spend[catalogId] then
			return nil, "MissingMaterials"
		end
	end

	local outputs, sourceIndex = {}, nil
	if recipe.kind == ForgeRecipes.Kinds.Permanent then
		sourceIndex = vaultIndexOf(profile, request.sourceId)
		local source = sourceIndex and profile.vault.items[sourceIndex]
		local ok, reason = PermanentRules.CanConvert(source, request.ownerId)
		if not ok then
			return nil, reason
		end
		if source.catalogId ~= recipe.source then
			return nil, "WrongSource"
		end
	elseif ItemCatalog.IsStackable(recipe.output) then
		outputs[1] = { catalogId = recipe.output, quantity = recipe.quantity * count }
	else
		for _ = 1, count do
			table.insert(outputs, {
				instanceId = request.newId(),
				catalogId = recipe.output,
				ownerId = request.ownerId,
				location = "LobbyBackpack",
				qualityRoll = 0,
			})
		end
	end
	if not backpackFits(profile, outputs) then
		return nil, "BackpackFull"
	end

	-- Everything checked: charge the inputs for all `count` crafts and create
	-- exactly their results.
	for catalogId, quantity in spend do
		local remaining = ForgeRules.Owned(profile, catalogId) - quantity
		profile.vault.materials[catalogId] = if remaining > 0 then remaining else nil
	end
	local receipt = {
		at = request.now,
		recipeId = recipe.id,
		recipeVersion = recipe.version,
		count = count,
		inputs = spend,
		status = "Committed",
	}
	if sourceIndex then
		local item = PermanentRules.Convert(profile.vault.items[sourceIndex], request.operationId, request.now)
		profile.permanentItems[item.instanceId] = PermanentRules.LedgerEntry(item, request.now)
		receipt.sourceId = item.instanceId
		receipt.output = { catalogId = item.catalogId, instanceId = item.instanceId, permanent = true }
	else
		local instanceIds = {}
		for _, output in outputs do
			ExtractionRules.AddToLobbyBackpack(profile.lobbyBackpack.slots, output)
			table.insert(instanceIds, output.instanceId)
		end
		local first = outputs[1]
		receipt.output = {
			catalogId = first.catalogId,
			quantity = first.quantity,
			instanceId = first.instanceId,
			instanceIds = if #instanceIds > 0 then instanceIds else nil,
		}
	end
	Receipts.Store(profile.receipts.forge, request.operationId, receipt)
	return receipt, nil
end

return ForgeRules
