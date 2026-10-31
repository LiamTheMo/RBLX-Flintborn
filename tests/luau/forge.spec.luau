local Server = game:GetService("ServerScriptService").Server
local Shared = game:GetService("ReplicatedStorage").Shared
local OperationJournal = require(Server.Infrastructure.OperationJournal)
local DeathRules = require(Shared.Admission.DeathRules)
local ExtractionRules = require(Shared.Extraction.ExtractionRules)
local ForgeRecipes = require(Shared.Crafting.ForgeRecipes)
local ForgeRules = require(Shared.Crafting.ForgeRules)
local InventoryRules = require(Shared.Inventory.InventoryRules)
local ItemCatalog = require(Shared.Items.ItemCatalog)
local PermanentRules = require(Shared.Items.PermanentRules)
local ProfileSchema = require(Shared.Data.ProfileSchema)
local Recipes = require(Shared.Crafting.Recipes)

local OWNER = 7

local function pickaxe(id, overrides)
	local item =
		{ instanceId = id, catalogId = "StonePickaxe", ownerId = OWNER, location = "Vault", qualityRoll = 0.03 }
	for key, value in overrides or {} do
		item[key] = value
	end
	return item
end

-- A profile that has earned the Permanent pickaxe: two extractions and an event reagent.
local function readyProfile()
	local profile = ProfileSchema.Default(0)
	profile.metrics.extractions = 2
	profile.recipes.discovered.AncientEmber = true
	profile.vault.materials = { Stone = 200, Wood = 80, Fiber = 40, IronBar = 25, AncientEmber = 1 }
	profile.vault.items = { pickaxe("p1") }
	ForgeRules.RefreshUnlocks(profile, 1)
	return profile
end

local counter = 0
local function request(recipeId, sourceId, operationId)
	return {
		recipeId = recipeId,
		sourceId = sourceId,
		ownerId = OWNER,
		operationId = operationId or "forge:1",
		now = 10,
		newId = function()
			counter += 1
			return "new" .. counter
		end,
	}
end

test("the pickaxe conversion unlocks after two extractions plus a rare event reagent", function()
	local profile = ProfileSchema.Default(0)
	ForgeRules.RefreshUnlocks(profile, 1)
	expect(not ForgeRules.IsUnlocked(profile, "PermanentStonePickaxe"), "locked at first")
	ExtractionRules.Settle(profile, { { catalogId = "AncientEmber", quantity = 1 } }, "Fixed", "r1", 1)
	ExtractionRules.Settle(profile, { { catalogId = "Stone", quantity = 5 } }, "Fixed", "r2", 2)
	local granted = ForgeRules.RefreshUnlocks(profile, 3)
	expect(table.find(granted, "PermanentStonePickaxe") ~= nil, "unlocked by discovery")
	expectEq(profile.recipes.unlocked.PermanentStonePickaxe.unlockSource, "Discovery", "recorded once")
	expect(table.find(granted, "PermanentStoneSpear") ~= nil, "every first-tier conversion unlocks together")
	expect(not ForgeRules.IsUnlocked(profile, "PermanentIronSword"), "higher tiers need more extractions")
	expectEq(#ForgeRules.RefreshUnlocks(profile, 4), 0, "never granted twice")
end)

test("conversion charges each input once, consumes the source and keeps its quality roll", function()
	local profile = readyProfile()
	local receipt = ForgeRules.Craft(profile, request("PermanentStonePickaxe", "p1"))
	expect(receipt ~= nil, "converted")
	-- 10× the Stone Pickaxe recipe (Stone 4, Wood 3, Fiber 2) plus one Ancient Ember.
	expectEq(profile.vault.materials.Stone, 160, "40 stone spent")
	expectEq(profile.vault.materials.Wood, 50, "30 wood spent")
	expectEq(profile.vault.materials.Fiber, 20, "20 fiber spent")
	expectEq(profile.vault.materials.IronBar, 25, "unrelated materials untouched")
	expectEq(profile.vault.materials.AncientEmber, nil, "reagent spent")
	expectEq(#profile.vault.items, 1, "one item, not an ordinary copy plus a Permanent one")
	local item = profile.vault.items[1]
	expect(item.permanent, "now Permanent")
	expectEq(item.instanceId, "p1", "same instance")
	expectEq(item.qualityRoll, 0.03, "quality roll preserved, never re-rolled")
	expectEq(profile.permanentItems.p1.ownershipVersion, 1, "ledger entry")
	expectEq(profile.receipts.forge["forge:1"], receipt, "receipt stored")
end)

test("ineligible, foreign, deployed, unvaulted or already Permanent sources are rejected", function()
	local cases = {
		{ pickaxe("p1", { ownerId = 99 }), "NotYours" },
		{ pickaxe("p1", { location = "LobbyBackpack" }), "NotVaulted" },
		{ pickaxe("p1", { permanent = true }), "AlreadyPermanent" },
	}
	for _, case in cases do
		local profile = readyProfile()
		profile.vault.items = { case[1] }
		local receipt, reason = ForgeRules.Craft(profile, request("PermanentStonePickaxe", "p1"))
		expect(receipt == nil and reason == case[2], case[2])
		expectEq(profile.vault.materials.Stone, 200, case[2] .. ": nothing charged")
	end
	local profile = readyProfile()
	profile.vault.items = { { instanceId = "s1", catalogId = "StoneSword", ownerId = OWNER, location = "Vault" } }
	local _, reason = ForgeRules.Craft(profile, request("PermanentStonePickaxe", "s1"))
	expectEq(reason, "WrongSource", "a sword cannot be converted by the pickaxe recipe")
	expectEq(profile.vault.materials.Stone, 200, "WrongSource: nothing charged")
	profile = readyProfile()
	profile.vault.items = { { instanceId = "r1", catalogId = "ExtractionRune", ownerId = OWNER, location = "Vault" } }
	_, reason = ForgeRules.Craft(profile, request("PermanentStonePickaxe", "r1"))
	expectEq(reason, "NotEligible", "a rune is not a Permanent archetype")
	expectEq(profile.vault.materials.Stone, 200, "NotEligible: nothing charged")
	profile = readyProfile()
	profile.transit = { reservationId = "t1", items = {} }
	_, reason = ForgeRules.Craft(profile, request("PermanentStonePickaxe", "p1"))
	expectEq(reason, "InTransit", "nothing converts while a Deploy is pending")
	profile = readyProfile()
	_, reason = ForgeRules.Craft(profile, request("PermanentStonePickaxe", "missing"))
	expectEq(reason, "NoSource", "client-invented IDs are rejected")
	profile = readyProfile()
	_, reason = ForgeRules.Craft(profile, request("PermanentBasicPickaxe", "p1"))
	expectEq(reason, "UnknownRecipe", "the old Basic Pickaxe recipe is gone")
end)

test("two conversions of one item commit once; a retried nonce returns the same receipt", function()
	local profile = readyProfile()
	profile.vault.materials.Stone = 1000
	profile.vault.materials.AncientEmber = 5
	profile.vault.materials.IronBar = 100
	profile.vault.materials.Wood = 500
	profile.vault.materials.Fiber = 200
	local function convert(operationId)
		return function(working)
			local receipt, reason = ForgeRules.Craft(working, request("PermanentStonePickaxe", "p1", operationId))
			if receipt == nil then
				error(reason, 0)
			end
			return receipt
		end
	end
	local first = OperationJournal.Run(profile, "forge:a", "Forge", 1, convert("forge:a"))
	local ok, reason = pcall(OperationJournal.Run, profile, "forge:b", "Forge", 2, convert("forge:b"))
	expect(not ok and reason == "AlreadyPermanent", "the second request fails")
	local again, applied = OperationJournal.Run(profile, "forge:a", "Forge", 3, convert("forge:a"))
	expect(not applied and again.recipeId == first.recipeId, "retry is a no-op with the same receipt")
	expectEq(profile.vault.materials.Stone, 960, "charged exactly once")
	expectEq(profile.vault.materials.AncientEmber, 4, "one reagent spent")
end)

test("locked or underfunded recipes change nothing; special outputs have default quality", function()
	local profile = ProfileSchema.Default(0)
	profile.vault.materials = { IronBar = 19, Wood = 10 }
	ForgeRules.RefreshUnlocks(profile, 1)
	local _, reason = ForgeRules.Craft(profile, request("ForgeIronPickaxe"))
	expectEq(reason, "MissingMaterials", "one iron bar short")
	profile.vault.materials.IronOre = 50
	_, reason = ForgeRules.Craft(profile, request("ForgeIronPickaxe"))
	expectEq(reason, "MissingMaterials", "ore is not a bar")
	_, reason = ForgeRules.Craft(profile, request("ForgeIronSword"))
	expectEq(reason, "Locked", "needs an extraction with iron first")
	profile.vault.materials.IronBar = 20
	local receipt = ForgeRules.Craft(profile, request("ForgeIronPickaxe"))
	expect(receipt ~= nil, "crafted")
	expectEq(profile.vault.materials.IronBar, nil, "iron bars used up")
	expectEq(profile.vault.materials.IronOre, 50, "ore untouched")
	local made = profile.lobbyBackpack.slots[1]
	expectEq(made.catalogId, "IronPickaxe", "lands in the lobby backpack")
	expectEq(made.qualityRoll, 0, "lobby crafting has no quality roll")
	expectEq(made.ownerId, OWNER, "owned by the crafter")
end)

test("a full lobby backpack refuses a special craft instead of deleting it", function()
	local profile = ProfileSchema.Default(0)
	profile.vault.materials = { IronBar = 40, Wood = 20 }
	for i = 1, 50 do
		profile.lobbyBackpack.slots[i] = { instanceId = "x" .. i, catalogId = "StoneDagger", ownerId = OWNER }
	end
	ForgeRules.RefreshUnlocks(profile, 1)
	local _, reason = ForgeRules.Craft(profile, request("ForgeIronPickaxe"))
	expectEq(reason, "BackpackFull", "refused")
	expectEq(profile.vault.materials.IronBar, 40, "nothing charged")
end)

test("Permanent items survive death, including several at once", function()
	local items = {
		pickaxe("p1", { permanent = true, location = "Carried" }),
		pickaxe("p2", { permanent = true, location = "Carried" }),
		{ catalogId = "Stone", quantity = 30 },
	}
	local body, kept = DeathRules.Split(items)
	expectEq(#kept, 2, "both Permanent items kept")
	expectEq(#body, 1, "only the stone drops")
end)

test("dropping and picking up transfers ownership once", function()
	local item = PermanentRules.Convert(pickaxe("p1"), "forge:1", 1)
	local inventory = InventoryRules.New()
	InventoryRules.Add(inventory, item)
	local dropped = InventoryRules.TakeAt(inventory, "hotbar", 1)
	expectEq(dropped, item, "taken out of the slot")
	expectEq(InventoryRules.At(inventory, "hotbar", 1), nil, "slot emptied")
	PermanentRules.Transfer(dropped, 42)
	expectEq(dropped.ownerId, 42, "new owner")
	expectEq(dropped.ownershipVersion, 2, "ownership version bumped")
	expect(dropped.permanent and dropped.qualityRoll == 0.03, "still Permanent, same roll")
	expect(not PermanentRules.CanConvert(dropped, OWNER), "the former owner has no claim")
end)

test("every Permanent recipe names an eligible source and needs an event reagent", function()
	for _, recipe in ForgeRecipes.List do
		if recipe.kind == ForgeRecipes.Kinds.Permanent then
			expect(PermanentRules.IsEligible(recipe.source), recipe.id)
			expectEq(recipe.id, "Permanent" .. recipe.source, recipe.id .. " is named after its source")
			expect((recipe.inputs.AncientEmber or 0) >= 1, recipe.id .. " cannot come from farming alone")
		end
	end
end)

test("every piece of gear has a Permanent conversion priced by its tier", function()
	-- Ancient Ember and rare inputs per tier (GDD §51), on top of 10× the recipe.
	local function extras(tier: string, isArmor: boolean)
		if tier == "Iron" or tier == "Obsidian" or tier == "Silver" then
			return { AncientEmber = 2 }
		elseif tier == "Cobalt" or tier == "Jade" then
			return { AncientEmber = 3, Moonpetal = 2 }
		elseif tier == "Mithril" then
			return if isArmor then { AncientEmber = 4, GlowFur = 3 } else { AncientEmber = 4, ChargedCore = 3 }
		elseif tier == "Adamantine" then
			return if isArmor
				then { AncientEmber = 5, GuardianHeart = 1, Emberglass = 3 }
				else { AncientEmber = 5, GuardianHeart = 1, AbyssalShard = 3 }
		end
		return { AncientEmber = 1 }
	end
	local gear = 0
	for _, recipe in Recipes.List do
		local def = ItemCatalog.Get(recipe.output)
		if PermanentRules.IsEligible(recipe.output) then
			gear += 1
			local permanent = ForgeRecipes.Get("Permanent" .. recipe.output)
			expect(permanent ~= nil, recipe.output .. " can become Permanent")
			if permanent then
				expectEq(permanent.source, recipe.output, permanent.id .. " source")
				expectEq(permanent.kind, ForgeRecipes.Kinds.Permanent, permanent.id .. " kind")
				local expected = {}
				for input, amount in recipe.inputs do
					expected[input] = amount * ForgeRecipes.PERMANENT_MULTIPLIER
				end
				for input, amount in extras(def.tier, def.family == ItemCatalog.Families.Armor) do
					expected[input] = (expected[input] or 0) + amount
				end
				for input, amount in expected do
					expectEq(permanent.inputs[input], amount, permanent.id .. " " .. input)
				end
				for input in permanent.inputs do
					expect(expected[input] ~= nil, permanent.id .. " charges no stray " .. input)
				end
			end
		else
			expectEq(ForgeRecipes.Get("Permanent" .. recipe.output), nil, recipe.output .. " never becomes Permanent")
		end
	end
	expect(gear > 0, "gear recipes exist")
	for id, def in ItemCatalog.Items do
		if PermanentRules.IsEligible(id) then
			expect(ForgeRecipes.Get("Permanent" .. id) ~= nil, id .. " has a conversion")
		end
		local isGear = def.family == ItemCatalog.Families.Weapon
			or def.family == ItemCatalog.Families.Tool
			or def.family == ItemCatalog.Families.Armor
		expectEq(PermanentRules.IsEligible(id), isGear, id .. " eligibility follows its family")
	end
	local stone = ForgeRecipes.Get("PermanentStonePickaxe").inputs
	expect(stone.Stone == 40 and stone.Wood == 30 and stone.Fiber == 20, "stone pickaxe at 10× its recipe")
	expect(ForgeRecipes.Get("PermanentStoneSpear") ~= nil, "spears convert")
	expect(ForgeRecipes.Get("PermanentIronSword") ~= nil, "swords convert")
	expect(ForgeRecipes.Get("PermanentHideChest") ~= nil, "armor converts")
	expect(ForgeRecipes.Get("PermanentGuardianFang") ~= nil, "the Guardian's Fang converts")
	expect(
		(ForgeRecipes.Get("PermanentGuardianFang").inputs.GuardianHeart or 0) >= 1,
		"the Fang needs a Guardian Heart"
	)
	for _, removed in { "PermanentBasicPickaxe", "PermanentSickle", "PermanentWoodChest", "PermanentStoneChest" } do
		expectEq(ForgeRecipes.Get(removed), nil, removed .. " is gone")
	end
end)

test("a full lobby backpack never deletes an extracted Permanent item", function()
	local profile = ProfileSchema.Default(0)
	for i = 1, 50 do
		profile.lobbyBackpack.slots[i] = { instanceId = "x" .. i, catalogId = "StoneDagger", ownerId = OWNER }
	end
	local receipt = ExtractionRules.Settle(profile, {
		pickaxe("p1", { permanent = true, location = "Carried" }),
		{ instanceId = "d1", catalogId = "StoneDagger", ownerId = OWNER },
	}, "Fixed", "r1", 1)
	expectEq(#profile.lobbyBackpack.slots, 51, "the Permanent pickaxe still lands")
	expectEq(receipt.deleted.StonePickaxe, nil, "never listed as deleted")
	expectEq(receipt.deleted.StoneDagger, 1, "the ordinary dagger overflows")
end)

-- Batch forging (UI rebuild D4) -----------------------------------------------------

local function batch(recipeId, count, operationId)
	local req = request(recipeId, nil, operationId)
	req.count = count
	return req
end

local function pickaxeProfile(ironBars)
	local profile = ProfileSchema.Default(0)
	profile.vault.materials = { IronBar = ironBars, Wood = 200 }
	ForgeRules.RefreshUnlocks(profile, 1)
	return profile
end

test("a batch must be a whole count from 1 to MAX_BATCH", function()
	expectEq(ForgeRules.MAX_BATCH, 10, "batch cap")
	for _, bad in { 0, -1, 11, 2.5, 0 / 0, math.huge, "3", true, {} } do
		local profile = pickaxeProfile(1000)
		local receipt, reason = ForgeRules.Craft(profile, batch("ForgeIronPickaxe", bad))
		expect(receipt == nil and reason == "BadQuantity", "refused " .. tostring(bad))
		expectEq(profile.vault.materials.IronBar, 1000, tostring(bad) .. ": nothing charged")
		expectEq(#profile.lobbyBackpack.slots, 0, tostring(bad) .. ": nothing granted")
	end
	local profile = pickaxeProfile(1000)
	local receipt = ForgeRules.Craft(profile, batch("ForgeIronPickaxe", nil))
	expect(receipt ~= nil and receipt.count == 1, "no count means one")
	expectEq(profile.vault.materials.IronBar, 980, "one craft charged")
end)

test("a batch charges and grants all N crafts at once", function()
	local profile = pickaxeProfile(205)
	local receipt = ForgeRules.Craft(profile, batch("ForgeIronPickaxe", 10))
	expect(receipt ~= nil, "crafted")
	expectEq(receipt.count, 10, "receipt count")
	expectEq(receipt.inputs.IronBar, 200, "receipt lists the total spent")
	expectEq(profile.vault.materials.IronBar, 5, "200 bars spent")
	expectEq(profile.vault.materials.Wood, 100, "100 wood spent")
	expectEq(#profile.lobbyBackpack.slots, 10, "ten pickaxes")
	local seen = {}
	for _, item in profile.lobbyBackpack.slots do
		expect(item.catalogId == "IronPickaxe" and item.qualityRoll == 0, "default-quality pickaxe")
		expect(not seen[item.instanceId], "unique instance")
		seen[item.instanceId] = true
	end
	expectEq(#receipt.output.instanceIds, 10, "every instance on the receipt")
	expectEq(receipt.output.instanceId, receipt.output.instanceIds[1], "first instance kept for old readers")

	profile = ProfileSchema.Default(0)
	profile.vault.materials = { Wood = 120, Flint = 40, Fiber = 80 }
	ForgeRules.RefreshUnlocks(profile, 1)
	receipt = ForgeRules.Craft(profile, batch("ForgeArrows", 10))
	expect(receipt ~= nil, "arrows crafted")
	expectEq(receipt.output.quantity, 500, "ten crafts of 50 arrows")
	expectEq(#profile.lobbyBackpack.slots, 1, "one stack")
	expectEq(profile.lobbyBackpack.slots[1].quantity, 500, "stacked")
	expectEq(profile.vault.materials.Wood, nil, "wood used up")
end)

test("a batch the vault cannot fully pay for changes nothing", function()
	local profile = pickaxeProfile(199)
	expectEq(ForgeRules.MaxCount(profile, ForgeRecipes.Get("ForgeIronPickaxe")), 9, "materials allow nine")
	local receipt, reason = ForgeRules.Craft(profile, batch("ForgeIronPickaxe", 10))
	expect(receipt == nil and reason == "MissingMaterials", "ten refused")
	expectEq(profile.vault.materials.IronBar, 199, "nothing charged")
	expectEq(profile.vault.materials.Wood, 200, "no wood charged")
	expectEq(#profile.lobbyBackpack.slots, 0, "nothing granted")
	expect(ForgeRules.Craft(profile, batch("ForgeIronPickaxe", 9)) ~= nil, "nine fit")
	expectEq(ForgeRules.MaxCount(profile, ForgeRecipes.Get("ForgeIronPickaxe")), 0, "none left")
	expectEq(ForgeRules.MaxCount(pickaxeProfile(10000), ForgeRecipes.Get("ForgeIronPickaxe")), 10, "capped")
end)

test("a batch that does not all fit the lobby backpack is refused whole", function()
	local profile = pickaxeProfile(1000)
	for i = 1, 45 do
		profile.lobbyBackpack.slots[i] = { instanceId = "x" .. i, catalogId = "StoneDagger", ownerId = OWNER }
	end
	local receipt, reason = ForgeRules.Craft(profile, batch("ForgeIronPickaxe", 6))
	expect(receipt == nil and reason == "BackpackFull", "six do not fit in five slots")
	expectEq(#profile.lobbyBackpack.slots, 45, "none added")
	expectEq(profile.vault.materials.IronBar, 1000, "nothing charged")
	expectEq(ForgeRules.MaxCount(profile, ForgeRecipes.Get("ForgeIronPickaxe")), 5, "MaxCount offers only what fits")
	expect(ForgeRules.Craft(profile, batch("ForgeIronPickaxe", 5)) ~= nil, "five fit")
	expectEq(ForgeRules.MaxCount(profile, ForgeRecipes.Get("ForgeIronPickaxe")), 0, "a full backpack offers none")
	local arrows = ProfileSchema.Default(0)
	arrows.vault.materials = { Wood = 1000, Flint = 1000, Fiber = 1000 }
	arrows.lobbyBackpack.slots = { { catalogId = "FlintArrow", quantity = 380 } }
	ForgeRules.RefreshUnlocks(arrows, 1)
	expectEq(ForgeRules.MaxCount(arrows, ForgeRecipes.Get("ForgeArrows")), 2, "a stack's room: 120 more arrows")
	expectEq(#profile.lobbyBackpack.slots, 50, "backpack full")
end)

test("MaxCount works on a snapshot without a lobby backpack or vault", function()
	local recipe = ForgeRecipes.Get("ForgeIronPickaxe")
	local snapshot = { vault = { materials = { IronBar = 65, Wood = 200 } } }
	expectEq(ForgeRules.MaxCount(snapshot, recipe), 3, "materials only: no backpack, no room limit")
	snapshot.lobbyBackpack = {}
	expectEq(ForgeRules.MaxCount(snapshot, recipe), 3, "a backpack without slots is no limit either")
	expectEq(ForgeRules.MaxCount({}, recipe), 0, "no vault: nothing owned")
	expectEq(ForgeRules.MaxCount(snapshot, ForgeRecipes.Get("PermanentStonePickaxe")), 0, "conversions too")
end)

test("a Permanent conversion is always exactly one", function()
	local profile = readyProfile()
	local recipe = ForgeRecipes.Get("PermanentStonePickaxe")
	expectEq(ForgeRules.MaxCount(profile, recipe), 1, "one source per conversion")
	local receipt, reason = ForgeRules.Craft(profile, batch("PermanentStonePickaxe", 2))
	expect(receipt == nil and reason == "BadQuantity", "two refused")
	expectEq(profile.vault.materials.Stone, 200, "nothing charged")
	local req = batch("PermanentStonePickaxe", 1)
	req.sourceId = "p1"
	expect(ForgeRules.Craft(profile, req) ~= nil, "one converts")
end)

test("a retried batch nonce returns the first receipt and charges once", function()
	local profile = pickaxeProfile(1000)
	local function run(count)
		return function(working)
			local receipt, reason = ForgeRules.Craft(working, batch("ForgeIronPickaxe", count, "forge:batch"))
			if receipt == nil then
				error(reason, 0)
			end
			return receipt
		end
	end
	local first, applied = OperationJournal.Run(profile, "forge:batch", "Forge", 1, run(4))
	expect(applied and first.count == 4, "first commit")
	local again, appliedAgain = OperationJournal.Run(profile, "forge:batch", "Forge", 2, run(10))
	expect(not appliedAgain and again.count == 4, "a retry, even with another count, is the first receipt")
	expectEq(profile.vault.materials.IronBar, 920, "charged for four, once")
	expectEq(#profile.lobbyBackpack.slots, 4, "four pickaxes")
end)
