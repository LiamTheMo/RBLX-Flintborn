local Server = game:GetService("ServerScriptService").Server
local Shared = game:GetService("ReplicatedStorage").Shared
local CrashRecoveryRules = require(Shared.Recovery.CrashRecoveryRules)
local OperationJournal = require(Server.Infrastructure.OperationJournal)
local ProfileSchema = require(Shared.Data.ProfileSchema)

local NOW = 100000

local function carried()
	return {
		{ instanceId = "s1", catalogId = "IronSword", ownerId = 1, qualityRoll = 0.02 },
		{ instanceId = "p1", catalogId = "StonePickaxe", ownerId = 1, permanent = true, ownershipVersion = 1 },
		{ instanceId = "d1", catalogId = "StoneDagger", ownerId = 1 },
		{ catalogId = "IronOre", quantity = 30 },
	}
end

test("a crash (checkpoint left, heartbeat gone) is eligible", function()
	local checkpoint = CrashRecoveryRules.Checkpoint("run1", "job1", carried(), {}, NOW - 20)
	expectEq(CrashRecoveryRules.Classify(checkpoint, nil, NOW), "Eligible", "no heartbeat")
	expectEq(CrashRecoveryRules.Classify(checkpoint, NOW - 200, NOW), "Eligible", "stale heartbeat")
	expectEq(CrashRecoveryRules.Classify(checkpoint, NOW - 10, NOW), "ServerAlive", "the server still runs")
end)

test("a logout or planned shutdown leaves no checkpoint and is never eligible", function()
	-- Logout makes a body and shutdown escrows; both end the run, deleting the checkpoint.
	expectEq(CrashRecoveryRules.Classify(nil, nil, NOW), "NoCheckpoint", "logout")
	expectEq(CrashRecoveryRules.Classify(nil, NOW - 500, NOW), "NoCheckpoint", "shutdown")
end)

test("items already dropped, stored or traded away are not restored", function()
	local profile = ProfileSchema.Default(0)
	local checkpoint = CrashRecoveryRules.Checkpoint("run1", "job1", carried(), { d1 = true }, NOW)
	local receipt = CrashRecoveryRules.Restore(profile, checkpoint, NOW)
	expectEq(receipt.restored, 3, "sword, Permanent pickaxe and iron")
	for _, slot in profile.lobbyBackpack.slots do
		expect(slot.instanceId ~= "d1", "the looted dagger stays with its new owner")
	end
	expect(profile.permanentItems.p1 ~= nil, "Permanent ownership restored")
	expectEq(profile.lobbyBackpack.slots[1].qualityRoll, 0.02, "same instance, same roll")
end)

test("recovery restores once, even when retried", function()
	local profile = ProfileSchema.Default(0)
	local checkpoint = CrashRecoveryRules.Checkpoint("run1", "job1", carried(), {}, NOW)
	local function restore(working)
		local receipt = CrashRecoveryRules.Restore(working, checkpoint, NOW)
		if receipt == nil then
			error("AlreadyRestored", 0)
		end
		return receipt
	end
	OperationJournal.Run(profile, "crash:run1", "CrashRecovery", NOW, restore)
	OperationJournal.Run(profile, "crash:run1", "CrashRecovery", NOW + 1, restore)
	expectEq(#profile.lobbyBackpack.slots, 4, "four items once")
	local ok = pcall(OperationJournal.Run, profile, "crash:run1-again", "CrashRecovery", NOW + 2, restore)
	expect(not ok, "a new operation for the same run is refused")
	expectEq(#profile.lobbyBackpack.slots, 4, "still once")
end)
