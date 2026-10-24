-- Survival HUD (GDD §11, §4.5): health, stamina and food bars with numbers, the
-- medicine cooldown and pending food healing. Consumables are used from the hotbar
-- (InventoryController). Low states use text and a symbol, not colour alone.
-- World place only. The new HUD (HudController) replaces these bars when HudMode
-- says so, including the medicine and food-healing status; this stays as the
-- fallback for a place published without the HUD layout.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local GameConstants = require(ReplicatedStorage.Shared.GameConstants)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local SessionStates = require(ReplicatedStorage.Shared.Admission.SessionStates)
local HudMode = require(script.Parent.Parent.Hud.HudMode)

local SurvivalHudController = {}

local player = Players.LocalPlayer
local ui = {}

local function make(className: string, props, parent)
	local instance = Instance.new(className)
	for key, value in props do
		instance[key] = value
	end
	instance.Parent = parent
	return instance
end

local function bar(name: string, color: Color3, order: number, parent)
	local holder = make("Frame", {
		Name = name,
		Size = UDim2.new(1, 0, 0, 22),
		BackgroundColor3 = Color3.fromRGB(30, 26, 22),
		LayoutOrder = order,
	}, parent)
	make("UICorner", { CornerRadius = UDim.new(0, 4) }, holder)
	local fill = make("Frame", { Size = UDim2.fromScale(1, 1), BackgroundColor3 = color }, holder)
	make("UICorner", { CornerRadius = UDim.new(0, 4) }, fill)
	local text = make("TextLabel", {
		Size = UDim2.fromScale(1, 1),
		BackgroundTransparency = 1,
		TextColor3 = Color3.fromRGB(255, 250, 240),
		TextStrokeTransparency = 0.5,
		Font = Enum.Font.GothamBold,
		TextSize = 13,
	}, holder)
	return { fill = fill, text = text }
end

local function update()
	local inRun = SessionStates.IsAtRisk(player:GetAttribute("SessionState"))
	ui.root.Visible = inRun
	if not inRun then
		return
	end
	local humanoid = player.Character and player.Character:FindFirstChildOfClass("Humanoid")
	local health = humanoid and humanoid.Health or 0
	local maxHealth = humanoid and humanoid.MaxHealth or GameConstants.BASE_MAX_HEALTH
	ui.health.fill.Size = UDim2.fromScale(math.clamp(health / maxHealth, 0, 1), 1)
	ui.health.text.Text = ("♥ Health %d / %d"):format(math.ceil(health), maxHealth)

	local stamina = player:GetAttribute("Stamina") or 1
	ui.stamina.fill.Size = UDim2.fromScale(stamina, 1)
	ui.stamina.text.Text = ("⚡ Stamina %d%%%s"):format(
		math.round(stamina * 100),
		player:GetAttribute("Crouching") and " · crouching" or ""
	)

	local food = player:GetAttribute("Food") or 1
	ui.food.fill.Size = UDim2.fromScale(food, 1)
	local slowed = GameConstants.IsFoodSlowed(food)
	ui.food.text.Text = ("🍖 Food %d%%%s"):format(math.round(food * 100), slowed and " · ! slowed" or "")

	local lockLeft = (player:GetAttribute("MedicineLockUntil") or 0) - workspace:GetServerTimeNow()
	local healing = player:GetAttribute("FoodHealing") or 0
	local status = {}
	if lockLeft > 0 then
		table.insert(status, ("Medicine ready in %.1f s"):format(lockLeft))
	end
	if healing > 0 then
		table.insert(status, ("Food healing +%d"):format(healing))
	end
	ui.status.Text = table.concat(status, "  ·  ")
end

local function build()
	local gui = make("ScreenGui", { Name = "SurvivalHud", ResetOnSpawn = false }, player:WaitForChild("PlayerGui"))
	ui.root = make("Frame", {
		AnchorPoint = Vector2.new(0, 1),
		Position = UDim2.new(0, 16, 1, -48),
		Size = UDim2.fromOffset(320, 100),
		BackgroundTransparency = 1,
		Visible = false,
	}, gui)
	make("UIListLayout", { Padding = UDim.new(0, 4), SortOrder = Enum.SortOrder.LayoutOrder }, ui.root)
	ui.health = bar("Health", Color3.fromRGB(176, 52, 44), 1, ui.root)
	ui.stamina = bar("Stamina", Color3.fromRGB(196, 160, 48), 2, ui.root)
	ui.food = bar("Food", Color3.fromRGB(118, 150, 62), 3, ui.root)
	ui.status = make("TextLabel", {
		Size = UDim2.new(1, 0, 0, 18),
		BackgroundTransparency = 1,
		TextColor3 = Color3.fromRGB(240, 232, 220),
		TextXAlignment = Enum.TextXAlignment.Left,
		Font = Enum.Font.Gotham,
		TextSize = 13,
		LayoutOrder = 4,
	}, ui.root)
end

function SurvivalHudController.Start()
	if not PlaceConfig.IsWorld() or HudMode.ReplacesLegacy() then
		return
	end
	build()
	RunService.RenderStepped:Connect(update)
end

return SurvivalHudController
