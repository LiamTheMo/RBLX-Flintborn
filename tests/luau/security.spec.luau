-- One test per GDD §24 abuse case. Many cases are also covered in depth by the
-- feature specs; these pin the security property itself.
local Server = game:GetService("ServerScriptService").Server
local Shared = game:GetService("ReplicatedStorage").Shared
local BossRules = require(Shared.Bosses.BossRules)
local BuildRules = require(Shared.Building.BuildRules)
local DataStoreGateway = require(Server.Infrastructure.DataStoreGateway)
local EconomyRules = require(Shared.Economy.EconomyRules)
local ExtractionRules = require(Shared.Extraction.ExtractionRules)
local ForgeRules = require(Shared.Crafting.ForgeRules)
local InMemoryDataStore = require(Server.Infrastructure.InMemoryDataStore)
local MovementRules = require(Shared.Security.MovementRules)
local OfferCatalog = require(Shared.Economy.OfferCatalog)
local OperationJournal = require(Server.Infrastructure.OperationJournal)
local PermanentRules = require(Shared.Items.PermanentRules)
local ProfileSchema = require(Shared.Data.ProfileSchema)
local ProfileStore = require(Server.Infrastructure.ProfileStore)
local ProgressionRules = require(Shared.Progression.ProgressionRules)
local RemoteGuard = require(Shared.Net.RemoteGuard)
local SessionLease = require(Shared.Data.SessionLease)
local SessionStates = require(Shared.Admission.SessionStates)
local TradeRules = require(Shared.Economy.TradeRules)
local Validation = require(Shared.Data.Validation)

local function forgeReady()
	local profile = ProfileSchema.Default(0)
	profile.metrics.extractions = 2
	profile.recipes.discovered.AncientEmber = true
	profile.vault.materials = { Stone = 999, Wood = 999, Iron = 999, AncientEmber = 9 }
	profile.vault.items = { { instanceId = "p1", catalogId = "BasicPickaxe", ownerId = 7, location = "Vault" } }
	ForgeRules.RefreshUnlocks(profile, 1)
	return profile
end

local function convert(profile, operationId, sourceId)
	return function(working)
		local receipt, reason = ForgeRules.Craft(working, {
			recipeId = "PermanentBasicPickaxe",
			sourceId = sourceId or "p1",
			ownerId = 7,
			operationId = operationId,
			now = 1,
			newId = function()
				return "x"
			end,
		})
		if receipt == nil then
			error(reason, 0)
		end
		return receipt
	end
end

test("§24 forged Permanent IDs are rejected", function()
	local profile = forgeReady()
	local ok, reason =
		pcall(OperationJournal.Run, profile, "forge:a", "Forge", 1, convert(profile, "forge:a", "forged-id"))
	expect(not ok and reason == "NoSource", "unknown instance")
	expect(
		not PermanentRules.CanConvert(
			{ instanceId = "p9", catalogId = "BasicPickaxe", ownerId = 99, location = "Vault" },
			7
		),
		"someone else's item"
	)
end)

test("§24 double Forge requests commit once", function()
	local profile = forgeReady()
	OperationJournal.Run(profile, "forge:a", "Forge", 1, convert(profile, "forge:a"))
	local _, applied = OperationJournal.Run(profile, "forge:a", "Forge", 2, convert(profile, "forge:a"))
	expect(not applied, "the same nonce is a no-op")
	expectEq(profile.vault.materials.Stone, 849, "charged once")
end)

test("§24 simultaneous devices cannot both hold a profile", function()
	local lease = SessionLease.New("serverA", 100)
	expect(not SessionLease.CanAcquire(lease, "serverB", 110), "a second server is refused while the lease is fresh")
	expect(SessionLease.IsHeldBy(lease, "serverA"), "the first keeps it")
end)

test("§24 teleporting mid-operation (pending Deploy) blocks vault-side changes", function()
	local profile = forgeReady()
	profile.transit = { reservationId = "t1", items = {} }
	local ok, reason = pcall(OperationJournal.Run, profile, "forge:b", "Forge", 1, convert(profile, "forge:b"))
	expect(not ok and reason == "InTransit", "nothing converts during transit")
end)

test("§24 death and extraction are mutually exclusive", function()
	expect(not SessionStates.CanTransition("Dead", "ExtractionProtected"), "dead players cannot extract")
	expect(not SessionStates.CanTransition("ExtractionProtected", "Dead"), "protected players cannot die")
	expect(
		not ExtractionRules.Qualifies({ alive = false, downed = false, atRisk = true, inZone = true }),
		"the dead never qualify"
	)
end)

test("§24 Center bonus replays never pay twice", function()
	local profile = ProfileSchema.Default(0)
	ProgressionRules.StartRun(profile, "run1")
	ProgressionRules.GrantXp(profile, 100)
	local function settle(working)
		return ExtractionRules.Settle(working, {}, "Center", "extract:e1", 1)
	end
	OperationJournal.Run(profile, "extract:e1", "Extraction", 1, settle)
	OperationJournal.Run(profile, "extract:e1", "Extraction", 2, settle)
	local level, xp = profile.progression.level, profile.progression.xp
	ExtractionRules.Settle(profile, {}, "Center", "extract:e2", 3)
	expect(profile.progression.level == level and profile.progression.xp == xp, "a second receipt adds nothing")
end)

test("§24 ineligible trades are rejected even if both accept", function()
	local profile = ProfileSchema.Default(0)
	profile.lobbyBackpack.slots = { { catalogId = "Wood", quantity = 100 } }
	expect(not TradeRules.ValidateOffer(profile, { items = { 1 } }, 1), "raw wood")
	expect(not TradeRules.ValidateOffer(profile, { items = {}, coins = 5 }, 1), "Coins")
	expect(not TradeRules.ValidateOffer(profile, { items = {}, gems = -5 }, 1), "negative Gems")
end)

test("§24 an interrupted trade recovers to one outcome", function()
	local a, b = ProfileSchema.Default(0), ProfileSchema.Default(0)
	a.lobbyBackpack.slots = { { instanceId = "s1", catalogId = "IronSword", ownerId = 1 } }
	local bStored = ProfileSchema.DeepCopy(b)
	TradeRules.Settle("t1", { profile = a, userId = 1, offer = { items = { 1 } } }, {
		profile = b,
		userId = 2,
		offer = { items = {} },
	}, 1)
	expectEq(TradeRules.Reconcile(a, "t1", bStored, 2), "RolledBack", "B never saved: A is undone")
	expectEq(#a.lobbyBackpack.slots + #bStored.lobbyBackpack.slots, 1, "exactly one sword exists")
end)

test("§24 a double purchase receipt grants once", function()
	local profile = ProfileSchema.Default(0)
	local function fulfil(working)
		return EconomyRules.Fulfil(working, OfferCatalog.ById.GemPack, 1)
	end
	OperationJournal.Run(profile, "purchase:1", "Purchase", 1, fulfil)
	OperationJournal.Run(profile, "purchase:1", "Purchase", 2, fulfil)
	expectEq(profile.currency.gems, 100, "once")
end)

test("§24 rebirth replays grant tokens once", function()
	local profile = ProfileSchema.Default(0)
	profile.progression.level = 50
	profile.rebirth.legendariesSinceRebirth = 1
	local function rebirth(working)
		local ok, reason = ProgressionRules.Rebirth(working)
		if not ok then
			error(reason, 0)
		end
	end
	OperationJournal.Run(profile, "rebirth:1", "Rebirth", 1, rebirth)
	OperationJournal.Run(profile, "rebirth:1", "Rebirth", 2, rebirth)
	expectEq(profile.rebirth.tokens, 3, "one rebirth's tokens")
	expect(
		not pcall(OperationJournal.Run, profile, "rebirth:2", "Rebirth", 3, rebirth),
		"a fresh nonce fails the requirements"
	)
end)

test("§24 repeated 25% boss crossings release one Legendary", function()
	local released = {}
	local count = 0
	for _, hp in { 6000, 9000, 6100, 5000 } do
		if BossRules.CrossesLegendary(6300, hp, 25000) and BossRules.ReleaseLegendary(released, "enc") then
			count += 1
		end
	end
	expectEq(count, 1, "one Legendary per encounter")
end)

test("§24 negative and fractional quantities are rejected", function()
	expect(not Validation.IsQuantity(-1), "negative")
	expect(not Validation.IsQuantity(1.5), "fractional")
	expect(not Validation.IsQuantity(0 / 0), "NaN")
	expect(not Validation.IsQuantity(math.huge), "infinite")
	local profile = ProfileSchema.Default(0)
	profile.vault.materials.Iron = 10
	expect(not EconomyRules.Sell(profile, "vault", "Iron", -5, "s", 1), "negative sale")
end)

test("§24 DataStore budget exhaustion loses nothing", function()
	local store = InMemoryDataStore.new()
	local gateway = DataStoreGateway.new({ store = store, sleep = function() end, maxAttempts = 3 })
	local profiles = ProfileStore.new({
		gateway = gateway,
		jobId = "s1",
		clock = function()
			return 1
		end,
	})
	local profile = profiles:Load(1)
	profile.currency.coins = 500
	profiles:MarkDirty(1)
	store.failNext = 10
	local ok = profiles:Save(1, false)
	expect(not ok, "the save reports failure")
	expectEq(profiles:Status(1), ProfileStore.SaveState.Pending, "still pending, never 'saved'")
	expectEq(profiles:Get(1).currency.coins, 500, "the live profile keeps its change")
	store.failNext = 0
	expect(profiles:Save(1, false), "a later save succeeds")
end)

test("§24 structures overlapping a portal aura are rejected", function()
	local auras = { { center = Vector3.new(0, 0, 0), radius = BuildRules.AURA_RADIUS } }
	local half = BuildRules.HalfExtents(Vector3.new(8, 8, 1), 0)
	expect(BuildRules.OverlapsAura(Vector3.new(BuildRules.AURA_RADIUS + 2, 0, 0), half, auras), "edge inside")
end)

test("§24 malformed remote arguments and floods are dropped", function()
	expect(RemoteGuard.Check(table.pack(1, "ok", true, nil, { a = 1 })), "plain data passes")
	expect(not RemoteGuard.Check(table.pack(0 / 0)), "NaN")
	expect(not RemoteGuard.Check(table.pack(math.huge)), "infinity")
	expect(not RemoteGuard.Check(table.pack(string.rep("x", 300))), "long string")
	expect(not RemoteGuard.Check(table.pack({ { { 1 } } })), "deep table")
	expect(not RemoteGuard.Check(table.pack(function() end)), "function")
	local huge = {}
	for i = 1, 100 do
		huge[i] = i
	end
	expect(not RemoteGuard.Check(table.pack(huge)), "large table")
	expect(not RemoteGuard.Check(table.pack(1, 2, 3, 4, 5, 6, 7, 8, 9)), "too many arguments")
	local bucket = RemoteGuard.NewBucket(0)
	local accepted = 0
	for _ = 1, 100 do
		if RemoteGuard.Take(bucket, 0) then
			accepted += 1
		end
	end
	expectEq(accepted, RemoteGuard.BURST, "a burst of 40, then throttled")
	expect(RemoteGuard.Take(bucket, 1), "refills over time")
end)

test("§24 impossible movement is caught; sprinting and falling are not", function()
	local from = Vector3.new(0, 50, 0)
	expect(MovementRules.Plausible(from, Vector3.new(6, 0, 0), 0.25, MovementRules.MaxSpeed(false)), "sprint")
	expect(
		MovementRules.Plausible(from, Vector3.new(0, -200, 0) + from, 0.25, MovementRules.MaxSpeed(false)),
		"a long fall"
	)
	expect(not MovementRules.Plausible(from, Vector3.new(80, 50, 0), 0.25, MovementRules.MaxSpeed(false)), "teleport")
	expect(
		not MovementRules.Plausible(from, Vector3.new(12, 50, 0), 0.25, MovementRules.MaxSpeed(true)),
		"downed crawl"
	)
end)
