-- Run lifecycle and persistence hardening: inventory conservation, run-start
-- overflow, crash-recovery receipts, signal isolation, downed/death edge cases,
-- extraction qualification and release saves that race a change.
local Server = game:GetService("ServerScriptService").Server
local Shared = game:GetService("ReplicatedStorage").Shared
local CrashRecoveryRules = require(Shared.Recovery.CrashRecoveryRules)
local DataStoreGateway = require(Server.Infrastructure.DataStoreGateway)
local DeathRules = require(Shared.Admission.DeathRules)
local DownedRules = require(Shared.Combat.DownedRules)
local ExtractionRules = require(Shared.Extraction.ExtractionRules)
local GameConstants = require(Shared.GameConstants)
local InMemoryDataStore = require(Server.Infrastructure.InMemoryDataStore)
local InventoryRules = require(Shared.Inventory.InventoryRules)
local OperationJournal = require(Server.Infrastructure.OperationJournal)
local ProfileSchema = require(Shared.Data.ProfileSchema)
local ProfileStore = require(Server.Infrastructure.ProfileStore)
local Signal = require(Shared.Core.Signal)

local NOW = 200000
local NAN = 0 / 0

-- Inventory conservation ---------------------------------------------------------

-- A multiset signature: unique instance IDs plus total quantity per stack type.
local function signature(items)
	local result = {}
	for _, item in items do
		local key = item.instanceId and ("#" .. item.instanceId) or item.catalogId
		result[key] = (result[key] or 0) + (if item.instanceId then 1 else item.quantity or 1)
	end
	return result
end

local function sameSignature(a, b): boolean
	for key, count in a do
		if b[key] ~= count then
			return false
		end
	end
	for key in b do
		if a[key] == nil then
			return false
		end
	end
	return true
end

local function wellFormed(inventory): boolean
	for _, area in { "hotbar", "backpack" } do
		for index in inventory[area] do
			if type(index) ~= "number" or index % 1 ~= 0 or index < 1 or index > InventoryRules.Size(area) then
				return false
			end
		end
	end
	for slot, item in inventory.armor do
		if not table.find(InventoryRules.ArmorSlots, slot) then
			return false
		end
		if item.catalogId ~= ("Iron" .. slot) and item.catalogId ~= ("Hide" .. slot) then
			return false
		end
	end
	return true
end

local function starterItems()
	local items = {
		{ catalogId = "Wood", quantity = 300 },
		{ catalogId = "FlintArrow", quantity = 40 },
		{ catalogId = "Stone", quantity = 12 },
	}
	for index, catalogId in { "IronHead", "IronChest", "IronLegs", "HideHead", "HideChest", "HideLegs" } do
		table.insert(items, { instanceId = "armor" .. index, catalogId = catalogId, qualityRoll = index / 100 })
	end
	for index = 1, 20 do
		table.insert(items, { instanceId = "tool" .. index, catalogId = "StoneAxe", permanent = index % 3 == 0 })
	end
	return items
end

test("moves, armor swaps and takes never create or destroy items, even with bad indexes", function()
	local inventory, leftovers = InventoryRules.FromItems(starterItems())
	expectEq(#leftovers, 0, "everything fits")
	local before = signature(InventoryRules.Items(inventory))
	local rng = Random.new(7)
	local areas = { "hotbar", "backpack", "armor", "bogus" }
	local bad = { NAN, 0, -1, 1.5, 10, 51, math.huge, -math.huge }
	local function index()
		if rng:NextInteger(1, 4) == 1 then
			return bad[rng:NextInteger(1, #bad)]
		end
		return rng:NextInteger(1, 50)
	end
	for _ = 1, 3000 do
		local op = rng:NextInteger(1, 4)
		local area = areas[rng:NextInteger(1, #areas)]
		if op == 1 then
			InventoryRules.Move(inventory, area, index(), areas[rng:NextInteger(1, #areas)], index())
		elseif op == 2 then
			InventoryRules.EquipArmor(inventory, area, index())
		elseif op == 3 then
			local slots = { "Head", "Chest", "Legs", "Bogus" }
			InventoryRules.UnequipArmor(inventory, slots[rng:NextInteger(1, #slots)])
		else
			local taken = InventoryRules.TakeAt(inventory, area, index())
			if taken then
				expectEq(InventoryRules.Add(inventory, taken), 0, "a taken item fits back")
			end
		end
	end
	expect(sameSignature(before, signature(InventoryRules.Items(inventory))), "same items before and after")
	expect(wellFormed(inventory), "no item sits at an invalid slot")
end)

test("invalid slot indexes are refused outright", function()
	local inventory = InventoryRules.FromItems(starterItems())
	for _, bad in { NAN, 0, -1, 1.5, 10, math.huge } do
		expect(not InventoryRules.Move(inventory, "hotbar", bad, "backpack", 1), "move from " .. tostring(bad))
		expect(not InventoryRules.Move(inventory, "hotbar", 1, "hotbar", bad), "move to " .. tostring(bad))
		expect(not InventoryRules.EquipArmor(inventory, "hotbar", bad), "equip " .. tostring(bad))
		expectEq(InventoryRules.TakeAt(inventory, "hotbar", bad), nil, "take " .. tostring(bad))
	end
	expect(not InventoryRules.Move(inventory, "armor", 1, "hotbar", 1), "armor is not a movable area")
	expect(not InventoryRules.UnequipArmor(inventory, "Bogus"), "unknown armor slot")
end)

test("a run start never drops items that do not fit (> 59 entries, over-cap stacks, armor)", function()
	local items = {}
	for index = 1, 70 do
		table.insert(items, {
			instanceId = "i" .. index,
			catalogId = if index % 2 == 0 then "IronChest" else "StoneSword",
			qualityRoll = index / 1000,
			permanent = index == 70,
			ownerId = 5,
		})
	end
	table.insert(items, { catalogId = "Wood", quantity = 2500 })
	table.insert(items, { catalogId = "Wood", quantity = 700 })
	table.insert(items, { catalogId = "Redberry", quantity = 80 })
	table.insert(items, { catalogId = "MysteryRelic" }) -- unknown, non-stackable
	local inventory, leftovers = InventoryRules.FromItems(items)

	local placed = InventoryRules.Items(inventory)
	expectEq(#placed, GameConstants.HOTBAR_SLOTS + GameConstants.BACKPACK_SLOTS, "every slot is used")
	local combined = table.clone(placed)
	for _, item in leftovers do
		table.insert(combined, item)
	end
	expect(sameSignature(signature(items), signature(combined)), "placed + leftovers == what entered")
	local permanentKept = false
	for _, item in leftovers do
		if item.instanceId == "i70" then
			permanentKept = item.permanent == true and item.qualityRoll == 0.07 and item.ownerId == 5
		end
		if item.catalogId == "MysteryRelic" then
			expectEq(item.quantity, nil, "a unique record is returned as it was")
		end
	end
	expect(permanentKept, "a Permanent leftover keeps its full record")
end)

test("over-cap stacks split into a full slot and a leftover", function()
	local inventory, leftovers = InventoryRules.FromItems({
		{ catalogId = "Wood", quantity = 800 },
		{ catalogId = "Wood", quantity = 700 },
	})
	expectEq(InventoryRules.Count(inventory, "Wood"), 1000, "one slot at the cap")
	expectEq(#leftovers, 1, "one leftover")
	expectEq(leftovers[1].quantity, 500, "the rest is returned")
end)

-- Crash recovery receipts --------------------------------------------------------

local function runProfile(runId: string)
	local profile = ProfileSchema.Default(0)
	profile.progression.currentRun = { runId = runId, general = 0, mastery = {}, settled = false }
	return profile
end

local function carried()
	return {
		{ instanceId = "s1", catalogId = "IronSword", ownerId = 1 },
		{ catalogId = "IronOre", quantity = 30 },
	}
end

test("a run that ended normally is never restored, even if its checkpoint survived", function()
	for _, ending in { "Extraction", "Death", "Maintenance" } do
		local profile = runProfile("run-" .. ending)
		OperationJournal.Run(profile, "end:" .. ending, ending, NOW, function(working)
			if ending == "Extraction" then
				ExtractionRules.Settle(working, carried(), "Fixed", "extract:x", NOW)
			end
			CrashRecoveryRules.MarkEnded(working, NOW)
		end)
		local before = #profile.lobbyBackpack.slots
		local checkpoint = CrashRecoveryRules.Checkpoint("run-" .. ending, "dead-job", carried(), {}, NOW)
		expectEq(CrashRecoveryRules.Restore(profile, checkpoint, NOW + 5), nil, ending .. " run refused")
		expectEq(#profile.lobbyBackpack.slots, before, ending .. ": nothing duplicated")
		expect(CrashRecoveryRules.IsSettled(profile, "run-" .. ending), ending .. " is settled")
	end
end)

test("MarkEnded never replaces a receipt and needs a tracked run", function()
	local profile = runProfile("r1")
	local checkpoint = CrashRecoveryRules.Checkpoint("r1", "job", carried(), {}, NOW)
	local receipt = CrashRecoveryRules.Restore(profile, checkpoint, NOW)
	expectEq(receipt.status, "Restored", "restored")
	expectEq(CrashRecoveryRules.MarkEnded(profile, NOW + 1), "r1", "returns the run ID")
	expectEq(profile.receipts.crashRecovery.r1.status, "Restored", "the restore receipt stays")
	expectEq(CrashRecoveryRules.MarkEnded(ProfileSchema.Default(0), NOW), nil, "no run, no receipt")
end)

test("the heartbeat boundary sits exactly at STALE_SECONDS", function()
	local checkpoint = CrashRecoveryRules.Checkpoint("r", "job", carried(), {}, NOW)
	local stale = CrashRecoveryRules.STALE_SECONDS
	expectEq(CrashRecoveryRules.Classify(checkpoint, NOW - stale + 1, NOW), "ServerAlive", "one second inside")
	expectEq(CrashRecoveryRules.Classify(checkpoint, NOW - stale, NOW), "Eligible", "exactly stale")
	expectEq(CrashRecoveryRules.Classify(checkpoint, NOW, NOW), "ServerAlive", "beat this second")
end)

test("old crash receipts are pruned, recent ones kept", function()
	local profile = runProfile("new")
	profile.receipts.crashRecovery.ancient = { status = "Ended", at = NOW - CrashRecoveryRules.RECEIPT_SECONDS - 1 }
	profile.receipts.crashRecovery.recent = { status = "Ended", at = NOW - 60 }
	CrashRecoveryRules.MarkEnded(profile, NOW)
	expectEq(profile.receipts.crashRecovery.ancient, nil, "pruned")
	expect(profile.receipts.crashRecovery.recent ~= nil, "kept")
	expect(profile.receipts.crashRecovery.new ~= nil, "written")
end)

-- Signal ---------------------------------------------------------------------------

test("one failing signal handler never stops the others", function()
	local signal = Signal.new()
	local seen = {}
	signal:Connect(function()
		error("boom")
	end)
	signal:Connect(function(a, b)
		table.insert(seen, a + b)
	end)
	local ok = pcall(function()
		signal:Fire(2, 3)
	end)
	expect(ok, "Fire itself does not throw")
	expectEq(seen[1], 5, "the second handler ran with the arguments")
end)

test("handlers disconnected mid-fire are skipped; destroy clears all", function()
	local signal = Signal.new()
	local calls = 0
	local second
	signal:Connect(function()
		calls += 1
		second:Disconnect()
	end)
	second = signal:Connect(function()
		calls += 100
	end)
	signal:Fire()
	expectEq(calls, 1, "disconnected during the fire")
	signal:Destroy()
	signal:Fire()
	expectEq(calls, 1, "nothing after destroy")
end)

-- Downed and death -------------------------------------------------------------------

test("a revive hold released within the tolerance completes; earlier resets", function()
	local state = DownedRules.New()
	DownedRules.StartRevive(state, 9)
	for _ = 1, 96 do
		DownedRules.Step(state, 0.1)
	end
	expectEq(DownedRules.EndHold(state, 4), nil, "someone else's release changes nothing")
	expectNear(state.reviveProgress, 9.6, 1e-6, "progress intact")
	expectEq(DownedRules.EndHold(state, 9), "Revived", "9.6 s counts as 10 s")

	local early = DownedRules.New()
	DownedRules.StartRevive(early, 9)
	for _ = 1, 94 do
		DownedRules.Step(early, 0.1)
	end
	expectEq(DownedRules.EndHold(early, 9), nil, "9.4 s is too early")
	expectEq(early.reviverId, nil, "revive stopped")
	expectEq(early.reviveProgress, 0, "progress restarts")
end)

test("downed edge cases: same reviver may restart, bleed-out exactly at 60 s, huge damage kills", function()
	local state = DownedRules.New()
	expect(DownedRules.StartRevive(state, 1), "start")
	expect(DownedRules.StartRevive(state, 1), "same reviver again")
	expect(not DownedRules.StartRevive(state, 2), "second reviver refused")
	DownedRules.StopRevive(state, 2)
	expectEq(state.reviverId, 1, "a stranger's stop changes nothing")
	DownedRules.StopRevive(state, nil)
	expectEq(state.reviverId, nil, "a forced stop clears")

	local outcome = nil
	local seconds = 0
	while outcome == nil and seconds < 100 do
		outcome = DownedRules.Step(state, 1)
		seconds += 1
	end
	expectEq(outcome, "BledOut", "bleeds out")
	expectEq(seconds, GameConstants.BLEED_OUT_SECONDS, "at exactly 60 s")

	local hurt = DownedRules.New()
	expect(not DownedRules.Damage(hurt, 1, 0), "no damage, no death")
	expect(DownedRules.Damage(hurt, 1, 10000), "overwhelming damage finishes")
end)

test("taking from a body shifts later entries and ignores invalid indexes", function()
	local contents = { { catalogId = "A" }, { catalogId = "B" }, { catalogId = "C" } }
	for _, bad in { 0, -1, 1.5, NAN, 4, math.huge, "1" } do
		expectEq(DeathRules.Take(contents, bad :: any), nil, "invalid " .. tostring(bad))
	end
	expectEq(#contents, 3, "nothing removed by invalid takes")
	expectEq(DeathRules.Take(contents, 2).catalogId, "B", "takes B")
	expectEq(contents[2].catalogId, "C", "C shifted into slot 2")
	expectEq(DeathRules.Take(contents, 3), nil, "old last index is gone")
	expectEq(#contents, 2, "two left")
end)

-- Extraction qualification ----------------------------------------------------------

test("only a living, standing, at-risk player in the zone qualifies (all 16 cases)", function()
	local qualified = 0
	for mask = 0, 15 do
		local candidate = {
			alive = bit32.band(mask, 1) ~= 0,
			downed = bit32.band(mask, 2) ~= 0,
			atRisk = bit32.band(mask, 4) ~= 0,
			inZone = bit32.band(mask, 8) ~= 0,
		}
		local expected = candidate.alive and not candidate.downed and candidate.atRisk and candidate.inZone
		local actual = ExtractionRules.Qualifies(candidate)
		expectEq(actual == true, expected, "case " .. mask)
		if actual then
			qualified += 1
		end
	end
	expectEq(qualified, 1, "exactly one combination qualifies")
end)

test("zone boundaries are inclusive and vertical reach is radius + 10", function()
	local center = Vector3.new(0, 0, 0)
	expect(ExtractionRules.InZone(Vector3.new(10, 0, 0), center, 10), "on the edge")
	expect(ExtractionRules.InZone(Vector3.new(6, 0, 8), center, 10), "diagonal edge")
	expect(not ExtractionRules.InZone(Vector3.new(10.01, 0, 0), center, 10), "just outside")
	expect(ExtractionRules.InZone(Vector3.new(0, 20, 0), center, 10), "top of the reach")
	expect(ExtractionRules.InZone(Vector3.new(0, -20, 0), center, 10), "bottom of the reach")
	expect(not ExtractionRules.InZone(Vector3.new(0, 20.01, 0), center, 10), "above the reach")
end)

-- Release saves that race a change ----------------------------------------------------

local USER = 77

local function hookedStore()
	local backing = InMemoryDataStore.new()
	local hooks = {}
	local store = {
		UpdateAsync = function(_, key, transform)
			local hook = table.remove(hooks, 1)
			if hook then
				hook()
			end
			return backing:UpdateAsync(key, transform)
		end,
		GetAsync = function(_, key)
			return backing:GetAsync(key)
		end,
	}
	local gateway = DataStoreGateway.new({ store = store, sleep = function() end })
	local function server(jobId)
		return ProfileStore.new({
			gateway = gateway,
			jobId = jobId,
			clock = function()
				return NOW
			end,
		})
	end
	return backing, hooks, server
end

test("a change made while the release is being written is saved, not forgotten", function()
	local _, hooks, server = hookedStore()
	local a = server("job-a")
	local profile = assert(a:Load(USER))
	table.insert(hooks, function()
		-- e.g. a departure keeping a Permanent item, committed mid-write.
		profile.currency.coins = 77
		a:MarkDirty(USER)
	end)
	expect(a:Save(USER, true), "release succeeds")
	expectEq(a:Status(USER), nil, "forgotten only after the re-save")
	local again = assert(server("job-b"):Load(USER))
	expectEq(again.currency.coins, 77, "the late change persisted")
end)

test("the follow-up write never clobbers a server that loaded after the release", function()
	local backing, hooks, server = hookedStore()
	local a = server("job-a")
	local b = server("job-b")
	local profile = assert(a:Load(USER))
	table.insert(hooks, function()
		profile.currency.coins = 5
		a:MarkDirty(USER)
	end)
	table.insert(hooks, function()
		assert(b:Load(USER))
	end)
	local ok, reason = a:Save(USER, true)
	expect(not ok, "the follow-up write is refused")
	expect(reason == "LeaseLost" or reason == "StaleRevision", "another server owns it now: " .. tostring(reason))
	expectEq(backing._data[ProfileStore.KeyFor(USER)].sessionLease.jobId, "job-b", "job-b keeps it")
end)

test("a release whose follow-up write failed can still be saved when the player rejoins", function()
	local backing, hooks, server = hookedStore()
	local a = server("job-a")
	local profile = assert(a:Load(USER))
	table.insert(hooks, function()
		profile.currency.coins = 9
		a:MarkDirty(USER)
		backing.failNext = DataStoreGateway.MAX_ATTEMPTS
	end)
	expect(not a:Save(USER, true), "the follow-up write failed")
	expectEq(a:Status(USER), "Pending", "the change is still pending here")
	expect(a:Save(USER, false), "saved again for the rejoined player")
	expectEq(backing._data[ProfileStore.KeyFor(USER)].currency.coins, 9, "persisted")
	local _, held = server("job-b"):Load(USER)
	expectEq(held, "LeaseHeld", "and this server holds the lease again")
end)
