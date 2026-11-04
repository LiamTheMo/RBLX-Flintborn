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
local Geometry = require(ReplicatedStorage.Shared.Core.Geometry)
local HudModel = require(ReplicatedStorage.Shared.UI.HudModel)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local PoiCatalog = require(ReplicatedStorage.Shared.World.PoiCatalog)
local Keybinds = require(ReplicatedStorage.Shared.Settings.Keybinds)
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
local OverheadHealth = require(Hud.OverheadHealth)
local PartyFrames = require(Hud.PartyFrames)
local Vitals = require(Hud.Vitals)
local Binds = require(script.Parent.Parent.Ui.Binds)
local Theme = require(script.Parent.Parent.Ui.Theme)

local HudController = {}

-- The menu tiles (left, the lobby's 2 × 3 grid): {id, icon, bind action named
-- in the tooltip, controller, function}. Touch players have no keys, so every
-- panel with a key has a tile.
HudController.MENU = {
	{ "Backpack", "backpack", "Backpack", "InventoryController", "ToggleBackpack" },
	{ "Craft", "hammer", "Craft", "CraftingController", "Toggle" },
	{ "Build", "icon.build", "Build", "BuildController", "Toggle" },
	{ "Tribe", "party", "Tribe", "TribeController", "Toggle" },
	{ "Map", "map", "Map", "MapController", "Toggle" },
	{ "Progress", "trophy", "Progression", "ProgressionController", "Toggle" },
}

-- The selected hotbar slot. A slot is always held in a run (slot 1 at start; an
-- empty one is bare hands), so a slot is always selected: the selection follows
-- the held slot, and every key press or tap on a slot selects and uses it.
HudController.Selected = 1 :: number?

-- Status text ticks fast (the medicine countdown); party, objective and event
-- panels refresh a little slower.
HudController.FAST_SECONDS = 0.1
HudController.SLOW_SECONDS = 0.25
-- A portal site counts as reached inside this radius when the part has no
-- ZoneRadius attribute and the catalog has no entry.
HudController.DEFAULT_ZONE_RADIUS = 10
-- Where Theme's shared top column sits when the HUD is not pushing it down.
HudController.TOP_STACK_POSITION = Theme.TOP_STACK_POSITION
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

-- The status plaques and the hotbar's items (pure rules in HudModel; the
-- capture scenes call them here).
HudController.StatusChips = HudModel.StatusChips
HudController.HotbarItems = HudModel.HotbarItems

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

local function rootPart(): BasePart?
	local character = player.Character
	return character and character:FindFirstChild("HumanoidRootPart") :: BasePart?
end

-- Scale and top inset ----------------------------------------------------------

-- The HUD grid (ARCHITECTURE D30; HudLayout "grid", the lobby HUD uses the
-- same): the right-hand column (vitals, status plaques, extraction objective
-- and, on desktops and tablets, the world event) starts the grid's margin
-- from the screen's top and right edges, its pieces one under another with
-- the grid's gap and one width; the left-hand column (the tribe frames on
-- desktops; on phones the menu tiles and the world event) starts the gap
-- under Roblox's top-bar buttons, the desktop tiles centred on the screen's
-- height, all at one left edge. Each column keeps the margin from its side
-- while it lies wholly in the corner bands, else the device safe inset where
-- that is larger (Layout.PlaceColumns). The compass sits in the top bar's
-- row, centred (owner decision D28).
-- Design px kept between the compass and Roblox's buttons or the vitals.
HudController.TOP_ROW_GAP = 16
-- Where Roblox's left-hand top-bar buttons end (screen px) when the engine
-- does not report it (GuiService.TopbarInset): an 844 × 390 iPhone's, notch
-- included, with room to spare.
HudController.TOP_BUTTONS_REACH = 230

-- Roblox's top bar in the HUD root's design px: `inset` how far down it
-- reaches, `left` how far right its left-hand buttons reach, `right` where its
-- right-hand area starts and `width` the root's width; `scale` is the root's
-- UIScale. From the bar's reach and the gui's width in screen px, the
-- engine's GuiService.TopbarInset (the bar's free area, or nil) and the gui's
-- left edge on the screen.
function HudController.TopBar(insetPx: number, widthPx: number, k: number, topbar: Rect?, originX: number?)
	k = math.max(k, 0.01)
	local left, right = HudController.TOP_BUTTONS_REACH, widthPx
	if topbar and topbar.Max.Y > 0 and topbar.Max.X > topbar.Min.X then
		left = math.max(0, topbar.Min.X - (originX or 0))
		right = math.min(widthPx, topbar.Max.X - (originX or 0))
	end
	return { inset = insetPx / k, left = left / k, right = right / k, width = widthPx / k, scale = k }
end

-- The mounted regions by column: {right = {GuiObject} (stacked from the
-- top), left = {GuiObject} (stacked under the bar), free = {GuiObject} (left
-- column, placed by their own height: the desktop tiles), compass, strip
-- (the phone tribe strip under the compass), vitals}. A region's column is
-- its layout entry's (HudLayout "column", Layout.ForScreen).
function HudController.TopRegions(mounted)
	local layout = Layout.Get()
	local regions = { right = {}, left = {}, free = {} }
	local compass = mounted.compass
	regions.compass = {
		object = compass.root,
		base = compass.root.Position,
		size = compass.root.Size,
		-- The leather arrow pokes above the plaque: keep it on screen.
		minTop = math.max(0, -compass.cfg.marker[2]) + 2,
		depth = compass.cfg.waypoints.y + compass.cfg.waypoints.size,
	}
	local function add(object: GuiObject, key: string)
		local cfg = Layout.Section(layout, key)
		if cfg.column == "right" then
			table.insert(regions.right, object)
		elseif cfg.column == "left" then
			table.insert(if type(cfg.centreY) == "number" then regions.free else regions.left, object)
		end
	end
	if mounted.party.cfg.strip then
		local party = mounted.party.root
		regions.strip = { object = party, base = party.Position, height = mounted.party.cfg.height }
	else
		add(mounted.party.root, "party")
	end
	add(mounted.tileRegion, "tiles")
	add(mounted.vitals.root, "vitals")
	add(mounted.vitals.status, "status")
	add(mounted.objective.root, "objective")
	add(mounted.event.root, "event")
	regions.vitals = mounted.vitals.root
	return regions
end

-- A region's left edge in design px on a root `width` wide.
local function leftEdge(object: GuiObject, width: number): number
	local w = object.Size.X.Offset
	return object.Position.X.Scale * width + object.Position.X.Offset - object.AnchorPoint.X * w
end

-- Places the regions for the Roblox top bar `bar` (HudController.TopBar) on
-- the `screen` (Kit.Scale.HudScreen): the right-hand column the grid's
-- margin from the top (below the bar only when the bar's right-hand area
-- reaches over it), the left-hand column the grid's gap under Roblox's
-- buttons, both on the grid (Layout.PlaceColumns), then the compass centred
-- on the buttons' line between them and the right-hand column (below the
-- bar when it does not fit) and the phone tribe strip centred under it.
-- Returns {right, left (each column's gap from its edge, design px),
-- rightTop, leftTop, compassTop, compassX (its centre's offset from the
-- screen's centre), inRow}.
function HudController.PlaceTop(regions, bar, screen)
	local k = bar.scale or 1
	local grid = Layout.Grid()
	local rowTop, rowCentre = HudModel.TopRow(bar.inset * k)
	-- Under Roblox's buttons, the grid's gap below their foot.
	local belowBar = (rowTop + HudModel.TOP_BUTTON) / k + grid.gap
	-- The right-hand column: the margin from the top, unless the bar's
	-- right-hand area reaches over it (the bar's free area ends before the
	-- column's edge and before the safe area's: Roblox's own right-hand items
	-- sit inside the safe area).
	local safeRight = bar.width - (if screen.insets then screen.insets.right else 0) / k
	local rightTop = grid.margin
	if bar.right < math.min(bar.width - grid.margin, safeRight) - 0.5 then
		rightTop = math.max(rightTop, math.ceil(bar.inset + grid.gap))
	end
	local placed = Layout.PlaceColumns({
		right = { stack = regions.right, top = rightTop },
		left = { stack = regions.left, free = regions.free, top = math.ceil(belowBar) },
	}, screen)
	placed.rightTop, placed.leftTop = rightTop, math.ceil(belowBar)
	placed.inRow = false

	-- The compass: centred on the buttons' line, clear of them and the column.
	local compass = regions.compass
	if compass then
		local w, h = compass.size.X.Offset, compass.size.Y.Offset
		local columnLeft = if regions.vitals then leftEdge(regions.vitals, bar.width) else bar.width
		local rightLimit = math.min(bar.right, columnLeft)
		local centre = HudModel.RowCentre(bar.width, w, bar.left, rightLimit, HudController.TOP_ROW_GAP)
		local y
		if centre then
			placed.inRow = true
			y = math.max(compass.minTop, math.round(rowCentre / k - h / 2))
		else
			centre = bar.width / 2
			y = math.max(compass.minTop, math.ceil(belowBar))
		end
		placed.compassX = math.round(centre - bar.width / 2)
		placed.compassTop = y
		compass.object.Position = UDim2.new(0.5, placed.compassX, 0, y)
		-- The phone tribe strip hangs under the compass, centred on it.
		local strip = regions.strip
		if strip then
			strip.object.Position = UDim2.new(0.5, placed.compassX, 0, strip.base.Y.Offset + y - compass.base.Y.Offset)
		end
	end
	return placed
end

local function applyTop()
	scale = uiScale.Scale
	local screen = Kit.Scale.HudScreen(gui, scale)
	local bar = HudController.TopBar(
		Kit.Scale.TopInset(gui),
		screen.width,
		scale,
		Kit.Scale.TopbarInset(),
		gui.AbsolutePosition.X
	)
	local placed = HudController.PlaceTop(tops, bar, screen)
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
	local below = (placed.compassTop or 0) + tops.compass.depth + 4
	-- Phones: the tribe strip sits under the compass, so banners start below it.
	if tops.strip then
		below = math.max(below, tops.strip.object.Position.Y.Offset + tops.strip.height + 6)
	end
	stack.Position = UDim2.new(0.5, 0, 0, below * scale / factor)
end

-- The columns stack their shown pieces (D30), so they are placed again when
-- a piece shows, hides or changes height (the status plaques, the world
-- event, the tribe frames), once per frame at most.
local regionConnections = {}
local topQueued = false
local function queueTop()
	if topQueued then
		return
	end
	topQueued = true
	task.defer(function()
		topQueued = false
		applyTop()
	end)
end
local function watchRegions()
	for _, connection in regionConnections do
		connection:Disconnect()
	end
	table.clear(regionConnections)
	for _, object in { widgets.vitals.status, widgets.objective.root, widgets.event.root, widgets.party.root } do
		table.insert(regionConnections, object:GetPropertyChangedSignal("Visible"):Connect(queueTop))
		table.insert(regionConnections, object:GetPropertyChangedSignal("Size"):Connect(queueTop))
	end
end

-- Vitals -----------------------------------------------------------------------

local function updateHealth(instant: boolean?)
	local maxHealth = humanoid and humanoid.MaxHealth or GameConstants.BASE_MAX_HEALTH
	local fraction, shown = HudModel.Health(humanoid and humanoid.Health or 0, maxHealth)
	local cap = math.ceil(if maxHealth > 0 then maxHealth else 100)
	widgets.vitals:Set("health", fraction, ("%d/%d"):format(shown, cap), instant or Kit.Motion.Reduced())
end

-- Stamina and Food replicate as 0–1 fractions (SurvivalService); shown out of 100.
local function updateFraction(key: string, attribute: string, instant: boolean?)
	local value = player:GetAttribute(attribute)
	local fraction = HudModel.Clamp01(if type(value) == "number" then value else 1)
	widgets.vitals:Set(key, fraction, ("%d/100"):format(HudModel.Percent(fraction)), instant or Kit.Motion.Reduced())
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
		local distance = Geometry.FlatDistance(position, event.position)
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
		local distance = Geometry.FlatDistance(position, part.Position)
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

local function selectSlot(index: number?)
	HudController.Selected = index
	widgets.bottom:Select(index)
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
	-- use their slot, as before. Below High, so build mode's rotate (ButtonR1 /
	-- ButtonL1) sinks the bumpers before they reach us.
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
				selectSlot(HudModel.HotbarStep(HudController.Selected or 1, step, count))
			end
		end
		return Enum.ContextActionResult.Pass
	end, false, Enum.ContextActionPriority.Medium.Value + 1, table.unpack(keys))
end

-- Build ------------------------------------------------------------------------

-- The gamepad button bound to a menu tile's action (a KeyCode name), if any.
function HudController.GamepadKey(action: string): string?
	local bind = Keybinds.Get(action)
	return bind and bind.gamepad and bind.gamepad[1] or nil
end

-- A tile's tooltip for the input in use: its key ("Backpack (B)"), its
-- gamepad button ("Backpack (Y)"), or just its name on touch.
function HudController.TileHint(entry): string
	local hint = Kit.Input.Hint(Binds.Label(entry[3]), HudController.GamepadKey(entry[3]))
	return if hint then ("%s (%s)"):format(entry[1], hint) else entry[1]
end

-- The menu tiles in the lobby's grid (2 × 3 at the left edge; on phones 3 × 2
-- at the top left, above the thumbstick's touch zone). Each tile's tooltip names its
-- key or gamepad button, which follows the player's rebinds. `open(entry)`
-- runs a tile's action.
function HudController.BuildTiles(parent: Instance, cfg, open: (any) -> ())
	cfg = Layout.ForScreen(cfg)
	local columns = cfg.columns or 2
	local grid = Layout.TileGrid(cfg, #HudController.MENU)
	local region = Instance.new("Frame")
	region.Name = "Tiles"
	region.BackgroundTransparency = 1
	region.AnchorPoint = Vector2.new(cfg.anchor[1], cfg.anchor[2])
	region.Position = UDim2.new(cfg.pos[1], cfg.pos[2], cfg.pos[3], cfg.pos[4])
	region.Size = UDim2.fromOffset(grid.w, grid.h)
	region.Parent = parent
	local tiles = {}
	for index, entry in HudController.MENU do
		local tile = Kit.IconButton.new(region, {
			name = entry[1],
			rect = grid.rects[index],
			variant = "tile",
			icon = entry[2],
			onPress = function()
				open(entry)
			end,
		})
		Kit.Tooltip.Attach(tile, function()
			return HudController.TileHint(entry)
		end, { side = if columns > 2 then "top" else "right" })
		tiles[index] = tile
	end
	for index, tile in tiles do
		local hit = tile.control.hit
		local function at(i: number)
			return tiles[i] and tiles[i].control.hit
		end
		local column = (index - 1) % columns
		hit.NextSelectionUp = at(index - columns)
		hit.NextSelectionDown = at(index + columns)
		hit.NextSelectionLeft = if column > 0 then at(index - 1) else nil
		hit.NextSelectionRight = if column < columns - 1 then at(index + 1) else nil
	end
	return region, tiles
end

-- Builds every HUD region into `parent` (a design-px root) and returns them:
-- {party, compass, vitals, objective, event, bottom, tileRegion, tiles,
-- tileColumns}.
-- `open(entry)` runs a menu tile; the capture scenes build the HUD this way.
function HudController.Mount(parent: Instance, hudLayout, open: (any) -> ())
	local mounted = {}
	mounted.party = PartyFrames.new(parent, hudLayout)
	mounted.compass = Compass.new(parent, hudLayout)
	mounted.vitals = Vitals.new(parent, hudLayout)
	mounted.objective = ObjectivePanel.new(parent, hudLayout)
	mounted.event = EventPanel.new(parent, hudLayout)
	mounted.bottom = BottomBar.new(parent, hudLayout)
	mounted.tileRegion, mounted.tiles = HudController.BuildTiles(parent, hudLayout.tiles, open)
	mounted.tileColumns = Layout.ForScreen(hudLayout.tiles).columns or 2
	return mounted
end

-- The live HUD's regions (nil before Start), for scenes and diagnostics.
function HudController.Widgets()
	return if gui then widgets else nil
end

local function openTile(entry)
	-- Required on use: these controllers start after the HUD.
	(require(script.Parent[entry[4]]) :: any)[entry[5]]()
end

local function build()
	-- Both guis use full-screen design px on the whole screen and keep clear of
	-- the top bar and of notches themselves (applyTop, the HUD grid: D30).
	gui, root = Kit.Scale.HudGui("FlintbornHud", Kit.Tokens.Order("hud"))
	gui.Enabled = false
	widgets = HudController.Mount(root, layout, openTile)
	tops = HudController.TopRegions(widgets)
	gui.Parent = player:WaitForChild("PlayerGui")
	Kit.Scale.Hud(gui, root)
	uiScale = root:FindFirstChildWhichIsA("UIScale") :: UIScale

	-- XP pop-ups live in their own always-enabled gui, laid out like the bottom
	-- group, so pop-ups outside a run (protected extraction, tutorial) still show.
	local overlayRoot
	overlay, overlayRoot = Kit.Scale.HudGui("FlintbornHudOverlay", Kit.Tokens.Order("hud") + 1)
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

-- Gamepad entry to the HUD (docs/ui/HudScreen.md, "Gamepad"). ButtonSelect stays
-- on Progress, and every tile has its own button (Y, the D-pad, View), so the
-- HUD needs no menu button. The HUD never takes the selection by itself (a
-- gamepad player walks as soon as the run starts): its first tile is only
-- registered as the target for when the player enters UI navigation
-- (Kit.Input.SetHudDefault), and B hands the stick back to walking, since with
-- a control selected the stick moves the selection, not the character.
-- Windows' own B (Kit.Modal, higher priority) still closes them first.
local releaseBound = false
local remounted = Signal.new()
-- Fires after the regions are mounted again (the world ⚙ re-links to the hotbar).
HudController.Remounted = remounted

-- The form factor ("phone", "tablet", "desktop") the regions were mounted for.
local mountedForm = "desktop"
local function bindRelease(active: boolean)
	if active == releaseBound then
		return
	end
	releaseBound = active
	-- The HUD's navigation target (it is never selected here).
	Kit.Input.SetHudDefault(if active then widgets.tiles[1].control.hit else nil)
	if not active then
		ContextActionService:UnbindAction("FlintbornHudRelease")
		local selected = GuiService.SelectedObject
		if selected and selected:IsDescendantOf(gui) then
			GuiService.SelectedObject = nil
		end
		return
	end
	ContextActionService:BindActionAtPriority("FlintbornHudRelease", function(_, state)
		local selected = GuiService.SelectedObject
		if state == Enum.UserInputState.Begin and selected and selected:IsDescendantOf(gui) then
			GuiService.SelectedObject = nil
			return Enum.ContextActionResult.Sink
		end
		return Enum.ContextActionResult.Pass
	end, false, Enum.ContextActionPriority.Medium.Value, Enum.KeyCode.ButtonB)
end

local function refreshVisible()
	local visible = SessionStates.IsAtRisk(player:GetAttribute("SessionState"))
	gui.Enabled = visible
	bindHotbar(visible)
	bindRelease(visible)
	-- Re-places (or resets) the shared banner column for the new state.
	applyTop()
	HudMode.SetVisible(visible)
end

-- Rebuilds the regions when the form factor changes (Kit.Scale.
-- OnFormFactorChanged): phones arrange the HUD differently and touch screens
-- use larger text, so the regions are mounted again and refilled from the live
-- state.
local function remount()
	local popups = widgets.popups
	if widgets.bottom.stopWatching then
		widgets.bottom.stopWatching()
	end
	for _, child in root:GetChildren() do
		if not child:IsA("UIScale") then
			child:Destroy()
		end
	end
	mountedForm = Kit.Scale.FormFactor()
	widgets = HudController.Mount(root, layout, openTile)
	widgets.popups = popups
	tops = HudController.TopRegions(widgets)
	watchRegions()
	if releaseBound then
		Kit.Input.SetHudDefault(widgets.tiles[1].control.hit)
	end
	remounted:Fire()
	applyTop()
end

function HudController.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	if not HudMode.WorldHud() then
		-- No older HUD stands behind this one: say why the run has none.
		warn("[Hud] the HUD layout (Shared.UI.HudLayout) did not load; the world HUD is not built")
		return
	end
	layout = Layout.Get()
	mountedForm = Kit.Scale.FormFactor()
	build()
	applyTop()
	uiScale:GetPropertyChangedSignal("Scale"):Connect(applyTop)
	gui:GetPropertyChangedSignal("AbsoluteSize"):Connect(applyTop)
	pcall(function()
		GuiService:GetPropertyChangedSignal("TopbarInset"):Connect(applyTop)
	end)
	Kit.Scale.OnSafeInsetsChanged(applyTop)
	watchRegions()

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
		widgets.bottom:SetProgress(view, Kit.Motion.Reduced())
	end)
	ProgressionController.MountPopups(widgets.popups)

	-- Hotbar: the run inventory's hotbar items. The Hotbar1–6 binds (keys 1–6 by
	-- default) and taps select a slot and use it, as InventoryController's keys do
	-- (equip or hold, place, ready); the right gamepad bumper only steps the
	-- selection. The mouse wheel stays on camera zoom (GDD Q58). Slot badges name
	-- the bound keys and follow rebinds.
	local count = layout.bottom.hotbar.count
	local function showItems(snapshot)
		widgets.bottom:SetSlotItems(HudController.HotbarItems(snapshot, count))
		local equipped = snapshot.equipped
		if equipped and equipped ~= HudController.Selected then
			selectSlot(equipped)
		end
	end
	InventoryController.Changed:Connect(showItems)
	-- Fills freshly mounted regions (at start and after a remount).
	local function fill()
		widgets.bottom.SlotPressed:Connect(function(index)
			selectSlot(index)
			task.spawn(InventoryController.ActivateHotbar, index)
		end)
		-- Hotbar items drag to other hotbar slots, and to and from the Inventory
		-- window's cells (the same "hotbar:i" ids).
		for index, slot in widgets.bottom.slots do
			Kit.Drag.Attach(slot, {
				group = "run",
				id = function()
					return "hotbar:" .. index
				end,
				canDrop = InventoryController.CanDrop,
				onDrop = InventoryController.Drop,
			})
		end
		widgets.bottom:SetProgress(ProgressionController.View(), true)
		selectSlot(HudController.Selected)
		showItems(InventoryController.Snapshot)
		widgets.bottom:SetSlotLabels(hotbarLabels(count))
		updateHealth(true)
		updateFraction("stamina", "Stamina", true)
		updateFraction("food", "Food", true)
	end
	fill()
	remounted:Connect(function()
		fill()
		rebuildWaypoints()
	end)
	Kit.Scale.OnFormFactorChanged(function()
		if mountedForm ~= Kit.Scale.FormFactor() then
			remount()
		end
	end)
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
	-- Bars over hurt players' heads, at the HUD's scale.
	OverheadHealth.Start(function()
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
			widgets.party:Set(members, Kit.Motion.Reduced(), total)
			widgets.objective:Set(HudModel.ExtractionObjective(nearestExtraction(position)))
			local event = HudModel.WorldEvent(views, now, position and position.X, position and position.Z)
			widgets.event:Set(event, event and eventCategory(views, event.id))
		end
	end)
end

return HudController
