-- The in-world HUD (HudController.Mount, docs/ui/HudScreen.md) at the 1672 × 941
-- design size with sample data, over a stand-in background (the lobby village,
-- art/reference/lobby_map.png; see below).
--   1 a run in a tribe of four: three tribe-mates, the compass with waypoints,
--     vitals, a medicine lock, the extraction objective, a world event, LV 12
--     450/750 XP, the hotbar with slot 1 selected, an interaction prompt and
--     the Settings button at the bottom left
-- Laid out as the owner asked (ARCHITECTURE D28): the compass in Roblox's top
-- bar (stand-ins for its buttons drawn at the top left), the vitals in the
-- top-right corner with the objective and event under them, the tiles at the
-- left edge; the layout checks (hud_checks.luau) run on both pages.
--   2 alone: no tribe frames, no event, the objective searching, hotbar slot 3
--     selected, a hold prompt with a gamepad key, and the level cap
local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local Hud = Client.Hud
local HudModel = require(game:GetService("ReplicatedStorage").Shared.UI.HudModel)
local HudController = require(Client.Controllers.HudController)
local InteractionPrompt = require(Hud.InteractionPrompt)
local Layout = require(Hud.Layout)

local W, H = 1672, 941
-- Stand-in background: art/reference/lobby_map.png is the lobby village (the
-- repo has no in-world screenshot). The world HUD never shows in the lobby: it
-- builds only in the world place (HudMode.ReplacesLegacy) and shows only during
-- a run (SessionStates.IsAtRisk).
local BACKGROUND = { background = "art/reference/lobby_map.png" }
local layout = Layout.Get()

local function page()
	local gui, root = __screen(W, H)
	local hud = HudController.Mount(root, layout, function() end)
	local chrome = __robloxChrome(root, W, H)
	local placed = HudController.PlaceTop(
		HudController.TopRegions(hud),
		HudController.TopBar(chrome.bar, W, 1, game:GetService("GuiService").TopbarInset, 0)
	)
	print(
		("world_hud: compass top %d, centre %+d from the middle, in the bar's row: %s"):format(
			placed.compassTop,
			placed.compassX,
			tostring(placed.inRow)
		)
	)
	-- The world ⚙ as SettingsController places it (its own HUD-scaled gui in
	-- game), at the bottom left.
	local SettingsController = require(Client.Controllers.SettingsController)
	local g = SettingsController.GEAR
	local gear = require(Hud.Kit).IconButton.new(root, {
		name = "Settings",
		variant = "settings",
		size = { g.w, g.h },
		position = SettingsController.GearPosition(W, H, 1, false),
		anchorPoint = Vector2.new(0, 1),
	})
	local function check()
		__checkWorldHud({
			scene = "world_hud",
			hud = hud,
			root = root,
			W = W,
			H = H,
			k = 1,
			chrome = chrome,
			gear = gear.root,
		})
	end
	return gui, root, hud, check
end

local function prompt(root, x: number, y: number, texts)
	local holder = Instance.new("Frame")
	holder.Name = "Prompt"
	holder.BackgroundTransparency = 1
	holder.Position = UDim2.fromOffset(x, y)
	holder.Parent = root
	local drawn = InteractionPrompt.Draw(holder, texts)
	holder.Size = UDim2.fromOffset(drawn.width, drawn.height)
	return drawn
end

local function compass(hud, heading: number)
	local list, bearings = {}, {}
	for index, waypoint in
		{
			{ "mountain", -62 },
			{ "campfire", 18 },
			{ "portal", 64 },
			{ "plant_fiber", -20 },
		}
	do
		table.insert(list, { id = "w" .. index, icon = waypoint[1] })
		bearings["w" .. index] = heading + waypoint[2]
	end
	hud.compass:SetWaypoints(list)
	hud.compass:Update(heading, bearings)
end

local function hotbar(hud, items)
	hud.bottom:SetSlotLabels({ "1", "2", "3", "4", "5", "6" })
	hud.bottom:SetSlotItems(items)
end

-- 1: a run in a tribe.
do
	local _, root, hud, check = page()
	hud.party:Set({
		{ userId = 2, name = "ForestRanger", health = 0.9 },
		{ userId = 3, name = "Mira", health = 0.46 },
		{ userId = 4, name = "StoneSeeker", health = 0.18 },
	}, true, 3)
	compass(hud, 30)
	hud.vitals:Set("health", 0.85, "85/100", true)
	hud.vitals:Set("stamina", 0.62, "62/100", true)
	hud.vitals:Set("food", 0.48, "48/100", true)
	hud.vitals:SetStatus(HudController.StatusChips(12.4, 0, false))
	hud.objective:Set(HudModel.ExtractionObjective({
		name = "Old Quarry",
		kind = "Fixed",
		distance = 1615,
		inZone = false,
		total = 120,
	}))
	hud.event:Set({
		title = "World Event",
		timer = "6:12",
		name = "Bloodroot Bloom",
		description = "Rare · Prized plants have sprouted · NE, 312 m",
	}, "Vegetation")
	hud.bottom:SetProgress({ level = 12, xp = 450, xpToNext = 750 }, true)
	hotbar(hud, {
		{ itemId = "StoneAxe", quantity = 1, permanent = true },
		{ itemId = "StoneSpear", quantity = 1 },
		{ itemId = "Redberry", quantity = 5 },
	})
	hud.bottom:Select(1)
	prompt(root, 900, 520, { key = "E", action = "Gather", object = "Redberry Bush" })
	check()
	__dump(root, W, H, BACKGROUND)
end

-- 2: alone, searching, at the level cap, holding a gamepad prompt.
do
	local _, root, hud, check = page()
	hud.party:Set({}, true, 0)
	compass(hud, 205)
	hud.vitals:Set("health", 1, "100/100", true)
	hud.vitals:Set("stamina", 1, "100/100", true)
	hud.vitals:Set("food", 0.9, "90/100", true)
	hud.vitals:SetStatus({})
	hud.objective:Set(HudModel.ExtractionObjective(nil))
	hud.event:Set(nil)
	hud.bottom:SetProgress({ level = 50, xp = 0 }, true)
	hotbar(hud, {
		{ itemId = "StonePickaxe", quantity = 1 },
		{ itemId = "StoneSpear", quantity = 1 },
		{ itemId = "WoodenBow", quantity = 1 },
		{ itemId = "FlintArrow", quantity = 24 },
		{ itemId = "Workbench", quantity = 1 },
		{ itemId = "Redberry", quantity = 12 },
	})
	hud.bottom:Select(3)
	local drawn = prompt(root, 880, 520, { key = "X", action = "Open", object = "Supply Cache", hold = true })
	drawn.hold:Set(0.4, true)
	check()
	__dump(root, W, H, BACKGROUND)
end
__hudChecksDone("world_hud")
