--!nocheck
-- Fake Roblox services, players, characters and instances for specs that drive the
-- real server services. Each helper installs only what it names; a spec combines
-- the ones its services use.
--
--     local FakeRoblox = require(game:GetService("ServerStorage").TestSupport.FakeRoblox)
--     local Players = FakeRoblox.Players()
--     FakeRoblox.Provide({ Players = Players, HttpService = FakeRoblox.Guids() })
--     local net = FakeRoblox.Remotes()          -- net.handlers.RequestPlay(player, ...)

local EngineSignal = require(script.Parent.EngineSignal)

local FakeRoblox = {}

-- game:GetService(name) returns the fake provided under `name`, else the prelude's
-- instance-tree stand-in. Later calls add to (or replace) earlier fakes.
local provided = nil
function FakeRoblox.Provide(services)
	if provided == nil then
		provided = {}
		local originalGetService = game.GetService
		game.GetService = function(self, name)
			return provided[name] or originalGetService(self, name)
		end
	end
	for name, service in services do
		provided[name] = service
	end
	return services
end

-- HttpService whose GUIDs are well-formed and numbered; `last` is the latest.
function FakeRoblox.Guids()
	local http = { count = 0, last = nil }
	function http.GenerateGUID()
		http.count += 1
		http.last = ("%08x-0000-4000-8000-%012x"):format(http.count, http.count)
		return http.last
	end
	return http
end

-- Makes PlaceConfig report a world ("World") or the lobby ("Lobby").
function FakeRoblox.Place(kind: string)
	local PlaceConfig = require(game:GetService("ReplicatedStorage").Shared.Config.PlaceConfig)
	PlaceConfig.IsWorld = function()
		return kind == "World"
	end
	PlaceConfig.IsLobby = function()
		return kind == "Lobby"
	end
end

-- Replaces Remotes.Handle/Get. The returned record holds every handler by name,
-- the arguments each remote last sent each player (sent[name][player], packed),
-- the first argument of the last message to each player on any remote (last) and
-- how many messages each player was sent (fires).
function FakeRoblox.Remotes()
	local Remotes = require(game:GetService("ReplicatedStorage").Shared.Net.Remotes)
	local net = { handlers = {}, sent = {}, last = {}, fires = {} }
	Remotes.Handle = function(name, fn)
		net.handlers[name] = fn
	end
	Remotes.Get = function(name)
		return {
			FireClient = function(_, player, ...)
				net.sent[name] = net.sent[name] or {}
				net.sent[name][player] = table.pack(...)
				net.last[player] = (...)
				net.fires[player] = (net.fires[player] or 0) + 1
			end,
			FireAllClients = function() end,
		}
	end
	return net
end

-- Makes `require(Server.Services.<Name>)` return stubs[Name] when there is one, so
-- a service under test sees fakes for the services it calls.
function FakeRoblox.StubServices(stubs)
	local realRequire = require
	require = function(node)
		local path = type(node) == "table" and rawget(node, "__path")
		if path and path[1] == "ServerScriptService" and path[3] == "Services" and stubs[path[4]] then
			return stubs[path[4]]
		end
		return realRequire(node)
	end
	return stubs
end

-- Players with PlayerAdded/PlayerRemoving (handlers run in their own threads when
-- `threaded`, as the engine runs them; install a Scheduler first). Join adds a
-- player and fires PlayerAdded; Leave removes one, unparents it and fires
-- PlayerRemoving.
function FakeRoblox.Players(threaded: boolean?)
	local Players = {
		PlayerAdded = EngineSignal.new(threaded),
		PlayerRemoving = EngineSignal.new(threaded),
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
	function Players.GetPlayerFromCharacter(self, character)
		for _, player in self._list do
			if player.Character == character then
				return player
			end
		end
		return nil
	end
	function Players.Join(self, player)
		player.Parent = self
		table.insert(self._list, player)
		self.PlayerAdded:Fire(player)
		return player
	end
	function Players.Leave(self, player)
		local index = table.find(self._list, player)
		if index then
			table.remove(self._list, index)
			player.Parent = nil
			self.PlayerRemoving:Fire(player)
		end
	end
	return Players
end

-- A character at `position` (default 0, 5, 0): `humanoid`, `root` and `head` are
-- plain tables a spec may change. Died runs threaded handlers when `threaded`.
function FakeRoblox.Character(position: Vector3?, threaded: boolean?)
	local at = position or Vector3.new(0, 5, 0)
	local humanoid =
		{ Health = 100, MaxHealth = 100, WalkSpeed = 16, JumpHeight = 7.2, Died = EngineSignal.new(threaded) }
	local root = { Position = at, Anchored = false, CFrame = { LookVector = Vector3.new(0, 0, 1) } }
	local head = { Position = at + Vector3.new(0, 1.5, 0) }
	local character = { humanoid = humanoid, root = root, head = head }
	function character.FindFirstChildOfClass(_, className)
		return if className == "Humanoid" then humanoid else nil
	end
	function character.FindFirstChild(_, name)
		return if name == "HumanoidRootPart" then root elseif name == "Head" then head else nil
	end
	function character.PivotTo() end
	function character.GetPivot()
		return { Position = root.Position }
	end
	function character.Destroy() end
	return character
end

-- A player with attributes; `fields` are set on it (Name, DisplayName, Parent,
-- Character, teleportData, ...). GetJoinData returns `teleportData`; Kick records
-- the message and leaves `players`; LoadCharacter waits `loadDelay` seconds, then
-- gives it a fresh character with threaded Died handlers.
function FakeRoblox.Player(userId: number, fields, players)
	local player = {
		UserId = userId,
		Name = "Player" .. userId,
		DisplayName = "Player" .. userId,
		Parent = players,
		attributes = {},
		loadDelay = 0,
	}
	for key, value in fields or {} do
		player[key] = value
	end
	function player.SetAttribute(self, key, value)
		self.attributes[key] = value
	end
	function player.GetAttribute(self, key)
		return self.attributes[key]
	end
	function player.GetJoinData(self)
		return { TeleportData = self.teleportData }
	end
	function player.Kick(self, message)
		self.kickMessage = message
		if players then
			players:Leave(self)
		end
	end
	function player.LoadCharacter(self)
		if self.loadDelay > 0 then
			task.wait(self.loadDelay)
		end
		self.Character = FakeRoblox.Character(nil, true)
	end
	return player
end

-- Installs Instance.new, CFrame and RaycastParams stand-ins. Instance properties are
-- plain fields (setting CFrame moves Position too); an event is a shared Signal
-- (handlers run protected, a failure warns) made on first use. Returns the list of
-- every instance made, oldest first.
function FakeRoblox.Instances()
	local Signal = require(game:GetService("ReplicatedStorage").Shared.Core.Signal)
	local created = {}
	local cframeMeta = {
		__mul = function(a)
			return a
		end,
	}
	CFrame = {
		new = function(position)
			return setmetatable({ Position = position }, cframeMeta)
		end,
	}
	RaycastParams = {
		new = function()
			return {}
		end,
	}
	Instance = {
		new = function(className)
			local instance = {
				ClassName = className,
				Destroy = function(self)
					self.destroyed = true
				end,
				IsA = function(_, name)
					return name == className or (name == "BasePart" and className == "Part")
				end,
			}
			table.insert(created, instance)
			return setmetatable(instance, {
				__index = function(self, key)
					local signal = Signal.new()
					rawset(self, key, signal)
					return signal
				end,
				__newindex = function(self, key, value)
					rawset(self, key, value)
					if key == "CFrame" then
						rawset(self, "Position", value.Position)
					end
				end,
			})
		end,
	}
	return created
end

return FakeRoblox
