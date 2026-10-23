-- Follow-up review of crash recovery and trade settlement: a new run racing an
-- unrecovered crash checkpoint, a restore racing a new run's checkpoint, a crash
-- between the Play's consume save and its first checkpoint, and spending while a
-- trade can still roll back. Drives the real server services against fake Roblox
-- services, a DataStore and a MemoryStore with latency and a fake clock.

local Shared = game:GetService("ReplicatedStorage").Shared
local Server = game:GetService("ServerScriptService").Server

-- Fake clock and task scheduler ---------------------------------------------------

local clock = 0
local queue = {}
local sequence = 0
local threadErrors = {}

local function resume(thread, ...)
	local ok, err = coroutine.resume(thread, ...)
	if not ok then
		table.insert(threadErrors, tostring(err))
	end
end

local function enqueue(at: number, thread, args)
	sequence += 1
	table.insert(queue, { at = at, sequence = sequence, thread = thread, args = args })
end

task = {}
function task.spawn(fn, ...)
	local thread = if type(fn) == "thread" then fn else coroutine.create(fn)
	resume(thread, ...)
	return thread
end
function task.defer(fn, ...)
	local thread = coroutine.create(fn)
	enqueue(clock, thread, table.pack(...))
	return thread
end
function task.delay(seconds, fn, ...)
	local thread = coroutine.create(fn)
	enqueue(clock + (seconds or 0), thread, table.pack(...))
	return thread
end
function task.wait(seconds)
	enqueue(clock + (seconds or 0), coroutine.running(), table.pack())
	coroutine.yield()
	return seconds
end

warn = function() end

-- Runs everything due within the next `seconds`, in time order.
local function advance(seconds: number)
	local target = clock + seconds
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
		clock = math.max(clock, entry.at)
		resume(entry.thread, table.unpack(entry.args, 1, entry.args.n))
	end
	clock = target
end

-- Fake Roblox services ------------------------------------------------------------

-- Roblox runs every connection of an engine event in its own thread.
local function engineSignal()
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
				task.spawn(fn, ...)
			end
		end,
	}
end

local function deepCopy(value)
	if type(value) ~= "table" then
		return value
	end
	local copy = {}
	for key, inner in value do
		copy[key] = deepCopy(inner)
	end
	return copy
end

local InMemoryDataStore = require(Server.Infrastructure.InMemoryDataStore)
local backing = InMemoryDataStore.new()
local LATENCY = 0.3
-- A DataStore whose writes take LATENCY seconds to land.
local slowStore = {
	UpdateAsync = function(_, key, transform)
		task.wait(LATENCY)
		return backing:UpdateAsync(key, transform)
	end,
	GetAsync = function(_, key)
		task.wait(LATENCY)
		return backing:GetAsync(key)
	end,
}

-- MemoryStore hash maps whose calls land after a per-call latency ("Map.Method").
local memory = { maps = {}, latency = {} }
local function hashMap(name: string)
	local data = {}
	memory.maps[name] = data
	local function pause(method: string)
		local seconds = memory.latency[name .. "." .. method]
		if seconds and seconds > 0 then
			task.wait(seconds)
		end
	end
	return {
		SetAsync = function(_, key, value)
			pause("SetAsync")
			data[key] = deepCopy(value)
			return true
		end,
		GetAsync = function(_, key)
			pause("GetAsync")
			return deepCopy(data[key])
		end,
		RemoveAsync = function(_, key)
			pause("RemoveAsync")
			data[key] = nil
		end,
		UpdateAsync = function(_, key, transform)
			pause("UpdateAsync")
			local value = transform(deepCopy(data[key]))
			if value ~= nil then
				data[key] = deepCopy(value)
			end
			return value
		end,
	}
end

local Players = {
	PlayerAdded = engineSignal(),
	PlayerRemoving = engineSignal(),
	CharacterAutoLoads = true,
	_list = {},
}
function Players.GetPlayers(self)
	return table.clone(self._list)
end
function Players.GetPlayerByUserId(self, userId)
	for _, player in self._list do
		if player.UserId == userId then
			return player
		end
	end
	return nil
end

local guids = 0
local fakes = {
	Players = Players,
	HttpService = {
		GenerateGUID = function()
			guids += 1
			return string.format("%08x-0000-4000-8000-%012x", guids, guids)
		end,
	},
	RunService = {
		Heartbeat = engineSignal(),
		IsStudio = function()
			return false
		end,
	},
	DataStoreService = {
		GetDataStore = function()
			return slowStore
		end,
		GetRequestBudgetForRequestType = function()
			return 100
		end,
	},
	TeleportService = { TeleportInitFailed = engineSignal() },
	MemoryStoreService = {
		GetHashMap = function(_, name)
			return hashMap(name)
		end,
	},
}
local originalGetService = game.GetService
game.GetService = function(self, name)
	return fakes[name] or originalGetService(self, name)
end
game.JobId = "job-followup"
game.PrivateServerId = "world-followup"
game.PlaceId = 1
game.BindToClose = function() end

local function newCharacter()
	local humanoid = { Health = 100, MaxHealth = 100, WalkSpeed = 16, JumpHeight = 7.2, Died = engineSignal() }
	local root = { Position = Vector3.new(0, 5, 0), Anchored = false }
	local character = {}
	function character.FindFirstChildOfClass(_, className)
		return if className == "Humanoid" then humanoid else nil
	end
	function character.FindFirstChild(_, name)
		return if name == "HumanoidRootPart" then root else nil
	end
	function character.PivotTo() end
	function character.GetPivot()
		return { Position = root.Position }
	end
	function character.Destroy() end
	return character
end

local function leave(player)
	local index = table.find(Players._list, player)
	if index then
		table.remove(Players._list, index)
		player.Parent = nil
		Players.PlayerRemoving:Fire(player)
	end
end

local function newPlayer(userId: number, reservationId: string?)
	local player = {
		UserId = userId,
		Name = "Player" .. userId,
		DisplayName = "Player" .. userId,
		Parent = Players,
		Character = nil,
		attributes = {},
	}
	function player.SetAttribute(self, key, value)
		self.attributes[key] = value
	end
	function player.GetAttribute(self, key)
		return self.attributes[key]
	end
	function player.GetJoinData()
		return { TeleportData = { reservations = { [tostring(userId)] = reservationId } } }
	end
	function player.Kick(self, message)
		self.kickMessage = message
		leave(self)
	end
	function player.LoadCharacter(self)
		self.Character = newCharacter()
	end
	return player
end

-- Real services, wired as the Loader would ----------------------------------------

local PlaceConfig = require(Shared.Config.PlaceConfig)
PlaceConfig.IsWorld = function()
	return true
end
PlaceConfig.IsLobby = function()
	return false
end
local Remotes = require(Shared.Net.Remotes)
local handlers = {}
local notices = {}
Remotes.Handle = function(name, fn)
	handlers[name] = fn
end
Remotes.Get = function(name)
	return {
		FireClient = function(_, player, payload)
			if name == "Notice" then
				table.insert(notices, { player = player, payload = payload })
			end
		end,
		FireAllClients = function() end,
	}
end

local CrashRecoveryRules = require(Shared.Recovery.CrashRecoveryRules)
local EconomyRules = require(Shared.Economy.EconomyRules)
local ForgeRules = require(Shared.Crafting.ForgeRules)
local ProfileSchema = require(Shared.Data.ProfileSchema)
local TradeRules = require(Shared.Economy.TradeRules)
local TransitRules = require(Shared.Admission.TransitRules)
local ProfileStore = require(Server.Infrastructure.ProfileStore)
local CheckpointStore = require(Server.Infrastructure.CheckpointStore)
local TravelService = require(Server.Services.TravelService)
TravelService.ToLobby = function(players)
	for _, player in players do
		player.sentToLobby = true
	end
	return true
end
local SpawnService = require(Server.Services.SpawnService)
SpawnService.Pick = function()
	return "spawn"
end

local CrashRecoveryService = require(Server.Services.CrashRecoveryService)
local InventoryService = require(Server.Services.InventoryService)
local LoadoutService = require(Server.Services.LoadoutService)
local ProfileService = require(Server.Services.ProfileService)
local RunCheckpointService = require(Server.Services.RunCheckpointService)
local WorldAdmissionService = require(Server.Services.WorldAdmissionService)

-- Periodic autosaves would only add noise to the timelines below.
ProfileService.AUTOSAVE_SECONDS = 1e9
ProfileService.Init()
WorldAdmissionService.Init()
for _, service in
	{
		CrashRecoveryService,
		InventoryService,
		LoadoutService,
		ProfileService,
		RunCheckpointService,
		WorldAdmissionService,
	}
do
	service.Start()
end

local started = {}
WorldAdmissionService.RunStarted:Connect(function(player, _, items)
	started[player] = items
end)

local checkpoints = memory.maps.FlintbornRunCheckpoints
local beats = memory.maps.FlintbornServerHeartbeats

-- Helpers -------------------------------------------------------------------------

local function stacks(prefix: string, count: number)
	local items = {}
	for index = 1, count do
		table.insert(items, { instanceId = ("%s-%d"):format(prefix, index), catalogId = "StoneSword", ownerId = 1 })
	end
	return items
end

local function stored(userId: number)
	return backing._data[ProfileStore.KeyFor(userId)]
end

-- Joins this world with `profile` stored for `userId` and waits on the menu.
local function join(userId: number, profile, reservationId: string?)
	backing._data[ProfileStore.KeyFor(userId)] = profile
	local player = newPlayer(userId, reservationId)
	table.insert(Players._list, player)
	Players.PlayerAdded:Fire(player)
	advance(2)
	assert(WorldAdmissionService.GetState(player) == "WorldMainMenuReady", "player reached the menu")
	return player
end

-- A profile arriving with a reserved loadout.
local function withTransit(userId: number, items)
	local profile = ProfileSchema.Default(0)
	local reservationId = ("res-%d"):format(userId)
	profile.transit = { reservationId = reservationId, items = items, createdAt = 0, status = "Reserved" }
	return profile, reservationId
end

-- A profile whose last run, on another server, was never settled.
local function crashedRun(profile, runId: string, jobId: string)
	profile.progression.currentRun = { runId = runId, general = 0, mastery = {}, settled = false, jobId = jobId }
	return profile
end

local function play(player, requestId: string)
	local result = {}
	task.spawn(function()
		result.ok, result.reason = handlers.RequestPlay(player, requestId)
	end)
	return result
end

local function hasInstance(slots, instanceId: string): number
	local count = 0
	for _, item in slots do
		if item.instanceId == instanceId then
			count += 1
		end
	end
	return count
end

-- Issue 1: a new run racing an unrecovered crash checkpoint ------------------------

test("a crashed run's checkpoint is never overwritten: Play waits until it is restored", function()
	local profile, reservationId = withTransit(301, stacks("new301", 2))
	crashedRun(profile, "run-301", "dead-301")
	checkpoints["301"] = CrashRecoveryRules.Checkpoint("run-301", "dead-301", stacks("old301", 3), {}, os.time())
	-- The crashed server's last heartbeat still counts as alive for a while.
	beats["dead-301"] = os.time()
	local player = join(301, profile, reservationId)

	local first = play(player, "req-301-a")
	advance(2)
	expectEq(first.ok, false, "no new run while the crashed run is unrecovered")
	expectEq(first.reason, "RecoveringItems", "the player is told why")
	expectEq(checkpoints["301"] and checkpoints["301"].runId, "run-301", "the crashed checkpoint is intact")

	-- The heartbeat expires: recovery restores the crashed run on its next check.
	beats["dead-301"] = nil
	advance(CrashRecoveryService.RETRY_SECONDS + 2)
	local slots = stored(301).lobbyBackpack.slots
	for index = 1, 3 do
		expectEq(hasInstance(slots, "old301-" .. index), 1, "crashed item " .. index .. " restored once")
	end
	expectEq(stored(301).receipts.crashRecovery["run-301"].status, "Restored", "the run is settled")

	local second = play(player, "req-301-b")
	advance(2)
	expectEq(second.ok, true, "the new run starts once the crashed one is settled")
	expectEq(started[player] and #started[player], 2, "with the new loadout")
	local ok, checkpoint = CheckpointStore.Read(301)
	expect(ok and checkpoint and checkpoint.runId ~= "run-301", "the new run has its own checkpoint")
	expectEq(#stored(301).lobbyBackpack.slots, 3, "and the restored items are not restored twice")
end)

test("a checkpoint whose server still beats is never restored; the wait ends once it is cleared", function()
	local profile = crashedRun(ProfileSchema.Default(0), "run-302", "live-302")
	checkpoints["302"] = CrashRecoveryRules.Checkpoint("run-302", "live-302", stacks("old302", 2), {}, os.time())
	beats["live-302"] = os.time()
	local player = join(302, profile)
	for _ = 1, 6 do
		beats["live-302"] = os.time()
		advance(CrashRecoveryService.RETRY_SECONDS)
	end
	expectEq(#stored(302).lobbyBackpack.slots, 0, "nothing restored while its server runs")
	local early = play(player, "req-302-a")
	advance(1)
	expectEq(early.reason, "RecoveringItems", "and no new run replaces it")

	-- That server ends the run itself (a body, an extraction) and clears its checkpoint.
	CheckpointStore.Clear(302, "run-302")
	advance(CrashRecoveryService.RETRY_SECONDS + 1)
	expectEq(#stored(302).lobbyBackpack.slots, 0, "nothing to restore without a checkpoint or loadout")
	local later = play(player, "req-302-b")
	advance(2)
	expectEq(later.ok, true, "the player can play again")
end)

-- Issue 2: deletes compare the run --------------------------------------------------

test("clearing a checkpoint only removes the run it names", function()
	CheckpointStore.Write(390, CrashRecoveryRules.Checkpoint("run-a", "job", {}, {}, 0))
	CheckpointStore.Clear(390, "run-b")
	local _, kept = CheckpointStore.Read(390)
	expectEq(kept and kept.runId, "run-a", "another run's clear leaves it")
	CheckpointStore.Clear(390, "run-a")
	local _, gone = CheckpointStore.Read(390)
	expectEq(gone, nil, "its own clear removes it")
end)

test("a restore whose delete lands late never deletes a run started meanwhile", function()
	local profile, reservationId = withTransit(303, stacks("new303", 2))
	crashedRun(profile, "run-303", "dead-303")
	checkpoints["303"] = CrashRecoveryRules.Checkpoint("run-303", "dead-303", stacks("old303", 1), {}, os.time())
	memory.latency["FlintbornRunCheckpoints.UpdateAsync"] = 5
	memory.latency["FlintbornRunCheckpoints.RemoveAsync"] = 5
	local player = join(303, profile, reservationId)
	local result = play(player, "req-303")
	advance(10)
	memory.latency["FlintbornRunCheckpoints.UpdateAsync"] = nil
	memory.latency["FlintbornRunCheckpoints.RemoveAsync"] = nil
	expectEq(result.ok, true, "the new run started once the crashed run was restored")
	expectEq(hasInstance(stored(303).lobbyBackpack.slots, "old303-1"), 1, "the crashed item is restored")
	local ok, checkpoint = CheckpointStore.Read(303)
	expect(ok and checkpoint ~= nil, "the new run's checkpoint survived the restore's delete")
	expect(checkpoint == nil or checkpoint.runId ~= "run-303", "and it is the new run's")
end)

-- Issue 3: a crash between the consume save and the first checkpoint --------------

-- The stored profile as a crashed server left it, joined again "elsewhere": specs
-- run one server, so the dead server's JobId is written into the run record.
local function rejoinAfterCrash(fromUserId: number, toUserId: number)
	local crashed = ProfileSchema.DeepCopy(stored(fromUserId))
	crashed.sessionLease = nil
	local run = crashed.progression.currentRun
	if run then
		run.jobId = "dead-" .. fromUserId
	end
	return join(toUserId, crashed)
end

test("a crash before the first checkpoint lands still restores the consumed loadout", function()
	local profile, reservationId = withTransit(401, stacks("i401", 3))
	local player = join(401, profile, reservationId)
	-- The first checkpoint write never lands before the server dies.
	memory.latency["FlintbornRunCheckpoints.SetAsync"] = 1e6
	play(player, "req-401")
	advance(1)
	memory.latency["FlintbornRunCheckpoints.SetAsync"] = nil
	expectEq(WorldAdmissionService.GetState(player), "ActiveRun", "the run started")
	expectEq(stored(401).transit, nil, "the consume is saved")
	expectEq(checkpoints["401"], nil, "but no checkpoint exists yet")

	rejoinAfterCrash(401, 402)
	advance(1)
	local slots = stored(402).lobbyBackpack.slots
	for index = 1, 3 do
		expectEq(hasInstance(slots, "i401-" .. index), 1, "loadout item " .. index .. " restored once")
	end
	expectEq(#notices > 0 and notices[#notices].payload.text ~= nil, true, "the player is told")
end)

test("the consume names the run its checkpoint uses, and the loadout goes once checkpointed", function()
	local profile, reservationId = withTransit(403, stacks("i403", 2))
	local player = join(403, profile, reservationId)
	play(player, "req-403")
	advance(5)
	local run = stored(403).progression.currentRun
	local _, checkpoint = CheckpointStore.Read(403)
	expect(run ~= nil and checkpoint ~= nil and run.runId == checkpoint.runId, "one run ID for both")
	expectEq(run and run.jobId, CheckpointStore.JobId(), "recorded with this server")
	expectEq(run and run.loadout, nil, "only the checkpoint recovers it now")
end)

test("a Play cancelled after its consume saved is settled, so recovery never doubles it", function()
	local profile, reservationId = withTransit(404, stacks("i404", 2))
	local player = join(404, profile, reservationId)
	local result = play(player, "req-404")
	task.delay(0.1, function()
		player.Character:FindFirstChildOfClass("Humanoid").Health = 0
	end)
	advance(10)
	expectEq(result.reason, "Cancelled", "the Play was cancelled during its save")
	rejoinAfterCrash(404, 405)
	advance(1)
	local again = stored(405)
	local total = #again.lobbyBackpack.slots + (if again.transit then #again.transit.items else 0)
	expectEq(total, 2, "each item exists exactly once")
end)

-- Issue 4: nothing a trade rollback cannot reclaim while it settles ---------------

local NOW = 200000

local function settling()
	local profile = ProfileSchema.Default(0)
	profile.progression.level = 12
	profile.currency.coins = 100
	profile.currency.gems = 1000
	profile.vault.materials.Iron = 50
	profile.vault.materials.Wood = 50
	profile.lobbyBackpack.slots = { { catalogId = "AncientEmber", quantity = 1 } }
	profile.trades.pending.t1 = {
		counterpart = 2,
		gave = { items = {}, gems = 0 },
		received = { items = { { catalogId = "AncientEmber", quantity = 1 } }, gems = 0 },
		at = NOW,
	}
	return profile
end

test("selling, forging, Gem spending and Deploy wait while a trade settles", function()
	local profile = settling()
	local ok, reason = EconomyRules.Sell(profile, "backpack", 1, nil, "sale:x", NOW)
	expectEq(ok, false, "no backpack sale")
	expectEq(reason, "TradeSettling", "with a clear reason")
	ok = EconomyRules.Sell(profile, "vault", "Iron", 5, "sale:y", NOW)
	expectEq(ok, false, "no vault sale")
	ok, reason = EconomyRules.BuyVaultTier(profile)
	expectEq(reason, "TradeSettling", "no Gem vault upgrade")
	ok, reason = EconomyRules.Spend(profile, 0, 250)
	expectEq(reason, "TradeSettling", "no Gem respec")
	expectEq(profile.currency.gems, 1000, "Gems untouched")
	expectEq(EconomyRules.Spend(profile, 10, 0), true, "Coins (never traded) still spend")
	local receipt, why = ForgeRules.Craft(profile, {
		recipeId = "ForgeIronPickaxe",
		ownerId = 1,
		operationId = "forge:x",
		now = NOW,
		newId = function()
			return "forged"
		end,
	})
	expectEq(receipt, nil, "no Forge craft")
	expectEq(why, "TradeSettling", "with a clear reason")
	expectEq(profile.vault.materials.Iron, 50, "inputs untouched")
	local reserved, err = pcall(TransitRules.Reserve, profile, "res-x", NOW)
	expect(not reserved and tostring(err):find("TradeSettling") ~= nil, "no Deploy reservation")
	expectEq(#profile.lobbyBackpack.slots, 1, "the received item stays reclaimable")
end)

test("the wait always ends: a counterpart that never saves rolls the trade back", function()
	local a, b = ProfileSchema.Default(0), ProfileSchema.Default(0)
	a.lobbyBackpack.slots = { { instanceId = "s1", catalogId = "StoneSword", ownerId = 1 } }
	b.lobbyBackpack.slots = { { catalogId = "AncientEmber", quantity = 3 } }
	local bStored = ProfileSchema.DeepCopy(b)
	TradeRules.Settle("t1", { profile = a, userId = 1, offer = { items = { 1 } } }, {
		profile = b,
		userId = 2,
		offer = { items = { 1 } },
	}, NOW)
	a.trades.pending.t1.server = "S"
	bStored.sessionLease = { jobId = "S", expiresAt = NOW + 300 }
	expectEq(TradeRules.Reconcile(a, "t1", bStored, NOW + 10), "Deferred", "B may still save on S")
	expectEq((EconomyRules.Sell(a, "backpack", 1, nil, "sale:a", NOW + 10)), false, "A's received Ember is held")
	expectEq(TradeRules.Reconcile(a, "t1", bStored, NOW + 400), "RolledBack", "B's lease expired unsaved")
	expectEq(next(a.trades.pending), nil, "nothing pending any more")
	expectEq(hasInstance(a.lobbyBackpack.slots, "s1"), 1, "A has the sword back")
	expectEq((EconomyRules.Sell(a, "backpack", 1, nil, "sale:b", NOW + 400)), true, "and may sell again")
end)

test("a Deploy reservation is refused while a trade settles", function()
	local profile = settling()
	local player = join(501, profile)
	local result = {}
	task.spawn(function()
		result.id, result.reason = LoadoutService.Reserve(player)
	end)
	advance(2)
	expectEq(result.id, nil, "nothing reserved")
	expectEq(result.reason, "TradeSettling", "with a clear reason")
	expectEq(stored(501).transit, nil, "no transit stored")
	expectEq(#stored(501).lobbyBackpack.slots, 1, "the backpack is untouched")
end)

test("no spawned thread errored", function()
	for _, err in threadErrors do
		print("    thread error: " .. err)
	end
	expectEq(#threadErrors, 0, "thread errors")
end)
