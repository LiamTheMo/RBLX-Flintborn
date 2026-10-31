-- A phone held sideways (844 × 390, touch only): the HUD scale × 0.9, the top bar
-- 58 px down, the Kit touch attack button beside where Roblox puts the jump
-- button, and a prompt reading TAP.
-- Built with the real scaling (Kit.Scale.Hud and HudController.PlaceTop, as
-- HudController does) and the world_hud sample data.
local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local UserInputService = game:GetService("UserInputService")
local HudModel = require(game:GetService("ReplicatedStorage").Shared.UI.HudModel)
local HudController = require(Client.Controllers.HudController)
local InteractionPrompt = require(Client.Hud.InteractionPrompt)
local Kit = require(Client.Hud.Kit)
local Layout = require(Client.Hud.Layout)

local W, H = 844, 390
local TOP_BAR = 58
local BACKGROUND = { background = "art/reference/lobby_map.png" }
workspace.CurrentCamera.ViewportSize = Vector2.new(W, H)
UserInputService.TouchEnabled = true
UserInputService.KeyboardEnabled = false
local layout = Layout.Get()

local gui, root = __screen(W, H)
local hud = HudController.Mount(root, layout, function() end)
Kit.Scale.Hud(gui, root)
local scale = root:FindFirstChildWhichIsA("UIScale").Scale
local shift = HudController.PlaceTop(HudController.TopRegions(hud), TOP_BAR / scale)
print(("world_hud_phone: scale %.3f, root %d x %d design px, top shift %d"):format(scale, W / scale, H / scale, shift))

hud.party:Set({
	{ userId = 2, name = "ForestRanger", health = 0.9 },
	{ userId = 3, name = "Mira", health = 0.46 },
}, true, 2)
local list, bearings = {}, {}
for index, waypoint in { { "mountain", -62 }, { "campfire", 18 }, { "portal", 64 } } do
	table.insert(list, { id = "w" .. index, icon = waypoint[1] })
	bearings["w" .. index] = 30 + waypoint[2]
end
hud.compass:SetWaypoints(list)
hud.compass:Update(30, bearings)
hud.vitals:Set("health", 0.85, "85/100", true)
hud.vitals:Set("stamina", 0.62, "62/100", true)
hud.vitals:Set("food", 0.48, "48/100", true)
hud.vitals:SetStatus(HudController.StatusChips(12.4, 0, false))
hud.objective:Set(
	HudModel.ExtractionObjective({ name = "Old Quarry", kind = "Fixed", distance = 1615, inZone = false, total = 120 })
)
hud.event:Set({
	title = "World Event",
	timer = "6:12",
	name = "Bloodroot Bloom",
	description = "Rare · Rare plants have sprouted · NE, 312 m",
}, "Vegetation")
hud.bottom:SetProgress({ level = 12, xp = 450, xpToNext = 750 }, true)
hud.bottom:SetSlotLabels({ "1", "2", "3", "4", "5", "6" })
hud.bottom:SetSlotItems({
	{ itemId = "StoneAxe", quantity = 1, permanent = true },
	{ itemId = "StoneSpear", quantity = 1 },
	{ itemId = "Redberry", quantity = 5 },
})
hud.bottom:Select(1)

-- The prompt at the HUD's scale near the screen's centre.
local holder = Instance.new("Frame")
holder.Name = "Prompt"
holder.BackgroundTransparency = 1
holder.Position = UDim2.new(0.55, 0, 0.55, 0)
holder.Parent = root
local drawn = InteractionPrompt.Draw(holder, { key = "TAP", action = "Gather", object = "Redberry Bush" })
holder.Size = UDim2.fromOffset(drawn.width, drawn.height)

if UserInputService.TouchEnabled then
	-- The touch attack button, as CombatController places it.
	local cfg = layout.attack
	local attack = Instance.new("Frame")
	attack.Name = "Attack"
	attack.BackgroundTransparency = 1
	Layout.Place(attack, cfg)
	attack.Parent = root
	Kit.IconButton.new(attack, { rect = { 0, 0, cfg.size[1], cfg.size[2] }, variant = "round", icon = "spear" })
end
__dump(gui, W, H, BACKGROUND)
