-- Run checkpoints (GDD §29.1, §34.1, Q157). During an active run the server writes
-- a compact snapshot of each player's carried items every 15 s and shortly after
-- any inventory change, plus a heartbeat for this server. Every normal ending
-- (logout, death, extraction, planned shutdown) writes an "Ended" crash receipt
-- in its own profile operation; the checkpoint is deleted once that ending is
-- saved, so a crash before the save still leaves it to be recovered, and a
-- deletion that fails can never restore an ended run. Deletes name their run, so
-- they never remove a newer run's checkpoint. World place only.

local HttpService = game:GetService("HttpService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local CrashRecoveryRules = require(ReplicatedStorage.Shared.Recovery.CrashRecoveryRules)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local CheckpointStore = require(script.Parent.Parent.Infrastructure.CheckpointStore)
local DropService = require(script.Parent.DropService)
local InventoryService = require(script.Parent.InventoryService)
local ProfileService = require(script.Parent.ProfileService)
local WorldAdmissionService = require(script.Parent.WorldAdmissionService)

local RunCheckpointService = {}

RunCheckpointService.INTERVAL = 15
RunCheckpointService.DEBOUNCE = 1
RunCheckpointService.HEARTBEAT = 30
-- How long a cleared run waits for its ending to be saved before giving up (the
-- Ended receipt then guards it, and the checkpoint expires on its own).
RunCheckpointService.SAVE_WAIT_SECONDS = 600
RunCheckpointService.CLEAR_ATTEMPTS = 5
RunCheckpointService.CLEAR_RETRY_SECONDS = 2

local runs = {}
local clearing = {}

function RunCheckpointService.JobId(): string
	return CheckpointStore.JobId()
end

-- The run ID ProgressionService recorded for this run (the key of its receipt).
local function currentRunId(player: Player): string?
	local profile = ProfileService.GetProfile(player)
	local current = profile and profile.progression.currentRun
	return current and current.runId or nil
end

-- Deletes the run's checkpoint once the profile has saved its ending, retrying a
-- failed delete. One waiter per run at a time. The delete matches this run only,
-- so a newer run of the same user (a rejoin) keeps its own checkpoint.
local function clearWhenSaved(userId: number, runId: string)
	local key = userId .. ":" .. runId
	if clearing[key] then
		clearing[key] = "again"
		return
	end
	clearing[key] = true
	task.spawn(function()
		repeat
			clearing[key] = true
			local deadline = os.clock() + RunCheckpointService.SAVE_WAIT_SECONDS
			while not ProfileService.IsSaved(userId) and os.clock() < deadline do
				task.wait(1)
			end
			if ProfileService.IsSaved(userId) then
				for attempt = 1, RunCheckpointService.CLEAR_ATTEMPTS do
					if CheckpointStore.Clear(userId, runId) then
						break
					end
					task.wait(RunCheckpointService.CLEAR_RETRY_SECONDS * attempt)
				end
			end
		until clearing[key] ~= "again"
		clearing[key] = nil
	end)
end

local function write(player: Player)
	local run = runs[player]
	if run == nil then
		return
	end
	if run.writing then
		run.dirty = true
		return
	end
	run.writing = true
	run.dirty = false
	run.runId = run.runId or currentRunId(player) or HttpService:GenerateGUID(false)
	local checkpoint = CrashRecoveryRules.Checkpoint(
		run.runId,
		CheckpointStore.JobId(),
		InventoryService.Items(player),
		run.transferred,
		os.time()
	)
	CheckpointStore.Write(player.UserId, checkpoint)
	run.writing = false
	if not run.checkpointed then
		-- From now on the checkpoint, not the loadout recorded at Play, recovers it.
		run.checkpointed = true
		ProfileService.Mutate(player, function(profile)
			CrashRecoveryRules.Checkpointed(profile, run.runId)
		end)
	end
	-- The run may have ended while the write was in flight: clear again then.
	if runs[player] ~= run then
		clearWhenSaved(player.UserId, run.runId)
	elseif run.dirty then
		task.spawn(write, player)
	end
end

local function schedule(player: Player)
	local run = runs[player]
	if run and not run.scheduled then
		run.scheduled = true
		task.delay(RunCheckpointService.DEBOUNCE, function()
			run.scheduled = false
			write(player)
		end)
	end
end

function RunCheckpointService.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	WorldAdmissionService.RunStarted:Connect(function(player, _, _, runId)
		-- The Play's consume recorded the run, so the checkpoint and the Ended
		-- receipt share one key.
		runs[player] = { runId = runId or currentRunId(player), transferred = {} }
		-- Written at once, not debounced: the consumed loadout is already saved out
		-- of the profile, so until this lands a crash would lose it.
		task.spawn(write, player)
	end)
	-- Any ending other than a crash clears the checkpoint once it is saved (Q157).
	WorldAdmissionService.RunEnded:Connect(function(player)
		local run = runs[player]
		runs[player] = nil
		local runId = run and (run.runId or currentRunId(player))
		if runId then
			clearWhenSaved(player.UserId, runId)
		end
	end)
	InventoryService.Changed:Connect(schedule)
	-- Items handed to the world or a chest are not restored after a crash.
	DropService.Released:Connect(function(player, item)
		local run = runs[player]
		if run and item.instanceId then
			run.transferred[item.instanceId] = true
			schedule(player)
		end
	end)
	task.spawn(function()
		local sinceBeat = math.huge
		while true do
			if sinceBeat >= RunCheckpointService.HEARTBEAT then
				sinceBeat = 0
				CheckpointStore.Beat(CheckpointStore.JobId(), os.time())
			end
			task.wait(RunCheckpointService.INTERVAL)
			sinceBeat += RunCheckpointService.INTERVAL
			for player in runs do
				task.spawn(write, player)
			end
		end
	end)
end

return RunCheckpointService
