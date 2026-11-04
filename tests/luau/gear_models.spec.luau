-- Placeholder gear models (v0.19): every held item, worn armor piece and dropped
-- gear item has a buildable recipe, held tool heads sit up the handle, and armor
-- covers the body parts its slot should.
local Shared = game:GetService("ReplicatedStorage").Shared
local Server = game:GetService("ServerScriptService").Server
local GearModels = require(Server.Rules.Visuals.GearModels)
local InventoryRules = require(Server.Rules.Inventory.InventoryRules)
local ItemCatalog = require(Server.Rules.Items.ItemCatalog)
local Recipe = require(Server.Rules.Visuals.Recipe)
local Tiers = require(Shared.Items.Tiers)

local MAX_PARTS = 8

local function itemsOf(...)
	local families = {}
	for _, family in { ... } do
		families[family] = true
	end
	local found = {}
	for id, def in ItemCatalog.Items do
		if families[def.family] then
			table.insert(found, id)
		end
	end
	table.sort(found)
	return found
end

local HEAD_PARTS = { Head = true, Blade = true, Tip = true }

test("every tool, weapon, siege item and arrow has a buildable held recipe", function()
	local ids = itemsOf("Tool", "Weapon", "Siege", "Ammo")
	expect(#ids > 40, "the catalog has gear to cover")
	for _, id in ids do
		local recipe = GearModels.Held(id)
		assert(recipe, "no held recipe for " .. id)
		local problems = Recipe.Problems(recipe, MAX_PARTS)
		expectEq(#problems, 0, id .. ": " .. table.concat(problems, "; "))
	end
	local neon = false
	for _, spec in GearModels.Held("GuardianFang").parts do
		neon = neon or spec.material == "Neon"
	end
	expect(neon, "the Guardian's Fang has a Neon accent")
	-- Every ladder tier that makes gear has a look.
	for _, tier in Tiers.Ladder do
		local look = GearModels.Tiers[tier.id]
		expect(look ~= nil and #look.color == 3, tier.id .. " has an RGB colour")
	end
end)

test("consumables and placeables get a small generic held model, materials none", function()
	for _, id in itemsOf("Consumable", "Placeable") do
		local recipe = GearModels.Held(id)
		assert(recipe, "no held recipe for " .. id)
		expectEq(#Recipe.Problems(recipe, MAX_PARTS), 0, id .. " is buildable")
		local low, high = GearModels.Extent(recipe)
		expect(high[2] - low[2] <= 1.6, id .. " stays small in the hand")
	end
	expectEq(GearModels.Held("Wood"), nil, "materials show nothing in the hand")
	expectEq(GearModels.Held("NoSuchItem"), nil, "unknown ids show nothing")
end)

test("held tools and weapons put the business end at +Y at a believable size for an R6 hand", function()
	for _, id in itemsOf("Tool", "Weapon") do
		if not GearModels.IsBow(id) then
			local recipe = GearModels.Held(id)
			local low, high = GearModels.Extent(recipe)
			expect(high[2] > -low[2], id .. " extends further up the handle than below the grip")
			local headY
			for _, spec in recipe.parts do
				if HEAD_PARTS[spec.name] then
					headY = math.max(headY or -math.huge, spec.pos[2])
				end
			end
			assert(headY, id .. " has a head, blade or tip")
			expect(headY > 0.5, id .. " head sits above the grip")
		end
	end
	for id, range in
		{
			IronSword = { 3.5, 5 },
			StoneDagger = { 1.4, 2.4 },
			WoodenSpear = { 6, 8 },
			IronAxe = { 2.6, 3.6 },
			IronPickaxe = { 2.6, 3.6 },
			WoodenBow = { 3.5, 4.5 },
		}
	do
		local low, high = GearModels.Extent(GearModels.Held(id))
		local length = high[2] - low[2]
		expect(length >= range[1] and length <= range[2], ("%s is %.1f studs"):format(id, length))
	end
end)

test("bows are held upright and are the only items held in the left hand", function()
	for _, id in itemsOf("Weapon") do
		expectEq(GearModels.IsBow(id), ItemCatalog.Get(id).weapon.family == "Bow", id)
	end
	expectEq(GearModels.IsBow("IronAxe"), false)
	expectEq(GearModels.IsBow("Wood"), false)
end)

local SLOT_PARTS = {
	Head = { "Head" },
	Chest = { "Torso", "Right Arm", "Left Arm" },
	Legs = { "Right Leg", "Left Leg" },
}

test("every armor piece covers the body parts of its slot", function()
	local ids = itemsOf("Armor")
	expect(#ids >= 24, "eight armor tiers of three slots")
	for _, id in ids do
		local armor = ItemCatalog.Get(id).armor
		local recipes = GearModels.Armor(id)
		assert(recipes, "no armor recipe for " .. id)
		local expected = SLOT_PARTS[armor.slot]
		local count = 0
		for partName, recipe in recipes do
			count += 1
			expect(table.find(expected, partName) ~= nil, id .. " covers unexpected part " .. partName)
			local problems = Recipe.Problems(recipe, MAX_PARTS)
			expectEq(#problems, 0, id .. " " .. partName .. ": " .. table.concat(problems, "; "))
		end
		expectEq(count, #expected, id .. " covers every part of its slot")
	end
	for _, slot in InventoryRules.ArmorSlots do
		expect(SLOT_PARTS[slot] ~= nil, slot .. " is a known armor slot")
	end
	expectEq(GearModels.Armor("IronSword"), nil, "non-armor has no armor model")
end)

test("armor shells sit just outside the body part they cover", function()
	local function width(recipe)
		local low, high = Recipe.Bounds(recipe)
		return high[1] - low[1], high[3] - low[3]
	end
	local torso = GearModels.Armor("IronChest").Torso
	local torsoX, torsoZ = width(torso)
	expect(torsoX > 2 and torsoX < 2.5, "chest plate is a little wider than the 2 stud torso")
	expect(torsoZ > 1 and torsoZ < 1.5, "chest plate is a little deeper than the 1 stud torso")
	local legX = width(GearModels.Armor("IronLegs")["Right Leg"])
	expect(legX > 1 and legX < 1.5, "greaves hug the 1 stud leg")
	local helmet = GearModels.Armor("IronHead").Head
	local low, high = Recipe.Bounds(helmet)
	expect(high[1] - low[1] < 1.7, "the helmet is modest")
	expect(high[2] > 0.3, "the helmet sits above the head's centre")
end)

test("dropped gear has a small buildable ground model", function()
	for _, id in itemsOf("Tool", "Weapon", "Armor", "Siege") do
		local recipe = GearModels.Drop(id)
		assert(recipe, "no drop model for " .. id)
		local problems = Recipe.Problems(recipe, MAX_PARTS)
		expectEq(#problems, 0, id .. ": " .. table.concat(problems, "; "))
		local low, high = GearModels.Extent(recipe)
		expect(low[2] >= -0.75 and low[2] <= -0.65, id .. " rests on the pickup box floor")
		expect(high[2] - low[2] <= 1.4, id .. " fits the pickup box height")
		expect(high[1] - low[1] <= 3.6 and high[3] - low[3] <= 3.6, id .. " stays small on the ground")
	end
	expectEq(GearModels.Drop("Wood"), nil, "gathered materials keep their plain cube")
end)
