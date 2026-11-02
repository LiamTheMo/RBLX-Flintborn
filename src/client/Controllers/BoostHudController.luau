-- Active boosts (GDD §51, §25.4): one line per running berry or draught boost with
-- its strength and time left, e.g. "✦ XP +25% · 9:41 left". The server replicates
-- each boost as player attributes (ModifierService); this only counts down. Every
-- line says what it is in words, and the last 30 seconds add "ending soon" as well
-- as the warning colour. Shown only during a run. World place only. Each boost is
-- a kit notice card at the left edge whose bar shows the time left out of the
-- boost's full length (the matching draught or berry's duration).

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local BoostRules = require(ReplicatedStorage.Shared.Survival.BoostRules)
local Consumables = require(ReplicatedStorage.Shared.Items.Consumables)
local HudModel = require(ReplicatedStorage.Shared.UI.HudModel)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local SessionStates = require(ReplicatedStorage.Shared.Admission.SessionStates)
local KitScale = require(script.Parent.Parent.Hud.Kit.Scale)
local Layout = require(script.Parent.Parent.Hud.Layout)
local NoticeCard = require(script.Parent.Parent.Hud.NoticeCard)
local Theme = require(script.Parent.Parent.Ui.Theme)

local BoostHudController = {}

BoostHudController.ENDING_SECONDS = 30
BoostHudController.REFRESH_SECONDS = 0.25

BoostHudController.WIDTH = 340

-- Where the list starts on its gui (a whole-screen gui whose root draws at
-- `listScale`, the overlay scale): the HUD grid's gap right of the world ⚙ in
-- the bottom-left corner (HudModel.GearCorner, as SettingsController places
-- it; right of its touch pad where that reaches further), its foot the grid's
-- margin above the screen's bottom edge, level with the ⚙'s and the hotbar's
-- (D30). So the corner button and the boosts never cover each other.
function BoostHudController.Position(gui: GuiBase2d, listScale: number): UDim2
	local grid, gear = Layout.Grid(), Layout.Gear()
	local k = KitScale.HudScaleOf(gui)
	local margin = if grid then grid.margin else 24
	local gap = if grid then grid.gap else 12
	local size = if gear then gear.size else { 52, 46 }
	local left = margin
	if grid and gear then
		left = HudModel.GearCorner(grid, gear, KitScale.HudScreen(gui, k))
	end
	local w = size[1] * k
	local right = left * k + w + math.max(0, (if gear then gear.pad else 44) - w) / 2
	local x = right + gap * k
	return UDim2.new(0, x / listScale, 1, -margin * k / listScale)
end

local ICONS = { XP = "star", Luck = "treasure" }
local FILLS = { XP = "xp", Luck = "green" }
local NAMES = { XP = "XP", Luck = "Luck" }
local SUFFIXES = { XP = "", Luck = " rare drops" }

local player = Players.LocalPlayer
local make = Theme.Make
local ui = { rows = {} }

-- The full length of a running boost: the shortest consumable of its kind and
-- strength that lasts at least the time left when it was first seen (so a 10-
-- and a 15-minute draught of equal strength each fill the bar when fresh).
-- Remembered per boost, so the bar empties as it runs.
local lengths = {}

function BoostHudController.Length(kind: string, amount: number, left: number): number
	local best = nil
	for _, item in Consumables.Catalog do
		local boost = item.boost
		if boost and boost.kind == kind and math.abs(boost.amount - amount) < 1e-6 and boost.seconds >= left - 1 then
			best = if best then math.min(best, boost.seconds) else boost.seconds
		end
	end
	return math.max(best or left, left, 1)
end

local function build()
	local gui = make("ScreenGui", {
		Name = "Boosts",
		ResetOnSpawn = false,
		DisplayOrder = 4,
		ZIndexBehavior = Enum.ZIndexBehavior.Sibling,
	}, player:WaitForChild("PlayerGui"))
	-- The whole screen, like the HUD and its ⚙, so the list lines up with them.
	KitScale.FullScreen(gui)
	ui.gui = gui
	-- Bottom left, growing upwards beside the world ⚙: clear of the party
	-- frames and menu tiles above and of the XP bar and hotbar to the right.
	ui.root = make("Frame", {
		Name = "BoostList",
		AnchorPoint = Vector2.new(0, 1),
		Position = UDim2.new(0, 0, 1, 0),
		Size = UDim2.fromOffset(BoostHudController.WIDTH, 0),
		AutomaticSize = Enum.AutomaticSize.Y,
		BackgroundTransparency = 1,
		Visible = false,
	}, gui)
	ui.root.Parent = Theme.HudRoot(gui)
	make("UIListLayout", {
		Padding = UDim.new(0, 8),
		SortOrder = Enum.SortOrder.LayoutOrder,
		VerticalAlignment = Enum.VerticalAlignment.Bottom,
	}, ui.root)
	for order, kind in BoostRules.ORDER do
		ui.rows[kind] = NoticeCard.new(ui.root, {
			name = kind,
			width = BoostHudController.WIDTH,
			layoutOrder = order,
			title = "",
			icon = ICONS[kind] or "lightning",
		})
	end
end

local function update()
	local inRun = SessionStates.IsAtRisk(player:GetAttribute("SessionState"))
	local now = workspace:GetServerTimeNow()
	local any = false
	for kind, row in ui.rows do
		local amountName, untilName = BoostRules.Attributes(kind)
		local amount = player:GetAttribute(amountName)
		local endsAt = player:GetAttribute(untilName)
		local left = if type(amount) == "number" and type(endsAt) == "number" then endsAt - now else 0
		if inRun and left > 0 then
			any = true
			local key = ("%s:%s:%s"):format(kind, tostring(amount), tostring(endsAt))
			if lengths[kind] == nil or lengths[kind].key ~= key then
				lengths[kind] = { key = key, seconds = BoostHudController.Length(kind, amount, left) }
			end
			local ending = left <= BoostHudController.ENDING_SECONDS
			row:SetTone(if ending then "short" else "ink")
			row:SetBar(left / lengths[kind].seconds, if ending then "red" else FILLS[kind] or "xp")
			row:Show(
				("%s left%s"):format(BoostRules.FormatTime(left), if ending then " · ending soon" else ""),
				("%s %s%s"):format(NAMES[kind] or kind, BoostRules.Percent(amount), SUFFIXES[kind] or "")
			)
		else
			row:Hide()
		end
	end
	ui.root.Visible = any
	if any then
		local fit = ui.root.Parent:FindFirstChildWhichIsA("UIScale")
		ui.root.Position = BoostHudController.Position(ui.gui, if fit then fit.Scale else 1)
	end
end

function BoostHudController.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	build()
	local elapsed = 0
	RunService.Heartbeat:Connect(function(dt)
		elapsed += dt
		if elapsed >= BoostHudController.REFRESH_SECONDS then
			elapsed = 0
			update()
		end
	end)
end

return BoostHudController
