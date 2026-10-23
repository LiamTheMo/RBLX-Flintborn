local Server = game:GetService("ServerScriptService").Server
local Shared = game:GetService("ReplicatedStorage").Shared
local DataStoreGateway = require(Server.Infrastructure.DataStoreGateway)
local InMemoryDataStore = require(Server.Infrastructure.InMemoryDataStore)
local OperationJournal = require(Server.Infrastructure.OperationJournal)
local ProfileStore = require(Server.Infrastructure.ProfileStore)
local ProfileSchema = require(Shared.Data.ProfileSchema)

local USER = 4242

local function setup()
	local backing = InMemoryDataStore.new()
	local sleeps = {}
	local gateway = DataStoreGateway.new({
		store = backing,
		sleep = function(seconds)
			table.insert(sleeps, seconds)
		end,
	})
	local now = 1000
	local function clock()
		return now
	end
	local function advance(seconds)
		now += seconds
	end
	local function server(jobId)
		return ProfileStore.new({ gateway = gateway, jobId = jobId, clock = clock })
	end
	return backing, sleeps, server, advance
end

test("load, change, save and reload keeps the data", function()
	local _, _, server = setup()
	local a = server("job-a")
	local profile = assert(a:Load(USER))
	expectEq(profile.profileRevision, 1, "first load bumps revision")
	profile.currency.coins = 250
	a:MarkDirty(USER)
	expectEq(a:Status(USER), "Pending", "dirty profile is pending")
	expect(a:Save(USER, true), "release save")
	expectEq(a:Status(USER), nil, "released profile is forgotten")

	local b = server("job-b")
	local again = assert(b:Load(USER))
	expectEq(again.currency.coins, 250, "coins persisted")
	expectEq(again.sessionLease.jobId, "job-b", "lease moved to the new server")
end)

test("a second server waits while the first holds the lease", function()
	local _, _, server, advance = setup()
	local a = server("job-a")
	assert(a:Load(USER))
	local b = server("job-b")
	local profile, reason = b:Load(USER)
	expectEq(profile, nil, "second server refused")
	expectEq(reason, "LeaseHeld", "because the lease is held")

	advance(301)
	profile = b:Load(USER)
	expect(profile ~= nil, "expired lease can be taken over")
end)

test("a server that lost its lease never writes again", function()
	local backing, _, server, advance = setup()
	local a = server("job-a")
	local profile = assert(a:Load(USER))
	advance(301)
	local b = server("job-b")
	local taken = assert(b:Load(USER))
	taken.currency.gems = 25
	b:MarkDirty(USER)
	assert(b:Save(USER))

	profile.currency.gems = 9999
	a:MarkDirty(USER)
	local ok, reason = a:Save(USER)
	expect(not ok, "stale server save rejected")
	expectEq(reason, "LeaseLost", "reason")
	expectEq(a:Status(USER), "LeaseLost", "status")
	expectEq(a:Get(USER), nil, "lost profile is no longer readable")
	local stored = backing:GetAsync(ProfileStore.KeyFor(USER))
	expectEq(stored.currency.gems, 25, "newer data kept")
end)

test("a write from an outdated revision is rejected", function()
	local backing, _, server = setup()
	local a = server("job-a")
	assert(a:Load(USER))
	-- Simulate a write this server did not make while it still appears to hold the lease.
	backing:UpdateAsync(ProfileStore.KeyFor(USER), function(old)
		old.profileRevision += 5
		return old
	end)
	local ok, reason = a:Save(USER)
	expect(not ok, "rejected")
	expectEq(reason, "StaleRevision", "stale revision")
end)

test("DataStore failures retry with backoff and never report success early", function()
	local backing, sleeps, server = setup()
	local a = server("job-a")
	assert(a:Load(USER))
	backing.failNext = 2
	expect(a:Save(USER), "succeeds after two failures")
	expectEq(#sleeps, 2, "two backoff waits")
	expectEq(sleeps[2], sleeps[1] * 2, "exponential backoff")

	a:MarkDirty(USER)
	backing.failNext = 99
	local ok, reason = a:Save(USER)
	expect(not ok, "gives up after max attempts")
	expect(string.find(reason, "DataStoreError") ~= nil, "reports the error")
	expectEq(a:Status(USER), "Pending", "still pending, never marked saved")
	backing.failNext = 0
	expect(a:Save(USER), "a later retry saves")
	expectEq(a:Status(USER), "Saved", "saved")
end)

test("a profile from a newer schema is not loaded or overwritten", function()
	local backing, _, server = setup()
	backing:UpdateAsync(ProfileStore.KeyFor(USER), function()
		return { schemaVersion = ProfileSchema.CURRENT_VERSION + 1, marker = true }
	end)
	local a = server("job-a")
	local profile, reason = a:Load(USER)
	expectEq(profile, nil, "refused")
	expect(reason ~= nil, "with a reason")
	expect(backing:GetAsync(ProfileStore.KeyFor(USER)).marker, "stored data untouched")
end)

test("operations apply exactly once and failures change nothing", function()
	local profile = ProfileSchema.Default(0)
	local function grant(amount)
		return function(working)
			working.currency.coins += amount
			return working.currency.coins
		end
	end
	local result, applied = OperationJournal.Run(profile, "quest:1", "QuestReward", 1, grant(250))
	expectEq(result, 250, "result")
	expect(applied, "applied")
	result, applied = OperationJournal.Run(profile, "quest:1", "QuestReward", 2, grant(250))
	expectEq(result, 250, "replay returns the stored result")
	expect(not applied, "replay not applied")
	expectEq(profile.currency.coins, 250, "granted once")
	expectEq(profile.lastCommittedOperationId, "quest:1", "last committed")

	local ok = pcall(OperationJournal.Run, profile, "buy:1", "Purchase", 3, function(working)
		working.currency.coins -= 100
		error("insufficient funds")
	end)
	expect(not ok, "failing operation raises")
	expectEq(profile.currency.coins, 250, "failed operation left the profile untouched")
	expectEq(OperationJournal.Get(profile, "buy:1"), nil, "failed operation not recorded")
end)

test("the journal keeps a bounded history", function()
	local profile = ProfileSchema.Default(0)
	for i = 1, OperationJournal.RETENTION + 25 do
		OperationJournal.Run(profile, "op:" .. i, "Test", i, function() end)
	end
	expectEq(#profile.operations.order, OperationJournal.RETENTION, "trimmed to retention")
	expectEq(OperationJournal.Get(profile, "op:1"), nil, "oldest trimmed")
	expect(OperationJournal.Get(profile, "op:" .. (OperationJournal.RETENTION + 25)) ~= nil, "newest kept")
end)

test("changes made during a save keep the profile pending", function()
	local backing, _, server = setup()
	local a = server("job-a")
	local profile = assert(a:Load(USER))
	local original = backing.UpdateAsync
	backing.UpdateAsync = function(self, key, transform)
		-- A gameplay change lands while the write is in flight.
		profile.currency.coins += 1
		a:MarkDirty(USER)
		return original(self, key, transform)
	end
	assert(a:Save(USER))
	backing.UpdateAsync = original
	expectEq(a:Status(USER), "Pending", "the in-flight change still needs saving")
end)
