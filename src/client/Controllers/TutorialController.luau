-- Tutorial hints (GDD §25.5, §36.5). Shows the current step with its hint, a
-- "Got it" button for explanation steps, Skip after the safe Play step, and a
-- marker over the nearest relevant thing (a resource node, an event, a portal).
-- The marker bobs unless reduced motion is on. Works in both places.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Theme = require(script.Parent.Parent.Ui.Theme)

local TutorialController = {}

local player = Players.LocalPlayer
local ui = {}
local state = nil
local marker = nil

local make = Theme.Make

-- What the marker points at for each step, if anything.
local function targets(stepId: string?)
	local list = {}
	if stepId == "Gather" then
		local folder = workspace:FindFirstChild("ResourceNodes")
		if folder then
			for _, part in folder:GetChildren() do
				table.insert(list, part)
			end
		end
	elseif stepId == "Events" then
		local folder = workspace:FindFirstChild("WorldEvents")
		if folder then
			for _, model in folder:GetChildren() do
				local part = model:FindFirstChildWhichIsA("BasePart")
				if part then
					table.insert(list, part)
				end
			end
		end
	elseif stepId == "Extract" then
		for _, part in workspace:GetChildren() do
			if part:IsA("BasePart") and part:GetAttribute("PortalKind") then
				table.insert(list, part)
			end
		end
	end
	return list
end

local function nearest(list)
	local root = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
	if root == nil then
		return nil
	end
	local best, bestDistance = nil, math.huge
	for _, part in list do
		local distance = (part.Position - root.Position).Magnitude
		if distance < bestDistance then
			best, bestDistance = part, distance
		end
	end
	return best
end

local function updateMarker()
	local target = state and not state.done and not state.skipped and nearest(targets(state.id))
	if target == nil then
		if marker then
			marker.Enabled = false
		end
		return
	end
	if marker == nil then
		marker = make("BillboardGui", { Size = UDim2.fromOffset(40, 40), AlwaysOnTop = true }, nil)
		make("TextLabel", {
			Size = UDim2.fromScale(1, 1),
			BackgroundTransparency = 1,
			Text = "▼",
			TextColor3 = Theme.Colors.Heading,
			TextStrokeTransparency = 0.2,
			Font = Theme.Fonts.Title,
			TextSize = 30,
		}, marker)
		marker.Parent = player:WaitForChild("PlayerGui")
	end
	marker.Enabled = true
	marker.Adornee = target
	local bob = if Theme.ReducedMotion() then 0 else math.sin(os.clock() * 4) * 0.6
	marker.StudsOffset = Vector3.new(0, target.Size.Y / 2 + 3 + bob, 0)
end

local function render()
	local visible = state ~= nil and not state.done and not state.skipped and state.id ~= nil
	ui.card.Visible = visible
	if not visible then
		return
	end
	ui.title.Text = ("Tutorial %d/%d · %s"):format(state.index, state.total, state.title)
	ui.hint.Text = state.hint
	ui.ack.Visible = state.ack
	ui.skip.Visible = state.index > 1
end

local function build()
	local gui = make("ScreenGui", { Name = "Tutorial", ResetOnSpawn = false }, player:WaitForChild("PlayerGui"))
	ui.card = make("Frame", {
		Position = UDim2.fromOffset(12, 300),
		Size = UDim2.fromOffset(330, 0),
		AutomaticSize = Enum.AutomaticSize.Y,
		BackgroundColor3 = Theme.Colors.Card,
		BackgroundTransparency = 0.1,
		Visible = false,
	}, gui)
	make("UICorner", { CornerRadius = UDim.new(0, 8) }, ui.card)
	make("UIPadding", {
		PaddingTop = UDim.new(0, 8),
		PaddingBottom = UDim.new(0, 8),
		PaddingLeft = UDim.new(0, 10),
		PaddingRight = UDim.new(0, 10),
	}, ui.card)
	make("UIListLayout", { Padding = UDim.new(0, 6), SortOrder = Enum.SortOrder.LayoutOrder }, ui.card)
	ui.title = make("TextLabel", {
		Size = UDim2.new(1, 0, 0, 20),
		BackgroundTransparency = 1,
		TextXAlignment = Enum.TextXAlignment.Left,
		TextColor3 = Theme.Colors.Heading,
		Font = Theme.Fonts.Bold,
		TextSize = Theme.TextSize.Heading,
		LayoutOrder = 1,
	}, ui.card)
	ui.hint = make("TextLabel", {
		Size = UDim2.new(1, 0, 0, 0),
		AutomaticSize = Enum.AutomaticSize.Y,
		BackgroundTransparency = 1,
		TextXAlignment = Enum.TextXAlignment.Left,
		TextWrapped = true,
		TextColor3 = Theme.Colors.Text,
		Font = Theme.Fonts.Body,
		TextSize = Theme.TextSize.Body,
		LayoutOrder = 2,
	}, ui.card)
	local function action(text: string, order: number, name: string)
		local b = make("TextButton", {
			Text = text,
			Size = UDim2.new(1, 0, 0, Theme.TOUCH_TARGET - 8),
			BackgroundColor3 = Theme.Colors.Button,
			TextColor3 = Theme.Colors.Text,
			Font = Theme.Fonts.Bold,
			TextSize = Theme.TextSize.Body,
			LayoutOrder = order,
		}, ui.card)
		make("UICorner", { CornerRadius = UDim.new(0, 6) }, b)
		b.Activated:Connect(function()
			pcall(function()
				Remotes.Get("TutorialAction"):InvokeServer(name)
			end)
		end)
		return b
	end
	ui.ack = action("Got it", 3, "Ack")
	ui.skip = action("Skip tutorial", 4, "Skip")
	ui.skip.BackgroundColor3 = Theme.Colors.ButtonDisabled
end

function TutorialController.Start()
	build()
	Remotes.Get("TutorialChanged").OnClientEvent:Connect(function(payload)
		state = payload
		render()
	end)
	RunService.Heartbeat:Connect(updateMarker)
end

return TutorialController
