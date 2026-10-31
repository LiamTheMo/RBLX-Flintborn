-- Boss UI (GDD §8, §25.4). Shows a health bar for the nearest boss with its phase
-- and remaining pillars, the Guardian's Horn of War countdown (styled apart from
-- event and cache banners), and a clear "Legendary released" cue. World only.
-- The bar and the horn are kit notice cards in the shared top-centre column; the
-- cue is a kit plaque across the upper screen.

local Debris = game:GetService("Debris")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local SoundService = game:GetService("SoundService")

local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Kit = require(script.Parent.Parent.Hud.Kit)
local NoticeCard = require(script.Parent.Parent.Hud.NoticeCard)
local Theme = require(script.Parent.Parent.Ui.Theme)

local BossUiController = {}

BossUiController.SHOW_DISTANCE = 250
BossUiController.CUE_SOUND = "rbxasset://sounds/electronicpingshort.wav"
BossUiController.CUE_SECONDS = 5

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

local function cue(text: string)
	if ui.cue then
		ui.cue:Destroy()
	end
	local w = math.min(Kit.Text.Width(text, "detailTitle") + 120, 900)
	ui.cueHolder.Size = UDim2.fromOffset(w, 86)
	ui.cue = Kit.Panel.new(ui.cueHolder, { name = "Cue", rect = { 0, 0, w, 86 }, variant = "plaque", text = text })
	ui.cueText = text
	task.delay(BossUiController.CUE_SECONDS, function()
		if ui.cueText == text and ui.cue then
			ui.cue:Destroy()
			ui.cue = nil
		end
	end)
	local sound = make("Sound", { SoundId = BossUiController.CUE_SOUND, Volume = 1, PlaybackSpeed = 0.7 }, SoundService)
	-- Debris cleans up even when the asset fails to load and Ended never fires.
	Debris:AddItem(sound, 5)
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
	if body then
		local hp, maxHp = body:GetAttribute("HP") or 0, body:GetAttribute("MaxHP") or 1
		local shielded = body:GetAttribute("Shielded") == true
		local phase = PHASE_TEXT[body:GetAttribute("Phase")] or ""
		local pillars = body:GetAttribute("PillarsLeft")
		if body:GetAttribute("Phase") == "Pillars" and pillars then
			phase ..= (" (%d left)"):format(pillars)
		end
		-- Shielded reads in words as well as the blue fill.
		ui.bar:SetBar(hp / maxHp, if shielded then "blue" else "red", ("%d / %d"):format(hp, maxHp))
		ui.bar:Show(phase, body:GetAttribute("BossName"))
	else
		ui.bar:Hide()
	end
	if hornSpawnAt then
		local left = math.max(0, math.floor(hornSpawnAt - workspace:GetServerTimeNow()))
		if left > 0 then
			ui.horn:Show(("The Guardian rises in the Center Crater in %d:%02d"):format(left // 60, left % 60))
		else
			ui.horn:Hide()
		end
	else
		ui.horn:Hide()
	end
end

local function build()
	local gui = make("ScreenGui", {
		Name = "BossUi",
		ResetOnSpawn = false,
		ZIndexBehavior = Enum.ZIndexBehavior.Sibling,
	}, player:WaitForChild("PlayerGui"))
	-- The bar and the horn live in the shared top-centre column with the other banners.
	local stack = Theme.TopStack()
	ui.bar = NoticeCard.new(stack, {
		name = "BossBar",
		width = 560,
		layoutOrder = Theme.TopOrder.BossBar,
		title = "",
		icon = "tusk",
	})
	ui.horn = NoticeCard.new(stack, {
		name = "Horn",
		width = 600,
		layoutOrder = Theme.TopOrder.Horn,
		title = "Horn of War",
		icon = "warning",
	})
	ui.horn:SetTone("short")
	ui.cueHolder = make("Frame", {
		Name = "CueHolder",
		AnchorPoint = Vector2.new(0.5, 0.5),
		BackgroundTransparency = 1,
		Position = UDim2.fromScale(0.5, 0.3),
		Size = UDim2.fromOffset(600, 86),
	}, gui)
	Theme.FitHud(gui, make("UIScale", { Name = "Fit" }, ui.cueHolder))
end

function BossUiController.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	build()
	Remotes.Get("BossAlert").OnClientEvent:Connect(function(payload)
		if payload.kind == "Horn" then
			hornSpawnAt = payload.spawnAt
			cue("The Horn of War sounds")
		elseif payload.kind == "Spawned" then
			hornSpawnAt = nil
			cue("The Guardian has risen")
		elseif payload.kind == "Phase" then
			cue("The Guardian's shield is down!")
		elseif payload.kind == "Legendary" then
			cue("Legendary released")
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
