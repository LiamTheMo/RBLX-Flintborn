-- Drives MapController headlessly: the parchment world map with the painted
-- island, camp and landmark pins, a portal and an event marker, your position,
-- zoom and close.
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
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
check(gui and gui.Enabled, "the map opens")
local window = gui.Window
local canvas = window.Map.Canvas
check(canvas:FindFirstChild("Portal" .. portal.Name) ~= nil, "active portals are marked")
check(canvas:FindFirstChild("Evente1") ~= nil, "announced events are marked")
check(canvas.You.Visible, "your position is marked")
window.ZoomIn.Press.Activated:Fire()
check(canvas.Size.X.Offset > 856, "zoom in enlarges the map")
print(__failed and "FLOW FAILED" or "FLOW OK")
window.ZoomOut.Press.Activated:Fire()
window.UIScale.Scale = 1
window.Position = UDim2.fromOffset(640, 460)
__dump(gui, 1280, 920)
MapController.Toggle()
check(not gui.Enabled, "the map closes")
if __failed then
	error("map flow failed")
end
