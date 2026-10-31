-- Drives MapController headlessly: the world map in its kit window
-- (docs/ui/ListWindows.md) with the painted island, camp and landmark pins, a
-- portal and an event marker, your position, a chosen pin's name plate, zoom
-- and close.
--
--   python3 art/ui/capture/capture.py map_flow
--
-- Pages: 1 the map, 2 zoomed in on you with a pin chosen, 3 forced states,
-- 4 phone 844 × 390 (the wide phone window).

for key, widths in table.clone(__textWidths or {}) do
	__textWidths["Enum." .. key] = __textWidths["Enum." .. key] or widths
end

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local UserInputService = game:GetService("UserInputService")
workspace:SetAttribute("FlintbornPlaceRole", "World")
workspace:SetAttribute("FlintbornWorldReady", true)
workspace:SetAttribute("FlintbornGeneratedIsland", true)
local folder = Instance.new("Folder")
folder.Name = "FlintbornRemotes"
folder.Parent = ReplicatedStorage
for _, name in { "EventAnnounced", "EventEnded" } do
	local remote = Instance.new("RemoteEvent")
	remote.Name = name
	remote.Parent = folder
end
local player = Players.LocalPlayer
local character = Instance.new("Model")
local root = Instance.new("Part")
root.Name = "HumanoidRootPart"
root.Position = Vector3.new(-600, 10, 700)
root.Parent = character
player.Character = character
local portal = Instance.new("Part")
portal.Name = "East Portal"
portal.Position = Vector3.new(1400, 10, -200)
portal:SetAttribute("PortalKind", "Edge")
portal.Parent = workspace
local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local Kit = require(Client.Hud.Kit)
local MapController = require(Client.Controllers.MapController)
MapController.Start()
folder.EventAnnounced.OnClientEvent:Fire({
	id = "e1",
	name = "Meteor shower",
	rarity = "Epic",
	position = Vector3.new(300, 0, 300),
})
MapController.Toggle()
local gui = player.PlayerGui:FindFirstChild("FlintbornMap")
local function check(cond, msg)
	print((cond and "  ok " or "  FAIL ") .. msg)
	if not cond then
		__failed = true
	end
end
local function find(target: Instance?, name: string): Instance?
	return target and target:FindFirstChild(name, true)
end
local function press(component: Instance?)
	local hit = component and component:FindFirstChild("Hit")
	assert(hit, "nothing to press")
	-- Past the kit's press debounce (time only passes for real here).
	local start = os.clock()
	while os.clock() - start < 0.16 do
	end
	hit.Activated:Fire()
end

check(gui and gui.Enabled, "the map opens")
local canvas = find(gui, "Canvas")
check(canvas:FindFirstChild("Portal" .. portal.Name) ~= nil, "active portals are marked")
check(canvas:FindFirstChild("Evente1") ~= nil, "announced events are marked")
check(canvas.You.Visible, "your position is marked")
local side = canvas.Size.X.Offset
press(find(gui, "ZoomIn"))
check(canvas.Size.X.Offset > side, "zoom in enlarges the map")
check(find(gui, "ZoomIn"):GetAttribute("KitState") ~= "disabled", "zoom in stays on below the top zoom")
press(find(gui, "ZoomOut"))
check(canvas.Size.X.Offset == side, "zoom out returns")
check(find(gui, "ZoomOut"):GetAttribute("KitState") == "disabled", "zoom out is off at the widest view")
print(__failed and "FLOW FAILED" or "FLOW OK")

local W, H = 1672, 941
local function centre()
	gui.Holder.Fit.Scale = 0.98
	gui.Holder.Position = UDim2.fromOffset(W / 2, H / 2 + 26)
end
centre()
__dump(player.PlayerGui, W, H)
press(find(gui, "ZoomIn"))
local pin = canvas:FindFirstChildWhichIsA("Frame")
for _, child in canvas:GetChildren() do
	if child:GetAttribute("KitComponent") == "MapPin" then
		pin = child
		break
	end
end
press(pin)
check(find(canvas, "Label").Visible, "a chosen pin shows its name")
__dump(player.PlayerGui, W, H)
press(find(gui, "ZoomOut"))
find(gui, "ZoomIn"):SetAttribute("DebugState", "hover")
find(gui, "Close"):SetAttribute("DebugState", "pressed")
__dump(player.PlayerGui, W, H)
for _, part in player.PlayerGui:GetDescendants() do
	if part:GetAttribute("DebugState") then
		part:SetAttribute("DebugState", "")
	end
end
workspace.CurrentCamera.ViewportSize = Vector2.new(844, 390)
UserInputService.TouchEnabled = true
UserInputService.KeyboardEnabled = false
UserInputService.MouseEnabled = false
-- The screen became a phone: MapController rebuilt the window in its phone
-- arrangement (legend beside the map). Reopen it and fit it as the game does.
gui = player.PlayerGui:FindFirstChild("FlintbornMap")
check(gui ~= nil and gui:FindFirstChild("Holder") ~= nil, "a phone gets the wide map window")
if not gui:GetAttribute("KitState") or gui:GetAttribute("KitState") == "closed" then
	MapController.Toggle()
end
local size = MapController.LAYOUTS.phone.size
local k, c = Kit.Scale.WindowFit(844, 390, 58, size[1], size[2], 1)
gui.Holder.Fit.Scale = k
gui.Holder.Position = UDim2.fromOffset(c.X, c.Y)
print(("map phone: window scale %.3f"):format(k))
__dump(player.PlayerGui, 844, 390)
MapController.Toggle()
check(not gui:GetAttribute("KitState") or gui:GetAttribute("KitState") == "closed", "the map closes")
if __failed then
	error("map flow failed")
end
