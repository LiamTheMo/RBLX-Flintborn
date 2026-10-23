-- Moves a player's unvaulted items in and out of transit (GDD §31.4, Q155). Deploy
-- reserves every lobby backpack item; successful Play consumes the reservation once;
-- any failure, menu exit or stale reservation rolls it back. Nothing is ever lost
-- before a confirmed spawn. The consume also records the new run (crash recovery),
-- and no new run starts while an earlier one on another server is unsettled.

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local CrashRecoveryRules = require(ReplicatedStorage.Shared.Recovery.CrashRecoveryRules)
local InventoryRules = require(ReplicatedStorage.Shared.Inventory.InventoryRules)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local ProfileSchema = require(ReplicatedStorage.Shared.Data.ProfileSchema)
local TransitRules = require(ReplicatedStorage.Shared.Admission.TransitRules)
local CheckpointStore = require(script.Parent.Parent.Infrastructure.CheckpointStore)
local ProfileService = require(script.Parent.ProfileService)
local TravelService = require(script.Parent.TravelService)

local LoadoutService = {}

-- Reservation ID each world player arrived with, from teleport data.
local arrivedWith = {}
-- What Consume took for a Play that has not entered the run yet, so a failed save
-- or a departure can put it back exactly once.
local unconfirmed = {}

-- Reserves every unvaulted item and saves before the player travels.
-- Returns (reservationId) or (nil, reason).
function LoadoutService.Reserve(player: Player)
	local reservationId = HttpService:GenerateGUID(false)
	local ok, result = ProfileService.RunOperation(
		player,
		"transit:" .. reservationId,
		"TransitReserve",
		function(profile)
			return TransitRules.Reserve(profile, reservationId, os.time())
		end
	)
	if not ok then
		return nil, tostring(result)
	end
	local saved, reason = ProfileService.SaveNow(player)
	if not saved then
		LoadoutService.Rollback(player)
		return nil, "Could not save before travelling: " .. tostring(reason)
	end
	return reservationId
end

-- Puts back what an unconfirmed Consume took: the reservation as it was and any
-- maintenance receipts as Pending again, and settles the run it recorded (it never
-- started, so it must never be restored). Runs at most once per Consume.
local function unconsume(player: Player)
	local taken = unconfirmed[player]
	if taken == nil then
		return true
	end
	unconfirmed[player] = nil
	local ok = ProfileService.RunOperation(
		player,
		"unconsume:" .. HttpService:GenerateGUID(false),
		"TransitUnconsume",
		function(profile)
			if taken.transit then
				if profile.transit == nil then
					profile.transit = ProfileSchema.DeepCopy(taken.transit)
				else
					for _, item in ProfileSchema.DeepCopy(taken.transit.items) do
						table.insert(profile.lobbyBackpack.slots, item)
					end
				end
			end
			for _, operationId in taken.maintenance do
				local receipt = profile.receipts.maintenance[operationId]
				if receipt then
					receipt.status = "Pending"
				end
			end
			local run = profile.progression.currentRun
			if run and run.runId == taken.runId then
				CrashRecoveryRules.MarkEnded(profile, os.time())
			end
		end
	)
	if not ok then
		warn("[LoadoutService] Could not return consumed items for " .. player.Name)
		return false
	end
	if taken.transit and player.Parent then
		arrivedWith[player] = taken.transit.reservationId
	end
	return true
end

-- Undoes a Play that never entered the run but keeps the reservation, so the
-- player can press Play again with the same loadout (GDD §31.3 #8).
function LoadoutService.Restore(player: Player)
	return unconsume(player)
end

-- Returns reserved items to the lobby backpack, first undoing a Play that never
-- entered the run. Safe to call when nothing is reserved.
function LoadoutService.Rollback(player: Player)
	unconsume(player)
	local profile = ProfileService.GetProfile(player)
	if profile == nil or profile.transit == nil then
		return true
	end
	local id = "rollback:" .. profile.transit.reservationId
	local ok = ProfileService.RunOperation(player, id, "TransitRollback", TransitRules.Rollback)
	return ok
end

-- Pending maintenance receipts (items saved by a safe kick, GDD §30).
local function pendingMaintenance(profile)
	local pending = {}
	for operationId, receipt in profile.receipts.maintenance do
		if receipt.status == "Pending" then
			table.insert(pending, operationId)
		end
	end
	table.sort(pending)
	return pending
end

-- True while a run this profile started on another server is not yet settled:
-- crash recovery must restore it before a new run may replace its record.
function LoadoutService.RecoveryPending(player: Player): boolean
	local profile = ProfileService.GetProfile(player)
	return profile ~= nil and CrashRecoveryRules.Unsettled(profile, CheckpointStore.JobId()) ~= nil
end

-- What the run inventory will hold of `items`: the same packing InventoryService
-- applies at run start, whose leftovers it saves back to the lobby backpack.
local function carriedPart(items)
	local inventory = InventoryRules.FromItems(ProfileSchema.DeepCopy(items))
	return InventoryRules.Items(inventory)
end

-- Consumes this player's reservation on a confirmed spawn, together with anything
-- earlier safe kicks escrowed, in ONE operation: maintenance receipts are marked
-- restored only if the transit consume succeeds too. The same operation records
-- the new run, so a crash before its first checkpoint can still restore the
-- loadout. Returns (ok, items, changed, runId); `changed` means the profile must
-- be saved before the run starts. The caller then calls Confirm once the run
-- starts, or Restore to put everything back.
function LoadoutService.Consume(player: Player)
	local profile = ProfileService.GetProfile(player)
	if profile == nil or LoadoutService.RecoveryPending(player) then
		return false, {}, false, nil
	end
	local jobId = CheckpointStore.JobId()
	local runId = HttpService:GenerateGUID(false)
	local reservationId = arrivedWith[player]
	if profile.transit == nil or profile.transit.reservationId ~= reservationId then
		reservationId = nil
	end
	local pending = pendingMaintenance(profile)
	if reservationId == nil and #pending == 0 then
		-- Nothing to carry in or to lose: the run is still named for its receipts.
		ProfileService.Mutate(player, function(working)
			CrashRecoveryRules.BeginRun(working, runId, jobId, {}, os.time())
		end)
		return true, {}, false, runId
	end
	local items, taken = {}, nil
	-- One ID per attempt: a restored reservation may be consumed again later.
	local operationId = "consume:" .. HttpService:GenerateGUID(false)
	local ok, _, applied = ProfileService.RunOperation(player, operationId, "TransitConsume", function(working)
		items, taken = {}, { transit = nil, maintenance = {}, runId = runId }
		if reservationId then
			taken.transit = ProfileSchema.DeepCopy(working.transit)
			for _, item in TransitRules.Consume(working, reservationId) do
				table.insert(items, item)
			end
		end
		for _, receiptId in pending do
			local receipt = working.receipts.maintenance[receiptId]
			if receipt and receipt.status == "Pending" then
				receipt.status = "Restored"
				table.insert(taken.maintenance, receiptId)
				for _, item in receipt.items do
					table.insert(items, item)
				end
			end
		end
		CrashRecoveryRules.BeginRun(working, runId, jobId, carriedPart(items), os.time())
		return { reservationId = reservationId, restored = #taken.maintenance, runId = runId }
	end)
	-- An operation that was already committed hands nothing out a second time.
	if not ok or not applied then
		return false, {}, false, nil
	end
	arrivedWith[player] = nil
	unconfirmed[player] = taken
	if #taken.maintenance > 0 then
		player:SetAttribute("MaintenanceNotice", nil)
	end
	return true, ProfileSchema.DeepCopy(items), true, runId
end

-- The consumed items have entered a run (they are at risk from now on).
function LoadoutService.Confirm(player: Player)
	unconfirmed[player] = nil
end

-- Items that will enter the run on the next Deploy (lobby preview).
function LoadoutService.Preview(player: Player)
	local profile = ProfileService.GetProfile(player)
	return profile and profile.lobbyBackpack.slots or {}
end

local function reservationFromTeleport(player: Player)
	local joinData = player:GetJoinData()
	local data = joinData and joinData.TeleportData
	local reservations = type(data) == "table" and data.reservations
	local id = type(reservations) == "table" and reservations[tostring(player.UserId)]
	return type(id) == "string" and id or nil
end

-- A reservation is only valid in the world it was made for. Anything else (the
-- lobby after a teleport that never landed, or a mismatched ID) is rolled back.
local function reconcile(player: Player, profile)
	if #pendingMaintenance(profile) > 0 then
		-- Tell the player their items survived a game update (GDD §30.2 #6).
		player:SetAttribute("MaintenanceNotice", true)
	end
	if profile.transit == nil then
		return
	end
	if PlaceConfig.IsWorld() then
		local claimed = reservationFromTeleport(player)
		if claimed ~= nil and claimed == profile.transit.reservationId then
			arrivedWith[player] = claimed
			return
		end
	end
	LoadoutService.Rollback(player)
end

function LoadoutService.Start()
	ProfileService.ProfileLoaded:Connect(reconcile)
	-- A graceful shutdown releases every profile without waiting for a Play that is
	-- still saving its consume: put those back first, or the release would store
	-- the consumed loadout and forget the profile before the Play could undo it.
	ProfileService.BeforeShutdown:Connect(function()
		for player in unconfirmed do
			unconsume(player)
		end
	end)
	TravelService.TeleportFailed:Connect(function(player)
		if PlaceConfig.IsLobby() then
			LoadoutService.Rollback(player)
		end
	end)
	Players.PlayerRemoving:Connect(function(player)
		-- Deferred: the departure rollback (ProfileService.BeforeRelease) runs first.
		task.defer(function()
			arrivedWith[player] = nil
			unconfirmed[player] = nil
		end)
	end)
end

return LoadoutService
