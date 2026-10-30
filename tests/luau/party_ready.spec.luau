-- Advisory party Ready (UI rebuild D3): a lobby-only per-player flag set through
-- PartyAction("ready", bool). Covers the pure rules and what PartyService sends
-- each client (ready flags, createdAt, the leader's pending invites, the cap).

local Shared = game:GetService("ReplicatedStorage").Shared
local Server = game:GetService("ServerScriptService").Server

local PartyRules = require(Shared.Admission.PartyRules)

-- Pure rules ------------------------------------------------------------------------

test("a solo player can be ready without creating a party", function()
	local state = PartyRules.NewState()
	expect(PartyRules.SetReady(state, 1, true), "set")
	expect(PartyRules.IsReady(state, 1), "ready")
	expectEq(PartyRules.PartyOf(state, 1), nil, "no party created")
	expectEq(next(state.parties), nil, "no party record at all")
	expect(PartyRules.SetReady(state, 1, false), "unset")
	expect(not PartyRules.IsReady(state, 1), "not ready")
	expectEq(state.ready[1], nil, "no entry kept for false")
end)

test("only a boolean sets ready", function()
	local state = PartyRules.NewState()
	for _, bad in { 1, "true", {} } do
		local ok, reason = PartyRules.SetReady(state, 1, bad)
		expect(not ok and reason == "BadRequest", "refused " .. tostring(bad))
	end
	local ok, reason = PartyRules.SetReady(state, 1, nil)
	expect(not ok and reason == "BadRequest", "refused nil")
	expect(not PartyRules.IsReady(state, 1), "unchanged")
end)

test("accept clears ready for every member of both parties", function()
	local state = PartyRules.NewState()
	PartyRules.Invite(state, 1, 2, "a", 100)
	PartyRules.Accept(state, 2, "a")
	PartyRules.Invite(state, 3, 4, "b", 100)
	PartyRules.Accept(state, 4, "b")
	PartyRules.Invite(state, 1, 4, "x", 100)
	for userId = 1, 5 do
		PartyRules.SetReady(state, userId, true)
	end
	expect(PartyRules.Accept(state, 4, "a"), "4 moves to party a")
	for _, userId in { 1, 2, 3, 4 } do
		expect(not PartyRules.IsReady(state, userId), userId .. " cleared")
	end
	expect(PartyRules.IsReady(state, 5), "a bystander keeps ready")
end)

test("leave and forget clear the whole party; invite and decline do not", function()
	local state = PartyRules.NewState()
	PartyRules.Invite(state, 1, 2, "a", 100)
	PartyRules.Accept(state, 2, "a")
	PartyRules.Invite(state, 1, 3, "x", 100)
	PartyRules.Invite(state, 1, 4, "x", 100)
	for userId = 1, 4 do
		PartyRules.SetReady(state, userId, true)
	end
	PartyRules.Decline(state, 3, "a")
	PartyRules.Invite(state, 1, 5, "x", 100)
	expect(PartyRules.IsReady(state, 1) and PartyRules.IsReady(state, 3), "invite and decline keep ready")
	PartyRules.Leave(state, 2)
	expect(not PartyRules.IsReady(state, 1) and not PartyRules.IsReady(state, 2), "leave clears leaver and party")
	expect(PartyRules.IsReady(state, 4), "an invitee outside the party is untouched")

	PartyRules.Invite(state, 1, 2, "x", 100)
	PartyRules.Accept(state, 2, "a")
	PartyRules.SetReady(state, 1, true)
	PartyRules.SetReady(state, 2, true)
	PartyRules.Forget(state, 1)
	expect(not PartyRules.IsReady(state, 2), "a member leaving the server clears the rest")
	PartyRules.Forget(state, 4)
	expectEq(state.ready[4], nil, "a solo player's flag is forgotten too")
	expectEq(PartyRules.PartyOf(state, 2).invites[4], nil, "and their invites")
end)

test("a party records when it was created and lists pending invites", function()
	local state = PartyRules.NewState()
	PartyRules.Invite(state, 1, 9, "a", 1234)
	PartyRules.Invite(state, 1, 3, "x", 9999)
	local party = PartyRules.PartyOf(state, 1)
	expectEq(party.createdAt, 1234, "created at the first invite")
	local pending = PartyRules.PendingInvites(party)
	expect(#pending == 2 and pending[1] == 3 and pending[2] == 9, "sorted pending invites")
	PartyRules.Accept(state, 3, "a")
	pending = PartyRules.PendingInvites(party)
	expect(#pending == 1 and pending[1] == 9, "an accepted invite is no longer pending")
	expectEq(party.createdAt, 1234, "joining does not change createdAt")
end)

-- PartyService views ----------------------------------------------------------------

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

local guids = 0
local fakes = {
	Players = Players,
	HttpService = {
		GenerateGUID = function()
			guids += 1
			return string.format("%08x-0000-4000-8000-%012x", guids, guids)
		end,
	},
}
local originalGetService = game.GetService
game.GetService = function(self, name)
	return fakes[name] or originalGetService(self, name)
end

local PlaceConfig = require(Shared.Config.PlaceConfig)
local Remotes = require(Shared.Net.Remotes)
local handlers = {}
-- The latest view each player was sent, by UserId.
local sent = {}
Remotes.Handle = function(name, fn)
	handlers[name] = fn
end
Remotes.Get = function()
	return {
		FireClient = function(_, player, view)
			sent[player.UserId] = view
		end,
	}
end
PlaceConfig.IsLobby = function()
	return true
end
local PartyService = require(Server.Services.PartyService)
PartyService.Start()
local COOLDOWN = PartyService.REQUEST_COOLDOWN_SECONDS
PartyService.REQUEST_COOLDOWN_SECONDS = -1

local function newPlayer(userId: number)
	local player = { UserId = userId, Name = "P" .. userId, DisplayName = "Name" .. userId, Parent = Players }
	table.insert(Players._list, player)
	Players.PlayerAdded:Fire(player)
	return player
end

local function removePlayer(player)
	table.remove(Players._list, table.find(Players._list, player))
	Players.PlayerRemoving:Fire(player)
end

local leader, member, invitee, solo = newPlayer(1), newPlayer(2), newPlayer(3), newPlayer(4)

test("ready rides PartyAction with a type check and reaches every view", function()
	expectEq(sent[4].ready, false, "not ready at first")
	expectEq(sent[4].maxSize, 8, "the cap is sent")
	expect(handlers.PartyAction(solo, "ready", true), "solo ready")
	expectEq(sent[4].ready, true, "solo sees ready")
	expectEq(sent[4].party, nil, "solo still has no party")
	expectEq(PartyService.PartyIdOf(solo), nil, "no party to deploy with")
	for _, bad in { "yes", 1, {} } do
		local ok, reason = handlers.PartyAction(solo, "ready", bad)
		expect(not ok and reason == "BadRequest", "refused " .. tostring(bad))
	end
	local ok, reason = handlers.PartyAction(solo, "ready")
	expect(not ok and reason == "BadRequest", "refused a missing flag")
	expectEq(sent[4].ready, true, "bad requests change nothing")
end)

test("the party view carries ready flags, createdAt, cap and the leader's invites", function()
	local before = os.time()
	handlers.PartyAction(leader, "invite", 2)
	handlers.PartyAction(leader, "invite", 3)
	local partyId = PartyService.PartyIdOf(leader)
	handlers.PartyAction(member, "accept", partyId)
	handlers.PartyAction(member, "ready", true)

	local view = sent[1]
	expect(view.party ~= nil, "leader has a party")
	expect(type(view.party.createdAt) == "number" and view.party.createdAt >= before, "createdAt is server os.time")
	expectEq(#view.party.members, 2, "two members")
	expectEq(view.party.members[2].userId, 2, "member listed")
	expectEq(view.party.members[2].ready, true, "member ready")
	expectEq(view.party.members[1].ready, false, "leader not ready")
	expectEq(view.ready, false, "own flag")
	expect(#view.party.invited == 1 and view.party.invited[1] == 3, "the leader sees the pending invite")
	expectEq(view.maxSize, 8, "cap")

	local memberView = sent[2]
	expectEq(#memberView.party.invited, 0, "other members do not see who was invited")
	expectEq(memberView.ready, true, "member's own flag")

	local inviteeView = sent[3]
	expectEq(inviteeView.party, nil, "an invitee sees no party details")
	expectEq(#inviteeView.invites, 1, "only the invite")
	expectEq(inviteeView.invites[1].from, "Name1", "from the leader's display name")
	expectEq(inviteeView.invites[1].members, nil, "no member list leaks with an invite")

	local soloView = sent[4]
	expectEq(soloView.party, nil, "a stranger sees nothing of the party")
	expectEq(#soloView.invites, 0, "and no invites")
end)

test("accept, leave and disconnect clear ready for the parties involved", function()
	local partyId = PartyService.PartyIdOf(leader)
	handlers.PartyAction(leader, "ready", true)
	handlers.PartyAction(member, "ready", true)
	handlers.PartyAction(invitee, "ready", true)
	handlers.PartyAction(invitee, "accept", partyId)
	expect(not sent[1].ready and not sent[2].ready and not sent[3].ready, "accept clears all three")
	expectEq(sent[4].ready, true, "the solo player is untouched")

	handlers.PartyAction(leader, "ready", true)
	handlers.PartyAction(member, "ready", true)
	handlers.PartyAction(invitee, "leave")
	expect(not sent[1].ready and not sent[2].ready, "leave clears the party")

	handlers.PartyAction(leader, "ready", true)
	handlers.PartyAction(member, "ready", true)
	removePlayer(member)
	expect(not sent[1].ready, "a disconnect clears the rest of the party")
	expectEq(#sent[1].party.members, 1, "member gone")
end)

test("a starting deploy clears its group's ready flags", function()
	handlers.PartyAction(leader, "ready", true)
	handlers.PartyAction(invitee, "ready", true)
	PartyService.ClearReady({ leader, solo })
	expect(not sent[1].ready and not sent[4].ready, "deploying group cleared")
	expectEq(sent[3].ready, true, "others keep theirs")
end)

test("the per-player cooldown still applies to ready", function()
	PartyService.REQUEST_COOLDOWN_SECONDS = COOLDOWN
	local fresh = newPlayer(5)
	expect(handlers.PartyAction(fresh, "ready", true), "first request")
	local ok, reason = handlers.PartyAction(fresh, "ready", false)
	expect(not ok and reason == "TooFast", "spam refused")
	expectEq(sent[5].ready, true, "the refused request changed nothing")
	PartyService.REQUEST_COOLDOWN_SECONDS = -1
end)

test("unknown actions are refused", function()
	local ok, reason = handlers.PartyAction(solo, "kick", 1)
	expect(not ok and reason == "BadRequest", "no kick action")
end)
