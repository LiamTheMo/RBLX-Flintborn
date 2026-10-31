-- The Settings window (Hud/Screens/SettingsWindow) at 1672 × 941 over the lobby
-- HUD, placed where 03_settings.png draws it, with the mockup's sample values
-- where a real setting matches (Camera Sensitivity 1.0, keys E / B / M /
-- Left Shift). Compare page 1 with:
--   python3 art/ui/capture/capture.py settings --compare art/reference/ui/lobby/03_settings.png
--
--   1 Gameplay (APPLY lit: a change is pending)
--   2 Audio
--   3 Graphics
--   4 Controls
--   5 states: tab hover / pressed, slider hover / pressed, checkbox off and hover,
--     key cap hover, pressed and capturing, RESET pressed, APPLY disabled,
--     close hover
--   6 Graphics with the quality dropdown open, its field focused
--   7 no keyboard: key caps disabled, the Controls note says why
--   8 the Controls list's last rows (what scrolling reveals)
--   9 a landscape phone, 844 × 390, touch only

local Players = game:GetService("Players")
local Shared = game:GetService("ReplicatedStorage").Shared
local Hud = game:GetService("StarterPlayer").StarterPlayerScripts.Client.Hud
local Keybinds = require(Shared.Settings.Keybinds)
local SettingsRules = require(Shared.Settings.SettingsRules)
local Kit = require(Hud.Kit)
local SettingsWindow = require(Hud.Screens.SettingsWindow)

local W, H = 1672, 941
local BACKGROUND = { background = "art/reference/ui/lobby/01_hud.png" }
local noop = function() end

local view = SettingsWindow.new(Players.LocalPlayer.PlayerGui, {
	onApply = noop,
	onReset = noop,
	onChange = noop,
	onRebind = noop,
	onReplayTutorial = noop,
})
view.screen:Open()
-- Pinned to the mockup's scale and place (in game Kit.Scale fits and centres it).
view.screen.scale.Scale = 1
view.screen.holder.Position = UDim2.fromOffset(287 + 1098 / 2, 150 + 656 / 2)

local values = SettingsRules.Resolve(nil)
view:SetValues(values)
local keys = Keybinds.Resolve(nil)
view:SetKeys(keys, nil, nil, true)
view:SetDirty(true)

local function dump()
	__dump(Players.LocalPlayer.PlayerGui, W, H, BACKGROUND)
end

for _, tab in SettingsWindow.TABS do
	view:SelectTab(tab.id)
	dump()
end

-- Page 5: states, forced through DebugState as verifiers do.
view:SelectTab("Gameplay")
local force = Kit.Debug.Force
force(view.tabs.Audio.root, "hover")
force(view.tabs.Graphics.root, "pressed")
local gameplay = view.pages.Gameplay
force(gameplay.cameraSensitivity, "hover")
force(gameplay.musicVolume, "pressed")
local unchecked = table.clone(values)
unchecked.showNames = false
view:SetValues(unchecked)
force(gameplay.showDamage, "hover")
force(gameplay.Key_Interact, "hover")
force(gameplay.Key_Backpack, "pressed")
view:SetKeys(keys, "Map", nil, true)
force(view.reset.root, "pressed")
view:SetDirty(false)
force(view.close.root, "hover")
dump()
for _, root in
	{
		view.tabs.Audio.root,
		view.tabs.Graphics.root,
		gameplay.cameraSensitivity,
		gameplay.musicVolume,
		gameplay.showDamage,
		gameplay.Key_Interact,
		gameplay.Key_Backpack,
		view.reset.root,
		view.close.root,
	}
do
	force(root, nil)
end
view:SetValues(values)
view:SetKeys(keys, nil, nil, true)
view:SetDirty(true)

-- Page 6: the quality list open.
view:SelectTab("Graphics")
view.dropdowns[1]:SetOpen(true)
dump()
view.dropdowns[1]:SetOpen(false)

-- Page 7: no keyboard.
view:SelectTab("Controls")
view:SetKeys(keys, nil, nil, false)
dump()

-- Page 8: the rest of the Controls list, down to Settings. The renderer draws a
-- ScrollingFrame from its top (CanvasPosition is not drawn), so the first 11
-- rows are hidden for this page to show the rows a scroll reveals.
view:SetKeys(keys, nil, nil, true)
local rows = {}
for _, row in view.keyList:Content():GetChildren() do
	if row:IsA("Frame") and row.LayoutOrder <= 11 then
		row.Visible = false
		table.insert(rows, row)
	end
end
dump()
for _, row in rows do
	row.Visible = true
end

-- Page 9: a landscape phone (844 × 390, touch only): the window fills the
-- room under the top bar, as Kit.Scale fits it in game.
local UserInputService = game:GetService("UserInputService")
UserInputService.TouchEnabled = true
UserInputService.KeyboardEnabled = false
view:SelectTab("Gameplay")
view:SetKeys(keys, nil, nil, false)
view.screen:Fit(844, 390, 52, 1)
__dump(Players.LocalPlayer.PlayerGui, 844, 390, BACKGROUND)
