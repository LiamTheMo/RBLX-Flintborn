--!nocheck
-- Fake DataStore and MemoryStore services with latency, for specs that race saves,
-- checkpoints and deploy records against each other. Calls wait on `task.wait`, so
-- install a Scheduler first.
--
--     local FakeStores = require(game:GetService("ServerStorage").TestSupport.FakeStores)
--     local data = FakeStores.DataStore(0.3)   -- data.backing._data[key], data.service
--     local memory = FakeStores.MemoryStore()  -- memory.maps[name][key], memory.service

local FakeStores = {}

local function deepCopy(value)
	if type(value) ~= "table" then
		return value
	end
	local copy = {}
	for key, inner in value do
		copy[key] = deepCopy(inner)
	end
	return copy
end

-- A DataStoreService whose every store is one InMemoryDataStore (`backing`; set
-- backing.failNext to fail writes) whose reads and writes take `latency` seconds.
function FakeStores.DataStore(latency: number)
	local InMemoryDataStore = require(game:GetService("ServerScriptService").Server.Infrastructure.InMemoryDataStore)
	local backing = InMemoryDataStore.new()
	local store = {
		UpdateAsync = function(_, key, transform)
			task.wait(latency)
			return backing:UpdateAsync(key, transform)
		end,
		GetAsync = function(_, key)
			task.wait(latency)
			return backing:GetAsync(key)
		end,
	}
	return {
		backing = backing,
		service = {
			GetDataStore = function()
				return store
			end,
			GetRequestBudgetForRequestType = function()
				return 100
			end,
		},
	}
end

-- A MemoryStoreService of hash maps holding copies of what is written. Each call
-- first waits latency["Map.Method"] seconds when set; while `failing` every call
-- errors. `writes` counts successful SetAsync calls.
function FakeStores.MemoryStore()
	local memory = { maps = {}, latency = {}, failing = false, writes = 0 }
	local function hashMap(name: string)
		memory.maps[name] = memory.maps[name] or {}
		local function enter(method: string)
			if memory.failing then
				error("MemoryStore unavailable")
			end
			local seconds = memory.latency[name .. "." .. method]
			if seconds and seconds > 0 then
				task.wait(seconds)
			end
			return memory.maps[name]
		end
		return {
			SetAsync = function(_, key, value)
				enter("SetAsync")[key] = deepCopy(value)
				memory.writes += 1
				return true
			end,
			GetAsync = function(_, key)
				return deepCopy(enter("GetAsync")[key])
			end,
			RemoveAsync = function(_, key)
				enter("RemoveAsync")[key] = nil
			end,
			UpdateAsync = function(_, key, transform)
				local data = enter("UpdateAsync")
				local value = transform(deepCopy(data[key]))
				if value ~= nil then
					data[key] = deepCopy(value)
				end
				return value
			end,
		}
	end
	memory.service = {
		GetHashMap = function(_, name)
			return hashMap(name)
		end,
	}
	return memory
end

-- A MemoryStoreService that is down: GetHashMap errors, so stores fall back.
FakeStores.NoMemoryStore = {
	GetHashMap = function()
		error("MemoryStore unavailable in specs")
	end,
}

return FakeStores
