-- Server half of Shared.Data.Receipts: what only the server uses. Everything in
-- ReplicatedStorage is downloaded to every player, so the shared module keeps
-- only what clients need; this one clones it and adds the rest, and server code
-- requires this module.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local SharedReceipts = require(ReplicatedStorage.Shared.Data.Receipts)

local Receipts = table.clone(SharedReceipts)

Receipts.RETENTION = 20

-- Stores `receipt` (which must carry `at`) under `id`, dropping the oldest beyond
-- the retention limit.
function Receipts.Store(map, id: string, receipt)
	map[id] = receipt
	local ids = {}
	for key in map do
		table.insert(ids, key)
	end
	table.sort(ids, function(a, b)
		return map[a].at < map[b].at
	end)
	for index = 1, #ids - Receipts.RETENTION do
		map[ids[index]] = nil
	end
end

return Receipts
