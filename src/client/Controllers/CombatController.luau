-- Attack input (GDD §5.1, Q26, Q134): click, tap or right trigger. With a melee
-- weapon (or empty hands) each press sends a swing toward the aim point; with a bow
-- the press starts a draw and release fires, and a longer draw shoots farther (never
-- harder). The server decides every hit. World place only.
-- On touch screens the attack is a Kit round button beside the jump button
-- (its touch pad comes from the Kit); the hit marker is a Kit plaque and the bow
-- draw a Kit bar, at the HUD's scale.

local ContextActionService = game:GetService("ContextActionService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")

local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local WeaponCatalog = require(ReplicatedStorage.Shared.Combat.WeaponCatalog)
local DamageNumbers = require(script.Parent.Parent.Hud.DamageNumbers)
local Kit = require(script.Parent.Parent.Hud.Kit)
local Layout = require(script.Parent.Parent.Hud.Layout)
local Theme = require(script.Parent.Parent.Ui.Theme)

local CombatController = {}

-- The hit marker and draw bar, in design px from the screen centre.
CombatController.MARKER = { y = -70, w = 220, h = 46 }
CombatController.DRAW = { y = 48, w = 280, h = 36 }
-- The touch attack button when the HUD layout has no entry for it.
CombatController.ATTACK = { anchor = { 1, 1 }, pos = { 1, -300, 1, -60 }, size = { 130, 124 } }

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

local function flash(text: string, colorKey: string)
	ui.markerText:SetText(text)
	ui.markerText:SetColor(colorKey)
	ui.marker.Visible = true
	task.delay(0.6, function()
		if ui.markerText.root.Text == text then
			ui.marker.Visible = false
		end
	end)
end

local function onAttack(_, inputState)
	local profile = equippedProfile()
	if profile.kind == "Bow" then
		if inputState == Enum.UserInputState.Begin then
			drawStartedAt = os.clock()
			ui.drawBar:Set(0, true)
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
	ui.attack.Visible = active and UserInputService.TouchEnabled
	if active then
		-- No Roblox touch button: touch players press the Kit button instead.
		ContextActionService:BindAction(
			"FlintbornAttack",
			onAttack,
			false,
			Enum.UserInputType.MouseButton1,
			Enum.KeyCode.ButtonR2
		)
	else
		ContextActionService:UnbindAction("FlintbornAttack")
		drawStartedAt = nil
		ui.draw.Visible = false
	end
end

-- A design-px region centred on the screen, `y` px below the centre.
local function centred(parent: Instance, name: string, spec): Frame
	local frame = Instance.new("Frame")
	frame.Name = name
	frame.BackgroundTransparency = 1
	frame.AnchorPoint = Vector2.new(0.5, 0.5)
	frame.Position = UDim2.new(0.5, 0, 0.5, spec.y)
	frame.Size = UDim2.fromOffset(spec.w, spec.h)
	frame.Visible = false
	frame.Parent = parent
	return frame
end

local function build()
	local gui = Instance.new("ScreenGui")
	gui.Name = "Combat"
	gui.ResetOnSpawn = false
	gui.DisplayOrder = Kit.Tokens.Order("hud")
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	gui.IgnoreGuiInset = true
	pcall(function()
		gui.ScreenInsets = Enum.ScreenInsets.DeviceSafeInsets
	end)
	local root = Instance.new("Frame")
	root.Name = "Root"
	root.BackgroundTransparency = 1
	root.Size = UDim2.fromScale(1, 1)
	root.Parent = gui

	local m = CombatController.MARKER
	ui.marker = centred(root, "HitMarker", m)
	Kit.Panel.new(ui.marker, { name = "Plaque", rect = { 0, 0, m.w, m.h }, variant = "plaque", pad = 0 })
	ui.markerText = Kit.Text.new(ui.marker, {
		name = "Text",
		rect = { 14, 0, m.w - 28, m.h },
		text = "",
		role = "hudName",
		align = "Center",
		scaled = true,
		zIndex = 8,
	})

	local d = CombatController.DRAW
	ui.draw = centred(root, "Draw", d)
	ui.drawBar =
		Kit.Bar.new(ui.draw, { name = "Range", rect = { 0, 0, d.w, d.h }, fill = "xp", frame = "well", text = "" })

	local layout = Layout.Get()
	local cfg = layout and layout.attack or CombatController.ATTACK
	ui.attack = Instance.new("Frame")
	ui.attack.Name = "Attack"
	ui.attack.BackgroundTransparency = 1
	ui.attack.Visible = false
	Layout.Place(ui.attack, cfg)
	ui.attack.Parent = root
	local button = Kit.IconButton.new(ui.attack, {
		name = "Button",
		rect = { 0, 0, cfg.size[1], cfg.size[2] },
		variant = "round",
		icon = "spear",
	})
	-- Press starts the swing or the draw; release fires a drawn bow.
	local hit = button.control.hit
	hit.InputBegan:Connect(function(input)
		if
			input.UserInputType == Enum.UserInputType.Touch
			or input.UserInputType == Enum.UserInputType.MouseButton1
		then
			onAttack(nil, Enum.UserInputState.Begin)
		end
	end)
	hit.InputEnded:Connect(function(input)
		if
			input.UserInputType == Enum.UserInputType.Touch
			or input.UserInputType == Enum.UserInputType.MouseButton1
		then
			onAttack(nil, Enum.UserInputState.End)
		end
	end)
	gui.Parent = player:WaitForChild("PlayerGui")
	Kit.Scale.Hud(gui, root)
end

function CombatController.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	build()
	-- With Show Damage off the markers still confirm a hit, without the number.
	Remotes.Get("CombatFeedback").OnClientEvent:Connect(function(kind, amount, hitPosition)
		local numbers = player:GetAttribute("ShowDamage") ~= false
		if kind == "Hit" then
			flash(if numbers then "Hit " .. tostring(amount) else "Hit", "ink")
			if numbers and typeof(hitPosition) == "Vector3" and type(amount) == "number" then
				DamageNumbers.Show(hitPosition, amount)
			end
		elseif kind == "Hurt" then
			flash(if numbers then "Hurt -" .. tostring(amount) else "Hurt", "short")
		end
	end)
	RunService.RenderStepped:Connect(function()
		if drawStartedAt then
			local t = math.clamp((os.clock() - drawStartedAt) / WeaponCatalog.FULL_DRAW_SECONDS, 0, 1)
			ui.drawBar:Set(t, true)
			ui.drawBar:SetText(("Range %d%%"):format(math.round(t * 100)))
		end
	end)
	local function refresh()
		bind(player:GetAttribute("SessionState") == "ActiveRun")
	end
	player:GetAttributeChangedSignal("SessionState"):Connect(refresh)
	refresh()
end

return CombatController
