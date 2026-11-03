-- The rebuilt item catalog (GDD §51, docs/design/ITEM_CATALOG.md): pre-release saves lose
-- every item whose catalogId no longer exists, wherever the profile holds it, and
-- the cleanup is safe on every load. Also covers the generated Permanent
-- conversions (cost, unlock gates, tier browsing), the starter shop's prices
-- against merchant values, and which vault materials and consumables trade —
-- through the real TradeService session flow against fake Roblox services.

local Shared = game:GetService("ReplicatedStorage").Shared

local lobby = require(game:GetService("ServerStorage").TestSupport.LobbyTrade).new()
local handlers, pushed, profiles = lobby.handlers, lobby.pushed, lobby.profiles

local EconomyRules = require(Shared.Economy.EconomyRules)
local ForgeRecipes = require(Shared.Crafting.ForgeRecipes)
local ForgeRules = require(Shared.Crafting.ForgeRules)
local ItemCatalog = require(Shared.Items.ItemCatalog)
local ProfileSchema = require(Shared.Data.ProfileSchema)
local Recipes = require(Shared.Crafting.Recipes)
local ShopCatalog = require(Shared.Economy.ShopCatalog)
local TradeRules = require(Shared.Economy.TradeRules)

-- Helpers -------------------------------------------------------------------------

local DAY = 86400 * 20000
local OWNER = 7

-- Every catalogId the old catalog had that the rebuilt one dropped (§8).
local REMOVED = {
	"Iron",
	"Arrow",
	"Sickle",
	"BasicPickaxe",
	"BasicBow",
	"Berries",
	"WoodHead",
	"WoodChest",
	"WoodLegs",
	"StoneHead",
	"StoneChest",
	"StoneLegs",
	"HerbSeeds",
}

local function gear(id: string, catalogId: string, location: string?, extra: any?)
	local item = {
		instanceId = id,
		catalogId = catalogId,
		ownerId = OWNER,
		location = location or "LobbyBackpack",
		qualityRoll = 0.02,
	}
	for key, value in extra or {} do
		item[key] = value
	end
	return item
end

local function deepEqual(a, b): boolean
	if type(a) ~= "table" or type(b) ~= "table" then
		return a == b
	end
	for key, value in a do
		if not deepEqual(value, b[key]) then
			return false
		end
	end
	for key in b do
		if a[key] == nil then
			return false
		end
	end
	return true
end

-- Every catalogId the profile still names, with where it was found.
local function namedIds(profile)
	local found = {}
	local function list(where, items)
		for _, item in items or {} do
			table.insert(found, { where = where, id = item.catalogId })
		end
	end
	local function map(where, entries)
		for catalogId in entries or {} do
			table.insert(found, { where = where, id = catalogId })
		end
	end
	list("backpack", profile.lobbyBackpack.slots)
	list("vault items", profile.vault.items)
	map("vault materials", profile.vault.materials)
	list("transit", profile.transit and profile.transit.items)
	for _, receipt in profile.receipts.maintenance do
		list("maintenance", receipt.items)
	end
	for _, receipt in profile.receipts.extraction do
		map("extraction receipt", receipt.vaulted)
		map("extraction receipt", receipt.toBackpack)
		map("extraction receipt", receipt.deleted)
	end
	for _, receipt in profile.receipts.forge do
		table.insert(found, { where = "forge receipt", id = receipt.output.catalogId })
	end
	list("run loadout", profile.progression.currentRun and profile.progression.currentRun.loadout)
	for _, pending in profile.trades.pending do
		list("trade gave", pending.gave.items)
		list("trade received", pending.received.items)
		map("trade gave", pending.gave.materials)
		map("trade received", pending.received.materials)
	end
	for _, entry in profile.permanentItems do
		table.insert(found, { where = "permanent ledger", id = entry.catalogId })
	end
	map("discovered", profile.recipes.discovered)
	if profile.vault.lastOverflow then
		map("overflow", profile.vault.lastOverflow.deleted)
	end
	return found
end

-- A pre-release save holding removed items everywhere a profile keeps items,
-- next to valid ones that must survive untouched.
local function legacyProfile()
	local profile = ProfileSchema.Default(0)
	profile.lobbyBackpack.slots = {
		gear("b1", "BasicPickaxe"),
		gear("b2", "IronSword"),
		{ catalogId = "Arrow", quantity = 40 },
		{ catalogId = "FlintArrow", quantity = 20 },
		gear("b3", "WoodChest"),
		{ catalogId = "Berries", quantity = 5 },
		{ catalogId = "Redberry", quantity = 3 },
	}
	profile.vault.items = {
		gear("v1", "Sickle", "Vault"),
		gear("v2", "StoneHead", "Vault"),
		gear("v3", "StonePickaxe", "Vault"),
		gear("v4", "BasicBow", "Vault", { permanent = true, ownershipVersion = 1 }),
		gear("v5", "IronPickaxe", "Vault", { permanent = true, ownershipVersion = 2 }),
		{ catalogId = "Sunberry", quantity = 4 },
	}
	profile.vault.materials = { Iron = 120, Berries = 30, Wood = 500, IronOre = 40, AncientEmber = 2 }
	profile.vault.lastOverflow = { at = 5, deleted = { Iron = 3, Stone = 10 } }
	profile.transit = {
		reservationId = "r1",
		createdAt = 1,
		status = "Reserved",
		items = { gear("t1", "WoodLegs", "Transit"), gear("t2", "CopperSpear", "Transit") },
	}
	profile.receipts.maintenance.m1 = {
		at = 2,
		status = "Pending",
		items = { { catalogId = "Arrow", quantity = 12 }, gear("m2", "StoneSword", "Carried") },
	}
	profile.receipts.extraction.e1 = {
		at = 3,
		kind = "Fixed",
		multiplier = 1,
		vaulted = { Iron = 10, Wood = 4 },
		toBackpack = { Sickle = 1, StoneSpear = 1 },
		deleted = { Berries = 2 },
		shown = true,
	}
	profile.receipts.forge.f1 =
		{ at = 4, recipeId = "PermanentBasicBow", output = { catalogId = "BasicBow", instanceId = "v4" } }
	profile.receipts.forge.f2 =
		{ at = 5, recipeId = "PermanentIronPickaxe", output = { catalogId = "IronPickaxe", instanceId = "v5" } }
	profile.progression.currentRun = {
		runId = "run1",
		jobId = "elsewhere",
		loadout = {
			{ catalogId = "BasicPickaxe", instanceId = "l1" },
			{ catalogId = "WoodenSpear", instanceId = "l2" },
		},
	}
	profile.trades.pending.t1 = {
		counterpart = 9,
		at = 6,
		gave = { items = { gear("g1", "StoneLegs") }, materials = { Iron = 5 }, gems = 0 },
		received = { items = { gear("g2", "BoneSpear") }, materials = { AncientEmber = 1 }, gems = 0 },
	}
	profile.permanentItems = {
		v4 = { catalogId = "BasicBow", qualityRoll = 0.02, ownershipVersion = 1, acquiredAt = 1 },
		v5 = { catalogId = "IronPickaxe", qualityRoll = 0.02, ownershipVersion = 2, acquiredAt = 1 },
	}
	profile.recipes.discovered = { Iron = true, Berries = true, IronOre = true, AncientEmber = true }
	profile.recipes.unlocked = {
		PermanentBasicPickaxe = { unlockSource = "Discovery", unlockedAt = 1 },
		ForgeIronSword = { unlockSource = "Discovery", unlockedAt = 1 },
	}
	return profile
end

local function idsOf(items)
	local ids = {}
	for _, item in items do
		table.insert(ids, item.instanceId or item.catalogId)
	end
	return table.concat(ids, ",")
end

-- Migration -----------------------------------------------------------------------

test("loading a pre-release save deletes removed items everywhere and keeps the rest", function()
	for _, catalogId in REMOVED do
		expectEq(ItemCatalog.Get(catalogId), nil, catalogId .. " is not an item")
	end
	local profile = assert(ProfileSchema.Migrate(legacyProfile(), 10))
	expectEq(idsOf(profile.lobbyBackpack.slots), "b2,FlintArrow,Redberry", "backpack")
	expectEq(profile.lobbyBackpack.slots[1].qualityRoll, 0.02, "a kept item is untouched")
	expectEq(idsOf(profile.vault.items), "v3,v5,Sunberry", "vault items")
	expectEq(profile.vault.materials.Iron, nil, "the old Iron material is gone")
	expectEq(profile.vault.materials.Berries, nil, "plain Berries are gone")
	expectEq(profile.vault.materials.Wood, 500, "Wood stays")
	expectEq(profile.vault.materials.IronOre, 40, "Iron Ore stays")
	expectEq(profile.vault.materials.AncientEmber, 2, "Ancient Ember stays")
	expectEq(profile.vault.lastOverflow.deleted.Iron, nil, "overflow notice")
	expectEq(profile.vault.lastOverflow.deleted.Stone, 10, "overflow keeps Stone")
	expectEq(idsOf(profile.transit.items), "t2", "transit reservation")
	expectEq(profile.transit.reservationId, "r1", "the reservation itself survives")
	expectEq(idsOf(profile.receipts.maintenance.m1.items), "m2", "maintenance escrow")
	local receipt = profile.receipts.extraction.e1
	expect(receipt.vaulted.Iron == nil and receipt.vaulted.Wood == 4, "extraction receipt vaulted")
	expect(receipt.toBackpack.Sickle == nil and receipt.toBackpack.StoneSpear == 1, "extraction receipt backpack")
	expectEq(next(receipt.deleted), nil, "extraction receipt deleted")
	expectEq(profile.receipts.forge.f1, nil, "a forge receipt for a removed item")
	expect(profile.receipts.forge.f2 ~= nil, "a forge receipt for a kept item")
	expectEq(idsOf(profile.progression.currentRun.loadout), "l2", "crash-recovery loadout")
	local pending = profile.trades.pending.t1
	expectEq(#pending.gave.items, 0, "a pending trade gives back no removed item")
	expectEq(pending.gave.materials.Iron, nil, "nor removed material")
	expectEq(idsOf(pending.received.items), "g2", "received gear stays")
	expectEq(pending.received.materials.AncientEmber, 1, "received Ember stays")
	expectEq(profile.permanentItems.v4, nil, "the Permanent ledger drops the Basic Bow")
	expect(profile.permanentItems.v5 ~= nil, "and keeps the Iron Pickaxe")
	expect(profile.recipes.discovered.Iron == nil and profile.recipes.discovered.Berries == nil, "discoveries")
	expect(profile.recipes.discovered.IronOre and profile.recipes.discovered.AncientEmber, "real discoveries stay")
	expectEq(profile.recipes.unlocked.PermanentBasicPickaxe, nil, "a removed Forge recipe unlock")
	expect(profile.recipes.unlocked.ForgeIronSword ~= nil, "a real unlock stays")
	for _, entry in namedIds(profile) do
		expect(ItemCatalog.Get(entry.id) ~= nil, "unknown " .. tostring(entry.id) .. " left in " .. entry.where)
	end
end)

test("the cleanup is idempotent and never touches a clean profile", function()
	local once = assert(ProfileSchema.Migrate(legacyProfile(), 10))
	local twice = assert(ProfileSchema.Migrate(once, 11))
	expect(deepEqual(once, twice), "a second load changes nothing")
	expectEq(ProfileSchema.PruneRetiredItems(twice), 0, "nothing left to remove")
	local fresh = ProfileSchema.Default(0)
	local copy = ProfileSchema.DeepCopy(fresh)
	expectEq(ProfileSchema.PruneRetiredItems(fresh), 0, "a new profile is clean")
	expect(deepEqual(fresh, copy), "and untouched")
	local legacy = legacyProfile()
	expectEq(ProfileSchema.PruneRetiredItems(legacy), 23, "every legacy reference counted once")
end)

test("items from a newer build survive an older server's cleanup", function()
	-- A server still running an older build after a publish must never delete
	-- what a newer build added: only the explicit retired list is pruned.
	local profile = ProfileSchema.Default(0)
	profile.vault.materials.FutureOre = 7
	table.insert(profile.vault.items, gear("future", "FutureBlade", "Vault"))
	profile.permanentItems.future = { catalogId = "FutureBlade" }
	profile.recipes.discovered.FutureOre = true
	profile.recipes.unlocked.PermanentFutureBlade = { unlockSource = "Discovery", unlockedAt = 1 }
	profile.recipes.unlocked.PermanentWoodChest = { unlockSource = "Discovery", unlockedAt = 1 }
	expectEq(ProfileSchema.PruneRetiredItems(profile), 1, "only the retired Wood Chest conversion goes")
	expectEq(profile.vault.materials.FutureOre, 7, "an unknown material is kept")
	expectEq(#profile.vault.items, 1, "an unknown item is kept")
	expect(profile.permanentItems.future ~= nil, "its Permanent ledger entry is kept")
	expect(profile.recipes.discovered.FutureOre, "its discovery is kept")
	expect(profile.recipes.unlocked.PermanentFutureBlade ~= nil, "its Forge unlock is kept")
	expectEq(profile.recipes.unlocked.PermanentWoodChest, nil, "a retired item's conversion is dropped")
end)

test("every current item survives the cleanup", function()
	local profile = ProfileSchema.Default(0)
	local count = 0
	for catalogId in ItemCatalog.Items do
		count += 1
		if ItemCatalog.IsMaterial(catalogId) then
			profile.vault.materials[catalogId] = 1
		elseif ItemCatalog.IsStackable(catalogId) then
			table.insert(profile.lobbyBackpack.slots, { catalogId = catalogId, quantity = 1 })
		else
			table.insert(profile.vault.items, gear("i" .. count, catalogId, "Vault"))
		end
		profile.recipes.discovered[catalogId] = true
	end
	for _, recipe in ForgeRecipes.List do
		profile.recipes.unlocked[recipe.id] = { unlockSource = "Discovery", unlockedAt = 1 }
	end
	local before = ProfileSchema.DeepCopy(profile)
	expectEq(ProfileSchema.PruneRetiredItems(profile), 0, "nothing removed")
	expect(deepEqual(before, profile), "nothing changed")
end)

-- Forge ---------------------------------------------------------------------------

test("every weapon, tool and armor piece has one Permanent conversion at 10x its recipe", function()
	local gearCount = 0
	for id, def in ItemCatalog.Items do
		local family = def.family
		if family == "Weapon" or family == "Tool" or family == "Armor" then
			gearCount += 1
			local recipe = ForgeRecipes.Get("Permanent" .. id)
			expect(recipe ~= nil, id .. " has a conversion")
			if recipe and Recipes.Get(id) then
				expectEq(recipe.kind, ForgeRecipes.Kinds.Permanent, id .. " kind")
				expectEq(recipe.category, "Permanent", id .. " category")
				for input, amount in Recipes.Get(id).inputs do
					expect((recipe.inputs[input] or 0) >= amount * 10, id .. " needs 10x " .. input)
				end
				expect((recipe.inputs.AncientEmber or 0) >= 1, id .. " needs Ancient Ember")
				for _, gate in { "extractions", "level" } do
					expect(type(recipe.unlock[gate]) == "number", id .. " gates on " .. gate)
				end
				expect(table.find(recipe.unlock.discovered, "AncientEmber") ~= nil, id .. " needs Ember discovered")
			end
		end
	end
	local conversions = 0
	for _, recipe in ForgeRecipes.List do
		if recipe.kind == ForgeRecipes.Kinds.Permanent then
			conversions += 1
		end
	end
	expectEq(conversions, gearCount, "one conversion per gear item")
	local adamantine = ForgeRecipes.Get("PermanentAdamantineChest")
	local ember = Recipes.Get("AdamantineChest").inputs.Emberglass * 10
	expect(adamantine.inputs.GuardianHeart == 1 and adamantine.inputs.Emberglass == ember + 3, "Adamantine armor rares")
	local mithril = ForgeRecipes.Get("PermanentMithrilSword")
	expect((mithril.inputs.ChargedCore or 0) >= 3, "Mithril weapon rares")
end)

test("conversions unlock by extractions, level and a discovered Ember", function()
	local profile = ProfileSchema.Default(0)
	local wooden = ForgeRecipes.Get("PermanentWoodenAxe")
	local adamantine = ForgeRecipes.Get("PermanentAdamantineSword")
	expect(not ForgeRules.RequirementsMet(profile, wooden), "nothing at first")
	profile.metrics.extractions = 2
	expect(not ForgeRules.RequirementsMet(profile, wooden), "extractions alone are not enough")
	profile.recipes.discovered.AncientEmber = true
	expect(ForgeRules.RequirementsMet(profile, wooden), "two extractions and an Ember")
	expect(not ForgeRules.RequirementsMet(profile, adamantine), "Adamantine still locked")
	profile.metrics.extractions = 10
	expect(not ForgeRules.RequirementsMet(profile, adamantine), "extractions without the level")
	profile.progression.level = 40
	expect(ForgeRules.RequirementsMet(profile, adamantine), "level 40 opens Adamantine")
	local granted = ForgeRules.RefreshUnlocks(profile, 1)
	expect(table.find(granted, adamantine.id) ~= nil, "recorded once")
	expectEq(#ForgeRules.RefreshUnlocks(profile, 2), 0, "and never again")
end)

test("a funded Adamantine conversion converts the vaulted sword in place", function()
	local profile = ProfileSchema.Default(0)
	profile.metrics.extractions = 10
	profile.progression.level = 40
	profile.recipes.discovered.AncientEmber = true
	ForgeRules.RefreshUnlocks(profile, 1)
	local recipe = ForgeRecipes.Get("PermanentAdamantineSword")
	for input, amount in recipe.inputs do
		profile.vault.materials[input] = amount + 1
	end
	profile.vault.items = { gear("sword", "AdamantineSword", "Vault") }
	local receipt, reason = ForgeRules.Craft(profile, {
		recipeId = recipe.id,
		sourceId = "sword",
		ownerId = OWNER,
		operationId = "forge:1",
		now = 5,
		newId = function()
			return "never"
		end,
	})
	expect(receipt ~= nil, "converted: " .. tostring(reason))
	local sword = profile.vault.items[1]
	expect(sword.permanent and sword.qualityRoll == 0.02, "same instance, same roll")
	expect(profile.permanentItems.sword ~= nil, "ledger entry")
	for input in recipe.inputs do
		expectEq(profile.vault.materials[input], 1, "charged " .. input .. " once")
	end
end)

test("the browser order groups conversions by tier, weakest first", function()
	local ordered = ForgeRules.Ordered()
	expectEq(#ordered, #ForgeRecipes.List, "every recipe listed")
	local rank = {}
	for index, tierId in ForgeRules.TIER_ORDER do
		rank[tierId] = index
	end
	local last = 0
	for _, recipe in ordered do
		local tierId = ForgeRules.PermanentTier(recipe)
		if tierId then
			expect(rank[tierId] ~= nil, recipe.id .. " has a browsing tier")
			expect(rank[tierId] >= last, recipe.id .. " is in tier order")
			last = rank[tierId]
		end
	end
	expectEq(ForgeRules.PermanentTier(ForgeRecipes.Get("PermanentGuardianFang")), "Legendary", "the Fang")
	expectEq(ForgeRules.PermanentTier(ForgeRecipes.Get("ForgeIronSword")), nil, "special recipes")
end)

-- Shop and merchant ---------------------------------------------------------------

test("the shop sells starter supplies only, each above what a merchant pays for it", function()
	for _, entry in ShopCatalog.Stock do
		if entry.catalogId then
			local each = ShopCatalog.SellValue(entry.catalogId) or 0
			expect(entry.price > each * entry.quantity, entry.id .. " cannot be bought to sell")
		end
		local def = entry.catalogId and ItemCatalog.Get(entry.catalogId)
		if def then
			expect(def.tier == nil or def.tier == "Wood" or def.tier == "Stone", entry.id .. " is Wood or Stone")
			expect(def.family ~= "Material", entry.id .. " is not a material")
		end
	end
end)

test("merchants buy every material and berry at its value and gear at 40%", function()
	for catalogId, value in ShopCatalog.MATERIAL_VALUES do
		expect(ItemCatalog.Get(catalogId) ~= nil, catalogId .. " is an item")
		expect(value > 0, catalogId .. " has a price")
	end
	for catalogId in ItemCatalog.Items do
		if ItemCatalog.IsMaterial(catalogId) then
			expect(ShopCatalog.MATERIAL_VALUES[catalogId] ~= nil, catalogId .. " sells")
			local profile = ProfileSchema.Default(0)
			profile.vault.materials[catalogId] = 3
			local ok, coins = EconomyRules.Sell(profile, "vault", catalogId, 3, "sale:" .. catalogId, 1)
			expect(ok and coins == ShopCatalog.MATERIAL_VALUES[catalogId] * 3, catalogId .. " sold from the vault")
		end
	end
	local recipe = Recipes.Get("IronSword")
	local total = 0
	for input, quantity in recipe.inputs do
		total += ShopCatalog.MATERIAL_VALUES[input] * quantity
	end
	expectEq(ShopCatalog.SellValue("IronSword"), math.floor(total * ShopCatalog.CRAFTED_FRACTION), "40% of inputs")
end)

test("no Forge special craft sells for more than its inputs", function()
	for _, recipe in ForgeRecipes.List do
		if recipe.kind == ForgeRecipes.Kinds.Special then
			local cost = 0
			for input, quantity in recipe.inputs do
				cost += (ShopCatalog.MATERIAL_VALUES[input] or 0) * quantity
			end
			local value = (ShopCatalog.SellValue(recipe.output) or 0) * recipe.quantity
			expect(value <= cost, recipe.id .. " makes no Coins")
		end
	end
end)

-- Trading -------------------------------------------------------------------------

local TRADEABLE = {
	DireHide = true,
	ChargedCore = true,
	GlowFur = true,
	GuardianHeart = true,
	AshenOil = true,
	SiegeResin = true,
	AbyssalShard = true,
	Emberglass = true,
	Bloodroot = true,
	Moonpetal = true,
	AncientEmber = true,
}

test("exactly the rare materials and berries trade; ores, bars, common food and draughts never do", function()
	for catalogId in ItemCatalog.Items do
		if ItemCatalog.IsMaterial(catalogId) then
			expectEq(TradeRules.IsTradeableMaterial(catalogId), TRADEABLE[catalogId] == true, catalogId)
		end
	end
	local profile = ProfileSchema.Default(0)
	profile.vault.materials = { IronBar = 10, CopperOre = 10, Wood = 10, Bloodroot = 2 }
	for _, catalogId in { "IronBar", "CopperOre", "Wood" } do
		local ok, reason = TradeRules.ValidateOffer(profile, { items = {}, materials = { [catalogId] = 1 } }, DAY)
		expect(not ok and reason == "NotTradeable", catalogId .. " refused")
	end
	expect(TradeRules.ValidateOffer(profile, { items = {}, materials = { Bloodroot = 2 } }, DAY), "Bloodroot")
	for _, catalogId in { "Sunberry", "Glimmerberry" } do
		expect(TradeRules.IsTradeableSlot({ catalogId = catalogId, quantity = 3 }), catalogId .. " trades")
	end
	for _, catalogId in { "Redberry", "Sweetberry", "CookedMeat", "SunberryDraught", "BasicMedicine" } do
		expect(not TradeRules.IsTradeableSlot({ catalogId = catalogId, quantity = 3 }), catalogId .. " does not")
	end
end)

test("a session trades Sunberries and Moonpetal, merging into the partner's stack", function()
	local giver, taker = lobby.trader(), lobby.trader()
	giver.lobbyBackpack.slots = { { catalogId = "Sunberry", quantity = 6 }, { catalogId = "Redberry", quantity = 5 } }
	giver.vault.materials = { Moonpetal = 4, SilverBar = 50 }
	taker.lobbyBackpack.slots = { { catalogId = "Sunberry", quantity = 2 } }
	local a, b, id = lobby.session(giver, taker)
	local refused, reason = handlers.TradeOffer(a, id, { "stack:Redberry" }, 0)
	expect(not refused and reason == "NotTradeable", "common berries are refused")
	refused, reason = handlers.TradeOffer(a, id, {}, 0, { SilverBar = 5 })
	expect(not refused and reason == "NotTradeable", "bars are refused")
	local ok
	ok, reason = handlers.TradeOffer(a, id, { "stack:Sunberry" }, 0, { Moonpetal = 3 })
	expect(ok, "Sunberries and Moonpetal offered: " .. tostring(reason))
	expectEq(#pushed[b].theirs.items, 2, "the partner sees both")
	local offered = {}
	for _, item in pushed[b].theirs.items do
		offered[item.key] = item.catalogId
	end
	expectEq(offered["stack:Sunberry"], "Sunberry", "a backpack stack carries its catalog id")
	expectEq(offered["mat:Moonpetal"], "Moonpetal", "a vault material carries its catalog id")
	expectEq(pushed[a].mine.items[1].catalogId ~= nil, true, "my own side too")
	lobby.lockAndConfirm(a, b, id)
	expectEq(pushed[a].reason, "Completed", "completed")
	expectEq(#profiles[b].lobbyBackpack.slots, 1, "one Sunberry slot")
	expectEq(profiles[b].lobbyBackpack.slots[1].quantity, 8, "merged into the partner's stack")
	expectEq(profiles[b].vault.materials.Moonpetal, 3, "Moonpetal lands in the vault")
	expectEq(profiles[a].vault.materials.Moonpetal, 1, "and leaves the giver's")
	expectEq(idsOf(profiles[a].lobbyBackpack.slots), "Redberry", "the giver keeps the Redberries")
	lobby.scheduler:ExpectNoThreadErrors()
end)

test("a rolled-back berry trade takes back exactly what was received", function()
	local profile = lobby.trader()
	profile.lobbyBackpack.slots = { { catalogId = "Glimmerberry", quantity = 9 } }
	profile.trades.pending.old = {
		counterpart = 2,
		gave = { items = {}, gems = 0 },
		received = { items = { { catalogId = "Glimmerberry", quantity = 4 } }, gems = 0 },
		at = DAY,
	}
	expectEq(TradeRules.Reconcile(profile, "old", ProfileSchema.Default(0), DAY + 1), "RolledBack", "rolled back")
	expectEq(profile.lobbyBackpack.slots[1].quantity, 5, "four taken back")
end)
