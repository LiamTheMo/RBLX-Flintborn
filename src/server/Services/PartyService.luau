-- Lobby parties (GDD Q161c): invite, accept, decline and leave, up to 8 players,
-- so a group deploys into the same world, where it starts as one tribe. Invitees
-- see a party's id, so a deploy also writes who actually went to a short-lived
-- MemoryStore record under a fresh token; the world trusts only that record and
-- treats anything it cannot verify as solo. Party state is lobby only. Each player
-- also has an advisory Ready flag ("ready", bool); solo players can set it too,
-- and it never blocks a deploy.

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local PartyRules = require(ReplicatedStorage.Shared.Admission.PartyRules)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)

local PartyService = {}

PartyService.REQUEST_COOLDOWN_SECONDS = 0.25
PartyService.MAP_NAME = "FlintbornPartyDeploys"
PartyService.STORE_ATTEMPTS = 2

local state = PartyRules.NewState()
local lastRequest = {}
local deployMap = nil

local function newPartyId()
	return HttpService:GenerateGUID(false)
end

-- What one player sees: their party (members with their ready flags, when it was
-- created, and for the leader only the invites still pending), the invites waiting
-- for them, their own ready flag (solo players can be ready) and the size cap.
-- Nothing about players outside their party is included beyond who invited them.
local function viewFor(player: Player)
	local view = {
		party = nil,
		invites = {},
		ready = PartyRules.IsReady(state, player.UserId),
		maxSize = PartyRules.MAX_SIZE,
	}
	local party = PartyRules.PartyOf(state, player.UserId)
	if party then
		local members = {}
		for _, userId in party.members do
			local member = Players:GetPlayerByUserId(userId)
			table.insert(members, {
				userId = userId,
				name = member and member.DisplayName or tostring(userId),
				ready = PartyRules.IsReady(state, userId),
			})
		end
		view.party = {
			id = party.id,
			leader = party.leader,
			members = members,
			createdAt = party.createdAt,
			invited = if party.leader == player.UserId then PartyRules.PendingInvites(party) else {},
		}
	end
	for id, other in state.parties do
		if other.invites[player.UserId] then
			local leader = Players:GetPlayerByUserId(other.leader)
			table.insert(view.invites, { partyId = id, from = leader and leader.DisplayName or tostring(other.leader) })
		end
	end
	return view
end

local function broadcast()
	local changed = Remotes.Get("PartyChanged")
	for _, player in Players:GetPlayers() do
		changed:FireClient(player, viewFor(player))
	end
end

-- Clears the ready flag of everyone in `group` (a deploy is starting) and tells
-- every client.
function PartyService.ClearReady(group: { Player })
	local userIds = {}
	for _, member in group do
		table.insert(userIds, member.UserId)
	end
	PartyRules.ClearReady(state, userIds)
	broadcast()
end

-- The party ID a deploy carries into the world, where the party becomes a tribe.
function PartyService.PartyIdOf(player: Player): string?
	local party = PartyRules.PartyOf(state, player.UserId)
	return party and party.id or nil
end

-- The shared deploy-record map, or false where MemoryStore is unavailable.
local function records()
	if deployMap == nil then
		local ok, map = pcall(function()
			return game:GetService("MemoryStoreService"):GetHashMap(PartyService.MAP_NAME)
		end)
		deployMap = ok and map or false
	end
	return deployMap
end

-- Runs a MemoryStore call, retrying once. Returns (ok, result).
local function tryStore(call)
	local ok, result = false, nil
	for attempt = 1, PartyService.STORE_ATTEMPTS do
		ok, result = pcall(call)
		if ok then
			return true, result
		end
		if attempt < PartyService.STORE_ATTEMPTS then
			task.wait(attempt)
		end
	end
	warn("[PartyService] Deploy record unavailable: " .. tostring(result))
	return false, nil
end

-- Lobby: records who deploys with `leader`'s party into `worldId` and returns the
-- token their teleport data carries, or nil when they have no party or the record
-- could not be written (they then arrive solo; the deploy itself goes ahead).
function PartyService.RecordDeploy(leader: Player, group: { Player }, worldId: string?): string?
	local party = PartyRules.PartyOf(state, leader.UserId)
	local map = records()
	if party == nil or not map then
		return nil
	end
	local userIds = {}
	for _, member in group do
		table.insert(userIds, member.UserId)
	end
	local token = HttpService:GenerateGUID(false)
	local record = PartyRules.DeployRecord(party.id, userIds, worldId, os.time())
	local ok = tryStore(function()
		map:SetAsync(token, record, PartyRules.DEPLOY_RECORD_SECONDS)
	end)
	return if ok then token else nil
end

-- World: the lobby party `player` verifiably deployed with into this world, or
-- nil (solo). Yields for the MemoryStore read.
function PartyService.VerifiedPartyId(player: Player): string?
	local joinData = player:GetJoinData()
	local data = joinData and joinData.TeleportData
	local token = type(data) == "table" and data.partyToken or nil
	local map = records()
	if not PartyRules.IsGuid(token) or not map then
		return nil
	end
	local ok, record = tryStore(function()
		return map:GetAsync(token)
	end)
	if not ok then
		return nil
	end
	return PartyRules.VerifiedPartyId(record, player.UserId, game.PrivateServerId, os.time())
end

-- Members who deploy with `player`: the whole party when they lead it, just them
-- when they have no party. Returns (players) or (nil, reason).
function PartyService.DeployGroup(player: Player)
	local party = PartyRules.PartyOf(state, player.UserId)
	if party == nil then
		return { player }
	end
	if party.leader ~= player.UserId then
		return nil, "OnlyLeaderDeploys"
	end
	local group = {}
	for _, userId in party.members do
		local member = Players:GetPlayerByUserId(userId)
		if member then
			table.insert(group, member)
		end
	end
	return group
end

local function handle(player: Player, action: any, argument: any)
	local now = os.clock()
	if lastRequest[player] and now - lastRequest[player] < PartyService.REQUEST_COOLDOWN_SECONDS then
		return false, "TooFast"
	end
	lastRequest[player] = now
	local ok, reason
	if action == "invite" and type(argument) == "number" then
		if Players:GetPlayerByUserId(argument) == nil then
			return false, "PlayerNotHere"
		end
		ok, reason = PartyRules.Invite(state, player.UserId, argument, newPartyId(), os.time())
	elseif action == "accept" and type(argument) == "string" then
		ok, reason = PartyRules.Accept(state, player.UserId, argument)
	elseif action == "decline" and type(argument) == "string" then
		ok, reason = PartyRules.Decline(state, player.UserId, argument)
	elseif action == "leave" then
		ok, reason = PartyRules.Leave(state, player.UserId)
	elseif action == "ready" and type(argument) == "boolean" then
		ok, reason = PartyRules.SetReady(state, player.UserId, argument)
	else
		return false, "BadRequest"
	end
	broadcast()
	return ok, reason
end

function PartyService.Start()
	if not PlaceConfig.IsLobby() then
		return
	end
	Remotes.Handle("PartyAction", handle)
	Players.PlayerAdded:Connect(function()
		broadcast()
	end)
	Players.PlayerRemoving:Connect(function(player)
		PartyRules.Forget(state, player.UserId)
		lastRequest[player] = nil
		broadcast()
	end)
end

return PartyService
