-- Registry of live public worlds in a MemoryStore sorted map, shared by every lobby
-- and world server in the universe. Lobbies reserve worlds and record their access
-- codes; worlds report their player count and exclusions. Entries expire on their
-- own if a world stops reporting.

local MemoryStoreService = game:GetService("MemoryStoreService")

local WorldRegistry = {}

WorldRegistry.MAP_NAME = "FlintbornWorlds_v1"
WorldRegistry.ENTRY_TTL_SECONDS = 180
WorldRegistry.MAX_LISTED = 100

local map = nil

local function getMap()
	if map == nil then
		map = MemoryStoreService:GetSortedMap(WorldRegistry.MAP_NAME)
	end
	return map
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

return WorldRegistry
