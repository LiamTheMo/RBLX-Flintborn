-- Lobby Deploy flow (GDD §2.1, §31.4, Q155): the party leader deploys the party;
-- each member's unvaulted items move into a saved transit reservation, a world is
-- chosen and everyone teleports together. Any failure rolls every reservation back.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local SessionStates = require(ReplicatedStorage.Shared.Admission.SessionStates)
local TransitRules = require(ReplicatedStorage.Shared.Admission.TransitRules)
local LoadoutService = require(script.Parent.LoadoutService)
local MatchmakingService = require(script.Parent.MatchmakingService)
local PartyService = require(script.Parent.PartyService)
local ProfileService = require(script.Parent.ProfileService)
local TravelService = require(script.Parent.TravelService)

local DeployService = {}

DeployService.STATE_ATTRIBUTE = "SessionState"

local deploying = {}

local function setState(player: Player, state: string)
	player:SetAttribute(DeployService.STATE_ATTRIBUTE, state)
end

local function rollbackAll(group: { Player })
	for _, member in group do
		LoadoutService.Rollback(member)
		if member.Parent then
			setState(member, SessionStates.LobbySafe)
		end
		deploying[member] = nil
	end
end

local function deploy(player: Player)
	local group, reason = PartyService.DeployGroup(player)
	if group == nil then
		return false, reason
	end
	for _, member in group do
		if deploying[member] then
			return false, "AlreadyDeploying"
		end
		if ProfileService.GetProfile(member) == nil then
			return false, member.DisplayName .. "'s data is still loading"
		end
	end
	for _, member in group do
		deploying[member] = true
		setState(member, SessionStates.TeleportPending)
	end
	local reservations = {}
	local userIds = {}
	for _, member in group do
		local reservationId, problem = LoadoutService.Reserve(member)
		if reservationId == nil then
			rollbackAll(group)
			return false, problem
		end
		reservations[tostring(member.UserId)] = reservationId
		table.insert(userIds, member.UserId)
	end

	local world, problem = MatchmakingService.FindWorld(userIds)
	if world == nil then
		rollbackAll(group)
		return false, problem
	end
	-- Only a token travels: the world checks it against the server-written record,
	-- so editing teleport data cannot join anyone to a party they are not in.
	local partyToken = PartyService.RecordDeploy(player, group, world.privateServerId)
	local teleportData = { reservations = reservations, partyToken = partyToken }
	local ok, err = TravelService.ToWorld(group, world.accessCode, teleportData)
	if not ok then
		rollbackAll(group)
		return false, err
	end
	return true, nil
end

function DeployService.Start()
	if not PlaceConfig.IsLobby() then
		return
	end
	Players.PlayerAdded:Connect(function(player)
		setState(player, SessionStates.LobbySafe)
	end)
	for _, player in Players:GetPlayers() do
		setState(player, SessionStates.LobbySafe)
	end
	Players.PlayerRemoving:Connect(function(player)
		deploying[player] = nil
	end)
	-- A teleport that fails after starting leaves the player here: they are safe again.
	TravelService.TeleportFailed:Connect(function(player)
		deploying[player] = nil
		if player.Parent then
			setState(player, SessionStates.LobbySafe)
		end
	end)

	Remotes.Handle("Deploy", deploy)
	Remotes.Handle("DeployPreview", function(player)
		local items = {}
		for _, item in LoadoutService.Preview(player) do
			if TransitRules.Deployable(item) then
				table.insert(
					items,
					{ catalogId = item.catalogId, quantity = item.quantity, permanent = item.permanent }
				)
			end
		end
		return items
	end)
end

return DeployService
