-- Compass, map and safe-zone notice (GDD §3, §25, §54). A compass strip shows
-- your heading; the Map key (N by default; DPadDown) opens the world map in a
-- kit window (docs/ui/ListWindows.md): the painted island (Hud/IslandMap, the
-- Journal's map) in an inset panel with zoom buttons, pins for the safe camps
-- and main landmarks, the active portals and announced events, and your
-- position, followed while zoomed in, with a legend underneath. An authored
-- map (not the generated island) shows the bare panel with its live markers.
-- Entering a safe camp shows a clear notice. World place only.

local CollectionService = game:GetService("CollectionService")
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
local Kit = require(script.Parent.Parent.Hud.Kit)
local NoticeCard = require(script.Parent.Parent.Hud.NoticeCard)
local Theme = require(script.Parent.Parent.Ui.Theme)
local Binds = require(script.Parent.Parent.Ui.Binds)

local MapController = {}

-- The window's design size, the inset panel and the map inside it.
MapController.SIZE = { 1000, 860 }
MapController.PANEL_RECT = { 28, 104, 944, 680 }
MapController.MAP_RECT = { 36, 112, 928, 664 }
-- Marker colours (kit tokens): camps on an authored map, portals.
MapController.CAMP_COLOR = "toggleOn"
MapController.PORTAL_COLOR = "blue"
MapController.SAFE_CHECK_SECONDS = 0.25

local player = Players.LocalPlayer
local ui = {}
local screen = nil
local map = nil
local window = nil
local safeCard = nil
local following = true

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
					color = Kit.Tokens.Color(MapController.CAMP_COLOR),
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
				color = Kit.Tokens.Color(MapController.PORTAL_COLOR),
			})
		end
	end
	for id, view in events do
		table.insert(markers, {
			id = "Event" .. tostring(id),
			x = view.position.X,
			z = view.position.Z,
			name = view.name,
			color = Rarity.Colors[view.rarity] or Kit.Tokens.Color("ink"),
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

	screen = Kit.Screen.new("FlintbornMap", { size = MapController.SIZE, parent = player:WaitForChild("PlayerGui") })
	window = Kit.Window.new(screen, {
		title = "Map",
		icon = "map",
		clasps = "right",
		claspYs = { 0.18, 0.9 },
		onClose = function()
			MapController.Toggle()
		end,
	})
	local v = window.base.visual
	local panel = MapController.PANEL_RECT
	Kit.Panel.new(v, { name = "MapPanel", rect = panel, variant = "inset", zIndex = 6 })
	local r = MapController.MAP_RECT
	map = IslandMap.new(v, r, {
		zIndex = 7,
		zoomButtons = {
			{ r[1] + r[3] - 70, r[2] + r[4] - 134, 58, 58 },
			{ r[1] + r[3] - 70, r[2] + r[4] - 70, 58, 58 },
		},
	})
	-- North is up: the compass in the map's top-left corner says so.
	Kit.Icon.new(v, { name = "Compass", rect = { r[1] + 12, r[2] + 12, 72, 72 }, icon = "compass", zIndex = 14 })
	-- The legend: your arrow, the pins, and the coloured live markers.
	local legend = {
		{ icon = "compass_arrow", text = "You" },
		{ icon = "map_pin", text = "Camps and landmarks" },
		{ dot = MapController.PORTAL_COLOR, text = "Portals" },
		{ dot = "glow", text = "Events (by rarity)" },
	}
	local x = panel[1] + 8
	local y = panel[2] + panel[4] + 16
	for index, entry in legend do
		if entry.icon then
			Kit.Icon.new(
				v,
				{ name = "LegendIcon" .. index, rect = { x, y + 2, 32, 32 }, icon = entry.icon, zIndex = 8 }
			)
		else
			Kit.Picture.new(v, {
				name = "LegendDot" .. index,
				rect = { x + 6, y + 8, 20, 20 },
				role = "dot.yellow",
				tint = entry.dot,
				zIndex = 8,
			})
		end
		local tw = math.ceil(Kit.Text.Width(entry.text, "rowLabel")) + 6
		Kit.Text.new(v, {
			name = "Legend" .. index,
			rect = { x + 40, y, tw, 36 },
			text = entry.text,
			role = "rowLabel",
			zIndex = 8,
		})
		x += 40 + tw + 28
	end
	screen:SetDefaultSelection(window.close.control.hit)
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
	end)
	screen:Watch()
end

-- Opens or closes this panel (keys, and the on-screen navigation bar).
function MapController.Toggle()
	-- Escape and gamepad B close it too (Kit.Modal).
	if screen:IsOpen() then
		screen:Close()
		return
	end
	renderMarkers()
	following = true
	local root = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
	if root then
		map:SetMarker(root.Position.X, root.Position.Z)
		map:Focus(root.Position.X, root.Position.Z)
	end
	screen:Open(GuiService.SelectedObject ~= nil or UserInputService.GamepadEnabled)
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
