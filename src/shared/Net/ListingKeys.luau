-- Stable keys for the entries of a listing a client takes from (a body, a storage
-- chest). The server sends each entry's `key` with its index; a take names both,
-- and the server resolves the key, so a request sent after the list changed (a
-- double press, another looter) takes the item the player saw or nothing, never
-- the one that moved into that index. A unique item's key is its instance id; a
-- stack's is its catalog id, since any stack of one material is the same take.

local ListingKeys = {}

ListingKeys.STACK_PREFIX = "stack:"
ListingKeys.MAX_LENGTH = 80

function ListingKeys.KeyOf(item): string
	return item.instanceId or (ListingKeys.STACK_PREFIX .. tostring(item.catalogId))
end

-- The index in `list` of the entry `key` names, preferring `index` when it still
-- holds it. Returns (index) or (nil, reason): "BadRequest" for malformed
-- arguments, "Gone" when no entry has that key any more.
function ListingKeys.Resolve(list, index: any, key: any): (number?, string?)
	if type(index) ~= "number" or index ~= index or index % 1 ~= 0 then
		return nil, "BadRequest"
	end
	if type(key) ~= "string" or #key == 0 or #key > ListingKeys.MAX_LENGTH then
		return nil, "BadRequest"
	end
	local at = list[index]
	if at ~= nil and ListingKeys.KeyOf(at) == key then
		return index, nil
	end
	for position, entry in list do
		if ListingKeys.KeyOf(entry) == key then
			return position, nil
		end
	end
	return nil, "Gone"
end

return ListingKeys
