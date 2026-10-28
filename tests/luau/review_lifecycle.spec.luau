-- Run lifecycle review: a shutdown racing a Play, a Play whose save fails, a safe
-- kick whose save fails, a redirected arrival whose teleport fails, and the crash
-- windows right after a Play. Drives the real server services against fake Roblox
-- services, a DataStore with latency and a fake clock.

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
		GetHashMap = function()
			error("MemoryStore unavailable in specs")
		end,
	},
}
local closeHandlers = {}
local originalGetService = game.GetService
game.GetService = function(self, name)
	return fakes[name] or originalGetService(self, name)
end
game.JobId = "job-review"
game.PrivateServerId = "world-review"
game.PlaceId = 1
game.BindToClose = function(_, fn)
	table.insert(closeHandlers, fn)
end

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
		loadDelay = 0,
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
		if self.loadDelay > 0 then
			task.wait(self.loadDelay)
		end
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
local silentRemote = {
	FireClient = function() end,
	FireAllClients = function() end,
}
Remotes.Handle = function(name, fn)
	handlers[name] = fn
end
Remotes.Get = function()
	return silentRemote
end

local ProfileSchema = require(Shared.Data.ProfileSchema)
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

local AdminService = require(Server.Services.AdminService)
local InventoryService = require(Server.Services.InventoryService)
local LoadoutService = require(Server.Services.LoadoutService)
local MaintenanceService = require(Server.Services.MaintenanceService)
local ProfileService = require(Server.Services.ProfileService)
local RunCheckpointService = require(Server.Services.RunCheckpointService)
local WorldAdmissionService = require(Server.Services.WorldAdmissionService)

-- Periodic autosaves would only add noise to the timelines below.
ProfileService.AUTOSAVE_SECONDS = 1e9
ProfileService.Init()
WorldAdmissionService.Init()
for _, service in
	{
		InventoryService,
		LoadoutService,
		MaintenanceService,
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

-- Helpers -------------------------------------------------------------------------

local function seedTransit(userId: number, reservationId: string, items)
	local profile = ProfileSchema.Default(0)
	profile.transit = { reservationId = reservationId, items = items, createdAt = 0, status = "Reserved" }
	backing._data[ProfileStore.KeyFor(userId)] = profile
end

local function stacks(count: number)
	local items = {}
	for index = 1, count do
		table.insert(items, { instanceId = ("item-%d"):format(index), catalogId = "StoneSword", ownerId = 1 })
	end
	return items
end

-- Joins a world with a reserved loadout and waits on the menu.
local function arrive(userId: number, items)
	local reservationId = ("res-%d"):format(userId)
	seedTransit(userId, reservationId, items)
	local player = newPlayer(userId, reservationId)
	table.insert(Players._list, player)
	Players.PlayerAdded:Fire(player)
	advance(2)
	assert(WorldAdmissionService.GetState(player) == "WorldMainMenuReady", "player reached the menu")
	return player
end

local function play(player, requestId: string)
	local result = {}
	task.spawn(function()
		result.ok, result.reason = handlers.RequestPlay(player, requestId)
	end)
	return result
end

local function stored(userId: number)
	return backing._data[ProfileStore.KeyFor(userId)]
end

-- Items the stored profile still owns outside a run.
local function storedCount(userId: number): number
	local profile = stored(userId)
	local count = #profile.lobbyBackpack.slots
	if profile.transit then
		count += #profile.transit.items
	end
	for _, receipt in profile.receipts.maintenance do
		if receipt.status == "Pending" then
			count += #receipt.items
		end
	end
	return count
end

-- Cases (the shutdown case runs last: a shutdown cannot be undone) ---------------

test("a Play whose save failed keeps the reservation, so the next Play brings the loadout", function()
	local player = arrive(101, stacks(3))
	backing.failNext = 5
	local first = play(player, "req-101-a")
	advance(60)
	expectEq(first.reason, "SaveFailed", "the first Play reports the failed save")
	expectEq(WorldAdmissionService.GetState(player), "WorldMainMenuReady", "back on the menu")
	expectEq(storedCount(101), 3, "nothing lost in the store")

	local second = play(player, "req-101-b")
	advance(5)
	expectEq(second.ok, true, "the retry enters the run")
	expectEq(started[player] and #started[player], 3, "with the reserved loadout")
	local profile = stored(101)
	expectEq(profile.transit, nil, "the reservation was consumed once")
	expectEq(#profile.lobbyBackpack.slots, 0, "and is not also in the lobby backpack")
end)

test("a safe kick whose save failed retries the save and kicks once it sticks", function()
	local player = arrive(102, stacks(2))
	play(player, "req-102")
	advance(2)
	expectEq(WorldAdmissionService.GetState(player), "ActiveRun", "in the run")
	backing.failNext = 5
	local kicked = nil
	task.spawn(function()
		kicked = AdminService.SafeKick(player)
	end)
	advance(60)
	expectEq(kicked, false, "the admin is told the save failed")
	advance(120)
	expect(player.kickMessage ~= nil, "the player is kicked once the escrow is saved")
	local escrowed = 0
	for _, receipt in stored(102).receipts.maintenance do
		escrowed += #receipt.items
	end
	expectEq(escrowed, 2, "the escrow is stored")
end)

test("a redirected arrival whose lobby teleport fails is not left stranded", function()
	game.PrivateServerId = ""
	local player = newPlayer(103, nil)
	table.insert(Players._list, player)
	Players.PlayerAdded:Fire(player)
	advance(2)
	game.PrivateServerId = "world-review"
	expect(player.sentToLobby, "sent to the lobby")
	expectEq(WorldAdmissionService.GetState(player), nil, "never staged")
	TravelService.TeleportFailed:Fire(player)
	advance(1)
	expect(player.kickMessage ~= nil, "kicked with a rejoin message instead of a blank world")
end)

test("the run's checkpoint exists as soon as the run starts", function()
	local player = arrive(104, stacks(1))
	play(player, "req-104")
	advance(0.5)
	expectEq(WorldAdmissionService.GetState(player), "ActiveRun", "in the run")
	expectEq(stored(104).transit, nil, "the consumed reservation is already saved")
	local ok, checkpoint = CheckpointStore.Read(104)
	expect(ok and checkpoint ~= nil, "a crash now can still recover the carried items")
	expectEq(checkpoint and #checkpoint.items, 1, "with the carried item")
end)

test("items that do not fit the run are saved back to the lobby at once", function()
	local player = arrive(105, stacks(70))
	play(player, "req-105")
	advance(1)
	expectEq(WorldAdmissionService.GetState(player), "ActiveRun", "in the run")
	expectEq(#stored(105).lobbyBackpack.slots, 11, "the 11 overflow items are already stored")
end)

test("lobby backpack materials stay put on load and after every write (GDD §53)", function()
	local legacy = ProfileSchema.Default(0)
	legacy.vault.materials.IronOre = 995
	legacy.lobbyBackpack.slots = {
		{ catalogId = "IronOre", quantity = 20 },
		{ instanceId = "spear-301", catalogId = "StoneSpear", ownerId = 1 },
	}
	backing._data[ProfileStore.KeyFor(301)] = legacy
	local player = newPlayer(301, nil)
	table.insert(Players._list, player)
	Players.PlayerAdded:Fire(player)
	advance(2)
	local profile = ProfileService.GetProfile(player)
	expectEq(profile.vault.materials.IronOre, 995, "nothing banked on load")
	expectEq(profile.vault.lastOverflow, nil, "and nothing deleted")
	expectEq(#profile.lobbyBackpack.slots, 2, "the Iron Ore waits in the backpack")

	local ok = ProfileService.RunOperation(player, "test-bank-301", "Test", function(working)
		table.insert(working.lobbyBackpack.slots, { catalogId = "AncientEmber", quantity = 3 })
	end)
	expect(ok, "operation committed")
	expectEq(profile.vault.materials.AncientEmber, nil, "an operation banks nothing")
	expectEq(#profile.lobbyBackpack.slots, 3, "the Ember stays in the backpack")
	ProfileService.Mutate(player, function(live)
		table.insert(live.lobbyBackpack.slots, { catalogId = "Wood", quantity = 4 })
	end)
	expectEq(profile.vault.materials.Wood, nil, "a direct mutation banks nothing")
	expectEq(#profile.lobbyBackpack.slots, 4, "the Wood stays in the backpack")
end)

-- The run inventory's stack of a material, or nil.
local function runStack(player, catalogId: string)
	for _, entry in InventoryService.Items(player) do
		if entry.instanceId == nil and entry.catalogId == catalogId then
			return entry
		end
	end
	return nil
end

test("a Play tags the materials it carries in, and escrow keeps each stack's own tag (GDD §53)", function()
	local player = arrive(106, {
		{ catalogId = "Wood", quantity = 60 },
		{ instanceId = "sword-106", catalogId = "StoneSword", ownerId = 1 },
		{ catalogId = "Wood", quantity = 40 },
		{ catalogId = "IronOre", quantity = 7 },
	})
	play(player, "req-106")
	advance(1)
	expectEq(WorldAdmissionService.GetState(player), "ActiveRun", "in the run")
	local wood = runStack(player, "Wood")
	expectEq(wood and wood.quantity, 100, "both Wood stacks merge into one")
	expectEq(wood and wood.carried, 100, "all of it carried in")
	expectEq(runStack(player, "IronOre").carried, 7, "Iron Ore carried in")
	local run = stored(106).progression.currentRun
	expectEq(run.carriedIn, nil, "no per-run total: the stacks are the record")
	local loadoutWood = 0
	for _, item in run.loadout do
		if item.catalogId == "Wood" then
			loadoutWood += item.carried or 0
		elseif item.catalogId == "StoneSword" then
			expectEq(item.carried, nil, "gear is never tagged")
		end
	end
	expectEq(loadoutWood, 100, "the saved loadout keeps the tags for a crash")

	-- Gathered Wood joins the stack; a checkpoint keeps the split.
	InventoryService.Add(player, { catalogId = "Wood", quantity = 30 })
	expectEq(runStack(player, "Wood").quantity, 130, "130 Wood")
	expectEq(runStack(player, "Wood").carried, 100, "still only 100 carried")
	advance(5)
	local ok, checkpoint = CheckpointStore.Read(106)
	local checkpointed = nil
	for _, item in (ok and checkpoint and checkpoint.items) or {} do
		if item.catalogId == "Wood" then
			checkpointed = item
		end
	end
	expectEq(checkpointed and checkpointed.carried, 100, "the checkpoint keeps the tag")

	-- A safe kick escrows the stacks as they are: the 30 gathered stay eligible.
	expect(MaintenanceService.Escrow(player), "escrowed")
	local escrowed = nil
	for _, receipt in ProfileService.GetProfile(player).receipts.maintenance do
		for _, item in receipt.items do
			if item.catalogId == "Wood" then
				escrowed = item
			end
		end
	end
	expectEq(escrowed and escrowed.quantity, 130, "all 130 Wood escrowed")
	expectEq(escrowed and escrowed.carried, 100, "with only its own 100 carried")
	leave(player)
	advance(5)

	-- The next Play brings the escrow back with its tags, beside 5 Wood from the lobby.
	local saved = stored(106)
	saved.transit = {
		reservationId = "res-106b",
		items = { { catalogId = "Wood", quantity = 5 } },
		createdAt = 0,
		status = "Reserved",
	}
	local again = newPlayer(106, "res-106b")
	table.insert(Players._list, again)
	Players.PlayerAdded:Fire(again)
	advance(2)
	play(again, "req-106b")
	advance(1)
	expectEq(WorldAdmissionService.GetState(again), "ActiveRun", "back in a run")
	expectEq(runStack(again, "Wood").quantity, 135, "130 escrowed + 5 from the lobby")
	expectEq(runStack(again, "Wood").carried, 105, "the gathered 30 are still not carried")
end)

test("a shutdown racing a Play never loses the reserved loadout", function()
	-- X's character finishes loading while the shutdown release is being written;
	-- Y consumed just before the shutdown while an earlier save held the slot.
	local x = arrive(201, stacks(3))
	local y = arrive(202, stacks(4))
	x.loadDelay = 1.2
	y.loadDelay = 1.0
	local playX = play(x, "req-201")
	local playY = play(y, "req-202")
	task.delay(0.95, function()
		ProfileService.SaveNow(y)
	end)
	task.delay(1.08, function()
		for _, fn in closeHandlers do
			fn()
		end
	end)
	advance(10)
	expectEq(playX.ok, false, "X does not start a run")
	expectEq(playY.ok, false, "Y does not start a run")
	expectEq(storedCount(201), 3, "X keeps every reserved item")
	expectEq(storedCount(202), 4, "Y keeps every reserved item")
end)

test("no spawned thread errored", function()
	for _, err in threadErrors do
		print("    thread error: " .. err)
	end
	expectEq(#threadErrors, 0, "thread errors")
end)
