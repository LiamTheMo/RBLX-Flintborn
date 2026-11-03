local Shared = game:GetService("ReplicatedStorage").Shared
local LobbyHudModel = require(Shared.UI.LobbyHudModel)

local ME = { userId = 1, name = "LiamTheMo" }

test("menu tiles follow the mockup's 2 × 3 order", function()
	local ids = {}
	for _, tile in LobbyHudModel.TILES do
		table.insert(ids, tile.id)
	end
	expectEq(table.concat(ids, ","), "Inventory,Play,Quests,Shop,Forge,Trade", "order")
end)

test("level and XP lines", function()
	local p = LobbyHudModel.Progress({ level = 12, xp = 450, xpToNext = 750 })
	expectEq(p.level, "LV. 12", "level")
	expectEq(p.text, "450/750 XP", "xp text")
	expectNear(p.fraction, 0.6, 1e-9, "real fraction, not the mockup's drawn fill")
	local max = LobbyHudModel.Progress({ level = 50, xp = 10 })
	expectEq(max.level, "LV. 50", "the cap still reads as its level number")
	expectEq(max.fraction, 1, "full at the cap")
	expectEq(max.text, "Max level", "cap text")
	local loading = LobbyHudModel.Progress(nil)
	expectEq(loading.level, "", "blank while loading")
	expectEq(loading.fraction, 0, "empty while loading")
	expectEq(LobbyHudModel.Progress({ level = 3, xp = 12.7, xpToNext = 100 }).text, "12/100 XP", "whole numbers")
end)

test("solo you lead a party of one; in a party: leader crown, no ready state, invite rights", function()
	local solo = LobbyHudModel.Party({ party = nil, invites = {}, maxSize = 8 }, ME)
	expect(solo.count == "1/8" and #solo.members == 1 and solo.free == 7, "solo: one row, free rows up to the cap")
	expect(solo.members[1].leader and solo.members[1].self and solo.canInvite, "solo: you lead and can invite")
	local view = {
		party = {
			id = "p1",
			leader = 2,
			members = {
				{ userId = 2, name = "Ranger" },
				{ userId = 1, name = "LiamTheMo" },
			},
		},
		invites = { { partyId = "p9", from = "Bob" } },
		maxSize = 8,
	}
	local party = LobbyHudModel.Party(view, ME)
	expectEq(party.count, "2/8", "count")
	expectEq(party.members[1].leader, true, "leader marked")
	expectEq(party.members[1].ready, nil, "no ready flag")
	expectEq(party.members[2].leader, false, "not leader")
	expectEq(party.members[2].self, true, "you")
	expectEq(party.free, 6, "free rows")
	expectEq(party.canInvite, false, "only the leader invites")
	expectEq(party.showReady, nil, "no ready dots")
	expectEq(#party.invites, 1, "incoming invites pass through")
	expectEq(party.invites[1].busy, false, "an invite with no answer on its way")
	local answering = LobbyHudModel.Party(view, ME, { p9 = true })
	expectEq(answering.invites[1].busy, true, "an answer on its way marks the invite busy")
	expectEq(view.invites[1].busy, nil, "the view's own invite table is untouched")
	view.party.leader = 1
	expectEq(LobbyHudModel.Party(view, ME).canInvite, true, "leader invites")
	local full = { party = { leader = 1, members = {} }, maxSize = 2 }
	full.party.members = { { userId = 1, name = "A" }, { userId = 3, name = "B" } }
	local fullParty = LobbyHudModel.Party(full, ME)
	expectEq(fullParty.canInvite, false, "no invites when full")
	expectEq(fullParty.free, 0, "no free rows when full")
	expectEq(LobbyHudModel.Party(nil, ME).count, "1/8", "missing view reads solo with the default cap")
end)

test("hotbar shows what lands in the run's hotbar", function()
	local slots = LobbyHudModel.Hotbar(nil)
	expectEq(#slots, 6, "six slots")
	expectEq(slots[1], false, "unknown preview shows empty slots")
	slots = LobbyHudModel.Hotbar({
		{ catalogId = "Wood", quantity = 40 },
		{ catalogId = "StoneAxe", quantity = 1, permanent = true },
		{ catalogId = "StoneSpear", quantity = 1 },
	})
	-- Tools and weapons prefer the hotbar; materials go to the backpack first.
	expectEq(slots[1] and slots[1].itemId, "StoneAxe", "axe first")
	expectEq(slots[1] and slots[1].permanent, true, "permanent kept")
	expectEq(slots[2] and slots[2].itemId, "StoneSpear", "spear second")
	expectEq(slots[3], false, "wood stays in the backpack")
	local many = {}
	for _ = 1, 8 do
		table.insert(many, { catalogId = "StoneAxe", quantity = 1 })
	end
	slots = LobbyHudModel.Hotbar(many)
	expectEq(#slots, 6, "never more than six")
	expect(slots[6] ~= false, "all six filled")
end)

test("tile grid gamepad neighbours", function()
	local n = LobbyHudModel.TileNeighbours(1)
	expectEq(n.right, 2, "1 -> 2")
	expectEq(n.down, 3, "1 v 3")
	expectEq(n.up, nil, "top edge")
	expectEq(n.left, nil, "left edge")
	n = LobbyHudModel.TileNeighbours(6)
	expectEq(n.left, 5, "6 <- 5")
	expectEq(n.up, 4, "6 ^ 4")
	expectEq(n.down, nil, "bottom edge")
	expectEq(n.right, nil, "right edge")
	-- Phones draw the run's 3 × 2 grid.
	n = LobbyHudModel.TileNeighbours(2, 3)
	expectEq(n.left, 1, "3 columns: 2 <- 1")
	expectEq(n.right, 3, "3 columns: 2 -> 3")
	expectEq(n.down, 5, "3 columns: 2 v 5")
	n = LobbyHudModel.TileNeighbours(4, 3)
	expectEq(n.left, nil, "3 columns: 4 starts the second row")
	expectEq(n.up, 1, "3 columns: 4 ^ 1")
	expectEq(n.down, nil, "3 columns: bottom edge")
end)
