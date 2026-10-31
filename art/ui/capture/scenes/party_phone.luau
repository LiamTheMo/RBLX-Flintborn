-- The Party window on a phone held sideways (844 × 390, touch only, the top bar
-- 58 px down): the real window fit (Kit.Scale.Window via screen:Watch) fills the
-- room under the top bar for readability (ARCHITECTURE §1.1). Sample data as in
-- the party scene, in a party of three with an invitation waiting.
--
--   python3 art/ui/capture/capture.py party_phone

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")
local Hud = game:GetService("StarterPlayer").StarterPlayerScripts.Client.Hud
local PartyModel = require(ReplicatedStorage.Shared.UI.PartyModel)
local PartyWindow = require(Hud.Screens.PartyWindow)

local W, H = 844, 390
local NOW = 1_700_000_000
workspace.CurrentCamera.ViewportSize = Vector2.new(W, H)
UserInputService.TouchEnabled = true
UserInputService.KeyboardEnabled = false
UserInputService.MouseEnabled = false

local view = {
	party = {
		id = "p1",
		leader = 1,
		createdAt = NOW - 12 * 60,
		members = {
			{ userId = 1, name = "LiamTheMo", ready = true },
			{ userId = 2, name = "ForestRanger", ready = false },
			{ userId = 3, name = "SunnyVale", ready = true },
		},
		invited = { 4 },
	},
	invites = { { partyId = "p9", from = "RiverFox", fromUserId = 6 } },
	ready = true,
	maxSize = 8,
}
local data = PartyModel.WindowData(view, { userId = 1, name = "LiamTheMo" }, {
	{ userId = 4, name = "Emberwick", userName = "Emberwick" },
	{ userId = 5, name = "MossyStone", userName = "MossyStone" },
}, { now = NOW, levels = { [1] = 12, [2] = 15, [3] = 8, [4] = 21, [5] = 3, [6] = 9 } })

local window = PartyWindow.new({})
window:SetData(data)
window:Open()
local screen = window.screen
-- The capture env has no AbsoluteSize: fit the way Scale.Window does in game.
screen:Fit(W, H, 58, 1)
local k = screen.scale.Scale
print(("party_phone: window scale %.3f -> %d x %d screen px"):format(k, 1124 * k, 637 * k))
__dump(Players.LocalPlayer.PlayerGui, W, H)
window:Destroy()
