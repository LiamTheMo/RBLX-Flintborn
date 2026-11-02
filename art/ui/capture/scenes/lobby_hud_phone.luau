-- A notched phone held sideways (844 × 390, touch only; the device safe area
-- keeps 47 px at each side, __NOTCHED_PHONE): the HUD scale × 0.9 and the top
-- bar 58 px down, with stand-ins for Roblox's top-bar buttons, the touch jump
-- button and the thumbstick ring inside the safe area, the notch drawn at the
-- left. Built with the real scaling (Kit.Scale.Hud, as LobbyHudController
-- does) and the mockup's sample data; page 2 is the same screen in a party of
-- three with an invite waiting, the game-update notice and XP pop-ups stacked
-- above it; pages 3 and 4 are a 667 × 375 phone without a notch (Settings
-- above the thumbstick ring, the tiles moved up for its touch pad) and a
-- 2000 × 924 touch screen. The layout checks (hud_checks.luau, ARCHITECTURE
-- D28, D29: the pills and the Party panel at the right edge by the edge rule,
-- Settings in the bottom-left corner left of the thumbstick) run on each.
local Hud = game:GetService("StarterPlayer").StarterPlayerScripts.Client.Hud
-- Members' replicated level and progress (PlayerRow levelBar reads them).
for userId, level in { [1] = { 12, 0.6 }, [2] = { 15, 0.35 }, [3] = { 8, 0.8 }, [4] = { 21, 0.15 }, [5] = { 3, 0.5 } } do
	local member = game:GetService("Players"):GetPlayerByUserId(userId)
	member:SetAttribute("Level", level[1])
	member:SetAttribute("LevelProgress", level[2])
end
local Shared = game:GetService("ReplicatedStorage").Shared
local UserInputService = game:GetService("UserInputService")
local Kit = require(Hud.Kit)
local LobbyHud = require(Hud.Screens.LobbyHud)
local LobbyHudModel = require(Shared.UI.LobbyHudModel)

local TOP_BAR = 58
local ME = { userId = 1, name = "LiamTheMo" }
UserInputService.TouchEnabled = true
UserInputService.KeyboardEnabled = false
-- The last input was a touch (Kit.Input: no keyboard hotkey badges).
UserInputService.GetLastInputType = function()
	return Enum.UserInputType.Touch
end

-- Sample XP pop-ups in the HUD's lane, drawn as ProgressionController draws
-- them, and a check that the lane ends above the game-update notice.
local function xpPopups(hud)
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
		("  %s lobby_hud_phone: the XP pop-up lane ends above the notice (%d <= %d)"):format(
			if clear then "ok" else "FAIL",
			foot,
			notice.Position.Y.Offset
		)
	)
	if not clear then
		error("lobby_hud_phone: XP pop-ups overlap the notice")
	end
end

local function page(W, H, view, notice, insets)
	workspace.CurrentCamera.ViewportSize = Vector2.new(W, H)
	local gui, root = __screen(W, H)
	local hud = LobbyHud.new(root, {})
	Kit.Scale.Hud(gui, root)
	local scale = root:FindFirstChildWhichIsA("UIScale").Scale
	local chrome = __robloxChrome(gui, W, H, { touch = true, bar = TOP_BAR, insets = insets })
	local lift = __placeLobbyHud(hud, W, H, scale, chrome, true)
	hud:SetProgress({ level = 12, xp = 450, xpToNext = 750 }, true)
	hud:SetCurrency(2450, 125, true)
	hud:SetParty(LobbyHudModel.Party(view, ME))
	hud:SetHotbar(LobbyHudModel.Hotbar({
		{ catalogId = "StoneAxe", quantity = 1 },
		{ catalogId = "StoneSpear", quantity = 1 },
		{ catalogId = "Redberry", quantity = 5 },
	}))
	if notice then
		hud:SetNotice(notice)
		xpPopups(hud)
	end
	print(
		("lobby_hud_phone %dx%d: scale %.3f, root %d x %d design px, tiles lifted %d design px"):format(
			W,
			H,
			scale,
			W / scale,
			H / scale,
			lift
		)
	)
	__checkLobbyHud({
		scene = ("lobby_hud_phone %dx%d"):format(W, H),
		hud = hud,
		root = root,
		W = W,
		H = H,
		k = scale,
		chrome = chrome,
		phone = Kit.Scale.FormFactor() == "phone",
	})
	__dump(gui, W, H)
end

local SOLO = { party = nil, invites = {}, maxSize = 8 }
page(844, 390, SOLO, nil, __NOTCHED_PHONE)
page(844, 390, {
	party = {
		id = "p1",
		leader = 1,
		members = {
			{ userId = 1, name = "LiamTheMo" },
			{ userId = 2, name = "ForestRanger" },
			{ userId = 3, name = "StoneSeeker" },
		},
	},
	invites = { { partyId = "p9", from = "RiverFox" } },
	maxSize = 8,
}, "Game update: your items were saved and return on your next Play.", __NOTCHED_PHONE)
page(667, 375, SOLO)
page(2000, 924, SOLO)
__hudChecksDone("lobby_hud_phone")
