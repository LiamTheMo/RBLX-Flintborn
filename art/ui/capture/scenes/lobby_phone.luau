-- The lobby on a 750 x 390 phone: the fit scale, the top bar 58 px down.
local Hud = game:GetService("StarterPlayer").StarterPlayerScripts.Client.Hud
local Layout = require(Hud.Layout)
local LobbyHud = require(Hud.LobbyHud)
local HudModel = require(game:GetService("ReplicatedStorage").Shared.UI.HudModel)
local layout = Layout.Get()
local gui, root = __screen()
local scale = HudModel.HudScale(750, 390, 1672, 941, layout.scale.min, layout.scale.max, 1) * 0.9
local ui = Instance.new("UIScale")
ui.Scale = scale
ui.Parent = root
root.Size = UDim2.fromScale(1 / scale, 1 / scale)
local hud = LobbyHud.new(root, layout, function() return true end)
hud:Fit(750 / scale, 390 / scale, 58 / scale, scale)
hud:SetProfile("OrangeCheasy", "rbxthumb://x")
hud:SetProgress({ level = 2, xp = 40, xpToNext = 100 }, true)
hud:SetCurrency(0, 0)
hud:SetParty({ { userId = 1, name = "OrangeCheasy", leader = true, thumbnail = "rbxthumb://x" } }, {}, 8, true, false)
print("scale", scale)
__dump(gui, 750, 390)
