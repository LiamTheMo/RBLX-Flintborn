-- Lobby parties (GDD Q161c): invite, accept, decline and leave, up to 8 players,
-- so a group deploys into the same world. Lobby place only.

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local PartyRules = require(ReplicatedStorage.Shared.Admission.PartyRules)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)

local PartyService = {}

PartyService.REQUEST_COOLDOWN_SECONDS = 0.25

local state = PartyRules.NewState()
local lastRequest = {}

local function newPartyId()
	return HttpService:GenerateGUID(false)
end

-- What one player sees: their party and the invites waiting for them.
local function viewFor(player: Player)
	local view = { party = nil, invites = {} }
	local party = PartyRules.PartyOf(state, player.UserId)
	if party then
		local members = {}
		for _, userId in party.members do
			local member = Players:GetPlayerByUserId(userId)
			table.insert(members, { userId = userId, name = member and member.DisplayName or tostring(userId) })
		end
		view.party = { id = party.id, leader = party.leader, members = members }
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
		ok, reason = PartyRules.Invite(state, player.UserId, argument, newPartyId())
	elseif action == "accept" and type(argument) == "string" then
		ok, reason = PartyRules.Accept(state, player.UserId, argument)
	elseif action == "decline" and type(argument) == "string" then
		ok, reason = PartyRules.Decline(state, player.UserId, argument)
	elseif action == "leave" then
		ok, reason = PartyRules.Leave(state, player.UserId)
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
	Remotes.Get("PartyAction").OnServerInvoke = handle
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
