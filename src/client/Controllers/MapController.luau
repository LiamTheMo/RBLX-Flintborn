-- Compass, map and safe-zone notice (GDD §3, §25, §54). A compass strip shows
-- your heading; the Map key (N by default; DPadDown) opens a top-down map of the
-- island with its named zones (tinted by danger tier), Crater Lake and the river,
-- landmarks, safe camps, active portals, announced events and your position.
-- Entering a safe camp shows a clear notice. World place only.

local CollectionService = game:GetService("CollectionService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local BiomeCatalog = require(ReplicatedStorage.Shared.World.BiomeCatalog)
local IslandLayout = require(ReplicatedStorage.Shared.World.IslandLayout)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local PoiCatalog = require(ReplicatedStorage.Shared.World.PoiCatalog)
local Rarity = require(ReplicatedStorage.Shared.Items.Rarity)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local HudMode = require(script.Parent.Parent.Hud.HudMode)
local Theme = require(script.Parent.Parent.Ui.Theme)
local Binds = require(script.Parent.Parent.Ui.Binds)

local MapController = {}

-- The map's largest size; it shrinks to fit short screens (positions are scale-based).
MapController.MAP_PIXELS = 420
MapController.SAFE_CHECK_SECONDS = 0.25
-- Cells per side of the zone picture (rows are merged into runs of one colour).
MapController.RESOLUTION = 64

local TIER_TEXT = {
	OuterRim = Color3.fromRGB(240, 236, 220),
	InnerRing = Color3.fromRGB(255, 214, 110),
	CenterCrater = Color3.fromRGB(255, 120, 100),
}
local WATER = Color3.fromRGB(56, 112, 160)

local player = Players.LocalPlayer
local ui = {}
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

-- World X/Z to a map position (the island square fills the map, -Z up as north).
local function toMap(position: Vector3): UDim2
	local span = BiomeCatalog.ISLAND_SIZE
	return UDim2.fromScale(0.5 + position.X / span, 0.5 + position.Z / span)
end

-- One cell's colour: its zone (darker low, lighter high), lake and river water,
-- or nil for the open sea.
local function cellColor(x: number, z: number): Color3?
	local zoneId = BiomeCatalog.ZoneAt(x, z)
	if zoneId == nil then
		return nil
	end
	if not IslandLayout.IsDry(x, z) then
		return WATER
	end
	local shade = math.clamp(math.floor(IslandLayout.HeightAt(x, z) / 60), 0, 4)
	local color = BiomeCatalog.Zones[zoneId].color
	return color:Lerp(Color3.fromRGB(250, 250, 250), shade * 0.08):Lerp(Color3.new(0, 0, 0), 0.12 - shade * 0.03)
end

-- The zone picture, drawn once: runs of equal colour per row, the river on top and
-- each zone's name at its heart.
local function drawZones()
	local cells = MapController.RESOLUTION
	local span = BiomeCatalog.ISLAND_SIZE
	local cell = span / cells
	for row = 0, cells - 1 do
		local z = -span / 2 + (row + 0.5) * cell
		local runStart, runColor = 0, nil
		for column = 0, cells do
			local color = if column < cells then cellColor(-span / 2 + (column + 0.5) * cell, z) else nil
			if color ~= runColor then
				if runColor then
					make("Frame", {
						Position = UDim2.fromScale(runStart / cells, row / cells),
						Size = UDim2.fromScale((column - runStart) / cells, 1 / cells),
						BackgroundColor3 = runColor,
						BorderSizePixel = 0,
						ZIndex = 1,
					}, ui.terrain)
				end
				runStart, runColor = column, color
			end
		end
	end
	for _, river in IslandLayout.Rivers do
		for index = 2, #river.points do
			local a, b = river.points[index - 1], river.points[index]
			local mid = (a + b) / 2
			make("Frame", {
				AnchorPoint = Vector2.new(0.5, 0.5),
				Position = toMap(mid),
				Size = UDim2.new((b - a).Magnitude / span, 2, 0, 3),
				Rotation = math.deg(math.atan2(b.Z - a.Z, b.X - a.X)),
				BackgroundColor3 = WATER,
				BorderSizePixel = 0,
				ZIndex = 2,
			}, ui.terrain)
		end
	end
	for _, zoneId in BiomeCatalog.ZONE_IDS do
		local zone = BiomeCatalog.Zones[zoneId]
		local x, z = BiomeCatalog.Center(zoneId)
		if zone.label then
			x, z = zone.label.x, zone.label.z
		end
		make("TextLabel", {
			AnchorPoint = Vector2.new(0.5, 0.5),
			Position = toMap(Vector3.new(x, 0, z)),
			Size = UDim2.fromOffset(120, 14),
			BackgroundTransparency = 1,
			Text = zone.name:upper(),
			TextColor3 = TIER_TEXT[zone.tier],
			TextStrokeTransparency = 0.2,
			Font = Enum.Font.GothamBlack,
			TextSize = 10,
			ZIndex = 2,
		}, ui.terrain)
	end
end

local function marker(parent, position: Vector3, text: string, color: Color3)
	return make("TextLabel", {
		AnchorPoint = Vector2.new(0.5, 0.5),
		Position = toMap(position),
		Size = UDim2.fromOffset(120, 16),
		BackgroundTransparency = 1,
		Text = text,
		TextColor3 = color,
		TextStrokeTransparency = 0.3,
		Font = Enum.Font.GothamBold,
		TextSize = 11,
		ZIndex = 3,
	}, parent)
end

local function renderMarkers()
	for _, child in ui.markers:GetChildren() do
		child:Destroy()
	end
	for _, entry in PoiCatalog.Landmarks do
		marker(ui.markers, PoiCatalog.Position(entry), "▲ " .. entry.name, Color3.fromRGB(240, 230, 210))
	end
	for _, entry in PoiCatalog.SafeZones do
		marker(ui.markers, PoiCatalog.Position(entry), "🛡 " .. entry.name, Color3.fromRGB(150, 200, 255))
	end
	-- Only the portals active in this world exist as portal parts.
	for _, part in workspace:GetChildren() do
		local kind = part:IsA("BasePart") and part:GetAttribute("PortalKind")
		if kind then
			marker(ui.markers, part.Position, "⟁ " .. part.Name, Color3.fromRGB(120, 220, 255))
		end
	end
	for _, view in events do
		marker(ui.markers, view.position, "✦ " .. view.name, Rarity.Colors[view.rarity] or Color3.new(1, 1, 1))
	end
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
		ui.me.Position = toMap(root.Position)
		if sinceSafeCheck >= MapController.SAFE_CHECK_SECONDS then
			sinceSafeCheck = 0
			local camp = inSafeZone(root.Position)
			ui.safe.Visible = camp ~= nil
			if camp then
				ui.safe.Text = "🛡 " .. camp .. " — safe: no damage here"
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
	ui.safe = make("TextLabel", {
		AnchorPoint = Vector2.new(0.5, 1),
		Position = UDim2.new(0.5, 0, 1, -150),
		Size = UDim2.fromOffset(340, 26),
		BackgroundColor3 = Color3.fromRGB(30, 70, 140),
		BackgroundTransparency = 0.2,
		TextColor3 = Color3.fromRGB(240, 245, 255),
		Font = Enum.Font.GothamBold,
		TextSize = 14,
		Visible = false,
	}, gui)
	make("UICorner", { CornerRadius = UDim.new(0, 6) }, ui.safe)
	ui.map = make("Frame", {
		AnchorPoint = Vector2.new(0.5, 0.5),
		Position = UDim2.fromScale(0.5, 0.5),
		Size = UDim2.fromScale(0.9, 0.9),
		BackgroundColor3 = Color3.fromRGB(34, 72, 110),
		Active = true,
		Visible = false,
	}, gui)
	make("UICorner", { CornerRadius = UDim.new(0, 10) }, ui.map)
	make("UIAspectRatioConstraint", { AspectRatio = 1 }, ui.map)
	make("UISizeConstraint", { MaxSize = Vector2.new(MapController.MAP_PIXELS, MapController.MAP_PIXELS) }, ui.map)
	local close = make("TextButton", {
		Text = "✕",
		AnchorPoint = Vector2.new(1, 0),
		Position = UDim2.new(1, -6, 0, 6),
		Size = UDim2.fromOffset(28, 24),
		BackgroundColor3 = Color3.fromRGB(70, 56, 40),
		TextColor3 = Color3.fromRGB(245, 236, 222),
		Font = Enum.Font.GothamBold,
		TextSize = 14,
		ZIndex = 5,
	}, ui.map)
	close.Activated:Connect(function()
		ui.map.Visible = false
	end)
	ui.terrain = make("Frame", {
		Size = UDim2.fromScale(1, 1),
		BackgroundTransparency = 1,
		ClipsDescendants = true,
	}, ui.map)
	make("TextLabel", {
		AnchorPoint = Vector2.new(0.5, 1),
		Position = UDim2.new(0.5, 0, 1, -4),
		Size = UDim2.fromOffset(260, 14),
		BackgroundTransparency = 1,
		RichText = true,
		Text = '<font color="#F0ECDC">Low</font> · <font color="#FFD66E">Medium</font> · <font color="#FF7864">Extreme</font>',
		TextColor3 = Color3.fromRGB(240, 236, 220),
		TextStrokeTransparency = 0.3,
		Font = Enum.Font.GothamBold,
		TextSize = 11,
		ZIndex = 5,
	}, ui.map)
	ui.markers = make("Folder", { Name = "Markers" }, ui.map)
	ui.me = make("TextLabel", {
		AnchorPoint = Vector2.new(0.5, 0.5),
		Size = UDim2.fromOffset(18, 18),
		BackgroundTransparency = 1,
		Text = "●",
		TextColor3 = Color3.fromRGB(255, 255, 255),
		TextStrokeTransparency = 0,
		Font = Enum.Font.GothamBlack,
		TextSize = 16,
		ZIndex = 4,
	}, ui.map)
end

-- Opens or closes this panel (keys, and the on-screen navigation bar).
function MapController.Toggle()
	ui.map.Visible = not ui.map.Visible
	if ui.map.Visible then
		if not ui.drawn then
			-- Drawn on first open so the island's heights are only worked out if needed.
			ui.drawn = true
			drawZones()
		end
		renderMarkers()
	end
end

function MapController.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	build()
	Remotes.Get("EventAnnounced").OnClientEvent:Connect(function(view)
		events[view.id] = view
		if ui.map.Visible then
			renderMarkers()
		end
	end)
	Remotes.Get("EventEnded").OnClientEvent:Connect(function(eventId)
		events[eventId] = nil
		if ui.map.Visible then
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
