-- The Settings window on every tab, at the design size, with the reference
-- sheet's values (Music 75, Effects 80, Camera 60) and keys (Interact E, Map M).
local Shared = game:GetService("ReplicatedStorage").Shared
local Hud = game:GetService("StarterPlayer").StarterPlayerScripts.Client.Hud
local Keybinds = require(Shared.Settings.Keybinds)
local SettingsRules = require(Shared.Settings.SettingsRules)
local SettingsPanel = require(Hud.SettingsPanel)

local gui, root = __screen()
local noop = function() end
local panel = SettingsPanel.new(root, {
	onClose = noop,
	onApply = noop,
	onReset = noop,
	onChange = noop,
	onRebind = noop,
	onReplayTutorial = noop,
})
panel.screen.gui.Enabled = true
panel.screen:Fit(1672, 941, 0, 1)
-- Pinned to the sheet's own scale and place so the capture overlays the reference
-- (in game Fit centres it below the top bar).
panel.screen.scale.Scale = 1
panel.screen.window.Position = UDim2.fromOffset(21 + 815, 58 + 353)

local values = SettingsRules.Resolve(nil)
values.cameraSensitivity = 60
panel:SetValues(values)
local keys = Keybinds.Resolve({ Interact = "E", Map = "M" })
panel:SetKeys(keys, nil, nil, true)
panel:SetDirty(true)

for _, tab in SettingsPanel.TABS do
	panel:SelectTab(tab.id)
	__dump(panel.screen.gui, 1672, 941)
end
