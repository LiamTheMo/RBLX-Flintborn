-- In-world HUD (GDD §11, §25.4; docs/ui/HudScreen.md), built only from the shared
-- Kit like the lobby HUD (ARCHITECTURE §4.8, D15) and placed from
-- src/shared/UI/HudLayout.json: tribe frames, compass with waypoints, the
-- vitals as the kit's stat bars, status plaques, extraction objective, world
-- event, the menu tiles, level/XP bar, the hotbar (its items; a tap uses a slot
-- like its key) and the custom interaction prompt. It only displays what the
-- server already replicated: Humanoid health, the Stamina/Food/MedicineLockUntil/
-- FoodHealing attributes, progression snapshots, TribeId attributes, and the
-- extraction and event remotes (through their controllers). World place only,
-- during a run.

local ContextActionService = game:GetService("ContextActionService")
local GuiService = game:GetService("GuiService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local ExtractionRules = require(ReplicatedStorage.Shared.Extraction.ExtractionRules)
local GameConstants = require(ReplicatedStorage.Shared.GameConstants)
local HudModel = require(ReplicatedStorage.Shared.UI.HudModel)
local PoiCatalog = require(ReplicatedStorage.Shared.World.PoiCatalog)
local SessionStates = require(ReplicatedStorage.Shared.Admission.SessionStates)
local Signal = require(ReplicatedStorage.Shared.Core.Signal)
local WorldState = require(ReplicatedStorage.Shared.World.WorldState)
local EventFeedController = require(script.Parent.EventFeedController)
local ExtractionController = require(script.Parent.ExtractionController)
local InventoryController = require(script.Parent.InventoryController)
local ProgressionController = require(script.Parent.ProgressionController)
local Hud = script.Parent.Parent.Hud
local BottomBar = require(Hud.BottomBar)
local Compass = require(Hud.Compass)
local EventPanel = require(Hud.EventPanel)
local HudMode = require(Hud.HudMode)
local InteractionPrompt = require(Hud.InteractionPrompt)
local Kit = require(Hud.Kit)
local Layout = require(Hud.Layout)
local ObjectivePanel = require(Hud.ObjectivePanel)
local PartyFrames = require(Hud.PartyFrames)
local Vitals = require(Hud.Vitals)
local Binds = require(script.Parent.Parent.Ui.Binds)
local Theme = require(script.Parent.Parent.Ui.Theme)

local HudController = {}

-- Fires (index) when the selected hotbar slot changes. The selection follows the
-- equipped slot, and every key press or tap on a slot also uses it.
HudController.SelectionChanged = Signal.new()

-- The menu tiles (left, the lobby's 2 × 3 grid): {id, icon, bind action named
-- in the tooltip, controller, function}. Touch players have no keys, so every
-- panel with a key has a tile.
HudController.MENU = {
	{ "Backpack", "backpack", "Backpack", "InventoryController", "ToggleBackpack" },
	{ "Craft", "hammer", "Craft", "CraftingController", "Toggle" },
	{ "Build", "build", "Build", "BuildController", "Toggle" },
	{ "Tribe", "party", "Tribe", "TribeController", "Toggle" },
	{ "Map", "map", "Map", "MapController", "Toggle" },
	{ "Progress", "trophy", "Progression", "ProgressionController", "Toggle" },
}
HudController.Selected = 1

-- Status text ticks fast (the medicine countdown); party, objective and event
-- panels refresh a little slower.
HudController.FAST_SECONDS = 0.1
HudController.SLOW_SECONDS = 0.25
-- A portal site counts as reached inside this radius when the part has no
-- ZoneRadius attribute and the catalog has no entry.
HudController.DEFAULT_ZONE_RADIUS = 10
-- Where Theme's shared top column sits when the HUD is not pushing it down.
HudController.TOP_STACK_POSITION = UDim2.new(0.5, 0, 0, 2)
-- Design px kept between the Roblox top bar and the top regions.
HudController.TOP_GAP = 2
-- Compass waypoint icons per kind of point (events use their category's icon).
HudController.WAYPOINT_ICONS = {
	landmark = "mountain",
	camp = "campfire",
	portal = "portal",
	extract = "exit",
}

-- The right bumper steps the selection forward, wrapping. The left bumper is left to
-- InventoryController's Drop, so one press never does two things. Gamepad buttons
-- are fixed (GDD §46), so this one is not rebindable.
local HOTBAR_STEP_KEYS = { [Enum.KeyCode.ButtonR1] = 1 }

-- The keyboard keys that select each slot: the player's Hotbar1–6 binds (1–6 by
-- default, rebindable in Settings, GDD §46).
local function hotbarKeys(count: number): { [Enum.KeyCode]: number }
	local keys = {}
	for index = 1, count do
		local key = Binds.Key("Hotbar" .. index)
		if key then
			keys[key] = index
		end
	end
	return keys
end

local function hotbarLabels(count: number): { string }
	local labels = {}
	for index = 1, count do
		labels[index] = Binds.Label("Hotbar" .. index)
	end
	return labels
end

-- The status plaques for the survival state: medicine lock (hourglass), pending
-- food healing (heart) and the hunger slow (warning), each in words.
function HudController.StatusChips(medicineLockLeft: number?, foodHealing: number?, slowed: boolean?)
	local chips = {}
	if (medicineLockLeft or 0) > 0 then
		table.insert(chips, { icon = "hourglass", text = ("Medicine ready in %.1f s"):format(medicineLockLeft) })
	end
	if (foodHealing or 0) > 0 then
		table.insert(chips, { icon = "heart", text = ("Food healing +%d"):format(foodHealing) })
	end
	if slowed then
		table.insert(chips, { icon = "warning", text = "Hungry: slowed" })
	end
	return chips
end

-- The hotbar's items from an inventory snapshot ({slots, equipped}):
-- index -> {itemId, quantity, permanent}, or nil for an empty slot.
function HudController.HotbarItems(snapshot, count: number)
	local items = {}
	for _, slot in (snapshot and snapshot.slots) or {} do
		local index = slot.index
		if slot.area == "hotbar" and type(index) == "number" and index >= 1 and index <= count then
			items[index] = {
				itemId = slot.catalogId,
				quantity = slot.quantity,
				permanent = slot.permanent == true,
			}
		end
	end
	return items
end

local player = Players.LocalPlayer
local layout = nil
local gui = nil
local root = nil
local uiScale = nil
local overlay = nil
local scale = 1
local widgets = {}
local tops = {}
local humanoid = nil
local humanoidConnections = {}
local portals = {}
local waypointPositions = {}
local hotbarBound = false

local function instantMotion(): boolean
	return Kit.Motion.Reduced()
end

local function rootPart(): BasePart?
	local character = player.Character
	return character and character:FindFirstChild("HumanoidRootPart") :: BasePart?
end

local function flatDistance(a: Vector3, b: Vector3): number
	local dx, dz = a.X - b.X, a.Z - b.Z
	return math.sqrt(dx * dx + dz * dz)
end

-- Scale and top inset ----------------------------------------------------------

-- How far the top regions move down so the Roblox top bar never covers them
-- (phones), in design px, as the lobby HUD does.
function HudController.TopShift(insetDesignPx: number): number
	local top = math.huge
	for _, entry in tops do
		top = math.min(top, entry.base.Y.Offset)
	end
	if top == math.huge then
		return 0
	end
	return math.max(0, math.ceil(insetDesignPx + HudController.TOP_GAP - top))
end

local function applyTop()
	scale = uiScale.Scale
	local shift = HudController.TopShift(Kit.Scale.TopInset(gui) / math.max(scale, 0.01))
	for _, entry in tops do
		entry.object.Position = entry.base + UDim2.fromOffset(0, shift)
	end
	-- While the HUD shows, banners in the shared top column start below the
	-- compass and its waypoints; otherwise they keep their usual place.
	local stack = Theme.TopStack()
	if not gui.Enabled then
		stack.Position = HudController.TOP_STACK_POSITION
		return
	end
	local stackGui = stack:FindFirstAncestorWhichIsA("ScreenGui")
	local stackScale = stackGui and stackGui:FindFirstChild("FlintbornScale")
	local factor = if stackScale and stackScale:IsA("UIScale") and stackScale.Scale > 0 then stackScale.Scale else 1
	local compass = layout.compass
	local below = compass.pos[4] + shift + compass.waypoints.y + compass.waypoints.size + 4
	stack.Position = UDim2.new(0.5, 0, 0, below * scale / factor)
end

-- Vitals -----------------------------------------------------------------------

local function updateHealth(instant: boolean?)
	local maxHealth = humanoid and humanoid.MaxHealth or GameConstants.BASE_MAX_HEALTH
	local fraction, shown = HudModel.Health(humanoid and humanoid.Health or 0, maxHealth)
	local cap = math.ceil(if maxHealth > 0 then maxHealth else 100)
	widgets.vitals:Set("health", fraction, ("%d/%d"):format(shown, cap), instant or instantMotion())
end

-- Stamina and Food replicate as 0–1 fractions (SurvivalService); shown out of 100.
local function updateFraction(key: string, attribute: string, instant: boolean?)
	local value = player:GetAttribute(attribute)
	local fraction = HudModel.Clamp01(if type(value) == "number" then value else 1)
	widgets.vitals:Set(key, fraction, ("%d/100"):format(HudModel.Percent(fraction)), instant or instantMotion())
end

local function updateStatus()
	local food = player:GetAttribute("Food")
	local lockLeft = (player:GetAttribute("MedicineLockUntil") or 0) - workspace:GetServerTimeNow()
	local slowed = type(food) == "number" and GameConstants.IsFoodSlowed(food)
	widgets.vitals:SetStatus(HudController.StatusChips(lockLeft, player:GetAttribute("FoodHealing") or 0, slowed))
end

local function forgetCharacter()
	for _, connection in humanoidConnections do
		connection:Disconnect()
	end
	table.clear(humanoidConnections)
	humanoid = nil
	updateHealth(true)
end

local function watchCharacter(character: Model)
	forgetCharacter()
	local found = character:WaitForChild("Humanoid", 10)
	if found == nil or player.Character ~= character or not found:IsA("Humanoid") then
		return
	end
	humanoid = found
	local function onHealth()
		updateHealth()
	end
	table.insert(humanoidConnections, found.HealthChanged:Connect(onHealth))
	table.insert(humanoidConnections, found:GetPropertyChangedSignal("MaxHealth"):Connect(onHealth))
	updateHealth(true)
end

-- Party ------------------------------------------------------------------------

-- Tribe-mates in this server (the TribeId attribute TribeService replicates),
-- excluding the local player, alphabetically, at most the layout's row count;
-- and how many there are in all.
local function partyMembers()
	local tribeId = player:GetAttribute("TribeId")
	if tribeId == nil then
		return {}, 0
	end
	local others = {}
	for _, other in Players:GetPlayers() do
		if other ~= player and other:GetAttribute("TribeId") == tribeId then
			table.insert(others, other)
		end
	end
	table.sort(others, function(a, b)
		return string.lower(a.DisplayName) < string.lower(b.DisplayName)
	end)
	local members = {}
	for index = 1, math.min(#others, layout.party.maxRows) do
		local other = others[index]
		local otherHumanoid = other.Character and other.Character:FindFirstChildOfClass("Humanoid")
		local health = if otherHumanoid then HudModel.Health(otherHumanoid.Health, otherHumanoid.MaxHealth) else 0
		members[index] = { userId = other.UserId, name = other.DisplayName, health = health }
	end
	return members, #others
end

-- Extraction objective -----------------------------------------------------------

-- A portal's zone radius: the server's ZoneRadius attribute, else the catalog.
local function zoneRadius(part: BasePart): number
	local radius = part:GetAttribute("ZoneRadius")
	if type(radius) == "number" and radius > 0 then
		return radius
	end
	for _, portal in PoiCatalog.Portals do
		if portal.name == part.Name then
			return portal.zoneRadius
		end
	end
	return HudController.DEFAULT_ZONE_RADIUS
end

-- The nearest running countdown, else the nearest active portal site.
local function nearestExtraction(position: Vector3?)
	if position == nil then
		return nil
	end
	local now = workspace:GetServerTimeNow()
	local best, bestDistance = nil, math.huge
	for _, event in ExtractionController.Events do
		local distance = flatDistance(position, event.position)
		if distance < bestDistance then
			bestDistance = distance
			best = {
				name = event.name,
				kind = event.kind,
				distance = distance,
				inZone = ExtractionRules.InZone(position, event.position, event.radius),
				remaining = math.max(0, event.endsAt - now),
				total = if event.kind == ExtractionRules.Kinds.Portable
					then ExtractionRules.PORTABLE_SECONDS
					else ExtractionRules.FIXED_SECONDS,
			}
		end
	end
	if best then
		return best
	end
	for part in portals do
		local distance = flatDistance(position, part.Position)
		if distance < bestDistance then
			bestDistance = distance
			local kind = part:GetAttribute("PortalKind")
			best = {
				name = part.Name,
				kind = kind,
				distance = distance,
				inZone = ExtractionRules.InZone(position, part.Position, zoneRadius(part)),
				total = if kind == ExtractionRules.Kinds.Portable
					then ExtractionRules.PORTABLE_SECONDS
					else ExtractionRules.FIXED_SECONDS,
			}
		end
	end
	return best
end

-- The category of the event the panel shows (its header icon).
local function eventCategory(views, id: any): string?
	for _, view in views do
		if view.id == id then
			return view.category
		end
	end
	return nil
end

-- Compass waypoints --------------------------------------------------------------

local function rebuildWaypoints()
	local list = {}
	table.clear(waypointPositions)
	local icons = HudController.WAYPOINT_ICONS
	local function add(id: string, icon: string, position: Vector3)
		table.insert(list, { id = id, icon = icon })
		waypointPositions[id] = position
	end
	-- The catalog's landmarks and camps describe the generated island only.
	if WorldState.IsGenerated() then
		for _, entry in PoiCatalog.Landmarks do
			add("landmark:" .. entry.id, icons.landmark, PoiCatalog.Position(entry))
		end
		for _, entry in PoiCatalog.SafeZones do
			add("camp:" .. entry.id, icons.camp, PoiCatalog.Position(entry))
		end
	end
	for part in portals do
		add("portal:" .. part:GetFullName(), icons.portal, part.Position)
	end
	for id, event in ExtractionController.Events do
		add("extract:" .. id, icons.extract, event.position)
	end
	for _, view in EventFeedController.ActiveViews() do
		add("event:" .. view.id, EventPanel.ICONS[view.category] or EventPanel.DEFAULT_ICON, view.position)
	end
	widgets.compass:SetWaypoints(list)
end

local function watchPortals()
	local function consider(child: Instance)
		if child:IsA("BasePart") and child:GetAttribute("PortalKind") then
			portals[child] = true
			rebuildWaypoints()
		end
	end
	for _, child in workspace:GetChildren() do
		consider(child)
	end
	workspace.ChildAdded:Connect(consider)
	workspace.ChildRemoved:Connect(function(child)
		if portals[child] then
			portals[child] = nil
			rebuildWaypoints()
		end
	end)
end

local function updateCompass()
	local camera = workspace.CurrentCamera
	if camera == nil then
		return
	end
	local look = camera.CFrame.LookVector
	local heading = HudModel.Heading(look.X, look.Z)
	local origin = rootPart()
	local from = if origin then origin.Position else camera.CFrame.Position
	local bearings = {}
	for id, position in waypointPositions do
		bearings[id] = HudModel.Bearing(from.X, from.Z, position.X, position.Z)
	end
	widgets.compass:Update(heading, bearings)
end

-- Hotbar -----------------------------------------------------------------------

local function selectSlot(index: number)
	HudController.Selected = index
	widgets.bottom:Select(index)
	HudController.SelectionChanged:Fire(index)
end

local function bindHotbar(active: boolean)
	if active == hotbarBound then
		return
	end
	hotbarBound = active
	if not active then
		ContextActionService:UnbindAction("FlintbornHudHotbar")
		return
	end
	-- One step above InventoryController's bindings (Medium, rebound often, so
	-- otherwise usually first) and passing every key on, so the hotbar keys still
	-- use their slot, as before. Below High, so build mode's placement (ButtonR1)
	-- sinks the bumper before it reaches us.
	-- Rebinding in Settings re-runs this with the new keys (Binds.Changed).
	local count = layout.bottom.hotbar.count
	local slotKeys = hotbarKeys(count)
	local keys = {}
	for key in slotKeys do
		table.insert(keys, key)
	end
	for key in HOTBAR_STEP_KEYS do
		table.insert(keys, key)
	end
	ContextActionService:BindActionAtPriority("FlintbornHudHotbar", function(_, state, input)
		if state == Enum.UserInputState.Begin then
			local index = slotKeys[input.KeyCode]
			local step = HOTBAR_STEP_KEYS[input.KeyCode]
			if index then
				selectSlot(index)
			elseif step then
				selectSlot(HudModel.HotbarStep(HudController.Selected, step, count))
			end
		end
		return Enum.ContextActionResult.Pass
	end, false, Enum.ContextActionPriority.Medium.Value + 1, table.unpack(keys))
end

-- Build ------------------------------------------------------------------------

local function newGui(name: string, order: number): (ScreenGui, Frame)
	local screen = Instance.new("ScreenGui")
	screen.Name = name
	screen.ResetOnSpawn = false
	screen.DisplayOrder = order
	screen.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	-- The layout uses full-screen design px and keeps clear of the top bar itself
	-- (applyTop); device cut-outs stay excluded.
	screen.IgnoreGuiInset = true
	pcall(function()
		screen.ScreenInsets = Enum.ScreenInsets.DeviceSafeInsets
	end)
	local frame = Instance.new("Frame")
	frame.Name = "Root"
	frame.BackgroundTransparency = 1
	frame.Size = UDim2.fromScale(1, 1)
	frame.Parent = screen
	return screen, frame
end

-- The menu tiles in the lobby's grid. Each tile's tooltip names its key, which
-- follows the player's rebinds. `open(entry)` runs a tile's action.
function HudController.BuildTiles(parent: Instance, cfg, open: (any) -> ())
	local region = Instance.new("Frame")
	region.Name = "Tiles"
	region.BackgroundTransparency = 1
	region.AnchorPoint = Vector2.new(0, 0.5)
	region.Position = UDim2.new(0, cfg.x, cfg.centreY, 0)
	region.Size = UDim2.fromOffset(cfg.size[1], cfg.size[2])
	region.Parent = parent
	local tiles = {}
	for index, entry in HudController.MENU do
		local column, row = (index - 1) % 2, (index - 1) // 2
		local tile = Kit.IconButton.new(region, {
			name = entry[1],
			rect = { column * cfg.pitch[1], row * cfg.pitch[2], cfg.tile[1], cfg.tile[2] },
			variant = "tile",
			icon = entry[2],
			onPress = function()
				open(entry)
			end,
		})
		Kit.Tooltip.Attach(tile, function()
			return ("%s (%s)"):format(entry[1], Binds.Label(entry[3]))
		end, { side = "right" })
		tiles[index] = tile
	end
	for index, tile in tiles do
		local hit = tile.control.hit
		local function at(i: number)
			return tiles[i] and tiles[i].control.hit
		end
		hit.NextSelectionUp = at(index - 2)
		hit.NextSelectionDown = at(index + 2)
		hit.NextSelectionLeft = if index % 2 == 0 then at(index - 1) else nil
		hit.NextSelectionRight = if index % 2 == 1 then at(index + 1) else nil
	end
	return region, tiles
end

local function build()
	local controllers = script.Parent
	gui, root = newGui("FlintbornHud", Kit.Tokens.Order("hud"))
	gui.Enabled = false
	widgets.party = PartyFrames.new(root, layout)
	widgets.compass = Compass.new(root, layout)
	widgets.vitals = Vitals.new(root, layout)
	widgets.objective = ObjectivePanel.new(root, layout)
	widgets.event = EventPanel.new(root, layout)
	widgets.bottom = BottomBar.new(root, layout)
	widgets.tileRegion, widgets.tiles = HudController.BuildTiles(root, layout.tiles, function(entry)
		-- Required on use: these controllers start after the HUD.
		(require(controllers[entry[4]]) :: any)[entry[5]]()
	end)
	for _, object in
		{
			widgets.party.root,
			widgets.compass.root,
			widgets.vitals.root,
			widgets.vitals.status,
			widgets.objective.root,
			widgets.event.root,
		}
	do
		table.insert(tops, { object = object, base = object.Position })
	end
	gui.Parent = player:WaitForChild("PlayerGui")
	Kit.Scale.Hud(gui, root)
	uiScale = root:FindFirstChildWhichIsA("UIScale") :: UIScale

	-- XP pop-ups live in their own always-enabled gui, laid out like the bottom
	-- group, so pop-ups outside a run (protected extraction, tutorial) still show.
	local overlayRoot
	overlay, overlayRoot = newGui("FlintbornHudOverlay", Kit.Tokens.Order("hud") + 1)
	local group = Instance.new("Frame")
	group.Name = "BottomGroup"
	group.BackgroundTransparency = 1
	Layout.Place(group, layout.bottom)
	group.Parent = overlayRoot
	local popups = Instance.new("Frame")
	popups.Name = "XpPopups"
	popups.BackgroundTransparency = 1
	popups.Position = Layout.Position(layout.bottom.popups)
	popups.Size = Layout.Size(layout.bottom.popups)
	popups.Parent = group
	widgets.popups = popups
	overlay.Parent = player:WaitForChild("PlayerGui")
	Kit.Scale.Hud(overlay, overlayRoot)
end

local function refreshVisible()
	local visible = SessionStates.IsAtRisk(player:GetAttribute("SessionState"))
	gui.Enabled = visible
	bindHotbar(visible)
	-- Re-places (or resets) the shared banner column for the new state.
	applyTop()
	HudMode.SetVisible(visible)
end

function HudController.Start()
	if not HudMode.ReplacesLegacy() then
		return
	end
	layout = Layout.Get()
	build()
	applyTop()
	uiScale:GetPropertyChangedSignal("Scale"):Connect(applyTop)
	gui:GetPropertyChangedSignal("AbsoluteSize"):Connect(applyTop)
	pcall(function()
		GuiService:GetPropertyChangedSignal("TopbarInset"):Connect(applyTop)
	end)

	-- Vitals: Humanoid health (respawns included) and the survival attributes.
	player.CharacterAdded:Connect(watchCharacter)
	player.CharacterRemoving:Connect(forgetCharacter)
	if player.Character then
		task.spawn(watchCharacter, player.Character)
	else
		updateHealth(true)
	end
	updateFraction("stamina", "Stamina", true)
	updateFraction("food", "Food", true)
	player:GetAttributeChangedSignal("Stamina"):Connect(function()
		updateFraction("stamina", "Stamina")
	end)
	player:GetAttributeChangedSignal("Food"):Connect(function()
		updateFraction("food", "Food")
	end)

	-- Level and XP from the same snapshots ProgressionController receives; its XP
	-- pop-ups appear just above the bar.
	ProgressionController.Changed:Connect(function(view)
		widgets.bottom:SetProgress(view, instantMotion())
	end)
	widgets.bottom:SetProgress(ProgressionController.View(), true)
	ProgressionController.MountPopups(widgets.popups)

	-- Hotbar: the run inventory's hotbar items. The Hotbar1–6 binds (keys 1–6 by
	-- default) and taps select a slot and use it, as InventoryController's keys do
	-- (equip, eat, place, ready); the right gamepad bumper only steps the
	-- selection. The mouse wheel stays on camera zoom (GDD Q58). Slot badges name
	-- the bound keys and follow rebinds.
	local count = layout.bottom.hotbar.count
	selectSlot(HudController.Selected)
	widgets.bottom.SlotPressed:Connect(function(index)
		selectSlot(index)
		task.spawn(InventoryController.ActivateHotbar, index)
	end)
	local function showItems(snapshot)
		widgets.bottom:SetSlotItems(HudController.HotbarItems(snapshot, count))
		if snapshot.equipped and snapshot.equipped ~= HudController.Selected then
			selectSlot(snapshot.equipped)
		end
	end
	InventoryController.Changed:Connect(showItems)
	showItems(InventoryController.Snapshot)
	widgets.bottom:SetSlotLabels(hotbarLabels(count))
	Binds.Changed:Connect(function()
		widgets.bottom:SetSlotLabels(hotbarLabels(count))
		if hotbarBound then
			hotbarBound = false
			bindHotbar(true)
		end
	end)

	-- Compass waypoints and the two top-right panels.
	watchPortals()
	rebuildWaypoints()
	workspace:GetAttributeChangedSignal(WorldState.GENERATED_ATTRIBUTE):Connect(rebuildWaypoints)
	ExtractionController.Changed:Connect(rebuildWaypoints)
	EventFeedController.Changed:Connect(rebuildWaypoints)

	InteractionPrompt.Start(function()
		return scale
	end)

	player:GetAttributeChangedSignal("SessionState"):Connect(refreshVisible)
	refreshVisible()

	local sinceFast, sinceSlow = math.huge, math.huge
	RunService.RenderStepped:Connect(function(dt)
		if not gui.Enabled then
			return
		end
		updateCompass()
		sinceFast += dt
		sinceSlow += dt
		if sinceFast >= HudController.FAST_SECONDS then
			sinceFast = 0
			updateStatus()
		end
		if sinceSlow >= HudController.SLOW_SECONDS then
			sinceSlow = 0
			local origin = rootPart()
			local position = origin and origin.Position
			local now = workspace:GetServerTimeNow()
			local views = EventFeedController.ActiveViews()
			local members, total = partyMembers()
			widgets.party:Set(members, instantMotion(), total)
			widgets.objective:Set(HudModel.ExtractionObjective(nearestExtraction(position)))
			local event = HudModel.WorldEvent(views, now, position and position.X, position and position.Z)
			widgets.event:Set(event, event and eventCategory(views, event.id))
		end
	end)
end

return HudController
