-- Crash recovery (GDD §29.1, §34.1, Q157). When a profile loads in either place,
-- a run checkpoint whose server no longer beats means that server crashed
-- mid-run: the checkpointed items (minus anything already handed away) return to
-- the lobby backpack once, through the operation journal, and the player sees a
-- notice. A run that crashed before its first checkpoint restores the loadout its
-- Play recorded instead. A live heartbeat means "not yet": the check repeats while
-- they stay, and a new run waits for it (LoadoutService.RecoveryPending), so a
-- crashed run is never overwritten, nor restored while its server still runs.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local CrashRecoveryRules = require(ReplicatedStorage.Shared.Recovery.CrashRecoveryRules)
local ProfileSchema = require(ReplicatedStorage.Shared.Data.ProfileSchema)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local CheckpointStore = require(script.Parent.Parent.Infrastructure.CheckpointStore)
local ProfileService = require(script.Parent.ProfileService)

local CrashRecoveryService = {}

CrashRecoveryService.RETRY_SECONDS = 15
-- Runs settled per check before waiting (a stale checkpoint, then the profile's run).
CrashRecoveryService.MAX_STEPS = 3

local function notify(player: Player, receipt)
	if player.Parent and receipt.restored > 0 then
		Remotes.Get("Notice"):FireClient(player, {
			title = "Server crashed — your items were recovered",
			text = ("%d item stack(s) are back in your lobby backpack."):format(receipt.restored),
		})
	end
end

-- The run to recover now, or (nil, outcome). Holding the profile here means any
-- other server released it or is gone, but a server that still beats might hold
-- a body of the same items, so a checkpoint with items waits for silence.
local function pick(player: Player, profile)
	local ok, checkpoint = CheckpointStore.Read(player.UserId)
	if not ok then
		return nil, "Unavailable"
	end
	local jobId = CheckpointStore.JobId()
	if checkpoint and CrashRecoveryRules.IsSettled(profile, checkpoint.runId) then
		-- The run ended normally (or was already restored); only its delete failed.
		-- Deleted once that receipt is saved, so a crash first can still restore it.
		if ProfileService.IsSaved(player.UserId) then
			CheckpointStore.Clear(player.UserId, checkpoint.runId)
		end
		checkpoint = nil
	elseif checkpoint and checkpoint.jobId == jobId then
		-- This very server owns that run; it is not a crash.
		checkpoint = nil
	end
	if checkpoint == nil then
		local run = CrashRecoveryRules.Unsettled(profile, jobId)
		if run == nil then
			return nil, "NoCheckpoint"
		end
		-- Never checkpointed (its loadout), or its checkpoint is gone (nothing left).
		checkpoint = CrashRecoveryRules.LoadoutCheckpoint(run)
	end
	if #checkpoint.items == 0 then
		return checkpoint, nil
	end
	local beatOk, lastBeat = true, nil
	if checkpoint.jobId then
		beatOk, lastBeat = CheckpointStore.LastBeat(checkpoint.jobId)
	end
	if not beatOk then
		return nil, "Unavailable"
	end
	local verdict = CrashRecoveryRules.Classify(checkpoint, lastBeat, os.time())
	if verdict ~= "Eligible" then
		return nil, verdict
	end
	return checkpoint, nil
end

local function attempt(player: Player): string
	local profile = ProfileService.GetProfile(player)
	if profile == nil then
		return "NoProfile"
	end
	local checkpoint, outcome = pick(player, profile)
	if checkpoint == nil then
		return outcome
	end
	local done, result, applied = ProfileService.RunOperation(
		player,
		"crash:" .. checkpoint.runId,
		"CrashRecovery",
		function(working)
			local restored = CrashRecoveryRules.Restore(working, checkpoint, os.time())
			if restored == nil then
				error("AlreadyRestored", 0)
			end
			-- A checkpoint written before a catalog change may name removed items.
			ProfileSchema.PruneRetiredItems(working)
			return restored
		end
	)
	if not done and result ~= "AlreadyRestored" then
		-- The profile could not take it (e.g. the player left mid-check): keep the
		-- checkpoint so the next load tries again.
		return "Failed"
	end
	if done and applied then
		notify(player, result)
		-- Delete the checkpoint only once the restore is saved: a crash before that
		-- leaves both unchanged, so the run is still restored exactly once.
		if not ProfileService.SaveNow(player) then
			return "Restored"
		end
	end
	-- Only this run's checkpoint: a run started here meanwhile keeps its own.
	CheckpointStore.Clear(player.UserId, checkpoint.runId)
	return "Restored"
end

local function check(player: Player)
	while player.Parent do
		local outcome = nil
		for _ = 1, CrashRecoveryService.MAX_STEPS do
			outcome = attempt(player)
			if outcome ~= "Restored" then
				break
			end
		end
		if outcome == "NoCheckpoint" or outcome == "NoProfile" then
			return
		end
		task.wait(CrashRecoveryService.RETRY_SECONDS)
	end
end

function CrashRecoveryService.Start()
	ProfileService.ProfileLoaded:Connect(function(player)
		task.spawn(check, player)
	end)
end

return CrashRecoveryService
