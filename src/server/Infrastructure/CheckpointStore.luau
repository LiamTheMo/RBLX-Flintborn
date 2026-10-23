-- Short-lived run checkpoints and server heartbeats (GDD §29.1, §34.1). Uses
-- MemoryStore hash maps with expiry, so checkpoints never become a source of
-- truth for the vault; falls back to server memory where MemoryStore is
-- unavailable (Studio without API access, headless specs). Every call is guarded:
-- a MemoryStore outage only means a crash cannot be recovered (documented).

local CheckpointStore = {}

CheckpointStore.CHECKPOINT_EXPIRY = 24 * 3600
CheckpointStore.HEARTBEAT_EXPIRY = 90

local fallback = { checkpoints = {}, heartbeats = {} }
local maps = nil

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

local function remove(kind: string, key: string)
	fallback[kind][key] = nil
	local store = open()
	if store then
		pcall(function()
			store[kind]:RemoveAsync(key)
		end)
	end
end

function CheckpointStore.Write(userId: number, checkpoint)
	return set("checkpoints", tostring(userId), checkpoint, CheckpointStore.CHECKPOINT_EXPIRY)
end

-- Returns (ok, checkpointOrNil); ok is false when the store could not be read.
function CheckpointStore.Read(userId: number)
	return get("checkpoints", tostring(userId))
end

function CheckpointStore.Clear(userId: number)
	remove("checkpoints", tostring(userId))
end

function CheckpointStore.Beat(jobId: string, now: number)
	set("heartbeats", jobId, now, CheckpointStore.HEARTBEAT_EXPIRY)
end

-- Returns (ok, lastBeatOrNil).
function CheckpointStore.LastBeat(jobId: string)
	return get("heartbeats", jobId)
end

return CheckpointStore
