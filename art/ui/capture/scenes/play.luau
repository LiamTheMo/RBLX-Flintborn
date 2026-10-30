-- The Play window (docs/ui/PlayScreen.md) at 1672 × 941 with the mockup's
-- sample data, placed where art/reference/ui/lobby/05_play.png has it, over the
-- lobby HUD mockup. Compare with:
--
--   python3 art/ui/capture/capture.py play --compare art/reference/ui/lobby/05_play.png

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local PlayModel = require(ReplicatedStorage.Shared.UI.PlayModel)
local PlayWindow = require(Client.Hud.Screens.PlayWindow)

local W, H = 1672, 941

-- The mockup's loadout: a stone axe, a spear and a herb bundle (Basic Medicine,
-- which packs into the hotbar as the mockup shows; materials go to the backpack).
local preview = {
	{ catalogId = "StoneAxe" },
	{ catalogId = "StoneSpear" },
	{ catalogId = "BasicMedicine", quantity = 3 },
}

local window = PlayWindow.new({})
local details = PlayModel.WorldRows()
table.insert(details, PlayModel.CarryingRow(preview))
window:SetDetails(details)
window:SetParty({ { userId = 1, name = "LiamTheMo", level = 12, leader = true, ready = false } }, false)
window:SetLoadout(PlayModel.LoadoutHotbar(preview))
window:SetMode("solo")
window:Open()
-- The mockup's window: 309..1361 × 127..791.
window.screen.holder.Position = UDim2.fromOffset(309 + PlayWindow.SIZE[1] / 2, 127 + PlayWindow.SIZE[2] / 2)
window.screen.scale.Scale = 1
__dump(Players.LocalPlayer.PlayerGui, W, H, { background = "art/reference/ui/lobby/01_hud.png" })
