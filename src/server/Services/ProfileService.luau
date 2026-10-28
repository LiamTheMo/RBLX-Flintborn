-- Loads, autosaves and releases player profiles (GDD §23.1). Other services read
-- profiles through GetProfile/WaitForProfile and change them only through
-- RunOperation, which makes every grant or charge exactly-once. The lobby
-- backpack may hold materials: they deploy like any other item (GDD §53).

local DataStoreService = game:GetService("DataStoreService")
local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Signal = require(ReplicatedStorage.Shared.Core.Signal)

local DataStoreGateway = require(script.Parent.Parent.Infrastructure.DataStoreGateway)
local InMemoryDataStore = require(script.Parent.Parent.Infrastructure.InMemoryDataStore)
local OperationJournal = require(script.Parent.Parent.Infrastructure.OperationJournal)
local ProfileStore = require(script.Parent.Parent.Infrastructure.ProfileStore)

local ProfileService = {}

ProfileService.STORE_NAME = "PlayerProfiles_v1"
ProfileService.STATUS_ATTRIBUTE = "SaveStatus"
ProfileService.AUTOSAVE_SECONDS = 60
ProfileService.SAVE_AFTER_CHANGE_SECONDS = 3
ProfileService.LOAD_ATTEMPTS = 10
ProfileService.LOAD_RETRY_SECONDS = 3
ProfileService.SHUTDOWN_BUDGET_SECONDS = 25

-- Fires (player, profile) once a player's profile is loaded and leased here.
ProfileService.ProfileLoaded = Signal.new()
-- Fires once at graceful shutdown, before profiles are released, so held items can
-- be written to profiles first. Handlers run to completion before releases start.
ProfileService.BeforeShutdown = Signal.new()
-- Fires (player) synchronously when a player leaves, before their release save
-- snapshots the profile, so departure changes (Permanent items kept, transit
-- rollback, escrow) are always part of the final write (GDD §29, §31.4).
ProfileService.BeforeRelease = Signal.new()

local store
local scheduledSaves = {}
local shuttingDown = false
local usingMemoryStore = false

local function setStatus(player: Player?)
	if player and player.Parent then
		local status = store:Status(player.UserId)
		if status then
			player:SetAttribute(ProfileService.STATUS_ATTRIBUTE, status)
		end
	end
end

local function waitForSaveSlot(userId: number)
	while store:IsSaving(userId) do
		task.wait(0.1)
	end
end

-- Saves one cached profile. `player` is nil when the player already left (a release
-- that failed earlier is retried this way until it succeeds).
local function saveUser(userId: number, release: boolean?, player: Player?)
	waitForSaveSlot(userId)
	if store:Status(userId) == nil then
		return false, "NotLoaded"
	end
	local ok, reason = store:Save(userId, release)
	if not ok then
		warn(("[ProfileService] Save for %d failed: %s"):format(userId, tostring(reason)))
		if reason == "LeaseLost" or reason == "StaleRevision" then
			-- Another server now owns this profile; never write again from here.
			store:Forget(userId)
			if player and player.Parent then
				player:Kick("Your Flintborn data was opened on another server. Please rejoin.")
			end
		end
	end
	setStatus(player)
	return ok, reason
end

local function save(player: Player, release: boolean?)
	return saveUser(player.UserId, release, player)
end

local function scheduleSave(player: Player)
	if scheduledSaves[player] then
		return
	end
	scheduledSaves[player] = true
	task.delay(ProfileService.SAVE_AFTER_CHANGE_SECONDS, function()
		scheduledSaves[player] = nil
		if player.Parent then
			save(player, false)
		end
	end)
end

local function createGateway()
	local studioProbe = nil
	local opened, dataStore = pcall(function()
		return DataStoreService:GetDataStore(ProfileService.STORE_NAME)
	end)
	if not opened and not RunService:IsStudio() then
		error("[ProfileService] Could not open the profile DataStore: " .. tostring(dataStore))
	end
	if not opened then
		-- Unpublished Studio places cannot even open a DataStore.
		studioProbe = dataStore
	elseif RunService:IsStudio() then
		-- Studio without "Enable Studio Access to API Services" cannot reach DataStores.
		local ok, err = pcall(function()
			return dataStore:GetAsync("__probe")
		end)
		if not ok then
			studioProbe = err
		end
	end
	if studioProbe then
		warn(
			"[ProfileService] DataStores unavailable in Studio ("
				.. tostring(studioProbe)
				.. "); using an in-memory store. Data will not persist."
		)
		usingMemoryStore = true
		return DataStoreGateway.new({ store = InMemoryDataStore.new() })
	end
	return DataStoreGateway.new({
		store = dataStore,
		waitForBudget = function()
			while DataStoreService:GetRequestBudgetForRequestType(Enum.DataStoreRequestType.UpdateAsync) < 1 do
				task.wait(1)
			end
		end,
	})
end

local function loadPlayer(player: Player)
	local userId = player.UserId
	-- Rejoined while this server is still writing their release: wait for that
	-- write, then look again (a finished release forgot the profile).
	waitForSaveSlot(userId)
	if not player.Parent then
		return
	end
	local cached = store:Get(userId)
	if cached ~= nil then
		-- An earlier release failed: this server still holds the newest copy and its
		-- lease, so keep using it.
		setStatus(player)
		ProfileService.ProfileLoaded:Fire(player, cached)
		return
	end
	if store:Status(userId) ~= nil then
		-- Lost its lease while the player was away: never reuse that copy.
		store:Forget(userId)
	end
	player:SetAttribute(ProfileService.STATUS_ATTRIBUTE, ProfileStore.SaveState.Loading)
	local lastReason = nil
	for _ = 1, ProfileService.LOAD_ATTEMPTS do
		if not player.Parent then
			return
		end
		local profile, reason = store:Load(userId)
		if profile then
			if not player.Parent then
				-- Left while loading: hand the lease straight back.
				saveUser(userId, true, nil)
				return
			end
			setStatus(player)
			ProfileService.ProfileLoaded:Fire(player, profile)
			return
		end
		lastReason = reason
		if reason ~= "LeaseHeld" then
			break
		end
		task.wait(ProfileService.LOAD_RETRY_SECONDS)
	end
	warn(("[ProfileService] Could not load profile %d: %s"):format(userId, tostring(lastReason)))
	if player.Parent then
		player:SetAttribute(ProfileService.STATUS_ATTRIBUTE, ProfileStore.SaveState.Error)
		local message = if lastReason == "LeaseHeld"
			then "Your Flintborn data is still in use by another server. Nothing was lost — please rejoin in a minute."
			else "Flintborn could not load your data safely. Nothing was lost — please rejoin."
		player:Kick(message)
	end
end

function ProfileService.Init()
	local jobId = game.JobId
	if jobId == "" then
		jobId = "studio-" .. HttpService:GenerateGUID(false)
	end
	store = ProfileStore.new({ gateway = createGateway(), jobId = jobId, clock = os.time })
end

function ProfileService.Start()
	Players.PlayerAdded:Connect(loadPlayer)
	for _, player in Players:GetPlayers() do
		-- Deferred so services that start after this one connect to ProfileLoaded first.
		task.defer(loadPlayer, player)
	end

	Players.PlayerRemoving:Connect(function(player)
		scheduledSaves[player] = nil
		local ok, err = pcall(function()
			ProfileService.BeforeRelease:Fire(player)
		end)
		if not ok then
			warn("[ProfileService] BeforeRelease handler failed: " .. tostring(err))
		end
		save(player, true)
	end)

	-- Autosave every cached profile, which also renews its lease. Profiles whose
	-- player already left are released (retrying a release that failed earlier).
	task.spawn(function()
		while true do
			task.wait(ProfileService.AUTOSAVE_SECONDS)
			for _, userId in store:LoadedUserIds() do
				local player = Players:GetPlayerByUserId(userId)
				task.spawn(saveUser, userId, player == nil, player)
			end
		end
	end)

	game:BindToClose(function()
		shuttingDown = true
		local ok, err = pcall(function()
			ProfileService.BeforeShutdown:Fire()
		end)
		if not ok then
			warn("[ProfileService] BeforeShutdown handler failed: " .. tostring(err))
		end
		local remaining = 0
		for _, userId in store:LoadedUserIds() do
			remaining += 1
			task.spawn(function()
				saveUser(userId, true, Players:GetPlayerByUserId(userId))
				remaining -= 1
			end)
		end
		local deadline = os.clock() + ProfileService.SHUTDOWN_BUDGET_SECONDS
		while remaining > 0 and os.clock() < deadline do
			task.wait(0.1)
		end
	end)
end

-- The live profile, or nil while loading or after it was released.
function ProfileService.GetProfile(player: Player)
	return store and store:Get(player.UserId) or nil
end

function ProfileService.WaitForProfile(player: Player, timeoutSeconds: number?)
	local deadline = os.clock() + (timeoutSeconds or 30)
	while player.Parent and os.clock() < deadline do
		local profile = ProfileService.GetProfile(player)
		if profile then
			return profile
		end
		task.wait(0.1)
	end
	return nil
end

-- Applies `apply(profile)` exactly once for `operationId`, then schedules a save.
-- Returns (ok, result, applied). An error inside `apply` changes nothing.
function ProfileService.RunOperation(player: Player, operationId: string, kind: string, apply: (any) -> any)
	local profile = ProfileService.GetProfile(player)
	if profile == nil then
		return false, "ProfileNotLoaded", false
	end
	local ok, result, applied = pcall(OperationJournal.Run, profile, operationId, kind, os.time(), apply)
	if not ok then
		return false, result, false
	end
	if applied then
		store:MarkDirty(player.UserId)
		setStatus(player)
		scheduleSave(player)
	end
	return true, result, applied
end

-- Applies a small, naturally idempotent change in place (XP and mastery grants
-- from server-verified actions) and schedules a save, without a journal entry.
-- Returns false when the profile is not loaded.
function ProfileService.Mutate(player: Player, apply: (any) -> ())
	local profile = ProfileService.GetProfile(player)
	if profile == nil then
		return false
	end
	apply(profile)
	store:MarkDirty(player.UserId)
	setStatus(player)
	scheduleSave(player)
	return true
end

-- Another player's last saved profile, read without a lease. Returns (ok, data).
function ProfileService.ReadStored(userId: number)
	return store:ReadStored(userId)
end

function ProfileService.SaveNow(player: Player)
	return save(player, false)
end

-- True once a graceful shutdown began: removals from now on are not logouts.
function ProfileService.IsShuttingDown(): boolean
	return shuttingDown
end

-- True when profiles live only in server memory (Studio without API access).
function ProfileService.IsUsingMemoryStore(): boolean
	return usingMemoryStore
end

-- True when every change to this user's profile has been written (or it was
-- released). Run checkpoints are deleted only after their ending is saved.
function ProfileService.IsSaved(userId: number): boolean
	local status = store and store:Status(userId)
	return status == nil or status == ProfileStore.SaveState.Saved
end

return ProfileService
