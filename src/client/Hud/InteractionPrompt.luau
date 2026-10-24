-- Custom ProximityPrompt look (GDD §11): the game's prompts switch to
-- Style = Custom on this client, and each shown prompt draws a rope-framed
-- panel with a keycap (the prompt's key, the gamepad button, or TAP), ActionText
-- as the title and ObjectText as the subtitle, plus a hold bar for timed prompts.
-- Touch and click call InputHoldBegin/End; the server still validates every
-- trigger. Roblox re-shows a prompt with the new input type when the player
-- switches input, so the keycap follows keyboard, gamepad and touch. Binds
-- retargets prompts authored on E to the player's Interact key (F by default,
-- GDD §46), and the keycap redraws whenever that key is rebound.

local Players = game:GetService("Players")
local ProximityPromptService = game:GetService("ProximityPromptService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")

local HudModel = require(ReplicatedStorage.Shared.UI.HudModel)
local Binds = require(script.Parent.Parent.Ui.Binds)
local Layout = require(script.Parent.Layout)
local Widgets = require(script.Parent.Widgets)

local InteractionPrompt = {}

local player = Players.LocalPlayer
local shown = {}

local function adorneeFor(prompt: ProximityPrompt): Instance?
	local parent = prompt.Parent
	if parent == nil then
		return nil
	end
	if parent:IsA("BasePart") or parent:IsA("Attachment") then
		return parent
	end
	if parent:IsA("Model") then
		return parent.PrimaryPart or parent:FindFirstChildWhichIsA("BasePart", true)
	end
	return parent:FindFirstAncestorWhichIsA("BasePart")
end

-- Only prompts the custom panel can attach to (a part or attachment to adorn)
-- switch to Custom; any other stays on Roblox's default look so it never vanishes.
local function adopt(instance: Instance)
	if instance:IsA("ProximityPrompt") and adorneeFor(instance) ~= nil then
		instance.Style = Enum.ProximityPromptStyle.Custom
	end
end

local function keyName(prompt: ProximityPrompt, inputType: Enum.ProximityPromptInputType): string
	if inputType == Enum.ProximityPromptInputType.Touch then
		return HudModel.KeyLabel("Touch", nil)
	elseif inputType == Enum.ProximityPromptInputType.Gamepad then
		return HudModel.KeyLabel("Gamepad", prompt.GamepadKeyCode.Name)
	end
	-- Binds keeps KeyboardKeyCode on the current Interact key (or a second
	-- choice's own key), so the keycap reads the prompt's live key.
	local interact = Binds.Key("Interact")
	return HudModel.KeyLabel("Keyboard", prompt.KeyboardKeyCode.Name, interact and interact.Name)
end

local function build(prompt: ProximityPrompt, inputType: Enum.ProximityPromptInputType, scale: number)
	local cfg = Layout.Get().prompt
	local width, height = cfg.size[1], cfg.size[2]
	local adornee = adorneeFor(prompt)
	if adornee == nil then
		return nil
	end
	local billboard = Widgets.Make("BillboardGui", {
		Name = "FlintbornPrompt",
		Adornee = adornee,
		AlwaysOnTop = true,
		Active = true,
		ResetOnSpawn = false,
		ZIndexBehavior = Enum.ZIndexBehavior.Sibling,
		Size = UDim2.fromOffset(width * scale, height * scale),
		StudsOffset = Vector3.new(cfg.studsOffset[1], cfg.studsOffset[2], cfg.studsOffset[3]),
		LightInfluence = 0,
	})
	local content = Widgets.Make("Frame", {
		Name = "Content",
		BackgroundTransparency = 1,
		Size = UDim2.fromOffset(width, height),
	}, billboard)
	Widgets.Make("UIScale", { Scale = scale }, content)
	Widgets.Panel(cfg, { Name = "Panel", Size = UDim2.fromOffset(width, height) }, content)
	-- A cool-white keycap on a dark rounded backing plate.
	local plate = Widgets.Make("Frame", {
		Name = "KeyPlate",
		BackgroundColor3 = Layout.Color(cfg.plate.color),
		BackgroundTransparency = cfg.plate.transparency,
		BorderSizePixel = 0,
		Position = Layout.Position(cfg.plate.rect),
		Size = Layout.Size(cfg.plate.rect),
		ZIndex = 4,
	}, content)
	Widgets.Make("UICorner", { CornerRadius = UDim.new(0, 9) }, plate)
	local keycap = Widgets.Make("Frame", {
		Name = "Keycap",
		BackgroundColor3 = Color3.new(1, 1, 1),
		BorderSizePixel = 0,
		Position = Layout.Position(cfg.keycap.rect),
		Size = Layout.Size(cfg.keycap.rect),
		ZIndex = 5,
	}, content)
	Widgets.Make("UICorner", { CornerRadius = UDim.new(0, 7) }, keycap)
	Widgets.Make("UIGradient", {
		Rotation = 90,
		Color = ColorSequence.new(Layout.Color("keycap"), Layout.Color("keycapShade")),
	}, keycap)
	local key = Widgets.Text(cfg.keycap, {
		Name = "Key",
		Size = UDim2.fromScale(1, 1),
		TextXAlignment = Enum.TextXAlignment.Center,
		TextStrokeTransparency = 1,
		TextScaled = false,
		ZIndex = 6,
	}, keycap)
	local title = Widgets.Text(cfg.title, {
		Name = "Action",
		Position = Layout.Position(cfg.title.rect),
		Size = Layout.Size(cfg.title.rect),
	}, content)
	local subtitle = Widgets.Text(cfg.subtitle, {
		Name = "Object",
		Position = Layout.Position(cfg.subtitle.rect),
		Size = Layout.Size(cfg.subtitle.rect),
	}, content)
	local hold = Widgets.Bar({ rect = cfg.hold.rect, fillColor = cfg.hold.fillColor }, content)
	hold.root.Visible = false

	local connections = {}
	local holdTween = nil
	local function refresh()
		key.Text = keyName(prompt, inputType)
		key.TextSize = if #key.Text > 1 then cfg.keycap.textSize * 0.6 else cfg.keycap.textSize
		title.Text = prompt.ActionText
		subtitle.Text = prompt.ObjectText
		subtitle.Visible = prompt.ObjectText ~= ""
		-- A prompt without object text centres its action vertically.
		title.Position = if subtitle.Visible
			then Layout.Position(cfg.title.rect)
			else UDim2.fromOffset(cfg.title.rect[1], (height - cfg.title.rect[4]) / 2)
		hold.root.Visible = prompt.HoldDuration > 0
	end
	refresh()
	for _, property in { "ActionText", "ObjectText", "HoldDuration", "KeyboardKeyCode", "GamepadKeyCode" } do
		table.insert(connections, prompt:GetPropertyChangedSignal(property):Connect(refresh))
	end
	-- A rebind in Settings retargets the prompt first, then fires Changed.
	table.insert(connections, Binds.Changed:Connect(refresh))
	Widgets.SetBar(hold, 0, true)
	local function holdBegan()
		if prompt.HoldDuration <= 0 then
			return
		end
		Widgets.SetBar(hold, 0, true)
		hold.fill.Visible = true
		local info = TweenInfo.new(prompt.HoldDuration, Enum.EasingStyle.Linear)
		holdTween = TweenService:Create(hold.fill, info, { Size = UDim2.fromOffset(hold.maxWidth, hold.height) })
		holdTween:Play()
	end
	local function holdEnded()
		if holdTween then
			holdTween:Cancel()
			holdTween = nil
		end
		Widgets.SetBar(hold, 0, true)
	end
	table.insert(connections, prompt.PromptButtonHoldBegan:Connect(holdBegan))
	table.insert(connections, prompt.PromptButtonHoldEnded:Connect(holdEnded))

	-- Touch players (and clickable prompts) press the panel itself.
	if inputType == Enum.ProximityPromptInputType.Touch or prompt.ClickablePrompt then
		local button = Widgets.Make("TextButton", {
			Name = "Press",
			Text = "",
			BackgroundTransparency = 1,
			Size = UDim2.fromScale(1, 1),
			ZIndex = 10,
		}, content)
		local function isPress(input: InputObject): boolean
			local kind = input.UserInputType
			return kind == Enum.UserInputType.Touch or kind == Enum.UserInputType.MouseButton1
		end
		local function pressBegan(input: InputObject)
			if isPress(input) then
				prompt:InputHoldBegin()
			end
		end
		local function pressEnded(input: InputObject)
			if isPress(input) then
				prompt:InputHoldEnd()
			end
		end
		table.insert(connections, button.InputBegan:Connect(pressBegan))
		table.insert(connections, button.InputEnded:Connect(pressEnded))
	end

	billboard.Parent = player:WaitForChild("PlayerGui")
	return function()
		if holdTween then
			holdTween:Cancel()
		end
		for _, connection in connections do
			connection:Disconnect()
		end
		billboard:Destroy()
	end
end

-- getScale() returns the HUD's current UI scale so prompts match the HUD.
function InteractionPrompt.Start(getScale: () -> number)
	for _, descendant in workspace:GetDescendants() do
		adopt(descendant)
	end
	workspace.DescendantAdded:Connect(adopt)
	ProximityPromptService.PromptShown:Connect(function(prompt, inputType)
		-- Prompts the game did not hand to us keep Roblox's own look.
		if prompt.Style ~= Enum.ProximityPromptStyle.Custom or shown[prompt] then
			return
		end
		local cleanup = build(prompt, inputType, getScale())
		if cleanup == nil then
			return
		end
		shown[prompt] = cleanup
		local hidden
		hidden = prompt.PromptHidden:Connect(function()
			hidden:Disconnect()
			local done = shown[prompt]
			shown[prompt] = nil
			if done then
				done()
			end
		end)
	end)
end

return InteractionPrompt
