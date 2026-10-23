-- Compass, map and safe-zone notice (GDD §3, §25). A compass strip shows your
-- heading; N (or DPadDown) opens a top-down map of the Shattered Crater with its
-- three regions, landmarks, safe camps, active portals, announced events and your
-- position. Entering a safe camp shows a clear notice. World place only.

local CollectionService = game:GetService("CollectionService")
local ContextActionService = game:GetService("ContextActionService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local BiomeCatalog = require(ReplicatedStorage.Shared.World.BiomeCatalog)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local PoiCatalog = require(ReplicatedStorage.Shared.World.PoiCatalog)
local Rarity = require(ReplicatedStorage.Shared.Items.Rarity)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)

local MapController = {}

MapController.MAP_PIXELS = 420

local player = Players.LocalPlayer
local ui = {}
local events = {}

local HEADINGS = { "N", "NE", "E", "SE", "S", "SW", "W", "NW" }

local function make(className: string, props, parent)
	local instance = Instance.new(className)
	for key, value in props do
		instance[key] = value
	end
	instance.Parent = parent
	return instance
end

-- World X/Z to map pixels (the island centre in the middle, -Z up as north).
local function toMap(position: Vector3): UDim2
	local scale = MapController.MAP_PIXELS / (BiomeCatalog.MAP_RADIUS * 2)
	return UDim2.fromOffset(
		MapController.MAP_PIXELS / 2 + position.X * scale,
		MapController.MAP_PIXELS / 2 + position.Z * scale
	)
end

local function ring(radius: number, color: Color3)
	local size = radius * 2 * MapController.MAP_PIXELS / (BiomeCatalog.MAP_RADIUS * 2)
	local circle = make("Frame", {
		AnchorPoint = Vector2.new(0.5, 0.5),
		Position = UDim2.fromScale(0.5, 0.5),
		Size = UDim2.fromOffset(size, size),
		BackgroundColor3 = color,
	}, ui.map)
	make("UICorner", { CornerRadius = UDim.new(0.5, 0) }, circle)
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
		if entry.style ~= "Ridge" then
			marker(ui.markers, PoiCatalog.Position(entry), "▲ " .. entry.name, Color3.fromRGB(240, 230, 210))
		end
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
	for _, zone in CollectionService:GetTagged("SafeZone") do
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
		local camp = inSafeZone(root.Position)
		ui.safe.Visible = camp ~= nil
		if camp then
			ui.safe.Text = "🛡 " .. camp .. " — safe: no damage here"
		end
	end
end

local function build()
	local gui = make("ScreenGui", { Name = "Map", ResetOnSpawn = false }, player:WaitForChild("PlayerGui"))
	ui.compass = make("TextLabel", {
		AnchorPoint = Vector2.new(0.5, 0),
		Position = UDim2.new(0.5, 0, 0, 2),
		Size = UDim2.fromOffset(200, 18),
		BackgroundTransparency = 0.5,
		BackgroundColor3 = Color3.fromRGB(20, 18, 16),
		TextColor3 = Color3.fromRGB(240, 230, 210),
		Font = Enum.Font.GothamBold,
		TextSize = 12,
	}, gui)
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
		Size = UDim2.fromOffset(MapController.MAP_PIXELS, MapController.MAP_PIXELS),
		BackgroundColor3 = Color3.fromRGB(40, 90, 130),
		Visible = false,
	}, gui)
	make("UICorner", { CornerRadius = UDim.new(0, 10) }, ui.map)
	ring(BiomeCatalog.Regions.OuterRim.outer, Color3.fromRGB(104, 150, 74))
	ring(BiomeCatalog.Regions.InnerRing.outer, Color3.fromRGB(58, 112, 52))
	ring(BiomeCatalog.Regions.CenterCrater.outer, Color3.fromRGB(70, 56, 52))
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
	ContextActionService:BindAction("FlintbornMap", function(_, state)
		if state == Enum.UserInputState.Begin then
			MapController.Toggle()
		end
		return Enum.ContextActionResult.Pass
	end, false, Enum.KeyCode.N, Enum.KeyCode.DPadDown)
	RunService.RenderStepped:Connect(update)
end

return MapController
