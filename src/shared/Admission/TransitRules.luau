-- Loss-free transit of a player's unvaulted items between the lobby and a world
-- (GDD §31.4, §53, Q155). Pressing Deploy moves every unvaulted lobby backpack
-- item, materials included (GDD §53), into one transit reservation. Successful
-- Play consumes it exactly once; any failure before that rolls it back. These
-- functions run inside ProfileService operations.

local InventoryRules = require(script.Parent.Parent.Inventory.InventoryRules)
local TradeRules = require(script.Parent.Parent.Economy.TradeRules)

local TransitRules = {}

TransitRules.Reserved = "Reserved"

-- True for a lobby backpack entry that may enter a run: every entry, materials
-- included (GDD §53 reverses §45, which kept materials in the lobby).
function TransitRules.Deployable(item): boolean
	return type(item) == "table" and type(item.catalogId) == "string"
end

-- Moves every deployable lobby backpack slot into a new reservation (malformed
-- entries stay behind). Errors (changing nothing, since operations run on a copy)
-- if a reservation already exists, or while a trade settles (a rollback cannot
-- reclaim items carried into a run).
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

-- Hands the reserved items to the starting run and clears the reservation. Every
-- material stack leaves the lobby tagged carried in whole, so the Center bonus
-- never multiplies it, whoever extracts it (GDD §53).
function TransitRules.Consume(profile, reservationId: string)
	local transit = profile.transit
	if transit == nil or transit.reservationId ~= reservationId then
		error("No matching transit reservation")
	end
	profile.transit = nil
	return InventoryRules.MarkCarried(transit.items)
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
