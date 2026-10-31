-- Play window rules: the run hotbar, carrying summary, party rows, who presses
-- Play and the deploy check.

local Shared = game:GetService("ReplicatedStorage").Shared
local PlayModel = require(Shared.UI.PlayModel)
local InventoryRules = require(Shared.Inventory.InventoryRules)
local BiomeCatalog = require(Shared.World.BiomeCatalog)

local ME = { userId = 1, name = "LiamTheMo" }

test("the hotbar matches the run's own packing", function()
	local items = {
		{ catalogId = "StoneAxe", permanent = true },
		{ catalogId = "Wood", quantity = 40 },
		{ catalogId = "StoneSpear" },
		{ catalogId = "Fiber", quantity = 8 },
	}
	local hotbar, more = PlayModel.LoadoutHotbar(items)
	local inventory = InventoryRules.FromItems(items)
	for index = 1, PlayModel.HOTBAR_SLOTS do
		local expected = inventory.hotbar[index]
		expectEq(hotbar[index] and hotbar[index].catalogId, expected and expected.catalogId, "slot " .. index)
	end
	expectEq(hotbar[1].catalogId, "StoneAxe", "tools go to the hotbar first")
	expectEq(hotbar[1].permanent, true, "Permanent flag kept")
	local inBackpack = 0
	for _, entry in inventory.backpack do
		if entry then
			inBackpack += 1
		end
	end
	expectEq(more, inBackpack, "the rest is counted as backpack")
	expectEq(items[2].quantity, 40, "the preview is not changed")
end)

test("a full hotbar spills into the backpack count", function()
	local items = {}
	for _ = 1, 8 do
		table.insert(items, { catalogId = "StoneAxe" })
	end
	local hotbar, more = PlayModel.LoadoutHotbar(items)
	local filled = 0
	for index = 1, PlayModel.HOTBAR_SLOTS do
		if hotbar[index] then
			filled += 1
		end
	end
	expectEq(filled, 6, "six slots")
	expectEq(more, 2, "two more in the backpack")
	expectEq(PlayModel.MoreText(more), "+2 more in your backpack", "the note")
	expectEq(PlayModel.MoreText(0), nil, "no note when nothing is left")
end)

test("no preview means an empty hotbar", function()
	local hotbar, more = PlayModel.LoadoutHotbar(nil)
	expectEq(next(hotbar), nil, "empty")
	expectEq(more, 0, "nothing more")
	hotbar = PlayModel.LoadoutHotbar({})
	expectEq(next(hotbar), nil, "empty list")
end)

test("carrying summary", function()
	expectEq(PlayModel.CarryingText(nil), "Checking…", "before the first read")
	expectEq(PlayModel.CarryingText({}), "Nothing", "empty backpack")
	local items = { { catalogId = "StoneAxe", permanent = true }, { catalogId = "Wood", quantity = 4 } }
	expectEq(PlayModel.CarryingText(items), "2 items, 1 at risk", "mixed")
	expectEq(PlayModel.CarryingText({ items[1] }), "1 item, all Permanent", "all safe")
	local summary = PlayModel.Carrying(items)
	expectEq(summary.stacks, 2, "stacks")
	expectEq(summary.permanent, 1, "permanent")
	expectEq(PlayModel.CarryingRow(items).icon, "chest", "chest icon")
end)

test("world rows show only catalog data", function()
	local rows = PlayModel.WorldRows()
	expectEq(#rows, 3, "three world rows")
	expectEq(rows[1].value, "Shattered Crater", "the world's name")
	expectEq(rows[2].value, ("%d · Low to Extreme"):format(#BiomeCatalog.ZONE_IDS), "zones and danger range")
	expectEq(rows[3].value, "Random location", "random spawn")
	local u, v = PlayModel.MarkerUV(4400)
	expect(u > 0 and u < 1 and v > 0 and v < 1, "the marked zone is on the map")
end)

test("who presses Play", function()
	expectEq(PlayModel.Role({ party = nil }, 1), "solo", "alone")
	local party = { leader = 1, members = { { userId = 2, name = "Ana" }, { userId = 1, name = "Liam" } } }
	expectEq(PlayModel.Role({ party = party }, 1), "leader", "leader")
	expectEq(PlayModel.Role({ party = party }, 2), "member", "member")
	local rows = PlayModel.Members({ party = party }, ME)
	expectEq(rows[1].userId, 1, "leader first")
	expectEq(rows[1].leader, true, "crowned")
	expectEq(rows[2].ready, nil, "no ready flag")
	local solo = PlayModel.Members({ party = nil }, ME)
	expect(#solo == 1 and solo[1].leader, "solo is a party of one, led by you")
	expectEq(PlayModel.ReadyCounts, nil, "no ready count")
	expectEq(PlayModel.ReadyNote, nil, "no ready note")
end)

test("deploy check", function()
	expectEq(PlayModel.DeployCheck({}), nil, "an empty backpack deploys at once")
	local unread = PlayModel.DeployCheck(nil)
	expectEq(unread.title, PlayModel.TITLE_UNREAD, "unread preview")
	expectEq(unread.confirmLabel, "Enter anyway", "enter anyway")
	local check = PlayModel.DeployCheck({
		{ catalogId = "StoneAxe", permanent = true },
		{ catalogId = "Wood", quantity = 20 },
	})
	expectEq(check.title, PlayModel.TITLE_CHECK, "lists the items")
	expectEq(check.lines[1], "★ Stone Axe", "permanent star")
	expectEq(check.lines[2], "• Wood ×20", "quantity")
	expectEq(check.notes[1], PlayModel.LINE_AT_RISK, "risk warning")
	expectEq(#check.notes, 2, "the risk warning and the vault line only")
	local safe = PlayModel.DeployCheck({ { catalogId = "StoneAxe", permanent = true } })
	expectEq(safe.notes[1], PlayModel.LINE_VAULT, "no risk warning when all Permanent")
end)
