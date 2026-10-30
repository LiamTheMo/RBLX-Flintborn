-- The Party window (docs/ui/PartyScreen.md) at 1672 × 941 over the lobby
-- mockup, with the mockup's sample data: LiamTheMo (LV 12) leads a party of
-- one formed just now and is ready; ForestRanger (LV 15) and SunnyVale (LV 8)
-- can be invited. Compare with art/reference/ui/lobby/04_party.png:
--
--   python3 art/ui/capture/capture.py party --compare art/reference/ui/lobby/04_party.png

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Hud = game:GetService("StarterPlayer").StarterPlayerScripts.Client.Hud
local PartyModel = require(ReplicatedStorage.Shared.UI.PartyModel)
local PartyWindow = require(Hud.Screens.PartyWindow)

local W, H = 1672, 941
local NOW = 1_700_000_000

local view = {
	party = {
		id = "p1",
		leader = 1,
		createdAt = NOW - 12,
		members = { { userId = 1, name = "LiamTheMo", ready = true } },
		invited = {},
	},
	invites = {},
	ready = true,
	maxSize = 8,
}
local candidates = {
	{ userId = 2, name = "ForestRanger", userName = "ForestRanger" },
	{ userId = 3, name = "SunnyVale", userName = "SunnyVale" },
}
local data = PartyModel.WindowData(view, { userId = 1, name = "LiamTheMo" }, candidates, {
	now = NOW,
	levels = { [1] = 12, [2] = 15, [3] = 8 },
})

local window = PartyWindow.new({})
window:SetData(data)
window:Open()
-- Where the mockup draws the window (its centre is 836, 461.5).
window.screen.holder.Position = UDim2.fromOffset(268 + 1136 / 2, 139 + 642 / 2)
window.screen.scale.Scale = 1
__dump(Players.LocalPlayer.PlayerGui, W, H, { background = "art/reference/ui/lobby/01_hud.png" })
window:Destroy()
