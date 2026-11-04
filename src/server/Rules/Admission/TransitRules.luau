-- Loss-free transit of a player's unvaulted items between the lobby and a world
-- (GDD §31.4, §53, Q155). Pressing Deploy moves every unvaulted lobby backpack
-- item, materials included (GDD §53), into one transit reservation. Successful
-- Play consumes it exactly once; any failure before that rolls it back. These
-- functions run inside ProfileService operations.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local InventoryRules = require(ReplicatedStorage.Shared.Inventory.InventoryRules)
local LobbyLoadoutRules = require(script.Parent.Parent.Inventory.LobbyLoadoutRules)
local TradeRules = require(ReplicatedStorage.Shared.Economy.TradeRules)

local TransitRules = {}

TransitRules.Reserved = "Reserved"

-- True for a lobby backpack entry that may enter a run: every entry, materials
-- included (GDD §53 reverses §45, which kept materials in the lobby).
function TransitRules.Deployable(item): boolean
	return type(item) == "table" and type(item.catalogId) == "string"
end

-- Moves every deployable lobby backpack slot into a new reservation (malformed
-- entries stay behind), and the lobby hotbar and worn armour too, each tagged with
-- its place (LobbyLoadoutRules.TakePlaced) so the run starts with them where they
-- were. Errors (changing nothing, since operations run on a copy)
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
	for _, item in LobbyLoadoutRules.TakePlaced(profile) do
		table.insert(deploying, item)
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

-- Returns reserved items to the lobby: hotbar and worn armour to their places,
-- the rest to the lobby backpack (LobbyLoadoutRules.Return). A missing
-- reservation is a no-op.
function TransitRules.Rollback(profile)
	local transit = profile.transit
	if transit == nil then
		return 0
	end
	local returned = 0
	for _, item in transit.items do
		LobbyLoadoutRules.Return(profile, item)
		returned += 1
	end
	profile.transit = nil
	return returned
end

return TransitRules
