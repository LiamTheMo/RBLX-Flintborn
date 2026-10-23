-- Exactly-once profile operations (GDD §23.3). Every grant, charge or transfer runs
-- through Run with a stable operation ID: a committed ID returns its stored result
-- and never applies twice, and a failed operation leaves the profile untouched.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local ProfileSchema = require(ReplicatedStorage.Shared.Data.ProfileSchema)
local Validation = require(ReplicatedStorage.Shared.Data.Validation)

local OperationJournal = {}

-- Committed records kept per profile; older ones are trimmed to bound profile size.
OperationJournal.RETENTION = 200

export type Record = {
	kind: string,
	status: string,
	at: number,
	result: any,
}

function OperationJournal.Get(profile, operationId: string): Record?
	return profile.operations.records[operationId]
end

local function trim(journal)
	while #journal.order > OperationJournal.RETENTION do
		local oldest = table.remove(journal.order, 1)
		journal.records[oldest] = nil
	end
end

-- Applies `apply(working)` to a copy of the profile and commits it only if `apply`
-- returns without error. Returns (result, applied): applied is false when the ID was
-- already committed and the stored result is returned instead.
function OperationJournal.Run(profile, operationId: string, kind: string, now: number, apply: (any) -> any)
	assert(Validation.IsId(operationId), "Invalid operation ID")
	local existing = profile.operations.records[operationId]
	if existing and existing.status == "committed" then
		return existing.result, false
	end

	local working = ProfileSchema.DeepCopy(profile)
	local result = apply(working)

	-- Commit: replace the profile's contents in place so callers' references stay valid.
	table.clear(profile)
	for key, value in working do
		profile[key] = value
	end
	local journal = profile.operations
	journal.records[operationId] = { kind = kind, status = "committed", at = now, result = result }
	table.insert(journal.order, operationId)
	trim(journal)
	profile.lastCommittedOperationId = operationId
	return result, true
end

return OperationJournal
