-- Shared guards for values that reach persistent state. The server applies these to
-- every quantity and ID; a client request is never trusted to be well-formed.

local Validation = {}

-- Upper bound for any stored count (well inside DataStore and Luau integer precision).
Validation.MAX_QUANTITY = 1_000_000_000

-- True for a finite whole number in [minimum, maximum].
function Validation.IsQuantity(value: any, minimum: number?, maximum: number?): boolean
	if type(value) ~= "number" or value ~= value then
		return false
	end
	if value == math.huge or value == -math.huge or value % 1 ~= 0 then
		return false
	end
	return value >= (minimum or 0) and value <= (maximum or Validation.MAX_QUANTITY)
end

-- Operation, item and receipt IDs: non-empty, bounded, URL-safe characters only.
function Validation.IsId(value: any): boolean
	return type(value) == "string" and #value >= 1 and #value <= 64 and string.match(value, "^[%w%-_:]+$") ~= nil
end

return Validation
