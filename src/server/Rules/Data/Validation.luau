-- Server half of Shared.Data.Validation: what only the server uses. Everything in
-- ReplicatedStorage is downloaded to every player, so the shared module keeps
-- only what clients need; this one clones it and adds the rest, and server code
-- requires this module.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local SharedValidation = require(ReplicatedStorage.Shared.Data.Validation)

local Validation = table.clone(SharedValidation)

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

-- A client's operation nonce: an ID of at most 50 characters.
function Validation.IsNonce(value: any): boolean
	return Validation.IsId(value) and #value <= 50
end

-- A client aim: the unit vector of a real (not tiny, not NaN) Vector3, or nil.
function Validation.Direction(value: any): Vector3?
	if typeof(value) ~= "Vector3" or value.Magnitude < 0.5 or value.Magnitude ~= value.Magnitude then
		return nil
	end
	return value.Unit
end

return Validation
