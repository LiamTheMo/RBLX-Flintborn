-- Unique item instance records (GDD §22.1, §23.2). Every weapon, tool, armor piece
-- or other non-stacking item exists as exactly one record with one owner and one
-- location. IDs come from the server's generator; clients never create them.

local Validation = require(script.Parent.Validation)

local ItemInstance = {}

-- Where a unique item can be. Exactly one at a time.
ItemInstance.Locations = {
	Vault = "Vault",
	LobbyBackpack = "LobbyBackpack",
	Transit = "Transit",
	Carried = "Carried",
	WorldDropped = "WorldDropped",
	BaseStored = "BaseStored",
	TradeEscrow = "TradeEscrow",
	ForgeReserved = "ForgeReserved",
	Consumed = "Consumed",
}

-- Quality rolls are at most ±5% of catalog stats (GDD Q138).
ItemInstance.MAX_QUALITY_ROLL = 0.05

export type Record = {
	instanceId: string,
	catalogId: string,
	ownerId: number,
	location: string,
	qualityRoll: number,
	acquisitionId: string?,
}

function ItemInstance.New(
	generateId: () -> string,
	catalogId: string,
	ownerId: number,
	location: string,
	qualityRoll: number?,
	acquisitionId: string?
): Record
	local record = {
		instanceId = generateId(),
		catalogId = catalogId,
		ownerId = ownerId,
		location = location,
		qualityRoll = qualityRoll or 0,
		acquisitionId = acquisitionId,
	}
	local ok, reason = ItemInstance.Validate(record)
	assert(ok, reason)
	return record
end

function ItemInstance.Validate(record: any): (boolean, string?)
	if type(record) ~= "table" then
		return false, "Item record must be a table"
	end
	if not Validation.IsId(record.instanceId) then
		return false, "Invalid instanceId"
	end
	if not Validation.IsId(record.catalogId) then
		return false, "Invalid catalogId"
	end
	if not Validation.IsQuantity(record.ownerId, 1) then
		return false, "Invalid ownerId"
	end
	if ItemInstance.Locations[record.location] == nil then
		return false, "Unknown location " .. tostring(record.location)
	end
	local roll = record.qualityRoll
	if type(roll) ~= "number" or roll ~= roll or math.abs(roll) > ItemInstance.MAX_QUALITY_ROLL then
		return false, "Quality roll outside ±5%"
	end
	if record.acquisitionId ~= nil and not Validation.IsId(record.acquisitionId) then
		return false, "Invalid acquisitionId"
	end
	return true, nil
end

return ItemInstance
