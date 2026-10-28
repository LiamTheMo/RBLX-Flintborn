-- Field crafting (GDD §16.8, §19.1, §51, Q103–107). Basic recipes craft anywhere;
-- the rest need a nearby built station (Workbench, Furnace, Anvil or Cauldron).
-- Gear made at a Workbench or Anvil rolls a small ±5% quality. Inputs are removed
-- and the output created in one server step; a repeated request ID is applied once
-- (a request refused as TooFast or Busy can be retried with the same ID), nothing
-- is charged if the output does not fit, and downed players cannot craft.
-- Crafting mastery gives only better quality rolls and, when smelting, a chance
-- of a bonus bar (owner decision 2026-10-28); it never speeds crafting up.
--
-- Smelting costs only time (no fuel): a request for N bars starts one job bound to
-- the furnace the player stands at, and each bar takes its ore in the same step
-- that grants it, every `seconds`. Each bar may bring one bonus bar (Crafting
-- mastery's SmeltBonus chance); a bonus bar with no room drops at the smelter's
-- feet, so it never stops the job. The job stops, keeping
-- the bars already made and taking nothing more, when the player moves away,
-- dies, is downed, leaves the run or the server, or the furnace is destroyed. One
-- job per player; its progress replicates as Smelt* player attributes. World
-- place only.

local CollectionService = game:GetService("CollectionService")
local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local CraftingRules = require(ReplicatedStorage.Shared.Crafting.CraftingRules)
local InventoryRules = require(ReplicatedStorage.Shared.Inventory.InventoryRules)
local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local ItemInstance = require(ReplicatedStorage.Shared.Data.ItemInstance)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local ProfileSchema = require(ReplicatedStorage.Shared.Data.ProfileSchema)
local QualityRoll = require(ReplicatedStorage.Shared.Crafting.QualityRoll)
local Recipes = require(ReplicatedStorage.Shared.Crafting.Recipes)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Validation = require(ReplicatedStorage.Shared.Data.Validation)
local BuildingService = require(script.Parent.BuildingService)
local DownedService = require(script.Parent.DownedService)
local DropService = require(script.Parent.DropService)
local InventoryService = require(script.Parent.InventoryService)
local ModifierService = require(script.Parent.ModifierService)
local ProfileService = require(script.Parent.ProfileService)
local ProgressionService = require(script.Parent.ProgressionService)
local WorldAdmissionService = require(script.Parent.WorldAdmissionService)

local CraftingService = {}

CraftingService.REMEMBERED_REQUESTS = 32
CraftingService.CRAFT_SECONDS = 1
-- How often running smelting jobs are checked and advanced.
CraftingService.SMELT_TICK = 0.2

-- Stations whose gear rolls quality (QualityRoll's world workbench roll).
local ROLLING_STATIONS = { [Recipes.Workbench] = true, [Recipes.Anvil] = true }

-- What a stopped job tells its smelter.
local STOP_TEXT = {
	MovedAway = "you moved away from the furnace",
	StationGone = "the furnace was destroyed",
	Died = "you died",
	Downed = "you were downed",
	NotInRun = "you left the run",
	MissingIngredients = "you ran out of ore",
	InventoryFull = "your inventory is full",
}

local rng = Random.new()
local seenRequests = {}
local lastCraft = {}
local jobs = {}

local function now(): number
	return workspace:GetServerTimeNow()
end

local function rootOf(player: Player)
	local character = player.Character
	return character and character:FindFirstChild("HumanoidRootPart")
end

-- The closest standing tagged station part in range, or nil.
local function nearestStation(player: Player, tag: string)
	local root = rootOf(player)
	if root == nil then
		return nil
	end
	local best, bestDistance = nil, CraftingRules.STATION_RANGE
	for _, part in CollectionService:GetTagged(tag) do
		if part:IsA("BasePart") and part.Parent ~= nil then
			local distance = (part.Position - root.Position).Magnitude
			if distance <= bestDistance then
				best, bestDistance = part, distance
			end
		end
	end
	return best
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

local function makeOutput(player: Player, recipe, station: string, source: string)
	if ItemCatalog.IsStackable(recipe.output) then
		return { catalogId = recipe.output, quantity = recipe.quantity }
	end
	local output = ItemInstance.New(
		function()
			return HttpService:GenerateGUID(false)
		end,
		recipe.output,
		player.UserId,
		ItemInstance.Locations.Carried,
		QualityRoll.Roll(rng, station, craftingMastery(player)),
		source
	)
	output.recipeVersion = recipe.version
	return output
end

-- True when `inputs` could be paid and `output` would fit, checked on a copy.
local function fits(inventory, inputs, output): (boolean, string?)
	local trial = ProfileSchema.DeepCopy(inventory)
	if not InventoryRules.RemoveAll(trial, inputs) then
		return false, "MissingIngredients"
	end
	if output and InventoryRules.Add(trial, ProfileSchema.DeepCopy(output)) > 0 then
		return false, "InventoryFull"
	end
	return true, nil
end

-- Takes one unit's inputs and grants `output` in one step, after checking both on
-- a copy. Nothing changes when it fails.
local function commit(player: Player, inventory, recipe, output): (boolean, string?)
	local ok, reason = fits(inventory, recipe.inputs, output)
	if not ok then
		return false, reason
	end
	InventoryRules.RemoveAll(inventory, recipe.inputs)
	InventoryRules.Add(inventory, output)
	-- Crafting mastery's bonus bar when smelting (never on instant crafts).
	if CraftingRules.IsTimed(recipe) and rng:NextNumber() < ModifierService.Sum(player, "SmeltBonus") then
		local bonus = { catalogId = recipe.output, quantity = 1 }
		if InventoryRules.Add(inventory, table.clone(bonus)) > 0 then
			-- No room: the bonus bar lands at the smelter's feet, not nowhere.
			local root = rootOf(player)
			if root then
				DropService.Spawn(bonus, root.Position - Vector3.new(0, 2.5, 0))
			end
		end
	end
	InventoryService.Publish(player)
	ProgressionService.GrantXp(player, "Craft", "Crafting")
	ProgressionService.GrantMastery(player, "Crafting", 1)
	return true, nil
end

-- Smelting jobs -------------------------------------------------------------------

local function publishJob(player: Player, job)
	player:SetAttribute("SmeltRecipe", job and job.recipe.id or nil)
	player:SetAttribute("SmeltCount", job and job.count or nil)
	player:SetAttribute("SmeltDone", job and job.done or nil)
	player:SetAttribute("SmeltEndsAt", job and job.unitEndsAt or nil)
	player:SetAttribute("SmeltSeconds", job and job.recipe.seconds or nil)
end

local function stopJob(player: Player, reason: string)
	local job = jobs[player]
	if job == nil then
		return
	end
	jobs[player] = nil
	if player.Parent == nil then
		return
	end
	publishJob(player, nil)
	local name = ItemCatalog.Get(job.recipe.output).name
	if reason == "Done" then
		InventoryService.Notify(player, ("Smelted %d %s."):format(job.done, name))
	elseif reason ~= "Stopped" then
		InventoryService.Notify(
			player,
			("Smelting stopped (%d/%d %s): %s."):format(job.done, job.count, name, STOP_TEXT[reason] or reason)
		)
	end
end

local function interruption(player: Player, job): string?
	local character = player.Character
	local humanoid = character and character:FindFirstChildOfClass("Humanoid")
	local root = rootOf(player)
	local station = job.station
	return CraftingRules.Interruption({
		atRisk = player.Parent ~= nil and WorldAdmissionService.IsAtRisk(player),
		sameCharacter = character ~= nil and character == job.character,
		alive = humanoid ~= nil and humanoid.Health > 0,
		downed = DownedService.IsDowned(player),
		stationStanding = station.Parent ~= nil,
		distance = root and (station.Position - root.Position).Magnitude,
	})
end

-- Checks one job and finishes its current unit when due.
local function stepJob(player: Player, job, at: number)
	local reason = interruption(player, job)
	if reason then
		stopJob(player, reason)
		return
	end
	if not CraftingRules.UnitDue(job, at) then
		return
	end
	local inventory = InventoryService.Get(player)
	if inventory == nil then
		stopJob(player, "NotInRun")
		return
	end
	local output = makeOutput(player, job.recipe, QualityRoll.Stations.Anywhere, "smelt")
	local ok, failure = commit(player, inventory, job.recipe, output)
	if not ok then
		stopJob(player, failure or "MissingIngredients")
		return
	end
	if CraftingRules.Advance(job) then
		stopJob(player, "Done")
	else
		publishJob(player, job)
	end
end

local function step()
	local at = now()
	for player, job in table.clone(jobs) do
		-- A job stopped earlier in this pass is not stepped again.
		if jobs[player] == job then
			stepJob(player, job, at)
		end
	end
end

-- Crafting --------------------------------------------------------------------

local function craft(player: Player, requestId: any, recipeId: any, count: any)
	if not Validation.IsId(requestId) then
		return false, "BadRequest"
	end
	local recipe = Recipes.Get(recipeId)
	if recipe == nil then
		return false, "UnknownRecipe"
	end
	count = CraftingRules.BatchCount(recipe, count)
	if count == nil then
		return false, "BadQuantity"
	end
	if count == 0 then
		-- Stopping keeps the bars already made; the unit in progress takes nothing.
		stopJob(player, "Stopped")
		return true, nil
	end
	if not WorldAdmissionService.IsAtRisk(player) then
		return false, "NotInRun"
	end
	if DownedService.IsDowned(player) then
		return false, "Downed"
	end
	local inventory = InventoryService.Get(player)
	if inventory == nil then
		return false, "NotInRun"
	end
	local stationTag = CraftingRules.StationFor(recipe)
	local stationPart = stationTag and nearestStation(player, stationTag)
	if stationTag and stationPart == nil then
		return false, CraftingRules.Refusal(stationTag)
	end
	local timed = CraftingRules.IsTimed(recipe)
	if timed and jobs[player] then
		return false, "Busy"
	end
	-- One craft per second for everyone; also stops spam. Checked before the
	-- request ID is recorded, so a retry is not a "Duplicate".
	local at = os.clock()
	if lastCraft[player] and at - lastCraft[player] < CraftingService.CRAFT_SECONDS then
		return false, "TooFast"
	end
	if not firstTime(player, requestId) then
		return false, "Duplicate"
	end

	if timed then
		-- Nothing is taken now: every unit pays for itself when it finishes.
		local ok, reason = fits(inventory, CraftingRules.BatchInputs(recipe, count), {
			catalogId = recipe.output,
			quantity = recipe.quantity,
		})
		if not ok then
			return false, reason
		end
		local job = CraftingRules.NewJob(recipe, count, now(), stationPart, player.Character)
		jobs[player] = job
		lastCraft[player] = at
		publishJob(player, job)
		return true, nil
	end

	local station = if ROLLING_STATIONS[recipe.station]
		then QualityRoll.Stations.WorldWorkbench
		else QualityRoll.Stations.Anywhere
	local ok, reason = commit(player, inventory, recipe, makeOutput(player, recipe, station, "craft:" .. requestId))
	if not ok then
		return false, reason
	end
	lastCraft[player] = at
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
	Remotes.Handle("Craft", craft)
	Remotes.Handle("PlaceItem", place)
	-- A destroyed or decayed furnace stops the jobs bound to it at once.
	BuildingService.Removing:Connect(function(record)
		for player, job in table.clone(jobs) do
			if job.station == record.part then
				stopJob(player, "StationGone")
			end
		end
	end)
	Players.PlayerRemoving:Connect(function(player)
		jobs[player] = nil
		seenRequests[player] = nil
		lastCraft[player] = nil
	end)
	task.spawn(function()
		while true do
			task.wait(CraftingService.SMELT_TICK)
			step()
		end
	end)
end

return CraftingService
