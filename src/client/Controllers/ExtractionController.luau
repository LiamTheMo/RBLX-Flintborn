-- Extraction HUD (GDD §9, §25.3). Lists every running countdown in the world with
-- its distance and whether you are inside its zone, and confirms protection once
-- you extract. World place only. With the new HUD (HudMode) the list is hidden and
-- the objective panel shows the nearest countdown from `Events` instead. Both the
-- list and the protection notice are kit notice cards.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local ExtractionRules = require(ReplicatedStorage.Shared.Extraction.ExtractionRules)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Signal = require(ReplicatedStorage.Shared.Core.Signal)
local HudMode = require(script.Parent.Parent.Hud.HudMode)
local NoticeCard = require(script.Parent.Parent.Hud.NoticeCard)
local Theme = require(script.Parent.Parent.Ui.Theme)

local ExtractionController = {}

local player = Players.LocalPlayer
local events = {}
local ui = {}

-- Running countdowns by id ({id, name, kind, position, radius, endsAt}), read-only
-- for other controllers; Changed fires whenever one starts or ends.
ExtractionController.Events = events
ExtractionController.Changed = Signal.new()

local function build()
	local gui = Theme.Make("ScreenGui", {
		Name = "Extraction",
		ResetOnSpawn = false,
		ZIndexBehavior = Enum.ZIndexBehavior.Sibling,
	}, player:WaitForChild("PlayerGui"))
	-- The countdown list lives in the shared top-centre column with the other banners.
	ui.list = NoticeCard.new(Theme.TopStack(), {
		name = "ExtractionList",
		width = 500,
		layoutOrder = Theme.TopOrder.Extraction,
		title = "Extraction",
		icon = "portal",
	})
	local holder = Theme.Make("Frame", {
		Name = "Holder",
		AnchorPoint = Vector2.new(0.5, 0.5),
		BackgroundTransparency = 1,
		Position = UDim2.fromScale(0.5, 0.4),
		Size = UDim2.fromOffset(460, 0),
	}, gui)
	Theme.FitHud(gui, Theme.Make("UIScale", { Name = "Fit" }, holder))
	ui.protected = NoticeCard.new(holder, { name = "Protected", width = 460, title = "Protected", icon = "check" })
	ui.protected.frame.AnchorPoint = Vector2.new(0, 0.5)
	ui.protected:SetTone("toggleOn")
end

local function update()
	local root = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
	local now = workspace:GetServerTimeNow()
	local lines = {}
	for _, event in events do
		local remaining = math.max(0, math.ceil(event.endsAt - now))
		local where = ""
		if root then
			local inside = ExtractionRules.InZone(root.Position, event.position, event.radius)
			where = if inside
				then " · IN ZONE — stay alive"
				else (" · %d studs away"):format(math.floor((root.Position - event.position).Magnitude))
		end
		local bonus = event.kind == ExtractionRules.Kinds.Center and " (2× materials)" or ""
		table.insert(lines, ("%s%s — %ds%s"):format(event.name, bonus, remaining, where))
	end
	if #lines > 0 and not HudMode.ReplacesLegacy() then
		table.sort(lines)
		ui.list:Show(table.concat(lines, "\n"))
	else
		ui.list:Hide()
	end
end

function ExtractionController.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	build()
	Remotes.Get("ExtractionEvent").OnClientEvent:Connect(function(view)
		if events[view.id] == nil then
			-- The server plays a large-radius alert ping for every extraction start.
			Theme.Subtitle("Extraction alert: " .. view.name)
		end
		events[view.id] = view
		ExtractionController.Changed:Fire()
	end)
	Remotes.Get("ExtractionEnded").OnClientEvent:Connect(function(eventId)
		events[eventId] = nil
		ExtractionController.Changed:Fire()
	end)
	player:GetAttributeChangedSignal("SessionState"):Connect(function()
		if player:GetAttribute("SessionState") == "ExtractionProtected" then
			ui.protected:Show("Extracting. Returning to the lobby…")
		else
			ui.protected:Hide()
		end
	end)
	RunService.Heartbeat:Connect(update)
end

return ExtractionController
