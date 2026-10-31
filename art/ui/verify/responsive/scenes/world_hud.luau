-- QA: the in-world HUD as HudController builds it (Mount, Kit.Scale.Hud,
-- PlaceTop below a QA.top px top bar), the interaction prompt (TAP / E / ButtonX)
-- and, on touch, the Kit attack button where CombatController places it.
--   page 1: world_hud sample data      page 2: long strings
local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local HudModel = require(game:GetService("ReplicatedStorage").Shared.UI.HudModel)
local HudController = require(Client.Controllers.HudController)
local InteractionPrompt = require(Client.Hud.InteractionPrompt)
local Kit = require(Client.Hud.Kit)
local Layout = require(Client.Hud.Layout)

local W, H = QA.W, QA.H
local layout = Layout.Get()
local key = if QA.touch then HudModel.KeyLabel("Touch", nil)
	elseif QA.gamepad then HudModel.KeyLabel("Gamepad", "ButtonX")
	else HudModel.KeyLabel("Keyboard", "E", "E")

local function page(long)
	local gui, root = __screen(W, H)
	local hud = HudController.Mount(root, layout, function() end)
	Kit.Scale.Hud(gui, root)
	local scale = root:FindFirstChildWhichIsA("UIScale").Scale
	local shift = HudController.PlaceTop(HudController.TopRegions(hud), QA.top / scale)
	hud.party:Set({
		{ userId = 2, name = if long then "MightyWarriorQueen99" else "ForestRanger", health = 0.9 },
		{ userId = 3, name = if long then "WWWWWWWWWWWWWWWWWWWW" else "Mira", health = 0.46 },
		{ userId = 4, name = if long then "Explorer_Of_Isles_7" else "Pip", health = 0.2 },
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
	hud.vitals:SetStatus(HudController.StatusChips(12.4, if long then 3 else 0, long))
	hud.objective:Set(HudModel.ExtractionObjective({
		name = if long then "The Forgotten Quarry of the Northern Ridge" else "Old Quarry",
		kind = "Fixed",
		distance = 1615,
		inZone = false,
		total = 120,
	}))
	hud.event:Set({
		title = "World Event",
		timer = "6:12",
		name = if long then "Bloodroot Bloom of the Ancient Grove" else "Bloodroot Bloom",
		description = if long
			then "Legendary · Rare plants have sprouted across the island's eastern ridges · NE, 1312 m"
			else "Rare · Rare plants have sprouted · NE, 312 m",
	}, "Vegetation")
	hud.bottom:SetProgress({ level = if long then 100 else 12, xp = if long then 123456 else 450, xpToNext = if long then 999999 else 750 }, true)
	hud.bottom:SetSlotLabels({ "1", "2", "3", "4", "5", "6" })
	hud.bottom:SetSlotItems({
		{ itemId = "StoneAxe", quantity = 1, permanent = true },
		{ itemId = "StoneSpear", quantity = 1 },
		{ itemId = "Redberry", quantity = if long then 999 else 5 },
	})
	hud.bottom:Select(1)
	local holder = Instance.new("Frame")
	holder.Name = "Prompt"
	holder.BackgroundTransparency = 1
	holder.Position = UDim2.new(0.55, 0, 0.55, 0)
	holder.Parent = root
	local drawn = InteractionPrompt.Draw(holder, {
		key = key,
		action = if long then "Gather carefully" else "Gather",
		object = if long then "Permanent Portable Extraction Rune" else "Redberry Bush",
	})
	holder.Size = UDim2.fromOffset(drawn.width, drawn.height)
	if QA.touch then
		local cfg = layout.attack
		local attack = Instance.new("Frame")
		attack.Name = "Attack"
		attack.BackgroundTransparency = 1
		Layout.Place(attack, cfg)
		attack.Parent = root
		Kit.IconButton.new(attack, { rect = { 0, 0, cfg.size[1], cfg.size[2] }, variant = "round", icon = "spear" })
	end
	QA.report(gui, { scale = scale, shift = shift, phone = Layout.IsPhone(), smallTouch = Kit.Scale.IsSmallTouch(H) })
	__dump(gui, W, H)
end

page(false)
page(true)
