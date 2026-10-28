-- Active boosts (GDD §51, §25.4): one line per running berry or draught boost with
-- its strength and time left, e.g. "✦ XP +25% · 9:41 left". The server replicates
-- each boost as player attributes (ModifierService); this only counts down. Every
-- line says what it is in words, and the last 30 seconds add "ending soon" as well
-- as the warning colour. Shown only during a run. World place only.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local BoostRules = require(ReplicatedStorage.Shared.Survival.BoostRules)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local SessionStates = require(ReplicatedStorage.Shared.Admission.SessionStates)
local Theme = require(script.Parent.Parent.Ui.Theme)

local BoostHudController = {}

BoostHudController.ENDING_SECONDS = 30
BoostHudController.REFRESH_SECONDS = 0.25

local SYMBOLS = { XP = "✦", Luck = "☘" }
local NAMES = { XP = "XP", Luck = "Luck" }
local SUFFIXES = { XP = "", Luck = " rare drops" }

local player = Players.LocalPlayer
local make = Theme.Make
local ui = { rows = {} }

local function build()
	local gui =
		make("ScreenGui", { Name = "Boosts", ResetOnSpawn = false, DisplayOrder = 4 }, player:WaitForChild("PlayerGui"))
	-- Left edge, mid-height: clear of the party frames above and the vitals below.
	ui.root = make("Frame", {
		Name = "Boosts",
		AnchorPoint = Vector2.new(0, 0.5),
		Position = UDim2.new(0, 16, 0.5, -40),
		Size = UDim2.fromOffset(250, 0),
		AutomaticSize = Enum.AutomaticSize.Y,
		BackgroundTransparency = 1,
		Visible = false,
	}, gui)
	make("UIListLayout", { Padding = UDim.new(0, 4), SortOrder = Enum.SortOrder.LayoutOrder }, ui.root)
	for order, kind in BoostRules.ORDER do
		local row = make("TextLabel", {
			Name = kind,
			Size = UDim2.new(1, 0, 0, 26),
			BackgroundColor3 = Theme.Colors.Card,
			BackgroundTransparency = 0.15,
			TextColor3 = Theme.Colors.Text,
			TextXAlignment = Enum.TextXAlignment.Left,
			Font = Theme.Fonts.Bold,
			TextSize = Theme.TextSize.Body,
			LayoutOrder = order,
			Visible = false,
		}, ui.root)
		make("UICorner", { CornerRadius = UDim.new(0, 6) }, row)
		make("UIPadding", { PaddingLeft = UDim.new(0, 8), PaddingRight = UDim.new(0, 8) }, row)
		ui.rows[kind] = row
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
		row.Visible = inRun and left > 0
		if row.Visible then
			any = true
			local ending = left <= BoostHudController.ENDING_SECONDS
			row.Text = ("%s %s %s%s · %s left%s"):format(
				SYMBOLS[kind] or "•",
				NAMES[kind] or kind,
				BoostRules.Percent(amount),
				SUFFIXES[kind] or "",
				BoostRules.FormatTime(left),
				if ending then " · ending soon" else ""
			)
			row.TextColor3 = if ending then Theme.Colors.Warn else Theme.Colors.Good
		end
	end
	ui.root.Visible = any
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
