-- The lobby HUD (Hud/Screens/LobbyHud) at the 1672 × 941 design size with the
-- mockup's sample data, drawn over the mockup's world (art/reference/ui/lobby/01_hud.png).
--   1 the mockup state: LiamTheMo, LV 12, 450/750 XP, 2,450 Coins, 125 Gems,
--     party 1/8, hotbar Stone Axe, Stone Spear, Redberries (the mockup's
--     plant bundle is a material, which never lands in the hotbar)
--   2 a party of three with an incoming invite, a non-leader's view, the
--     game-update notice with XP pop-ups stacked above it, and a full hotbar
-- Stand-ins for Roblox's top-bar buttons are drawn at the top left; the layout
-- checks (hud_checks.luau, ARCHITECTURE D28: Settings at the bottom left, the
-- pills alone at the top right) run on both pages.
local Hud = game:GetService("StarterPlayer").StarterPlayerScripts.Client.Hud
-- Members' replicated level and progress (PlayerRow levelBar reads them).
for userId, level in { [1] = { 12, 0.6 }, [2] = { 15, 0.35 }, [3] = { 8, 0.8 }, [4] = { 21, 0.15 }, [5] = { 3, 0.5 } } do
	local member = game:GetService("Players"):GetPlayerByUserId(userId)
	member:SetAttribute("Level", level[1])
	member:SetAttribute("LevelProgress", level[2])
end
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
	hud:SetScreen(W, H, 1, false)
	hud.chrome = __robloxChrome(root, W, H)
	hud:SetProgress({ level = 12, xp = 450, xpToNext = 750 }, true)
	hud:SetCurrency(2450, 125, true)
	return gui, root, hud
end

local function check(root, hud)
	__checkLobbyHud({ scene = "lobby_hud", hud = hud, root = root, W = W, H = H, k = 1, chrome = hud.chrome })
end

-- A sample XP pop-up in the HUD's lane, drawn as ProgressionController draws
-- one, and a check that the lane ends above the game-update notice.
local function xpPopups(hud, tag)
	local Kit = require(Hud.Kit)
	local lane = hud.popups
	local list = Instance.new("UIListLayout")
	list.VerticalAlignment = Enum.VerticalAlignment.Bottom
	list.Padding = UDim.new(0, 2)
	list.Parent = lane
	for _, line in { { "Level up! +120 XP · Quest", true }, { "+40 XP · Gathered", false } } do
		local label = Kit.Text.new(lane, {
			name = "Popup",
			size = { 320, if line[2] then 24 else 20 },
			text = line[1],
			role = "hudSmall",
			textSize = if line[2] then 18 else 15,
			color = if line[2] then "gold" else "cream",
			outline = "ink",
		}).root
		label.Size = UDim2.new(1, 0, 0, if line[2] then 24 else 20)
	end
	local notice = hud.noticeRegion
	local foot = lane.Position.Y.Offset + lane.Size.Y.Offset
	local clear = not notice.Visible or foot <= notice.Position.Y.Offset
	print(
		("  %s %s: the XP pop-up lane ends above the notice (%d <= %d)"):format(
			if clear then "ok" else "FAIL",
			tag,
			foot,
			notice.Position.Y.Offset
		)
	)
	if not clear then
		error(tag .. ": XP pop-ups overlap the notice")
	end
end

-- 1: the mockup.
do
	local _, root, hud = page()
	hud:SetParty(LobbyHudModel.Party({ party = nil, invites = {}, maxSize = 8 }, ME))
	hud:SetHotbar(LobbyHudModel.Hotbar({
		{ catalogId = "StoneAxe", quantity = 1 },
		{ catalogId = "StoneSpear", quantity = 1 },
		{ catalogId = "Redberry", quantity = 5 },
		-- Materials pack into the backpack, so Plant Fiber stays out of the hotbar.
		{ catalogId = "Fiber", quantity = 12 },
	}))
	check(root, hud)
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
				{ userId = 2, name = "ForestRanger" },
				{ userId = 1, name = "LiamTheMo" },
				{ userId = 3, name = "StoneSeeker" },
			},
		},
		invites = { { partyId = "p9", from = "RiverFox" } },
		maxSize = 8,
	}, ME))
	hud:SetProgress({ level = 50, xp = 0 }, true)
	hud:SetNotice("Game update: your items were saved and return on your next Play.")
	xpPopups(hud, "lobby_hud")
	hud:SetHotbar(LobbyHudModel.Hotbar({
		{ catalogId = "StoneAxe", quantity = 1, permanent = true },
		{ catalogId = "StonePickaxe", quantity = 1 },
		{ catalogId = "StoneSpear", quantity = 1 },
		{ catalogId = "WoodenBow", quantity = 1 },
		{ catalogId = "FlintArrow", quantity = 40 },
		{ catalogId = "Workbench", quantity = 1 },
	}))
	check(root, hud)
	__dump(root, W, H)
end
__hudChecksDone("lobby_hud")
