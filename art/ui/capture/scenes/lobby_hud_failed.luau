-- The lobby HUD when its uploaded art is not served (every image reports
-- Failure, as on the device that showed only text): the kit draws its own
-- stand-ins (paper and leather plates, slots, tracks, ink glyphs) instead.
__failImages = true
local Hud = game:GetService("StarterPlayer").StarterPlayerScripts.Client.Hud
local Shared = game:GetService("ReplicatedStorage").Shared
local LobbyHud = require(Hud.Screens.LobbyHud)
local LobbyHudModel = require(Shared.UI.LobbyHudModel)

local W, H = 1672, 941
local BACKGROUND = { background = "art/reference/ui/lobby/01_hud.png" }
local ME = { userId = 1, name = "LiamTheMo" }

local function page()
	local gui, root = __screen(W, H)
	local hud = LobbyHud.new(root, {})
	hud:SetTopInset(58)
	hud:SetProfile(ME.name, ME.userId)
	hud:SetProgress({ level = 12, xp = 450, xpToNext = 750 }, true)
	hud:SetCurrency(2450, 125, true)
	return gui, root, hud
end

-- 1: the mockup.
do
	local _, root, hud = page()
	hud:SetParty(LobbyHudModel.Party({ party = nil, invites = {}, ready = false, maxSize = 8 }, ME))
	hud:SetHotbar(LobbyHudModel.Hotbar({
		{ catalogId = "StoneAxe", quantity = 1 },
		{ catalogId = "StoneSpear", quantity = 1 },
		{ catalogId = "Redberry", quantity = 5 },
		-- Materials pack into the backpack, so Plant Fiber stays out of the hotbar.
		{ catalogId = "Fiber", quantity = 12 },
	}))
	__dump(root, W, H, BACKGROUND)
end

-- 2: in someone else's party, an invite waiting, the update notice, a full hotbar.
do
	local _, root, hud = page()
	hud:SetParty(LobbyHudModel.Party({
		party = {
			id = "p1",
			leader = 2,
			members = {
				{ userId = 2, name = "ForestRanger", ready = true },
				{ userId = 1, name = "LiamTheMo", ready = false },
				{ userId = 3, name = "StoneSeeker", ready = true },
			},
		},
		invites = { { partyId = "p9", from = "RiverFox" } },
		ready = false,
		maxSize = 8,
	}, ME))
	hud:SetProgress({ level = 50, xp = 0 }, true)
	hud:SetNotice("Game update: your items were saved and return on your next Play.")
	hud:SetHotbar(LobbyHudModel.Hotbar({
		{ catalogId = "StoneAxe", quantity = 1, permanent = true },
		{ catalogId = "StonePickaxe", quantity = 1 },
		{ catalogId = "StoneSpear", quantity = 1 },
		{ catalogId = "WoodenBow", quantity = 1 },
		{ catalogId = "FlintArrow", quantity = 40 },
		{ catalogId = "Workbench", quantity = 1 },
	}))
	__dump(root, W, H)
end
