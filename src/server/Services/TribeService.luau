-- In-world tribes (GDD §5.2, Q39, Q161c): create, invite, accept, leave, kick and
-- mutual alliances, up to 8 members. A lobby party arrives as one tribe. Members
-- carry a TribeId attribute that combat uses to block friendly fire. World only.

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local TribeRules = require(ReplicatedStorage.Shared.Admission.TribeRules)
local Validation = require(ReplicatedStorage.Shared.Data.Validation)
local WorldAdmissionService = require(script.Parent.WorldAdmissionService)

local TribeService = {}

TribeService.REQUEST_COOLDOWN_SECONDS = 0.25

local state = TribeRules.NewState()
local lastRequest = {}

function TribeService.TribeIdOf(player: Player): string?
	return state.memberOf[player.UserId]
end

function TribeService.InTribe(player: Player): boolean
	return state.memberOf[player.UserId] ~= nil
end

local function nameOf(userId: number): string
	local player = Players:GetPlayerByUserId(userId)
	return player and player.DisplayName or tostring(userId)
end

local function viewFor(player: Player)
	local view = { tribe = nil, invites = {}, others = {} }
	local tribe = TribeRules.TribeOf(state, player.UserId)
	if tribe then
		local members = {}
		for _, userId in tribe.members do
			table.insert(members, { userId = userId, name = nameOf(userId) })
		end
		local allies = {}
		for allyId in tribe.allies do
			table.insert(allies, allyId)
		end
		view.tribe = { id = tribe.id, leader = tribe.leader, members = members, allies = allies }
	end
	for id, other in state.tribes do
		if other.invites[player.UserId] then
			table.insert(view.invites, { tribeId = id, from = nameOf(other.leader) })
		end
		if tribe == nil or other.id ~= tribe.id then
			table.insert(view.others, { tribeId = id, leader = nameOf(other.leader), size = #other.members })
		end
	end
	return view
end

local function broadcast()
	local changed = Remotes.Get("TribeChanged")
	for _, player in Players:GetPlayers() do
		player:SetAttribute("TribeId", state.memberOf[player.UserId])
		changed:FireClient(player, viewFor(player))
	end
end

local function handle(player: Player, action: any, argument: any)
	local now = os.clock()
	if lastRequest[player] and now - lastRequest[player] < TribeService.REQUEST_COOLDOWN_SECONDS then
		return false, "TooFast"
	end
	lastRequest[player] = now
	local ok, reason
	if action == "create" then
		ok, reason = TribeRules.Create(state, player.UserId, HttpService:GenerateGUID(false))
	elseif action == "invite" and type(argument) == "number" then
		if Players:GetPlayerByUserId(argument) == nil then
			return false, "PlayerNotHere"
		end
		ok, reason = TribeRules.Invite(state, player.UserId, argument)
	elseif action == "accept" and Validation.IsId(argument) then
		ok, reason = TribeRules.Accept(state, player.UserId, argument)
	elseif action == "leave" then
		ok, reason = TribeRules.Leave(state, player.UserId)
	elseif action == "kick" and type(argument) == "number" then
		ok, reason = TribeRules.Kick(state, player.UserId, argument)
	elseif action == "ally" and Validation.IsId(argument) then
		ok, reason = TribeRules.Ally(state, player.UserId, argument)
	else
		return false, "BadRequest"
	end
	broadcast()
	return ok, reason
end

-- A lobby party deploys together and starts as one tribe.
local function joinPartyTribe(player: Player)
	local joinData = player:GetJoinData()
	local data = joinData and joinData.TeleportData
	local partyId = type(data) == "table" and data.partyId
	if Validation.IsId(partyId) and state.memberOf[player.UserId] == nil then
		TribeRules.JoinOrCreate(state, player.UserId, partyId)
		broadcast()
	end
end

function TribeService.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	Remotes.Get("TribeAction").OnServerInvoke = handle
	WorldAdmissionService.RunStarted:Connect(joinPartyTribe)
	Players.PlayerAdded:Connect(broadcast)
	Players.PlayerRemoving:Connect(function(player)
		TribeRules.Leave(state, player.UserId)
		for _, tribe in state.tribes do
			tribe.invites[player.UserId] = nil
		end
		lastRequest[player] = nil
		broadcast()
	end)
end

return TribeService
