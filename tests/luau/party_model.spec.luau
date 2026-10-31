local Shared = game:GetService("ReplicatedStorage").Shared
local PartyModel = require(Shared.UI.PartyModel)

local function partyView(members, leader, extra)
	local view = {
		party = { id = "p1", leader = leader, createdAt = 1000, members = members, invited = {} },
		invites = {},
		ready = false,
		maxSize = 8,
	}
	for key, value in extra or {} do
		view.party[key] = value
	end
	return view
end

test("alone you are listed as the leader of a party of one", function()
	local view = { party = nil, invites = {}, ready = true, maxSize = 8 }
	local members = PartyModel.Members(view, 1, "LiamTheMo")
	expectEq(#members, 1, "one row")
	expectEq(members[1].name, "LiamTheMo", "your name")
	expect(members[1].leader, "leads")
	expect(members[1].ready, "your own ready flag counts when solo")
	expect(members[1].isSelf, "marked as you")
	expectEq(PartyModel.LeaderName(members), "LiamTheMo", "leader name")
end)

test("the leader is listed first, then members in joining order", function()
	local view = partyView({
		{ userId = 2, name = "ForestRanger", ready = true },
		{ userId = 1, name = "LiamTheMo", ready = false },
		{ userId = 3, name = "SunnyVale" },
	}, 1)
	local members = PartyModel.Members(view, 3, "SunnyVale")
	expectEq(members[1].userId, 1, "leader first")
	expectEq(members[2].userId, 2, "then the first joiner")
	expectEq(members[3].userId, 3, "then the next")
	expect(members[3].isSelf, "you are marked")
	expect(not members[1].isSelf, "others are not")
	expect(members[2].ready and not members[3].ready, "ready flags carried, missing is false")
	local ready, total = PartyModel.ReadyCount(members)
	expectEq(ready, 1, "one ready")
	expectEq(total, 3, "of three")
end)

test("counts read n/8 and n / 8 within the cap", function()
	expectEq(PartyModel.CountText(1, 8), "1/8", "heading")
	expectEq(PartyModel.CountText(nil, 8), "1/8", "alone")
	expectEq(PartyModel.CountText(9, 8), "8/8", "clamped")
	expectEq(PartyModel.MembersText(3, 8), "3 / 8", "detail row")
	expectEq(PartyModel.EmptySlots(1, 8), 7, "seven free")
	expectEq(PartyModel.EmptySlots(8, 8), 0, "full")
	expectEq(PartyModel.EmptySlots(9, 8), 0, "never negative")
end)

test("created time reads relative to the server clock", function()
	expectEq(PartyModel.RelativeTime(1000, 1000), "Just now", "same second")
	expectEq(PartyModel.RelativeTime(1000, 1059.9), "Just now", "under a minute")
	expectEq(PartyModel.RelativeTime(1000, 1060), "1 min ago", "one minute")
	expectEq(PartyModel.RelativeTime(1000, 1000 + 5 * 60 + 30), "5 min ago", "minutes round down")
	expectEq(PartyModel.RelativeTime(1000, 1000 + 3599), "59 min ago", "just under an hour")
	expectEq(PartyModel.RelativeTime(1000, 1000 + 2 * 3600 + 100), "2 h ago", "hours")
	expectEq(PartyModel.RelativeTime(1000, 1000 + 3 * 86400), "3 d ago", "days")
	expectEq(PartyModel.RelativeTime(1000, 990), "Just now", "a clock behind the server is not negative")
	expectEq(PartyModel.RelativeTime(nil, 1000), "—", "no party")
	expectEq(PartyModel.RelativeTime(1000, nil), "—", "no clock")
end)

test("only the leader or a solo player may invite, and not into a full party", function()
	expect(PartyModel.CanInvite({ party = nil, maxSize = 8 }, 1), "solo")
	expect(PartyModel.CanInvite(partyView({ { userId = 1, name = "A" } }, 1), 1), "leader")
	local ok, reason = PartyModel.CanInvite(partyView({ { userId = 1 }, { userId = 2 } }, 1), 2)
	expect(not ok, "member")
	expectEq(reason, "NotLeader", "member reason")
	local full = {}
	for i = 1, 8 do
		table.insert(full, { userId = i, name = "P" .. i })
	end
	ok, reason = PartyModel.CanInvite(partyView(full, 1), 1)
	expect(not ok, "full")
	expectEq(reason, "PartyFull", "full reason")
end)

test("search matches display or user name, case-insensitively and literally", function()
	expect(PartyModel.Matches("", "ForestRanger", "fr_01"), "empty query")
	expect(PartyModel.Matches("  ", "ForestRanger", "fr_01"), "blank query")
	expect(PartyModel.Matches("forest", "ForestRanger", "fr_01"), "display name")
	expect(PartyModel.Matches("FR_", "ForestRanger", "fr_01"), "user name")
	expect(not PartyModel.Matches("sunny", "ForestRanger", "fr_01"), "no match")
	expect(not PartyModel.Matches("(", "ForestRanger", "fr_01"), "patterns are literal")
	expect(PartyModel.Matches("e.r", "Rang.e.r", nil), "dots are literal too")
end)

test("invite rows are filtered, sorted and carry their button state", function()
	local candidates = {
		{ userId = 3, name = "SunnyVale", userName = "sunny", level = 8 },
		{ userId = 2, name = "ForestRanger", userName = "forest", level = 15 },
		{ userId = 4, name = "ashfall", userName = "ash" },
		{ userId = 1, name = "LiamTheMo" },
	}
	local view = partyView({ { userId = 1, name = "LiamTheMo" } }, 1, { invited = { 3 } })
	local rows = PartyModel.InviteRows(candidates, view, 1, "", { [4] = true })
	expectEq(#rows, 3, "you are never listed")
	expectEq(rows[1].name, "ashfall", "sorted by name, ignoring case")
	expectEq(rows[1].state, "pending", "a request in flight")
	expectEq(rows[2].name, "ForestRanger", "second")
	expectEq(rows[2].state, "invite", "can invite")
	expectEq(rows[2].level, 15, "level carried")
	expectEq(rows[3].state, "invited", "the server lists the invite")
	rows = PartyModel.InviteRows(candidates, view, 1, "sun")
	expectEq(#rows, 1, "filtered")
	expectEq(rows[1].userId, 3, "the match")
	local full = {}
	for i = 1, 8 do
		table.insert(full, { userId = 10 + i, name = "P" .. i })
	end
	full[1].userId = 1
	rows = PartyModel.InviteRows(candidates, partyView(full, 1), 1, "")
	expectEq(rows[1].state, "full", "a full party disables invites")
end)

test("the invite list explains why it is empty", function()
	local member = partyView({ { userId = 1 }, { userId = 2 } }, 1)
	expectEq(PartyModel.InviteNote(member, 2, 0, ""), "Only the party leader can invite players.", "member")
	expectEq(PartyModel.InviteNote({ party = nil }, 1, 0, ""), "No other players in this lobby.", "alone")
	expectEq(PartyModel.InviteNote({ party = nil }, 1, 3, "zz"), "No players match your search.", "no match")
	expectEq(PartyModel.InviteNote({ party = nil }, 1, 3, ""), nil, "nothing to explain")
end)

test("the ready toggle reads the next action and waits for the server", function()
	local b = PartyModel.ReadyButton(false, nil)
	expectEq(b.label, "Ready", "not ready offers Ready")
	expectEq(b.variant, "primary", "leather")
	expect(not b.busy, "idle")
	b = PartyModel.ReadyButton(true, nil)
	expectEq(b.label, "Not Ready", "ready offers Not Ready")
	expectEq(b.variant, "secondary", "paper")
	b = PartyModel.ReadyButton(false, true)
	expectEq(b.label, "Not Ready", "shows the asked state while pending")
	expect(b.busy, "busy while pending")
	expect(PartyModel.ReadySettled({ ready = true }, true), "settled when the view agrees")
	expect(not PartyModel.ReadySettled({ ready = false }, true), "still pending")
	expect(PartyModel.ReadySettled({ ready = false }, nil), "nothing pending")
end)

test("leave shows only in a party with someone else", function()
	expect(not PartyModel.CanLeave({ party = nil }), "solo")
	expect(not PartyModel.CanLeave(partyView({ { userId = 1 } }, 1)), "party of one")
	expect(PartyModel.CanLeave(partyView({ { userId = 1 }, { userId = 2 } }, 1)), "two")
end)

test("refusal codes read as sentences", function()
	expectEq(PartyModel.ReasonText("PartyFull"), "The party is full.", "full")
	expect(#PartyModel.ReasonText(nil) > 0, "unknown failure")
	expect(#PartyModel.ReasonText("Weird") > 0, "unlisted code")
end)
