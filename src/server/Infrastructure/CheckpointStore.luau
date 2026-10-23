-- Short-lived run checkpoints and server heartbeats (GDD §29.1, §34.1). Uses
-- MemoryStore hash maps with expiry, so checkpoints never become a source of
-- truth for the vault; falls back to server memory where MemoryStore is
-- unavailable (Studio without API access, headless specs). Every call is guarded:
-- a MemoryStore outage only means a crash cannot be recovered (documented).
-- Deletes name the run they mean, so clearing one run never removes another's.

local HttpService = game:GetService("HttpService")

local CheckpointStore = {}

CheckpointStore.CHECKPOINT_EXPIRY = 24 * 3600
CheckpointStore.HEARTBEAT_EXPIRY = 90
-- A cleared checkpoint leaves a short-lived marker (a delete cannot compare).
CheckpointStore.CLEARED_EXPIRY = 60

local fallback = { checkpoints = {}, heartbeats = {} }
local maps = nil
local jobId = nil

-- This server's ID in checkpoints and heartbeats (a fixed one per Studio session).
function CheckpointStore.JobId(): string
	if jobId == nil then
		local id = game.JobId
		jobId = if type(id) == "string" and id ~= "" then id else ("studio-" .. HttpService:GenerateGUID(false))
	end
	return jobId
end

local function open()
	if maps ~= nil then
		return maps
	end
	local ok, service = pcall(function()
		return game:GetService("MemoryStoreService")
	end)
	if ok and service then
		local okMaps, result = pcall(function()
			return {
				checkpoints = service:GetHashMap("FlintbornRunCheckpoints"),
				heartbeats = service:GetHashMap("FlintbornServerHeartbeats"),
			}
		end)
		if okMaps then
			maps = result
			return maps
		end
	end
	maps = false
	return maps
end

local function set(kind: string, key: string, value, expiry: number)
	local store = open()
	if store then
		local ok, err = pcall(function()
			store[kind]:SetAsync(key, value, expiry)
		end)
		if ok then
			return true
		end
		warn(("[CheckpointStore] %s write failed: %s"):format(kind, tostring(err)))
	end
	fallback[kind][key] = value
	return store == false
end

local function get(kind: string, key: string)
	local store = open()
	if store then
		local ok, value = pcall(function()
			return store[kind]:GetAsync(key)
		end)
		if ok then
			return true, value
		end
		return false, nil
	end
	return true, fallback[kind][key]
end

local function isRun(value, runId: string): boolean
	return type(value) == "table" and value.runId == runId and not value.cleared
end

function CheckpointStore.Write(userId: number, checkpoint)
	return set("checkpoints", tostring(userId), checkpoint, CheckpointStore.CHECKPOINT_EXPIRY)
end

-- Returns (ok, checkpointOrNil); ok is false when the store could not be read.
function CheckpointStore.Read(userId: number)
	local ok, value = get("checkpoints", tostring(userId))
	if type(value) == "table" and value.cleared then
		value = nil
	end
	return ok, value
end

-- Deletes the user's checkpoint only while it still belongs to `runId`: a newer
-- run's checkpoint written meanwhile stays. Returns false when the shared store
-- could not be reached (the caller retries).
function CheckpointStore.Clear(userId: number, runId: string): boolean
	local key = tostring(userId)
	if isRun(fallback.checkpoints[key], runId) then
		fallback.checkpoints[key] = nil
	end
	local store = open()
	if not store then
		return true
	end
	local ok, err = pcall(function()
		store.checkpoints:UpdateAsync(key, function(old)
			if not isRun(old, runId) then
				-- Another run's checkpoint (or none): returning nil writes nothing.
				return nil
			end
			return { runId = runId, cleared = true }
		end, CheckpointStore.CLEARED_EXPIRY)
	end)
	if not ok then
		warn(("[CheckpointStore] checkpoints clear failed: %s"):format(tostring(err)))
	end
	return ok
end

function CheckpointStore.Beat(jobId: string, now: number)
	set("heartbeats", jobId, now, CheckpointStore.HEARTBEAT_EXPIRY)
end

-- Returns (ok, lastBeatOrNil).
function CheckpointStore.LastBeat(jobId: string)
	return get("heartbeats", jobId)
end

return CheckpointStore
