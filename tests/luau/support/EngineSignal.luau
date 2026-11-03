--!nocheck
-- A stand-in for an engine event (Players.PlayerAdded, Heartbeat, Humanoid.Died):
-- Connect returns a connection whose Disconnect removes the handler, and Fire
-- runs the handlers connected at the time. With `threaded`, each handler runs in
-- its own thread through `task.spawn`, as the engine runs them (install a
-- Scheduler first); otherwise they run in order on the firing thread.
--
--     local EngineSignal = require(game:GetService("ServerStorage").TestSupport.EngineSignal)
--     local Players = { PlayerAdded = EngineSignal.new() }

local EngineSignal = {}

function EngineSignal.new(threaded: boolean?)
	local handlers = {}
	return {
		Connect = function(_, fn)
			table.insert(handlers, fn)
			return {
				Disconnect = function()
					local index = table.find(handlers, fn)
					if index then
						table.remove(handlers, index)
					end
				end,
			}
		end,
		Fire = function(_, ...)
			for _, fn in table.clone(handlers) do
				if threaded then
					task.spawn(fn, ...)
				else
					fn(...)
				end
			end
		end,
	}
end

return EngineSignal
