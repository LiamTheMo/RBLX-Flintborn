-- Whole-server crash recovery (GDD §29.1, §34.1, Q157). While a run is active the
-- server keeps a short-lived checkpoint of the player's carried items and a
-- heartbeat for itself. Every normal ending — logout (a body), death, extraction,
-- a planned shutdown (maintenance escrow) — writes an "Ended" receipt for the run
-- in the same profile operation, then deletes the checkpoint once that is saved.
-- Deletion is best effort; the receipt is what guarantees that only a real crash
-- is ever restored. Recovery then restores the checkpointed items once, minus
-- anything already dropped, stored or traded away, into the lobby backpack.
--
-- The Play that starts a run records it in the profile together with the consume
-- (its ID, its server and, until the first checkpoint, the loadout it carries in),
-- so a crash before any checkpoint still restores the loadout, and a new run can
-- start only once the previous one is settled (one checkpoint slot per user). The
-- record also keeps, for the whole run, the material quantities carried in, which
-- the Center bonus never multiplies (GDD §53).

local ExtractionRules = require(script.Parent.Parent.Extraction.ExtractionRules)
local PermanentRules = require(script.Parent.Parent.Items.PermanentRules)
local ProgressionRules = require(script.Parent.Parent.Progression.ProgressionRules)

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

local function compact(items)
	local list = {}
	for _, item in items do
		table.insert(list, {
			instanceId = item.instanceId,
			catalogId = item.catalogId,
			quantity = item.quantity,
			qualityRoll = item.qualityRoll,
			ownerId = item.ownerId,
			permanent = item.permanent,
			ownershipVersion = item.ownershipVersion,
		})
	end
	return list
end

-- A compact checkpoint of the items a player carries right now.
function CrashRecoveryRules.Checkpoint(runId: string, jobId: string, items, transferred, now: number)
	local gone = {}
	for instanceId in transferred do
		table.insert(gone, instanceId)
	end
	return { runId = runId, jobId = jobId, at = now, items = compact(items), transferred = gone }
end

-- Records the run a Play starts, inside its consume operation. `carried` are the
-- consumed items that enter the run inventory (the rest stay in the lobby), kept
-- until the first checkpoint; their material quantities stay recorded as carried
-- in for the whole run (GDD §53).
function CrashRecoveryRules.BeginRun(profile, runId: string, jobId: string, carried, now: number)
	ProgressionRules.StartRun(profile, runId)
	local run = profile.progression.currentRun
	run.jobId = jobId
	run.startedAt = now
	run.loadout = if #carried > 0 then compact(carried) else nil
	ExtractionRules.RecordCarriedIn(run, carried)
end

-- The run's first checkpoint was written (or tried): from now on only
-- checkpoints recover it, so a MemoryStore outage never restores stale items.
function CrashRecoveryRules.Checkpointed(profile, runId: string)
	local run = profile.progression.currentRun
	if run and run.runId == runId then
		run.loadout = nil
	end
end

-- The run this profile last started, while nothing settled it and it belongs to
-- another server (or predates runs naming one). Holding the profile here means
-- that server released it or is gone, so the run must be recovered before a new
-- run replaces it. Nil when there is nothing to settle.
function CrashRecoveryRules.Unsettled(profile, jobId: string)
	local run = profile.progression.currentRun
	if run == nil or type(run.runId) ~= "string" or run.jobId == jobId then
		return nil
	end
	if profile.receipts.crashRecovery[run.runId] ~= nil then
		return nil
	end
	return run
end

-- A checkpoint made from the loadout an unsettled run recorded at Play: what a
-- run that crashed before its first checkpoint carried. Empty once checkpointed.
function CrashRecoveryRules.LoadoutCheckpoint(run)
	return {
		runId = run.runId,
		jobId = run.jobId,
		at = run.startedAt or 0,
		items = table.clone(run.loadout or {}),
		transferred = {},
	}
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
	run.loadout = nil
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
	CrashRecoveryRules.Checkpointed(profile, checkpoint.runId)
	return receipt
end

return CrashRecoveryRules
