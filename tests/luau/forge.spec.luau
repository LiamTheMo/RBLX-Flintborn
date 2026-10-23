local Server = game:GetService("ServerScriptService").Server
local Shared = game:GetService("ReplicatedStorage").Shared
local OperationJournal = require(Server.Infrastructure.OperationJournal)
local DeathRules = require(Shared.Admission.DeathRules)
local ExtractionRules = require(Shared.Extraction.ExtractionRules)
local ForgeRecipes = require(Shared.Crafting.ForgeRecipes)
local ForgeRules = require(Shared.Crafting.ForgeRules)
local InventoryRules = require(Shared.Inventory.InventoryRules)
local PermanentRules = require(Shared.Items.PermanentRules)
local ProfileSchema = require(Shared.Data.ProfileSchema)

local OWNER = 7

local function pickaxe(id, overrides)
	local item =
		{ instanceId = id, catalogId = "BasicPickaxe", ownerId = OWNER, location = "Vault", qualityRoll = 0.03 }
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
	profile.vault.materials = { Stone = 200, Wood = 80, Iron = 25, AncientEmber = 1 }
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
	expect(not ForgeRules.IsUnlocked(profile, "PermanentBasicPickaxe"), "locked at first")
	ExtractionRules.Settle(profile, { { catalogId = "AncientEmber", quantity = 1 } }, "Fixed", "r1", 1)
	ExtractionRules.Settle(profile, { { catalogId = "Stone", quantity = 5 } }, "Fixed", "r2", 2)
	local granted = ForgeRules.RefreshUnlocks(profile, 3)
	expect(table.find(granted, "PermanentBasicPickaxe") ~= nil, "unlocked by discovery")
	expectEq(profile.recipes.unlocked.PermanentBasicPickaxe.unlockSource, "Discovery", "recorded once")
	expectEq(#ForgeRules.RefreshUnlocks(profile, 4), 0, "never granted twice")
end)

test("conversion charges each input once, consumes the source and keeps its quality roll", function()
	local profile = readyProfile()
	local receipt = ForgeRules.Craft(profile, request("PermanentBasicPickaxe", "p1"))
	expect(receipt ~= nil, "converted")
	expectEq(profile.vault.materials.Stone, 50, "150 stone spent")
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
		local receipt, reason = ForgeRules.Craft(profile, request("PermanentBasicPickaxe", "p1"))
		expect(receipt == nil and reason == case[2], case[2])
		expectEq(profile.vault.materials.Stone, 200, case[2] .. ": nothing charged")
	end
	local profile = readyProfile()
	profile.vault.items = { { instanceId = "s1", catalogId = "StoneSword", ownerId = OWNER, location = "Vault" } }
	local _, reason = ForgeRules.Craft(profile, request("PermanentBasicPickaxe", "s1"))
	expectEq(reason, "NotEligible", "a sword is not a Permanent archetype")
	profile = readyProfile()
	profile.transit = { reservationId = "t1", items = {} }
	_, reason = ForgeRules.Craft(profile, request("PermanentBasicPickaxe", "p1"))
	expectEq(reason, "InTransit", "nothing converts while a Deploy is pending")
	profile = readyProfile()
	_, reason = ForgeRules.Craft(profile, request("PermanentBasicPickaxe", "missing"))
	expectEq(reason, "NoSource", "client-invented IDs are rejected")
end)

test("two conversions of one item commit once; a retried nonce returns the same receipt", function()
	local profile = readyProfile()
	profile.vault.materials.Stone = 1000
	profile.vault.materials.AncientEmber = 5
	profile.vault.materials.Iron = 100
	profile.vault.materials.Wood = 500
	local function convert(operationId)
		return function(working)
			local receipt, reason = ForgeRules.Craft(working, request("PermanentBasicPickaxe", "p1", operationId))
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
	expectEq(profile.vault.materials.Stone, 850, "charged exactly once")
end)

test("locked or underfunded recipes change nothing; special outputs have default quality", function()
	local profile = ProfileSchema.Default(0)
	profile.vault.materials = { Iron = 19, Wood = 10 }
	ForgeRules.RefreshUnlocks(profile, 1)
	local _, reason = ForgeRules.Craft(profile, request("ForgeIronPickaxe"))
	expectEq(reason, "MissingMaterials", "one iron short")
	_, reason = ForgeRules.Craft(profile, request("ForgeIronSword"))
	expectEq(reason, "Locked", "needs an extraction with iron first")
	profile.vault.materials.Iron = 20
	local receipt = ForgeRules.Craft(profile, request("ForgeIronPickaxe"))
	expect(receipt ~= nil, "crafted")
	expectEq(profile.vault.materials.Iron, nil, "iron used up")
	local made = profile.lobbyBackpack.slots[1]
	expectEq(made.catalogId, "IronPickaxe", "lands in the lobby backpack")
	expectEq(made.qualityRoll, 0, "lobby crafting has no quality roll")
	expectEq(made.ownerId, OWNER, "owned by the crafter")
end)

test("a full lobby backpack refuses a special craft instead of deleting it", function()
	local profile = ProfileSchema.Default(0)
	profile.vault.materials = { Iron = 40, Wood = 20 }
	for i = 1, 50 do
		profile.lobbyBackpack.slots[i] = { instanceId = "x" .. i, catalogId = "StoneDagger", ownerId = OWNER }
	end
	ForgeRules.RefreshUnlocks(profile, 1)
	local _, reason = ForgeRules.Craft(profile, request("ForgeIronPickaxe"))
	expectEq(reason, "BackpackFull", "refused")
	expectEq(profile.vault.materials.Iron, 40, "nothing charged")
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
			expect((recipe.inputs.AncientEmber or 0) >= 1, recipe.id .. " cannot come from farming alone")
		end
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
	expectEq(receipt.deleted.BasicPickaxe, nil, "never listed as deleted")
	expectEq(receipt.deleted.StoneDagger, 1, "the ordinary dagger overflows")
end)
