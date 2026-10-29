-- Inventory screen item info: category tabs, search and stat chips.

local Shared = game:GetService("ReplicatedStorage").Shared
local ItemInfo = require(Shared.Items.ItemInfo)
local ItemCatalog = require(Shared.Items.ItemCatalog)

test("items sort into the category tabs", function()
	expectEq(ItemInfo.Category("Wood"), "Materials", "wood is a material")
	expectEq(ItemInfo.Category("StoneAxe"), "Tools", "axes are tools")
	expectEq(ItemInfo.Category("StoneSpear"), "Tools", "weapons share the tools tab")
	expectEq(ItemInfo.Category("Redberry"), "Food", "berries are food")
	expectEq(ItemInfo.Category("Nope"), nil, "unknown items have no tab")
	expectEq(ItemInfo.InCategory("Wood", "All"), true, "All shows everything")
	expectEq(ItemInfo.InCategory("Wood", "Food"), false, "wood is not food")
end)

test("search matches names, ignoring case", function()
	expectEq(ItemInfo.Matches("Iron Axe", "axe"), true, "part of a word")
	expectEq(ItemInfo.Matches("Iron Axe", ""), true, "empty search matches")
	expectEq(ItemInfo.Matches("Iron Axe", "bow"), false, "no match")
	expectEq(ItemInfo.Matches("Iron Axe", "("), false, "plain text, not a pattern")
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
