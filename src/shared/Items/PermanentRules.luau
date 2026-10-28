-- Permanent items (GDD §15, §17, Q8–13, Q109–110, Q156). A Permanent item is the
-- same unique instance with the same stats and quality roll, flagged `permanent`:
-- it survives its owner's death, transfers ownership when dropped and picked up
-- (or traded, v0.14), and is lost if left on the ground when the world resets.
-- Any gear converts; rarity alone grants nothing.

local ItemCatalog = require(script.Parent.ItemCatalog)

local PermanentRules = {}

-- Any weapon, tool or armor piece can become Permanent (GDD §51); the Forge prices
-- the conversion by tier.
local GEAR = { Weapon = true, Tool = true, Armor = true }

function PermanentRules.IsEligible(catalogId: string): boolean
	local def = ItemCatalog.Get(catalogId)
	return def ~= nil and GEAR[def.family] == true
end

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
