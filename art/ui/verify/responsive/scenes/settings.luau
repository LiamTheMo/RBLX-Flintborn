-- QA: the Settings window (Hud/Screens/SettingsWindow) fitted by screen:Watch and
-- opened the way SettingsController.Toggle opens it. Pages: Gameplay, Audio,
-- Graphics (quality dropdown open), Controls; then B.
local Players = game:GetService("Players")
local GuiService = game:GetService("GuiService")
local UserInputService = game:GetService("UserInputService")
local Shared = game:GetService("ReplicatedStorage").Shared
local Hud = game:GetService("StarterPlayer").StarterPlayerScripts.Client.Hud
local Keybinds = require(Shared.Settings.Keybinds)
local SettingsRules = require(Shared.Settings.SettingsRules)
local SettingsWindow = require(Hud.Screens.SettingsWindow)
local noop = function() end

local view = SettingsWindow.new(Players.LocalPlayer.PlayerGui, {
	onApply = noop,
	onReset = noop,
	onChange = noop,
	onRebind = noop,
	onReplayTutorial = noop,
})
view.screen:Watch()
view:SetValues(SettingsRules.Resolve(nil))
local keys = Keybinds.Resolve(nil)
view:SetKeys(keys, nil, nil, QA.kbm)
view:SetDirty(true)
view:SelectTab("Gameplay")
view.screen:SetDefaultSelection(view.tabs.Gameplay.control.hit)
view.screen:Open(GuiService.SelectedObject ~= nil or UserInputService.GamepadEnabled)
for _, tab in SettingsWindow.TABS do
	view:SelectTab(tab.id)
	if tab.id == "Graphics" then
		view.dropdowns[1]:SetOpen(true)
	end
	QA.report(Players.LocalPlayer.PlayerGui, { scale = view.screen.scale.Scale, tab = tab.id })
	__dump(Players.LocalPlayer.PlayerGui, QA.W, QA.H)
	if tab.id == "Graphics" then
		view.dropdowns[1]:SetOpen(false)
	end
end
print("QA back:", QA.back(), "open after B:", view.screen:IsOpen())
