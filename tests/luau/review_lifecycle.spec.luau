-- Run lifecycle review: a shutdown racing a Play, a Play whose save fails, a safe
-- kick whose save fails, a redirected arrival whose teleport fails, and the crash
-- windows right after a Play. Drives the real server services against fake Roblox
-- services, a DataStore with latency and a fake clock.

local Server = game:GetService("ServerScriptService").Server

local world = require(game:GetService("ServerStorage").TestSupport.WorldServer).new({
	jobId = "job-review",
	privateServerId = "world-review",
	start = {
		"InventoryService",
		"LoadoutService",
		"MaintenanceService",
		"ProfileService",
		"RunCheckpointService",
		"WorldAdmissionService",
	},
})
local advance, play, stored, started = world.advance, world.play, world.stored, world.started

local ProfileSchema = require(Server.Rules.Data.ProfileSchema)
local CheckpointStore = require(Server.Infrastructure.CheckpointStore)
local AdminService = require(Server.Services.AdminService)
local InventoryService = require(Server.Services.InventoryService)
local MaintenanceService = require(Server.Services.MaintenanceService)
local ProfileService = require(Server.Services.ProfileService)
local TravelService = require(Server.Services.TravelService)
local WorldAdmissionService = require(Server.Services.WorldAdmissionService)

-- Joins a world with `items` reserved and waits on the menu.
local function arrive(userId: number, items)
	return world.join(userId, world.transit(userId, items))
end

local function stacks(count: number)
	return world.stacks("item", count)
end

-- Items the stored profile still owns outside a run.
local function storedCount(userId: number): number
	local profile = stored(userId)
	local count = #profile.lobbyBackpack.slots
	if profile.transit then
		count += #profile.transit.items
	end
	for _, receipt in profile.receipts.maintenance do
		if receipt.status == "Pending" then
			count += #receipt.items
		end
	end
	return count
end

-- Cases (the shutdown case runs last: a shutdown cannot be undone) ---------------

test("Play waits for the island to finish building, losing nothing (GDD §54)", function()
	local player = arrive(100, stacks(2))
	world.ready = false
	local early = play(player, "req-100-a")
	advance(2)
	expectEq(early.ok, false, "no run while the map builds")
	expectEq(early.reason, "WorldLoading", "the player is told the island is loading")
	expectEq(WorldAdmissionService.GetState(player), "WorldMainMenuReady", "still on the menu")
	expectEq(storedCount(100), 2, "the loadout stays reserved")
	world.ready = true
	local later = play(player, "req-100-b")
	advance(5)
	expectEq(later.ok, true, "Play works once the map is ready")
	expectEq(started[player] and #started[player], 2, "with the reserved loadout")
end)

test("a Play whose save failed keeps the reservation, so the next Play brings the loadout", function()
	local player = arrive(101, stacks(3))
	world.backing.failNext = 5
	local first = play(player, "req-101-a")
	advance(60)
	expectEq(first.reason, "SaveFailed", "the first Play reports the failed save")
	expectEq(WorldAdmissionService.GetState(player), "WorldMainMenuReady", "back on the menu")
	expectEq(storedCount(101), 3, "nothing lost in the store")

	local second = play(player, "req-101-b")
	advance(5)
	expectEq(second.ok, true, "the retry enters the run")
	expectEq(started[player] and #started[player], 3, "with the reserved loadout")
	local profile = stored(101)
	expectEq(profile.transit, nil, "the reservation was consumed once")
	expectEq(#profile.lobbyBackpack.slots, 0, "and is not also in the lobby backpack")
end)

test("a safe kick whose save failed retries the save and kicks once it sticks", function()
	local player = arrive(102, stacks(2))
	play(player, "req-102")
	advance(2)
	expectEq(WorldAdmissionService.GetState(player), "ActiveRun", "in the run")
	world.backing.failNext = 5
	local kicked = nil
	task.spawn(function()
		kicked = AdminService.SafeKick(player)
	end)
	advance(60)
	expectEq(kicked, false, "the admin is told the save failed")
	advance(120)
	expect(player.kickMessage ~= nil, "the player is kicked once the escrow is saved")
	local escrowed = 0
	for _, receipt in stored(102).receipts.maintenance do
		escrowed += #receipt.items
	end
	expectEq(escrowed, 2, "the escrow is stored")
end)

test("a redirected arrival whose lobby teleport fails is not left stranded", function()
	game.PrivateServerId = ""
	local player = world.enter(world.newPlayer(103))
	game.PrivateServerId = "world-review"
	expect(player.sentToLobby, "sent to the lobby")
	expectEq(WorldAdmissionService.GetState(player), nil, "never staged")
	TravelService.TeleportFailed:Fire(player)
	advance(1)
	expect(player.kickMessage ~= nil, "kicked with a rejoin message instead of a blank world")
end)

test("the run's checkpoint exists as soon as the run starts", function()
	local player = arrive(104, stacks(1))
	play(player, "req-104")
	advance(0.5)
	expectEq(WorldAdmissionService.GetState(player), "ActiveRun", "in the run")
	expectEq(stored(104).transit, nil, "the consumed reservation is already saved")
	local ok, checkpoint = CheckpointStore.Read(104)
	expect(ok and checkpoint ~= nil, "a crash now can still recover the carried items")
	expectEq(checkpoint and #checkpoint.items, 1, "with the carried item")
end)

test("items that do not fit the run are saved back to the lobby at once", function()
	local player = arrive(105, stacks(70))
	play(player, "req-105")
	advance(1)
	expectEq(WorldAdmissionService.GetState(player), "ActiveRun", "in the run")
	-- 70 stacks into 6 hotbar + 50 backpack slots leave 14 behind.
	expectEq(#stored(105).lobbyBackpack.slots, 14, "the 14 overflow items are already stored")
end)

test("lobby backpack materials stay put on load and after every write (GDD §53)", function()
	local legacy = ProfileSchema.Default(0)
	legacy.vault.materials.IronOre = 995
	legacy.lobbyBackpack.slots = {
		{ catalogId = "IronOre", quantity = 20 },
		{ instanceId = "spear-301", catalogId = "StoneSpear", ownerId = 1 },
	}
	local player = world.join(301, legacy)
	local profile = ProfileService.GetProfile(player)
	expectEq(profile.vault.materials.IronOre, 995, "nothing banked on load")
	expectEq(profile.vault.lastOverflow, nil, "and nothing deleted")
	expectEq(#profile.lobbyBackpack.slots, 2, "the Iron Ore waits in the backpack")

	local ok = ProfileService.RunOperation(player, "test-bank-301", "Test", function(working)
		table.insert(working.lobbyBackpack.slots, { catalogId = "AncientEmber", quantity = 3 })
	end)
	expect(ok, "operation committed")
	expectEq(profile.vault.materials.AncientEmber, nil, "an operation banks nothing")
	expectEq(#profile.lobbyBackpack.slots, 3, "the Ember stays in the backpack")
	ProfileService.Mutate(player, function(live)
		table.insert(live.lobbyBackpack.slots, { catalogId = "Wood", quantity = 4 })
	end)
	expectEq(profile.vault.materials.Wood, nil, "a direct mutation banks nothing")
	expectEq(#profile.lobbyBackpack.slots, 4, "the Wood stays in the backpack")
end)

-- The run inventory's stack of a material, or nil.
local function runStack(player, catalogId: string)
	for _, entry in InventoryService.Items(player) do
		if entry.instanceId == nil and entry.catalogId == catalogId then
			return entry
		end
	end
	return nil
end

test("a Play tags the materials it carries in, and escrow keeps each stack's own tag (GDD §53)", function()
	local player = arrive(106, {
		{ catalogId = "Wood", quantity = 60 },
		{ instanceId = "sword-106", catalogId = "StoneSword", ownerId = 1 },
		{ catalogId = "Wood", quantity = 40 },
		{ catalogId = "IronOre", quantity = 7 },
	})
	play(player, "req-106")
	advance(1)
	expectEq(WorldAdmissionService.GetState(player), "ActiveRun", "in the run")
	local wood = runStack(player, "Wood")
	expectEq(wood and wood.quantity, 100, "both Wood stacks merge into one")
	expectEq(wood and wood.carried, 100, "all of it carried in")
	expectEq(runStack(player, "IronOre").carried, 7, "Iron Ore carried in")
	local run = stored(106).progression.currentRun
	expectEq(run.carriedIn, nil, "no per-run total: the stacks are the record")
	local loadoutWood = 0
	for _, item in run.loadout do
		if item.catalogId == "Wood" then
			loadoutWood += item.carried or 0
		elseif item.catalogId == "StoneSword" then
			expectEq(item.carried, nil, "gear is never tagged")
		end
	end
	expectEq(loadoutWood, 100, "the saved loadout keeps the tags for a crash")

	-- Gathered Wood joins the stack; a checkpoint keeps the split.
	InventoryService.Add(player, { catalogId = "Wood", quantity = 30 })
	expectEq(runStack(player, "Wood").quantity, 130, "130 Wood")
	expectEq(runStack(player, "Wood").carried, 100, "still only 100 carried")
	advance(5)
	local ok, checkpoint = CheckpointStore.Read(106)
	local checkpointed = nil
	for _, item in (ok and checkpoint and checkpoint.items) or {} do
		if item.catalogId == "Wood" then
			checkpointed = item
		end
	end
	expectEq(checkpointed and checkpointed.carried, 100, "the checkpoint keeps the tag")

	-- A safe kick escrows the stacks as they are: the 30 gathered stay eligible.
	expect(MaintenanceService.Escrow(player), "escrowed")
	local escrowed = nil
	for _, receipt in ProfileService.GetProfile(player).receipts.maintenance do
		for _, item in receipt.items do
			if item.catalogId == "Wood" then
				escrowed = item
			end
		end
	end
	expectEq(escrowed and escrowed.quantity, 130, "all 130 Wood escrowed")
	expectEq(escrowed and escrowed.carried, 100, "with only its own 100 carried")
	world.leave(player)
	advance(5)

	-- The next Play brings the escrow back with its tags, beside 5 Wood from the lobby.
	local saved = stored(106)
	saved.transit = {
		reservationId = "res-106b",
		items = { { catalogId = "Wood", quantity = 5 } },
		createdAt = 0,
		status = "Reserved",
	}
	local again = world.enter(world.newPlayer(106, "res-106b"))
	play(again, "req-106b")
	advance(1)
	expectEq(WorldAdmissionService.GetState(again), "ActiveRun", "back in a run")
	expectEq(runStack(again, "Wood").quantity, 135, "130 escrowed + 5 from the lobby")
	expectEq(runStack(again, "Wood").carried, 105, "the gathered 30 are still not carried")
end)

test("a shutdown racing a Play never loses the reserved loadout", function()
	-- X's character finishes loading while the shutdown release is being written;
	-- Y consumed just before the shutdown while an earlier save held the slot.
	local x = arrive(201, stacks(3))
	local y = arrive(202, stacks(4))
	x.loadDelay = 1.2
	y.loadDelay = 1.0
	local playX = play(x, "req-201")
	local playY = play(y, "req-202")
	task.delay(0.95, function()
		ProfileService.SaveNow(y)
	end)
	task.delay(1.08, function()
		for _, fn in world.closeHandlers do
			fn()
		end
	end)
	advance(10)
	expectEq(playX.ok, false, "X does not start a run")
	expectEq(playY.ok, false, "Y does not start a run")
	expectEq(storedCount(201), 3, "X keeps every reserved item")
	expectEq(storedCount(202), 4, "Y keeps every reserved item")
end)

test("no spawned thread errored", world.expectNoThreadErrors)
