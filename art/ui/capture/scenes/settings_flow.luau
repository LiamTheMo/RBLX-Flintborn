-- Drives SettingsController and its window (Hud/Screens/SettingsWindow)
-- headlessly and checks what reaches the server: the Settings key opens it;
-- values change in a draft (a setting shown on two pages stays in step); APPLY
-- sends only what changed; a rebind swaps keys, Escape cancels a capture and
-- reserved keys are refused; RESET puts the open tab back to its defaults;
-- Escape / B close an open dropdown before the window; closing discards the
-- draft; Replay Tutorial asks the server; no keyboard disables the caps; the
-- gamepad order runs tabs → page → RESET / APPLY. Fails loudly on any broken
-- rule, then dumps the window after a key swap and after closing the list.

local ContextActionService = game:GetService("ContextActionService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)

local W, H = 1672, 941
local BACKGROUND = { background = "art/reference/ui/lobby/01_hud.png" }

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
	remote.InvokeServer = function(_, payload)
		table.insert(sent, { name, payload })
		return true
	end
end
assert(Remotes.Get("SaveSettings"), "remotes ready")

-- The env's enum items are plain names; priorities need their numbers.
local envEnum = Enum
Enum = setmetatable({
	ContextActionPriority = { Low = { Value = 1000 }, Medium = { Value = 2000 }, High = { Value = 3000 } },
}, { __index = envEnum })

-- ContextActionService keeps the handlers so the scene can press keys.
local actions = {}
ContextActionService.BindAction = function(_, name, handler)
	actions[name] = handler
end
ContextActionService.BindActionAtPriority = function(_, name, handler)
	actions[name] = handler
end
ContextActionService.UnbindAction = function(_, name)
	actions[name] = nil
end
local BEGIN = Enum.UserInputState.Begin
local function key(name)
	return { KeyCode = { Name = name }, UserInputType = Enum.UserInputType.Keyboard }
end
local ESCAPE = { KeyCode = Enum.KeyCode.Escape, UserInputType = Enum.UserInputType.Keyboard }

local failures = 0
local function check(ok, message)
	print((if ok then "  ok " else "  FAIL ") .. message)
	if not ok then
		failures += 1
	end
end
local function count(t)
	local n = 0
	for _ in t do
		n += 1
	end
	return n
end

local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local SettingsController = require(Client.Controllers.SettingsController)
local player = Players.LocalPlayer
SettingsController.Start()
local view = SettingsController.View()
local gui = view.screen.gui
local function press(component)
	component.control:Activate()
end
local function state(component)
	return component.root:GetAttribute("KitState")
end

-- The Settings key (O) opens the window on Gameplay with nothing to save.
check(actions.FlintbornSettings ~= nil, "the Settings key is bound")
actions.FlintbornSettings("FlintbornSettings", BEGIN, key("O"))
check(view.screen:IsOpen() and gui.Enabled, "the Settings key opens the window")
check(view.tab == "Gameplay" and view.pages.Gameplay.Visible, "opens on Gameplay")
check(state(view.apply) == "disabled", "APPLY is dim with nothing to save")

-- Gameplay: a checkbox and its one slider; the volumes are on Audio only.
check(view.fields["Gameplay.musicVolume"] == nil, "Gameplay has no Music slider (Audio has it)")
check(view.fields["Gameplay.effectsVolume"] == nil, "Gameplay has no Effects slider")
press(view.fields["Gameplay.showDamage"])
view.fields["Gameplay.cameraSensitivity"]:_change(80)
view.fields["Audio.musicVolume"]:_change(40)
check(#sent == 0, "nothing is sent before APPLY")
check(state(view.apply) ~= "disabled", "APPLY lights up with a change")
check(view.fields["Gameplay.cameraSensitivity"].valueLabel.Text == "1.6", "Camera Sensitivity shows the multiplier")
press(view.apply)
check(#sent == 1 and sent[1][1] == "SaveSettings", "APPLY sends one SaveSettings")
local saved = sent[1][2]
check(
	count(saved) == 3 and saved.showDamage == false and saved.cameraSensitivity == 80 and saved.musicVolume == 40,
	"only the three changes are sent"
)
-- The server's echo arrives as attributes.
player:SetAttribute("ShowDamage", false)
player:SetAttribute("CameraSensitivity", 80)
player:SetAttribute("MusicVolume", 40)
press(view.apply)
check(#sent == 1, "APPLY with nothing changed sends nothing")
check(state(view.apply) == "disabled", "APPLY dims once saved")

-- Rebinding on Gameplay: Interact takes B, Backpack gets E (swap).
local interact = view.keycaps.Interact[1]
press(interact)
check(actions.FlintbornKeyCapture ~= nil, "pressing a key cap waits for a key")
check(state(interact) == "capturing", "the cap shows it is waiting")
check(view.notes.Gameplay.root.Text:find("Escape") ~= nil, "the note says how to cancel")
actions.FlintbornKeyCapture("FlintbornKeyCapture", BEGIN, key("B"))
check(actions.FlintbornKeyCapture == nil, "the capture ends after a key")
check(view.keycaps.Interact[1].label.Text == "B", "Interact shows B")
check(view.keycaps.Backpack[1].label.Text == "E", "Backpack swapped to E")
check(view.keycaps.Interact[2].label.Text == "B", "the Controls list shows the swap too")
-- Escape cancels a capture; a reserved key is refused.
press(view.keycaps.Map[1])
actions.FlintbornKeyCapture("FlintbornKeyCapture", BEGIN, ESCAPE)
check(view.keycaps.Map[1].label.Text == "M" and state(view.keycaps.Map[1]) ~= "capturing", "Escape cancels")
view.keycaps.Sprint[1].control:Activate()
actions.FlintbornKeyCapture("FlintbornKeyCapture", BEGIN, key("W"))
check(view.keycaps.Sprint[1].label.Text == "Left Shift", "W stays with movement")
check(view.notes.Gameplay.root.Text:find("kept for movement") ~= nil, "the note says why")
-- Pressing the waiting cap again cancels too.
press(view.keycaps.Map[1])
press(view.keycaps.Map[1])
check(actions.FlintbornKeyCapture == nil, "pressing the waiting cap again cancels")
interact.root:SetAttribute("DebugState", nil)
__dump(Players.LocalPlayer.PlayerGui, W, H, BACKGROUND)
press(view.apply)
check(#sent == 2 and sent[2][1] == "SaveKeybinds", "APPLY sends the keys")
check(sent[2][2].Interact == "B" and sent[2][2].Backpack == "E" and count(sent[2][2]) == 2, "only the swapped pair")

-- RESET on Controls returns every key to its default (nothing left to save).
view:SelectTab("Controls")
press(view.reset)
check(view.keycaps.Interact[2].label.Text == "E", "RESET on Controls restores Interact E")
check(state(view.apply) == "disabled", "the reset keys match what is saved")

-- RESET on Gameplay: its settings back to their defaults, in the draft (the
-- Audio page's Music volume is not Gameplay's to reset).
view:SelectTab("Gameplay")
press(view.reset)
check(view.fields["Gameplay.cameraSensitivity"].value == 50, "Camera Sensitivity back to 50")
check(view.fields["Gameplay.showDamage"].checked == true, "Show Damage back on")
check(view.fields["Audio.musicVolume"].value == 40, "Music keeps its saved 40")
press(view.apply)
local reset = sent[3] and sent[3][2] or {}
check(
	sent[3]
		and sent[3][1] == "SaveSettings"
		and reset.cameraSensitivity == 50
		and reset.showDamage == true
		and count(reset) == 2,
	"APPLY after RESET saves the defaults that differ"
)
player:SetAttribute("ShowDamage", true)
player:SetAttribute("CameraSensitivity", 50)
player:SetAttribute("MusicVolume", 75)

-- Graphics: the dropdown; Escape / B close the list before the window.
press(view.tabs.Graphics)
check(view.tab == "Graphics" and view.pages.Graphics.Visible and not view.pages.Gameplay.Visible, "Graphics tab")
local dropdown = view.fields["Graphics.graphicsQuality"]
press(dropdown)
check(dropdown:IsOpen(), "the quality list opens")
local Kit = require(Client.Hud.Kit)
Kit.Modal.Back()
check(not dropdown:IsOpen() and view.screen:IsOpen(), "Escape / B close the list first")
press(dropdown)
press(dropdown.rows.Low)
check(not dropdown:IsOpen() and dropdown.value == "Low", "choosing closes the list")
press(view.fields["Graphics.reducedMotion"])
check(state(view.apply) ~= "disabled", "Graphics changes are pending")
__dump(Players.LocalPlayer.PlayerGui, W, H, BACKGROUND)

-- Closing discards the draft; reopening shows what is saved.
press(view.close)
check(not view.screen:IsOpen(), "✕ closes the window")
SettingsController.Toggle()
check(view.screen:IsOpen() and view.tab == "Graphics", "reopens on the last tab")
check(dropdown.value == "High" and view.fields["Graphics.reducedMotion"].checked == false, "the draft was discarded")
press(view.apply)
check(#sent == 3, "nothing to save after a discarded draft")
Kit.Modal.Back()
check(not view.screen:IsOpen(), "Escape / B close the window")

-- Gamepad order on Controls: tab → first key → … → RESET → APPLY.
SettingsController.Toggle()
view:SelectTab("Controls")
local tabHit = view.tabs.Controls.control.hit
local first = view.controls.Controls[1]
check(tabHit.NextSelectionRight == first, "right from the tab enters the page")
check(first.NextSelectionLeft == tabHit, "left from the page returns to the tab")
check(view.reset.control.hit.NextSelectionRight == view.apply.control.hit, "RESET → APPLY")
check(view.tabs.Audio.control.hit.NextSelectionDown == view.tabs.Graphics.control.hit, "tabs run down the left")
check(
	#view.controls.Controls == #require(ReplicatedStorage.Shared.Settings.Keybinds).Actions + 1,
	"every action is reachable"
)

-- Replay Tutorial closes the window and asks the server.
press(view.fields["Controls.replayTutorial"])
check(not view.screen:IsOpen(), "Replay Tutorial closes the window")
local last = sent[#sent]
check(last and last[1] == "TutorialAction" and last[2] == "Replay", "TutorialAction Replay is asked")

-- Without a keyboard the caps are dim and the note says why.
UserInputService.KeyboardEnabled = false
SettingsController.Toggle()
check(state(view.keycaps.Interact[2]) == "disabled", "no keyboard: caps disabled")
check(view.notes.Controls.root.Text:find("Connect a keyboard") ~= nil, "no keyboard: the note says why")
UserInputService.KeyboardEnabled = true

-- The world ⚙ sits in the bottom-left corner on a HUD-scaled root that covers
-- the whole screen (ARCHITECTURE D29); on touch screens it goes left of
-- Roblox's thumbstick ring, centred on its height, or above the ring where the
-- screen has no room beside it (no side inset).
local gear = SettingsController.gear
local gearRoot = gear.root.Parent
local gearGui = gearRoot.Parent
check(
	gear.root.Position.X.Scale == 0
		and gear.root.Position.X.Offset == 24
		and gear.root.Position.Y.Scale == 1
		and gear.root.Position.Y.Offset == -24
		and gear.root.AnchorPoint.X == 0
		and gear.root.AnchorPoint.Y == 1,
	"desktop: the world gear is in the bottom-left corner, 24 px from both edges"
)
check(gearRoot:FindFirstChildWhichIsA("UIScale") ~= nil, "the gear scales with the HUD")
check(
	gearGui.ScreenInsets == Enum.ScreenInsets.None and gearGui.IgnoreGuiInset == true,
	"its gui covers the whole screen (ScreenInsets None)"
)
do
	local HudModel = require(game:GetService("ReplicatedStorage").Shared.UI.HudModel)
	local g = SettingsController.GEAR
	for _, screen in
		{
			{ 844, 390, 0.5, __NOTCHED_PHONE, "beside" },
			{ 667, 375, 0.5, __NO_INSETS, "above" },
			{ 2000, 924, 0.884, __NO_INSETS, "above" },
		}
	do
		local w, h, k, insets, want = screen[1], screen[2], screen[3], screen[4], screen[5]
		local at = SettingsController.GearPosition(__hudScreen(w, h, k, true, insets))
		local _, _, where = HudModel.GearCorner(__hudScreen(w, h, k, true, insets), g)
		local stick = HudModel.Thumbstick(w, h, insets)
		local left, foot = at.X.Offset * k, h + at.Y.Offset * k
		local right, top = left + g.w * k, foot - g.h * k
		local half = math.max(0, g.pad - g.w * k) / 2
		local ok
		if want == "beside" then
			ok = right + half + g.gap <= stick.x + 0.01
				and math.abs((top + foot) / 2 - (stick.y + stick.size / 2)) <= 0.5
				and left >= 12 - 0.01
		else
			ok = foot + g.gap <= stick.y + 0.01 and left - half >= -0.01
		end
		check(
			ok and where == want,
			("touch %dx%d (insets %d / %d): the world gear (x %d..%d, y %d..%d) sits %s the thumbstick ring (x %d, y %d)"):format(
				w,
				h,
				insets.left,
				insets.right,
				left,
				right,
				top,
				foot,
				if want == "beside" then "left of" else "above",
				stick.x,
				stick.y
			)
		)
	end
	local desk = SettingsController.GearPosition(__hudScreen(1672, 941, 1, false))
	check(desk.X.Offset == 24 and desk.Y.Offset == -24, "desktop: the gear 24 px from the left and the bottom")
end
-- Gamepad: the world gear sits left of the hotbar's first slot and under the
-- tiles' bottom-left tile (Map in the 2 × 3 grid).
do
	local HudController = require(Client.Controllers.HudController)
	local holder = Instance.new("Frame")
	local mounted = HudController.Mount(holder, require(Client.Hud.Layout).Get(), function() end)
	local hit = gear.control.hit
	SettingsController.LinkGear(hit, mounted)
	local first = mounted.bottom.slots[1].control.hit
	local corner = mounted.tiles[5].control.hit
	check(hit.NextSelectionRight == first and first.NextSelectionLeft == hit, "gamepad: gear <-> the first hotbar slot")
	check(hit.NextSelectionUp == corner and corner.NextSelectionDown == hit, "gamepad: the Map tile v the gear ^ it")
	holder:Destroy()
end

-- Leak check counts: the PlayerGui's instances, and the live connections on
-- every instance still in the game (a destroyed one drops out with its
-- connections, as in Roblox) plus those on the shared Core.Signal objects.
local leakCounts
do
	local SignalMeta = getmetatable(Instance.new("Frame"):GetPropertyChangedSignal("Name"))
	local CoreSignal = require(game:GetService("ReplicatedStorage").Shared.Core.Signal)
	local coreLive = setmetatable({}, { __mode = "k" })
	local connect = CoreSignal.Connect
	CoreSignal.Connect = function(signal, fn)
		local connection = connect(signal, fn)
		coreLive[connection] = true
		return connection
	end
	local ROOTS = {
		"Players",
		"UserInputService",
		"GuiService",
		"RunService",
		"Lighting",
		"ReplicatedStorage",
		"StarterPlayer",
		"SoundService",
		"ContextActionService",
		"SocialService",
		"TweenService",
	}
	function leakCounts(): (number, number)
		local count = 0
		local seen = {}
		local function signals(map)
			for _, value in map or {} do
				if type(value) == "table" and getmetatable(value) == SignalMeta then
					count += #value.handlers
				end
			end
		end
		local function visit(instance)
			if instance == nil or seen[instance] then
				return
			end
			seen[instance] = true
			signals(rawget(instance, "__props"))
			signals(rawget(instance, "__changed"))
			signals(rawget(instance, "__attrChanged"))
			for _, child in rawget(instance, "__children") or {} do
				visit(child)
			end
		end
		visit(game)
		visit(workspace)
		visit(workspace.CurrentCamera)
		for _, name in ROOTS do
			visit(game:GetService(name))
		end
		local player = game:GetService("Players").LocalPlayer
		visit(player)
		for connection in coreLive do
			if connection.Connected then
				count += 1
			end
		end
		return #player.PlayerGui:GetDescendants(), count
	end
end

-- ×20 open / close: no instances and no connections left behind (Settings).
SettingsController.Toggle()
SettingsController.Toggle()
local instancesBefore, connectionsBefore = leakCounts()
for _ = 1, 20 do
	SettingsController.Toggle()
	SettingsController.Toggle()
end
local instancesAfter, connectionsAfter = leakCounts()
check(
	instancesAfter == instancesBefore,
	("open/close ×20 leaves the instances as they were (%d → %d)"):format(instancesBefore, instancesAfter)
)
check(
	connectionsAfter == connectionsBefore,
	("open/close ×20 leaves the connections as they were (%d → %d)"):format(connectionsBefore, connectionsAfter)
)

print(if failures == 0 then "FLOW OK" else ("FLOW FAILED (%d)"):format(failures))
if failures > 0 then
	error("settings flow failed")
end
