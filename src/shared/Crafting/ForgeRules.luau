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

local ForgeRules = {}

-- Vaulted quantity of a material. The lobby backpack never counts (§25.3).
function ForgeRules.Owned(profile, catalogId: string): number
	return profile.vault.materials[catalogId] or 0
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

local function backpackFits(profile, item): boolean
	local trial = table.clone(profile.lobbyBackpack.slots)
	for index, slot in trial do
		trial[index] = table.clone(slot)
	end
	return ExtractionRules.AddToLobbyBackpack(trial, table.clone(item)) == 0
end

-- Applies one Forge request. `request` = {recipeId, sourceId?, ownerId, operationId,
-- now, newId}. Returns (receipt, nil) or (nil, reason) with the profile untouched.
function ForgeRules.Craft(profile, request)
	local recipe = ForgeRecipes.Get(request.recipeId)
	if recipe == nil then
		return nil, "UnknownRecipe"
	end
	if profile.transit ~= nil then
		return nil, "InTransit"
	end
	if not ForgeRules.IsUnlocked(profile, recipe.id) then
		return nil, "Locked"
	end
	for catalogId, quantity in recipe.inputs do
		if ForgeRules.Owned(profile, catalogId) < quantity then
			return nil, "MissingMaterials"
		end
	end

	local output, sourceIndex
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
		output = { catalogId = recipe.output, quantity = recipe.quantity }
	else
		output = {
			instanceId = request.newId(),
			catalogId = recipe.output,
			ownerId = request.ownerId,
			location = "LobbyBackpack",
			qualityRoll = 0,
		}
	end
	if output and not backpackFits(profile, output) then
		return nil, "BackpackFull"
	end

	-- Everything checked: charge the inputs and create exactly one result.
	for catalogId, quantity in recipe.inputs do
		local remaining = ForgeRules.Owned(profile, catalogId) - quantity
		profile.vault.materials[catalogId] = if remaining > 0 then remaining else nil
	end
	local receipt = {
		at = request.now,
		recipeId = recipe.id,
		recipeVersion = recipe.version,
		inputs = table.clone(recipe.inputs),
		status = "Committed",
	}
	if sourceIndex then
		local item = PermanentRules.Convert(profile.vault.items[sourceIndex], request.operationId, request.now)
		profile.permanentItems[item.instanceId] = PermanentRules.LedgerEntry(item, request.now)
		receipt.sourceId = item.instanceId
		receipt.output = { catalogId = item.catalogId, instanceId = item.instanceId, permanent = true }
	else
		ExtractionRules.AddToLobbyBackpack(profile.lobbyBackpack.slots, output)
		receipt.output = { catalogId = output.catalogId, quantity = output.quantity, instanceId = output.instanceId }
	end
	Receipts.Store(profile.receipts.forge, request.operationId, receipt)
	return receipt, nil
end

return ForgeRules
