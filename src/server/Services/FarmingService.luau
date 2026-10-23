-- Planters and crops (GDD §6.1, Q41). Anyone can plant a crop in a planter by
-- paying its seed cost, and anyone can harvest it once ripe: farms are as public
-- as the rest of a base. Growth uses server timestamps, so crops keep growing while
-- their planter is unattended, for as long as the world exists. Harvest XP and
-- mastery are capped per player per minute (BuildRules.TakeCropCredit), so a field
-- of hundreds of planters is not a progression farm. World place only.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local BuildRules = require(ReplicatedStorage.Shared.Building.BuildRules)
local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local ModifierRules = require(ReplicatedStorage.Shared.Progression.ModifierRules)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local StructureCatalog = require(ReplicatedStorage.Shared.Building.StructureCatalog)
local BuildingService = require(script.Parent.BuildingService)
local DownedService = require(script.Parent.DownedService)
local DropService = require(script.Parent.DropService)
local InventoryService = require(script.Parent.InventoryService)
local ModifierService = require(script.Parent.ModifierService)
local ProgressionService = require(script.Parent.ProgressionService)
local WorldAdmissionService = require(script.Parent.WorldAdmissionService)

local FarmingService = {}

local KEYS = {
	{ Enum.KeyCode.E, Enum.KeyCode.ButtonX },
	{ Enum.KeyCode.R, Enum.KeyCode.ButtonY },
	{ Enum.KeyCode.F, Enum.KeyCode.ButtonB },
}

local planters = {}
local credits = {}
local rng = Random.new()

local function now(): number
	return workspace:GetServerTimeNow()
end

local function canAct(player: Player): boolean
	local humanoid = player.Character and player.Character:FindFirstChildOfClass("Humanoid")
	return WorldAdmissionService.IsAtRisk(player)
		and humanoid ~= nil
		and humanoid.Health > 0
		and not DownedService.IsDowned(player)
end

local function seedText(seed): string
	local parts = {}
	for catalogId, quantity in seed do
		local def = ItemCatalog.Get(catalogId)
		table.insert(parts, ("%d %s"):format(quantity, def and def.name or catalogId))
	end
	return table.concat(parts, ", ")
end

local function refresh(planter)
	local crop = planter.cropId and StructureCatalog.Crops[planter.cropId]
	for _, prompt in planter.plantPrompts do
		prompt.Enabled = crop == nil
	end
	if crop == nil then
		planter.harvest.Enabled = false
		if planter.plant then
			planter.plant:Destroy()
			planter.plant = nil
		end
		return
	end
	local remaining = BuildRules.CropRemaining(crop, planter.plantedAt, now())
	local progress = 1 - remaining / crop.seconds
	planter.harvest.Enabled = remaining <= 0
	planter.harvest.ObjectText = if remaining <= 0
		then planter.cropId .. " (ripe)"
		else ("%s — %d:%02d"):format(planter.cropId, remaining // 60, remaining % 60)
	if planter.plant then
		local height = 0.4 + 2.6 * progress
		planter.plant.Size = Vector3.new(1.5, height, 1.5)
		planter.plant.CFrame = planter.record.part.CFrame * CFrame.new(0, 0.75 + height / 2, 0)
		planter.plant.Color = if remaining <= 0 then Color3.fromRGB(220, 60, 90) else Color3.fromRGB(80, 170, 70)
	end
end

local function plant(player: Player, planter, cropId: string)
	local crop = StructureCatalog.Crops[cropId]
	if planter.cropId or not canAct(player) then
		return
	end
	if not InventoryService.RemoveAll(player, crop.seed) then
		InventoryService.Notify(player, "You need " .. seedText(crop.seed) .. " to plant that.")
		return
	end
	planter.cropId = cropId
	planter.plantedAt = now()
	local sprout = Instance.new("Part")
	sprout.Name = "Crop"
	sprout.Anchored = true
	sprout.CanCollide = false
	sprout.CanQuery = false
	sprout.Material = Enum.Material.Grass
	sprout.Parent = planter.record.part
	planter.plant = sprout
	refresh(planter)
end

local function harvest(player: Player, planter)
	local crop = planter.cropId and StructureCatalog.Crops[planter.cropId]
	if crop == nil or not canAct(player) or BuildRules.CropRemaining(crop, planter.plantedAt, now()) > 0 then
		return
	end
	planter.cropId = nil
	planter.plantedAt = nil
	local yield = table.clone(crop.yield)
	yield.quantity =
		ModifierRules.RollYield(yield.quantity, ModifierService.Get(player, "FarmingYield", "DropQuantity"), rng)
	local remaining = InventoryService.Add(player, yield)
	if remaining > 0 then
		DropService.Spawn({ catalogId = yield.catalogId, quantity = remaining }, planter.record.position)
	end
	local ledger = credits[player] or {}
	credits[player] = ledger
	if BuildRules.TakeCropCredit(ledger, now()) then
		ProgressionService.GrantXp(player, "CropHarvest", "Harvest")
		ProgressionService.GrantMastery(player, "Farming", 3)
	end
	refresh(planter)
end

local function register(record)
	local planter = { record = record, plantPrompts = {} }
	for index, cropId in StructureCatalog.CROP_ORDER do
		local crop = StructureCatalog.Crops[cropId]
		local prompt = Instance.new("ProximityPrompt")
		prompt.ActionText = "Plant " .. cropId
		prompt.ObjectText = "Costs " .. seedText(crop.seed)
		prompt.KeyboardKeyCode = KEYS[index][1]
		prompt.GamepadKeyCode = KEYS[index][2]
		prompt.HoldDuration = 0.5
		prompt.MaxActivationDistance = 8
		prompt.Parent = record.part
		prompt.Triggered:Connect(function(player)
			plant(player, planter, cropId)
		end)
		table.insert(planter.plantPrompts, prompt)
	end
	planter.harvest = Instance.new("ProximityPrompt")
	planter.harvest.ActionText = "Harvest"
	planter.harvest.HoldDuration = 0.5
	planter.harvest.MaxActivationDistance = 8
	planter.harvest.Parent = record.part
	planter.harvest.Triggered:Connect(function(player)
		harvest(player, planter)
	end)
	planters[record.id] = planter
	refresh(planter)
end

function FarmingService.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	BuildingService.Placed:Connect(function(record)
		if record.pieceId == "Planter" then
			register(record)
		end
	end)
	BuildingService.Removing:Connect(function(record)
		planters[record.id] = nil
	end)
	Players.PlayerRemoving:Connect(function(player)
		credits[player] = nil
	end)
	task.spawn(function()
		while true do
			task.wait(1)
			for _, planter in planters do
				if planter.cropId then
					refresh(planter)
				end
			end
		end
	end)
end

return FarmingService
