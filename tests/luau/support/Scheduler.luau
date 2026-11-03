--!nocheck
-- A fake clock and task scheduler for specs that drive the real server services.
-- Install() puts a `task` library (spawn, defer, delay, wait) that runs on this
-- clock in place of the global one and silences `warn`; Advance(seconds) moves the
-- clock and runs everything due by then in time order (ties in the order they
-- were scheduled). An error in a scheduled thread is collected in `threadErrors`
-- instead of stopping the spec; ExpectNoThreadErrors() fails a case on any.
--
--     local scheduler = require(game:GetService("ServerStorage").TestSupport.Scheduler).new():Install()
--     scheduler:InstallServerTime() -- workspace:GetServerTimeNow() follows the clock
--     scheduler:Advance(5)

local Scheduler = {}
Scheduler.__index = Scheduler

function Scheduler.new(start: number?)
	return setmetatable({ clock = start or 0, queue = {}, sequence = 0, threadErrors = {} }, Scheduler)
end

function Scheduler:Resume(thread, ...)
	local ok, err = coroutine.resume(thread, ...)
	if not ok then
		table.insert(self.threadErrors, tostring(err))
	end
end

function Scheduler:Enqueue(at: number, thread, args)
	self.sequence += 1
	table.insert(self.queue, { at = at, sequence = self.sequence, thread = thread, args = args })
end

-- Replaces the global `task` library with this scheduler's and silences `warn`.
-- Returns the scheduler.
function Scheduler:Install()
	local scheduler = self
	task = {}
	function task.spawn(fn, ...)
		local thread = if type(fn) == "thread" then fn else coroutine.create(fn)
		scheduler:Resume(thread, ...)
		return thread
	end
	function task.defer(fn, ...)
		local thread = coroutine.create(fn)
		scheduler:Enqueue(scheduler.clock, thread, table.pack(...))
		return thread
	end
	function task.delay(seconds, fn, ...)
		local thread = coroutine.create(fn)
		scheduler:Enqueue(scheduler.clock + (seconds or 0), thread, table.pack(...))
		return thread
	end
	function task.wait(seconds)
		scheduler:Enqueue(scheduler.clock + (seconds or 0), coroutine.running(), table.pack())
		coroutine.yield()
		return seconds
	end
	warn = function() end
	return self
end

-- Makes workspace:GetServerTimeNow() read this clock (creating `workspace` when a
-- spec has none). Returns the scheduler.
function Scheduler:InstallServerTime()
	workspace = workspace or {}
	workspace.GetServerTimeNow = function()
		return self.clock
	end
	return self
end

-- Runs everything due within the next `seconds`, in time order.
function Scheduler:Advance(seconds: number)
	local target = self.clock + seconds
	local queue = self.queue
	while true do
		local best = nil
		for index, entry in queue do
			if entry.at <= target then
				local current = best and queue[best]
				if
					current == nil
					or entry.at < current.at
					or (entry.at == current.at and entry.sequence < current.sequence)
				then
					best = index
				end
			end
		end
		if best == nil then
			break
		end
		local entry = table.remove(queue, best)
		self.clock = math.max(self.clock, entry.at)
		self:Resume(entry.thread, table.unpack(entry.args, 1, entry.args.n))
	end
	self.clock = target
end

-- Fails the running spec case, printing each, when a scheduled thread raised.
function Scheduler:ExpectNoThreadErrors()
	for _, err in self.threadErrors do
		print("    thread error: " .. err)
	end
	expectEq(#self.threadErrors, 0, "thread errors")
end

return Scheduler
