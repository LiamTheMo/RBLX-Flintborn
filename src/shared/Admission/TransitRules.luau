-- Loss-free transit of a player's unvaulted items between the lobby and a world
-- (GDD §31.4, Q155). Pressing Deploy moves every unvaulted lobby backpack item
-- except materials into one transit reservation: once extracted, materials stay in
-- the lobby for good (vault, Forge, market and trades), whatever route brought
-- them to the backpack. Successful Play consumes it exactly once; any failure
-- before that rolls it back. These functions run inside ProfileService operations.

local ItemCatalog = require(script.Parent.Parent.Items.ItemCatalog)
local TradeRules = require(script.Parent.Parent.Economy.TradeRules)

local TransitRules = {}

TransitRules.Reserved = "Reserved"

-- True for a lobby backpack entry that may enter a run: anything but a material.
function TransitRules.Deployable(item): boolean
	return item.instanceId ~= nil or not ItemCatalog.IsMaterial(item.catalogId)
end

-- Moves every deployable lobby backpack slot into a new reservation; materials
-- stay behind. Errors (changing nothing, since operations run on a copy) if a
-- reservation already exists, or while a trade settles (a rollback cannot reclaim
-- items carried into a run).
function TransitRules.Reserve(profile, reservationId: string, now: number)
	if profile.transit ~= nil then
		error("A transit reservation already exists")
	end
	if TradeRules.IsSettling(profile) then
		error(TradeRules.SETTLING, 0)
	end
	local deploying, staying = {}, {}
	for _, item in profile.lobbyBackpack.slots do
		table.insert(if TransitRules.Deployable(item) then deploying else staying, item)
	end
	profile.transit = {
		reservationId = reservationId,
		items = deploying,
		createdAt = now,
		status = TransitRules.Reserved,
	}
	profile.lobbyBackpack.slots = staying
	return reservationId
end

-- Hands the reserved items to the starting run and clears the reservation.
function TransitRules.Consume(profile, reservationId: string)
	local transit = profile.transit
	if transit == nil or transit.reservationId ~= reservationId then
		error("No matching transit reservation")
	end
	profile.transit = nil
	return transit.items
end

-- Returns reserved items to the lobby backpack. A missing reservation is a no-op.
function TransitRules.Rollback(profile)
	local transit = profile.transit
	if transit == nil then
		return 0
	end
	local slots = profile.lobbyBackpack.slots
	local returned = 0
	for _, item in transit.items do
		table.insert(slots, item)
		returned += 1
	end
	profile.transit = nil
	return returned
end

return TransitRules
