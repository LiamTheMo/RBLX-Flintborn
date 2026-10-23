-- Versioned player profile (GDD §23.2). The default shape, the current schema
-- version and pure migrations from every older version live here so the server,
-- client and headless specs agree on one definition.

local GameConstants = require(script.Parent.Parent.GameConstants)

local ProfileSchema = {}

ProfileSchema.CURRENT_VERSION = 1

local function deepCopy(value)
	if type(value) ~= "table" then
		return value
	end
	local copy = {}
	for key, child in value do
		copy[key] = deepCopy(child)
	end
	return copy
end
ProfileSchema.DeepCopy = deepCopy

local function defaultMasteries()
	local tracks = {}
	for _, track in GameConstants.MASTERY_TRACKS do
		tracks[track] = { level = 0, counters = {} }
	end
	return tracks
end

-- A brand-new profile. Groups filled by later phases start empty.
function ProfileSchema.Default(now: number?)
	return {
		schemaVersion = ProfileSchema.CURRENT_VERSION,
		profileRevision = 0,
		sessionLease = nil,
		lastCommittedOperationId = nil,
		createdAt = now or 0,

		vault = { materials = {}, items = {}, upgradeTier = 0 },
		lobbyBackpack = { slots = {} },
		transit = nil,
		permanentItems = {},
		currency = { coins = 0, gems = 0 },
		progression = {
			level = 1,
			xp = 0,
			masteryTracks = defaultMasteries(),
			titles = {},
			appliedMilestones = {},
			currentRun = nil,
		},
		rebirth = { count = 0, tokens = 0, ownedPerks = {}, legendariesSinceRebirth = 0 },
		boosters = { xpUntil = 0 },
		recipes = { unlocked = {}, discovered = {} },
		receipts = { extraction = {}, forge = {}, maintenance = {}, crashRecovery = {} },
		operations = { records = {}, order = {} },
		choices = { camera = {}, hotbarBindings = {} },
		metrics = { runs = 0, extractions = 0, deaths = 0 },
	}
end

-- Fills keys missing from `data` with defaults without overwriting saved values.
-- Only tables that exist in the default are descended into, so saved maps keyed
-- by item or operation IDs are never pruned.
local function reconcile(data, defaults)
	for key, default in defaults do
		local current = data[key]
		if current == nil then
			data[key] = deepCopy(default)
		elseif type(current) == "table" and type(default) == "table" then
			reconcile(current, default)
		end
	end
end

-- Pure migrations: MIGRATIONS[n] upgrades a version-n profile to version n + 1.
local MIGRATIONS: { [number]: (any) -> any } = {}

-- Returns an up-to-date profile, or nil and a reason when the data cannot be loaded
-- safely. Data from a NEWER schema is refused so an old server never overwrites it.
function ProfileSchema.Migrate(data: any, now: number?)
	if data == nil then
		return ProfileSchema.Default(now), nil
	end
	if type(data) ~= "table" or type(data.schemaVersion) ~= "number" then
		return nil, "Corrupt profile: missing schemaVersion"
	end
	if data.schemaVersion > ProfileSchema.CURRENT_VERSION then
		return nil, "Profile schema " .. data.schemaVersion .. " is newer than this server"
	end
	local profile = deepCopy(data)
	while profile.schemaVersion < ProfileSchema.CURRENT_VERSION do
		local step = MIGRATIONS[profile.schemaVersion]
		if step == nil then
			return nil, "No migration from schema " .. profile.schemaVersion
		end
		profile = step(profile)
		profile.schemaVersion += 1
	end
	reconcile(profile, ProfileSchema.Default(profile.createdAt))
	return profile, nil
end

return ProfileSchema
