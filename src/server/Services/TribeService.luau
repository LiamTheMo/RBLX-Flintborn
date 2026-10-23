-- In-world tribes (GDD §5.2, Q39, Q161c): create, invite, accept, leave, kick and
-- mutual alliances, up to 8 members. A lobby party arrives as one tribe. Tribe IDs
-- always start with "tribe:" so they never collide with BuildingService's
-- "solo:<userId>" owner keys, and they never leave the server: clients (and the
-- TribeId attribute combat uses to block friendly fire) only ever see a separate
-- random handle per tribe. A party tribe is joined only on a party the lobby
-- recorded this player deploying with (PartyService.VerifiedPartyId), never on
-- anything a client can put in TeleportData. World only.

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local TribeRules = require(ReplicatedStorage.Shared.Admission.TribeRules)
local Validation = require(ReplicatedStorage.Shared.Data.Validation)
local PartyService = require(script.Parent.PartyService)
local WorldAdmissionService = require(script.Parent.WorldAdmissionService)

local TribeService = {}

TribeService.REQUEST_COOLDOWN_SECONDS = 0.25
TribeService.PREFIX = "tribe:"
TribeService.PARTY_PREFIX = "tribe:party:"

local state = TribeRules.NewState()
local lastRequest = {}
-- Internal tribe id <-> the public handle clients see.
local handleOf = {}
local idOfHandle = {}
-- Each player's verified lobby party id, or false when they arrived solo.
local partyOf = {}
local lookingUp = {}

local function handleFor(id: string): string
	local handle = handleOf[id]
	if handle == nil then
		handle = HttpService:GenerateGUID(false)
		handleOf[id] = handle
		idOfHandle[handle] = id
	end
	return handle
end

-- The internal id behind a client-supplied handle, if it names a live tribe.
local function idFromHandle(handle: any): string?
	local id = Validation.IsId(handle) and idOfHandle[handle] or nil
	return if id and state.tribes[id] then id else nil
end

-- Drops handles of tribes that no longer exist.
local function pruneHandles()
	for id, handle in handleOf do
		if state.tribes[id] == nil then
			handleOf[id] = nil
			idOfHandle[handle] = nil
		end
	end
end

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
			local ally = state.tribes[allyId]
			table.insert(allies, ally and nameOf(ally.leader) or "?")
		end
		view.tribe = { id = handleFor(tribe.id), leader = tribe.leader, members = members, allies = allies }
	end
	-- Other tribes appear by leader name and size; `tribeId` is only their public
	-- handle, which is what accept and ally take.
	for id, other in state.tribes do
		if other.invites[player.UserId] then
			table.insert(view.invites, { tribeId = handleFor(id), from = nameOf(other.leader) })
		end
		if tribe == nil or other.id ~= tribe.id then
			table.insert(view.others, { tribeId = handleFor(id), leader = nameOf(other.leader), size = #other.members })
		end
	end
	return view
end

local function broadcast()
	pruneHandles()
	local changed = Remotes.Get("TribeChanged")
	for _, player in Players:GetPlayers() do
		local id = state.memberOf[player.UserId]
		player:SetAttribute("TribeId", id and handleFor(id) or nil)
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
		ok, reason = TribeRules.Create(state, player.UserId, TribeService.PREFIX .. HttpService:GenerateGUID(false))
	elseif action == "invite" and type(argument) == "number" then
		if Players:GetPlayerByUserId(argument) == nil then
			return false, "PlayerNotHere"
		end
		ok, reason = TribeRules.Invite(state, player.UserId, argument)
	elseif action == "accept" and Validation.IsId(argument) then
		ok, reason = TribeRules.Accept(state, player.UserId, idFromHandle(argument) or "")
	elseif action == "leave" then
		ok, reason = TribeRules.Leave(state, player.UserId)
	elseif action == "kick" and type(argument) == "number" then
		ok, reason = TribeRules.Kick(state, player.UserId, argument)
	elseif action == "ally" and Validation.IsId(argument) then
		ok, reason = TribeRules.Ally(state, player.UserId, idFromHandle(argument) or "")
	else
		return false, "BadRequest"
	end
	broadcast()
	return ok, reason
end

-- A lobby party deploys together and starts as one tribe once its run begins.
local function joinPartyTribe(player: Player)
	local partyId = partyOf[player]
	if partyId and state.memberOf[player.UserId] == nil and WorldAdmissionService.IsAtRisk(player) then
		-- Party tribes live in their own namespace, never an in-world tribe or a
		-- "solo:" key.
		TribeRules.JoinOrCreate(state, player.UserId, TribeService.PARTY_PREFIX .. partyId)
		broadcast()
	end
end

-- Verifies the player's lobby party once per visit (a MemoryStore read, started on
-- arrival so it is usually done before Play), then joins if the run has begun.
local function lookUpParty(player: Player)
	if partyOf[player] ~= nil or lookingUp[player] then
		return
	end
	lookingUp[player] = true
	local partyId = PartyService.VerifiedPartyId(player)
	lookingUp[player] = nil
	if player.Parent == nil then
		return
	end
	partyOf[player] = partyId or false
	joinPartyTribe(player)
end

function TribeService.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	Remotes.Handle("TribeAction", handle)
	WorldAdmissionService.RunStarted:Connect(function(player)
		if partyOf[player] == nil then
			task.spawn(lookUpParty, player)
		else
			joinPartyTribe(player)
		end
	end)
	Players.PlayerAdded:Connect(function(player)
		task.spawn(lookUpParty, player)
		broadcast()
	end)
	Players.PlayerRemoving:Connect(function(player)
		partyOf[player] = nil
		lookingUp[player] = nil
		TribeRules.Leave(state, player.UserId)
		for _, tribe in state.tribes do
			tribe.invites[player.UserId] = nil
		end
		lastRequest[player] = nil
		broadcast()
	end)
end

return TribeService
