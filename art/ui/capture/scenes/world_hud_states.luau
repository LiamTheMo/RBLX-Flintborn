-- The in-world HUD's states at 1672 × 941 with sample data:
--   1 low health (warning mark, pulsing heart), stamina spent, hungry (food
--     low, the hunger slow and food healing plaques), the objective reached
--     with its hold running, one tribe-mate down to almost nothing
--   2 every pressable part forced through DebugState: tiles hover, pressed,
--     focused, disabled; hotbar slots selected, hover, pressed, disabled,
--     locked, empty
--   3 the objective completed and an event ending, all tiles and slots selected
local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local HudModel = require(game:GetService("ReplicatedStorage").Shared.UI.HudModel)
local HudController = require(Client.Controllers.HudController)
local Layout = require(Client.Hud.Layout)

local W, H = 1672, 941
-- Stand-in background: art/reference/lobby_map.png is the lobby village (the
-- repo has no in-world screenshot). The world HUD never shows in the lobby: it
-- builds only in the world place (HudMode.ReplacesLegacy) and shows only during
-- a run (SessionStates.IsAtRisk).
local BACKGROUND = { background = "art/reference/lobby_map.png" }
local layout = Layout.Get()

local function check(cond, msg)
	print((cond and "  ok " or "  FAIL ") .. msg)
	if not cond then
		__failed = true
	end
end

local function page()
	local gui, root = __screen(W, H)
	local hud = HudController.Mount(root, layout, function() end)
	hud.bottom:SetSlotLabels({ "1", "2", "3", "4", "5", "6" })
	hud.bottom:SetProgress({ level = 7, xp = 120, xpToNext = 400 }, true)
	hud.compass:SetWaypoints({})
	hud.compass:Update(270, {})
	return gui, root, hud
end

-- 1: low vitals.
do
	local _, root, hud = page()
	hud.party:Set({ { userId = 5, name = "RiverFox", health = 0.06 } }, true, 1)
	hud.vitals:Set("health", 0.18, "18/100", true)
	hud.vitals:Set("stamina", 0, "0/100", true)
	hud.vitals:Set("food", 0.12, "12/100", true)
	hud.vitals:SetStatus(HudController.StatusChips(0, 8, true))
	check(hud.vitals.rows.health.bar.root:GetAttribute("HudLow") == true, "health 18% reads low")
	check(hud.vitals.rows.health.mark.root.Visible, "the low mark shows over the heart")
	check(hud.vitals.rows.stamina.mark.root.Visible, "spent stamina shows the mark")
	check(#hud.vitals.chips == 2, "hunger slow and food healing plaques")
	hud.objective:Set(HudModel.ExtractionObjective({
		name = "Old Quarry",
		kind = "Fixed",
		distance = 4,
		inZone = true,
		remaining = 75,
		total = 120,
	}))
	check(hud.objective.rows[1].check.checked and not hud.objective.rows[2].check.checked, "reached, hold running")
	hud.event:Set(nil)
	hud.bottom:SetSlotItems({ { itemId = "StoneAxe", quantity = 1 }, false, { itemId = "Redberry", quantity = 2 } })
	hud.bottom:Select(3)
	hud.vitals:Set("health", 0.6, "60/100", true)
	check(not hud.vitals.rows.health.mark.root.Visible, "the mark clears when health recovers")
	hud.vitals:Set("health", 0.18, "18/100", true)
	__dump(root, W, H, BACKGROUND)
end

-- 2: forced states.
do
	local _, root, hud = page()
	hud.party:Set({}, true, 0)
	hud.vitals:Set("health", 1, "100/100", true)
	hud.vitals:Set("stamina", 0.8, "80/100", true)
	hud.vitals:Set("food", 0.7, "70/100", true)
	hud.vitals:SetStatus({})
	hud.objective:Set(HudModel.ExtractionObjective(nil))
	hud.event:Set(nil)
	hud.bottom:SetSlotItems({
		{ itemId = "StoneAxe", quantity = 1 },
		{ itemId = "StoneSpear", quantity = 1 },
		{ itemId = "StonePickaxe", quantity = 1 },
		{ itemId = "Redberry", quantity = 9 },
		{ itemId = "FlintArrow", quantity = 30 },
	})
	local tileStates = { "hover", "pressed", "focused", "disabled", "normal", "selected" }
	for index, tile in hud.tiles do
		tile.root:SetAttribute("DebugState", tileStates[index])
		check(tile.root:GetAttribute("KitState") == tileStates[index], tile.root.Name .. " draws " .. tileStates[index])
	end
	local slotStates = { "selected", "hover", "pressed", "disabled", "locked", "empty" }
	for index, slot in hud.bottom.slots do
		slot.root:SetAttribute("DebugState", slotStates[index])
		check(
			slot.root:GetAttribute("KitState") == slotStates[index],
			"slot " .. index .. " draws " .. slotStates[index]
		)
	end
	__dump(root, W, H, BACKGROUND)
end

-- 3: done and ending.
do
	local _, root, hud = page()
	hud.party:Set({
		{ userId = 2, name = "ForestRanger", health = 1 },
		{ userId = 3, name = "AVeryLongDisplayName_42", health = 0.5 },
	}, true, 5)
	hud.vitals:Set("health", 0.5, "50/100", true)
	hud.vitals:Set("stamina", 0.5, "50/100", true)
	hud.vitals:Set("food", 0.5, "50/100", true)
	hud.vitals:SetStatus(HudController.StatusChips(3.2, 15, false))
	hud.objective:Set(HudModel.ExtractionObjective({
		name = "Crater Heart",
		kind = "Center",
		distance = 2,
		inZone = true,
		remaining = 0,
		total = 120,
	}))
	check(hud.objective.rows[1].check.checked and hud.objective.rows[2].check.checked, "both tasks done")
	hud.event:Set({
		title = "World Event",
		timer = "0:09",
		name = "The Ashen Guardian",
		description = "Legendary · A Guardian has awoken · SW, 1.2 km  (+2 more)",
	}, "Boss")
	hud.bottom:SetSlotItems({})
	hud.bottom:Select(6)
	__dump(root, W, H, BACKGROUND)
end
