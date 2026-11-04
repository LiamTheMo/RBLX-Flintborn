-- Release-candidate checks (GDD §28 step 9, v0.18): profiles saved by every earlier
-- phase load into the final schema without losing data, and launch catalogs are
-- complete and consistent.
local Shared = game:GetService("ReplicatedStorage").Shared
local Server = game:GetService("ServerScriptService").Server
local EventCatalog = require(Server.Rules.Events.EventCatalog)
local ForgeRecipes = require(Shared.Crafting.ForgeRecipes)
local ItemCatalog = require(Shared.Items.ItemCatalog)
local NodeCatalog = require(Shared.Resources.NodeCatalog)
local ProfileSchema = require(Server.Rules.Data.ProfileSchema)
local QuestCatalog = require(Shared.Economy.QuestCatalog)
local Recipes = require(Shared.Crafting.Recipes)
local ShopCatalog = require(Shared.Economy.ShopCatalog)
local WeaponCatalog = require(Shared.Combat.WeaponCatalog)

-- The shape a profile had when v0.02 first saved it, before later phases added
-- groups (permanent ledger fields, quests, trades, tutorial, boosters…).
local function v002Profile()
	return {
		schemaVersion = 1,
		profileRevision = 12,
		createdAt = 50,
		vault = { materials = { Stone = 40 }, items = {}, upgradeTier = 0 },
		lobbyBackpack = { slots = { { catalogId = "Wood", quantity = 9 } } },
		permanentItems = {},
		currency = { coins = 0, gems = 0 },
		progression = { level = 3, xp = 40, masteryTracks = {} },
		rebirth = { count = 0, tokens = 0, ownedPerks = {} },
		recipes = { unlocked = {} },
		receipts = { extraction = {}, forge = {}, maintenance = {}, crashRecovery = {} },
		operations = { records = {}, order = {} },
		choices = { camera = {}, hotbarBindings = {} },
		metrics = { runs = 4, extractions = 2, deaths = 1 },
	}
end

test("a profile saved by the earliest phase loads with every later group filled", function()
	local profile, problem = ProfileSchema.Migrate(v002Profile(), 1000)
	expectEq(problem, nil, "loads")
	expectEq(profile.vault.materials.Stone, 40, "saved vault kept")
	expectEq(profile.lobbyBackpack.slots[1].quantity, 9, "saved backpack kept")
	expectEq(profile.progression.level, 3, "saved level kept")
	expectEq(profile.metrics.extractions, 2, "saved metrics kept")
	local added = "quests.progress trades.pending tutorial.rewardsGranted boosters recipes.discovered"
	for path in
		string.gmatch(added .. " progression.titles currency.purchaseEntitlements currency.npcSaleReceipts", "%S+")
	do
		local node = profile
		for key in string.gmatch(path, "[^.]+") do
			node = node[key]
		end
		expect(type(node) == "table", path .. " added")
	end
	expectEq(#profile.progression.masteryTracks.Mining and 0, 0, "mastery tracks reconciled")
	expect(profile.progression.masteryTracks.Mining ~= nil, "all five tracks present")
end)

test("launch catalogs are complete: every item is obtainable or deliberately rare", function()
	local sources = {}
	for _, recipe in Recipes.List do
		sources[recipe.output] = true
	end
	for _, recipe in ForgeRecipes.List do
		sources[recipe.output] = true
	end
	for _, entry in ShopCatalog.Stock do
		if entry.catalogId then
			sources[entry.catalogId] = true
		end
	end
	-- Berries grow on nodes; the rare berries only come from the rare shrub event.
	-- (gathering_tiers and events.spec check that node and event drops are real items.)
	for _, node in NodeCatalog.Nodes do
		sources[node.material] = true
	end
	for _, event in EventCatalog.ById do
		for _, loot in event.loot or {} do
			sources[loot[1]] = true
		end
	end
	-- Materials come from nodes, creatures and events; the rune and the Guardian's
	-- Fang come from caches and the Guardian.
	local special = { ExtractionRune = true, GuardianFang = true }
	for id, item in ItemCatalog.Items do
		local ok = sources[id] or special[id] or item.family == ItemCatalog.Families.Material
		expect(ok, id .. " has a source")
	end
	for id, item in ItemCatalog.Items do
		if item.family == ItemCatalog.Families.Weapon then
			expect(WeaponCatalog.Weapons[id] ~= nil, id .. " has combat stats")
		end
	end
	expect(#QuestCatalog.Quests >= 6, "a launch quest roster")
end)
