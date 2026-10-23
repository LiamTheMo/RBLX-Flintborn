-- Follow-up review: the Center 2× bonus must never double materials that came in
-- from the lobby, however they change hands (drops, bodies, chests, tribemates),
-- and a lobby party id seen in an invite must not admit anyone into that party's
-- in-world tribe. The second half drives PartyService against a fake MemoryStore.

local Shared = game:GetService("ReplicatedStorage").Shared
local Server = game:GetService("ServerScriptService").Server

-- Fake Roblox services -------------------------------------------------------------

local function engineSignal()
	local handlers = {}
	return {
		Connect = function(_, fn)
			table.insert(handlers, fn)
			return { Disconnect = function() end }
		end,
		Fire = function(_, ...)
			for _, fn in table.clone(handlers) do
				fn(...)
			end
		end,
	}
end

local Players = { PlayerAdded = engineSignal(), PlayerRemoving = engineSignal(), _list = {} }
function Players.GetPlayers(self)
	return table.clone(self._list)
end
function Players.GetPlayerByUserId(self, userId)
	for _, player in self._list do
		if player.UserId == userId then
			return player
		end
	end
	return nil
end

-- A MemoryStore hash map that can be made to fail.
local memory = { data = {}, failing = false, writes = 0 }
local fakeMap = {
	SetAsync = function(_, key, value)
		if memory.failing then
			error("MemoryStore unavailable")
		end
		memory.writes += 1
		memory.data[key] = value
		return true
	end,
	GetAsync = function(_, key)
		if memory.failing then
			error("MemoryStore unavailable")
		end
		return memory.data[key]
	end,
}

local guids = 0
local fakes = {
	Players = Players,
	HttpService = {
		GenerateGUID = function()
			guids += 1
			return string.format("%08x-0000-4000-8000-%012x", guids, guids)
		end,
	},
	MemoryStoreService = {
		GetHashMap = function()
			return fakeMap
		end,
	},
}
local originalGetService = game.GetService
game.GetService = function(self, name)
	return fakes[name] or originalGetService(self, name)
end
game.PrivateServerId = "world-1"
task = {
	wait = function() end,
	spawn = function(fn, ...)
		fn(...)
	end,
}
warn = function() end

local InventoryRules = require(Shared.Inventory.InventoryRules)
local ExtractionRules = require(Shared.Extraction.ExtractionRules)
local PartyRules = require(Shared.Admission.PartyRules)
local ProfileSchema = require(Shared.Data.ProfileSchema)
local ProgressionRules = require(Shared.Progression.ProgressionRules)

-- Helpers --------------------------------------------------------------------------

-- A run inventory as InventoryService builds it from the deployed lobby items.
local function deploy(items)
	local inventory = InventoryRules.FromItems(InventoryRules.MarkFromLobby(items))
	return inventory
end

-- Settles a Center extraction of everything `inventory` holds; returns the profile.
local function centerExtract(inventory)
	local profile = ProfileSchema.Default(0)
	ProgressionRules.StartRun(profile, "run1")
	local items = ProfileSchema.DeepCopy(InventoryRules.Items(inventory))
	ExtractionRules.Settle(profile, items, "Center", "r1", 1)
	return profile
end

-- One player picking up a dropped or looted stack: what fits joins their
-- inventory, the rest stays where it was (DropService, DepartureService).
local function claim(inventory, source)
	local remaining = InventoryRules.Add(inventory, ProfileSchema.DeepCopy(source))
	if remaining > 0 then
		InventoryRules.KeepRemainder(source, remaining)
	end
	return remaining
end

local function slotOf(inventory, catalogId)
	for _, item in InventoryRules.Items(inventory) do
		if item.catalogId == catalogId and item.instanceId == nil then
			return item
		end
	end
	return nil
end

-- 1. Carried-in materials are tagged on the stack itself ------------------------------

test("a carried-in stack dropped and picked up by another player is not doubled", function()
	local a = deploy({ { catalogId = "Iron", quantity = 1000 } })
	local area, index = "backpack", 1
	local dropped = InventoryRules.TakeAt(a, area, index)
	expectEq(dropped and dropped.quantity, 1000, "A dropped the whole stack")
	local b = InventoryRules.New()
	expectEq(claim(b, dropped), 0, "B picked it all up")
	expectEq(centerExtract(b).vault.materials.Iron, 1000, "B banks 1000, not 2000")
end)

test("a body's carried-in stack looted by a stranger is not doubled", function()
	local a = deploy({ { catalogId = "Stone", quantity = 300 }, { catalogId = "Wood", quantity = 40 } })
	InventoryRules.Add(a, { catalogId = "Stone", quantity = 100 }) -- gathered by A
	local body = ProfileSchema.DeepCopy(InventoryRules.Items(a))
	local b = InventoryRules.New()
	for _, entry in body do
		claim(b, entry)
	end
	local profile = centerExtract(b)
	expectEq(profile.vault.materials.Stone, 300 + 100 * 2, "only A's 100 gathered Stone doubles")
	expectEq(profile.vault.materials.Wood, 40, "carried-in Wood never doubles")
end)

test("a partial pickup splits the tag without creating or losing any", function()
	local a = deploy({ { catalogId = "Iron", quantity = 1000 } })
	local dropped = InventoryRules.TakeAt(a, "backpack", 1)
	local b = InventoryRules.New()
	InventoryRules.Add(b, { catalogId = "Iron", quantity = 600 }) -- gathered by B
	expectEq(claim(b, dropped), 600, "only 400 fit beside B's own 600")
	expectEq(dropped.quantity, 600, "600 stay on the ground")
	expectEq(InventoryRules.FromLobby(dropped), 600, "the ground keeps 600 tagged")
	local stack = slotOf(b, "Iron")
	expectEq(stack.quantity, 1000, "B's stack is full")
	expectEq(InventoryRules.FromLobby(stack), 400, "400 of B's stack came from A's lobby")
	expectEq(InventoryRules.FromLobby(stack) + InventoryRules.FromLobby(dropped), 1000, "tags add up")
	local profile = ProfileSchema.Default(0)
	ProgressionRules.StartRun(profile, "run1")
	local receipt = ExtractionRules.Settle(profile, InventoryRules.Items(b), "Center", "r1", 1)
	expectEq(receipt.vaulted.Iron + (receipt.deleted.Iron or 0), 400 + 600 * 2, "B's own 600 still double")
end)

test("carried-in materials stored in a chest stay tagged in a later run", function()
	local chest = {}
	local run1 = deploy({ { catalogId = "Iron", quantity = 500 } })
	local deposited = InventoryRules.TakeAt(run1, "backpack", 1)
	expect(InventoryRules.Store(chest, deposited, 30), "stored")
	-- Gathered Iron from someone else lands on the same chest stack.
	expect(InventoryRules.Store(chest, { catalogId = "Iron", quantity = 200 }, 30), "merged")
	expectEq(#chest, 1, "one stack")
	expectEq(chest[1].quantity, 700, "quantities add")
	expectEq(InventoryRules.FromLobby(chest[1]), 500, "the tagged count survives the merge")
	-- A later run with nothing carried in withdraws it all.
	local run2 = deploy({})
	expectEq(claim(run2, chest[1]), 0, "withdrawn")
	expectEq(centerExtract(run2).vault.materials.Iron, 500 + 200 * 2, "only the gathered 200 double")
end)

test("a chest stack withdrawn in part keeps the rest of its tag", function()
	local chest = {}
	InventoryRules.Store(chest, { catalogId = "Iron", quantity = 900, fromLobby = 900 }, 30)
	local taker = InventoryRules.New()
	InventoryRules.Add(taker, { catalogId = "Iron", quantity = 700 })
	expectEq(claim(taker, chest[1]), 600, "300 fit")
	expectEq(InventoryRules.FromLobby(chest[1]), 600, "the chest keeps 600 tagged")
	expectEq(InventoryRules.FromLobby(slotOf(taker, "Iron")), 300, "the taker carries 300 tagged")
end)

test("a tribemate handed carried-in materials does not double them", function()
	local giver = deploy({ { catalogId = "Obsidian", quantity = 50 }, { catalogId = "AncientEmber", quantity = 2 } })
	local mate = InventoryRules.New()
	InventoryRules.Add(mate, { catalogId = "Obsidian", quantity = 10 }) -- the mate's own haul
	for _, item in InventoryRules.Items(giver) do
		claim(mate, item)
	end
	local profile = centerExtract(mate)
	expectEq(profile.vault.materials.Obsidian, 50 + 10 * 2, "only the mate's own 10 double")
	local ember = 0
	for _, slot in profile.lobbyBackpack.slots do
		if slot.catalogId == "AncientEmber" then
			ember += slot.quantity
		end
	end
	expectEq(ember, 2, "a handed special material is not doubled either")
end)

test("the Center doubles what a player gathers even after dropping their carried stack", function()
	local a = deploy({ { catalogId = "Iron", quantity = 100 } })
	InventoryRules.TakeAt(a, "backpack", 1)
	InventoryRules.Add(a, { catalogId = "Iron", quantity = 100 })
	expectEq(centerExtract(a).vault.materials.Iron, 200, "fresh Iron doubles: no per-player carry-over")
end)

test("crafting spends gathered units first, so the tag never grows", function()
	local inventory = deploy({ { catalogId = "Wood", quantity = 10 } })
	InventoryRules.Add(inventory, { catalogId = "Wood", quantity = 50 })
	expectEq(InventoryRules.FromLobby(slotOf(inventory, "Wood")), 10, "10 tagged of 60")
	expect(InventoryRules.Remove(inventory, "Wood", 45), "spent 45")
	expectEq(InventoryRules.FromLobby(slotOf(inventory, "Wood")), 10, "still 10 tagged of 15")
	expect(InventoryRules.RemoveAll(inventory, { Wood = 8 }), "spent 8")
	local stack = slotOf(inventory, "Wood")
	expectEq(stack.quantity, 7, "7 left")
	expectEq(InventoryRules.FromLobby(stack), 7, "the tag never exceeds the stack")
end)

test("tagged and untagged stacks merge into one ordinary slot", function()
	local inventory = deploy({ { catalogId = "Stone", quantity = 20 }, { catalogId = "BasicMedicine", quantity = 3 } })
	InventoryRules.Add(inventory, { catalogId = "Stone", quantity = 5 })
	InventoryRules.Add(inventory, { catalogId = "Stone", quantity = 7, fromLobby = 7 })
	expectEq(InventoryRules.Count(inventory, "Stone"), 32, "one count")
	local stones = 0
	for _, item in InventoryRules.Items(inventory) do
		if item.catalogId == "Stone" then
			stones += 1
		end
	end
	expectEq(stones, 1, "one slot per stackable type")
	expectEq(InventoryRules.FromLobby(slotOf(inventory, "Stone")), 27, "20 + 7 tagged")
	expect(InventoryRules.Remove(inventory, "Stone", 32), "the whole stack can still be spent")
	expectEq(InventoryRules.Count(inventory, "Stone"), 0, "gone")
	expect(InventoryRules.Remove(inventory, "BasicMedicine", 1), "tagged consumables still work")
end)

test("the tag round-trips through FromItems, including leftovers", function()
	local items = {}
	for index = 1, 59 do
		table.insert(items, { instanceId = "i" .. index, catalogId = "StoneAxe", ownerId = 1 })
	end
	table.insert(items, { catalogId = "Iron", quantity = 40, fromLobby = 30 })
	local inventory, leftovers = InventoryRules.FromItems(items)
	expectEq(#leftovers, 1, "the stack did not fit")
	expectEq(leftovers[1].quantity, 40, "whole stack returned")
	expectEq(InventoryRules.FromLobby(leftovers[1]), 30, "with its tag")
	local again =
		InventoryRules.FromItems(ProfileSchema.DeepCopy({ { catalogId = "Iron", quantity = 40, fromLobby = 30 } }))
	expectEq(InventoryRules.FromLobby(slotOf(again, "Iron")), 30, "a rebuilt inventory keeps the tag")
	expect(inventory ~= nil, "built")
end)

test("a malformed tag is clamped and never costs items", function()
	for _, bad in { -5, 0 / 0, math.huge, "x", 2.5 } do
		local stack = { catalogId = "Iron", quantity = 10, fromLobby = bad }
		local tagged = InventoryRules.FromLobby(stack)
		expect(tagged >= 0 and tagged <= 10 and tagged % 1 == 0, "clamped " .. tostring(bad))
		local inventory = InventoryRules.New()
		expectEq(InventoryRules.Add(inventory, stack), 0, "added " .. tostring(bad))
		expectEq(InventoryRules.Count(inventory, "Iron"), 10, "nothing lost " .. tostring(bad))
	end
	local profile = ProfileSchema.Default(0)
	ProgressionRules.StartRun(profile, "run1")
	ExtractionRules.Settle(profile, { { catalogId = "Iron", quantity = 10, fromLobby = 99 } }, "Center", "r1", 1)
	expectEq(profile.vault.materials.Iron, 10, "an over-large tag only stops the bonus")
	local fixed = ProfileSchema.Default(0)
	ExtractionRules.Settle(fixed, { { catalogId = "Iron", quantity = 10, fromLobby = 10 } }, "Fixed", "r2", 1)
	expectEq(fixed.vault.materials.Iron, 10, "a fixed portal settles tagged stacks at face value")
end)

test("an interrupted ritual's spilled offering keeps its deployed units tagged", function()
	local summoner = deploy({ { catalogId = "AncientEmber", quantity = 3 }, { catalogId = "Iron", quantity = 30 } })
	InventoryRules.Add(summoner, { catalogId = "Iron", quantity = 40 }) -- gathered
	local offering = InventoryRules.TakeAll(summoner, { AncientEmber = 3, Iron = 50 })
	expect(offering ~= nil, "offered")
	local tagged = {}
	for _, stack in offering or {} do
		tagged[stack.catalogId] = InventoryRules.FromLobby(stack)
	end
	expectEq(tagged.AncientEmber, 3, "every Ember was deployed")
	expectEq(tagged.Iron, 10, "the 40 gathered Iron went first, then 10 deployed")
	expectEq(InventoryRules.FromLobby(slotOf(summoner, "Iron")), 20, "20 deployed Iron stay behind")
	expectEq(InventoryRules.TakeAll(summoner, { AncientEmber = 1 }), nil, "short: nothing taken")
	expectEq(InventoryRules.Count(summoner, "Iron"), 20, "a failed take changes nothing")
	-- Whoever grabs the spill cannot double the deployed part.
	local grabber = InventoryRules.New()
	for _, stack in offering or {} do
		claim(grabber, stack)
	end
	local profile = centerExtract(grabber)
	expectEq(profile.vault.materials.Iron, 10 + 40 * 2, "only the gathered Iron doubles")
end)

-- 2. Lobby party ids cannot be forged into a world tribe ----------------------------

local PlaceConfig = require(Shared.Config.PlaceConfig)
local Remotes = require(Shared.Net.Remotes)
local handlers = {}
Remotes.Handle = function(name, fn)
	handlers[name] = fn
end
Remotes.Get = function()
	return { FireClient = function() end, FireAllClients = function() end }
end
PlaceConfig.IsLobby = function()
	return true
end
local PartyService = require(Server.Services.PartyService)
PartyService.Start()

local function newPlayer(userId: number)
	local player = { UserId = userId, Name = "P" .. userId, DisplayName = "P" .. userId, Parent = Players }
	player.teleportData = nil
	function player.GetJoinData(self)
		return { TeleportData = self.teleportData }
	end
	table.insert(Players._list, player)
	Players.PlayerAdded:Fire(player)
	return player
end

local leader, member, decliner, stranger = newPlayer(1), newPlayer(2), newPlayer(3), newPlayer(4)
handlers.PartyAction(leader, "invite", 2)
handlers.PartyAction(leader, "invite", 3)
local partyId = PartyService.PartyIdOf(leader)
handlers.PartyAction(member, "accept", partyId)
handlers.PartyAction(decliner, "decline", partyId)

test("a deploy records the party's members under a fresh server token", function()
	local group = PartyService.DeployGroup(leader)
	expectEq(#group, 2, "leader and member deploy")
	local token = PartyService.RecordDeploy(leader, group, "world-1")
	expect(PartyRules.IsGuid(token), "a token travels in teleport data")
	expect(token ~= partyId, "the token is not the party id invitees saw")
	local record = memory.data[token]
	expectEq(record and record.partyId, partyId, "the record names the party")
	expectEq(record and #record.members, 2, "and only who deployed")
	for _, player in group do
		player.teleportData = { reservations = {}, partyToken = token }
		expectEq(PartyService.VerifiedPartyId(player), partyId, player.Name .. " joins the party tribe")
	end
end)

test("a declined invitee forging the party id or a member's token stays solo", function()
	local token = PartyService.RecordDeploy(leader, PartyService.DeployGroup(leader), "world-1")
	decliner.teleportData = { partyId = partyId }
	expectEq(PartyService.VerifiedPartyId(decliner), nil, "a bare party id proves nothing")
	decliner.teleportData = { partyId = partyId, partyToken = token }
	expectEq(PartyService.VerifiedPartyId(decliner), nil, "a leaked token does not list them")
	stranger.teleportData = { partyToken = "not-a-token" }
	expectEq(PartyService.VerifiedPartyId(stranger), nil, "garbage is solo")
	stranger.teleportData = { partyToken = string.format("%08x-0000-4000-8000-%012x", 999, 999) }
	expectEq(PartyService.VerifiedPartyId(stranger), nil, "an unknown token is solo")
	stranger.teleportData = "nonsense"
	expectEq(PartyService.VerifiedPartyId(stranger), nil, "non-table teleport data is solo")
end)

test("a token from another world or an expired deploy is refused", function()
	local token = PartyService.RecordDeploy(leader, PartyService.DeployGroup(leader), "world-2")
	member.teleportData = { partyToken = token }
	expectEq(PartyService.VerifiedPartyId(member), nil, "recorded for a different world")
	local record = PartyRules.DeployRecord(partyId, { 1, 2 }, "world-1", 100)
	expectEq(PartyRules.VerifiedPartyId(record, 2, "world-1", 100 + 60), partyId, "fresh")
	expectEq(
		PartyRules.VerifiedPartyId(record, 2, "world-1", 100 + PartyRules.DEPLOY_RECORD_SECONDS + 1),
		nil,
		"expired"
	)
	expectEq(PartyRules.VerifiedPartyId(record, 3, "world-1", 100), nil, "not a member")
	expectEq(PartyRules.VerifiedPartyId({ partyId = "x", members = { 2 }, at = 100 }, 2, "world-1", 100), nil, "bad id")
end)

test("a MemoryStore outage falls back to solo without blocking the deploy", function()
	memory.failing = true
	local token = PartyService.RecordDeploy(leader, PartyService.DeployGroup(leader), "world-1")
	expectEq(token, nil, "no token when the record could not be written")
	memory.failing = false
	local good = PartyService.RecordDeploy(leader, PartyService.DeployGroup(leader), "world-1")
	memory.failing = true
	member.teleportData = { partyToken = good }
	expectEq(PartyService.VerifiedPartyId(member), nil, "an unreadable record is solo")
	memory.failing = false
	expectEq(PartyService.VerifiedPartyId(member), partyId, "readable again")
end)

test("a solo player records nothing", function()
	local before = memory.writes
	expectEq(PartyService.RecordDeploy(stranger, { stranger }, "world-1"), nil, "no party, no token")
	expectEq(memory.writes, before, "no write")
end)
