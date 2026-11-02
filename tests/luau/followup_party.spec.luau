-- Follow-up review: a lobby party id seen in an invite must not admit anyone into
-- that party's in-world tribe. Drives PartyService against a fake MemoryStore.

local Shared = game:GetService("ReplicatedStorage").Shared
local Server = game:GetService("ServerScriptService").Server

-- Fake Roblox services -------------------------------------------------------------

local function engineSignal()
	local handlers = {}
	return {
		Connect = function(_, fn)
			table.insert(handlers, fn)
			return { Disconnect = function() end }
		end,
		Fire = function(_, ...)
			for _, fn in table.clone(handlers) do
				fn(...)
			end
		end,
	}
end

local Players = { PlayerAdded = engineSignal(), PlayerRemoving = engineSignal(), _list = {} }
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

-- A MemoryStore hash map that can be made to fail.
local memory = { data = {}, failing = false, writes = 0 }
local fakeMap = {
	SetAsync = function(_, key, value)
		if memory.failing then
			error("MemoryStore unavailable")
		end
		memory.writes += 1
		memory.data[key] = value
		return true
	end,
	GetAsync = function(_, key)
		if memory.failing then
			error("MemoryStore unavailable")
		end
		return memory.data[key]
	end,
}

local guids = 0
local fakes = {
	Players = Players,
	HttpService = {
		GenerateGUID = function()
			guids += 1
			return string.format("%08x-0000-4000-8000-%012x", guids, guids)
		end,
	},
	MemoryStoreService = {
		GetHashMap = function()
			return fakeMap
		end,
	},
}
local originalGetService = game.GetService
game.GetService = function(self, name)
	return fakes[name] or originalGetService(self, name)
end
game.PrivateServerId = "world-1"
task = {
	wait = function() end,
	spawn = function(fn, ...)
		fn(...)
	end,
}
warn = function() end

local PartyRules = require(Shared.Admission.PartyRules)

-- Lobby party ids cannot be forged into a world tribe ----------------------------

local PlaceConfig = require(Shared.Config.PlaceConfig)
local Remotes = require(Shared.Net.Remotes)
local handlers = {}
Remotes.Handle = function(name, fn)
	handlers[name] = fn
end
Remotes.Get = function()
	return { FireClient = function() end, FireAllClients = function() end }
end
PlaceConfig.IsLobby = function()
	return true
end
local PartyService = require(Server.Services.PartyService)
PartyService.Start()

local function newPlayer(userId: number)
	local player = { UserId = userId, Name = "P" .. userId, DisplayName = "P" .. userId, Parent = Players }
	player.teleportData = nil
	function player.GetJoinData(self)
		return { TeleportData = self.teleportData }
	end
	table.insert(Players._list, player)
	Players.PlayerAdded:Fire(player)
	return player
end

local leader, member, decliner, stranger = newPlayer(1), newPlayer(2), newPlayer(3), newPlayer(4)
handlers.PartyAction(leader, "invite", 2)
handlers.PartyAction(leader, "invite", 3)
local partyId = PartyService.PartyIdOf(leader)
handlers.PartyAction(member, "accept", partyId)
handlers.PartyAction(decliner, "decline", partyId)

test("a deploy records the party's members under a fresh server token", function()
	local group = PartyService.DeployGroup(leader)
	expectEq(#group, 2, "leader and member deploy")
	local token = PartyService.RecordDeploy(leader, group, "world-1")
	expect(PartyRules.IsGuid(token), "a token travels in teleport data")
	expect(token ~= partyId, "the token is not the party id invitees saw")
	local record = memory.data[token]
	expectEq(record and record.partyId, partyId, "the record names the party")
	expectEq(record and #record.members, 2, "and only who deployed")
	for _, player in group do
		player.teleportData = { reservations = {}, partyToken = token }
		expectEq(PartyService.VerifiedPartyId(player), partyId, player.Name .. " joins the party tribe")
	end
end)

test("a declined invitee forging the party id or a member's token stays solo", function()
	local token = PartyService.RecordDeploy(leader, PartyService.DeployGroup(leader), "world-1")
	decliner.teleportData = { partyId = partyId }
	expectEq(PartyService.VerifiedPartyId(decliner), nil, "a bare party id proves nothing")
	decliner.teleportData = { partyId = partyId, partyToken = token }
	expectEq(PartyService.VerifiedPartyId(decliner), nil, "a leaked token does not list them")
	stranger.teleportData = { partyToken = "not-a-token" }
	expectEq(PartyService.VerifiedPartyId(stranger), nil, "garbage is solo")
	stranger.teleportData = { partyToken = string.format("%08x-0000-4000-8000-%012x", 999, 999) }
	expectEq(PartyService.VerifiedPartyId(stranger), nil, "an unknown token is solo")
	stranger.teleportData = "nonsense"
	expectEq(PartyService.VerifiedPartyId(stranger), nil, "non-table teleport data is solo")
end)

test("a token from another world or an expired deploy is refused", function()
	local token = PartyService.RecordDeploy(leader, PartyService.DeployGroup(leader), "world-2")
	member.teleportData = { partyToken = token }
	expectEq(PartyService.VerifiedPartyId(member), nil, "recorded for a different world")
	local record = PartyRules.DeployRecord(partyId, { 1, 2 }, "world-1", 100)
	expectEq(PartyRules.VerifiedPartyId(record, 2, "world-1", 100 + 60), partyId, "fresh")
	expectEq(
		PartyRules.VerifiedPartyId(record, 2, "world-1", 100 + PartyRules.DEPLOY_RECORD_SECONDS + 1),
		nil,
		"expired"
	)
	expectEq(PartyRules.VerifiedPartyId(record, 3, "world-1", 100), nil, "not a member")
	expectEq(PartyRules.VerifiedPartyId({ partyId = "x", members = { 2 }, at = 100 }, 2, "world-1", 100), nil, "bad id")
end)

test("a MemoryStore outage falls back to solo without blocking the deploy", function()
	memory.failing = true
	local token = PartyService.RecordDeploy(leader, PartyService.DeployGroup(leader), "world-1")
	expectEq(token, nil, "no token when the record could not be written")
	memory.failing = false
	local good = PartyService.RecordDeploy(leader, PartyService.DeployGroup(leader), "world-1")
	memory.failing = true
	member.teleportData = { partyToken = good }
	expectEq(PartyService.VerifiedPartyId(member), nil, "an unreadable record is solo")
	memory.failing = false
	expectEq(PartyService.VerifiedPartyId(member), partyId, "readable again")
end)

test("a solo player records nothing", function()
	local before = memory.writes
	expectEq(PartyService.RecordDeploy(stranger, { stranger }, "world-1"), nil, "no party, no token")
	expectEq(memory.writes, before, "no write")
end)

test("the leader deploys the whole party; there is no ready step", function()
	local cooldown = PartyService.REQUEST_COOLDOWN_SECONDS
	PartyService.REQUEST_COOLDOWN_SECONDS = -1
	local ok, reason = handlers.PartyAction(member, "ready", true)
	expect(not ok and reason == "BadRequest", "ready is no longer a party action")
	local group = PartyService.DeployGroup(leader)
	expectEq(#group, 2, "the leader deploys the party")
	local token = PartyService.RecordDeploy(leader, group, "world-1")
	expectEq(memory.data[token].ready, nil, "the deploy record carries no ready state")
	local none, why = PartyService.DeployGroup(member)
	expect(none == nil and why == "OnlyLeaderDeploys", "a member cannot deploy")
	PartyService.REQUEST_COOLDOWN_SECONDS = cooldown
end)
