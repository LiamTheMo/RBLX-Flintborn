-- Versioned player profile (GDD §23.2). The default shape, the current schema
-- version and pure migrations from every older version live here so the server,
-- client and headless specs agree on one definition.

local BoostRules = require(script.Parent.Parent.Survival.BoostRules)
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
		currency = {
			coins = 0,
			gems = 0,
			gemTradeDay = 0,
			gemsTradedToday = 0,
			gemReceiveDay = 0,
			gemsReceivedToday = 0,
			npcSaleReceipts = {},
			purchaseEntitlements = {},
			redeemedCodes = {},
		},
		quests = { progress = {} },
		trades = { pending = {}, history = {} },
		progression = {
			level = 1,
			xp = 0,
			masteryTracks = defaultMasteries(),
			titles = {},
			appliedMilestones = {},
			currentRun = nil,
			pvpCredits = {},
		},
		rebirth = { count = 0, tokens = 0, ownedPerks = {}, legendariesSinceRebirth = 0 },
		-- `paused`: consumable boosts saved at extraction with their remaining
		-- seconds ({kind, amount, remaining}), resumed on the next deploy (GDD §53).
		boosters = { xpUntil = 0, paused = {} },
		recipes = { unlocked = {}, discovered = {} },
		receipts = { extraction = {}, forge = {}, maintenance = {}, crashRecovery = {} },
		operations = { records = {}, order = {} },
		choices = {
			camera = {},
			hotbarBindings = {},
			-- Keyboard rebinds that differ from the defaults (Keybinds, GDD §46).
			keybinds = {},
			uiScale = 1,
			colourBlindMode = false,
			reducedMotion = false,
			subtitles = true,
		},
		tutorial = { step = 1, skipped = false, everSkipped = false, completedAt = nil, rewardsGranted = {} },
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

-- Codes redeemed before the permanent ledger existed are recorded only in the
-- operation journal, which trims old entries: copy them into the ledger so a
-- trimmed journal never makes a code redeemable again. Safe on every load, since
-- only committed redemptions are journalled.
local function backfillRedeemedCodes(profile)
	local redeemed = profile.currency.redeemedCodes
	for operationId, record in profile.operations.records do
		if
			type(operationId) == "string"
			and string.sub(operationId, 1, 5) == "code:"
			and type(record) == "table"
			and record.kind == "CodeRedeem"
			and record.status == "committed"
		then
			redeemed[string.sub(operationId, 6)] = true
		end
	end
end

-- Pre-release catalog cleanup (GDD §51, ITEM_CATALOG §8): the items the catalog
-- retired are deleted wherever the profile holds them. Only this explicit list is
-- deleted, never "anything this server doesn't know": an older server still
-- running after a publish would otherwise delete items a newer build added.
-- Running it on every load is safe.
ProfileSchema.RETIRED_ITEMS = {
	Iron = true,
	Arrow = true,
	Sickle = true,
	BasicPickaxe = true,
	BasicBow = true,
	Berries = true,
	WoodHead = true,
	WoodChest = true,
	WoodLegs = true,
	StoneHead = true,
	StoneChest = true,
	StoneLegs = true,
}

local function known(catalogId: any): boolean
	return type(catalogId) == "string" and not ProfileSchema.RETIRED_ITEMS[catalogId]
end

-- Removes unknown records from a list in place. Returns how many were removed.
local function pruneList(list: any): number
	if type(list) ~= "table" then
		return 0
	end
	local removed = 0
	for index = #list, 1, -1 do
		local item = list[index]
		if type(item) ~= "table" or not known(item.catalogId) then
			table.remove(list, index)
			removed += 1
		end
	end
	return removed
end

-- Removes unknown keys from a {[catalogId] = value} map in place.
local function pruneMap(map: any): number
	if type(map) ~= "table" then
		return 0
	end
	local removed = 0
	for catalogId in table.clone(map) do
		if not known(catalogId) then
			map[catalogId] = nil
			removed += 1
		end
	end
	return removed
end

-- Deletes every reference to a retired item, and the Forge conversions of retired
-- items. Returns how many entries were removed (0 when the profile is clean).
function ProfileSchema.PruneRetiredItems(profile): number
	local removed = 0
	removed += pruneList(profile.lobbyBackpack.slots)
	removed += pruneList(profile.vault.items)
	removed += pruneMap(profile.vault.materials)
	local overflow = profile.vault.lastOverflow
	if type(overflow) == "table" then
		removed += pruneMap(overflow.deleted)
	end
	if type(profile.transit) == "table" then
		removed += pruneList(profile.transit.items)
	end
	for _, receipt in profile.receipts.maintenance do
		if type(receipt) == "table" then
			removed += pruneList(receipt.items)
		end
	end
	for _, receipt in profile.receipts.extraction do
		if type(receipt) == "table" then
			removed += pruneMap(receipt.vaulted) + pruneMap(receipt.toBackpack) + pruneMap(receipt.deleted)
			removed += pruneMap(receipt.carriedIn)
		end
	end
	for receiptId, receipt in table.clone(profile.receipts.forge) do
		local output = type(receipt) == "table" and receipt.output
		if type(output) == "table" and not known(output.catalogId) then
			profile.receipts.forge[receiptId] = nil
			removed += 1
		end
	end
	-- The loadout a run recorded at Play, restored if its server crashes, and the
	-- material quantities it carried in (GDD §53).
	local run = profile.progression.currentRun
	if type(run) == "table" then
		removed += pruneList(run.loadout)
		if type(run.loadout) == "table" and #run.loadout == 0 then
			run.loadout = nil
		end
		removed += pruneMap(run.carriedIn)
	end
	-- A trade awaiting reconciliation never hands back or claws back a removed item.
	for _, pending in profile.trades.pending do
		for _, side in { pending.gave, pending.received } do
			if type(side) == "table" then
				removed += pruneList(side.items) + pruneMap(side.materials)
			end
		end
	end
	for instanceId, entry in table.clone(profile.permanentItems) do
		if type(entry) ~= "table" or not known(entry.catalogId) then
			profile.permanentItems[instanceId] = nil
			removed += 1
		end
	end
	removed += pruneMap(profile.recipes.discovered)
	for recipeId in table.clone(profile.recipes.unlocked) do
		local source = string.match(recipeId, "^Permanent(.+)$")
		if source and not known(source) then
			profile.recipes.unlocked[recipeId] = nil
			removed += 1
		end
	end
	return removed
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
	profile.boosters.paused = BoostRules.Sanitize(profile.boosters.paused)
	backfillRedeemedCodes(profile)
	ProfileSchema.PruneRetiredItems(profile)
	return profile, nil
end

return ProfileSchema
