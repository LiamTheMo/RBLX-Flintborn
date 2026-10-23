-- Spike traps (GDD §6.1). A trap hurts any at-risk player from another tribe who
-- steps on it, at most once per victim per cooldown, under the normal combat rules
-- (no damage in safe zones or to the trap owner's own tribe). World place only.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local StructureCatalog = require(ReplicatedStorage.Shared.Building.StructureCatalog)
local BuildingService = require(script.Parent.BuildingService)
local CombatService = require(script.Parent.CombatService)

local TrapService = {}

local function arm(record)
	local lastHit = {}
	record.part.Touched:Connect(function(hit)
		local model = hit:FindFirstAncestorOfClass("Model")
		local victim = model and Players:GetPlayerFromCharacter(model)
		if victim == nil or BuildingService.Get(record.part) == nil then
			return
		end
		if BuildingService.OwnerKey(victim) == record.ownerKey then
			return
		end
		local at = os.clock()
		if lastHit[victim] and at - lastHit[victim] < StructureCatalog.TRAP_COOLDOWN then
			return
		end
		lastHit[victim] = at
		CombatService.ApplyEnvironmentHit(victim, StructureCatalog.TRAP_DAMAGE)
	end)
end

function TrapService.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	BuildingService.Placed:Connect(function(record)
		if record.pieceId == "Trap" then
			arm(record)
		end
	end)
end

return TrapService
