-- World event feed (GDD §7.1, §36.5). Every announced event shows a banner with an
-- icon, its rarity (colour and name), its direction and distance, and plays a
-- sound. Running events stay listed with their time left, and each one's area is
-- drawn as a faint circle on the ground. World place only. With the new HUD
-- (HudMode) the running list is hidden; the world event panel reads ActiveViews().
-- The banner is a kit toast in the shared top-centre column and the list a kit
-- notice card.

local Debris = game:GetService("Debris")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local SoundService = game:GetService("SoundService")

local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Rarity = require(ReplicatedStorage.Shared.Items.Rarity)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Signal = require(ReplicatedStorage.Shared.Core.Signal)
local HudMode = require(script.Parent.Parent.Hud.HudMode)
local Kit = require(script.Parent.Parent.Hud.Kit)
local NoticeCard = require(script.Parent.Parent.Hud.NoticeCard)
local Theme = require(script.Parent.Parent.Ui.Theme)

local EventFeedController = {}

EventFeedController.ALERT_SOUND = "rbxasset://sounds/electronicpingshort.wav"
EventFeedController.BANNER_SECONDS = 6

-- The kit icon for each event category.
EventFeedController.ICONS = {
	Vegetation = "berry_bush",
	Ore = "pickaxe",
	Npc = "paw",
	Cache = "treasure",
	Meteor = "magma_ore",
	Structure = "ruin",
	Boss = "tusk",
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
	return ("%s %s"):format(view.rarity, view.name)
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
	if ui.banner then
		ui.banner:Destroy()
	end
	local toast
	toast = Kit.Toast.new(Theme.TopStack(), {
		name = "EventBanner",
		size = { 560, 84 },
		layoutOrder = Theme.TopOrder.EventBanner,
		kind = "warn",
		icon = EventFeedController.ICONS[view.category] or "exclamation",
		title = title(view) .. " appeared",
		text = bearing(view.position),
		onClose = function()
			toast:Destroy()
			if ui.banner == toast then
				ui.banner = nil
			end
		end,
	})
	ui.banner = toast
	task.delay(EventFeedController.BANNER_SECONDS, function()
		if ui.banner == toast then
			toast:Destroy()
			ui.banner = nil
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
	if #lines > 0 and not HudMode.ReplacesLegacy() then
		ui.list:Show(table.concat(lines, "\n"))
	else
		ui.list:Hide()
	end
end

local function build()
	local gui = make("ScreenGui", {
		Name = "EventFeed",
		ResetOnSpawn = false,
		ZIndexBehavior = Enum.ZIndexBehavior.Sibling,
	}, player:WaitForChild("PlayerGui"))
	-- The running list sits at the left, under the party frames' corner.
	local holder = make("Frame", {
		Name = "Holder",
		BackgroundTransparency = 1,
		Position = UDim2.fromOffset(12, 120),
		Size = UDim2.fromOffset(400, 0),
	}, gui)
	Theme.FitHud(gui, make("UIScale", { Name = "Fit" }, holder))
	ui.list = NoticeCard.new(holder, { name = "Events", width = 400, title = "World events", icon = "map_pin" })
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
