-- Custom ProximityPrompt look (GDD §11): the game's prompts switch to
-- Style = Custom on this client, and each shown prompt draws the kit's paper
-- plaque (Kit.Panel "plaque") with a key cap (Kit.KeyCap: the prompt's key, the
-- gamepad button, or TAP), ActionText as the title and ObjectText under it,
-- plus the kit's XP track as a hold bar for timed prompts. The plaque's width
-- follows its key and text. Touch and click call InputHoldBegin/End; the
-- server still validates every trigger. Roblox re-shows a prompt with the new
-- input type when the player switches input, so the key cap follows keyboard,
-- gamepad and touch. Binds retargets prompts authored on E to the player's
-- Interact key (GDD §46), and the cap redraws whenever that key is rebound.

local Players = game:GetService("Players")
local ProximityPromptService = game:GetService("ProximityPromptService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local HudModel = require(ReplicatedStorage.Shared.UI.HudModel)
local Binds = require(script.Parent.Parent.Ui.Binds)
local Kit = require(script.Parent.Kit)
local Layout = require(script.Parent.Layout)

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
	-- choice's own key), so the cap reads the prompt's live key.
	local interact = Binds.Key("Interact")
	return HudModel.KeyLabel("Keyboard", prompt.KeyboardKeyCode.Name, interact and interact.Name)
end

-- The prompt's look, drawn into `content` (a frame in design px). `texts` are
-- {key, action, object, hold}. Returns {width, parts, hold (Kit.Bar?)}; the
-- capture scenes call it directly.
function InteractionPrompt.Draw(content: Instance, texts)
	local cfg = Layout.Get().prompt
	local height = cfg.size[2]
	local cap = cfg.keycap
	local capW = math.max(cap[3], Kit.KeyCap.Width(texts.key, cap[4]))
	local textX = cap[1] + capW + cfg.gap
	local hasObject = texts.object ~= nil and texts.object ~= ""
	local titleW = Kit.Text.Width(texts.action, "rowTitle", cfg.titleSize)
	local objectW = if hasObject then Kit.Text.Width(texts.object, "small", cfg.subtitleSize) else 0
	local width = math.clamp(math.ceil(textX + math.max(titleW, objectW) + cfg.padRight), cfg.size[1], cfg.maxWidth)
	local textW = width - textX - cfg.padRight
	local parts = {}
	table.insert(
		parts,
		Kit.Panel.new(content, { name = "Plaque", rect = { 0, 0, width, height }, variant = "plaque", pad = 0 })
	)
	table.insert(
		parts,
		Kit.KeyCap.new(content, { name = "Key", rect = { cap[1], cap[2], capW, cap[4] }, text = texts.key, zIndex = 8 })
	)
	table.insert(
		parts,
		Kit.Text.new(content, {
			name = "Action",
			rect = if hasObject then { textX, cfg.titleY, textW, cfg.titleH } else { textX, 0, textW, height },
			text = texts.action,
			role = "rowTitle",
			textSize = cfg.titleSize,
			scaled = true,
			zIndex = 8,
		})
	)
	if hasObject then
		table.insert(
			parts,
			Kit.Text.new(content, {
				name = "Object",
				rect = { textX, cfg.subtitleY, textW, cfg.subtitleH },
				text = texts.object,
				role = "small",
				textSize = cfg.subtitleSize,
				scaled = true,
				zIndex = 8,
			})
		)
	end
	local hold = nil
	if texts.hold then
		hold = Kit.Bar.new(content, {
			name = "Hold",
			rect = { textX, height - cfg.holdBottom, textW, cfg.holdH },
			fill = "xp",
			zIndex = 8,
		})
		table.insert(parts, hold)
	end
	return { width = width, height = height, parts = parts, hold = hold }
end

local function build(prompt: ProximityPrompt, inputType: Enum.ProximityPromptInputType, scale: number)
	local cfg = Layout.Get().prompt
	local adornee = adorneeFor(prompt)
	if adornee == nil then
		return nil
	end
	local billboard = Instance.new("BillboardGui")
	billboard.Name = "FlintbornPrompt"
	billboard.Adornee = adornee
	billboard.AlwaysOnTop = true
	billboard.Active = true
	billboard.ResetOnSpawn = false
	billboard.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	billboard.StudsOffset = Vector3.new(cfg.studsOffset[1], cfg.studsOffset[2], cfg.studsOffset[3])
	billboard.LightInfluence = 0
	local content = Instance.new("Frame")
	content.Name = "Content"
	content.BackgroundTransparency = 1
	content.Parent = billboard
	local uiScale = Instance.new("UIScale")
	uiScale.Scale = scale
	uiScale.Parent = content

	local drawn = nil
	local holding = false
	local function refresh()
		if drawn then
			for _, part in drawn.parts do
				part:Destroy()
			end
		end
		drawn = InteractionPrompt.Draw(content, {
			key = keyName(prompt, inputType),
			action = prompt.ActionText,
			object = prompt.ObjectText,
			hold = prompt.HoldDuration > 0,
		})
		content.Size = UDim2.fromOffset(drawn.width, drawn.height)
		billboard.Size = UDim2.fromOffset(drawn.width * scale, drawn.height * scale)
		if drawn.hold then
			drawn.hold:Set(0, true)
		end
		holding = false
	end
	refresh()
	local connections = {}
	for _, property in { "ActionText", "ObjectText", "HoldDuration", "KeyboardKeyCode", "GamepadKeyCode" } do
		table.insert(connections, prompt:GetPropertyChangedSignal(property):Connect(refresh))
	end
	-- A rebind in Settings retargets the prompt first, then fires Changed.
	table.insert(connections, Binds.Changed:Connect(refresh))

	-- The hold bar fills over HoldDuration (linear, as the hold itself runs).
	local holdStarted = 0
	table.insert(
		connections,
		prompt.PromptButtonHoldBegan:Connect(function()
			if drawn.hold then
				holding = true
				holdStarted = os.clock()
				drawn.hold:Set(0, true)
			end
		end)
	)
	table.insert(
		connections,
		prompt.PromptButtonHoldEnded:Connect(function()
			holding = false
			if drawn.hold then
				drawn.hold:Set(0, true)
			end
		end)
	)
	table.insert(
		connections,
		RunService.RenderStepped:Connect(function()
			if holding and drawn.hold then
				drawn.hold:Set((os.clock() - holdStarted) / math.max(prompt.HoldDuration, 0.01), true)
			end
		end)
	)

	-- Touch players (and clickable prompts) press the plaque itself.
	if inputType == Enum.ProximityPromptInputType.Touch or prompt.ClickablePrompt then
		local button = Instance.new("TextButton")
		button.Name = "Press"
		button.Text = ""
		button.BackgroundTransparency = 1
		button.Size = UDim2.fromScale(1, 1)
		button.ZIndex = 20
		button.Parent = content
		local function isPress(input: InputObject): boolean
			local kind = input.UserInputType
			return kind == Enum.UserInputType.Touch or kind == Enum.UserInputType.MouseButton1
		end
		table.insert(
			connections,
			button.InputBegan:Connect(function(input)
				if isPress(input) then
					prompt:InputHoldBegin()
				end
			end)
		)
		table.insert(
			connections,
			button.InputEnded:Connect(function(input)
				if isPress(input) then
					prompt:InputHoldEnd()
				end
			end)
		)
	end

	billboard.Parent = player:WaitForChild("PlayerGui")
	return function()
		for _, connection in connections do
			connection:Disconnect()
		end
		if drawn then
			for _, part in drawn.parts do
				part:Destroy()
			end
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
