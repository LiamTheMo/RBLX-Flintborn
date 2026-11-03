-- Phones held sideways (touch only): the HUD scale × 0.9, Roblox's top bar
-- 58 px down with stand-ins for its buttons, the touch jump button and the
-- thumbstick ring, the Kit touch attack button beside the jump button, and a
-- prompt reading TAP.
--   1 844 × 390, a notched iPhone (the owner's layout requests were drawn on
--     one): the device safe area keeps 47 px at each side (__NOTCHED_PHONE;
--     the notch drawn at the left, the side strips beside the middle band
--     shaded), Roblox's buttons and touch controls sit inside it
--   2 667 × 375 (a small phone without a notch: the compass moves right off
--     Roblox's buttons, Settings stands above the thumbstick ring)
--   3 2000 × 924 (a large touch screen with the desktop arrangement)
-- Built with the real scaling (Kit.Scale.Hud and HudController.PlaceTop, as
-- HudController does) and the world_hud sample data; the layout checks
-- (hud_checks.luau, ARCHITECTURE D30: the HUD grid, and the lobby's shared
-- pieces at the same screen) run on every page.
local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local UserInputService = game:GetService("UserInputService")
local HudModel = require(game:GetService("ReplicatedStorage").Shared.UI.HudModel)
local HudController = require(Client.Controllers.HudController)
local InteractionPrompt = require(Client.Hud.InteractionPrompt)
local Kit = require(Client.Hud.Kit)
local Layout = require(Client.Hud.Layout)
local SettingsController = require(Client.Controllers.SettingsController)

-- Stand-in background: art/reference/lobby_map.png is the lobby village (the
-- repo has no in-world screenshot). The world HUD never shows in the lobby: it
-- builds only in the world place (HudMode.WorldHud) and shows only during
-- a run (SessionStates.IsAtRisk).
local BACKGROUND = { background = "art/reference/lobby_map.png" }
UserInputService.TouchEnabled = true
UserInputService.KeyboardEnabled = false
local layout = Layout.Get()

local function page(W: number, H: number, insets)
	local scene = ("world_hud_phone %dx%d"):format(W, H)
	workspace.CurrentCamera.ViewportSize = Vector2.new(W, H)
	local phone = Kit.Scale.FormFactor() == "phone"
	local gui, root = __screen(W, H)
	local hud = HudController.Mount(root, layout, function() end)
	Kit.Scale.Hud(gui, root)
	local scale = root:FindFirstChildWhichIsA("UIScale").Scale
	local chrome = __robloxChrome(gui, W, H, { touch = true, insets = insets })
	local placed = __placeWorldHud(hud, W, H, scale, chrome, true)
	print(
		("%s: %s, scale %.3f, root %d x %d design px, column edges right %d / left %d design px, compass top %d (%+d from the middle), in the bar's row: %s"):format(
			scene,
			Kit.Scale.FormFactor(),
			scale,
			W / scale,
			H / scale,
			placed.right,
			placed.left,
			placed.compassTop,
			placed.compassX,
			tostring(placed.inRow)
		)
	)

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

	-- Tribe names and the prompt's lines show whole at their (phone floor) size:
	-- the strip's cells and the plaque widen for them.
	do
		local whole = true
		local function fits(label: Instance?)
			if label and label:IsA("TextLabel") and label.Text ~= "" then
				local role = label:GetAttribute("KitTextRole") or "body"
				local base = label.TextSize / Kit.Core.TextBoost(role, label.TextSize)
				if Kit.Text.Width(label.Text, role, base) > label.Size.X.Offset then
					whole = false
					print(("  FAIL %s: %q is cut (%s)"):format(scene, label.Text, label.Name))
				end
			end
		end
		for _, item in hud.party.root:GetDescendants() do
			if item.Name == "Name" then
				fits(item)
			end
		end
		fits(holder:FindFirstChild("Action", true))
		fits(holder:FindFirstChild("Object", true))
		__hudCheck(scene, whole, "tribe names and the prompt show whole")
	end

	-- The touch attack button, as CombatController places it (its own gui
	-- inside the device safe area, beside the jump button).
	local cfg = layout.attack
	local attack = Instance.new("Frame")
	attack.Name = "Attack"
	attack.BackgroundTransparency = 1
	Layout.Place(attack, cfg)
	attack.Position -= UDim2.fromOffset(chrome.insets.right / scale, chrome.insets.bottom / scale)
	attack.Parent = root
	Kit.IconButton.new(attack, { rect = { 0, 0, cfg.size[1], cfg.size[2] }, variant = "round", icon = "spear" })

	-- The stat bars' values read at 9 screen px or more and show whole.
	for _, row in hud.vitals.rows do
		local label = row.bar.label
		local role = label:GetAttribute("KitTextRole") or "value"
		local base = label.TextSize / Kit.Core.TextBoost(role, label.TextSize)
		local whole = Kit.Text.Width(label.Text, role, base) <= label.Size.X.Offset
		local px = label.TextSize * scale
		__hudCheck(
			scene,
			px >= 9 and whole,
			("%q at %.1f design px = %.1f screen px%s"):format(
				label.Text,
				label.TextSize,
				px,
				if whole then "" else " (cut)"
			)
		)
	end

	-- The world ⚙ as SettingsController places it (its own HUD-scaled gui in
	-- game): in the grid's bottom-left corner (above the thumbstick ring where
	-- the ring reaches the corner).
	local gear = __worldGear(root, W, H, scale, chrome, true)
	__checkWorldHud({
		scene = scene,
		hud = hud,
		root = root,
		W = W,
		H = H,
		k = scale,
		chrome = chrome,
		gear = gear.root,
		attack = attack,
		phone = phone,
	})
	__dump(gui, W, H, BACKGROUND)
end

page(844, 390, __NOTCHED_PHONE)
page(667, 375)
page(2000, 924)
__hudChecksDone("world_hud_phone")
