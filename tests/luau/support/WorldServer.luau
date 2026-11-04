--!nocheck
-- A world server for run-lifecycle specs: a fake clock, fake Roblox services, a
-- DataStore whose calls take 0.3 s, and the real ProfileService,
-- WorldAdmissionService and the services named in `start`, wired as the Loader
-- would. Travel to the lobby only marks the player (sentToLobby); spawns are
-- always ready unless `world.ready` is set false.
--
--     local world = require(game:GetService("ServerStorage").TestSupport.WorldServer).new({
--         jobId = "job-x", privateServerId = "world-x", memoryStore = true,
--         start = { "InventoryService", "LoadoutService", ... },
--     })
--     local player = world.join(101, world.transit(101, world.stacks("item", 2)))
--     local result = world.play(player, "req-1"); world.advance(5)

local Server = game:GetService("ServerScriptService").Server
local TestSupport = script.Parent
local FakeRoblox = require(TestSupport.FakeRoblox)
local FakeStores = require(TestSupport.FakeStores)
local Scheduler = require(TestSupport.Scheduler)

local WorldServer = {}

function WorldServer.new(options)
	local scheduler = Scheduler.new():Install()
	local world = { scheduler = scheduler, threadErrors = scheduler.threadErrors, ready = true, closeHandlers = {} }
	function world.advance(seconds: number)
		scheduler:Advance(seconds)
	end

	local data = FakeStores.DataStore(0.3)
	world.backing = data.backing
	world.memory = if options.memoryStore then FakeStores.MemoryStore() else nil
	local Players = FakeRoblox.Players(true)
	world.Players = Players
	FakeRoblox.Provide({
		Players = Players,
		HttpService = FakeRoblox.Guids(),
		RunService = {
			Heartbeat = require(TestSupport.EngineSignal).new(true),
			IsStudio = function()
				return false
			end,
		},
		DataStoreService = data.service,
		TeleportService = { TeleportInitFailed = require(TestSupport.EngineSignal).new(true) },
		MemoryStoreService = if world.memory then world.memory.service else FakeStores.NoMemoryStore,
	})
	game.JobId = options.jobId
	game.PrivateServerId = options.privateServerId
	game.PlaceId = 1
	game.BindToClose = function(_, fn)
		table.insert(world.closeHandlers, fn)
	end
	FakeRoblox.Place("World")
	world.net = FakeRoblox.Remotes()
	world.handlers = world.net.handlers

	local Server = game:GetService("ServerScriptService").Server
	local TravelService = require(Server.Services.TravelService)
	TravelService.ToLobby = function(players)
		for _, player in players do
			player.sentToLobby = true
		end
		return true
	end
	local SpawnService = require(Server.Services.SpawnService)
	SpawnService.WorldReady = function()
		return world.ready
	end
	SpawnService.Pick = function()
		return "spawn"
	end

	local ProfileService = require(Server.Services.ProfileService)
	local WorldAdmissionService = require(Server.Services.WorldAdmissionService)
	-- Periodic autosaves would only add noise to the timelines.
	ProfileService.AUTOSAVE_SECONDS = 1e9
	ProfileService.Init()
	WorldAdmissionService.Init()
	for _, name in options.start do
		require(Server.Services[name]).Start()
	end
	world.started = {}
	WorldAdmissionService.RunStarted:Connect(function(player, _, items)
		world.started[player] = items
	end)

	local ProfileSchema = require(Server.Rules.Data.ProfileSchema)
	local ProfileStore = require(Server.Infrastructure.ProfileStore)

	-- The profile stored for `userId`.
	function world.stored(userId: number)
		return world.backing._data[ProfileStore.KeyFor(userId)]
	end

	-- `count` unique swords named prefix-1, prefix-2, ...
	function world.stacks(prefix: string, count: number)
		local items = {}
		for index = 1, count do
			table.insert(items, { instanceId = ("%s-%d"):format(prefix, index), catalogId = "StoneSword", ownerId = 1 })
		end
		return items
	end

	-- A new profile arriving with `items` reserved; returns it and the reservation.
	function world.transit(userId: number, items)
		local profile = ProfileSchema.Default(0)
		local reservationId = ("res-%d"):format(userId)
		profile.transit = { reservationId = reservationId, items = items, createdAt = 0, status = "Reserved" }
		return profile, reservationId
	end

	-- A player arriving with `reservationId` in its teleport data.
	function world.newPlayer(userId: number, reservationId: string?)
		return FakeRoblox.Player(userId, {
			teleportData = { reservations = { [tostring(userId)] = reservationId } },
		}, Players)
	end

	-- The player joins and its profile loads (two seconds pass).
	function world.enter(player)
		Players:Join(player)
		world.advance(2)
		return player
	end

	-- Stores `profile` for `userId`, joins and checks the player waits on the menu.
	function world.join(userId: number, profile, reservationId: string?)
		world.backing._data[ProfileStore.KeyFor(userId)] = profile
		local player = world.enter(world.newPlayer(userId, reservationId))
		assert(WorldAdmissionService.GetState(player) == "WorldMainMenuReady", "player reached the menu")
		return player
	end

	function world.leave(player)
		Players:Leave(player)
	end

	-- Sends RequestPlay in its own thread; the result fills in {ok, reason}.
	function world.play(player, requestId: string)
		local result = {}
		task.spawn(function()
			result.ok, result.reason = world.handlers.RequestPlay(player, requestId)
		end)
		return result
	end

	-- Fails the spec case with every error a spawned thread raised.
	function world.expectNoThreadErrors()
		scheduler:ExpectNoThreadErrors()
	end

	return world
end

return WorldServer
