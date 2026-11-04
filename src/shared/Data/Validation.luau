-- Shared guards for values that reach persistent state. The server applies these to
-- every quantity and ID; a client request is never trusted to be well-formed.

local Validation = {}

-- True for a number that is neither NaN nor infinite.
function Validation.IsFinite(value: any): boolean
	return type(value) == "number" and value == value and value ~= math.huge and value ~= -math.huge
end

return Validation
