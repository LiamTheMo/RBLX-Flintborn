-- In-world HUD (GDD §11, §25.4), laid out from src/shared/UI/HudLayout.json and
-- drawn from the UI art sheets (art/ui/sprites, uploaded ids in UiAssetIds.json,
-- styled Frames until then). Party frames, compass with waypoints, extraction
-- objective, world event, vitals, level/XP bar, the hotbar (its items; a tap
-- uses a slot like its key) and the custom interaction prompt. It only displays what the server already
-- replicated: Humanoid health, the Stamina/Food/MedicineLockUntil/FoodHealing
-- attributes, progression snapshots, TribeId attributes, and the extraction and
-- event remotes (through their controllers). World place only, during a run.

local ContextActionService = game:GetService("ContextActionService")
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
local Layout = require(Hud.Layout)
local Parchment = require(Hud.Parchment)
local ObjectivePanel = require(Hud.ObjectivePanel)
local PartyFrames = require(Hud.PartyFrames)
local Vitals = require(Hud.Vitals)
local Widgets = require(Hud.Widgets)
local Binds = require(script.Parent.Parent.Ui.Binds)
local Theme = require(script.Parent.Parent.Ui.Theme)

local HudController = {}

-- Fires (index) when the selected hotbar slot changes. The selection follows the
-- equipped slot, and every key press or tap on a slot also uses it.
HudController.SelectionChanged = Signal.new()

-- The in-HUD menu row: {label, controller, function}.
HudController.MENU = {
	{ "CRAFT", "CraftingController", "Toggle" },
	{ "BUILD", "BuildController", "Toggle" },
	{ "TRIBE", "TribeController", "Toggle" },
	{ "MAP", "MapController", "Toggle" },
	{ "PROGRESS", "ProgressionController", "Toggle" },
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

local player = Players.LocalPlayer
local layout = nil
local gui = nil
local root = nil
local uiScale = nil
local overlayRoot = nil
local overlayScale = nil
local scale = 1
local widgets = {}
local humanoid = nil
local humanoidConnections = {}
local thumbnails = {}
local portals = {}
local waypointPositions = {}
local hotbarBound = false

local function instantMotion(): boolean
	return Theme.ReducedMotion()
end

local function rootPart(): BasePart?
	local character = player.Character
	return character and character:FindFirstChild("HumanoidRootPart") :: BasePart?
end

local function flatDistance(a: Vector3, b: Vector3): number
	local dx, dz = a.X - b.X, a.Z - b.Z
	return math.sqrt(dx * dx + dz * dz)
end

-- Scale ------------------------------------------------------------------------

local function applyScale()
	local size = gui.AbsoluteSize
	scale = HudModel.HudScale(
		size.X,
		size.Y,
		layout.reference.width,
		layout.reference.height,
		layout.scale.min,
		layout.scale.max,
		player:GetAttribute("UiScale")
	)
	uiScale.Scale = scale
	root.Size = UDim2.fromScale(1 / scale, 1 / scale)
	overlayScale.Scale = scale
	overlayRoot.Size = root.Size
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
	local below = compass.pos[4] + compass.waypoints.y + compass.waypoints.size + 4
	stack.Position = UDim2.new(0.5, 0, 0, below * scale / factor)
end

-- Vitals -----------------------------------------------------------------------

local function updateHealth(instant: boolean?)
	local fraction, shown = HudModel.Health(
		humanoid and humanoid.Health or 0,
		humanoid and humanoid.MaxHealth or GameConstants.BASE_MAX_HEALTH
	)
	widgets.vitals:Set("health", fraction, tostring(shown), instant or instantMotion())
end

-- Stamina and Food replicate as 0–1 fractions (SurvivalService); shown as 0–100.
local function updateFraction(key: string, attribute: string, instant: boolean?)
	local value = player:GetAttribute(attribute)
	local fraction = HudModel.Clamp01(if type(value) == "number" then value else 1)
	widgets.vitals:Set(key, fraction, tostring(HudModel.Percent(fraction)), instant or instantMotion())
end

local function updateStatus()
	local food = player:GetAttribute("Food")
	local lockLeft = (player:GetAttribute("MedicineLockUntil") or 0) - workspace:GetServerTimeNow()
	local slowed = type(food) == "number" and GameConstants.IsFoodSlowed(food)
	local crouching = player:GetAttribute("Crouching") == true
	local text = HudModel.SurvivalStatus(lockLeft, player:GetAttribute("FoodHealing") or 0, slowed, crouching)
	widgets.vitals:SetStatus(text)
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

local function thumbnail(userId: number): string?
	local cached = thumbnails[userId]
	if cached == nil then
		thumbnails[userId] = false
		task.spawn(function()
			local ok, content = pcall(
				Players.GetUserThumbnailAsync,
				Players,
				userId,
				Enum.ThumbnailType.HeadShot,
				Enum.ThumbnailSize.Size100x100
			)
			thumbnails[userId] = if ok then content else ""
		end)
		return nil
	end
	return if cached then cached else nil
end

-- Tribe-mates in this server (the TribeId attribute TribeService replicates),
-- excluding the local player, alphabetically, at most the layout's row count.
local function partyMembers()
	local tribeId = player:GetAttribute("TribeId")
	if tribeId == nil then
		return {}
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
		members[index] = {
			userId = other.UserId,
			name = other.DisplayName,
			health = health,
			thumbnail = thumbnail(other.UserId),
		}
	end
	return members
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

-- Compass waypoints --------------------------------------------------------------

local function rebuildWaypoints()
	local list = {}
	table.clear(waypointPositions)
	local function add(id: string, icon: string, position: Vector3)
		table.insert(list, { id = id, icon = icon })
		waypointPositions[id] = position
	end
	-- The catalog's landmarks and camps describe the generated island only.
	if WorldState.IsGenerated() then
		for _, entry in PoiCatalog.Landmarks do
			add("landmark:" .. entry.id, "icon_mountain", PoiCatalog.Position(entry))
		end
		for _, entry in PoiCatalog.SafeZones do
			add("camp:" .. entry.id, "icon_tower", PoiCatalog.Position(entry))
		end
	end
	for part in portals do
		add("portal:" .. part:GetFullName(), "icon_waypoint", part.Position)
	end
	for id, event in ExtractionController.Events do
		add("extract:" .. id, "icon_run", event.position)
	end
	for _, view in EventFeedController.ActiveViews() do
		add("event:" .. view.id, "icon_storm", view.position)
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
	local slotKeys = hotbarKeys(layout.bottom.hotbar.count)
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
				selectSlot(HudModel.HotbarStep(HudController.Selected, step, layout.bottom.hotbar.count))
			end
		end
		return Enum.ContextActionResult.Pass
	end, false, Enum.ContextActionPriority.Medium.Value + 1, table.unpack(keys))
end

-- Build ------------------------------------------------------------------------

local function build()
	gui = Instance.new("ScreenGui")
	gui.Name = "FlintbornHud"
	gui.ResetOnSpawn = false
	gui.DisplayOrder = 1
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	gui.Enabled = false
	root = Instance.new("Frame")
	root.Name = "Root"
	root.BackgroundTransparency = 1
	root.Size = UDim2.fromScale(1, 1)
	root.Parent = gui
	uiScale = Instance.new("UIScale")
	uiScale.Parent = root
	widgets.party = PartyFrames.new(root, layout)
	widgets.compass = Compass.new(root, layout)
	widgets.objective = ObjectivePanel.new(root, layout)
	widgets.event = EventPanel.new(root, layout)
	widgets.vitals = Vitals.new(root, layout)
	widgets.bottom = BottomBar.new(root, layout)
	-- The backpack button on the left, as the HUD sheet draws it (touch and mouse
	-- open the run backpack without a key).
	if layout.backpack then
		local holder = Instance.new("Frame")
		holder.Name = "Backpack"
		holder.BackgroundTransparency = 1
		Layout.Place(holder, layout.backpack)
		holder.Parent = root
		local art =
			Widgets.Sprite(layout.backpack.sprite, { Name = "Art", Size = UDim2.fromScale(1, 1), ZIndex = 3 }, holder)
		Parchment.Pressable(holder, art, function()
			InventoryController.ToggleBackpack()
		end)
	end
	-- The other panels' buttons (touch players have no keys): MENU under the
	-- backpack opens a row of them, so the old navigation bar no longer covers
	-- the vitals and cards on the right.
	if layout.menu then
		local cfg = layout.menu
		local holder = Instance.new("Frame")
		holder.Name = "Menu"
		holder.BackgroundTransparency = 1
		Layout.Place(holder, cfg)
		holder.Parent = root
		local row = Instance.new("Frame")
		row.Name = "Row"
		row.BackgroundTransparency = 1
		row.Position = UDim2.fromOffset(cfg.size[1] + cfg.gap, 0)
		row.Size = UDim2.fromOffset(#HudController.MENU * (cfg.item[1] + cfg.gap), cfg.item[2])
		row.Visible = false
		row.Parent = holder
		local controllers = script.Parent
		for index, entry in HudController.MENU do
			Parchment.Button(
				"pm_button_paper",
				{
					(index - 1) * (cfg.item[1] + cfg.gap),
					0,
					cfg.item[1],
					cfg.item[2],
				},
				row,
				function()
					row.Visible = false
					-- Required on use: these controllers start after the HUD.
					(require(controllers[entry[2]]) :: any)[entry[3]]()
				end,
				{ name = entry[1], label = entry[1], size = 20, inset = 14 }
			)
		end
		Parchment.Button("pm_button_paper", { 0, 0, cfg.size[1], cfg.size[2] }, holder, function()
			row.Visible = not row.Visible
		end, { name = "Toggle", label = "MENU", size = 22, inset = 14 })
	end
	gui.Parent = player:WaitForChild("PlayerGui")

	-- XP pop-ups live in their own always-enabled gui, laid out like the bottom
	-- group, so pop-ups outside a run (protected extraction, tutorial) still show.
	local overlay = Instance.new("ScreenGui")
	overlay.Name = "FlintbornHudOverlay"
	overlay.ResetOnSpawn = false
	overlay.DisplayOrder = 2
	overlayRoot = Instance.new("Frame")
	overlayRoot.Name = "Root"
	overlayRoot.BackgroundTransparency = 1
	overlayRoot.Size = UDim2.fromScale(1, 1)
	overlayRoot.Parent = overlay
	overlayScale = Instance.new("UIScale")
	overlayScale.Parent = overlayRoot
	local group = Instance.new("Frame")
	group.Name = "BottomGroup"
	group.BackgroundTransparency = 1
	Layout.Place(group, layout.bottom)
	group.Parent = overlayRoot
	local popups = Instance.new("Frame")
	popups.Name = "XpPopups"
	popups.BackgroundTransparency = 1
	popups.Position = Layout.Position(layout.bottom.popups.rect)
	popups.Size = Layout.Size(layout.bottom.popups.rect)
	popups.Parent = group
	widgets.popups = popups
	overlay.Parent = player:WaitForChild("PlayerGui")
end

local function refreshVisible()
	local visible = SessionStates.IsAtRisk(player:GetAttribute("SessionState"))
	gui.Enabled = visible
	bindHotbar(visible)
	-- Re-places (or resets) the shared banner column for the new state.
	applyScale()
	HudMode.SetVisible(visible)
end

function HudController.Start()
	if not HudMode.ReplacesLegacy() then
		return
	end
	layout = Layout.Get()
	build()
	applyScale()
	gui:GetPropertyChangedSignal("AbsoluteSize"):Connect(applyScale)
	player:GetAttributeChangedSignal("UiScale"):Connect(function()
		task.defer(applyScale)
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
	-- pop-ups move just above the new bar.
	ProgressionController.Changed:Connect(function(view)
		widgets.bottom:SetProgress(view, instantMotion())
	end)
	local view = ProgressionController.View()
	if view then
		widgets.bottom:SetProgress(view, true)
	end
	ProgressionController.MountPopups(widgets.popups)

	-- Hotbar: the run inventory's hotbar items. The Hotbar1–6 binds (keys 1–6 by
	-- default) and taps select a slot and use it, as InventoryController's keys do
	-- (equip, eat, place, ready); the right gamepad bumper only steps the
	-- selection. The mouse wheel stays on camera zoom (GDD Q58). Slot numbers name
	-- the bound keys and follow rebinds.
	selectSlot(HudController.Selected)
	widgets.bottom.SlotPressed:Connect(function(index)
		selectSlot(index)
		task.spawn(InventoryController.ActivateHotbar, index)
	end)
	local function showItems(snapshot)
		widgets.bottom:SetSlotItems(HudModel.HotbarSlots(snapshot, layout.bottom.hotbar.count))
		if snapshot.equipped and snapshot.equipped ~= HudController.Selected then
			selectSlot(snapshot.equipped)
		end
	end
	InventoryController.Changed:Connect(showItems)
	showItems(InventoryController.Snapshot)
	widgets.bottom:SetSlotLabels(hotbarLabels(layout.bottom.hotbar.count))
	Binds.Changed:Connect(function()
		widgets.bottom:SetSlotLabels(hotbarLabels(layout.bottom.hotbar.count))
		if hotbarBound then
			hotbarBound = false
			bindHotbar(true)
		end
	end)
	-- The backpack view uses the old strip to move items, so it takes the spot.
	InventoryController.BackpackToggled:Connect(function(open)
		widgets.bottom.hotbar.Visible = not open
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
			widgets.party:Set(partyMembers(), instantMotion())
			widgets.objective:Set(HudModel.ExtractionObjective(nearestExtraction(position)))
			widgets.event:Set(HudModel.WorldEvent(views, now, position and position.X, position and position.Z))
		end
	end)
end

return HudController
