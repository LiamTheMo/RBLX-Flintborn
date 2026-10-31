-- The Settings window on a phone held sideways (667 x 375, touch only, the top
-- bar 58 px down), every tab, fitted as in game; prints the smallest text.
local Players = game:GetService("Players")
local UserInputService = game:GetService("UserInputService")
local Shared = game:GetService("ReplicatedStorage").Shared
local Hud = game:GetService("StarterPlayer").StarterPlayerScripts.Client.Hud
workspace.CurrentCamera.ViewportSize = Vector2.new(667, 375)
UserInputService.TouchEnabled = true
UserInputService.KeyboardEnabled = false
UserInputService.MouseEnabled = false
UserInputService.GetLastInputType = function()
	return Enum.UserInputType.Touch
end
local Keybinds = require(Shared.Settings.Keybinds)
local SettingsRules = require(Shared.Settings.SettingsRules)
local SettingsWindow = require(Hud.Screens.SettingsWindow)
local noop = function() end

-- Effective screen size of every fixed-size kit label (scaled labels shrink to
-- their box and are listed apart).
local function report(gui, scale, tag)
	local smallest, count = math.huge, 0
	for _, item in gui:GetDescendants() do
		local shown = item.Visible
		local node = item.Parent
		while shown and node and node:IsA("GuiObject") do
			shown = node.Visible
			node = node.Parent
		end
		if shown and item:IsA("TextLabel") and item:GetAttribute("KitTextRole") and item.Text ~= "" then
			local px = item.TextSize * scale
			count += 1
			if px < smallest then
				smallest = px
			end
			if px < 9 then
				print(("  under 9 px: %s %q %.1f px (%s)"):format(tag, item.Text, px, item:GetAttribute("KitTextRole")))
			end
		end
	end
	print(("%s: window scale %.3f, %d labels, smallest %.1f screen px"):format(tag, scale, count, smallest))
end

local view = SettingsWindow.new(Players.LocalPlayer.PlayerGui, {
	onApply = noop,
	onReset = noop,
	onChange = noop,
	onRebind = noop,
	onReplayTutorial = noop,
})
view.screen:Open()
view.screen:Fit(667, 375, 58, 1)
view:SetValues(SettingsRules.Resolve(nil))
view:SetKeys(Keybinds.Resolve(nil), nil, nil, true)
for _, tab in SettingsWindow.TABS do
	view:SelectTab(tab.id)
	report(view.screen.gui, view.screen.scale.Scale, "settings_phone_small " .. tab.id)
	__dump(Players.LocalPlayer.PlayerGui, 667, 375)
end
