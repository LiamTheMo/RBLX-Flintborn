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
local ProfileSchema = require(ReplicatedStorage.Shared.Data.ProfileSchema)
local QualityRoll = require(ReplicatedStorage.Shared.Crafting.QualityRoll)
local Recipes = require(ReplicatedStorage.Shared.Crafting.Recipes)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Validation = require(ReplicatedStorage.Shared.Data.Validation)
local InventoryService = require(script.Parent.InventoryService)
local ProfileService = require(script.Parent.ProfileService)
local WorldAdmissionService = require(script.Parent.WorldAdmissionService)

local CraftingService = {}

CraftingService.WORKBENCH_TAG = "Workbench"
CraftingService.WORKBENCH_RANGE = 12
CraftingService.REMEMBERED_REQUESTS = 32

local rng = Random.new()
local seenRequests = {}

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

	-- Build the output, then check everything on a copy before touching the real inventory.
	local output
	if ItemCatalog.IsStackable(recipe.output) then
		output = { catalogId = recipe.output, quantity = recipe.quantity }
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
	InventoryService.Publish(player)
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
	if not InventoryService.RemoveAll(player, { [entry.catalogId] = 1 }) then
		return false, "NotCarried"
	end
	local bench = Instance.new("Part")
	bench.Name = "Workbench"
	bench.Anchored = true
	bench.Size = Vector3.new(5, 3, 3)
	bench.Color = Color3.fromRGB(122, 86, 52)
	bench.Material = Enum.Material.Wood
	bench.CFrame = CFrame.new(hit.Position + Vector3.new(0, 1.5, 0)) * root.CFrame.Rotation
	bench:SetAttribute("OwnerUserId", player.UserId)
	CollectionService:AddTag(bench, CraftingService.WORKBENCH_TAG)
	bench.Parent = workspace
	return true, nil
end

function CraftingService.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	Remotes.Get("Craft").OnServerInvoke = craft
	Remotes.Get("PlaceItem").OnServerInvoke = place
	Players.PlayerRemoving:Connect(function(player)
		seenRequests[player] = nil
	end)
end

return CraftingService
