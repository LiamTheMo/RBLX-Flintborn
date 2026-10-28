-- Crafting stations (Workbench, Furnace, Anvil, Cauldron), timed smelting, the
-- building tier ladder and planter crops (GDD §51). The station and smelting
-- rules are checked directly; CraftingService is driven against fake services so
-- a smelt is shown to take its inputs once, grant once and stop cleanly.

local Shared = game:GetService("ReplicatedStorage").Shared

local BuildRules = require(Shared.Building.BuildRules)
local CraftingRules = require(Shared.Crafting.CraftingRules)
local InventoryRules = require(Shared.Inventory.InventoryRules)
local ItemCatalog = require(Shared.Items.ItemCatalog)
local Recipes = require(Shared.Crafting.Recipes)
local Signal = require(Shared.Core.Signal)
local StructureCatalog = require(Shared.Building.StructureCatalog)
local Tiers = require(Shared.Items.Tiers)

-- Stations and recipes ------------------------------------------------------------

test("every recipe crafts by hand or at a buildable station", function()
	for _, recipe in Recipes.List do
		local station = CraftingRules.StationFor(recipe)
		expect(
			recipe.station == Recipes.Anywhere or station ~= nil,
			recipe.id .. " has a known station (" .. recipe.station .. ")"
		)
	end
	for _, station in CraftingRules.STATIONS do
		expect(StructureCatalog.Pieces[station] ~= nil, station .. " can be built")
		expect(table.find(StructureCatalog.ORDER, station) ~= nil, station .. " is in the build palette")
	end
	expect(CraftingRules.IsStation("Anvil") and CraftingRules.IsStation("Cauldron"), "new stations are tagged")
	expect(not CraftingRules.IsStation("Chest") and not CraftingRules.IsStation("Anywhere"), "others are not")
	expectEq(Recipes.Get("SilverSword").station, Recipes.Anvil, "silver gear at the anvil")
	expectEq(Recipes.Get("JadeDagger").station, Recipes.Anvil, "jade at the anvil")
	expectEq(Recipes.Get("Potion").station, Recipes.Cauldron, "potions at the cauldron")
	expectEq(CraftingRules.Refusal("Anvil"), "NeedsAnvil", "refusal code")
end)

test("smelting is 1 ore to 1 bar at the furnace, timed by metal", function()
	local expected = { Copper = 2, Iron = 3, Silver = 4, Cobalt = 5, Mithril = 6, Adamantine = 8 }
	for metal, seconds in expected do
		local tier = Tiers.Get(metal)
		local recipe = Recipes.Get(tier.material)
		expect(recipe ~= nil, metal .. " bar recipe")
		expectEq(recipe.station, Recipes.Furnace, metal .. " smelts at the furnace")
		expectEq(recipe.inputs[tier.ore], 1, metal .. " takes one ore")
		expectEq(recipe.quantity, 1, metal .. " makes one bar")
		expectEq(recipe.seconds, seconds, metal .. " smelt time")
		expect(CraftingRules.IsTimed(recipe), metal .. " is timed")
	end
	expect(not CraftingRules.IsTimed(Recipes.Get("CookedMeat")), "cooking is instant")
	expectEq(CraftingRules.TotalSeconds(Recipes.Get("IronBar"), 5), 15, "a batch of 5 takes 5 × 3 s")
end)

test("batch counts: nil is one, zero stops, only timed recipes take more", function()
	local bar, sword = Recipes.Get("CopperBar"), Recipes.Get("StoneSword")
	expectEq(CraftingRules.BatchCount(bar, nil), 1, "default one")
	expectEq(CraftingRules.BatchCount(bar, 0), 0, "zero stops")
	expectEq(CraftingRules.BatchCount(bar, CraftingRules.MAX_BATCH), CraftingRules.MAX_BATCH, "up to the cap")
	expectEq(CraftingRules.BatchCount(bar, CraftingRules.MAX_BATCH + 1), nil, "not above it")
	expectEq(CraftingRules.BatchCount(bar, 1.5), nil, "whole numbers only")
	expectEq(CraftingRules.BatchCount(bar, -1), nil, "no negatives")
	expectEq(CraftingRules.BatchCount(bar, "3"), nil, "numbers only")
	expectEq(CraftingRules.BatchCount(sword, 2), nil, "instant recipes craft one at a time")
	expectEq(CraftingRules.BatchCount(sword, 1), 1, "one is fine")
	expectEq(CraftingRules.BatchInputs(bar, 4).CopperOre, 4, "inputs scale with the batch")
end)

test("a job stops for every interruption, in a fixed order", function()
	local ok =
		{ atRisk = true, sameCharacter = true, alive = true, downed = false, stationStanding = true, distance = 4 }
	local function with(changes)
		local check = table.clone(ok)
		for key, value in changes do
			check[key] = value
		end
		return CraftingRules.Interruption(check)
	end
	expectEq(CraftingRules.Interruption(ok), nil, "close, alive, furnace standing")
	expectEq(with({ atRisk = false }), "NotInRun", "left the run")
	expectEq(with({ alive = false }), "Died", "died")
	expectEq(with({ sameCharacter = false }), "Died", "respawned")
	expectEq(with({ downed = true }), "Downed", "downed")
	expectEq(with({ stationStanding = false }), "StationGone", "furnace destroyed")
	expectEq(with({ distance = CraftingRules.STATION_RANGE + 0.1 }), "MovedAway", "walked off")
	expectEq(with({ distance = false }), "MovedAway", "no body")
	expectEq(with({ distance = CraftingRules.STATION_RANGE }), nil, "at the edge is still near")
end)

test("job progress advances one unit at a time", function()
	local job = CraftingRules.NewJob(Recipes.Get("IronBar"), 2, 100, "furnace", "body")
	expect(not CraftingRules.UnitDue(job, 102.9), "not before 3 s")
	expect(CraftingRules.UnitDue(job, 103), "due at 3 s")
	expect(not CraftingRules.Advance(job), "one of two")
	expectEq(job.unitEndsAt, 106, "the next unit ends 3 s later")
	local progress, left = CraftingRules.Progress(job.done, job.count, job.unitEndsAt, 3, 104.5)
	expectNear(progress, 0.75, 1e-9, "halfway through the second of two")
	expectNear(left, 1.5, 1e-9, "1.5 s left on this bar")
	expect(CraftingRules.Advance(job), "done")
	expect(not CraftingRules.UnitDue(job, 1000), "a finished job is never due")
end)

test("the menu groups by category and tier and filters by what is nearby", function()
	expectEq(CraftingRules.Category(Recipes.Get("IronSword")), "Weapons", "weapons")
	expectEq(CraftingRules.Category(Recipes.Get("FlintArrow")), "Weapons", "arrows sit with weapons")
	expectEq(CraftingRules.Category(Recipes.Get("SilverPickaxe")), "Tools", "tools")
	expectEq(CraftingRules.Category(Recipes.Get("BoneChest")), "Armor", "armor")
	expectEq(CraftingRules.Category(Recipes.Get("CobaltBar")), "Bars", "smelting")
	expectEq(CraftingRules.Category(Recipes.Get("Potion")), "Consumables", "potions")
	expectEq(CraftingRules.Category(Recipes.Get("FireBomb")), "Other", "siege")
	expectEq(CraftingRules.Tier(Recipes.Get("MithrilSpear")), "Mithril", "gear tier")
	expectEq(CraftingRules.Tier(Recipes.Get("AdamantineBar")), "Adamantine", "a bar's tier is its metal")
	expectEq(CraftingRules.Tier(Recipes.Get("Potion")), nil, "potions have no tier")

	local tiers = CraftingRules.TiersIn(Recipes.List)
	expectEq(tiers[1], "Wood", "ladder order starts at Wood")
	expectEq(tiers[#tiers], "Adamantine", "and ends at Adamantine")

	local nearby = { Furnace = true }
	local anvilSword, bar = Recipes.Get("SilverSword"), Recipes.Get("SilverBar")
	expect(CraftingRules.Matches(anvilSword, {}, nearby), "no filter shows everything")
	expect(not CraftingRules.Matches(anvilSword, { hereOnly = true }, nearby), "anvil gear hidden away from one")
	expect(CraftingRules.Matches(bar, { hereOnly = true }, nearby), "smelting shown at a furnace")
	expect(CraftingRules.Matches(Recipes.Get("WoodenSpear"), { hereOnly = true }, {}), "hand recipes anywhere")
	expect(not CraftingRules.Matches(bar, { tier = "Iron" }, nearby), "tier filter")
	expect(CraftingRules.Matches(bar, { tier = "Silver", category = "Bars" }, nearby), "tier and category")

	local sorted = CraftingRules.Sorted(Recipes.List)
	expectEq(#sorted, #Recipes.List, "every recipe listed once")
	local lastCategory, lastTier = 0, 0
	local order = {}
	for index, category in CraftingRules.CATEGORIES do
		order[category.id] = index
	end
	local ladder = {}
	for index, tier in Tiers.Ladder do
		ladder[tier.id] = index
	end
	local inOrder = true
	for _, recipe in sorted do
		local category = order[CraftingRules.Category(recipe)]
		local tier = ladder[CraftingRules.Tier(recipe) or ""] or 0
		if category < lastCategory or (category == lastCategory and tier < lastTier) then
			inOrder = false
		end
		lastCategory, lastTier = category, tier
	end
	expect(inOrder, "grouped by category, then up the ladder")
end)

-- Building ladder and planters ---------------------------------------------------

test("walls, floors, doors and roofs come in all eight tiers; stations in one", function()
	expectEq(#StructureCatalog.TIERS, 8, "Wood to Adamantine")
	expectEq(StructureCatalog.TIERS[1], "Wood", "first")
	expectEq(StructureCatalog.TIERS[8], "Adamantine", "last")
	for _, pieceId in { "Wall", "Floor", "Door", "Roof" } do
		expect(BuildRules.IsTiered(pieceId), pieceId .. " is tiered")
		local tiers = BuildRules.TiersOf(pieceId)
		expectEq(#tiers, 8, pieceId .. " in every tier")
		local lastHp = 0
		for index, tier in StructureCatalog.TIERS do
			expectEq(tiers[index], tier, pieceId .. " tier order")
			local piece, stats = StructureCatalog.Get(pieceId, tier)
			expect(piece ~= nil and stats ~= nil, pieceId .. " " .. tier .. " accepted")
			if stats then
				expect(stats.hp > lastHp, pieceId .. " " .. tier .. " is stronger than the tier below")
				lastHp = stats.hp
				expectEq(stats.material, tier, pieceId .. " " .. tier .. " material")
				local metal = Tiers.Get(tier)
				if metal and metal.ore then
					expect((stats.cost[metal.material] or 0) > 0, pieceId .. " " .. tier .. " costs its bars")
				end
				for catalogId in stats.cost do
					expect(ItemCatalog.Get(catalogId) ~= nil, pieceId .. " " .. tier .. " cost item " .. catalogId)
				end
			end
		end
	end
	local _, wall = StructureCatalog.Get("Wall", "Copper")
	expectEq(wall.hp, 1000, "Copper wall 1,000 HP")
	_, wall = StructureCatalog.Get("Wall", "Iron")
	expectEq(wall.hp, 1250, "Iron wall 1,250 HP")
	for _, pieceId in { "Anvil", "Cauldron", "Workbench", "Furnace", "Chest" } do
		expect(not BuildRules.IsTiered(pieceId), pieceId .. " has one tier")
		expectEq(BuildRules.TierFor(pieceId, "Mithril"), "Wood", pieceId .. " ignores the chosen tier")
	end
	local _, anvil = StructureCatalog.Get("Anvil", "Wood")
	expectEq(anvil.cost.IronBar, 20, "anvil costs 20 Iron Bars")
	local _, cauldron = StructureCatalog.Get("Cauldron", "Wood")
	expectEq(cauldron.cost.CopperBar, 5, "cauldron costs 5 Copper Bars")
	expectEq(StructureCatalog.Get("Wall", "Bronze"), StructureCatalog.Pieces.Wall, "piece found")
	expect(select(2, StructureCatalog.Get("Wall", "Bronze")) == nil, "an unknown tier is refused")
	expectEq(BuildRules.TierFor("Wall", "Cobalt"), "Cobalt", "a tiered piece keeps the choice")
	expectEq(BuildRules.CycleTier("Wall", "Adamantine", 1), "Wood", "stepping up wraps")
	expectEq(BuildRules.CycleTier("Wall", "Wood", -1), "Adamantine", "stepping down wraps")
	expectEq(BuildRules.CycleTier("Wall", "Iron", 1), "Silver", "one step")
	expectEq(BuildRules.StructureDamage(10, "Pickaxe", anvil.material), 15, "pickaxes break the iron anvil")
end)

test("planters grow four crops from real items", function()
	expectEq(#StructureCatalog.CROP_ORDER, 4, "four crops")
	for _, cropId in StructureCatalog.CROP_ORDER do
		local crop = StructureCatalog.Crops[cropId]
		expect(crop ~= nil, cropId .. " defined")
		for catalogId in crop.seed do
			expect(ItemCatalog.Get(catalogId) ~= nil, cropId .. " seed " .. catalogId)
		end
		expect(ItemCatalog.Get(crop.yield.catalogId) ~= nil, cropId .. " yield")
		expect(crop.seconds > 0, cropId .. " grows")
	end
	expectEq(StructureCatalog.Crops.Redberry.yield.catalogId, "Redberry", "redberries")
	expectEq(StructureCatalog.Crops.Sweetberry.yield.catalogId, "Sweetberry", "sweetberries")
end)

-- CraftingService against fake services -----------------------------------------

local clock = 1000
local Players = { PlayerRemoving = Signal.new(), PlayerAdded = Signal.new() }
local tagged = {}
local guids = 0
local fakes = {
	Players = Players,
	CollectionService = {
		GetTagged = function(_, tag)
			return tagged[tag] or {}
		end,
	},
	HttpService = {
		GenerateGUID = function()
			guids += 1
			return ("guid-%d"):format(guids)
		end,
	},
}
local originalGetService = game.GetService
game.GetService = function(self, name)
	return fakes[name] or originalGetService(self, name)
end
workspace = {
	GetServerTimeNow = function()
		return clock
	end,
}
-- The smelting loop runs as a coroutine that each pump() advances by one tick.
local loops = {}
task = {
	wait = function()
		coroutine.yield()
	end,
	spawn = function(fn, ...)
		local co = coroutine.create(fn)
		coroutine.resume(co, ...)
		table.insert(loops, co)
	end,
}
local function pump()
	for _, co in loops do
		local ok, err = coroutine.resume(co)
		assert(ok, err)
	end
end

local dropped = {}
local stubs = {
	BuildingService = { Removing = Signal.new(), Placed = Signal.new() },
	DownedService = {
		IsDowned = function(player)
			return player.downed == true
		end,
	},
	DropService = {
		Spawn = function(item)
			table.insert(dropped, item)
		end,
	},
	InventoryService = {
		Get = function(player)
			return player.inventory
		end,
		Publish = function() end,
		Notify = function(player, message)
			table.insert(player.notes, message)
		end,
	},
	ModifierService = {
		Sum = function()
			return 0
		end,
		Get = function()
			return {}
		end,
	},
	ProfileService = {
		GetProfile = function()
			return nil
		end,
	},
	ProgressionService = { GrantXp = function() end, GrantMastery = function() end },
	WorldAdmissionService = {
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
local Remotes = require(Shared.Net.Remotes)
local handlers = {}
Remotes.Handle = function(name, fn)
	handlers[name] = fn
end
PlaceConfig.IsWorld = function()
	return true
end
local CraftingService = require(game:GetService("ServerScriptService").Server.Services.CraftingService)
CraftingService.CRAFT_SECONDS = 0
CraftingService.Start()

local function station(tag: string, position)
	local part = {
		Position = position,
		Parent = "PlayerStructures",
		IsA = function(_, className)
			return className == "BasePart"
		end,
	}
	tagged[tag] = tagged[tag] or {}
	table.insert(tagged[tag], part)
	return part
end

local function body()
	local humanoid = { Health = 100 }
	local root = { Position = Vector3.new(0, 0, 0) }
	return {
		humanoid = humanoid,
		root = root,
		FindFirstChild = function(_, name)
			return if name == "HumanoidRootPart" then root else nil
		end,
		FindFirstChildOfClass = function(_, className)
			return if className == "Humanoid" then humanoid else nil
		end,
	}
end

local nextUserId = 0
local function newPlayer(items)
	nextUserId += 1
	local player = {
		UserId = nextUserId,
		Parent = Players,
		Character = body(),
		atRisk = true,
		attributes = {},
		notes = {},
		inventory = InventoryRules.New(),
	}
	function player.SetAttribute(self, key, value)
		self.attributes[key] = value
	end
	function player.GetAttribute(self, key)
		return self.attributes[key]
	end
	for catalogId, quantity in items do
		InventoryRules.Add(player.inventory, { catalogId = catalogId, quantity = quantity })
	end
	return player
end

-- Stacks by quantity, unique gear by instance.
local function count(player, catalogId)
	local total = 0
	for _, entry in InventoryRules.Items(player.inventory) do
		if entry.catalogId == catalogId then
			total += entry.quantity or 1
		end
	end
	return total
end

local function craft(player, recipeId, quantity, requestId)
	guids += 1
	return handlers.Craft(player, requestId or ("req-" .. guids), recipeId, quantity)
end

local furnace = station("Furnace", Vector3.new(4, 0, 0))

test("anvil and cauldron recipes need a built anvil or cauldron nearby", function()
	local player = newPlayer({ SilverBar = 6, Wood = 3, Fiber = 2, Resin = 1, Redberry = 5, Herbs = 5 })
	local ok, reason = craft(player, "SilverSword")
	expect(not ok and reason == "NeedsAnvil", "no anvil: " .. tostring(reason))
	ok, reason = craft(player, "Potion")
	expect(not ok and reason == "NeedsCauldron", "no cauldron: " .. tostring(reason))
	expectEq(count(player, "SilverBar"), 6, "nothing taken")
	local far = station("Anvil", Vector3.new(CraftingRules.STATION_RANGE + 5, 0, 0))
	ok, reason = craft(player, "SilverSword")
	expectEq(reason, "NeedsAnvil", "an anvil out of reach does not count")
	far.Position = Vector3.new(3, 0, 0)
	ok, reason = craft(player, "SilverSword")
	expect(ok, "crafted at the anvil: " .. tostring(reason))
	expectEq(count(player, "SilverBar"), 0, "bars used")
	expectEq(count(player, "SilverSword"), 1, "sword made")
	station("Cauldron", Vector3.new(0, 0, 3))
	ok, reason = craft(player, "Potion")
	expect(ok, "brewed at the cauldron: " .. tostring(reason))
	expectEq(count(player, "Potion"), 1, "potion made")
	expectEq(count(player, "Redberry"), 0, "berries used")
	ok, reason = craft(player, "IronSword")
	expectEq(reason, "NeedsWorkbench", "workbench recipes still need a workbench")
end)

test("a smelt batch takes each ore once as each bar finishes", function()
	local player = newPlayer({ CopperOre = 3 })
	local ok, reason = craft(player, "CopperBar", 3)
	expect(ok, "started: " .. tostring(reason))
	expectEq(count(player, "CopperOre"), 3, "nothing taken up front")
	expectEq(player.attributes.SmeltRecipe, "CopperBar", "progress published")
	expectEq(player.attributes.SmeltCount, 3, "batch size published")
	expectEq(player.attributes.SmeltEndsAt, clock + 2, "first bar due in 2 s")

	ok, reason = craft(player, "CopperBar", 1)
	expect(not ok and reason == "Busy", "one job at a time: " .. tostring(reason))
	for _ = 1, 5 do
		craft(player, "CopperBar", 3)
	end
	clock += 1.9
	pump()
	expectEq(count(player, "CopperBar"), 0, "not done before its time")
	clock += 0.1
	pump()
	pump()
	expectEq(count(player, "CopperBar"), 1, "one bar after 2 s (repeated ticks grant once)")
	expectEq(count(player, "CopperOre"), 2, "its ore taken")
	expectEq(player.attributes.SmeltDone, 1, "progress updated")
	clock += 2
	pump()
	clock += 2
	pump()
	expectEq(count(player, "CopperBar"), 3, "three bars after 6 s")
	expectEq(count(player, "CopperOre"), 0, "three ore taken")
	expectEq(player.attributes.SmeltRecipe, nil, "progress cleared")
	expect(string.find(player.notes[#player.notes], "Smelted 3") ~= nil, "told it finished")
	clock += 10
	pump()
	expectEq(count(player, "CopperBar"), 3, "nothing more after the job")
	ok = craft(player, "CopperBar", 1)
	expect(not ok, "no ore left to start another")
end)

test("a refused or repeated request starts nothing", function()
	local player = newPlayer({ IronOre = 3 })
	local ok, reason = craft(player, "IronBar", 5)
	expectEq(reason, "MissingIngredients", "a batch needs all its ore at the start")
	ok, reason = craft(player, "IronBar", CraftingRules.MAX_BATCH + 1)
	expectEq(reason, "BadQuantity", "over the cap")
	ok, reason = craft(player, "WoodenSpear", 2)
	expectEq(reason, "BadQuantity", "instant recipes are one at a time")
	ok, reason = craft(player, "IronBar", 1, "same-id")
	expect(ok, "started")
	ok, reason = craft(player, "IronBar", 1, "same-id")
	expectEq(reason, "Busy", "busy is checked before the id is spent")
	clock += 3
	pump()
	expectEq(count(player, "IronBar"), 1, "one bar")
	ok, reason = craft(player, "IronBar", 1, "same-id")
	expectEq(reason, "Duplicate", "a used request id is applied once")
	expectEq(count(player, "IronOre"), 2, "two ore left")
	local stranger = newPlayer({ IronOre = 1 })
	stranger.Character.root.Position = Vector3.new(100, 0, 0)
	ok, reason = craft(stranger, "IronBar")
	expectEq(reason, "NeedsFurnace", "smelting needs a furnace nearby")
end)

test("moving away, dying, being downed or leaving the run stops a smelt", function()
	local cases = {
		{
			"MovedAway",
			"moved away",
			function(player)
				player.Character.root.Position = Vector3.new(40, 0, 0)
			end,
		},
		{
			"Died",
			"died",
			function(player)
				player.Character.humanoid.Health = 0
			end,
		},
		{
			"Respawned",
			"died",
			function(player)
				player.Character = body()
			end,
		},
		{
			"Downed",
			"downed",
			function(player)
				player.downed = true
			end,
		},
		{
			"NotInRun",
			"left the run",
			function(player)
				player.atRisk = false
			end,
		},
	}
	for _, case in cases do
		local name, text, interrupt = case[1], case[2], case[3]
		local player = newPlayer({ SilverOre = 2 })
		local ok, reason = craft(player, "SilverBar", 2)
		expect(ok, name .. " started: " .. tostring(reason))
		clock += 4
		pump()
		expectEq(count(player, "SilverBar"), 1, name .. ": first bar made")
		clock += 3.9
		interrupt(player)
		pump()
		clock += 10
		pump()
		expectEq(count(player, "SilverBar"), 1, name .. ": no second bar")
		expectEq(count(player, "SilverOre"), 1, name .. ": second ore kept")
		expectEq(player.attributes.SmeltRecipe, nil, name .. ": progress cleared")
		local note = player.notes[#player.notes] or ""
		expect(string.find(note, text) ~= nil, name .. ": told why (" .. note .. ")")
	end
end)

test("a destroyed furnace, a Stop or leaving the server ends the job cleanly", function()
	local own = station("Furnace", Vector3.new(-4, 0, 0))
	-- Two furnaces in reach: the job binds to the nearer one (this one, 1 stud away).
	local player = newPlayer({ CobaltOre = 3 })
	player.Character.root.Position = Vector3.new(-3, 0, 0)
	local ok = craft(player, "CobaltBar", 3)
	expect(ok, "started")
	expectEq(craft(player, "CobaltBar", 1), false, "a second furnace does not allow a second job")
	stubs.BuildingService.Removing:Fire({ part = own })
	expectEq(player.attributes.SmeltRecipe, nil, "stopped at once")
	expect(string.find(player.notes[#player.notes], "destroyed") ~= nil, "told why")
	clock += 20
	pump()
	expectEq(count(player, "CobaltBar"), 0, "no bar")
	expectEq(count(player, "CobaltOre"), 3, "no ore taken")

	own.Parent = nil
	player.Character.root.Position = Vector3.new(0, 0, 0)
	ok = craft(player, "CobaltBar", 2)
	expect(ok, "restarted at the other furnace")
	clock += 5
	pump()
	expectEq(count(player, "CobaltBar"), 1, "one bar")
	ok = craft(player, "CobaltBar", 0)
	expect(ok, "stop accepted")
	clock += 20
	pump()
	expectEq(count(player, "CobaltBar"), 1, "stop keeps the bars made")
	expectEq(count(player, "CobaltOre"), 2, "and takes nothing more")

	furnace.Parent = nil
	ok = craft(player, "CobaltBar", 1)
	expect(not ok, "no standing furnace left in reach")
	furnace.Parent = "PlayerStructures"
	ok = craft(player, "CobaltBar", 2)
	expect(ok, "started again")
	furnace.Parent = nil
	clock += 5
	pump()
	expectEq(count(player, "CobaltBar"), 1, "a furnace gone without a removal signal still stops it")
	furnace.Parent = "PlayerStructures"

	local leaver = newPlayer({ MithrilOre = 2 })
	expect(craft(leaver, "MithrilBar", 2), "started")
	Players.PlayerRemoving:Fire(leaver)
	leaver.Parent = nil
	clock += 20
	pump()
	expectEq(count(leaver, "MithrilBar"), 0, "nothing granted after leaving")
	expectEq(count(leaver, "MithrilOre"), 2, "nothing taken")
end)

test("ore taken away mid-smelt stops the job without a free bar", function()
	local player = newPlayer({ AdamantineOre = 2 })
	expect(craft(player, "AdamantineBar", 2), "started")
	InventoryRules.RemoveAll(player.inventory, { AdamantineOre = 2 })
	clock += 8
	pump()
	expectEq(count(player, "AdamantineBar"), 0, "no bar from nothing")
	expectEq(player.attributes.SmeltRecipe, nil, "stopped")
	expect(string.find(player.notes[#player.notes], "ran out of ore") ~= nil, "told why")
end)
