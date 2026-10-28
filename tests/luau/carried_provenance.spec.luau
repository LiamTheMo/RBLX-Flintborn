-- Carried-in materials keep their provenance on the stack (GDD §53): the units a
-- Play takes from the lobby are tagged `carried`, every inventory operation
-- conserves the tag, and the Center bonus multiplies only untagged units. The
-- inventory rules are checked directly; the drop, body and chest paths drive the
-- real DropService, DepartureService and StorageService against fake services, so
-- handing carried units to another player never makes them doublable.

local Shared = game:GetService("ReplicatedStorage").Shared
local Server = game:GetService("ServerScriptService").Server

local CrashRecoveryRules = require(Shared.Recovery.CrashRecoveryRules)
local ExtractionRules = require(Shared.Extraction.ExtractionRules)
local InventoryRules = require(Shared.Inventory.InventoryRules)
local ProfileSchema = require(Shared.Data.ProfileSchema)
local Signal = require(Shared.Core.Signal)
local TransitRules = require(Shared.Admission.TransitRules)

local function stack(catalogId, quantity, carried)
	return { catalogId = catalogId, quantity = quantity, carried = carried }
end

-- The stack of a material in an inventory, or nil.
local function stackIn(inventory, catalogId)
	for _, entry in InventoryRules.Items(inventory) do
		if entry.instanceId == nil and entry.catalogId == catalogId then
			return entry
		end
	end
	return nil
end

-- What `items` settle to at the Center, per material.
local function centerYield(items, catalogId)
	local profile = ProfileSchema.Default(0)
	ExtractionRules.Settle(profile, ProfileSchema.DeepCopy(items), "Center", "r", 0)
	return profile.vault.materials[catalogId] or 0
end

-- Inventory rules ------------------------------------------------------------------

test("Play tags every material stack it takes from the lobby, and nothing else", function()
	local profile = ProfileSchema.Default(0)
	profile.transit = {
		reservationId = "res",
		items = {
			stack("Wood", 100),
			{ instanceId = "s1", catalogId = "StoneSword", ownerId = 1 },
			stack("FlintArrow", 20),
		},
		createdAt = 0,
		status = "Reserved",
	}
	local items = TransitRules.Consume(profile, "res")
	expectEq(items[1].carried, 100, "the Wood is carried in whole")
	expectEq(items[2].carried, nil, "gear is never tagged")
	expectEq(items[3].carried, nil, "arrows are not a material")
end)

test("merging adds the carried counts; the 100 + 60 × 2 = 220 example holds", function()
	local inventory = InventoryRules.New()
	InventoryRules.Add(inventory, stack("Wood", 100, 100))
	InventoryRules.Add(inventory, stack("Wood", 60))
	local wood = stackIn(inventory, "Wood")
	expectEq(wood.quantity, 160, "one stack of 160")
	expectEq(wood.carried, 100, "100 of them carried")
	expectEq(centerYield(InventoryRules.Items(inventory), "Wood"), 220, "100 + 60 × 2")
	-- Gathered first, then carried: the same.
	local other = InventoryRules.New()
	InventoryRules.Add(other, stack("Wood", 60))
	InventoryRules.Add(other, stack("Wood", 100, 100))
	expectEq(stackIn(other, "Wood").carried, 100, "the order of merging does not matter")
end)

test("a stack-cap spill conserves the carried units", function()
	local inventory = InventoryRules.New()
	InventoryRules.Add(inventory, stack("IronBar", 900))
	local remaining, carried = InventoryRules.Add(inventory, stack("IronBar", 300, 250))
	expectEq(remaining, 200, "100 fit under the 1,000 cap")
	expectEq(stackIn(inventory, "IronBar").carried, 100, "the units that fit take the carried ones first")
	expectEq(carried, 150, "the 200 left over carry the other 150")
	-- Nothing fits at all: everything comes back, tag included.
	remaining, carried = InventoryRules.Add(inventory, stack("IronBar", 40, 40))
	expectEq(remaining, 40, "nothing fits")
	expectEq(carried, 40, "all still carried")
	-- Leftovers from packing a run inventory keep their share too.
	local _, leftovers = InventoryRules.FromItems({ stack("Stone", 900, 900), stack("Stone", 300) })
	expectEq(leftovers[1].quantity, 200, "200 Stone do not fit")
	expectEq(leftovers[1].carried, nil, "the 900 carried all fit, so the leftover is gathered")
end)

test("consumption takes carried units first, so the gathered rest stays eligible", function()
	local inventory = InventoryRules.New()
	InventoryRules.Add(inventory, stack("Wood", 50, 20))
	local ok, used = InventoryRules.Remove(inventory, "Wood", 15)
	expect(ok, "15 removed")
	expectEq(used, 15, "all 15 were carried")
	expectEq(stackIn(inventory, "Wood").carried, 5, "5 carried left")
	ok, used = InventoryRules.RemoveAll(inventory, { Wood = 10 })
	expect(ok, "10 more removed")
	expectEq(used, 5, "the last 5 carried, then 5 gathered")
	expectEq(stackIn(inventory, "Wood").carried, nil, "the 25 left are all gathered")
	expectEq(centerYield(InventoryRules.Items(inventory), "Wood"), 50, "and all of them double")
	-- A refused removal changes nothing.
	ok, used = InventoryRules.RemoveAll(inventory, { Wood = 99 })
	expect(not ok and used == 0, "short: nothing taken")
	-- TakeAll hands back the carried units it took, so a spilled offering keeps them.
	InventoryRules.Add(inventory, stack("Stone", 10, 4))
	local taken = InventoryRules.TakeAll(inventory, { Stone = 6 })
	expectEq(taken[1].carried, 4, "the spill carries the 4")
	expectEq(stackIn(inventory, "Stone").carried, nil, "the 4 left are gathered")
end)

test("moving, taking and storing a stack keep its tag", function()
	local inventory = InventoryRules.New()
	InventoryRules.Add(inventory, stack("Wood", 30, 30))
	local area, index = "backpack", 1
	expect(InventoryRules.Move(inventory, area, index, "hotbar", 9), "moved")
	expectEq(InventoryRules.At(inventory, "hotbar", 9).carried, 30, "moved with its tag")
	local taken = InventoryRules.TakeAt(inventory, "hotbar", 9)
	expectEq(taken.carried, 30, "taken out with its tag")
	local chest = {}
	expect(InventoryRules.Store(chest, taken, 10), "stored")
	expect(InventoryRules.Store(chest, stack("Wood", 20), 10), "gathered Wood joins it")
	expectEq(chest[1].quantity, 50, "one chest stack")
	expectEq(chest[1].carried, 30, "still 30 carried")
end)

test("a malformed tag never counts more than the stack holds", function()
	expectEq(InventoryRules.Carried(stack("Wood", 10, 50)), 10, "capped at the quantity")
	expectEq(InventoryRules.Carried(stack("Wood", 10, -3)), 0, "negative counts as none")
	expectEq(InventoryRules.Carried(stack("Wood", 10, 0 / 0)), 0, "NaN counts as none")
	expectEq(InventoryRules.Carried(stack("Wood", 10, 2.7)), 2, "whole units only")
	expectEq(InventoryRules.Carried({ instanceId = "x", catalogId = "StoneSword", carried = 1 }), 0, "gear")
end)

test("old saves with a per-run carried-in total migrate onto the escrowed stacks", function()
	local legacy = ProfileSchema.Default(0)
	legacy.progression.currentRun = {
		runId = "old-run",
		general = 0,
		mastery = {},
		settled = false,
		carriedIn = { Wood = 100, IronOre = 7 },
	}
	-- A maintenance kick escrowed 130 Wood (100 brought in) and 3 Iron Ore.
	legacy.receipts.maintenance["maintenance:old"] = {
		items = { stack("Wood", 80), stack("Wood", 50), stack("IronOre", 3), stack("Stone", 9) },
		at = 0,
		status = "Pending",
	}
	legacy.receipts.maintenance["maintenance:done"] = { items = { stack("Wood", 40) }, at = 0, status = "Restored" }
	local profile = ProfileSchema.Migrate(ProfileSchema.DeepCopy(legacy), 0)
	expectEq(profile.progression.currentRun.carriedIn, nil, "the run total is gone: stacks are the record")
	local items = profile.receipts.maintenance["maintenance:old"].items
	expectEq(items[1].carried, 80, "the first Wood stack takes 80 of the 100")
	expectEq(items[2].carried, 20, "the second the other 20")
	expectEq(items[3].carried, 3, "never more than a stack holds")
	expectEq(items[4].carried, nil, "a material not carried in stays untagged")
	expectEq(profile.receipts.maintenance["maintenance:done"].items[1].carried, nil, "restored receipts untouched")
	expectEq(centerYield(items, "Wood"), 160, "100 once + 30 gathered × 2")
	-- Loading again changes nothing more.
	local again = ProfileSchema.Migrate(ProfileSchema.DeepCopy(profile), 0)
	expectEq(again.receipts.maintenance["maintenance:old"].items[2].carried, 20, "migration is idempotent")
	-- A save with no run, or a run with no record, loads as before.
	expect(ProfileSchema.Migrate(ProfileSchema.Default(0), 0) ~= nil, "a fresh profile loads")
end)

-- Drops, bodies and chests against the real services ---------------------------------

local errors = {}
warn = function(message)
	table.insert(errors, tostring(message))
end
task = {
	spawn = function(fn, ...)
		fn(...)
	end,
	defer = function(fn, ...)
		fn(...)
	end,
	delay = function() end,
	wait = function() end,
}
CFrame = {
	new = function(position)
		return { Position = position }
	end,
}

-- Instances: properties are plain fields (a CFrame moves Position too), events
-- are Signals made on first use.
local created = {}
local function fakeInstance(className)
	local instance = {
		ClassName = className,
		Destroy = function(self)
			self.destroyed = true
		end,
		IsA = function(_, name)
			return name == className or (name == "BasePart" and className == "Part")
		end,
	}
	table.insert(created, instance)
	return setmetatable(instance, {
		__index = function(self, key)
			local signal = Signal.new()
			rawset(self, key, signal)
			return signal
		end,
		__newindex = function(self, key, value)
			rawset(self, key, value)
			if key == "CFrame" then
				rawset(self, "Position", value.Position)
			end
		end,
	})
end
Instance = { new = fakeInstance }
workspace = {
	Raycast = function()
		return nil
	end,
}
RaycastParams = {
	new = function()
		return {}
	end,
}

local Players = { PlayerRemoving = Signal.new(), PlayerAdded = Signal.new(), _list = {} }
function Players.GetPlayerFromCharacter(_, character)
	for _, player in Players._list do
		if player.Character == character then
			return player
		end
	end
	return nil
end
function Players.GetPlayers()
	return table.clone(Players._list)
end
local lastGuid = nil
local guids = 0
local fakes = {
	Players = Players,
	HttpService = {
		GenerateGUID = function()
			guids += 1
			lastGuid = ("%08x-0000-4000-8000-%012x"):format(guids, guids)
			return lastGuid
		end,
	},
	RunService = { Heartbeat = Signal.new() },
}
local originalGetService = game.GetService
game.GetService = function(self, name)
	return fakes[name] or originalGetService(self, name)
end

local validated = {}
local stubs = {
	AntiExploitService = {
		ValidatedPosition = function(player)
			return validated[player]
		end,
	},
	BuildingService = { Placed = Signal.new(), Removing = Signal.new() },
	DownedService = {
		IsDowned = function()
			return false
		end,
	},
	ProfileService = {
		RunOperation = function(player, _, _, apply)
			player.profile = player.profile or ProfileSchema.Default(0)
			return true, apply(player.profile)
		end,
		SaveNow = function()
			return true
		end,
	},
	WorldAdmissionService = {
		RunStarted = Signal.new(),
		RunEnded = Signal.new(),
		Death = Signal.new(),
		ActiveDeparture = Signal.new(),
		IsAtRisk = function(player)
			return player.atRisk
		end,
	},
}
local realRequire = require
require = function(node)
	local path = type(node) == "table" and rawget(node, "__path")
	if path and path[1] == "ServerScriptService" and path[3] == "Services" and stubs[path[4]] then
		return stubs[path[4]]
	end
	return realRequire(node)
end

local PlaceConfig = require(Shared.Config.PlaceConfig)
PlaceConfig.IsWorld = function()
	return true
end
local Remotes = require(Shared.Net.Remotes)
local handlers = {}
Remotes.Handle = function(name, fn)
	handlers[name] = fn
end
local silentRemote = { FireClient = function() end, FireAllClients = function() end }
Remotes.Get = function()
	return silentRemote
end

local InventoryService = require(Server.Services.InventoryService)
local DropService = require(Server.Services.DropService)
local DepartureService = require(Server.Services.DepartureService)
local StorageService = require(Server.Services.StorageService)
for _, service in { InventoryService, DropService, DepartureService, StorageService } do
	service.Start()
end

local function newCharacter(position)
	local humanoid = { Health = 100 }
	local root = { Position = position, CFrame = { LookVector = Vector3.new(0, 0, 1) } }
	local head = { Position = position + Vector3.new(0, 1.5, 0) }
	return {
		root = root,
		FindFirstChild = function(_, name)
			return if name == "HumanoidRootPart" then root elseif name == "Head" then head else nil
		end,
		FindFirstChildOfClass = function(_, className)
			return if className == "Humanoid" then humanoid else nil
		end,
		GetPivot = function()
			return { Position = root.Position }
		end,
	}
end

local nextUserId = 500
-- A player in a run at `position`, holding `items`.
local function inRun(items, position)
	nextUserId += 1
	local player = {
		UserId = nextUserId,
		Name = "P" .. nextUserId,
		DisplayName = "P" .. nextUserId,
		Parent = Players,
		atRisk = true,
		attributes = {},
	}
	function player.SetAttribute(self, key, value)
		self.attributes[key] = value
	end
	function player.GetAttribute(self, key)
		return self.attributes[key]
	end
	player.Character = newCharacter(position or Vector3.new(0, 5, 0))
	table.insert(Players._list, player)
	stubs.WorldAdmissionService.RunStarted:Fire(player, player.Character, ProfileSchema.DeepCopy(items))
	return player
end

-- (area, index) of a player's stack of a material.
local function slotOf(player, catalogId)
	local inventory = InventoryService.Get(player)
	for _, area in { "hotbar", "backpack" } do
		for index = 1, InventoryRules.Size(area) do
			local entry = inventory[area][index]
			if entry and entry.catalogId == catalogId then
				return area, index
			end
		end
	end
	return nil, nil
end

local function held(player, catalogId)
	return stackIn(InventoryService.Get(player), catalogId)
end

local function lastPrompt()
	for index = #created, 1, -1 do
		if created[index].ClassName == "ProximityPrompt" then
			return created[index]
		end
	end
	return nil
end

test("a carried stack dropped for another player stays carried for them", function()
	local alt = inRun({ stack("IronBar", 1000, 1000) })
	local main = inRun({})
	local ok, reason = handlers.DropItem(alt, slotOf(alt, "IronBar"))
	expect(ok, "dropped: " .. tostring(reason))
	expectEq(held(alt, "IronBar"), nil, "the alt no longer has it")
	lastPrompt().Triggered:Fire(main)
	local bars = held(main, "IronBar")
	expectEq(bars and bars.quantity, 1000, "the main picked up all 1,000")
	expectEq(bars and bars.carried, 1000, "still carried")
	expectEq(centerYield(InventoryService.Items(main), "IronBar"), 1000, "the Center never doubles them")
end)

test("a partial pickup leaves the rest on the ground with its share of the tag", function()
	-- 300 bars, 120 of them brought in and 180 smelted from gathered ore.
	local alt = inRun({ stack("IronBar", 300, 120) })
	local main = inRun({ stack("IronBar", 850) })
	handlers.DropItem(alt, slotOf(alt, "IronBar"))
	local prompt = lastPrompt()
	prompt.Triggered:Fire(main)
	expectEq(held(main, "IronBar").quantity, 1000, "150 fit")
	expectEq(held(main, "IronBar").carried, 120, "the carried 120 among them")
	local other = inRun({})
	prompt.Triggered:Fire(other)
	expectEq(held(other, "IronBar").quantity, 150, "the other 150 are picked up later")
	expectEq(held(other, "IronBar").carried, nil, "and are all gathered: the tag was conserved, not copied")
end)

test("a gathered drop is in reach only from the server-validated position", function()
	local main = inRun({}, Vector3.new(0, 5, 0))
	DropService.Spawn(stack("Wood", 2), Vector3.new(1, 5, 0), { ownerId = main.UserId })
	local prompt = lastPrompt()
	-- The client claims to stand next to the drop; the server last saw it far away.
	validated[main] = Vector3.new(200, 5, 0)
	prompt.Triggered:Fire(main)
	expectEq(held(main, "Wood"), nil, "out of reach from the validated position")
	validated[main] = Vector3.new(2, 5, 0)
	prompt.Triggered:Fire(main)
	expectEq(held(main, "Wood") and held(main, "Wood").quantity, 2, "in reach once validated there")
	-- An untracked player falls back to the character position, as extraction does.
	local fresh = inRun({}, Vector3.new(0, 5, 0))
	DropService.Spawn(stack("Wood", 1), Vector3.new(1, 5, 0), { ownerId = fresh.UserId })
	lastPrompt().Triggered:Fire(fresh)
	expectEq(held(fresh, "Wood") and held(fresh, "Wood").quantity, 1, "untracked: the character position")
end)

test("a body looted by another player keeps each stack's carried units", function()
	local alt = inRun({ stack("IronBar", 500, 400), stack("Wood", 40) })
	stubs.WorldAdmissionService.Death:Fire(alt, Vector3.new(0, 5, 0))
	local bodyId = lastGuid
	local main = inRun({ stack("IronBar", 700) })
	local ok, reason = handlers.CorpseTake(main, bodyId, 1)
	expect(ok, "looted: " .. tostring(reason))
	expectEq(held(main, "IronBar").quantity, 1000, "300 of the 500 fit")
	expectEq(held(main, "IronBar").carried, 300, "all 300 carried")
	local other = inRun({})
	expect(handlers.CorpseTake(other, bodyId, 1), "the rest looted")
	expectEq(held(other, "IronBar").quantity, 200, "200 left on the body")
	expectEq(held(other, "IronBar").carried, 100, "with the other 100 carried")
	expect(handlers.CorpseTake(other, bodyId, 1), "the Wood looted")
	expectEq(held(other, "Wood").carried, nil, "gathered Wood stays eligible")
end)

test("a chest keeps the carried units of what goes in and comes out", function()
	local part = { Position = Vector3.new(3, 5, 0) }
	stubs.BuildingService.Placed:Fire({ id = "chest-1", pieceId = "Chest", part = part, position = part.Position })
	local alt = inRun({ stack("IronOre", 500, 500) })
	local ok, reason = handlers.ChestPut(alt, "chest-1", slotOf(alt, "IronOre"))
	expect(ok, "stored: " .. tostring(reason))
	local gatherer = inRun({ stack("IronOre", 100) })
	expect(handlers.ChestPut(gatherer, "chest-1", slotOf(gatherer, "IronOre")), "gathered ore joins it")
	local main = inRun({})
	expect(handlers.ChestTake(main, "chest-1", 1), "taken")
	local ore = held(main, "IronOre")
	expectEq(ore.quantity, 600, "one chest stack of 600")
	expectEq(ore.carried, 500, "the 500 carried come out carried")
	expectEq(centerYield(InventoryService.Items(main), "IronOre"), 500 + 100 * 2, "only the 100 gathered double")
end)

test("no service handler errored", function()
	expectEq(#errors, 0, "errors: " .. table.concat(errors, " | "))
end)
