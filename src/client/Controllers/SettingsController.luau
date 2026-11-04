-- Settings (GDD §25, §11, §46): the Settings window (Hud/Screens/SettingsWindow)
-- with its four tabs — volumes, camera sensitivity and inversion, damage numbers,
-- names, subtitles, graphics quality, UI scale, colour-blind palette, reduced
-- motion, keyboard controls and replaying the tutorial. The Settings key (O by
-- default) or a ⚙ button opens it. Changes collect in a draft: APPLY saves them to
-- the profile (the server echoes them back as player attributes, and every
-- controller reacts to those), RESET puts the open tab back to its defaults and
-- closing (✕, Escape, gamepad B) discards the draft. To rebind, click a key and
-- press the new one (Escape, or clicking it again, cancels); a key another
-- action uses swaps with it.
--
-- This module also applies two settings itself: UI scale on every ScreenGui that
-- does not fit itself, and the colour-blind rarity palette.

local ContextActionService = game:GetService("ContextActionService")
local GuiService = game:GetService("GuiService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local HudModel = require(ReplicatedStorage.Shared.UI.HudModel)
local Rarity = require(ReplicatedStorage.Shared.Items.Rarity)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Keybinds = require(ReplicatedStorage.Shared.Settings.Keybinds)
local SettingsRules = require(ReplicatedStorage.Shared.Settings.SettingsRules)
local HudMode = require(script.Parent.Parent.Hud.HudMode)
local Kit = require(script.Parent.Parent.Hud.Kit)
local Layout = require(script.Parent.Parent.Hud.Layout)
local SettingsWindow = require(script.Parent.Parent.Hud.Screens.SettingsWindow)
local Binds = require(script.Parent.Parent.Ui.Binds)
local Theme = require(script.Parent.Parent.Ui.Theme)

local SettingsController = {}

local player = Players.LocalPlayer
local playerGui = player:WaitForChild("PlayerGui")
local defaultRarity = table.clone(Rarity.Colors)
local panel = nil
-- The unsaved choices: every setting's value and the keyboard overrides.
local draft = nil
local keyDraft = nil
-- The action waiting for its new key, and a note shown under the keys.
local capturing = nil
local keyNote = ""

local CAPTURE_ACTION = "FlintbornKeyCapture"

local make = Theme.Make

-- Small screens (phones are about 360 px tall) shrink the whole UI so fixed-size
-- panels and their close buttons stay on-screen; the user's choice multiplies it.
SettingsController.DESIGN_HEIGHT = 600

local function viewportFactor(): number
	local camera = workspace.CurrentCamera
	if camera == nil or camera.ViewportSize.Y <= 1 then
		return 1
	end
	return math.min(1, camera.ViewportSize.Y / SettingsController.DESIGN_HEIGHT)
end

-- Roblox's own touch controls (thumbstick, jump and action buttons) live in
-- PlayerGui too; they size themselves for the screen and must not shrink. The
-- HUDs and parchment menus fit themselves to the screen and apply UiScale on
-- their own (menus mark their ScreenGui "FitsItself").
local UNSCALED = { TouchGui = true, FlintbornHud = true, FlintbornHudOverlay = true, FlintbornLobbyHud = true }

local function applyScale()
	local scale = (player:GetAttribute("UiScale") or 1) * viewportFactor()
	for _, gui in playerGui:GetChildren() do
		if gui:IsA("ScreenGui") and not UNSCALED[gui.Name] and not gui:GetAttribute("FitsItself") then
			local uiScale = gui:FindFirstChild("FlintbornScale") or make("UIScale", { Name = "FlintbornScale" }, gui)
			uiScale.Scale = scale
		end
	end
end

local function applyPalette()
	local palette = if player:GetAttribute("ColourBlind") then Theme.ColourBlindRarity else defaultRarity
	for name, color in palette do
		Rarity.Colors[name] = color
	end
end

-- Every setting as saved (the server's attributes), defaults where unset.
local function saved(): { [string]: any }
	local choices = {}
	for _, setting in SettingsRules.Settings do
		choices[setting.key] = player:GetAttribute(setting.attribute)
	end
	return SettingsRules.Resolve(choices)
end

local function sameKeys(a, b): boolean
	for id, key in a do
		if b[id] ~= key then
			return false
		end
	end
	for id, key in b do
		if a[id] ~= key then
			return false
		end
	end
	return true
end

-- The settings in the draft that differ from what is saved.
local function changes(): { [string]: any }
	local current = saved()
	local diff = {}
	for key, value in draft do
		if current[key] ~= value then
			diff[key] = value
		end
	end
	return diff
end

local function isDirty(): boolean
	return next(changes()) ~= nil or not sameKeys(Keybinds.Sanitize(keyDraft), Binds.Overrides())
end

local function canRebind(): boolean
	return UserInputService.KeyboardEnabled
end

local function showKeys()
	panel:SetKeys(Keybinds.Resolve(keyDraft), capturing, keyNote, canRebind())
end

local function refresh()
	panel:SetDirty(isDirty())
	showKeys()
end

local function stopCapture()
	if capturing then
		capturing = nil
		ContextActionService:UnbindAction(CAPTURE_ACTION)
	end
end

-- Waits for the next key for action `id`. Bound above every game action and sunk,
-- so pressing (say) Tab here rebinds instead of opening the backpack.
local function startCapture(id: string)
	stopCapture()
	capturing = id
	keyNote = ""
	ContextActionService:BindActionAtPriority(CAPTURE_ACTION, function(_, state, input)
		if state ~= Enum.UserInputState.Begin then
			return Enum.ContextActionResult.Sink
		end
		local key = input.KeyCode.Name
		if input.KeyCode == Enum.KeyCode.Escape then
			keyNote = ""
		elseif Keybinds.IsAllowed(key) then
			local overrides = Keybinds.Assign(keyDraft, id, key)
			if overrides then
				keyDraft = overrides
				keyNote = ("%s is now %s"):format(Keybinds.Get(id).label, SettingsWindow.KeyText(key))
			end
		else
			keyNote = ("%s is kept for movement, chat or menus."):format(SettingsWindow.KeyText(key))
		end
		stopCapture()
		refresh()
		return Enum.ContextActionResult.Sink
	end, false, Enum.ContextActionPriority.High.Value + 100, Enum.UserInputType.Keyboard)
	refresh()
end

-- Loads the saved choices into a fresh draft.
local function loadDraft()
	draft = saved()
	keyDraft = Binds.Overrides()
	keyNote = ""
	panel:SetValues(draft)
	refresh()
end

-- Closes the window; onClosed below drops the draft's key capture. Kit.Modal
-- gives back the gamepad selection the window took.
local function close()
	panel.screen:Close()
end

local function apply()
	stopCapture()
	local diff = changes()
	if next(diff) ~= nil then
		Remotes.Get("SaveSettings"):FireServer(diff)
	end
	local keys = Keybinds.Sanitize(keyDraft)
	if not sameKeys(keys, Binds.Overrides()) then
		Remotes.Get("SaveKeybinds"):FireServer(keys)
	end
	keyNote = "Saved."
	-- The saved state arrives as attributes in a moment; until then the draft is it.
	panel:SetDirty(false)
	showKeys()
end

-- RESET puts the open tab's settings and keys back to their defaults (in the
-- draft; APPLY saves them).
local function reset(tab: string)
	stopCapture()
	for _, key in SettingsWindow.TAB_SETTINGS[tab] or {} do
		draft[key] = (SettingsRules.Get(key) :: any).default
	end
	local keys = SettingsWindow.TAB_KEYS[tab]
	if keys == "all" then
		keyDraft = {}
	elseif keys then
		for _, id in keys do
			keyDraft = Keybinds.Assign(keyDraft, id, Keybinds.Get(id).default) or keyDraft
		end
	end
	keyNote = ""
	panel:SetValues(draft)
	refresh()
end

local function build()
	panel = SettingsWindow.new(playerGui, {
		onClosed = stopCapture,
		onApply = apply,
		onReset = reset,
		onChange = function(key: string, value)
			draft[key] = value
			refresh()
		end,
		onRebind = function(id: string)
			-- Clicking the waiting key again cancels, as Escape does.
			if capturing == id then
				stopCapture()
				refresh()
			elseif canRebind() then
				startCapture(id)
			end
		end,
		onReplayTutorial = function()
			close()
			task.spawn(function()
				pcall(function()
					Remotes.Get("TutorialAction"):InvokeServer("Replay")
				end)
			end)
		end,
		onTab = function()
			stopCapture()
			if draft then
				refresh()
			end
		end,
	})
	panel.screen:Watch()

	-- A small always-visible ⚙ button (the kit's settings button), so touch
	-- players can reach settings in the world too. The lobby HUD has its own gear
	-- button, so this one stays hidden there. It sits in the bottom-left corner
	-- of the HUD grid (D30), the same place, size and spec (HudLayout "gear")
	-- as the lobby's, on a root scaled like the HUD that covers the whole
	-- screen (HudModel.GearCorner).
	local gui = make("ScreenGui", {
		Name = "FlintbornSettingsButton",
		ResetOnSpawn = false,
		DisplayOrder = Kit.Tokens.Order("topStack"),
		ZIndexBehavior = Enum.ZIndexBehavior.Sibling,
		IgnoreGuiInset = true,
	}, playerGui)
	Kit.Scale.FullScreen(gui)
	-- Kit.Scale.Hud applies the UI Scale setting itself.
	gui:SetAttribute("FitsItself", true)
	local root = make("Frame", {
		Name = "Root",
		BackgroundTransparency = 1,
		Size = UDim2.fromScale(1, 1),
	}, gui)
	Kit.Scale.Hud(gui, root)
	local size = SettingsController.GearSize()
	local margin = SettingsController.MARGIN
	local gear = Kit.IconButton.new(root, {
		name = "Open",
		-- The menu tiles' frame (9-sliced, so square at any size) with the gear.
		variant = "tile",
		icon = "ink:gears",
		size = { size[1], size[2] },
		position = UDim2.new(0, margin, 1, -margin),
		anchorPoint = Vector2.new(0, 1),
		visible = not HudMode.ReplacesLobby(),
		onPress = function()
			SettingsController.Toggle()
		end,
	})
	local uiScale = root:FindFirstChildWhichIsA("UIScale") :: UIScale
	local function placeGear()
		gear.root.Position = SettingsController.GearPosition(Kit.Scale.HudScreen(gui, uiScale.Scale))
	end
	uiScale:GetPropertyChangedSignal("Scale"):Connect(placeGear)
	gui:GetPropertyChangedSignal("AbsoluteSize"):Connect(placeGear)
	UserInputService:GetPropertyChangedSignal("TouchEnabled"):Connect(placeGear)
	Kit.Scale.OnFormFactorChanged(placeGear)
	Kit.Scale.OnSafeInsetsChanged(placeGear)
	placeGear()
	SettingsController.gear = gear
	-- Gamepad: the gear sits left of the world hotbar's first slot and under
	-- the menu tiles' bottom-left tile (the HUD's regions are mounted again
	-- when the form factor changes).
	if not HudMode.ReplacesLobby() then
		local HudController = require(script.Parent.HudController) :: any
		local function link()
			SettingsController.LinkGear(gear.control.hit, HudController.Widgets())
		end
		HudController.Remounted:Connect(link)
		link()
	end
end

-- The world ⚙ button in HUD design px (HudLayout's 1672 × 941), in the
-- grid's bottom-left corner (D30; HudModel.GearCorner): the grid's margin from
-- the left and bottom edges, on touch screens too unless Roblox's thumbstick
-- ring reaches the corner (then above the ring). Its size and spec are
-- HudLayout's "gear", which the lobby's ⚙ shares. MARGIN is where it waits
-- when the layout is missing.
SettingsController.MARGIN = 24

-- The ⚙'s size in design px (HudLayout "gear").
function SettingsController.GearSize(): { number }
	local gear = Layout.Gear()
	return if gear then gear.size else { 52, 52 }
end

-- The world ⚙'s position on its HUD root (anchored at its bottom-left corner)
-- for a screen (Kit.Scale.HudScreen: {width, height, scale, touch, insets}).
function SettingsController.GearPosition(screen): UDim2
	local grid, gear = Layout.Grid(), Layout.Gear()
	if grid == nil or gear == nil then
		return UDim2.new(0, SettingsController.MARGIN, 1, -SettingsController.MARGIN)
	end
	local left, bottom = HudModel.GearCorner(grid, gear, screen)
	return UDim2.new(0, left, 1, -bottom)
end

-- Gamepad neighbours of the world ⚙ (`hit`) in the mounted HUD `widgets`
-- (HudController.Mount): right to the hotbar's first slot, up to the menu
-- tiles' bottom-left tile, and back.
function SettingsController.LinkGear(hit: GuiButton, widgets)
	local slots = widgets and widgets.bottom and widgets.bottom.slots
	local first = slots and slots[1]
	if first then
		first.control.hit.NextSelectionLeft = hit
		hit.NextSelectionRight = first.control.hit
	end
	local tiles = widgets and widgets.tiles
	if tiles and #tiles > 0 then
		local columns = widgets.tileColumns or 2
		local corner = tiles[(math.ceil(#tiles / columns) - 1) * columns + 1]
		if corner then
			corner.control.hit.NextSelectionDown = hit
			hit.NextSelectionUp = corner.control.hit
		end
	end
end

-- The window (Hud/Screens/SettingsWindow), for scenes and verifiers.
function SettingsController.View()
	return panel
end

-- Opens or closes the window (keys, the ⚙ buttons).
function SettingsController.Toggle()
	if panel.screen:IsOpen() then
		close()
		return
	end
	loadDraft()
	panel:SelectTab(panel.tab or "Gameplay")
	-- A gamepad starts on the open tab; Escape and B close (Kit.Modal), an open
	-- dropdown list first.
	panel.screen:SetDefaultSelection(panel.tabs[panel.tab].control.hit)
	panel.screen:Open(GuiService.SelectedObject ~= nil or Kit.Input.IsGamepad())
end

function SettingsController.Start()
	build()
	applyScale()
	applyPalette()
	playerGui.ChildAdded:Connect(function(child)
		if child:IsA("ScreenGui") then
			task.defer(applyScale)
		end
	end)
	player:GetAttributeChangedSignal("UiScale"):Connect(applyScale)
	local viewportConnection = nil
	local function watchCamera()
		if viewportConnection then
			viewportConnection:Disconnect()
			viewportConnection = nil
		end
		local camera = workspace.CurrentCamera
		if camera then
			viewportConnection = camera:GetPropertyChangedSignal("ViewportSize"):Connect(applyScale)
		end
		applyScale()
	end
	workspace:GetPropertyChangedSignal("CurrentCamera"):Connect(watchCamera)
	watchCamera()
	player:GetAttributeChangedSignal("ColourBlind"):Connect(applyPalette)
	-- Saved changes arriving while the window is open (the server's echo after
	-- APPLY): shown when nothing is left unsaved, so edits in progress stay.
	local function resync()
		if panel.screen:IsOpen() and draft and not isDirty() then
			local note = keyNote
			loadDraft()
			keyNote = note
			showKeys()
		elseif panel.screen:IsOpen() and draft then
			refresh()
		end
	end
	local watched = {}
	for _, setting in SettingsRules.Settings do
		watched[setting.attribute] = true
	end
	player.AttributeChanged:Connect(function(name: string)
		if watched[name] then
			resync()
		end
	end)
	Binds.Changed:Connect(resync)
	Binds.Bind("Settings", function(_, state)
		if state == Enum.UserInputState.Begin then
			SettingsController.Toggle()
		end
		return Enum.ContextActionResult.Pass
	end)
end

return SettingsController
