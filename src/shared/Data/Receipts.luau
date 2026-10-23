-- Player-facing receipts (GDD §25.2). Each kind keeps only its newest entries so
-- profiles stay bounded; the operation journal still guards exactly-once commits.

local Receipts = {}

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
