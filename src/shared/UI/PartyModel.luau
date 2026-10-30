-- Pure rules behind the Party window (docs/ui/PartyScreen.md, ARCHITECTURE §4.4
-- and decisions D3, D5, D6, D18): who is listed and in what order, the counts,
-- the relative "Created" time, the ready tally, who may be invited and how
-- each Invite button reads, and the ready toggle's label. No instances or
-- services, so specs cover it (tests/luau/party_model.spec.luau).
--
-- `view` is LobbyController.PartyView():
--   { party = nil | {id, leader, createdAt, members = {{userId, name, ready}},
--     invited = {userId}}, invites = {{partyId, from}}, ready, maxSize }

local PartyModel = {}

PartyModel.MAX_SIZE = 8
-- Rows the Your Party list shows before it scrolls (D5).
PartyModel.VISIBLE_ROWS = 7
PartyModel.JOIN_TYPE = "Invite Only"
PartyModel.NO_TIME = "—"

export type Member = { userId: number, name: string, leader: boolean, ready: boolean, isSelf: boolean }
export type Candidate = { userId: number, name: string, userName: string?, level: number? }
export type InviteRow = { userId: number, name: string, level: number?, state: string }

local function maxOf(view): number
	return if view and type(view.maxSize) == "number" and view.maxSize > 0 then view.maxSize else PartyModel.MAX_SIZE
end

-- The members to list, the leader first and the rest in joining order. Without
-- a party you are listed alone, as the leader of a party of one, with your own
-- ready flag (a solo player can be ready, D3).
function PartyModel.Members(view, selfId: number, selfName: string): { Member }
	local party = view and view.party
	if party == nil then
		return {
			{
				userId = selfId,
				name = selfName,
				leader = true,
				ready = view ~= nil and view.ready == true,
				isSelf = true,
			},
		}
	end
	local list = {}
	for _, member in party.members or {} do
		local entry = {
			userId = member.userId,
			name = member.name or tostring(member.userId),
			leader = member.userId == party.leader,
			ready = member.ready == true,
			isSelf = member.userId == selfId,
		}
		if entry.leader then
			table.insert(list, 1, entry)
		else
			table.insert(list, entry)
		end
	end
	return list
end

-- "1/8" for the Your Party heading (at least 1: alone you are a party of one).
function PartyModel.CountText(count: number?, maxSize: number?): string
	local cap = maxSize or PartyModel.MAX_SIZE
	return ("%d/%d"):format(math.clamp(count or 1, 1, cap), cap)
end

-- "1 / 8" for the Members detail row.
function PartyModel.MembersText(count: number?, maxSize: number?): string
	local cap = maxSize or PartyModel.MAX_SIZE
	return ("%d / %d"):format(math.clamp(count or 1, 1, cap), cap)
end

-- How many empty slots follow the members (the cap minus the members).
function PartyModel.EmptySlots(count: number, maxSize: number?): number
	return math.max(0, (maxSize or PartyModel.MAX_SIZE) - count)
end

-- The time since `createdAt` (server os.time) at `now` (workspace:
-- GetServerTimeNow()): "Just now" under a minute, then "5 min ago", "2 h ago",
-- "3 d ago". No party (or no time) reads "—"; a clock slightly behind the
-- server reads "Just now", never a negative age.
function PartyModel.RelativeTime(createdAt: number?, now: number?): string
	if type(createdAt) ~= "number" or type(now) ~= "number" then
		return PartyModel.NO_TIME
	end
	local age = math.max(0, now - createdAt)
	if age < 60 then
		return "Just now"
	elseif age < 3600 then
		return ("%d min ago"):format(math.floor(age / 60))
	elseif age < 86400 then
		return ("%d h ago"):format(math.floor(age / 3600))
	end
	return ("%d d ago"):format(math.floor(age / 86400))
end

-- (ready, total) over the listed members.
function PartyModel.ReadyCount(members: { Member }): (number, number)
	local ready = 0
	for _, member in members do
		if member.ready then
			ready += 1
		end
	end
	return ready, #members
end

-- The leader's display name: the leader member's name, or yours when alone.
function PartyModel.LeaderName(members: { Member }): string
	for _, member in members do
		if member.leader then
			return member.name
		end
	end
	return PartyModel.NO_TIME
end

-- Whether you may send invites, as PartyRules.Invite decides: you lead your
-- party or have none, and it is not full. Returns (ok, reason?) with the
-- server's codes ("NotLeader", "PartyFull").
function PartyModel.CanInvite(view, selfId: number): (boolean, string?)
	local party = view and view.party
	if party == nil then
		return true, nil
	end
	if party.leader ~= selfId then
		return false, "NotLeader"
	end
	if #(party.members or {}) >= maxOf(view) then
		return false, "PartyFull"
	end
	return true, nil
end

-- Case-insensitive plain substring match on the display name or user name;
-- an empty query matches everyone.
function PartyModel.Matches(query: string?, displayName: string?, name: string?): boolean
	local q = string.lower(string.gsub(query or "", "^%s*(.-)%s*$", "%1"))
	if q == "" then
		return true
	end
	return string.find(string.lower(displayName or ""), q, 1, true) ~= nil
		or string.find(string.lower(name or ""), q, 1, true) ~= nil
end

-- The Invite Players rows: `candidates` (LobbyController.Invitable(), as
-- {userId, name = DisplayName, userName = Name, level?}) filtered by `query` and
-- sorted by name. Each row's state:
--   "invite"   the button sends an invite
--   "pending"  an invite request is on its way (busy)
--   "invited"  the server lists an unanswered invite to them (D18)
--   "full"     the party is full (disabled)
function PartyModel.InviteRows(
	candidates: { Candidate },
	view,
	selfId: number,
	query: string?,
	pending: { [number]: boolean }?
): { InviteRow }
	local party = view and view.party
	local invited = {}
	for _, userId in party and party.invited or {} do
		invited[userId] = true
	end
	local _, reason = PartyModel.CanInvite(view, selfId)
	local rows = {}
	for _, candidate in candidates do
		if candidate.userId ~= selfId and PartyModel.Matches(query, candidate.name, candidate.userName) then
			local state = "invite"
			if invited[candidate.userId] then
				state = "invited"
			elseif pending and pending[candidate.userId] then
				state = "pending"
			elseif reason == "PartyFull" then
				state = "full"
			end
			table.insert(
				rows,
				{ userId = candidate.userId, name = candidate.name, level = candidate.level, state = state }
			)
		end
	end
	table.sort(rows, function(a, b)
		local la, lb = string.lower(a.name), string.lower(b.name)
		if la ~= lb then
			return la < lb
		end
		return a.userId < b.userId
	end)
	return rows
end

-- The line shown in the invite list when it has no rows.
function PartyModel.InviteNote(view, selfId: number, candidateCount: number, query: string?): string?
	local ok, reason = PartyModel.CanInvite(view, selfId)
	if not ok and reason == "NotLeader" then
		return "Only the party leader can invite players."
	end
	if candidateCount == 0 then
		return "No other players in this lobby."
	end
	if query and string.match(query, "%S") then
		return "No players match your search."
	end
	return nil
end

-- The ready toggle in the Readied Status card (D18): its label, variant and
-- whether it waits for the server. `pending` is the value asked for (nil when
-- nothing is in flight).
function PartyModel.ReadyButton(ready: boolean, pending: boolean?): { label: string, variant: string, busy: boolean }
	local shown = if pending ~= nil then pending else ready
	return {
		label = if shown then "Not Ready" else "Ready",
		variant = if shown then "secondary" else "primary",
		busy = pending ~= nil,
	}
end

-- Whether a pending ready request is answered by `view` (its own flag reached
-- the asked value).
function PartyModel.ReadySettled(view, pending: boolean?): boolean
	return pending == nil or (view ~= nil and (view.ready == true) == pending)
end

-- Leave shows when you are in a party with someone else (ARCHITECTURE §4.4).
function PartyModel.CanLeave(view): boolean
	local party = view and view.party
	return party ~= nil and #(party.members or {}) >= 2
end

export type Options = {
	query: string?,
	now: number?,
	levels: { [number]: number }?,
	pendingInvites: { [number]: boolean }?,
	busyInvites: { [string]: boolean }?,
	readyPending: boolean?,
	leaveBusy: boolean?,
	friends: boolean?,
}

-- Everything the Party window draws (PartyWindow:SetData) from the party view,
-- you ({userId, name}), the players you could invite and the controller's
-- in-flight requests. `levels` maps userId to the Level attribute (missing
-- levels are left out, never guessed); `invites[i].userId` is filled from
-- `fromUserIds[i]` when the controller could tell who sent it.
function PartyModel.WindowData(view, me, candidates: { Candidate }, opts: Options?, fromUserIds: { number? }?)
	opts = opts or {}
	local levels = opts.levels or {}
	local maxSize = maxOf(view)
	local members = PartyModel.Members(view, me.userId, me.name)
	for _, member in members do
		(member :: any).level = levels[member.userId]
	end
	local rows = PartyModel.InviteRows(candidates, view, me.userId, opts.query, opts.pendingInvites)
	for _, row in rows do
		row.level = row.level or levels[row.userId]
	end
	local invites = {}
	for i, invite in view and view.invites or {} do
		local from = fromUserIds and fromUserIds[i]
		table.insert(invites, {
			partyId = invite.partyId,
			from = invite.from,
			userId = from,
			level = from and levels[from] or nil,
			busy = opts.busyInvites ~= nil and opts.busyInvites[invite.partyId] == true,
		})
	end
	local selfReady = view ~= nil and view.ready == true
	local canInvite = PartyModel.CanInvite(view, me.userId)
	local party = view and view.party
	return {
		members = members,
		maxSize = maxSize,
		countText = PartyModel.CountText(#members, maxSize),
		membersText = PartyModel.MembersText(#members, maxSize),
		leaderName = PartyModel.LeaderName(members),
		joinType = PartyModel.JOIN_TYPE,
		createdText = PartyModel.RelativeTime(party and party.createdAt, opts.now),
		selfReady = selfReady,
		readyPending = opts.readyPending,
		readyButton = PartyModel.ReadyButton(selfReady, opts.readyPending),
		inviteRows = rows,
		inviteNote = if #rows == 0 then PartyModel.InviteNote(view, me.userId, #candidates, opts.query) else nil,
		canInvite = canInvite or (party ~= nil and party.leader == me.userId),
		invites = invites,
		canLeave = PartyModel.CanLeave(view),
		leaveBusy = opts.leaveBusy == true,
		friends = opts.friends == true,
	}
end

local REASONS = {
	NotLeader = "Only the party leader can invite players.",
	PartyFull = "The party is full.",
	AlreadyMember = "They are already in your party.",
	CannotInviteSelf = "You cannot invite yourself.",
	NoInvite = "That invite is no longer open.",
	BadRequest = "That request was not valid.",
	RequestFailed = "The server did not answer. Try again.",
}

-- Player-facing text for a party refusal code.
function PartyModel.ReasonText(code: string?): string
	return REASONS[code or "RequestFailed"] or "The party could not be changed right now."
end

return PartyModel
