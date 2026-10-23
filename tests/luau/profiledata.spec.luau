local Shared = game:GetService("ReplicatedStorage").Shared
local ProfileSchema = require(Shared.Data.ProfileSchema)
local Validation = require(Shared.Data.Validation)
local ItemInstance = require(Shared.Data.ItemInstance)
local SessionLease = require(Shared.Data.SessionLease)

test("a missing profile becomes a complete default at the current version", function()
	local profile, problem = ProfileSchema.Migrate(nil, 100)
	expectEq(problem, nil, "no problem")
	expectEq(profile.schemaVersion, ProfileSchema.CURRENT_VERSION, "current version")
	expectEq(profile.profileRevision, 0, "fresh revision")
	expectEq(profile.createdAt, 100, "creation time")
	for _, group in
		{
			"vault",
			"lobbyBackpack",
			"permanentItems",
			"currency",
			"progression",
			"rebirth",
			"recipes",
			"receipts",
			"operations",
			"choices",
			"metrics",
		}
	do
		expect(type(profile[group]) == "table", "has " .. group)
	end
	expectEq(profile.currency.coins, 0, "no coins")
	expectEq(profile.progression.level, 1, "level 1")
	local tracks = 0
	for _ in profile.progression.masteryTracks do
		tracks += 1
	end
	expectEq(tracks, 5, "five mastery tracks")
end)

test("saved values survive reconciliation and missing groups are filled", function()
	local saved = {
		schemaVersion = 1,
		profileRevision = 7,
		currency = { coins = 250 },
		vault = { materials = { Stone = 900 } },
	}
	local profile = ProfileSchema.Migrate(saved, 0)
	expectEq(profile.currency.coins, 250, "coins kept")
	expectEq(profile.currency.gems, 0, "gems filled")
	expectEq(profile.vault.materials.Stone, 900, "stone kept")
	expect(type(profile.vault.items) == "table", "items filled")
	expectEq(profile.profileRevision, 7, "revision kept")
	expectEq(saved.currency.gems, nil, "input not mutated")
end)

test("newer or corrupt data is refused rather than overwritten", function()
	local profile, problem = ProfileSchema.Migrate({ schemaVersion = ProfileSchema.CURRENT_VERSION + 1 }, 0)
	expectEq(profile, nil, "newer schema refused")
	expect(problem ~= nil, "newer schema has a reason")
	profile, problem = ProfileSchema.Migrate({ coins = 5 }, 0)
	expectEq(profile, nil, "corrupt data refused")
	expect(problem ~= nil, "corrupt data has a reason")
end)

test("quantities must be bounded whole numbers", function()
	expect(Validation.IsQuantity(0), "zero")
	expect(Validation.IsQuantity(1000), "1000")
	expect(not Validation.IsQuantity(-1), "negative")
	expect(not Validation.IsQuantity(1.5), "fractional")
	expect(not Validation.IsQuantity(0 / 0), "NaN")
	expect(not Validation.IsQuantity(math.huge), "infinity")
	expect(not Validation.IsQuantity(Validation.MAX_QUANTITY + 1), "too large")
	expect(not Validation.IsQuantity("5"), "string")
	expect(not Validation.IsQuantity(5, 10), "below minimum")
	expect(not Validation.IsQuantity(50, 0, 10), "above maximum")
end)

test("IDs are bounded and URL-safe", function()
	expect(Validation.IsId("0a1b2c3d-4e5f-6789-abcd-ef0123456789"), "GUID")
	expect(Validation.IsId("extract:run_7"), "namespaced")
	expect(not Validation.IsId(""), "empty")
	expect(not Validation.IsId(string.rep("a", 65)), "too long")
	expect(not Validation.IsId("has space"), "spaces")
	expect(not Validation.IsId(42), "number")
end)

test("item instances validate owner, location and the ±5% roll", function()
	local counter = 0
	local function nextId()
		counter += 1
		return "item-" .. counter
	end
	local sword = ItemInstance.New(nextId, "StoneSword", 123, ItemInstance.Locations.Carried, 0.04)
	expectEq(sword.instanceId, "item-1", "server-generated ID")
	expect(ItemInstance.Validate(sword), "valid sword")

	local bad = table.clone(sword)
	bad.qualityRoll = 0.06
	expect(not ItemInstance.Validate(bad), "roll above 5%")
	bad = table.clone(sword)
	bad.location = "Moon"
	expect(not ItemInstance.Validate(bad), "unknown location")
	bad = table.clone(sword)
	bad.ownerId = 0
	expect(not ItemInstance.Validate(bad), "no owner")
	local ok = pcall(ItemInstance.New, nextId, "bad id!", 1, ItemInstance.Locations.Vault)
	expect(not ok, "invalid catalog ID rejected on creation")
end)

test("a lease can be taken when free, own or expired, never from a live owner", function()
	expect(SessionLease.CanAcquire(nil, "job-a", 0), "free")
	local lease = SessionLease.New("job-a", 1000)
	expectEq(lease.expiresAt, 1000 + SessionLease.DURATION_SECONDS, "expiry")
	expect(SessionLease.CanAcquire(lease, "job-a", 1001), "own lease")
	expect(not SessionLease.CanAcquire(lease, "job-b", 1001), "held by another server")
	expect(SessionLease.CanAcquire(lease, "job-b", lease.expiresAt), "expired lease")
	expect(SessionLease.IsHeldBy(lease, "job-a"), "held by a")
	expect(not SessionLease.IsHeldBy(nil, "job-a"), "nil lease held by nobody")
end)
