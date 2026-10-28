-- Planters and crops (GDD §6.1, Q41). Anyone can plant a crop in a planter by
-- paying its seed cost, and anyone can harvest it once ripe: farms are as public
-- as the rest of a base. Growth uses server timestamps, so crops keep growing while
-- their planter is unattended, for as long as the world exists. Harvest XP and
-- mastery are capped per player per minute (BuildRules.TakeCropCredit), so a field
-- of hundreds of planters is not a progression farm. Planting with carried-in
-- seed (GDD §53) makes that many of the harvest carried too, so a planter never
-- turns carried units into ones the Center bonus multiplies. World place only.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local BuildRules = require(ReplicatedStorage.Shared.Building.BuildRules)
local InventoryRules = require(ReplicatedStorage.Shared.Inventory.InventoryRules)
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

-- One plant prompt per crop in CROP_ORDER, each on its own key. Every other
-- gamepad button already has a job (hotbar step, placement, drop, panels), so the
-- crops after the last key share its prompt: a tap shows the next of them and a
-- full hold plants the one shown.
local KEYS = {
	{ Enum.KeyCode.E, Enum.KeyCode.ButtonX },
	{ Enum.KeyCode.R, Enum.KeyCode.ButtonY },
	{ Enum.KeyCode.F, Enum.KeyCode.ButtonB },
	{ Enum.KeyCode.G, Enum.KeyCode.ButtonL2 },
}
-- A release this far short of the hold is a tap (cycles a shared prompt).
local TAP_FRACTION = 0.8
-- Colour of each crop once ripe (green while growing).
local RIPE_COLORS = {
	Redberry = Color3.fromRGB(220, 60, 90),
	Sweetberry = Color3.fromRGB(240, 150, 60),
	Herbs = Color3.fromRGB(120, 200, 90),
	Fiber = Color3.fromRGB(180, 200, 110),
	Sapling = Color3.fromRGB(120, 86, 50),
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

-- What players read for a crop: the item it yields ("Redberry"), or the crop
-- itself when that is a generic material (a Sapling grows Wood).
local function cropName(cropId: string): string
	local crop = StructureCatalog.Crops[cropId]
	local def = crop.yield.catalogId == cropId and ItemCatalog.Get(cropId)
	return def and def.name or cropId
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
		then cropName(planter.cropId) .. " (ripe)"
		else ("%s — %d:%02d"):format(cropName(planter.cropId), remaining // 60, remaining % 60)
	if planter.plant then
		local height = 0.4 + 2.6 * progress
		planter.plant.Size = Vector3.new(1.5, height, 1.5)
		planter.plant.CFrame = planter.record.part.CFrame * CFrame.new(0, 0.75 + height / 2, 0)
		planter.plant.Color = if remaining <= 0
			then RIPE_COLORS[planter.cropId] or Color3.fromRGB(220, 60, 90)
			else Color3.fromRGB(80, 170, 70)
	end
end

local function plant(player: Player, planter, cropId: string)
	local crop = StructureCatalog.Crops[cropId]
	if crop == nil or planter.cropId or not canAct(player) then
		return
	end
	local paid, carried = InventoryService.RemoveAll(player, crop.seed)
	if not paid then
		InventoryService.Notify(player, "You need " .. seedText(crop.seed) .. " to plant that.")
		return
	end
	planter.cropId = cropId
	planter.plantedAt = now()
	planter.carried = carried
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
	local carried = planter.carried or 0
	planter.cropId = nil
	planter.plantedAt = nil
	planter.carried = nil
	local yield = table.clone(crop.yield)
	yield.quantity =
		ModifierRules.RollYield(yield.quantity, ModifierService.Get(player, "FarmingYield", "DropQuantity"), rng)
	if ItemCatalog.IsMaterial(yield.catalogId) then
		InventoryRules.SetCarried(yield, carried)
	end
	local remaining, remainingCarried = InventoryService.Add(player, yield)
	if remaining > 0 then
		local spill = { catalogId = yield.catalogId, quantity = remaining }
		InventoryRules.SetCarried(spill, remainingCarried)
		DropService.Spawn(spill, planter.record.position)
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
	local order = StructureCatalog.CROP_ORDER
	for index, keys in KEYS do
		-- The crops this prompt offers: its own, or every remaining one on the last key.
		local choices = if index < #KEYS then { order[index] } else table.move(order, index, #order, 1, {})
		if #choices == 0 then
			break
		end
		local shown = 1
		local prompt = Instance.new("ProximityPrompt")
		local function label()
			local cropId = choices[shown]
			prompt.ActionText = "Plant " .. cropName(cropId)
			prompt.ObjectText = "Costs " .. seedText(StructureCatalog.Crops[cropId].seed)
			if #choices > 1 then
				prompt.ObjectText ..= (" · tap for %s"):format(cropName(choices[shown % #choices + 1]))
			end
		end
		label()
		prompt.KeyboardKeyCode = keys[1]
		prompt.GamepadKeyCode = keys[2]
		prompt.HoldDuration = 0.5
		prompt.MaxActivationDistance = 8
		prompt.Parent = record.part
		-- The crop shown when each player started holding, so a cycle by someone
		-- else mid-hold never changes what they plant.
		local holding = setmetatable({}, { __mode = "k" })
		prompt.PromptButtonHoldBegan:Connect(function(player)
			holding[player] = { at = os.clock(), cropId = choices[shown] }
		end)
		prompt.PromptButtonHoldEnded:Connect(function(player)
			local hold = holding[player]
			-- Only a tap is forgotten here. A long hold keeps its record, because
			-- Roblox may report the hold ending before Triggered, and Triggered must
			-- still plant the crop this player saw (the next HoldBegan replaces it).
			if hold and os.clock() - hold.at < prompt.HoldDuration * TAP_FRACTION then
				holding[player] = nil
				if #choices > 1 then
					shown = shown % #choices + 1
					label()
				end
			end
		end)
		prompt.Triggered:Connect(function(player)
			local hold = holding[player]
			holding[player] = nil
			plant(player, planter, if hold then hold.cropId else choices[shown])
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
