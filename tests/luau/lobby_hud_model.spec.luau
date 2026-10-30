local Shared = game:GetService("ReplicatedStorage").Shared
local ItemInfo = require(Shared.Items.ItemInfo)
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
	expectEq(max.level, "MAX", "level cap")
	expectEq(max.fraction, 1, "full at the cap")
	expectEq(max.text, "Max level", "cap text")
	local loading = LobbyHudModel.Progress(nil)
	expectEq(loading.level, "", "blank while loading")
	expectEq(loading.fraction, 0, "empty while loading")
	expectEq(LobbyHudModel.Progress({ level = 3, xp = 12.7, xpToNext = 100 }).text, "12/100 XP", "whole numbers")
end)

test("solo: a party of one led by you, with your ready flag", function()
	local party = LobbyHudModel.Party({ party = nil, invites = {}, ready = true, maxSize = 8 }, ME)
	expectEq(party.count, "1/8", "count")
	expectEq(#party.members, 1, "one row")
	expectEq(party.members[1].leader, true, "you lead")
	expectEq(party.members[1].ready, true, "solo ready shows")
	expectEq(party.members[1].self, true, "self")
	expectEq(party.free, 7, "free rows up to the cap")
	expectEq(party.canInvite, true, "solo can invite")
end)

test("in a party: leader crown, ready flags, invite rights", function()
	local view = {
		party = {
			id = "p1",
			leader = 2,
			members = {
				{ userId = 2, name = "Ranger", ready = true },
				{ userId = 1, name = "LiamTheMo", ready = false },
			},
		},
		invites = { { partyId = "p9", from = "Bob" } },
		ready = false,
		maxSize = 8,
	}
	local party = LobbyHudModel.Party(view, ME)
	expectEq(party.count, "2/8", "count")
	expectEq(party.members[1].leader, true, "leader marked")
	expectEq(party.members[1].ready, true, "member ready")
	expectEq(party.members[2].leader, false, "not leader")
	expectEq(party.members[2].self, true, "you")
	expectEq(party.free, 6, "free rows")
	expectEq(party.canInvite, false, "only the leader invites")
	expectEq(#party.invites, 1, "incoming invites pass through")
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
	expectEq(slots[1] and slots[1].catalogId, "StoneAxe", "axe first")
	expectEq(slots[1] and slots[1].permanent, true, "permanent kept")
	expectEq(slots[1] and slots[1].icon, ItemInfo.Icon("StoneAxe"), "icon id for art-less items")
	expectEq(slots[2] and slots[2].catalogId, "StoneSpear", "spear second")
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
end)
