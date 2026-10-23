-- Whole-server crash recovery (GDD §29.1, §34.1, Q157). While a run is active the
-- server keeps a short-lived checkpoint of the player's carried items and a
-- heartbeat for itself. Every normal ending — logout (a body), death, extraction,
-- a planned shutdown (maintenance escrow) — deletes the checkpoint first, so only
-- a real crash leaves one behind with no live heartbeat. Recovery then restores
-- the checkpointed items once, minus anything already dropped, stored or traded
-- away, into the lobby backpack.

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

-- Restores an eligible checkpoint once (the receipt keyed by run ID guards
-- repeats). Returns the receipt, or nil when this run was already recovered.
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
	local receipt = { at = now, status = "Restored", restored = restored, shown = false }
	receipts[checkpoint.runId] = receipt
	return receipt
end

return CrashRecoveryRules
