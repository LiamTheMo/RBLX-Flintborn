-- Lobby parties (GDD Q161c): players group in the lobby and deploy into the same
-- world together. Pure state transitions over a parties table, so the server and
-- specs share one definition. Every function returns (ok, reason?).

local GameConstants = require(script.Parent.Parent.GameConstants)

local PartyRules = {}

PartyRules.MAX_SIZE = GameConstants.MAX_TRIBE_SIZE

export type Party = {
	id: string,
	leader: number,
	members: { number },
	invites: { [number]: boolean },
	createdAt: number?,
}
export type State = { parties: { [string]: Party }, memberOf: { [number]: string } }

function PartyRules.NewState(): State
	return { parties = {}, memberOf = {} }
end

function PartyRules.PartyOf(state: State, userId: number): Party?
	local id = state.memberOf[userId]
	return id and state.parties[id] or nil
end

-- Leader's invites still waiting for an answer, as sorted user ids.
function PartyRules.PendingInvites(party: Party): { number }
	local userIds = {}
	for userId in party.invites do
		table.insert(userIds, userId)
	end
	table.sort(userIds)
	return userIds
end

-- A player with no party leads a party of one, created at `now` (the caller's
-- clock, so this module stays pure).
function PartyRules.Ensure(state: State, userId: number, partyId: string, now: number?): Party
	local party = PartyRules.PartyOf(state, userId)
	if party then
		return party
	end
	party = { id = partyId, leader = userId, members = { userId }, invites = {}, createdAt = now }
	state.parties[partyId] = party
	state.memberOf[userId] = partyId
	return party
end

function PartyRules.Invite(state: State, fromUserId: number, toUserId: number, newPartyId: string, now: number?)
	if fromUserId == toUserId then
		return false, "CannotInviteSelf"
	end
	local party = PartyRules.Ensure(state, fromUserId, newPartyId, now)
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

-- A deploy's party record (GDD Q161c). Invitees see a party's id, so the id alone
-- never makes anyone a member in a world: the lobby writes who actually deployed
-- under a fresh server token, and the world only trusts that record.
PartyRules.DEPLOY_RECORD_SECONDS = 3600

-- Lobby party ids and deploy tokens are server GUIDs.
function PartyRules.IsGuid(value: any): boolean
	return type(value) == "string"
		and string.match(value, "^%x%x%x%x%x%x%x%x%-%x%x%x%x%-%x%x%x%x%-%x%x%x%x%-%x%x%x%x%x%x%x%x%x%x%x%x$") ~= nil
end

function PartyRules.DeployRecord(partyId: string, userIds: { number }, worldId: string?, now: number)
	return { partyId = partyId, members = table.clone(userIds), worldId = worldId, at = now }
end

-- The party `userId` deployed with into world `worldId`, or nil (solo) unless a
-- fresh, well-formed record for that world lists them.
function PartyRules.VerifiedPartyId(record: any, userId: number, worldId: string?, now: number): string?
	if type(record) ~= "table" or not PartyRules.IsGuid(record.partyId) or type(record.members) ~= "table" then
		return nil
	end
	if type(record.at) ~= "number" or now - record.at > PartyRules.DEPLOY_RECORD_SECONDS then
		return nil
	end
	if record.worldId ~= nil and record.worldId ~= worldId then
		return nil
	end
	if table.find(record.members, userId) == nil then
		return nil
	end
	return record.partyId
end

-- Takes a player out of their party and clears their pending invites everywhere
-- (when they leave the lobby server).
function PartyRules.Forget(state: State, userId: number)
	PartyRules.Leave(state, userId)
	for _, party in state.parties do
		party.invites[userId] = nil
	end
end

return PartyRules
