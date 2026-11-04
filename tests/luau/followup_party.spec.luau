-- Follow-up review: a lobby party id seen in an invite must not admit anyone into
-- that party's in-world tribe. Drives PartyService against a fake MemoryStore.

local Shared = game:GetService("ReplicatedStorage").Shared
local Server = game:GetService("ServerScriptService").Server

local TestSupport = game:GetService("ServerStorage").TestSupport
local FakeRoblox = require(TestSupport.FakeRoblox)

-- PartyService's MemoryStore calls run inline; a retry does not wait.
task = {
	wait = function() end,
	spawn = function(fn, ...)
		fn(...)
	end,
}
warn = function() end

-- A MemoryStore that can be made to fail (memory.failing).
local memory = require(TestSupport.FakeStores).MemoryStore()
local Players = FakeRoblox.Players()
FakeRoblox.Provide({ Players = Players, HttpService = FakeRoblox.Guids(), MemoryStoreService = memory.service })
game.PrivateServerId = "world-1"
FakeRoblox.Place("Lobby")
local handlers = FakeRoblox.Remotes().handlers

local PartyRules = require(Server.Rules.Admission.PartyRules)
local PartyService = require(Server.Services.PartyService)
PartyService.Start()

-- The stored deploy record under `token`.
local function recordOf(token)
	return memory.maps[PartyService.MAP_NAME][token]
end

local function newPlayer(userId: number)
	return Players:Join(FakeRoblox.Player(userId, nil, Players))
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
	local record = recordOf(token)
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
	expectEq(recordOf(token).ready, nil, "the deploy record carries no ready state")
	local none, why = PartyService.DeployGroup(member)
	expect(none == nil and why == "OnlyLeaderDeploys", "a member cannot deploy")
	PartyService.REQUEST_COOLDOWN_SECONDS = cooldown
end)
