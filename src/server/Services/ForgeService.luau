-- The Ancestral Forge (GDD §15–16, §25.3). Lobby only. Shows every recipe with
-- vault-only Owned/Needed counts and its unlock state (Permanent conversions sorted
-- and tagged with their source's tier and family for grouping), and commits special crafts
-- and Permanent conversions as exactly-once operations keyed by the client's nonce,
-- so a retried request returns the first result instead of charging again. A special
-- craft may ask for a batch (count 1..ForgeRules.MAX_BATCH): all of it is paid for
-- and granted in that one operation, or none of it. Crafts wait while the player is
-- in an open trade, or while a settled trade may still roll back ("TradeSettling",
-- ForgeRules).

local HttpService = game:GetService("HttpService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local ForgeRecipes = require(ReplicatedStorage.Shared.Crafting.ForgeRecipes)
local ForgeRules = require(ReplicatedStorage.Shared.Crafting.ForgeRules)
local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Validation = require(ReplicatedStorage.Shared.Data.Validation)
local ProfileService = require(script.Parent.ProfileService)
local ProgressionService = require(script.Parent.ProgressionService)
local TradeService = require(script.Parent.TradeService)

local ForgeService = {}

local function nameOf(catalogId: string): string
	local def = ItemCatalog.Get(catalogId)
	return def and def.name or catalogId
end

local function requirementText(recipe): string
	local parts = {}
	if (recipe.unlock.extractions or 0) > 0 then
		table.insert(parts, ("extract %d time(s)"):format(recipe.unlock.extractions))
	end
	for _, catalogId in recipe.unlock.discovered or {} do
		table.insert(parts, "extract " .. nameOf(catalogId))
	end
	if (recipe.unlock.level or 0) > 0 then
		table.insert(parts, ("reach level %d"):format(recipe.unlock.level))
	end
	if (recipe.unlock.crafting or 0) > 0 then
		table.insert(parts, ("Crafting mastery %d"):format(recipe.unlock.crafting))
	end
	return if #parts > 0 then "Unlock: " .. table.concat(parts, ", ") else ""
end

local function snapshot(player: Player)
	local profile = ProfileService.GetProfile(player)
	if profile == nil then
		return nil
	end
	if #ForgeRules.PendingUnlocks(profile) > 0 then
		ProfileService.RunOperation(
			player,
			"unlock:" .. HttpService:GenerateGUID(false),
			"RecipeUnlock",
			function(working)
				return ForgeRules.RefreshUnlocks(working, os.time())
			end
		)
		profile = ProfileService.GetProfile(player)
	end
	local recipes = {}
	for _, recipe in ForgeRules.Ordered() do
		local inputs = {}
		for catalogId, needed in recipe.inputs do
			table.insert(inputs, {
				catalogId = catalogId,
				name = nameOf(catalogId),
				owned = ForgeRules.Owned(profile, catalogId),
				needed = needed,
			})
		end
		table.sort(inputs, function(a, b)
			return a.name < b.name
		end)
		local view = {
			id = recipe.id,
			kind = recipe.kind,
			category = recipe.category,
			name = (recipe.kind == ForgeRecipes.Kinds.Permanent and "Permanent " or "") .. nameOf(recipe.output),
			output = recipe.output,
			quantity = recipe.quantity,
			unlocked = ForgeRules.IsUnlocked(profile, recipe.id),
			requirement = requirementText(recipe),
			inputs = inputs,
			-- The most one request may forge right now (materials and batch cap).
			maxCount = ForgeRules.MaxCount(profile, recipe),
		}
		if recipe.kind == ForgeRecipes.Kinds.Permanent then
			local def = ItemCatalog.Get(recipe.output)
			view.tier = ForgeRules.PermanentTier(recipe)
			view.family = def and def.family
			view.sources = {}
			for _, item in ForgeRules.Sources(profile, recipe, player.UserId) do
				table.insert(view.sources, {
					instanceId = item.instanceId,
					name = nameOf(item.catalogId),
					qualityRoll = item.qualityRoll,
				})
			end
		end
		table.insert(recipes, view)
	end
	return {
		recipes = recipes,
		categories = ForgeRecipes.Categories,
		tiers = ForgeRules.TIER_ORDER,
		maxBatch = ForgeRules.MAX_BATCH,
	}
end

local function craft(player: Player, recipeId: any, sourceId: any, nonce: any, count: any)
	if ForgeRecipes.Get(recipeId) == nil or not Validation.IsId(nonce) or #nonce > 50 then
		return false, "BadRequest"
	end
	if sourceId ~= nil and not Validation.IsId(sourceId) then
		return false, "BadRequest"
	end
	count = if count == nil then 1 else count
	if not Validation.IsQuantity(count, 1, ForgeRules.MAX_BATCH) then
		return false, "BadQuantity"
	end
	if TradeService.InSession(player) then
		return false, "InTrade"
	end
	local operationId = "forge:" .. nonce
	local ok, result, applied = ProfileService.RunOperation(player, operationId, "Forge", function(profile)
		local now = os.time()
		ForgeRules.RefreshUnlocks(profile, now)
		local receipt, reason = ForgeRules.Craft(profile, {
			recipeId = recipeId,
			sourceId = sourceId,
			count = count,
			ownerId = player.UserId,
			operationId = operationId,
			now = now,
			newId = function()
				return HttpService:GenerateGUID(false)
			end,
		})
		if receipt == nil then
			error(reason, 0)
		end
		return receipt
	end)
	if not ok then
		return false, tostring(result)
	end
	if applied then
		-- A retried nonce returns the same receipt without granting XP again. A batch
		-- earns what the same crafts made one at a time would.
		local crafted = result.count or 1
		ProgressionService.GrantXp(player, "Forge", "Forging", if crafted > 1 then crafted else nil)
		ProgressionService.GrantMastery(player, "Crafting", 2 * crafted)
	end
	return true, result
end

function ForgeService.Start()
	if not PlaceConfig.IsLobby() then
		return
	end
	Remotes.Handle("ForgeSnapshot", snapshot)
	Remotes.Handle("ForgeCraft", craft)
end

return ForgeService
