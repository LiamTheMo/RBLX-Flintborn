-- Run checkpoints (GDD §29.1, §34.1, Q157). During an active run the server writes
-- a compact snapshot of each player's carried items every 15 s and shortly after
-- any inventory change, plus a heartbeat for this server. Every normal ending
-- (logout, death, extraction, planned shutdown) clears the checkpoint first, so
-- only a real crash leaves one behind. World place only.

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

local runs = {}
local jobId = nil

function RunCheckpointService.JobId(): string
	return jobId
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
	local checkpoint =
		CrashRecoveryRules.Checkpoint(run.runId, jobId, InventoryService.Items(player), run.transferred, os.time())
	CheckpointStore.Write(player.UserId, checkpoint)
	run.writing = false
	-- The run may have ended while the write was in flight: clear again then.
	if runs[player] ~= run then
		CheckpointStore.Clear(player.UserId)
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
	jobId = if game.JobId ~= "" then game.JobId else ("studio-" .. HttpService:GenerateGUID(false))
	WorldAdmissionService.RunStarted:Connect(function(player)
		local profile = ProfileService.GetProfile(player)
		local current = profile and profile.progression.currentRun
		runs[player] = {
			runId = current and current.runId or HttpService:GenerateGUID(false),
			transferred = {},
		}
		schedule(player)
	end)
	-- Any ending other than a crash clears the checkpoint (Q157: logouts lose items).
	WorldAdmissionService.RunEnded:Connect(function(player)
		runs[player] = nil
		task.spawn(CheckpointStore.Clear, player.UserId)
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
				CheckpointStore.Beat(jobId, os.time())
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
