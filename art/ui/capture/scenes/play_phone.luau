-- The Play window on a phone held sideways (844 × 390, touch only, the top bar
-- 58 px down), fitted by Kit.Scale.Window as in game (it fills the screen for
-- readability, ARCHITECTURE §1.1), with the mockup's sample data. Page 2: a
-- tall phone at 2000 × 924 (the owner's test device), also touch only.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")
local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local PlayModel = require(ReplicatedStorage.Shared.UI.PlayModel)
local PlayWindow = require(Client.Hud.Screens.PlayWindow)

local W, H = 844, 390
workspace.CurrentCamera.ViewportSize = Vector2.new(W, H)
UserInputService.TouchEnabled = true
UserInputService.KeyboardEnabled = false
-- The last input was a touch (Kit.Input: no keyboard hotkey badges).
UserInputService.GetLastInputType = function()
	return Enum.UserInputType.Touch
end

local preview = {
	{ catalogId = "StoneAxe" },
	{ catalogId = "StoneSpear" },
	{ catalogId = "BasicMedicine", quantity = 3 },
}
local function page(w: number, h: number)
	workspace.CurrentCamera.ViewportSize = Vector2.new(w, h)
	local window = PlayWindow.new({})
	local details = PlayModel.WorldRows()
	table.insert(details, PlayModel.CarryingRow(preview))
	window:SetDetails(details)
	window:SetParty({ { userId = 1, name = "LiamTheMo", level = 12, leader = true } })
	window:SetLoadout(PlayModel.LoadoutHotbar(preview))
	window:SetMode("solo")
	window.screen:Watch()
	window:Open()
	print(("play_phone %d × %d: window scale %.3f"):format(w, h, window.screen.scale.Scale))
	__dump(Players.LocalPlayer.PlayerGui, w, h)
	window:Destroy()
end

page(W, H)
page(2000, 924)
