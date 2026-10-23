-- Boss UI (GDD §8, §25.4). Shows a health bar for the nearest boss with its phase
-- and remaining pillars, the Guardian's Horn of War countdown (styled apart from
-- event and cache banners), and a clear "Legendary released" cue. World only.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local SoundService = game:GetService("SoundService")

local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Theme = require(script.Parent.Parent.Ui.Theme)

local BossUiController = {}

BossUiController.SHOW_DISTANCE = 250
BossUiController.CUE_SOUND = "rbxasset://sounds/electronicpingshort.wav"

local PHASE_TEXT = {
	Pillars = "Shielded — destroy the energy pillars",
	Gauntlet = "The shield is down",
	Final = "Legendary released — it still fights",
	Fight = "",
}

local player = Players.LocalPlayer
local ui = {}
local hornSpawnAt = nil

local function make(className: string, props, parent)
	local instance = Instance.new(className)
	for key, value in props do
		instance[key] = value
	end
	instance.Parent = parent
	return instance
end

local function cue(text: string, color: Color3)
	ui.cue.Text = text
	ui.cue.TextColor3 = color
	ui.cue.Visible = true
	task.delay(5, function()
		if ui.cue.Text == text then
			ui.cue.Visible = false
		end
	end)
	local sound = make("Sound", { SoundId = BossUiController.CUE_SOUND, Volume = 1, PlaybackSpeed = 0.7 }, SoundService)
	sound.Ended:Connect(function()
		sound:Destroy()
	end)
	sound:Play()
	Theme.Subtitle(text)
end

local function nearestBoss()
	local folder = workspace:FindFirstChild("Bosses")
	local root = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
	if folder == nil or root == nil then
		return nil
	end
	local best, bestDistance = nil, BossUiController.SHOW_DISTANCE
	for _, body in folder:GetChildren() do
		if body:IsA("BasePart") and body:GetAttribute("BossName") then
			local distance = (body.Position - root.Position).Magnitude
			if distance < bestDistance then
				best, bestDistance = body, distance
			end
		end
	end
	return best
end

local function update()
	local body = nearestBoss()
	ui.bar.Visible = body ~= nil
	if body then
		local hp, maxHp = body:GetAttribute("HP") or 0, body:GetAttribute("MaxHP") or 1
		ui.fill.Size = UDim2.fromScale(math.clamp(hp / maxHp, 0, 1), 1)
		ui.fill.BackgroundColor3 = if body:GetAttribute("Shielded")
			then Color3.fromRGB(120, 200, 255)
			else Color3.fromRGB(200, 50, 40)
		local phase = PHASE_TEXT[body:GetAttribute("Phase")] or ""
		local pillars = body:GetAttribute("PillarsLeft")
		if body:GetAttribute("Phase") == "Pillars" and pillars then
			phase ..= (" (%d left)"):format(pillars)
		end
		ui.name.Text = ("%s — %d / %d%s"):format(
			body:GetAttribute("BossName"),
			hp,
			maxHp,
			if phase ~= "" then "  ·  " .. phase else ""
		)
	end
	if hornSpawnAt then
		local left = math.max(0, math.floor(hornSpawnAt - workspace:GetServerTimeNow()))
		ui.horn.Text = ("⚔ HORN OF WAR — the Guardian rises in the Center Crater in %d:%02d"):format(
			left // 60,
			left % 60
		)
		ui.horn.Visible = left > 0
	else
		ui.horn.Visible = false
	end
end

local function build()
	local gui = make("ScreenGui", { Name = "BossUi", ResetOnSpawn = false }, player:WaitForChild("PlayerGui"))
	ui.bar = make("Frame", {
		AnchorPoint = Vector2.new(0.5, 0),
		Position = UDim2.new(0.5, 0, 0, 104),
		Size = UDim2.fromOffset(520, 38),
		BackgroundColor3 = Color3.fromRGB(20, 16, 14),
		BackgroundTransparency = 0.2,
		Visible = false,
	}, gui)
	make("UICorner", { CornerRadius = UDim.new(0, 6) }, ui.bar)
	local track = make("Frame", {
		Position = UDim2.new(0, 8, 1, -12),
		Size = UDim2.new(1, -16, 0, 6),
		BackgroundColor3 = Color3.fromRGB(60, 50, 44),
	}, ui.bar)
	ui.fill = make("Frame", { Size = UDim2.fromScale(1, 1), BorderSizePixel = 0 }, track)
	ui.name = make("TextLabel", {
		Position = UDim2.fromOffset(8, 2),
		Size = UDim2.new(1, -16, 0, 20),
		BackgroundTransparency = 1,
		TextXAlignment = Enum.TextXAlignment.Left,
		TextTruncate = Enum.TextTruncate.AtEnd,
		TextColor3 = Color3.fromRGB(250, 235, 220),
		Font = Enum.Font.GothamBold,
		TextSize = 14,
	}, ui.bar)
	ui.horn = make("TextLabel", {
		AnchorPoint = Vector2.new(0.5, 0),
		Position = UDim2.new(0.5, 0, 0, 20),
		Size = UDim2.fromOffset(600, 36),
		BackgroundColor3 = Color3.fromRGB(90, 14, 14),
		BackgroundTransparency = 0.1,
		TextColor3 = Color3.fromRGB(255, 220, 200),
		Font = Enum.Font.GothamBlack,
		TextSize = 16,
		Visible = false,
	}, gui)
	make("UICorner", { CornerRadius = UDim.new(0, 8) }, ui.horn)
	make("UIStroke", { Color = Color3.fromRGB(255, 120, 80), Thickness = 2 }, ui.horn)
	ui.cue = make("TextLabel", {
		AnchorPoint = Vector2.new(0.5, 0.5),
		Position = UDim2.fromScale(0.5, 0.3),
		Size = UDim2.fromOffset(560, 48),
		BackgroundTransparency = 1,
		Font = Enum.Font.GothamBlack,
		TextSize = 28,
		TextStrokeTransparency = 0.2,
		Visible = false,
	}, gui)
end

function BossUiController.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	build()
	Remotes.Get("BossAlert").OnClientEvent:Connect(function(payload)
		if payload.kind == "Horn" then
			hornSpawnAt = payload.spawnAt
			cue("⚔ The Horn of War sounds", Color3.fromRGB(255, 120, 80))
		elseif payload.kind == "Spawned" then
			hornSpawnAt = nil
			cue("The Guardian has risen", Color3.fromRGB(255, 120, 80))
		elseif payload.kind == "Phase" then
			cue("The Guardian's shield is down!", Color3.fromRGB(120, 200, 255))
		elseif payload.kind == "Legendary" then
			cue("★ LEGENDARY RELEASED ★", Color3.fromRGB(240, 170, 40))
		elseif payload.kind == "Ended" then
			hornSpawnAt = nil
		end
	end)
	task.spawn(function()
		while true do
			task.wait(0.25)
			update()
		end
	end)
end

return BossUiController
