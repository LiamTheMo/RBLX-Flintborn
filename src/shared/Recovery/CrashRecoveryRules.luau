-- Whole-server crash recovery (GDD §29.1, §34.1, Q157). While a run is active the
-- server keeps a short-lived checkpoint of the player's carried items and a
-- heartbeat for itself. Every normal ending — logout (a body), death, extraction,
-- a planned shutdown (maintenance escrow) — writes an "Ended" receipt for the run
-- in the same profile operation, then deletes the checkpoint once that is saved.
-- Deletion is best effort; the receipt is what guarantees that only a real crash
-- is ever restored. Recovery then restores the checkpointed items once, minus
-- anything already dropped, stored or traded away, into the lobby backpack.

local PermanentRules = require(script.Parent.Parent.Items.PermanentRules)

local CrashRecoveryRules = {}

-- A server heartbeat older than this means the server is gone (placeholder).
CrashRecoveryRules.STALE_SECONDS = 90

-- "NoCheckpoint" (the run ended normally), "ServerAlive" (try again later) or
-- "Eligible".
function CrashRecoveryRules.Classify(checkpoint, heartbeatAt: number?, now: number): string
	if checkpoint == nil then
		return "NoCheckpoint"
	end
	if heartbeatAt ~= nil and now - heartbeatAt < CrashRecoveryRules.STALE_SECONDS then
		return "ServerAlive"
	end
	return "Eligible"
end

-- A compact checkpoint of the items a player carries right now.
function CrashRecoveryRules.Checkpoint(runId: string, jobId: string, items, transferred, now: number)
	local compact = {}
	for _, item in items do
		table.insert(compact, {
			instanceId = item.instanceId,
			catalogId = item.catalogId,
			quantity = item.quantity,
			qualityRoll = item.qualityRoll,
			ownerId = item.ownerId,
			permanent = item.permanent,
			ownershipVersion = item.ownershipVersion,
		})
	end
	local gone = {}
	for instanceId in transferred do
		table.insert(gone, instanceId)
	end
	return { runId = runId, jobId = jobId, at = now, items = compact, transferred = gone }
end

CrashRecoveryRules.Ended = "Ended"
CrashRecoveryRules.Restored = "Restored"
-- Receipts outlive any checkpoint (MemoryStore expiry is 24 h), then are pruned
-- so profiles stay bounded.
CrashRecoveryRules.RECEIPT_SECONDS = 2 * 24 * 3600

local function prune(receipts, now: number)
	for runId, receipt in receipts do
		if
			type(receipt) ~= "table"
			or type(receipt.at) ~= "number"
			or now - receipt.at > CrashRecoveryRules.RECEIPT_SECONDS
		then
			receipts[runId] = nil
		end
	end
end

-- Records that the profile's current run ended normally (extraction, death,
-- departure or maintenance), inside the ending's own profile operation. Returns
-- the run ID, or nil when no run is being tracked. Never replaces a receipt.
function CrashRecoveryRules.MarkEnded(profile, now: number): string?
	local run = profile.progression.currentRun
	local runId = run and run.runId
	if type(runId) ~= "string" then
		return nil
	end
	local receipts = profile.receipts.crashRecovery
	prune(receipts, now)
	if receipts[runId] == nil then
		receipts[runId] = { status = CrashRecoveryRules.Ended, at = now }
	end
	return runId
end

-- True when this run already has a receipt: it ended normally or was restored.
function CrashRecoveryRules.IsSettled(profile, runId: string): boolean
	return profile.receipts.crashRecovery[runId] ~= nil
end

-- Restores an eligible checkpoint once. Any receipt for the run (Ended or
-- Restored) refuses it. Returns the receipt, or nil when the run is settled.
function CrashRecoveryRules.Restore(profile, checkpoint, now: number)
	local receipts = profile.receipts.crashRecovery
	if receipts[checkpoint.runId] then
		return nil
	end
	local excluded = {}
	for _, instanceId in checkpoint.transferred or {} do
		excluded[instanceId] = true
	end
	local restored = 0
	for _, item in checkpoint.items do
		if item.instanceId == nil or not excluded[item.instanceId] then
			local copy = table.clone(item)
			if copy.instanceId then
				copy.location = "LobbyBackpack"
				if copy.permanent then
					profile.permanentItems[copy.instanceId] = PermanentRules.LedgerEntry(copy, now)
				end
			end
			-- Recovered items always land: recovery never deletes for lack of room.
			table.insert(profile.lobbyBackpack.slots, copy)
			restored += 1
		end
	end
	prune(receipts, now)
	local receipt = { at = now, status = CrashRecoveryRules.Restored, restored = restored, shown = false }
	receipts[checkpoint.runId] = receipt
	return receipt
end

return CrashRecoveryRules
