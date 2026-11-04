-- Follow-up review of crash recovery and trade settlement: a new run racing an
-- unrecovered crash checkpoint, a restore racing a new run's checkpoint, a crash
-- between the Play's consume save and its first checkpoint, and spending while a
-- trade can still roll back. Drives the real server services against fake Roblox
-- services, a DataStore and a MemoryStore with latency and a fake clock.

local Shared = game:GetService("ReplicatedStorage").Shared
local Server = game:GetService("ServerScriptService").Server

local world = require(game:GetService("ServerStorage").TestSupport.WorldServer).new({
	jobId = "job-followup",
	privateServerId = "world-followup",
	memoryStore = true,
	start = {
		"CrashRecoveryService",
		"InventoryService",
		"LoadoutService",
		"ProfileService",
		"RunCheckpointService",
		"WorldAdmissionService",
	},
})
local advance, join, play, stored, stacks = world.advance, world.join, world.play, world.stored, world.stacks
local started = world.started

local CrashRecoveryRules = require(Server.Rules.Recovery.CrashRecoveryRules)
local EconomyRules = require(Server.Rules.Economy.EconomyRules)
local ForgeRules = require(Server.Rules.Crafting.ForgeRules)
local ProfileSchema = require(Server.Rules.Data.ProfileSchema)
local TradeRules = require(Server.Rules.Economy.TradeRules)
local TransitRules = require(Server.Rules.Admission.TransitRules)
local CheckpointStore = require(Server.Infrastructure.CheckpointStore)
local CrashRecoveryService = require(Server.Services.CrashRecoveryService)
local LoadoutService = require(Server.Services.LoadoutService)
local WorldAdmissionService = require(Server.Services.WorldAdmissionService)

local memory = world.memory
local checkpoints = memory.maps.FlintbornRunCheckpoints
local beats = memory.maps.FlintbornServerHeartbeats

-- A profile whose last run, on another server, was never settled.
local function crashedRun(profile, runId: string, jobId: string)
	profile.progression.currentRun = { runId = runId, general = 0, mastery = {}, settled = false, jobId = jobId }
	return profile
end

local function hasInstance(slots, instanceId: string): number
	local count = 0
	for _, item in slots do
		if item.instanceId == instanceId then
			count += 1
		end
	end
	return count
end

-- Issue 1: a new run racing an unrecovered crash checkpoint ------------------------

test("a crashed run's checkpoint is never overwritten: Play waits until it is restored", function()
	local profile, reservationId = world.transit(301, stacks("new301", 2))
	crashedRun(profile, "run-301", "dead-301")
	checkpoints["301"] = CrashRecoveryRules.Checkpoint("run-301", "dead-301", stacks("old301", 3), {}, os.time())
	-- The crashed server's last heartbeat still counts as alive for a while.
	beats["dead-301"] = os.time()
	local player = join(301, profile, reservationId)

	local first = play(player, "req-301-a")
	advance(2)
	expectEq(first.ok, false, "no new run while the crashed run is unrecovered")
	expectEq(first.reason, "RecoveringItems", "the player is told why")
	expectEq(checkpoints["301"] and checkpoints["301"].runId, "run-301", "the crashed checkpoint is intact")

	-- The heartbeat expires: recovery restores the crashed run on its next check.
	beats["dead-301"] = nil
	advance(CrashRecoveryService.RETRY_SECONDS + 2)
	local slots = stored(301).lobbyBackpack.slots
	for index = 1, 3 do
		expectEq(hasInstance(slots, "old301-" .. index), 1, "crashed item " .. index .. " restored once")
	end
	expectEq(stored(301).receipts.crashRecovery["run-301"].status, "Restored", "the run is settled")

	local second = play(player, "req-301-b")
	advance(2)
	expectEq(second.ok, true, "the new run starts once the crashed one is settled")
	expectEq(started[player] and #started[player], 2, "with the new loadout")
	local ok, checkpoint = CheckpointStore.Read(301)
	expect(ok and checkpoint and checkpoint.runId ~= "run-301", "the new run has its own checkpoint")
	expectEq(#stored(301).lobbyBackpack.slots, 3, "and the restored items are not restored twice")
end)

test("a checkpoint whose server still beats is never restored; the wait ends once it is cleared", function()
	local profile = crashedRun(ProfileSchema.Default(0), "run-302", "live-302")
	checkpoints["302"] = CrashRecoveryRules.Checkpoint("run-302", "live-302", stacks("old302", 2), {}, os.time())
	beats["live-302"] = os.time()
	local player = join(302, profile)
	for _ = 1, 6 do
		beats["live-302"] = os.time()
		advance(CrashRecoveryService.RETRY_SECONDS)
	end
	expectEq(#stored(302).lobbyBackpack.slots, 0, "nothing restored while its server runs")
	local early = play(player, "req-302-a")
	advance(1)
	expectEq(early.reason, "RecoveringItems", "and no new run replaces it")

	-- That server ends the run itself (a body, an extraction) and clears its checkpoint.
	CheckpointStore.Clear(302, "run-302")
	advance(CrashRecoveryService.RETRY_SECONDS + 1)
	expectEq(#stored(302).lobbyBackpack.slots, 0, "nothing to restore without a checkpoint or loadout")
	local later = play(player, "req-302-b")
	advance(2)
	expectEq(later.ok, true, "the player can play again")
end)

-- Issue 2: deletes compare the run --------------------------------------------------

test("clearing a checkpoint only removes the run it names", function()
	CheckpointStore.Write(390, CrashRecoveryRules.Checkpoint("run-a", "job", {}, {}, 0))
	CheckpointStore.Clear(390, "run-b")
	local _, kept = CheckpointStore.Read(390)
	expectEq(kept and kept.runId, "run-a", "another run's clear leaves it")
	CheckpointStore.Clear(390, "run-a")
	local _, gone = CheckpointStore.Read(390)
	expectEq(gone, nil, "its own clear removes it")
end)

test("a restore whose delete lands late never deletes a run started meanwhile", function()
	local profile, reservationId = world.transit(303, stacks("new303", 2))
	crashedRun(profile, "run-303", "dead-303")
	checkpoints["303"] = CrashRecoveryRules.Checkpoint("run-303", "dead-303", stacks("old303", 1), {}, os.time())
	memory.latency["FlintbornRunCheckpoints.UpdateAsync"] = 5
	memory.latency["FlintbornRunCheckpoints.RemoveAsync"] = 5
	local player = join(303, profile, reservationId)
	local result = play(player, "req-303")
	advance(10)
	memory.latency["FlintbornRunCheckpoints.UpdateAsync"] = nil
	memory.latency["FlintbornRunCheckpoints.RemoveAsync"] = nil
	expectEq(result.ok, true, "the new run started once the crashed run was restored")
	expectEq(hasInstance(stored(303).lobbyBackpack.slots, "old303-1"), 1, "the crashed item is restored")
	local ok, checkpoint = CheckpointStore.Read(303)
	expect(ok and checkpoint ~= nil, "the new run's checkpoint survived the restore's delete")
	expect(checkpoint == nil or checkpoint.runId ~= "run-303", "and it is the new run's")
end)

-- Issue 3: a crash between the consume save and the first checkpoint --------------

-- The stored profile as a crashed server left it, joined again "elsewhere": specs
-- run one server, so the dead server's JobId is written into the run record.
local function rejoinAfterCrash(fromUserId: number, toUserId: number)
	local crashed = ProfileSchema.DeepCopy(stored(fromUserId))
	crashed.sessionLease = nil
	local run = crashed.progression.currentRun
	if run then
		run.jobId = "dead-" .. fromUserId
	end
	return join(toUserId, crashed)
end

test("a crash before the first checkpoint lands still restores the consumed loadout", function()
	local profile, reservationId = world.transit(401, stacks("i401", 3))
	local player = join(401, profile, reservationId)
	-- The first checkpoint write never lands before the server dies.
	memory.latency["FlintbornRunCheckpoints.SetAsync"] = 1e6
	play(player, "req-401")
	advance(1)
	memory.latency["FlintbornRunCheckpoints.SetAsync"] = nil
	expectEq(WorldAdmissionService.GetState(player), "ActiveRun", "the run started")
	expectEq(stored(401).transit, nil, "the consume is saved")
	expectEq(checkpoints["401"], nil, "but no checkpoint exists yet")

	local again = rejoinAfterCrash(401, 402)
	advance(1)
	local slots = stored(402).lobbyBackpack.slots
	for index = 1, 3 do
		expectEq(hasInstance(slots, "i401-" .. index), 1, "loadout item " .. index .. " restored once")
	end
	local notice = world.net.sent.Notice and world.net.sent.Notice[again]
	expect(notice ~= nil and notice[1].text ~= nil, "the player is told")
end)

test("the consume names the run its checkpoint uses, and the loadout goes once checkpointed", function()
	local profile, reservationId = world.transit(403, stacks("i403", 2))
	local player = join(403, profile, reservationId)
	play(player, "req-403")
	advance(5)
	local run = stored(403).progression.currentRun
	local _, checkpoint = CheckpointStore.Read(403)
	expect(run ~= nil and checkpoint ~= nil and run.runId == checkpoint.runId, "one run ID for both")
	expectEq(run and run.jobId, CheckpointStore.JobId(), "recorded with this server")
	expectEq(run and run.loadout, nil, "only the checkpoint recovers it now")
end)

test("a Play cancelled after its consume saved is settled, so recovery never doubles it", function()
	local profile, reservationId = world.transit(404, stacks("i404", 2))
	local player = join(404, profile, reservationId)
	local result = play(player, "req-404")
	task.delay(0.1, function()
		player.Character:FindFirstChildOfClass("Humanoid").Health = 0
	end)
	advance(10)
	expectEq(result.reason, "Cancelled", "the Play was cancelled during its save")
	rejoinAfterCrash(404, 405)
	advance(1)
	local again = stored(405)
	local total = #again.lobbyBackpack.slots + (if again.transit then #again.transit.items else 0)
	expectEq(total, 2, "each item exists exactly once")
end)

-- Issue 4: nothing a trade rollback cannot reclaim while it settles ---------------

local NOW = 200000

local function settling()
	local profile = ProfileSchema.Default(0)
	profile.progression.level = 12
	profile.currency.coins = 100
	profile.currency.gems = 1000
	profile.vault.materials.IronBar = 50
	profile.vault.materials.Wood = 50
	profile.lobbyBackpack.slots = { { catalogId = "AncientEmber", quantity = 1 } }
	profile.trades.pending.t1 = {
		counterpart = 2,
		gave = { items = {}, gems = 0 },
		received = { items = { { catalogId = "AncientEmber", quantity = 1 } }, gems = 0 },
		at = NOW,
	}
	return profile
end

test("selling, forging, Gem spending and Deploy wait while a trade settles", function()
	local profile = settling()
	local ok, reason = EconomyRules.Sell(profile, "backpack", 1, nil, "sale:x", NOW)
	expectEq(ok, false, "no backpack sale")
	expectEq(reason, "TradeSettling", "with a clear reason")
	ok = EconomyRules.Sell(profile, "vault", "IronBar", 5, "sale:y", NOW)
	expectEq(ok, false, "no vault sale")
	ok, reason = EconomyRules.BuyVaultTier(profile)
	expectEq(reason, "TradeSettling", "no Gem vault upgrade")
	ok, reason = EconomyRules.Spend(profile, 0, 250)
	expectEq(reason, "TradeSettling", "no Gem respec")
	expectEq(profile.currency.gems, 1000, "Gems untouched")
	expectEq(EconomyRules.Spend(profile, 10, 0), true, "Coins (never traded) still spend")
	local receipt, why = ForgeRules.Craft(profile, {
		recipeId = "ForgeIronPickaxe",
		ownerId = 1,
		operationId = "forge:x",
		now = NOW,
		newId = function()
			return "forged"
		end,
	})
	expectEq(receipt, nil, "no Forge craft")
	expectEq(why, "TradeSettling", "with a clear reason")
	expectEq(profile.vault.materials.IronBar, 50, "inputs untouched")
	local reserved, err = pcall(TransitRules.Reserve, profile, "res-x", NOW)
	expect(not reserved and tostring(err):find("TradeSettling") ~= nil, "no Deploy reservation")
	expectEq(#profile.lobbyBackpack.slots, 1, "the received item stays reclaimable")
end)

test("the wait always ends: a counterpart that never saves rolls the trade back", function()
	local a, b = ProfileSchema.Default(0), ProfileSchema.Default(0)
	a.lobbyBackpack.slots = { { instanceId = "s1", catalogId = "StoneSword", ownerId = 1 } }
	b.lobbyBackpack.slots = { { catalogId = "AncientEmber", quantity = 3 } }
	local bStored = ProfileSchema.DeepCopy(b)
	TradeRules.Settle("t1", { profile = a, userId = 1, offer = { items = { 1 } } }, {
		profile = b,
		userId = 2,
		offer = { items = { 1 } },
	}, NOW)
	a.trades.pending.t1.server = "S"
	bStored.sessionLease = { jobId = "S", expiresAt = NOW + 300 }
	expectEq(TradeRules.Reconcile(a, "t1", bStored, NOW + 10), "Deferred", "B may still save on S")
	expectEq((EconomyRules.Sell(a, "backpack", 1, nil, "sale:a", NOW + 10)), false, "A's received Ember is held")
	expectEq(TradeRules.Reconcile(a, "t1", bStored, NOW + 400), "RolledBack", "B's lease expired unsaved")
	expectEq(next(a.trades.pending), nil, "nothing pending any more")
	expectEq(hasInstance(a.lobbyBackpack.slots, "s1"), 1, "A has the sword back")
	expectEq((EconomyRules.Sell(a, "backpack", 1, nil, "sale:b", NOW + 400)), true, "and may sell again")
end)

test("a Deploy reservation is refused while a trade settles", function()
	local profile = settling()
	local player = join(501, profile)
	local result = {}
	task.spawn(function()
		result.id, result.reason = LoadoutService.Reserve(player)
	end)
	advance(2)
	expectEq(result.id, nil, "nothing reserved")
	expectEq(result.reason, "TradeSettling", "with a clear reason")
	expectEq(stored(501).transit, nil, "no transit stored")
	expectEq(#stored(501).lobbyBackpack.slots, 1, "the backpack is untouched")
end)

test("no spawned thread errored", world.expectNoThreadErrors)
