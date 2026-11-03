--!nocheck
-- A lobby server for trade specs: a fake clock (also the server time), fake
-- Players, profiles held in memory (a save copies one into `stored`) and the real
-- TradeService session flow.
--
--     local lobby = require(game:GetService("ServerStorage").TestSupport.LobbyTrade).new()
--     local a, b, id = lobby.session(lobby.trader(), lobby.trader())
--     lobby.handlers.TradeOffer(a, id, { "sword-1" }, 0)
--     lobby.lockAndConfirm(a, b, id)

local TestSupport = script.Parent
local FakeRoblox = require(TestSupport.FakeRoblox)
local Scheduler = require(TestSupport.Scheduler)

local LobbyTrade = {}

function LobbyTrade.new()
	local scheduler = Scheduler.new():Install():InstallServerTime()
	local Players = FakeRoblox.Players()
	FakeRoblox.Provide({ Players = Players, HttpService = FakeRoblox.Guids() })
	game.JobId = "job-trade"
	FakeRoblox.Place("Lobby")
	local net = FakeRoblox.Remotes()

	local ProfileSchema = require(game:GetService("ReplicatedStorage").Shared.Data.ProfileSchema)
	local Services = game:GetService("ServerScriptService").Server.Services
	local profiles, stored = {}, {}
	local ProfileService = require(Services.ProfileService)
	ProfileService.GetProfile = function(player)
		return profiles[player]
	end
	ProfileService.Mutate = function(player, apply)
		local profile = profiles[player]
		if profile == nil then
			return false
		end
		apply(profile)
		return true
	end
	ProfileService.SaveNow = function(player)
		stored[player.UserId] = ProfileSchema.DeepCopy(profiles[player])
		return true
	end
	ProfileService.ReadStored = function(userId)
		return true, stored[userId]
	end
	require(Services.CurrencyService).Publish = function() end
	local TradeService = require(Services.TradeService)
	TradeService.Start()

	local lobby = {
		scheduler = scheduler,
		threadErrors = scheduler.threadErrors,
		Players = Players,
		handlers = net.handlers,
		-- The latest TradeChanged payload each player was sent.
		pushed = net.last,
		profiles = profiles,
		stored = stored,
	}
	function lobby.advance(seconds: number)
		scheduler:Advance(seconds)
	end

	-- A new profile at a level that may trade.
	function lobby.trader()
		local profile = ProfileSchema.Default(0)
		profile.progression.level = 12
		return profile
	end

	-- A new player joins with `profile`, which is also its saved copy.
	local nextUserId = 100
	function lobby.join(profile)
		nextUserId += 1
		local player = FakeRoblox.Player(nextUserId, { DisplayName = "P" .. nextUserId }, Players)
		Players:Join(player)
		profiles[player] = profile
		stored[player.UserId] = ProfileSchema.DeepCopy(profile)
		return player
	end

	-- The player leaves: PlayerRemoving fires, the release save stores the live
	-- profile and the server forgets it (ProfileService's PlayerRemoving handler).
	function lobby.leave(player)
		Players:Leave(player)
		stored[player.UserId] = ProfileSchema.DeepCopy(profiles[player])
		profiles[player] = nil
	end

	-- The same account joins again: its saved profile loads and ProfileLoaded fires.
	function lobby.rejoin(player)
		player.Parent = Players
		table.insert(Players._list, player)
		profiles[player] = ProfileSchema.DeepCopy(stored[player.UserId])
		ProfileService.ProfileLoaded:Fire(player, profiles[player])
	end

	-- Two joined players in an accepted session.
	function lobby.session(profileA, profileB)
		local a, b = lobby.join(profileA), lobby.join(profileB)
		local ok, id = net.handlers.TradeRequest(a, b.UserId)
		assert(ok, "invite: " .. tostring(id))
		assert(net.handlers.TradeRespond(b, id, true), "accept")
		return a, b, id
	end

	-- Both lock, the countdown runs out and both confirm; returns the last confirm.
	function lobby.lockAndConfirm(a, b, id)
		net.handlers.TradeLock(a, id)
		net.handlers.TradeLock(b, id)
		lobby.advance(TradeService.COUNTDOWN_SECONDS)
		net.handlers.TradeConfirm(a, id)
		return net.handlers.TradeConfirm(b, id)
	end

	return lobby
end

return LobbyTrade
