-- World event feed (GDD §7.1, §36.5). Every announced event shows a banner with an
-- icon, its rarity (colour and name), its direction and distance, and plays a
-- sound. Running events stay listed with their time left, and each one's area is
-- drawn as a faint circle on the ground. World place only. With the new HUD
-- (HudMode) the running list is hidden; the world event panel reads ActiveViews().

local Debris = game:GetService("Debris")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local SoundService = game:GetService("SoundService")

local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Rarity = require(ReplicatedStorage.Shared.Items.Rarity)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Signal = require(ReplicatedStorage.Shared.Core.Signal)
local HudMode = require(script.Parent.Parent.Hud.HudMode)
local Theme = require(script.Parent.Parent.Ui.Theme)

local EventFeedController = {}

EventFeedController.ALERT_SOUND = "rbxasset://sounds/electronicpingshort.wav"

local ICONS = {
	Vegetation = "🌿",
	Ore = "⛏",
	Npc = "🐺",
	Cache = "📦",
	Meteor = "☄",
	Structure = "🏚",
	Boss = "💀",
}

local COMPASS = { "E", "NE", "N", "NW", "W", "SW", "S", "SE" }

local player = Players.LocalPlayer
local ui = {}
local events = {}

-- Fires whenever an announced event starts or ends.
EventFeedController.Changed = Signal.new()

-- The server views of every running event: {id, name, rarity, category, kind,
-- position, radius, endsAt}.
function EventFeedController.ActiveViews()
	local views = {}
	for _, event in events do
		table.insert(views, event.view)
	end
	return views
end

local function make(className: string, props, parent)
	local instance = Instance.new(className)
	for key, value in props do
		instance[key] = value
	end
	instance.Parent = parent
	return instance
end

-- Compass direction and distance from the player to `position`.
local function bearing(position: Vector3): string
	local root = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
	if root == nil then
		return ""
	end
	local offset = position - root.Position
	-- Roblox's -Z is north on the placeholder island.
	local angle = math.deg(math.atan2(-offset.Z, offset.X)) % 360
	local direction = COMPASS[math.floor((angle + 22.5) / 45) % 8 + 1]
	return ("%s, %d studs"):format(direction, math.floor(Vector3.new(offset.X, 0, offset.Z).Magnitude))
end

local function title(view): string
	return ("%s %s %s"):format(ICONS[view.category] or "✦", view.rarity, view.name)
end

local function areaCircle(view)
	return make("Part", {
		Name = "EventArea",
		Anchored = true,
		CanCollide = false,
		CanQuery = false,
		CanTouch = false,
		CastShadow = false,
		Shape = Enum.PartType.Cylinder,
		Material = Enum.Material.ForceField,
		Color = Rarity.Colors[view.rarity] or Color3.new(1, 1, 1),
		Transparency = 0.7,
		Size = Vector3.new(0.2, view.radius * 2, view.radius * 2),
		CFrame = CFrame.new(view.position + Vector3.new(0, 0.3, 0)) * CFrame.Angles(0, 0, math.rad(90)),
	}, workspace.CurrentCamera)
end

local function banner(view)
	ui.banner.Text = ("%s appeared — %s"):format(title(view), bearing(view.position))
	ui.banner.TextColor3 = Rarity.Colors[view.rarity] or Color3.new(1, 1, 1)
	ui.banner.Visible = true
	local shown = ui.banner.Text
	task.delay(6, function()
		if ui.banner.Text == shown then
			ui.banner.Visible = false
		end
	end)
	local sound = make("Sound", { SoundId = EventFeedController.ALERT_SOUND, Volume = 0.8 }, SoundService)
	-- Debris cleans up even when the asset fails to load and Ended never fires.
	Debris:AddItem(sound, 5)
	sound:Play()
	Theme.Subtitle("Event alert: " .. view.rarity .. " " .. view.name)
end

local function refreshList()
	local now = workspace:GetServerTimeNow()
	local lines = {}
	for _, event in events do
		local left = math.max(0, math.floor(event.view.endsAt - now))
		table.insert(
			lines,
			("%s — %s · %d:%02d"):format(title(event.view), bearing(event.view.position), left // 60, left % 60)
		)
	end
	table.sort(lines)
	ui.list.Text = table.concat(lines, "\n")
	ui.list.Visible = #lines > 0 and not HudMode.ReplacesLegacy()
end

local function build()
	local gui = make("ScreenGui", { Name = "EventFeed", ResetOnSpawn = false }, player:WaitForChild("PlayerGui"))
	-- The banner lives in the shared top-centre column with the other banners.
	ui.banner = make("TextLabel", {
		Size = UDim2.fromOffset(520, 34),
		LayoutOrder = Theme.TopOrder.EventBanner,
		BackgroundColor3 = Color3.fromRGB(20, 18, 16),
		BackgroundTransparency = 0.15,
		TextWrapped = true,
		Font = Enum.Font.GothamBold,
		TextSize = 16,
		Visible = false,
	}, Theme.TopStack())
	make("UICorner", { CornerRadius = UDim.new(0, 8) }, ui.banner)
	ui.list = make("TextLabel", {
		Position = UDim2.fromOffset(12, 120),
		Size = UDim2.fromOffset(330, 0),
		AutomaticSize = Enum.AutomaticSize.Y,
		BackgroundColor3 = Color3.fromRGB(20, 18, 16),
		BackgroundTransparency = 0.35,
		TextXAlignment = Enum.TextXAlignment.Left,
		TextYAlignment = Enum.TextYAlignment.Top,
		TextColor3 = Color3.fromRGB(235, 226, 212),
		TextWrapped = true,
		Font = Enum.Font.GothamMedium,
		TextSize = 12,
		Visible = false,
	}, gui)
	make("UICorner", { CornerRadius = UDim.new(0, 6) }, ui.list)
	make("UIPadding", {
		PaddingTop = UDim.new(0, 4),
		PaddingBottom = UDim.new(0, 4),
		PaddingLeft = UDim.new(0, 6),
	}, ui.list)
end

function EventFeedController.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	build()
	Remotes.Get("EventAnnounced").OnClientEvent:Connect(function(view, catchUp)
		if events[view.id] then
			return
		end
		events[view.id] = { view = view, circle = areaCircle(view) }
		if not catchUp then
			banner(view)
		end
		refreshList()
		EventFeedController.Changed:Fire()
	end)
	Remotes.Get("EventEnded").OnClientEvent:Connect(function(eventId)
		local event = events[eventId]
		if event then
			events[eventId] = nil
			event.circle:Destroy()
			refreshList()
			EventFeedController.Changed:Fire()
		end
	end)
	task.spawn(function()
		while true do
			task.wait(1)
			refreshList()
		end
	end)
end

return EventFeedController
