-- The in-world HUD at the layout's 1672 × 941 reference size, filled with the
-- layout's preview values: party, compass with waypoints, objective, world
-- event, vitals, status pill, level/XP bar and the hotbar.
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local Hud = Client.Hud
local Layout = require(Hud.Layout)
local layout = Layout.Get()
local preview = layout.preview
local gui, root = __screen(1672, 941)
local PartyFrames = require(Hud.PartyFrames)
local Compass = require(Hud.Compass)
local ObjectivePanel = require(Hud.ObjectivePanel)
local EventPanel = require(Hud.EventPanel)
local Vitals = require(Hud.Vitals)
local BottomBar = require(Hud.BottomBar)
local party = PartyFrames.new(root, layout)
local members = {}
for index, member in preview.party do
	table.insert(members, { userId = index, name = member.name, health = member.health })
end
party:Set(members, true)
local compass = Compass.new(root, layout)
local list, bearings = {}, {}
for index, waypoint in preview.waypoints do
	table.insert(list, { id = "w" .. index, icon = waypoint.icon, size = waypoint.size })
	bearings["w" .. index] = waypoint.bearing
end
compass:SetWaypoints(list)
compass:Update(preview.heading, bearings)
local objective = ObjectivePanel.new(root, layout)
local lines = {}
for _, line in preview.objective do
	table.insert(lines, { text = line.text, distance = line.distance, progress = line.progress, done = false })
end
objective:Set({ title = "Extraction", lines = lines })
EventPanel.new(root, layout):Set(preview.event)
local vitals = Vitals.new(root, layout)
for key, value in preview.vitals do
	vitals:Set(key, value[1], value[2], true)
end
vitals:SetStatus("Medicine lock 0:12")
local bottom = BottomBar.new(root, layout)
bottom:SetSlotLabels({ "1", "2", "3", "4", "5", "6" })
bottom:SetSlotItems({
	{ name = "Stone Axe", count = "" },
	{ name = "Torch", count = "5" },
	nil,
	{ name = "Berries", count = "12" },
})
bottom:Select(1)
bottom:SetProgress({ level = 12, xp = 820, xpToNext = 1500 }, true)
local Widgets = require(Hud.Widgets)
local backpack = Instance.new("Frame")
backpack.Name = "Backpack"
backpack.BackgroundTransparency = 1
Layout.Place(backpack, layout.backpack)
backpack.Parent = root
Widgets.Sprite(layout.backpack.sprite, { Name = "Art", Size = UDim2.fromScale(1, 1) }, backpack)
-- The MENU button with its row open (HudController draws the same).
local Parchment = require(Hud.Parchment)
local HudController = require(Client.Controllers.HudController)
local cfg = layout.menu
local menu = Instance.new("Frame")
menu.Name = "Menu"
menu.BackgroundTransparency = 1
Layout.Place(menu, cfg)
menu.Parent = root
Parchment.Button("pm_button_paper", { 0, 0, cfg.size[1], cfg.size[2] }, menu, function() end, {
	label = "MENU",
	size = 22,
	inset = 14,
})
for index, entry in HudController.MENU do
	Parchment.Button("pm_button_paper", {
		cfg.size[1] + cfg.gap + (index - 1) * (cfg.item[1] + cfg.gap),
		0,
		cfg.item[1],
		cfg.item[2],
	}, menu, function() end, { label = entry[1], size = 20, inset = 14 })
end
__dump(gui, 1672, 941)
