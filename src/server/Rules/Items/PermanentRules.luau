-- Server half of Shared.Items.PermanentRules: what only the server uses. Everything in
-- ReplicatedStorage is downloaded to every player, so the shared module keeps
-- only what clients need; this one clones it and adds the rest, and server code
-- requires this module.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local SharedPermanentRules = require(ReplicatedStorage.Shared.Items.PermanentRules)

local PermanentRules = table.clone(SharedPermanentRules)

-- A conversion source must be an owned, vaulted, eligible unique item that is not
-- already Permanent (§15.3). Returns (ok, reason).
function PermanentRules.CanConvert(item, ownerId: number)
	if item == nil or item.instanceId == nil then
		return false, "NoSource"
	end
	if item.permanent then
		return false, "AlreadyPermanent"
	end
	if item.ownerId ~= ownerId then
		return false, "NotYours"
	end
	if item.location ~= "Vault" then
		return false, "NotVaulted"
	end
	if not PermanentRules.IsEligible(item.catalogId) then
		return false, "NotEligible"
	end
	return true, nil
end

-- Converts the source in place: one instance, never an ordinary copy left behind.
-- The quality roll is kept exactly as rolled.
function PermanentRules.Convert(item, operationId: string, now: number)
	item.permanent = true
	item.ownershipVersion = 1
	item.provenance = { kind = "Forge", operationId = operationId, at = now }
	return item
end

-- Hands a dropped Permanent item to whoever picks it up.
function PermanentRules.Transfer(item, newOwnerId: number)
	item.ownerId = newOwnerId
	item.ownershipVersion = (item.ownershipVersion or 1) + 1
	item.location = "Carried"
	return item
end

-- The owner's ledger entry for a Permanent item (profile.permanentItems).
function PermanentRules.LedgerEntry(item, now: number)
	return {
		catalogId = item.catalogId,
		qualityRoll = item.qualityRoll,
		ownershipVersion = item.ownershipVersion,
		acquiredAt = now,
	}
end

return PermanentRules
