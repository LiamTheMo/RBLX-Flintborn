-- Rules for gathered drops on the ground (GDD §53). Every node hit drops its
-- material as a pickup: for the first 10 s only the player whose hit made it may
-- take it, then anyone; it vanishes after 2 minutes. Walking over it or pressing
-- Interact on it collects it. Times are server clock seconds. Player-dropped items
-- keep their own rules (DropService).

local GameConstants = require(script.Parent.Parent.GameConstants)

local GroundDrops = {}

GroundDrops.OWNER_SECONDS = GameConstants.GATHER_DROP_OWNER_SECONDS
GroundDrops.LIFETIME_SECONDS = GameConstants.GATHER_DROP_LIFETIME_SECONDS
GroundDrops.PICKUP_RANGE = GameConstants.GATHER_DROP_PICKUP_RANGE

-- The claim rules of a drop made by `ownerId` at `now`.
function GroundDrops.New(ownerId: number, now: number)
	return {
		ownerId = ownerId,
		ownerUntil = now + GroundDrops.OWNER_SECONDS,
		expiresAt = now + GroundDrops.LIFETIME_SECONDS,
	}
end

-- True once the drop has lived out its lifetime.
function GroundDrops.Expired(rules, now: number): boolean
	return now >= rules.expiresAt
end

-- Whether `userId`, `distance` studs from the drop, may take it at `now`, and why
-- not ("Expired", "TooFar", "NotYours").
function GroundDrops.CanClaim(rules, userId: number, distance: number, now: number): (boolean, string?)
	if GroundDrops.Expired(rules, now) then
		return false, "Expired"
	end
	if distance > GroundDrops.PICKUP_RANGE then
		return false, "TooFar"
	end
	if userId ~= rules.ownerId and now < rules.ownerUntil then
		return false, "NotYours"
	end
	return true, nil
end

return GroundDrops
