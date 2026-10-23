-- Extraction HUD (GDD §9, §25.3). Lists every running countdown in the world with
-- its distance and whether you are inside its zone, and confirms protection once
-- you extract. World place only.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local ExtractionRules = require(ReplicatedStorage.Shared.Extraction.ExtractionRules)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Theme = require(script.Parent.Parent.Ui.Theme)

local ExtractionController = {}

local player = Players.LocalPlayer
local events = {}
local ui = {}

local function make(className: string, props, parent)
	local instance = Instance.new(className)
	for key, value in props do
		instance[key] = value
	end
	instance.Parent = parent
	return instance
end

local function build()
	local gui = make("ScreenGui", { Name = "Extraction", ResetOnSpawn = false }, player:WaitForChild("PlayerGui"))
	-- The countdown list lives in the shared top-centre column with the other banners.
	ui.list = make("TextLabel", {
		Size = UDim2.fromOffset(420, 0),
		LayoutOrder = Theme.TopOrder.Extraction,
		AutomaticSize = Enum.AutomaticSize.Y,
		BackgroundColor3 = Color3.fromRGB(16, 30, 38),
		BackgroundTransparency = 0.2,
		TextColor3 = Color3.fromRGB(190, 236, 255),
		TextWrapped = true,
		Font = Enum.Font.GothamBold,
		TextSize = 15,
		Visible = false,
	}, Theme.TopStack())
	make("UICorner", { CornerRadius = UDim.new(0, 8) }, ui.list)
	make("UIPadding", { PaddingTop = UDim.new(0, 6), PaddingBottom = UDim.new(0, 6) }, ui.list)
	ui.protected = make("TextLabel", {
		AnchorPoint = Vector2.new(0.5, 0.5),
		Position = UDim2.fromScale(0.5, 0.4),
		Size = UDim2.fromOffset(420, 70),
		BackgroundColor3 = Color3.fromRGB(16, 38, 30),
		BackgroundTransparency = 0.1,
		Text = "Protected: extracting.\nReturning to the lobby…",
		TextColor3 = Color3.fromRGB(190, 255, 214),
		Font = Enum.Font.GothamBold,
		TextSize = 18,
		Visible = false,
	}, gui)
	make("UICorner", { CornerRadius = UDim.new(0, 8) }, ui.protected)
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
				then "  ✓ IN ZONE — stay alive"
				else ("  · %d studs away"):format(math.floor((root.Position - event.position).Magnitude))
		end
		local bonus = event.kind == ExtractionRules.Kinds.Center and " (2× materials)" or ""
		table.insert(lines, ("⟁ %s%s — %ds%s"):format(event.name, bonus, remaining, where))
	end
	ui.list.Visible = #lines > 0
	ui.list.Text = table.concat(lines, "\n")
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
	end)
	Remotes.Get("ExtractionEnded").OnClientEvent:Connect(function(eventId)
		events[eventId] = nil
	end)
	player:GetAttributeChangedSignal("SessionState"):Connect(function()
		ui.protected.Visible = player:GetAttribute("SessionState") == "ExtractionProtected"
	end)
	RunService.Heartbeat:Connect(update)
end

return ExtractionController
