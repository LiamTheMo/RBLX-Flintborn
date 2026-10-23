-- Lobby parties (GDD Q161c): players group in the lobby and deploy into the same
-- world together. Pure state transitions over a parties table, so the server and
-- specs share one definition. Every function returns (ok, reason?).

local GameConstants = require(script.Parent.Parent.GameConstants)

local PartyRules = {}

PartyRules.MAX_SIZE = GameConstants.MAX_TRIBE_SIZE

export type Party = { id: string, leader: number, members: { number }, invites: { [number]: boolean } }
export type State = { parties: { [string]: Party }, memberOf: { [number]: string } }

function PartyRules.NewState(): State
	return { parties = {}, memberOf = {} }
end

function PartyRules.PartyOf(state: State, userId: number): Party?
	local id = state.memberOf[userId]
	return id and state.parties[id] or nil
end

-- A player with no party leads a party of one.
function PartyRules.Ensure(state: State, userId: number, partyId: string): Party
	local party = PartyRules.PartyOf(state, userId)
	if party then
		return party
	end
	party = { id = partyId, leader = userId, members = { userId }, invites = {} }
	state.parties[partyId] = party
	state.memberOf[userId] = partyId
	return party
end

function PartyRules.Invite(state: State, fromUserId: number, toUserId: number, newPartyId: string)
	if fromUserId == toUserId then
		return false, "CannotInviteSelf"
	end
	local party = PartyRules.Ensure(state, fromUserId, newPartyId)
	if party.leader ~= fromUserId then
		return false, "NotLeader"
	end
	if table.find(party.members, toUserId) then
		return false, "AlreadyMember"
	end
	if #party.members >= PartyRules.MAX_SIZE then
		return false, "PartyFull"
	end
	party.invites[toUserId] = true
	return true, nil
end

function PartyRules.Accept(state: State, userId: number, partyId: string)
	local party = state.parties[partyId]
	if party == nil or not party.invites[userId] then
		return false, "NoInvite"
	end
	if #party.members >= PartyRules.MAX_SIZE then
		return false, "PartyFull"
	end
	PartyRules.Leave(state, userId)
	party.invites[userId] = nil
	table.insert(party.members, userId)
	state.memberOf[userId] = partyId
	return true, nil
end

function PartyRules.Decline(state: State, userId: number, partyId: string)
	local party = state.parties[partyId]
	if party then
		party.invites[userId] = nil
	end
	return true, nil
end

-- Leaving hands leadership to the next member, and an empty party is removed.
function PartyRules.Leave(state: State, userId: number)
	local party = PartyRules.PartyOf(state, userId)
	if party == nil then
		return true, nil
	end
	local index = table.find(party.members, userId)
	if index then
		table.remove(party.members, index)
	end
	state.memberOf[userId] = nil
	if #party.members == 0 then
		state.parties[party.id] = nil
	elseif party.leader == userId then
		party.leader = party.members[1]
	end
	return true, nil
end

-- Clears a player's pending invites everywhere (when they leave the lobby server).
function PartyRules.Forget(state: State, userId: number)
	PartyRules.Leave(state, userId)
	for _, party in state.parties do
		party.invites[userId] = nil
	end
end

return PartyRules
