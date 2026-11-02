-- Drives the in-world HUD through HudController headlessly with real events: the
-- run starts (SessionState), Humanoid health and the Stamina/Food attributes
-- change, progression and inventory snapshots arrive through their signals, a
-- tribe-mate joins, the backpack opens, a hotbar slot and a menu tile are
-- pressed through their buttons; the live placement follows the owner's
-- layout (ARCHITECTURE D28, D29) under stand-ins for Roblox's top-bar buttons,
-- and moves with the device safe area its probes measure. Ends
-- with a capture of the whole PlayerGui.
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
workspace:SetAttribute("FlintbornPlaceRole", "World")

local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local Controllers = Client.Controllers
local HudController = require(Controllers.HudController)
local InventoryController = require(Controllers.InventoryController)
local ProgressionController = require(Controllers.ProgressionController)
local HudMode = require(Client.Hud.HudMode)

local function check(cond, msg)
	print((cond and "  ok " or "  FAIL ") .. msg)
	if not cond then
		__failed = true
	end
end

-- Record what the HUD asks other controllers to do instead of running them.
local calls = {}
InventoryController.ActivateHotbar = function(index)
	table.insert(calls, "ActivateHotbar " .. index)
end
InventoryController.ToggleBackpack = function()
	table.insert(calls, "ToggleBackpack")
end
local CraftingController = require(Controllers.CraftingController)
CraftingController.Toggle = function()
	table.insert(calls, "Crafting.Toggle")
end

local healthChangedBy = {}
local function character(owner, health: number)
	local model = Instance.new("Model")
	model.Name = owner.Name
	local humanoid = Instance.new("Humanoid")
	-- The headless env has no HealthChanged signal; a bindable stands in.
	local healthChanged = Instance.new("BindableEvent")
	humanoid.HealthChanged = healthChanged.Event
	healthChangedBy[humanoid] = healthChanged
	humanoid.MaxHealth = 100
	humanoid.Health = health
	humanoid.Parent = model
	model.Parent = workspace
	owner.Character = model
	return humanoid
end

local player = Players.LocalPlayer
-- The headless env has no CharacterRemoving signal; a bindable stands in.
player.CharacterRemoving = Instance.new("BindableEvent").Event
player:SetAttribute("TribeId", "t1")
local humanoid = character(player, 100)
-- Roblox's top-bar buttons (stand-ins; GuiService.TopbarInset follows them).
local chromeGui = Instance.new("ScreenGui")
chromeGui.Name = "RobloxChrome"
chromeGui.DisplayOrder = 100
chromeGui.Parent = player.PlayerGui
local chrome = __robloxChrome(chromeGui, 1672, 941)
HudController.Start()
local gui = player.PlayerGui:FindFirstChild("FlintbornHud")
local hud = HudController.Widgets()
check(gui ~= nil and hud ~= nil, "the HUD builds in the world")
check(gui and gui.DisplayOrder == 1 and gui.IgnoreGuiInset == true and gui.ResetOnSpawn == false, "gui setup")
check(gui and gui.Enabled == false and not HudMode.IsVisible(), "hidden outside a run")

player:SetAttribute("SessionState", "ActiveRun")
check(gui.Enabled and HudMode.IsVisible(), "shown when the run starts")

-- Vitals from the Humanoid and the survival attributes.
humanoid.Health = 40
healthChangedBy[humanoid]:Fire(40)
check(hud.vitals.rows.health.bar.label.Text == "40/100", "health plaque reads 40/100")
check(math.abs(hud.vitals.rows.health.bar.fraction - 0.4) < 1e-6, "health bar at the real fraction")
player:SetAttribute("Stamina", 0.3)
check(hud.vitals.rows.stamina.bar.label.Text == "30/100", "stamina from its attribute")
player:SetAttribute("Food", 0.1)
check(hud.vitals.rows.food.bar.label.Text == "10/100", "food from its attribute")
check(hud.vitals.rows.food.mark.root.Visible, "low food shows the warning mark")
player:SetAttribute("FoodHealing", 6)
player:SetAttribute("MedicineLockUntil", workspace:GetServerTimeNow() + 20)

-- Progression snapshots.
ProgressionController.Changed:Fire({ level = 12, xp = 450, xpToNext = 750 })
check(hud.bottom.levelText.root.Text == "LV. 12", "level from ProgressionChanged")
check(hud.bottom.xpText.root.Text == "450/750 XP", "XP text from ProgressionChanged")
check(math.abs(hud.bottom.xpBar.fraction - 0.6) < 1e-6, "XP bar at 0.6")

-- Inventory snapshots fill the hotbar and move the selection to the equipped slot.
InventoryController.Changed:Fire({
	slots = {
		{ area = "hotbar", index = 1, catalogId = "StoneAxe", quantity = 1, permanent = true },
		{ area = "hotbar", index = 2, catalogId = "StoneSpear", quantity = 1 },
		{ area = "hotbar", index = 4, catalogId = "Redberry", quantity = 7 },
		{ area = "backpack", index = 1, catalogId = "Wood", quantity = 30 },
	},
	equipped = 2,
})
local slots = hud.bottom.slots
check(slots[1].item and slots[1].item.itemId == "StoneAxe" and slots[1].item.permanent, "slot 1 from the snapshot")
check(slots[4].item and slots[4].item.quantity == 7 and slots[3].item == nil, "slot 4 stack, slot 3 empty")
check(HudController.Selected == 2 and slots[2].root:GetAttribute("KitState") == "selected", "equipped slot selected")

-- Opening the backpack leaves the hotbar where it is.
InventoryController.BackpackToggled:Fire(true)
check(hud.bottom.hotbar.Visible, "the hotbar stays visible with the backpack open")

-- A press on a slot selects and uses it.
slots[4].control:Activate()
check(HudController.Selected == 4, "a press selects slot 4")
check(table.find(calls, "ActivateHotbar 4") ~= nil, "and uses it like its key")
check(slots[4].root:GetAttribute("KitState") == "selected", "slot 4 draws selected")

-- Menu tiles open their panels.
hud.tiles[1].control:Activate()
hud.tiles[2].control:Activate()
check(table.find(calls, "ToggleBackpack") ~= nil, "the Backpack tile opens the backpack")
check(table.find(calls, "Crafting.Toggle") ~= nil, "the Craft tile opens crafting")

-- A tribe-mate joins; the slow refresh lists them with their health.
-- The camera looks north-east (the env's camera has no CFrame of its own).
workspace.CurrentCamera.CFrame = { LookVector = Vector3.new(0.7, 0, -0.7), Position = Vector3.new(0, 10, 0) }
local mate = Instance.new("Player")
mate.Name = "ForestRanger"
mate.DisplayName = "ForestRanger"
mate.UserId = 2
mate:SetAttribute("TribeId", "t1")
mate.Parent = Players
character(mate, 70)
RunService.RenderStepped:Fire(1)
check(hud.party.root.Visible and hud.party.shown == 1, "the tribe frame lists one tribe-mate")
check(math.abs(hud.party.rows[1].bar.fraction - 0.7) < 1e-6, "with their health")
check(#hud.vitals.chips == 3, "medicine, food healing and hunger plaques")
check(hud.objective.titleText ~= nil, "the objective refreshed")

-- The live placement (HudController's applyTop): the compass in the top bar's
-- row, the right-hand column in the top-right corner, the tiles at the left
-- edge; banners in the shared top column start under the compass waypoints.
do
	local root = gui:FindFirstChild("Root")
	local k = root:FindFirstChildWhichIsA("UIScale").Scale
	__checkWorldHud({ scene = "world_hud_flow", hud = hud, root = root, W = 1672, H = 941, k = k, chrome = chrome })
	local compass = __rect(hud.compass.root, root, 1672, 941, k)
	local stack = require(Client.Ui.Theme).TopStack()
	check(
		stack.Position.Y.Offset >= compass[2] + (hud.compass.cfg.waypoints.y + hud.compass.cfg.waypoints.size) * k,
		("banners start under the compass waypoints (y %d)"):format(stack.Position.Y.Offset)
	)
end

-- The device safe area (ARCHITECTURE D29) as Kit.Scale's probe guis measure
-- it: with 47 px side insets (a notched phone's, here on the desktop-size
-- screen) the live placement moves the regions that reach the middle band
-- inside them, while the corner regions keep the 24 px margin.
do
	local Kit = require(Client.Hud.Kit)
	local full = player.PlayerGui:FindFirstChild("FlintbornScreenProbe")
	local safe = player.PlayerGui:FindFirstChild("FlintbornSafeAreaProbe")
	check(
		full ~= nil and safe ~= nil and full.ScreenInsets == Enum.ScreenInsets.None,
		"the safe-area probes are in the PlayerGui"
	)
	check(
		gui.ScreenInsets == Enum.ScreenInsets.None and gui.ClipToDeviceSafeArea == false,
		"the HUD draws on the whole screen (ScreenInsets None, not clipped to the safe area)"
	)
	full.AbsolutePosition = Vector2.new(0, -58)
	full.AbsoluteSize = Vector2.new(1672, 941)
	safe.AbsolutePosition = Vector2.new(47, -58)
	safe.AbsoluteSize = Vector2.new(1672 - 94, 941)
	local insets = Kit.Scale.SafeInsets()
	check(
		insets.left == 47 and insets.right == 47 and insets.top == 0 and insets.bottom == 0,
		("the probes measure the safe area's insets (left %d, top %d, right %d, bottom %d)"):format(
			insets.left,
			insets.top,
			insets.right,
			insets.bottom
		)
	)
	local root = gui:FindFirstChild("Root")
	local k = root:FindFirstChildWhichIsA("UIScale").Scale
	local notched = table.clone(chrome)
	notched.insets = insets
	__checkWorldHud({
		scene = "world_hud_flow (47 px side insets)",
		hud = hud,
		root = root,
		W = 1672,
		H = 941,
		k = k,
		chrome = notched,
	})
	-- Back to a screen without insets: the regions return to the margin.
	safe.AbsolutePosition = Vector2.new(0, -58)
	safe.AbsoluteSize = Vector2.new(1672, 941)
	__checkWorldHud({
		scene = "world_hud_flow (no insets)",
		hud = hud,
		root = root,
		W = 1672,
		H = 941,
		k = k,
		chrome = chrome,
	})
end

-- Leaving the run hides it again.
player:SetAttribute("SessionState", "Lobby")
check(not gui.Enabled and not HudMode.IsVisible(), "hidden when the run ends")
player:SetAttribute("SessionState", "ActiveRun")
-- Stand-in background for this page: art/reference/lobby_map.png is the lobby village (the
-- repo has no in-world screenshot). The world HUD never shows in the lobby: it
-- builds only in the world place (HudMode.ReplacesLegacy) and shows only during
-- a run (SessionStates.IsAtRisk).
__hudChecksDone("world_hud_flow")
__dump(player.PlayerGui, 1672, 941, { background = "art/reference/lobby_map.png" })
