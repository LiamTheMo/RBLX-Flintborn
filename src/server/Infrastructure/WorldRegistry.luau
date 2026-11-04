-- Registry of live public worlds in a MemoryStore sorted map, shared by every lobby
-- and world server in the universe. Lobbies reserve worlds and record their access
-- codes; worlds report their player count and exclusions. Entries expire on their
-- own if a world stops reporting.
--
-- Each world's access code is also kept in a separate, long-lived hash map (CODES)
-- that only servers write. A world whose registry entry was lost (a failed first
-- write, or a MemoryStore outage long enough to expire it) reads its code back from
-- there and lists itself again; without it, no lobby could find it. Teleport data
-- would carry the code too, but it passes through the client, so it is not used.

local MemoryStoreService = game:GetService("MemoryStoreService")

local WorldRegistry = {}

WorldRegistry.MAP_NAME = "FlintbornWorlds_v1"
WorldRegistry.ENTRY_TTL_SECONDS = 180
WorldRegistry.MAX_LISTED = 100
WorldRegistry.CODES_MAP_NAME = "FlintbornWorldCodes_v1"
-- Longer than any world server is expected to run; removed when it closes.
WorldRegistry.CODE_TTL_SECONDS = 7 * 24 * 3600

local map = nil
local codes = nil

local function getMap()
	if map == nil then
		map = MemoryStoreService:GetSortedMap(WorldRegistry.MAP_NAME)
	end
	return map
end

local function getCodes()
	if codes == nil then
		codes = MemoryStoreService:GetHashMap(WorldRegistry.CODES_MAP_NAME)
	end
	return codes
end

-- All current entries (decoded). Returns (ok, worlds | error).
function WorldRegistry.List()
	return pcall(function()
		local worlds = {}
		for _, item in getMap():GetRangeAsync(Enum.SortDirection.Ascending, WorldRegistry.MAX_LISTED) do
			if type(item.value) == "table" then
				table.insert(worlds, item.value)
			end
		end
		return worlds
	end)
end

-- Atomically edits one world's entry. `transform(old)` returns the new entry or nil
-- to leave it unchanged. Returns (ok, newEntry | error).
function WorldRegistry.Update(privateServerId: string, transform: (any) -> any)
	return pcall(function()
		return getMap():UpdateAsync(privateServerId, transform, WorldRegistry.ENTRY_TTL_SECONDS)
	end)
end

function WorldRegistry.Remove(privateServerId: string)
	return pcall(function()
		getMap():RemoveAsync(privateServerId)
	end)
end

-- Records a world's access code (lobby, when it reserves the world). Returns (ok, error?).
function WorldRegistry.SaveCode(privateServerId: string, accessCode: string)
	return pcall(function()
		getCodes():SetAsync(privateServerId, accessCode, WorldRegistry.CODE_TTL_SECONDS)
	end)
end

-- A world's recorded access code. Returns (ok, code | nil | error).
function WorldRegistry.GetCode(privateServerId: string)
	return pcall(function()
		local code = getCodes():GetAsync(privateServerId)
		return if type(code) == "string" and code ~= "" then code else nil
	end)
end

function WorldRegistry.RemoveCode(privateServerId: string)
	return pcall(function()
		getCodes():RemoveAsync(privateServerId)
	end)
end

return WorldRegistry
