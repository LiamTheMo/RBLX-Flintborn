-- Compass, map and safe-zone notice (GDD §3, §25, §54). A compass strip shows
-- your heading; the Map key (N by default; DPadDown) opens the parchment world
-- map: the painted island (Hud/IslandMap, the Journal's map) in the hollow map
-- frame, with pins for the safe camps and main landmarks, the active portals and
-- announced events, and your position, followed while zoomed in. An authored
-- map (not the generated island) shows plain parchment with its live markers.
-- Entering a safe camp shows a clear notice. World place only.

local CollectionService = game:GetService("CollectionService")
local ContextActionService = game:GetService("ContextActionService")
local GuiService = game:GetService("GuiService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")

local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Rarity = require(ReplicatedStorage.Shared.Items.Rarity)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local WorldState = require(ReplicatedStorage.Shared.World.WorldState)
local HudMode = require(script.Parent.Parent.Hud.HudMode)
local IslandMap = require(script.Parent.Parent.Hud.IslandMap)
local Layout = require(script.Parent.Parent.Hud.Layout)
local NoticeCard = require(script.Parent.Parent.Hud.NoticeCard)
local Parchment = require(script.Parent.Parent.Hud.Parchment)
local Widgets = require(script.Parent.Parent.Hud.Widgets)
local Theme = require(script.Parent.Parent.Ui.Theme)
local Binds = require(script.Parent.Parent.Ui.Binds)

local MapController = {}

-- The window's design size and the map inside the hollow frame's opening.
MapController.SIZE = { 900, 880 }
MapController.MAP_RECT = { 22, 44, 856, 816 }
MapController.SAFE_CHECK_SECONDS = 0.25

local player = Players.LocalPlayer
local ui = {}
local screen = nil
local map = nil
local close = nil
local safeCard = nil
local following = true

local CLOSE_ACTION = "FlintbornMapClose"
local events = {}
local safeZones = {}
local sinceSafeCheck = math.huge

local HEADINGS = { "N", "NE", "E", "SE", "S", "SW", "W", "NW" }

local function make(className: string, props, parent)
	local instance = Instance.new(className)
	for key, value in props do
		instance[key] = value
	end
	instance.Parent = parent
	return instance
end

-- The world map's live markers: authored camps, active portals and events.
local function renderMarkers()
	local markers = {}
	if not WorldState.IsGenerated() then
		-- An authored map: its own camp volumes, not the placeholder catalog.
		for zone in safeZones do
			if zone:IsA("BasePart") then
				table.insert(markers, {
					id = "Camp" .. zone.Name,
					x = zone.Position.X,
					z = zone.Position.Z,
					name = zone:GetAttribute("SafeName") or zone.Name,
					color = Layout.Color("haveEnough"),
				})
			end
		end
	end
	-- Only the portals active in this world exist as portal parts.
	for _, part in workspace:GetChildren() do
		if part:IsA("BasePart") and part:GetAttribute("PortalKind") then
			table.insert(markers, {
				id = "Portal" .. part.Name,
				x = part.Position.X,
				z = part.Position.Z,
				name = part.Name,
				color = Color3.fromRGB(40, 110, 170),
			})
		end
	end
	for id, view in events do
		table.insert(markers, {
			id = "Event" .. tostring(id),
			x = view.position.X,
			z = view.position.Z,
			name = view.name,
			color = Rarity.Colors[view.rarity] or Layout.Color("ink"),
		})
	end
	map:SetMarkers(markers)
end

local function headingText(): string
	local look = workspace.CurrentCamera.CFrame.LookVector
	local angle = math.deg(math.atan2(look.X, -look.Z)) % 360
	local index = math.floor((angle + 22.5) / 45) % 8 + 1
	return ("◄  %s  ►   %d°"):format(HEADINGS[index], math.floor(angle))
end

local function inSafeZone(position: Vector3): string?
	for zone in safeZones do
		if zone:IsA("BasePart") then
			local localPoint = zone.CFrame:PointToObjectSpace(position)
			local half = zone.Size / 2
			if
				math.abs(localPoint.X) <= half.X
				and math.abs(localPoint.Y) <= half.Y
				and math.abs(localPoint.Z) <= half.Z
			then
				return zone:GetAttribute("SafeName") or zone.Name
			end
		end
	end
	return nil
end

local function update()
	ui.compass.Text = headingText()
	local root = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
	if root then
		if screen.gui.Enabled then
			map:SetMarker(root.Position.X, root.Position.Z)
			-- Zoomed in, the map keeps you in view until you pan it yourself.
			if map.dragging then
				following = false
			end
			if following and map.zoomIndex > 1 then
				map:Focus(root.Position.X, root.Position.Z)
			end
		end
		if sinceSafeCheck >= MapController.SAFE_CHECK_SECONDS then
			sinceSafeCheck = 0
			local camp = inSafeZone(root.Position)
			if camp == nil then
				safeCard:Hide()
			elseif safeCard.text.Text ~= camp .. ": no damage here." or not safeCard:IsShown() then
				safeCard:Show(camp .. ": no damage here.", "Safe camp")
			end
		end
	end
end

-- Safe zones are cached from tag signals instead of queried every frame.
local function watchSafeZones()
	for _, zone in CollectionService:GetTagged("SafeZone") do
		safeZones[zone] = true
	end
	CollectionService:GetInstanceAddedSignal("SafeZone"):Connect(function(zone)
		safeZones[zone] = true
	end)
	CollectionService:GetInstanceRemovedSignal("SafeZone"):Connect(function(zone)
		safeZones[zone] = nil
	end)
end

local function build()
	local gui = make("ScreenGui", { Name = "Map", ResetOnSpawn = false }, player:WaitForChild("PlayerGui"))
	ui.compass = make("TextLabel", {
		Size = UDim2.fromOffset(200, 18),
		BackgroundTransparency = 0.5,
		BackgroundColor3 = Color3.fromRGB(20, 18, 16),
		TextColor3 = Color3.fromRGB(240, 230, 210),
		Font = Enum.Font.GothamBold,
		TextSize = 12,
		LayoutOrder = Theme.TopOrder.Compass,
		-- The new HUD draws its own compass strip.
		Visible = not HudMode.ReplacesLegacy(),
	}, Theme.TopStack())
	safeCard = NoticeCard.new(gui, { name = "Safe", width = 360, title = "Safe camp" })
	safeCard.frame.AnchorPoint = Vector2.new(0.5, 1)
	safeCard.frame.Position = UDim2.new(0.5, 0, 1, -150)
	safeCard:SetTone("haveEnough")

	screen = Parchment.Screen("FlintbornMap", MapController.SIZE, 20, player:WaitForChild("PlayerGui"))
	local window = screen.window
	local r = MapController.MAP_RECT
	local paper = Widgets.Make("Frame", {
		Name = "Paper",
		BackgroundColor3 = Layout.Color("paper"),
		BorderSizePixel = 0,
		Position = UDim2.fromOffset(r[1], r[2]),
		Size = UDim2.fromOffset(r[3], r[4]),
		ZIndex = 2,
	}, window)
	map = IslandMap.new(window, r, {
		zoomButtons = {
			{ r[1] + r[3] - 84, r[2] + r[4] - 160, 62, 62 },
			{ r[1] + r[3] - 84, r[2] + r[4] - 94, 62, 63 },
		},
	})
	Widgets.Sprite("pm_frame_hollow", { Name = "Frame", Size = UDim2.fromScale(1, 1), ZIndex = 9 }, window, 1)
	Widgets.Sprite("pm_compass_rose", {
		Name = "Compass",
		Position = UDim2.fromOffset(r[1] + 18, r[2] + 74),
		Size = UDim2.fromOffset(93, 117),
		ImageColor3 = Layout.Color("ink"),
		ZIndex = 9,
	}, window)
	Widgets.Sprite("pm_button_leather", {
		Name = "TitlePlate",
		Position = UDim2.fromOffset(MapController.SIZE[1] / 2 - 170, 0),
		Size = UDim2.fromOffset(340, 86),
		ZIndex = 10,
	}, window, Parchment.SliceFor("pm_button_leather", { 0, 0, 340, 86 }))
	Parchment.Text("MAP", { MapController.SIZE[1] / 2 - 120, 12, 240, 50 }, window, {
		size = 34,
		color = "cream",
		align = "Center",
		name = "Title",
		z = 11,
	})
	close = Parchment.Button("pm_button_x", { r[1] + r[3] - 78, r[2] + 64, 58, 56 }, window, function()
		MapController.Toggle()
	end, { name = "Close", pad = 6, z = 10 }).button
	-- The painting is of the generated island; an authored map shows parchment.
	task.spawn(function()
		WorldState.WaitUntilReady()
		local island = map.canvas:FindFirstChild("Island")
		if island and not WorldState.IsGenerated() then
			island.Visible = false
			for _, pin in map.pins do
				pin.frame.Visible = false
			end
		end
		paper.Visible = not WorldState.IsGenerated()
	end)
	screen:Watch()
end

-- Opens or closes this panel (keys, and the on-screen navigation bar).
function MapController.Toggle()
	if screen:IsOpen() then
		ContextActionService:UnbindAction(CLOSE_ACTION)
		local focus = GuiService.SelectedObject
		if focus and focus:IsDescendantOf(screen.gui) then
			GuiService.SelectedObject = nil
		end
		screen:SetOpen(false)
		return
	end
	renderMarkers()
	following = true
	local root = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
	if root then
		map:SetMarker(root.Position.X, root.Position.Z)
		map:Focus(root.Position.X, root.Position.Z)
	end
	screen:SetOpen(true)
	ContextActionService:BindAction(CLOSE_ACTION, function(_, state)
		if state == Enum.UserInputState.Begin then
			MapController.Toggle()
		end
		return Enum.ContextActionResult.Sink
	end, false, Enum.KeyCode.ButtonB)
	if GuiService.SelectedObject ~= nil or UserInputService.GamepadEnabled then
		GuiService.SelectedObject = close
	end
end

function MapController.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	build()
	Remotes.Get("EventAnnounced").OnClientEvent:Connect(function(view)
		events[view.id] = view
		if screen:IsOpen() then
			renderMarkers()
		end
	end)
	Remotes.Get("EventEnded").OnClientEvent:Connect(function(eventId)
		events[eventId] = nil
		if screen:IsOpen() then
			renderMarkers()
		end
	end)
	Binds.Bind("Map", function(_, state)
		if state == Enum.UserInputState.Begin then
			MapController.Toggle()
		end
		return Enum.ContextActionResult.Pass
	end)
	watchSafeZones()
	RunService.RenderStepped:Connect(function(dt)
		sinceSafeCheck += dt
		update()
	end)
end

return MapController
