-- Crash recovery of items let go and taken back during a run (GDD §29.1, Q157): a
-- whole-server crash returns what the player carried at the last checkpoint. An
-- item dropped or put in a chest is left out only while someone else holds it;
-- once its owner picks it up again it is carried, and recovered, like any other.
-- Drives the real RunCheckpointService, InventoryService, DropService and
-- CheckpointStore (its in-memory fallback) against a fake clock.

local Shared = game:GetService("ReplicatedStorage").Shared
local Server = game:GetService("ServerScriptService").Server
local TestSupport = game:GetService("ServerStorage").TestSupport
local FakeRoblox = require(TestSupport.FakeRoblox)

local scheduler = require(TestSupport.Scheduler).new():Install()
local function advance(seconds: number)
	scheduler:Advance(seconds)
end
FakeRoblox.Provide({
	HttpService = FakeRoblox.Guids(),
	MemoryStoreService = require(TestSupport.FakeStores).NoMemoryStore,
})
game.JobId = "job-recovery"
FakeRoblox.Place("World")
FakeRoblox.Remotes()

local CrashRecoveryRules = require(Server.Rules.Recovery.CrashRecoveryRules)
local InventoryRules = require(Server.Rules.Inventory.InventoryRules)
local ProfileSchema = require(Server.Rules.Data.ProfileSchema)
local CheckpointStore = require(Server.Infrastructure.CheckpointStore)
local ProfileService = require(Server.Services.ProfileService)
local profiles = {}
ProfileService.GetProfile = function(player)
	return profiles[player]
end
ProfileService.Mutate = function(player, apply)
	apply(profiles[player])
	return true
end
ProfileService.RunOperation = function(player, _, _, apply)
	return true, apply(profiles[player]), true
end
local DropService = require(Server.Services.DropService)
local InventoryService = require(Server.Services.InventoryService)
local RunCheckpointService = require(Server.Services.RunCheckpointService)
local WorldAdmissionService = require(Server.Services.WorldAdmissionService)
InventoryService.Start()
RunCheckpointService.Start()

local function newPlayer(userId: number)
	local player = FakeRoblox.Player(userId, { Parent = {} })
	profiles[player] = ProfileSchema.Default(0)
	return player
end

local function startRun(player, items)
	WorldAdmissionService.RunStarted:Fire(player, nil, items, "run-" .. player.UserId)
	advance(RunCheckpointService.DEBOUNCE + 1)
end

-- DropService's DropItem handler: take the slot out of the inventory, release it.
local function drop(player, instanceId: string)
	for index, item in InventoryService.Get(player).hotbar do
		if item and item.instanceId == instanceId then
			local taken = InventoryService.TakeAt(player, InventoryRules.Hotbar, index)
			DropService.Release(player, taken, "WorldDropped")
			return taken
		end
	end
	error("not carried: " .. instanceId)
end

-- DropService's pick-up: claim a copy into the inventory, then record the claim.
local function pickUp(player, item)
	local copy = DropService.PrepareClaim(player, item)
	local remaining = InventoryService.Add(player, copy)
	assert(remaining == 0, "picked up")
	DropService.FinishClaim(player, copy, item.ownerId)
end

-- The server dies: the last checkpoint is restored into the saved profile.
local function crashAndRecover(player)
	local _, checkpoint = CheckpointStore.Read(player.UserId)
	assert(checkpoint, "a checkpoint was written")
	local profile = ProfileSchema.Default(0)
	CrashRecoveryRules.Restore(profile, checkpoint, scheduler.clock + 1000)
	return profile
end

local function holds(profile, instanceId: string): boolean
	for _, slot in profile.lobbyBackpack.slots do
		if slot.instanceId == instanceId then
			return true
		end
	end
	return false
end

local function gear(id: string, userId: number, permanent: boolean?)
	return {
		instanceId = id,
		catalogId = "IronSword",
		ownerId = userId,
		qualityRoll = 0,
		permanent = permanent,
		ownershipVersion = if permanent then 1 else nil,
	}
end

test("an item dropped and picked back up is restored after a crash", function()
	local player = newPlayer(7)
	startRun(player, { gear("sword-1", 7), gear("perm-1", 7, true) })
	for _, id in { "sword-1", "perm-1" } do
		local item = drop(player, id)
		advance(RunCheckpointService.DEBOUNCE + 1)
		pickUp(player, item)
	end
	advance(RunCheckpointService.DEBOUNCE + 1)
	local profile = crashAndRecover(player)
	expect(holds(profile, "sword-1"), "the carried sword comes back")
	expect(holds(profile, "perm-1"), "the carried Permanent sword comes back")
	expect(profile.permanentItems["perm-1"] ~= nil, "with its ownership")
	scheduler:ExpectNoThreadErrors()
end)

test("an item someone else holds at the crash is not restored to its old carrier", function()
	local owner, other = newPlayer(8), newPlayer(9)
	startRun(owner, { gear("axe-1", 8) })
	startRun(other, {})
	local item = drop(owner, "axe-1")
	advance(RunCheckpointService.DEBOUNCE + 1)
	pickUp(other, item)
	advance(RunCheckpointService.DEBOUNCE + 1)
	expect(not holds(crashAndRecover(owner), "axe-1"), "the dropper does not get it back")
	expect(holds(crashAndRecover(other), "axe-1"), "whoever carried it does")
	-- Passed back to its first carrier: carried by exactly one of them again.
	local back = drop(other, "axe-1")
	advance(RunCheckpointService.DEBOUNCE + 1)
	pickUp(owner, back)
	advance(RunCheckpointService.DEBOUNCE + 1)
	expect(holds(crashAndRecover(owner), "axe-1"), "the owner carries it again")
	expect(not holds(crashAndRecover(other), "axe-1"), "the other player no longer does")
	scheduler:ExpectNoThreadErrors()
end)
