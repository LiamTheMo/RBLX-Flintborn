-- Attack input (GDD §5.1, Q26, Q134): click, tap or right trigger. With a melee
-- weapon (or empty hands) each press sends a swing toward the aim point; with a bow
-- the press starts a draw and release fires, and a longer draw shoots farther (never
-- harder). The server decides every hit. World place only.

local ContextActionService = game:GetService("ContextActionService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local WeaponCatalog = require(ReplicatedStorage.Shared.Combat.WeaponCatalog)
local Theme = require(script.Parent.Parent.Ui.Theme)

local CombatController = {}

local player = Players.LocalPlayer
local mouse = player:GetMouse()
local sequence = 0
local drawStartedAt = nil
local ui = {}

local function nextSequence(): number
	sequence += 1
	return sequence
end

local function equippedProfile()
	local catalogId = player:GetAttribute("EquippedItem")
	local def = catalogId and ItemCatalog.Get(catalogId)
	return WeaponCatalog.For(def and def.family == ItemCatalog.Families.Weapon and catalogId or nil)
end

-- Aim from the head toward the mouse on desktop, or along the camera elsewhere.
local function aimDirection(): Vector3
	local head = player.Character and player.Character:FindFirstChild("Head")
	if head and Theme.UsingMouse() then
		local direction = mouse.Hit.Position - head.Position
		if direction.Magnitude > 0.5 then
			return direction.Unit
		end
	end
	return workspace.CurrentCamera.CFrame.LookVector
end

local function flash(text: string, color: Color3)
	ui.marker.Text = text
	ui.marker.TextColor3 = color
	ui.marker.Visible = true
	task.delay(0.6, function()
		if ui.marker.Text == text then
			ui.marker.Visible = false
		end
	end)
end

local function onAttack(_, inputState)
	local profile = equippedProfile()
	if profile.kind == "Bow" then
		if inputState == Enum.UserInputState.Begin then
			drawStartedAt = os.clock()
			ui.draw.Visible = true
		elseif inputState == Enum.UserInputState.End and drawStartedAt then
			local held = os.clock() - drawStartedAt
			drawStartedAt = nil
			ui.draw.Visible = false
			Remotes.Get("Shoot"):FireServer(nextSequence(), held, aimDirection())
		end
	elseif inputState == Enum.UserInputState.Begin then
		Remotes.Get("Attack"):FireServer(nextSequence(), aimDirection())
	end
	return Enum.ContextActionResult.Pass
end

local function bind(active: boolean)
	if active then
		ContextActionService:BindAction(
			"FlintbornAttack",
			onAttack,
			true,
			Enum.UserInputType.MouseButton1,
			Enum.KeyCode.ButtonR2
		)
		ContextActionService:SetTitle("FlintbornAttack", "Attack")
	else
		ContextActionService:UnbindAction("FlintbornAttack")
		drawStartedAt = nil
	end
end

local function build()
	local gui = Instance.new("ScreenGui")
	gui.Name = "Combat"
	gui.ResetOnSpawn = false
	gui.Parent = player:WaitForChild("PlayerGui")
	ui.marker = Instance.new("TextLabel")
	ui.marker.AnchorPoint = Vector2.new(0.5, 0.5)
	ui.marker.Position = UDim2.new(0.5, 0, 0.5, -60)
	ui.marker.Size = UDim2.fromOffset(200, 30)
	ui.marker.BackgroundTransparency = 1
	ui.marker.Font = Enum.Font.GothamBlack
	ui.marker.TextSize = 22
	ui.marker.TextStrokeTransparency = 0.4
	ui.marker.Visible = false
	ui.marker.Parent = gui
	ui.draw = Instance.new("TextLabel")
	ui.draw.AnchorPoint = Vector2.new(0.5, 0.5)
	ui.draw.Position = UDim2.new(0.5, 0, 0.5, 40)
	ui.draw.Size = UDim2.fromOffset(240, 24)
	ui.draw.BackgroundTransparency = 1
	ui.draw.Font = Enum.Font.GothamBold
	ui.draw.TextSize = 16
	ui.draw.TextColor3 = Color3.fromRGB(255, 236, 200)
	ui.draw.TextStrokeTransparency = 0.4
	ui.draw.Visible = false
	ui.draw.Parent = gui
end

function CombatController.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	build()
	Remotes.Get("CombatFeedback").OnClientEvent:Connect(function(kind, amount)
		if kind == "Hit" then
			flash("✕ Hit " .. tostring(amount), Color3.fromRGB(255, 220, 120))
		elseif kind == "Hurt" then
			flash("! -" .. tostring(amount), Color3.fromRGB(255, 120, 100))
		end
	end)
	game:GetService("RunService").RenderStepped:Connect(function()
		if drawStartedAt then
			local t = math.clamp((os.clock() - drawStartedAt) / WeaponCatalog.FULL_DRAW_SECONDS, 0, 1)
			ui.draw.Text = ("Drawing: range %d%%"):format(math.round(t * 100))
		end
	end)
	local function refresh()
		bind(player:GetAttribute("SessionState") == "ActiveRun")
	end
	player:GetAttributeChangedSignal("SessionState"):Connect(refresh)
	refresh()
end

return CombatController
