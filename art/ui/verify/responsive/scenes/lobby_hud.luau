-- QA: the lobby HUD as LobbyHudController builds and scales it (Kit.Scale.Hud,
-- SetTopInset(WindowTop / scale) with the top bar at QA.top px).
--   page 1: sample data, a party of three and an invite
--   page 2: long strings (20-char display names, 8 members, big balances, level 100, notice)
local Hud = game:GetService("StarterPlayer").StarterPlayerScripts.Client.Hud
local Shared = game:GetService("ReplicatedStorage").Shared
local Kit = require(Hud.Kit)
local LobbyHud = require(Hud.Screens.LobbyHud)
local LobbyHudModel = require(Shared.UI.LobbyHudModel)

local W, H = QA.W, QA.H

local function page(me, view, coins, gems, progress, notice, hotbar)
	local gui, root = __screen(W, H)
	local hud = LobbyHud.new(root, {})
	Kit.Scale.Hud(gui, root)
	local scale = root:FindFirstChildWhichIsA("UIScale").Scale
	hud:SetTopInset(math.max(QA.top, 52) / scale)
	hud:SetProfile(me.name, me.userId)
	hud:SetProgress(progress, true)
	hud:SetCurrency(coins, gems, true)
	hud:SetParty(LobbyHudModel.Party(view, me))
	hud:SetHotbar(LobbyHudModel.Hotbar(hotbar))
	if notice then
		hud:SetNotice(notice)
	end
	QA.mark(hud:DefaultSelection(), "DefaultSelection")
	QA.report(gui, { scale = scale, defaultSelectionCalledByController = false })
	__dump(gui, W, H)
end

page({ userId = 1, name = "LiamTheMo" }, {
	party = {
		id = "p1",
		leader = 1,
		members = {
			{ userId = 1, name = "LiamTheMo", ready = true },
			{ userId = 2, name = "ForestRanger", ready = true },
			{ userId = 3, name = "StoneSeeker", ready = false },
		},
	},
	invites = { { partyId = "p9", from = "RiverFox" } },
	ready = true,
	maxSize = 8,
}, 2450, 125, { level = 12, xp = 450, xpToNext = 750 }, nil, {
	{ catalogId = "StoneAxe", quantity = 1 },
	{ catalogId = "StoneSpear", quantity = 1 },
	{ catalogId = "Redberry", quantity = 5 },
})

local LONG = "MightyWarriorQueen99"
local WIDE = "WWWWWWWWWWWWWWWWWWWW"
local members = { { userId = 1, name = LONG, ready = true } }
for i = 2, 8 do
	table.insert(members, { userId = i, name = if i % 2 == 0 then WIDE else ("Explorer_Of_Isles_" .. i), ready = i % 3 == 0 })
end
page({ userId = 1, name = LONG }, {
	party = { id = "p1", leader = 2, members = members },
	invites = { { partyId = "p9", from = WIDE } },
	ready = true,
	maxSize = 8,
}, 9999999, 999999, { level = 100, xp = 123456, xpToNext = 999999 },
	"Game update: your items were saved and return on your next Play. Servers restart in 5 minutes.", {
	{ catalogId = "StoneAxe", quantity = 1, permanent = true },
	{ catalogId = "StonePickaxe", quantity = 1 },
	{ catalogId = "StoneSpear", quantity = 1 },
	{ catalogId = "WoodenBow", quantity = 1 },
	{ catalogId = "FlintArrow", quantity = 999 },
	{ catalogId = "Workbench", quantity = 1 },
})
