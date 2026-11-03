-- The Inventory window's sections and filters (src/shared/UI/InventoryModel,
-- docs/ui/InventoryScreen.md): the Backpack tab's All category shows every item
-- the player has, of every kind, in the lobby (backpack and vault) and in a run
-- (backpack, hotbar and worn armour); every other category shows exactly its
-- items; empty slots never push items out of sight.

local Shared = game:GetService("ReplicatedStorage").Shared
local GameConstants = require(Shared.GameConstants)
local InventoryModel = require(Shared.UI.InventoryModel)
local ItemInfo = require(Shared.Items.ItemInfo)

-- The cell ids a set of sections shows under `category` (and `query`).
local function shown(sections, category: string, query: string?): { [string]: boolean }
	local ids = {}
	for _, section in sections do
		for _, cell in section.cells do
			if InventoryModel.Visible(cell, category, query) then
				ids[cell.id] = true
			end
		end
	end
	return ids
end

local function items(sections): { [string]: string }
	local found = {}
	for _, section in sections do
		for _, cell in section.cells do
			if cell.item then
				found[cell.id] = cell.item.catalogId
			end
		end
	end
	return found
end

-- One of every kind: gear, tools, weapons, materials, plants, consumables,
-- ammunition, siege items and placeables.
local LOBBY = {
	backpack = {
		{ catalogId = "StoneAxe" },
		{ catalogId = "Redberry", quantity = 6 },
		{ catalogId = "BasicMedicine", quantity = 2 },
		{ catalogId = "FlintArrow", quantity = 20 },
	},
	items = {
		{ catalogId = "IronSword", qualityRoll = 0.02 },
		{ catalogId = "HideChest" },
		{ catalogId = "StonePickaxe", permanent = true },
	},
	materials = {
		{ catalogId = "Wood", quantity = 412 },
		{ catalogId = "Fiber", quantity = 37 },
		{ catalogId = "IronBar", quantity = 12 },
	},
	itemCapacity = 25,
	backpackCapacity = 50,
}

test("the Vault tab shows the vault alone, materials included", function()
	local sections = InventoryModel.LobbySections(LOBBY, "Vault")
	local found = items(sections)
	expect(found.b1 == nil, "no backpack items")
	expect(found.i1 and found.mWood and found.mIronBar, "items and materials")
	expectEq(sections[1].title, "Items 3/25", "the capacity in the heading")
end)

test("empty slots only fill out the last row", function()
	expectEq(InventoryModel.ShownCount(0, 50), 6, "an empty place shows one row")
	expectEq(InventoryModel.ShownCount(4, 50), 6, "four items and two empties")
	expectEq(InventoryModel.ShownCount(6, 50), 12, "a full row adds an empty row")
	expectEq(InventoryModel.ShownCount(48, 50), 50, "never past the capacity")
	expectEq(InventoryModel.ShownCount(25, 25), 25, "a full vault shows no empties")
	expectEq(InventoryModel.ShownCount(52, 50), 52, "every item shows, even past the capacity")
	local vault = InventoryModel.LobbySections(LOBBY, "Vault")
	expectEq(#vault[1].cells, 6, "three vault items, three empties: the materials follow at once")
end)

test("the lobby Backpack tab's All shows everything; a category shows exactly its items", function()
	local sections = InventoryModel.LobbySections(LOBBY, "Backpack")
	local found = items(sections)
	expectEq(sections[1].id, "backpack", "the backpack comes first")
	local all, count = shown(sections, "All"), 0
	for id in found do
		count += 1
		expect(all[id], id .. " shows under All")
	end
	expectEq(count, #LOBBY.backpack + #LOBBY.items + #LOBBY.materials, "backpack, vault items and materials")
	expect(found.b1 == "StoneAxe" and found.i1 == "IronSword" and found.mWood == "Wood", "backpack, vault, materials")
	local union = {}
	for _, category in ItemInfo.CATEGORIES do
		if category == "All" then
			continue
		end
		for id in shown(sections, category) do
			expectEq(ItemInfo.Category(found[id]), category, id .. " belongs under " .. category)
			expect(union[id] == nil, id .. " is under one category only")
			union[id] = category
		end
	end
	for id in found do
		expect(union[id] ~= nil, id .. " has a category tab")
	end
	local consumables = shown(sections, "Consumables")
	expect(consumables.b2 and consumables.b3, "berries and medicine are Consumables")
	expect(not consumables.b1, "an axe is not")
end)

test("filtering hides empty slots; All with no search keeps them", function()
	local sections = InventoryModel.LobbySections(LOBBY, "Backpack")
	expect(shown(sections, "All").be5, "an empty backpack slot shows under All")
	expect(not shown(sections, "Tools").be5, "not under Tools")
	expect(not shown(sections, "All", "axe").be5, "nor while searching")
	local search = shown(sections, "All", "IRON")
	expect(search.i1 and search.mIronBar and not search.b1, "search matches names, any case")
end)

test("the run Backpack tab's All shows the backpack, hotbar and worn armour", function()
	local slots = {
		{ area = "hotbar", index = 1, catalogId = "StoneAxe" },
		{ area = "hotbar", index = 2, catalogId = "Redberry", quantity = 6 },
		{ area = "armor", index = 2, catalogId = "HideChest" },
		{ area = "backpack", index = 1, catalogId = "Wood", quantity = 40 },
		{ area = "backpack", index = 9, catalogId = "SunberryDraught", quantity = 1 },
		{ area = "backpack", index = 30, catalogId = "FireBomb", quantity = 2 },
	}
	local sections = InventoryModel.RunSections(slots, "Backpack", function(i)
		return tostring(i)
	end)
	local found = items(sections)
	local all = shown(sections, "All")
	local count = 0
	for id in found do
		count += 1
		expect(all[id], id .. " shows under All")
	end
	expectEq(count, #slots, "every carried item")
	expectEq(found["hotbar:1"], "StoneAxe", "the tool on the hotbar")
	expectEq(found["armor:2"], "HideChest", "worn armour")
	expectEq(found["backpack:30"], "FireBomb", "a backpack item far down")
	-- The backpack's items come first, then the first empty slots to the row's end.
	local backpack = sections[1]
	expectEq(backpack.title, "Backpack 3/" .. GameConstants.BACKPACK_SLOTS, "the count in the heading")
	expectEq(#backpack.cells, 6, "three items and three empty slots")
	expectEq(backpack.cells[3].id, "backpack:30", "items in slot order")
	expectEq(backpack.cells[4].id, "backpack:2", "then the first empty slot")
	expectEq(sections[2].cells[1].hotkey, "1", "hotbar slots carry their keys")
	expectEq(sections[3].cells[1].caption, "Head", "armour slots their names")
	local equipped = InventoryModel.RunSections(slots, "Equipped")
	expectEq(#equipped, 2, "Equipped: the hotbar and armour only")
	expectEq(#equipped[1].cells, GameConstants.HOTBAR_SLOTS, "every hotbar slot")
end)
