-- Medicine and food use (GDD §4.5, Q64–65, Q135, Q137). The server checks the item
-- is carried, applies medicine instantly with its animation as the only cooldown,
-- starts food heals, and consumes exactly one item per accepted request. A request
-- refused during the medicine animation consumes nothing. World place only.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Consumables = require(ReplicatedStorage.Shared.Items.Consumables)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Signal = require(ReplicatedStorage.Shared.Core.Signal)
local SurvivalRules = require(ReplicatedStorage.Shared.Survival.SurvivalRules)
local Validation = require(ReplicatedStorage.Shared.Data.Validation)
local InventoryService = require(script.Parent.InventoryService)
local SurvivalService = require(script.Parent.SurvivalService)

local HealingService = {}

-- Fires (player, catalogId) after a medicine or food is used.
HealingService.Used = Signal.new()

HealingService.REMEMBERED_REQUESTS = 32

local seenRequests = {}

-- Remembers request IDs so a replayed or duplicated request is applied once.
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
	if #seen.order > HealingService.REMEMBERED_REQUESTS then
		seen.set[table.remove(seen.order, 1)] = nil
	end
	return true
end

function HealingService.Use(player: Player, requestId: any, catalogId: any)
	if not Validation.IsId(requestId) then
		return false, "BadRequest"
	end
	local item = Consumables.Get(catalogId)
	if item == nil then
		return false, "NotConsumable"
	end
	local rules = SurvivalService.Get(player)
	local humanoid = SurvivalService.Humanoid(player)
	if rules == nil or humanoid == nil or humanoid.Health <= 0 then
		return false, "NotInRun"
	end
	if player:GetAttribute("Downed") then
		return false, "Downed"
	end
	if not firstTime(player, requestId) then
		return false, "Duplicate"
	end
	if InventoryService.Count(player, catalogId) < 1 then
		return false, "NotCarried"
	end

	local now = workspace:GetServerTimeNow()
	if item.kind == Consumables.Medicine then
		local health = SurvivalRules.UseMedicine(rules, item, humanoid.Health, humanoid.MaxHealth, now)
		if health == nil then
			return false, "Cooldown"
		end
		InventoryService.RemoveAll(player, { [catalogId] = 1 })
		SurvivalService.SetHealth(player, health)
	else
		InventoryService.RemoveAll(player, { [catalogId] = 1 })
		SurvivalRules.Eat(rules, item, now)
	end
	HealingService.Used:Fire(player, catalogId)
	return true, nil
end

function HealingService.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	Remotes.Get("UseConsumable").OnServerInvoke = HealingService.Use
	Players.PlayerRemoving:Connect(function(player)
		seenRequests[player] = nil
	end)
end

return HealingService
