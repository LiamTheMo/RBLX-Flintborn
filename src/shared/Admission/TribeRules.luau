-- In-world tribes (GDD §5.2, Q39, Q161c): up to 8 members with a leader who can
-- invite and kick, and mutual alliances between tribes. A lobby party arrives as one
-- tribe. Pure state transitions; every function returns (ok, reason?).

local GameConstants = require(script.Parent.Parent.GameConstants)

local TribeRules = {}

TribeRules.MAX_SIZE = GameConstants.MAX_TRIBE_SIZE

function TribeRules.NewState()
	return { tribes = {}, memberOf = {}, allianceRequests = {} }
end

function TribeRules.TribeOf(state, userId: number)
	local id = state.memberOf[userId]
	return id and state.tribes[id] or nil
end

function TribeRules.Create(state, userId: number, tribeId: string)
	if state.memberOf[userId] then
		return false, "AlreadyInTribe"
	end
	if state.tribes[tribeId] then
		return false, "TribeExists"
	end
	state.tribes[tribeId] = { id = tribeId, leader = userId, members = { userId }, invites = {}, allies = {} }
	state.memberOf[userId] = tribeId
	return true, nil
end

-- Joins an existing tribe directly (lobby party arrival) or creates it.
function TribeRules.JoinOrCreate(state, userId: number, tribeId: string)
	local tribe = state.tribes[tribeId]
	if tribe == nil then
		return TribeRules.Create(state, userId, tribeId)
	end
	if state.memberOf[userId] == tribeId then
		return true, nil
	end
	if state.memberOf[userId] then
		return false, "AlreadyInTribe"
	end
	if #tribe.members >= TribeRules.MAX_SIZE then
		return false, "TribeFull"
	end
	table.insert(tribe.members, userId)
	state.memberOf[userId] = tribeId
	return true, nil
end

function TribeRules.Invite(state, leaderId: number, userId: number)
	local tribe = TribeRules.TribeOf(state, leaderId)
	if tribe == nil then
		return false, "NoTribe"
	end
	if tribe.leader ~= leaderId then
		return false, "NotLeader"
	end
	if state.memberOf[userId] then
		return false, "AlreadyInTribe"
	end
	if #tribe.members >= TribeRules.MAX_SIZE then
		return false, "TribeFull"
	end
	tribe.invites[userId] = true
	return true, nil
end

function TribeRules.Accept(state, userId: number, tribeId: string)
	local tribe = state.tribes[tribeId]
	if tribe == nil or not tribe.invites[userId] then
		return false, "NoInvite"
	end
	if state.memberOf[userId] then
		return false, "AlreadyInTribe"
	end
	if #tribe.members >= TribeRules.MAX_SIZE then
		return false, "TribeFull"
	end
	tribe.invites[userId] = nil
	table.insert(tribe.members, userId)
	state.memberOf[userId] = tribeId
	return true, nil
end

local function remove(state, tribe, userId: number)
	local index = table.find(tribe.members, userId)
	if index then
		table.remove(tribe.members, index)
	end
	state.memberOf[userId] = nil
	if #tribe.members == 0 then
		for allyId in tribe.allies do
			local ally = state.tribes[allyId]
			if ally then
				ally.allies[tribe.id] = nil
			end
		end
		state.tribes[tribe.id] = nil
	elseif tribe.leader == userId then
		tribe.leader = tribe.members[1]
	end
end

function TribeRules.Leave(state, userId: number)
	local tribe = TribeRules.TribeOf(state, userId)
	if tribe then
		remove(state, tribe, userId)
	end
	return true, nil
end

function TribeRules.Kick(state, leaderId: number, userId: number)
	local tribe = TribeRules.TribeOf(state, leaderId)
	if tribe == nil or tribe.leader ~= leaderId then
		return false, "NotLeader"
	end
	if leaderId == userId or state.memberOf[userId] ~= tribe.id then
		return false, "NotMember"
	end
	remove(state, tribe, userId)
	return true, nil
end

-- Alliances need both leaders: the first request records intent, the second makes it mutual.
function TribeRules.Ally(state, leaderId: number, otherTribeId: string)
	local tribe = TribeRules.TribeOf(state, leaderId)
	local other = state.tribes[otherTribeId]
	if tribe == nil or tribe.leader ~= leaderId then
		return false, "NotLeader"
	end
	if other == nil or other.id == tribe.id then
		return false, "NoSuchTribe"
	end
	local key = other.id .. ">" .. tribe.id
	if state.allianceRequests[key] then
		state.allianceRequests[key] = nil
		tribe.allies[other.id] = true
		other.allies[tribe.id] = true
		return true, "Allied"
	end
	state.allianceRequests[tribe.id .. ">" .. other.id] = true
	return true, "Requested"
end

return TribeRules
