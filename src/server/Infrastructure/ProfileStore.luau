-- Profile loading and saving with a session lease and revision checks (GDD §22.3,
-- §23.2). Pure apart from the injected gateway and clock, so specs drive it with an
-- in-memory store. ProfileService adds the Roblox lifecycle around it.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local ProfileSchema = require(ReplicatedStorage.Shared.Data.ProfileSchema)
local SessionLease = require(ReplicatedStorage.Shared.Data.SessionLease)

local ProfileStore = {}
ProfileStore.__index = ProfileStore

-- Status values replicated to the owning player.
ProfileStore.SaveState = {
	Loading = "Loading",
	Saved = "Saved",
	Saving = "Saving",
	Pending = "Pending",
	LeaseLost = "LeaseLost",
	Error = "Error",
}

export type Options = {
	gateway: any,
	jobId: string,
	clock: () -> number,
}

function ProfileStore.new(options: Options)
	assert(type(options.jobId) == "string" and options.jobId ~= "", "ProfileStore needs a jobId")
	return setmetatable({
		_gateway = options.gateway,
		_jobId = options.jobId,
		_clock = options.clock,
		_entries = {},
	}, ProfileStore)
end

function ProfileStore.KeyFor(userId: number): string
	return "Profile_" .. tostring(userId)
end

-- Loads and leases a profile. Returns (profile, nil) or (nil, reason) where reason
-- is "LeaseHeld" (another server owns it), a schema problem, or a DataStore error.
function ProfileStore:Load(userId: number)
	assert(self._entries[userId] == nil, "Profile already loaded")
	local now = self._clock()
	local reason = nil
	local ok, stored = self._gateway:Update(ProfileStore.KeyFor(userId), function(old)
		local profile, problem = ProfileSchema.Migrate(old, now)
		if profile == nil then
			reason = problem
			return nil
		end
		if not SessionLease.CanAcquire(profile.sessionLease, self._jobId, now) then
			reason = "LeaseHeld"
			return nil
		end
		profile.sessionLease = SessionLease.New(self._jobId, now)
		profile.profileRevision += 1
		return profile
	end)
	if not ok then
		return nil, "DataStoreError: " .. tostring(stored)
	end
	if stored == nil then
		return nil, reason or "Unknown load failure"
	end
	self._entries[userId] = {
		profile = stored,
		revision = stored.profileRevision,
		status = ProfileStore.SaveState.Saved,
		changes = 0,
		saving = false,
		lost = false,
	}
	return stored, nil
end

-- Reads another player's last saved profile without leasing it (trade recovery).
-- Returns (ok, profileOrNil).
function ProfileStore:ReadStored(userId: number)
	return self._gateway:Read(ProfileStore.KeyFor(userId))
end

function ProfileStore:Get(userId: number)
	local entry = self._entries[userId]
	return entry and not entry.lost and entry.profile or nil
end

function ProfileStore:Status(userId: number): string?
	local entry = self._entries[userId]
	return entry and entry.status or nil
end

function ProfileStore:IsSaving(userId: number): boolean
	local entry = self._entries[userId]
	return entry ~= nil and entry.saving
end

-- Records that the live profile changed and needs saving.
function ProfileStore:MarkDirty(userId: number)
	local entry = self._entries[userId]
	if entry and not entry.lost then
		entry.changes += 1
		entry.status = ProfileStore.SaveState.Pending
	end
end

-- Writes the live profile if this server still holds the lease and nobody else has
-- written since it loaded. `release` clears the lease and forgets the profile.
-- Returns (true) or (false, reason); a failed write keeps the profile pending.
function ProfileStore:Save(userId: number, release: boolean?)
	local entry = self._entries[userId]
	if entry == nil then
		return false, "NotLoaded"
	end
	if entry.lost then
		return false, "LeaseLost"
	end
	assert(not entry.saving, "Save already in progress")
	entry.saving = true
	entry.status = ProfileStore.SaveState.Saving

	local now = self._clock()
	local snapshotChanges = entry.changes
	local payload = ProfileSchema.DeepCopy(entry.profile)
	local reason = nil
	local ok, stored = self._gateway:Update(ProfileStore.KeyFor(userId), function(old)
		if old == nil then
			reason = "Missing"
			return nil
		end
		if not SessionLease.IsHeldBy(old.sessionLease, self._jobId) then
			reason = "LeaseLost"
			return nil
		end
		if old.profileRevision ~= entry.revision then
			reason = "StaleRevision"
			return nil
		end
		payload.profileRevision = entry.revision + 1
		payload.sessionLease = if release then nil else SessionLease.New(self._jobId, now)
		return payload
	end)
	entry.saving = false

	if not ok then
		entry.status = ProfileStore.SaveState.Pending
		return false, "DataStoreError: " .. tostring(stored)
	end
	if stored == nil then
		-- Another server owns or has rewritten this profile: stop writing at once.
		entry.lost = true
		entry.status = ProfileStore.SaveState.LeaseLost
		return false, reason or "Unknown save failure"
	end

	entry.revision = stored.profileRevision
	entry.profile.profileRevision = stored.profileRevision
	entry.profile.sessionLease = stored.sessionLease
	if release then
		self._entries[userId] = nil
	elseif entry.changes == snapshotChanges then
		entry.status = ProfileStore.SaveState.Saved
	else
		entry.status = ProfileStore.SaveState.Pending
	end
	return true, nil
end

-- Forgets a profile without writing (used after a lost lease).
function ProfileStore:Forget(userId: number)
	self._entries[userId] = nil
end

function ProfileStore:LoadedUserIds(): { number }
	local ids = {}
	for userId in self._entries do
		table.insert(ids, userId)
	end
	return ids
end

return ProfileStore
