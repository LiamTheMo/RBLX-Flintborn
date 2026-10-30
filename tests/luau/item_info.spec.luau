-- Inventory screen item info: category tabs, search, descriptions, stat rows,
-- item art (every catalog item) and stat chips.

local Shared = game:GetService("ReplicatedStorage").Shared
local ItemInfo = require(Shared.Items.ItemInfo)
local ItemCatalog = require(Shared.Items.ItemCatalog)

test("items sort into the category tabs", function()
	expectEq(ItemInfo.Category("Wood"), "Materials", "wood is a material")
	expectEq(ItemInfo.Category("StoneAxe"), "Tools", "axes are tools")
	expectEq(ItemInfo.Category("StoneSpear"), "Tools", "weapons share the tools tab")
	expectEq(ItemInfo.Category("Redberry"), "Food", "berries that are food stay food")
	expectEq(ItemInfo.Category("Fiber"), "Plants", "fiber is picked from plants")
	expectEq(ItemInfo.Category("CaveMushroom"), "Plants", "mushroom patches are farmed")
	expectEq(ItemInfo.Category("Resin"), "Materials", "resin comes from trees, not plants")
	expectEq(ItemInfo.Category("HideChest"), "Misc", "armour is misc")
	expectEq(ItemInfo.Category("FlintArrow"), "Misc", "ammunition is misc")
	expectEq(ItemInfo.Category("Workbench"), "Misc", "placeables are misc")
	expectEq(ItemInfo.Category("Nope"), nil, "unknown items have no tab")
	expectEq(ItemInfo.InCategory("Wood", "All"), true, "All shows everything")
	expectEq(ItemInfo.InCategory("Wood", "Food"), false, "wood is not food")
	for id in ItemCatalog.Items do
		local category = ItemInfo.Category(id)
		expect(category ~= nil and table.find(ItemInfo.CATEGORIES, category) ~= nil, id .. " has a listed tab")
	end
end)

test("search matches names, ignoring case", function()
	expectEq(ItemInfo.Matches("Iron Axe", "axe"), true, "part of a word")
	expectEq(ItemInfo.Matches("Iron Axe", ""), true, "empty search matches")
	expectEq(ItemInfo.Matches("Iron Axe", "bow"), false, "no match")
	expectEq(ItemInfo.Matches("Iron Axe", "("), false, "plain text, not a pattern")
end)

test("descriptions are authored or derived", function()
	expect(ItemInfo.Description("StoneAxe") ~= nil, "axes have a description")
	expect(ItemInfo.Description("Wood") ~= nil, "wood has its own description")
	expectEq(ItemInfo.Description("Clay"), nil, "clay has none")
	expectEq(
		ItemInfo.Summary({ catalogId = "Clay" }),
		"Common material · At risk — drops on death",
		"the summary names rarity, family and risk"
	)
	expectEq(
		ItemInfo.Summary({ catalogId = "StoneAxe", permanent = true }),
		"Common tool · Permanent — kept on death",
		"Permanent items are kept"
	)
	expectEq(ItemInfo.Text({ catalogId = "Clay" }), ItemInfo.Summary({ catalogId = "Clay" }), "falls back")
	expectEq(ItemInfo.Summary({ catalogId = "Nope" }), "", "unknown items say nothing")
	for id in ItemCatalog.Items do
		expect(#ItemInfo.Text({ catalogId = id }) > 0, id .. " has a line to show")
	end
end)

local function row(rows, label)
	for _, r in rows do
		if r.label == label then
			return r
		end
	end
	return nil
end

test("stat rows are labelled and real", function()
	local spear = ItemInfo.StatRows({ catalogId = "StoneSpear" })
	expectEq(row(spear, "Damage").value, "25", "stone spear deals 25")
	expectEq(row(spear, "Attack Speed").value, "0.9s", "the spear's real cooldown")
	local rolled = ItemInfo.StatRows({ catalogId = "StoneSpear", qualityRoll = 0.04 })
	expectEq(row(rolled, "Damage").value, "26", "the quality roll raises damage")
	expectEq(row(rolled, "Quality").value, "+4.0%", "and shows as its own row")
	local axe = ItemInfo.StatRows({ catalogId = "StoneAxe" })
	expectEq(row(axe, "Harvest Power").value, "3 per hit", "a stone axe drops 3 wood per hit")
	expectEq(row(axe, "Tool Tier").value, "2", "stone tools are tier 2")
	local bow = ItemInfo.StatRows({ catalogId = "WoodenBow" })
	expectEq(row(bow, "Damage").value, "6 + arrow", "bows add the arrow's damage")
	local chest = ItemInfo.StatRows({ catalogId = "IronChest" })
	expect(string.sub(row(chest, "Armour").value, 1, 1) == "+", "armour shows its increment")
	expectEq(row(chest, "Worn On").value, "Chest", "and where it is worn")
	local berry = ItemInfo.StatRows({ catalogId = "Redberry", quantity = 14 })
	expectEq(row(berry, "Heals").value, "10", "redberries heal")
	expectEq(row(berry, "Food").value, "+10%", "and feed")
	expectEq(row(berry, "Quantity").value, "14 / 50", "a stack shows its size and cap")
	local sun = ItemInfo.StatRows({ catalogId = "Sunberry" })
	expectEq(row(sun, "XP Boost").value, "+10% · 3 min", "boosts name amount and time")
	expectEq(#ItemInfo.StatRows({ catalogId = "Nope" }), 0, "unknown items have none")
	for id in ItemCatalog.Items do
		for _, r in ItemInfo.StatRows({ catalogId = id, quantity = 2, qualityRoll = 0.01 }) do
			expect(r.label ~= "Durability", id .. " shows no durability")
			expect(r.icon ~= "" and r.label ~= "" and r.value ~= "", id .. " rows are complete")
		end
	end
end)

test("every item resolves to kit art", function()
	local name, tint = ItemInfo.Icon("StoneAxe")
	expectEq(name, "stone_axe", "the stone axe has its own icon")
	expectEq(tint, nil, "drawn as it is")
	expectEq(ItemInfo.Icon("IronPickaxe"), "pickaxe", "the iron pickaxe is the pickaxe art")
	local ore, oreTint = ItemInfo.Icon("IronOre")
	expectEq(ore, "rocks", "iron ore is rocks")
	expect(oreTint ~= nil, "tinted iron-grey")
	expectEq(ItemInfo.Icon("Wood"), "logs", "wood shows logs")
	expectEq(ItemInfo.Icon("Nope"), nil, "unknown items have none")
	expectEq(ItemInfo.ArtStatus("Wood"), "exact", "wood is exact")
	expectEq(ItemInfo.ArtStatus("Clay"), "stand-in", "clay is a stand-in")
	expectEq(ItemInfo.ArtStatus("WoodenBow"), "none", "bows have no art yet")
	local sprites = {}
	for _, sprite in ItemInfo.ART_SPRITES do
		sprites[sprite] = true
	end
	local none = {}
	for id, def in ItemCatalog.Items do
		local icon = ItemInfo.Icon(id)
		if icon == nil then
			table.insert(none, id)
			expect(def.weapon ~= nil and def.weapon.family == "Bow", id .. " is a bow, the only gear without art")
		else
			expect(sprites[ItemInfo.Sprite(icon)] == true, id .. " uses listed kit art (" .. icon .. ")")
		end
		if ItemInfo.EXACT[id] then
			expectEq(ItemInfo.TINTS[id], nil, id .. " is exact, so untinted")
		end
	end
	expect(#none <= 7, "only the bows lack art")
end)

test("stat chips describe the item", function()
	local spear = ItemInfo.Stats({ catalogId = "StoneSpear" })
	expectEq(spear[1].text, "25 dmg", "stone spear deals 25")
	expectEq(spear[1].glyph, "sword", "with the sword glyph")
	local axe = ItemInfo.Stats({ catalogId = "StoneAxe" })
	expectEq(string.sub(axe[1].text, 1, 4), "Tier", "tools show their tier")
	local wood = ItemInfo.Stats({ catalogId = "Wood", quantity = 64 })
	expectEq(wood[1].text, "×64", "a stack shows its size")
	for id in ItemCatalog.Items do
		local chips = ItemInfo.Stats({ catalogId = id, quantity = 1 })
		expect(#chips <= 3, id .. " has at most three chips")
	end
	expectEq(#ItemInfo.Stats({ catalogId = "Nope" }), 0, "unknown items have none")
end)
