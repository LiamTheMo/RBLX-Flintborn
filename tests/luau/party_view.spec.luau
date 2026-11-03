-- Lobby party views: the pure rules behind them (createdAt, pending invites)
-- and what PartyService sends each client (members, createdAt, the leader's
-- pending invites, the cap). There is no Ready flag (ARCHITECTURE D24).

local Shared = game:GetService("ReplicatedStorage").Shared
local Server = game:GetService("ServerScriptService").Server

local PartyRules = require(Shared.Admission.PartyRules)

-- Pure rules ------------------------------------------------------------------------

test("a party records its creation and pending invites; leave and forget clear a player", function()
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
	PartyRules.Leave(state, 3)
	expectEq(PartyRules.PartyOf(state, 3), nil, "the leaver has no party")
	expectEq(#PartyRules.PartyOf(state, 1).members, 1, "the leader stays")
	PartyRules.Forget(state, 9)
	expectEq(PartyRules.PartyOf(state, 1).invites[9], nil, "a forgotten player's invites go")
end)

-- PartyService views ----------------------------------------------------------------

local FakeRoblox = require(game:GetService("ServerStorage").TestSupport.FakeRoblox)
local Players = FakeRoblox.Players()
FakeRoblox.Provide({ Players = Players, HttpService = FakeRoblox.Guids() })
FakeRoblox.Place("Lobby")
local net = FakeRoblox.Remotes()
local handlers = net.handlers
local PartyService = require(Server.Services.PartyService)
PartyService.Start()
local COOLDOWN = PartyService.REQUEST_COOLDOWN_SECONDS
PartyService.REQUEST_COOLDOWN_SECONDS = -1

local byId = {}
local function newPlayer(userId: number)
	byId[userId] = FakeRoblox.Player(userId, { Name = "P" .. userId, DisplayName = "Name" .. userId }, Players)
	return Players:Join(byId[userId])
end

-- The latest view sent to a player, and how many views it was sent, by UserId.
local function viewOf(userId: number)
	return net.last[byId[userId]]
end
local function fired(userId: number): number
	return net.fires[byId[userId]] or 0
end

local leader, member, invitee, solo = newPlayer(1), newPlayer(2), newPlayer(3), newPlayer(4)

test("there is no ready flag or action, and unknown actions are refused", function()
	expectEq(PartyRules.SetReady, nil, "no ready rule")
	expectEq(PartyRules.IsReady, nil, "no ready query")
	local keys = {}
	for key in PartyRules.NewState() do
		table.insert(keys, key)
	end
	table.sort(keys)
	expectEq(table.concat(keys, ","), "memberOf,parties", "no per-player ready state")
	expectEq(viewOf(4).ready, nil, "no ready flag in the view")
	expectEq(viewOf(4).maxSize, 8, "the cap is sent")
	for _, value in { true, false } do
		local ok, reason = handlers.PartyAction(solo, "ready", value)
		expect(not ok and reason == "BadRequest", "refused ready " .. tostring(value))
	end
	expectEq(viewOf(4).party, nil, "solo still has no party")
	expectEq(PartyService.ClearReady, nil, "no ready clearing on deploy")
	local ok, reason = handlers.PartyAction(solo, "kick", 1)
	expect(not ok and reason == "BadRequest", "no kick action")
end)

test("the party view carries members, createdAt, cap and the leader's invites", function()
	local before = os.time()
	handlers.PartyAction(leader, "invite", 2)
	handlers.PartyAction(leader, "invite", 3)
	local partyId = PartyService.PartyIdOf(leader)
	handlers.PartyAction(member, "accept", partyId)

	local view = viewOf(1)
	expect(view.party ~= nil, "leader has a party")
	expect(type(view.party.createdAt) == "number" and view.party.createdAt >= before, "createdAt is server os.time")
	expectEq(#view.party.members, 2, "two members")
	expectEq(view.party.members[2].userId, 2, "member listed")
	expectEq(view.party.members[2].name, "Name2", "by display name")
	expectEq(view.party.members[2].ready, nil, "no member ready flag")
	expectEq(view.ready, nil, "no own ready flag")
	expect(#view.party.invited == 1 and view.party.invited[1] == 3, "the leader sees the pending invite")
	expectEq(view.maxSize, 8, "cap")

	local memberView = viewOf(2)
	expectEq(#memberView.party.invited, 0, "other members do not see who was invited")

	local inviteeView = viewOf(3)
	expectEq(inviteeView.party, nil, "an invitee sees no party details")
	expectEq(#inviteeView.invites, 1, "only the invite")
	expectEq(inviteeView.invites[1].from, "Name1", "from the leader's display name")
	expectEq(inviteeView.invites[1].fromUserId, 1, "and the leader's user id")
	expectEq(inviteeView.invites[1].partyId, partyId, "for the leader's party")
	expectEq(inviteeView.invites[1].members, nil, "no member list leaks with an invite")

	local soloView = viewOf(4)
	expectEq(soloView.party, nil, "a stranger sees nothing of the party")
	expectEq(#soloView.invites, 0, "and no invites")
end)

test("accept, leave and disconnect update the views of the parties involved", function()
	local partyId = PartyService.PartyIdOf(leader)
	handlers.PartyAction(invitee, "accept", partyId)
	expectEq(#viewOf(1).party.members, 3, "accept adds the invitee")
	expectEq(#viewOf(2).party.members, 3, "every member sees it")
	expectEq(viewOf(4).party, nil, "the solo player is untouched")
	handlers.PartyAction(invitee, "leave")
	expectEq(viewOf(3).party, nil, "the leaver has no party")
	expectEq(#viewOf(1).party.members, 2, "leave updates the party")
	Players:Leave(member)
	expectEq(#viewOf(1).party.members, 1, "a disconnect removes the member")
end)

test("party actions and view requests share the per-player cooldown", function()
	PartyService.REQUEST_COOLDOWN_SECONDS = COOLDOWN
	local fresh = newPlayer(5)
	expect(handlers.PartyAction(fresh, "leave"), "first request")
	local ok, reason = handlers.PartyAction(fresh, "leave")
	expect(not ok and reason == "TooFast", "spam refused")
	local spammer = newPlayer(8)
	local before = fired(8)
	expect(handlers.PartyAction(spammer, "view"), "first view request")
	ok, reason = handlers.PartyAction(spammer, "view")
	expect(not ok and reason == "TooFast", "view spam refused")
	expectEq(fired(8), before + 1, "only one resend")
	PartyService.REQUEST_COOLDOWN_SECONDS = -1
end)

test("only players whose view changed are sent one; no-ops send nothing", function()
	local function snapshot()
		return table.clone(net.fires)
	end
	local function delta(before, userId)
		return fired(userId) - (before[byId[userId]] or 0)
	end
	-- leader (1) leads a party of one; invitee (3), solo (4) and 5 are alone.
	local before = snapshot()
	handlers.PartyAction(solo, "leave")
	handlers.PartyAction(solo, "decline", "no-such-party")
	expectEq(delta(before, 4), 0, "a leave or decline that changes nothing sends nothing")

	before = snapshot()
	handlers.PartyAction(leader, "invite", 4)
	expectEq(delta(before, 1), 1, "the leader sees the invite go out")
	expectEq(delta(before, 4), 1, "the invitee sees the invite")
	expectEq(delta(before, 5), 0, "others hear nothing")
	before = snapshot()
	handlers.PartyAction(solo, "decline", PartyService.PartyIdOf(leader))
	expect(delta(before, 1) == 1 and delta(before, 4) == 1, "a decline reaches the leader and the invitee")
	expectEq(delta(before, 5), 0, "and no one else")

	before = snapshot()
	newPlayer(6)
	expectEq(delta(before, 6), 1, "a joining player gets their first view")
	expectEq(delta(before, 1), 0, "a join changes no one else's view")
end)

test("a client that missed its first view gets it again on request", function()
	local late = newPlayer(7)
	local first = viewOf(7)
	expect(first ~= nil, "the join sends a view")
	-- The client connected its listener too late and lost that view; nothing has
	-- changed since, so only an explicit request sends it again.
	local before = fired(7)
	local ok = handlers.PartyAction(late, "view")
	expect(ok, "the request is accepted")
	expectEq(fired(7), before + 1, "the unchanged view is sent again")
	expectEq(viewOf(7).maxSize, 8, "a full view")
	local others = table.clone(net.fires)
	handlers.PartyAction(late, "view")
	for player, count in others do
		if player ~= late then
			expectEq(net.fires[player], count, "no one else hears a view request")
		end
	end
	-- Later broadcasts still skip the unchanged view.
	before = fired(7)
	handlers.PartyAction(leader, "invite", 5)
	expectEq(fired(7), before, "a change elsewhere does not resend it")
	local bad, reason = handlers.PartyAction(late, "view", "extra")
	expect(not bad and reason == "BadRequest", "a view request takes no argument")
end)
