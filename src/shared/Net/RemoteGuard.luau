-- Shared protection for every client request (GDD §24, §21.4). Each player gets a
-- token bucket per remote (20 calls/s, burst 40), and arguments must be plain,
-- bounded data: finite numbers, short strings, booleans, finite Vector3s and small
-- shallow tables. Anything else is dropped before a handler sees it.

local RemoteGuard = {}

RemoteGuard.RATE = 20
RemoteGuard.BURST = 40
RemoteGuard.MAX_ARGS = 8
RemoteGuard.MAX_STRING = 256
RemoteGuard.MAX_TABLE = 64
RemoteGuard.MAX_DEPTH = 2

function RemoteGuard.NewBucket(now: number)
	return { tokens = RemoteGuard.BURST, at = now }
end

-- Refills by elapsed time and spends one token. False when over the limit.
function RemoteGuard.Take(bucket, now: number): boolean
	bucket.tokens = math.min(RemoteGuard.BURST, bucket.tokens + (now - bucket.at) * RemoteGuard.RATE)
	bucket.at = now
	if bucket.tokens < 1 then
		return false
	end
	bucket.tokens -= 1
	return true
end

local function finite(value: number): boolean
	return value == value and value ~= math.huge and value ~= -math.huge
end

-- True for plain, bounded data.
function RemoteGuard.Sane(value: any, depth: number?): boolean
	local kind = typeof(value)
	if kind == "nil" or kind == "boolean" then
		return true
	elseif kind == "number" then
		return finite(value)
	elseif kind == "string" then
		return #value <= RemoteGuard.MAX_STRING
	elseif kind == "Vector3" then
		return finite(value.X) and finite(value.Y) and finite(value.Z)
	elseif kind == "table" then
		depth = (depth or 0) + 1
		if depth > RemoteGuard.MAX_DEPTH or getmetatable(value) ~= nil then
			return false
		end
		local count = 0
		for key, child in value do
			count += 1
			local keyKind = type(key)
			if count > RemoteGuard.MAX_TABLE or (keyKind ~= "string" and keyKind ~= "number") then
				return false
			end
			if not RemoteGuard.Sane(key, depth) or not RemoteGuard.Sane(child, depth) then
				return false
			end
		end
		return true
	end
	-- Instances, functions and other userdata are never accepted from clients.
	return false
end

function RemoteGuard.Check(args): boolean
	if args.n > RemoteGuard.MAX_ARGS then
		return false
	end
	for index = 1, args.n do
		if not RemoteGuard.Sane(args[index]) then
			return false
		end
	end
	return true
end

return RemoteGuard
