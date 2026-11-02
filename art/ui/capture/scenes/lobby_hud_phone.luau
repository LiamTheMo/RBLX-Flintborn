-- A phone held sideways (844 × 390, touch only): the HUD scale × 0.9 and the top bar 58 px down.
-- Built with the real scaling (Kit.Scale.Hud, as LobbyHudController does) and the
-- mockup's sample data; page 2 is the same screen in a party of three with an
-- invite waiting, the game-update notice and XP pop-ups stacked above it.
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

local W, H = 844, 390
local TOP_BAR = 58
local ME = { userId = 1, name = "LiamTheMo" }
workspace.CurrentCamera.ViewportSize = Vector2.new(W, H)
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

-- The Settings button sits left of where Roblox puts the jump button, centred
-- on its height, clear of the Party panel above and the hotbar to its left.
local function gearClear(hud, scale)
	local HudModel = require(Shared.UI.HudModel)
	local g = LobbyHud.GEAR
	local at = hud.settingsRegion.Position
	-- Screen rectangles {x1, y1, x2, y2}.
	local x2, y2 = W + at.X.Offset * scale, H + at.Y.Offset * scale
	local gear = { x2 - g.w * scale, y2 - g.h * scale, x2, y2 }
	local jumpAt = HudModel.JumpButton(W, H)
	local party = hud.partyRegion
	local partyFoot = (party.Position.Y.Offset + party.Size.Y.Offset) * scale
	local bottom = hud.bottom
	local hotbarRight = W / 2 + bottom.Size.X.Offset / 2 * scale
	local ok = gear[3] + g.gap <= jumpAt.x and gear[2] > partyFoot and gear[1] > hotbarRight
	print(
		("  %s lobby_hud_phone: the gear (%d..%d x %d..%d) clears the jump button (x %d), the Party panel (foot %d) and the hotbar (right %d)"):format(
			if ok then "ok" else "FAIL",
			gear[1],
			gear[3],
			gear[2],
			gear[4],
			jumpAt.x,
			partyFoot,
			hotbarRight
		)
	)
	if not ok then
		error("lobby_hud_phone: the settings gear overlaps")
	end
end

local function page(view, notice)
	local gui, root = __screen(W, H)
	local hud = LobbyHud.new(root, {})
	Kit.Scale.Hud(gui, root)
	local scale = root:FindFirstChildWhichIsA("UIScale").Scale
	hud:SetTopInset(TOP_BAR / scale)
	hud:SetScreen(W, H, scale, true)
	gearClear(hud, scale)
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
	print(("lobby_hud_phone: scale %.3f, root %d x %d design px"):format(scale, W / scale, H / scale))
	__dump(gui, W, H)
end

page({ party = nil, invites = {}, maxSize = 8 })
page({
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
}, "Game update: your items were saved and return on your next Play.")
