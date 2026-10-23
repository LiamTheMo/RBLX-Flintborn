-- Protected world main menu and Play admission (GDD §31). Every arrival waits in a
-- loss-free menu state; only an explicit Play that ends in a confirmed spawn puts
-- the player into ActiveRun, which is the only point where items become at risk.
-- World place only.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local SessionStates = require(ReplicatedStorage.Shared.Admission.SessionStates)
local Signal = require(ReplicatedStorage.Shared.Core.Signal)
local Validation = require(ReplicatedStorage.Shared.Data.Validation)
local LoadoutService = require(script.Parent.LoadoutService)
local MatchmakingService = require(script.Parent.MatchmakingService)
local ProfileService = require(script.Parent.ProfileService)
local SpawnService = require(script.Parent.SpawnService)
local TravelService = require(script.Parent.TravelService)

local WorldAdmissionService = {}

WorldAdmissionService.STATE_ATTRIBUTE = "SessionState"
WorldAdmissionService.PROFILE_WAIT_SECONDS = 60
WorldAdmissionService.CHARACTER_WAIT_SECONDS = 15
WorldAdmissionService.DEATH_RETURN_SECONDS = 5

-- Fires (player, runItems) when an at-risk player leaves the world without
-- extracting. v0.07 turns this into a lootable body; until then the run ends.
WorldAdmissionService.ActiveDeparture = Signal.new()

local states = {}
local runItems = {}
local lastPlayRequest = {}

function WorldAdmissionService.GetState(player: Player): string?
	return states[player]
end

function WorldAdmissionService.IsAtRisk(player: Player): boolean
	return SessionStates.IsAtRisk(states[player])
end

-- The items this player carries in the current run.
function WorldAdmissionService.RunItems(player: Player)
	return runItems[player]
end

local function setState(player: Player, state: string)
	local current = states[player]
	if current ~= nil and not SessionStates.CanTransition(current, state) then
		error(("Illegal session transition %s -> %s"):format(current, state))
	end
	states[player] = state
	if player.Parent then
		player:SetAttribute(WorldAdmissionService.STATE_ATTRIBUTE, state)
	end
end

local function sendToLobby(player: Player)
	local ok, err = TravelService.ToLobby({ player })
	if not ok and player.Parent then
		player:Kick("Could not return you to the lobby (" .. tostring(err) .. "). Nothing was lost — please rejoin.")
	end
end

local function livingPositions(except: Player): { Vector3 }
	local positions = {}
	for _, other in Players:GetPlayers() do
		if other ~= except and WorldAdmissionService.IsAtRisk(other) then
			local root = other.Character and other.Character:FindFirstChild("HumanoidRootPart")
			if root then
				table.insert(positions, root.Position)
			end
		end
	end
	return positions
end

local function onDied(player: Player)
	if states[player] ~= SessionStates.ActiveRun and states[player] ~= SessionStates.ExtractionHolding then
		return
	end
	setState(player, SessionStates.Dead)
	-- A dead player may not rejoin this world (GDD Q5) and returns to the lobby.
	MatchmakingService.Exclude(player.UserId)
	runItems[player] = nil
	task.delay(WorldAdmissionService.DEATH_RETURN_SECONDS, function()
		if player.Parent then
			sendToLobby(player)
		end
	end)
end

-- Server side of the Play button. Idempotent: duplicate or late requests never
-- create a second character.
local function requestPlay(player: Player, requestId: any)
	if not Validation.IsId(requestId) then
		return false, "BadRequest"
	end
	local state = states[player]
	if state == SessionStates.ActiveRun then
		return true, nil
	end
	if state ~= SessionStates.WorldMainMenuReady then
		return false, "NotReady"
	end
	if lastPlayRequest[player] == requestId then
		return false, "InProgress"
	end
	lastPlayRequest[player] = requestId
	setState(player, SessionStates.PlayRequested)

	local function fail(reason: string)
		if player.Character then
			player.Character:Destroy()
			player.Character = nil
		end
		if player.Parent and states[player] == SessionStates.PlayRequested then
			setState(player, SessionStates.WorldMainMenuReady)
		end
		return false, reason
	end

	local spawnAt = SpawnService.Pick(livingPositions(player))
	if spawnAt == nil then
		return fail("NoSpawn")
	end
	local loaded = pcall(function()
		player:LoadCharacter()
	end)
	local character = player.Character
	local humanoid = character and character:FindFirstChildOfClass("Humanoid")
	if not loaded or humanoid == nil or not player.Parent then
		return fail("SpawnFailed")
	end
	character:PivotTo(spawnAt)

	-- The spawn is confirmed: consume the reservation and only then enter risk.
	local consumed, items = LoadoutService.Consume(player)
	if not consumed then
		return fail("ReservationFailed")
	end
	runItems[player] = items
	setState(player, SessionStates.ActiveRun)
	humanoid.Died:Connect(function()
		onDied(player)
	end)
	return true, nil
end

-- Menu-only exit back to the lobby. Leaving the run itself needs an extraction.
local function returnToLobby(player: Player)
	if not SessionStates.ShowsWorldMenu(states[player]) or states[player] == SessionStates.PlayRequested then
		return false, "NotInMenu"
	end
	LoadoutService.Rollback(player)
	ProfileService.SaveNow(player)
	setState(player, SessionStates.LobbySafe)
	sendToLobby(player)
	return true, nil
end

local function onPlayerAdded(player: Player)
	local direct = game.PrivateServerId == "" and not RunService:IsStudio()
	if direct or MatchmakingService.IsExcluded(player.UserId) then
		-- Worlds are entered only from the lobby, and never by excluded players.
		sendToLobby(player)
		return
	end
	setState(player, SessionStates.StagingLoading)
	local profile = ProfileService.WaitForProfile(player, WorldAdmissionService.PROFILE_WAIT_SECONDS)
	if profile and player.Parent and states[player] == SessionStates.StagingLoading then
		setState(player, SessionStates.WorldMainMenuReady)
	end
end

function WorldAdmissionService.Init()
	if PlaceConfig.IsWorld() then
		-- Characters exist only after a validated Play (GDD §31.1).
		Players.CharacterAutoLoads = false
	end
end

function WorldAdmissionService.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	Remotes.Get("RequestPlay").OnServerInvoke = requestPlay
	Remotes.Get("ReturnToLobby").OnServerInvoke = returnToLobby
	Players.PlayerAdded:Connect(onPlayerAdded)
	for _, player in Players:GetPlayers() do
		task.spawn(onPlayerAdded, player)
	end
	Players.PlayerRemoving:Connect(function(player)
		if WorldAdmissionService.IsAtRisk(player) then
			-- Any logout during active play forfeits carried items (GDD Q157).
			WorldAdmissionService.ActiveDeparture:Fire(player, runItems[player])
		else
			-- Menu, loading or failed Play: loss-free.
			LoadoutService.Rollback(player)
		end
		states[player] = nil
		runItems[player] = nil
		lastPlayRequest[player] = nil
	end)
end

return WorldAdmissionService
