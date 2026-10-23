-- Maintenance-safe preservation (GDD §30, Q7, Q161b). Before an authorized safe kick
-- or a graceful shutdown, an at-risk player's exact held items are written to a
-- maintenance receipt in their profile and saved. Only then does the run end,
-- without a body. The items come back once, on the player's next successful Play
-- (LoadoutService), and are never treated as extracted or Forge-safe.

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local ProfileSchema = require(ReplicatedStorage.Shared.Data.ProfileSchema)
local InventoryService = require(script.Parent.InventoryService)
local ProfileService = require(script.Parent.ProfileService)
local WorldAdmissionService = require(script.Parent.WorldAdmissionService)

local MaintenanceService = {}

-- Saves the player's held items to escrow and ends their run without a body.
-- Returns false (and changes nothing) when the save fails: never promise a safe
-- removal that did not persist (GDD §30.2 #5).
function MaintenanceService.Preserve(player: Player): boolean
	if not PlaceConfig.IsWorld() or not WorldAdmissionService.IsAtRisk(player) then
		return true
	end
	local items = ProfileSchema.DeepCopy(InventoryService.Items(player))
	local operationId = "maintenance:" .. HttpService:GenerateGUID(false)
	local ok = ProfileService.RunOperation(player, operationId, "MaintenancePreserve", function(profile)
		profile.receipts.maintenance[operationId] = {
			items = items,
			at = os.time(),
			status = "Pending",
		}
	end)
	if not ok then
		return false
	end
	local saved = ProfileService.SaveNow(player)
	if not saved then
		warn("[MaintenanceService] Could not save maintenance escrow for " .. player.Name)
		return false
	end
	WorldAdmissionService.Preserve(player)
	return true
end

function MaintenanceService.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	-- A graceful shutdown (update or owner shutdown) preserves every active run.
	ProfileService.BeforeShutdown:Connect(function()
		for _, player in Players:GetPlayers() do
			local ok, err = pcall(MaintenanceService.Preserve, player)
			if not ok then
				warn("[MaintenanceService] Shutdown preserve failed: " .. tostring(err))
			end
		end
	end)
end

return MaintenanceService
