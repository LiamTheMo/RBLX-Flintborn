-- The lobby screen at the design size with sample data.
local Hud = game:GetService("StarterPlayer").StarterPlayerScripts.Client.Hud
local Layout = require(Hud.Layout)
local LobbyHud = require(Hud.LobbyHud)

local layout = Layout.Get()
local gui, root = __screen()
local hud = LobbyHud.new(root, layout, function()
	return true
end)
hud:Fit(1672, 941, 58, 1)
hud:SetProfile("LiamTheMo", "rbxthumb://type=AvatarHeadShot&id=1&w=150&h=150")
hud:SetProgress({ level = 12, xp = 76, xpToNext = 100 }, true)
hud:SetCurrency(2450, 125)
hud:SetParty({ { userId = 1, name = "LiamTheMo", leader = true, thumbnail = "rbxthumb://x" } }, {}, 8, true, false)
__dump(root, 1672, 941)
