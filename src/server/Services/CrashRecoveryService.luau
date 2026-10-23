-- Crash recovery (GDD §29.1, §34.1, Q157). When a profile loads in either place,
-- a run checkpoint whose server no longer beats means that server crashed
-- mid-run: the checkpointed items (minus anything already handed away) return to
-- the lobby backpack once, through the operation journal, and the player sees a
-- notice. A live heartbeat means "not yet": the check repeats while they stay.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local CrashRecoveryRules = require(ReplicatedStorage.Shared.Recovery.CrashRecoveryRules)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local CheckpointStore = require(script.Parent.Parent.Infrastructure.CheckpointStore)
local ProfileService = require(script.Parent.ProfileService)
local RunCheckpointService = require(script.Parent.RunCheckpointService)

local CrashRecoveryService = {}

CrashRecoveryService.RETRY_SECONDS = 100
CrashRecoveryService.MAX_RETRIES = 3

local function notify(player: Player, receipt)
	if player.Parent then
		Remotes.Get("Notice"):FireClient(player, {
			title = "Server crashed — your items were recovered",
			text = ("%d item stack(s) are back in your lobby backpack."):format(receipt.restored),
		})
	end
end

local function attempt(player: Player): string
	local ok, checkpoint = CheckpointStore.Read(player.UserId)
	if not ok then
		return "Unavailable"
	end
	if checkpoint and checkpoint.jobId == RunCheckpointService.JobId() then
		-- This very server owns the run; it is not a crash.
		return "ServerAlive"
	end
	local beatOk, lastBeat = true, nil
	if checkpoint then
		beatOk, lastBeat = CheckpointStore.LastBeat(checkpoint.jobId)
	end
	if not beatOk then
		return "Unavailable"
	end
	local verdict = CrashRecoveryRules.Classify(checkpoint, lastBeat, os.time())
	if verdict ~= "Eligible" then
		return verdict
	end
	local done, receipt = ProfileService.RunOperation(
		player,
		"crash:" .. checkpoint.runId,
		"CrashRecovery",
		function(profile)
			local restored = CrashRecoveryRules.Restore(profile, checkpoint, os.time())
			if restored == nil then
				error("AlreadyRestored", 0)
			end
			return restored
		end
	)
	CheckpointStore.Clear(player.UserId)
	if done then
		ProfileService.SaveNow(player)
		notify(player, receipt)
	end
	return "Restored"
end

local function check(player: Player)
	for _ = 1, CrashRecoveryService.MAX_RETRIES do
		local outcome = attempt(player)
		if outcome ~= "ServerAlive" and outcome ~= "Unavailable" then
			return
		end
		task.wait(CrashRecoveryService.RETRY_SECONDS)
		if not player.Parent then
			return
		end
	end
end

function CrashRecoveryService.Start()
	ProfileService.ProfileLoaded:Connect(function(player)
		task.spawn(check, player)
	end)
end

return CrashRecoveryService
