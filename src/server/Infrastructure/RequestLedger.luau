-- Remembers each player's recent request IDs so a replayed or duplicated request
-- is applied once. `capacity` is a function returning how many IDs to keep per
-- player; it is read on every request, so a service's tunable (and a spec that
-- changes it) takes effect at once.

local RequestLedger = {}
RequestLedger.__index = RequestLedger

function RequestLedger.new(capacity: () -> number)
	return setmetatable({ capacity = capacity, seen = {} }, RequestLedger)
end

-- True the first time `player` sends `requestId`; false for a repeat.
function RequestLedger:FirstTime(player: Player, requestId: string): boolean
	local seen = self.seen[player]
	if seen == nil then
		seen = { set = {}, order = {} }
		self.seen[player] = seen
	end
	if seen.set[requestId] then
		return false
	end
	seen.set[requestId] = true
	table.insert(seen.order, requestId)
	if #seen.order > self.capacity() then
		seen.set[table.remove(seen.order, 1)] = nil
	end
	return true
end

function RequestLedger:Forget(player: Player)
	self.seen[player] = nil
end

return RequestLedger
