-- In-memory stand-in for a DataStore with the same UpdateAsync/GetAsync shape.
-- Used by headless specs and by Studio sessions without API access; data is lost
-- when the server stops. `failNext` makes the next N calls error, to exercise
-- retry and pending-save paths.

local InMemoryDataStore = {}
InMemoryDataStore.__index = InMemoryDataStore

local function copy(value)
	if type(value) ~= "table" then
		return value
	end
	local result = {}
	for key, child in value do
		result[key] = copy(child)
	end
	return result
end

function InMemoryDataStore.new()
	return setmetatable({ _data = {}, failNext = 0, calls = 0 }, InMemoryDataStore)
end

function InMemoryDataStore:_maybeFail()
	self.calls += 1
	if self.failNext > 0 then
		self.failNext -= 1
		error("InMemoryDataStore: simulated failure")
	end
end

function InMemoryDataStore:UpdateAsync(key: string, transform: (any) -> any)
	self:_maybeFail()
	local new = transform(copy(self._data[key]))
	if new ~= nil then
		self._data[key] = copy(new)
	end
	return copy(new)
end

function InMemoryDataStore:GetAsync(key: string)
	self:_maybeFail()
	return copy(self._data[key])
end

return InMemoryDataStore
