-- Minimal in-process signal for decoupling modules on the same side of the
-- client/server boundary. Not for replication -- use RemoteEvents for that.

local Signal = {}
Signal.__index = Signal

function Signal.new()
	return setmetatable({ _connections = {} }, Signal)
end

function Signal.Connect(signal, fn: (...any) -> ())
	local connection = { _fn = fn, _signal = signal, Connected = true }

	function connection.Disconnect(conn)
		conn.Connected = false
		local connections = conn._signal._connections
		local index = table.find(connections, conn)
		if index then
			table.remove(connections, index)
		end
	end

	table.insert(signal._connections, connection)
	return connection
end

function Signal:Fire(...: any)
	for _, connection in ipairs(table.clone(self._connections)) do
		if connection.Connected then
			connection._fn(...)
		end
	end
end

function Signal:Destroy()
	table.clear(self._connections)
end

return Signal
