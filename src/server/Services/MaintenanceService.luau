-- Maintenance-safe preservation (GDD §30, Q7, Q161b). Before an authorized safe kick
-- or a graceful shutdown, an at-risk player's exact held items are written to a
-- maintenance receipt in their profile and the run ends without a body, all
-- without yielding, so the same items can never also become a body, a drop or an
-- extraction (§30.2 #4, #8). The profile is saved afterwards; a failed save means
-- no kick (§30.2 #5). The items come back once, on the player's next successful
-- Play (LoadoutService), and are never treated as extracted or Forge-safe.

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local CrashRecoveryRules = require(ReplicatedStorage.Shared.Recovery.CrashRecoveryRules)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local ProfileSchema = require(ReplicatedStorage.Shared.Data.ProfileSchema)
local SessionStates = require(ReplicatedStorage.Shared.Admission.SessionStates)
local InventoryService = require(script.Parent.InventoryService)
local ProfileService = require(script.Parent.ProfileService)
local WorldAdmissionService = require(script.Parent.WorldAdmissionService)

local MaintenanceService = {}

-- Writes the held items to escrow and ends the run, without yielding. Returns
-- false (changing nothing) when the profile operation fails.
function MaintenanceService.Escrow(player: Player): boolean
	if not WorldAdmissionService.IsAtRisk(player) then
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
		CrashRecoveryRules.MarkEnded(profile, os.time())
	end)
	if not ok then
		warn("[MaintenanceService] Could not escrow items for " .. player.Name)
		return false
	end
	WorldAdmissionService.Preserve(player)
	local root = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
	if root then
		root.Anchored = true
	end
	return true
end

-- Escrows the player's held items, ends their run without a body and saves.
-- Returns false when the escrow or its save failed: never promise a safe removal
-- that did not persist (GDD §30.2 #5). Calling it again retries the save.
function MaintenanceService.Preserve(player: Player): boolean
	if not PlaceConfig.IsWorld() then
		return true
	end
	local preserved = WorldAdmissionService.GetState(player) == SessionStates.MaintenancePreserved
	if not preserved and not WorldAdmissionService.IsAtRisk(player) then
		return true
	end
	if not MaintenanceService.Escrow(player) then
		return false
	end
	local saved = ProfileService.SaveNow(player)
	if not saved then
		warn("[MaintenanceService] Could not save maintenance escrow for " .. player.Name)
		return false
	end
	return true
end

function MaintenanceService.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	-- A graceful shutdown (update or owner shutdown) preserves every active run at
	-- once, with no yield in between; ProfileService then saves all profiles in
	-- parallel as it releases them.
	ProfileService.BeforeShutdown:Connect(function()
		for _, player in Players:GetPlayers() do
			local ok, err = pcall(MaintenanceService.Escrow, player)
			if not ok then
				warn("[MaintenanceService] Shutdown preserve failed: " .. tostring(err))
			end
		end
	end)
	-- Players removed while the server shuts down are escrowed the same way.
	WorldAdmissionService.ShutdownDeparture:Connect(MaintenanceService.Escrow)
end

return MaintenanceService
