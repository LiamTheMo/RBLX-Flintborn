-- A per-player request throttle: at most one accepted request every `interval()`
-- seconds of os.clock(). `interval` is a function so a service's tunable (and a
-- spec that changes it) is read on every request.

local Cooldown = {}
Cooldown.__index = Cooldown

function Cooldown.new(interval: () -> number)
	return setmetatable({ interval = interval, last = {} }, Cooldown)
end

-- True (and the request is recorded) when `player`'s last accepted request was at
-- least one interval ago; false while the cooldown runs.
function Cooldown:Try(player: Player): boolean
	local now = os.clock()
	local last = self.last[player]
	if last and now - last < self.interval() then
		return false
	end
	self.last[player] = now
	return true
end

function Cooldown:Forget(player: Player)
	self.last[player] = nil
end

return Cooldown
