-- Drives SettingsController headlessly: open, change values, APPLY, RESET, rebind,
-- and checks what reaches the server. Dumps the window after the changes.
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
-- The server makes the remotes; here they are stand-ins that record what is sent.
local folder = Instance.new("Folder")
folder.Name = "FlintbornRemotes"
folder.Parent = ReplicatedStorage
local sent = {}
for _, name in { "SaveSettings", "SaveKeybinds", "TutorialAction" } do
	local remote = Instance.new(if name == "TutorialAction" then "RemoteFunction" else "RemoteEvent")
	remote.Name = name
	remote.Parent = folder
	remote.FireServer = function(_, payload)
		table.insert(sent, { name, payload })
	end
end
assert(Remotes.Get("SaveSettings"), "remotes ready")
local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local SettingsController = require(Client.Controllers.SettingsController)
local player = Players.LocalPlayer
SettingsController.Start()
SettingsController.Toggle()

local gui = player.PlayerGui:FindFirstChild("FlintbornSettings")
assert(gui and gui.Enabled, "window opens")
local window = gui.Window
local function find(root, name)
	for _, d in root:GetDescendants() do
		if d.Name == name then
			return d
		end
	end
end
local function press(object)
	object.Press.Activated:Fire()
end
local function check(cond, msg)
	print((cond and "  ok " or "  FAIL ") .. msg)
	if not cond then
		__failed = true
	end
end

-- Toggle Show Damage off on the Gameplay page.
press(find(window.Page_Gameplay, "Show Damage"))
check(#sent == 0, "nothing saved before APPLY")
press(window.Apply)
check(#sent == 1 and sent[1][1] == "SaveSettings", "APPLY sends one SaveSettings")
check(sent[1][2].showDamage == false, "showDamage=false sent")
local count = 0
for _ in sent[1][2] do
	count += 1
end
check(count == 1, "only the changed setting is sent")

-- Server echo arrives.
player:SetAttribute("ShowDamage", false)
press(window.Apply)
check(#sent == 1, "APPLY with nothing changed sends nothing")

-- Graphics tab: pick Low from the dropdown, then RESET the tab.
press(window.Graphics)
check(window.Page_Graphics.Visible and not window.Page_Gameplay.Visible, "Graphics tab shows its page")
local dropdown = find(window.Page_Graphics, "Dropdown")
press(dropdown)
check(dropdown.Options.Visible, "dropdown opens")
dropdown.Options.Low.Activated:Fire()
check(not dropdown.Options.Visible, "dropdown closes on choice")
press(window.Reset)
press(window.Apply)
check(#sent == 1, "RESET returned the tab to saved defaults, nothing to save")
press(dropdown)
dropdown.Options.Medium.Activated:Fire()
press(window.Apply)
check(#sent == 2 and sent[2][2].graphicsQuality == "Medium", "graphicsQuality Medium saved")

-- Close discards a draft.
press(window.Accessibility)
press(find(window.Page_Accessibility, "Reduced motion"))
window.Close.Activated:Fire()
check(not gui.Enabled, "close hides the window")
SettingsController.Toggle()
press(window.Apply)
check(#sent == 2, "a closed draft is discarded")

-- Controls: RESET on the Controls tab clears key overrides.
press(window.Controls)
press(window.Reset)
press(window.Apply)
check(#sent == 2, "resetting default keys changes nothing")

print(__failed and "FLOW FAILED" or "FLOW OK")
__dump(gui, 1672, 941)
if __failed then
	error("settings flow failed")
end
