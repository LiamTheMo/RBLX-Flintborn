-- Field crafting (GDD §16.8, §19.1, Q103–107). Basic recipes craft anywhere;
-- advanced recipes need a nearby placed workbench, where gear rolls a small ±5%
-- quality. Inputs are removed and the output created in one server step; a
-- repeated request ID is applied once, and nothing is charged if the output does
-- not fit. World place only.

local CollectionService = game:GetService("CollectionService")
local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local InventoryRules = require(ReplicatedStorage.Shared.Inventory.InventoryRules)
local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local ItemInstance = require(ReplicatedStorage.Shared.Data.ItemInstance)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local ModifierRules = require(ReplicatedStorage.Shared.Progression.ModifierRules)
local ProfileSchema = require(ReplicatedStorage.Shared.Data.ProfileSchema)
local QualityRoll = require(ReplicatedStorage.Shared.Crafting.QualityRoll)
local Recipes = require(ReplicatedStorage.Shared.Crafting.Recipes)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Validation = require(ReplicatedStorage.Shared.Data.Validation)
local BuildingService = require(script.Parent.BuildingService)
local InventoryService = require(script.Parent.InventoryService)
local ModifierService = require(script.Parent.ModifierService)
local ProfileService = require(script.Parent.ProfileService)
local ProgressionService = require(script.Parent.ProgressionService)
local WorldAdmissionService = require(script.Parent.WorldAdmissionService)

local CraftingService = {}

CraftingService.WORKBENCH_TAG = "Workbench"
CraftingService.WORKBENCH_RANGE = 12
CraftingService.REMEMBERED_REQUESTS = 32
CraftingService.CRAFT_SECONDS = 1

local rng = Random.new()
local seenRequests = {}
local lastCraft = {}

local function rootOf(player: Player)
	local character = player.Character
	return character and character:FindFirstChild("HumanoidRootPart")
end

local function nearWorkbench(player: Player): boolean
	local root = rootOf(player)
	if root == nil then
		return false
	end
	for _, bench in CollectionService:GetTagged(CraftingService.WORKBENCH_TAG) do
		if bench:IsA("BasePart") and (bench.Position - root.Position).Magnitude <= CraftingService.WORKBENCH_RANGE then
			return true
		end
	end
	return false
end

local function firstTime(player: Player, requestId: string): boolean
	local seen = seenRequests[player]
	if seen == nil then
		seen = { set = {}, order = {} }
		seenRequests[player] = seen
	end
	if seen.set[requestId] then
		return false
	end
	seen.set[requestId] = true
	table.insert(seen.order, requestId)
	if #seen.order > CraftingService.REMEMBERED_REQUESTS then
		seen.set[table.remove(seen.order, 1)] = nil
	end
	return true
end

local function craftingMastery(player: Player): number
	local profile = ProfileService.GetProfile(player)
	local track = profile and profile.progression.masteryTracks.Crafting
	return track and track.level or 0
end

local function craft(player: Player, requestId: any, recipeId: any)
	if not Validation.IsId(requestId) then
		return false, "BadRequest"
	end
	local recipe = Recipes.Get(recipeId)
	if recipe == nil then
		return false, "UnknownRecipe"
	end
	if not WorldAdmissionService.IsAtRisk(player) then
		return false, "NotInRun"
	end
	local inventory = InventoryService.Get(player)
	if inventory == nil then
		return false, "NotInRun"
	end
	local station = QualityRoll.Stations.Anywhere
	if recipe.station == Recipes.Workbench then
		if not nearWorkbench(player) then
			return false, "NeedsWorkbench"
		end
		station = QualityRoll.Stations.WorldWorkbench
	end
	if not firstTime(player, requestId) then
		return false, "Duplicate"
	end
	-- One craft per second, faster with Crafting mastery (Q77); also stops spam.
	local cooldown = CraftingService.CRAFT_SECONDS / (1 + ModifierService.Sum(player, "CraftSpeed"))
	local now = os.clock()
	if lastCraft[player] and now - lastCraft[player] < cooldown then
		return false, "TooFast"
	end

	-- Build the output, then check everything on a copy before touching the real inventory.
	local output
	if ItemCatalog.IsStackable(recipe.output) then
		-- Larger outputs from Crafting mastery (every third level).
		local quantity = ModifierRules.Final(recipe.quantity, ModifierService.Get(player, "CraftOutput"))
		output = { catalogId = recipe.output, quantity = quantity }
	else
		output = ItemInstance.New(
			function()
				return HttpService:GenerateGUID(false)
			end,
			recipe.output,
			player.UserId,
			ItemInstance.Locations.Carried,
			QualityRoll.Roll(rng, station, craftingMastery(player)),
			"craft:" .. requestId
		)
		output.recipeVersion = recipe.version
	end
	local trial = ProfileSchema.DeepCopy(inventory)
	if not InventoryRules.RemoveAll(trial, recipe.inputs) then
		return false, "MissingIngredients"
	end
	if InventoryRules.Add(trial, ProfileSchema.DeepCopy(output)) > 0 then
		return false, "InventoryFull"
	end

	InventoryRules.RemoveAll(inventory, recipe.inputs)
	InventoryRules.Add(inventory, output)
	-- Ingredient savings: a chance to get one unit of one input back.
	if rng:NextNumber() < ModifierService.Sum(player, "IngredientSave") then
		local inputs = {}
		for catalogId in recipe.inputs do
			table.insert(inputs, catalogId)
		end
		table.sort(inputs)
		InventoryRules.Add(inventory, { catalogId = inputs[rng:NextInteger(1, #inputs)], quantity = 1 })
	end
	lastCraft[player] = now
	InventoryService.Publish(player)
	ProgressionService.GrantXp(player, ProgressionService.XP.Craft, "Crafting")
	ProgressionService.GrantMastery(player, "Crafting", 1)
	return true, nil
end

-- Places a carried workbench a few studs in front of the player.
local function place(player: Player, hotbarIndex: any)
	if not WorldAdmissionService.IsAtRisk(player) or type(hotbarIndex) ~= "number" then
		return false, "BadRequest"
	end
	local inventory = InventoryService.Get(player)
	local entry = inventory and InventoryRules.At(inventory, "hotbar", hotbarIndex)
	local def = entry and ItemCatalog.Get(entry.catalogId)
	if def == nil or def.placeable ~= "Workbench" then
		return false, "NotPlaceable"
	end
	local root = rootOf(player)
	if root == nil then
		return false, "NoCharacter"
	end
	local origin = root.Position + root.CFrame.LookVector * 6 + Vector3.new(0, 10, 0)
	local hit = workspace:Raycast(origin, Vector3.new(0, -40, 0))
	if hit == nil then
		return false, "NoGround"
	end
	-- A placed workbench is an ordinary structure: raidable, and it decays without
	-- totem cover like everything else built in the world.
	return BuildingService.PlaceFromItem(player, "Workbench", hit.Position, entry.catalogId)
end

function CraftingService.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	Remotes.Get("Craft").OnServerInvoke = craft
	Remotes.Get("PlaceItem").OnServerInvoke = place
	Players.PlayerRemoving:Connect(function(player)
		seenRequests[player] = nil
		lastCraft[player] = nil
	end)
end

return CraftingService
