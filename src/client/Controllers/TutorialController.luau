-- Tutorial hints (GDD §25.5, §36.5). Shows the current step with its hint, a
-- "Got it" button for explanation steps, Skip after the safe Play step, and a
-- marker over the nearest relevant thing (a resource node, an event, a portal).
-- The marker bobs unless reduced motion is on. Works in both places. The hint is a
-- kit notice card with key caps for the keys it names (the player's own binds).

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Kit = require(script.Parent.Parent.Hud.Kit)
local NoticeCard = require(script.Parent.Parent.Hud.NoticeCard)
local Binds = require(script.Parent.Parent.Ui.Binds)
local Theme = require(script.Parent.Parent.Ui.Theme)

local TutorialController = {}

local player = Players.LocalPlayer
local ui = {}
local state = nil
local marker = nil
local target = nil
local sinceScan = math.huge

-- Finding the nearest target walks folders, so it runs a few times a second;
-- only the marker's bob runs every frame.
TutorialController.SCAN_SECONDS = 0.3

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

local function updateMarker(dt: number)
	sinceScan += dt
	if sinceScan >= TutorialController.SCAN_SECONDS then
		sinceScan = 0
		target = state and not state.done and not state.skipped and nearest(targets(state.id)) or nil
	end
	if target ~= nil and target.Parent == nil then
		target = nil
	end
	if target == nil then
		if marker then
			marker.Enabled = false
		end
		return
	end
	if marker == nil then
		marker =
			make("BillboardGui", { Name = "TutorialMarker", Size = UDim2.fromOffset(44, 44), AlwaysOnTop = true }, nil)
		Kit.Icon.new(marker, { name = "Pin", rect = { 0, 0, 44, 44 }, icon = "map_pin" })
		marker.Parent = player:WaitForChild("PlayerGui")
	end
	marker.Enabled = true
	marker.Adornee = target
	local bob = if Theme.ReducedMotion() then 0 else math.sin(os.clock() * 4) * 0.6
	marker.StudsOffset = Vector3.new(0, target.Size.Y / 2 + 3 + bob, 0)
end

-- The actions a hint names ({Interact}, {Build}…), in order, once each.
local function hintKeys(hint: string)
	local keys, seen = {}, {}
	for id in string.gmatch(hint, "{(%w+)}") do
		if not seen[id] then
			seen[id] = true
			local ok, key = pcall(Binds.Label, id)
			if ok and key ~= "?" then
				table.insert(keys, { key = key, label = id })
			end
		end
	end
	return keys
end

local function render()
	local visible = state ~= nil and not state.done and not state.skipped and state.id ~= nil
	if not visible then
		ui.card:Hide()
		return
	end
	ui.card:SetButtonVisible(ui.ack, state.ack == true)
	ui.card:SetButtonVisible(ui.skip, state.index > 1)
	ui.card:SetKeys(hintKeys(state.hint or ""))
	ui.card:Show(Binds.Format(state.hint or ""), ("Tutorial %d/%d · %s"):format(state.index, state.total, state.title))
end

local function build()
	-- In the shared top-centre column, so Got it / Skip stay on-screen on phones
	-- and the card never overlaps other banners.
	ui.card = NoticeCard.new(Theme.TopStack(), {
		name = "Tutorial",
		width = 500,
		layoutOrder = Theme.TopOrder.Tutorial,
		title = "",
		icon = "scroll",
	})
	ui.card.frame.Active = true
	local function action(text: string, kind: string?, name: string)
		return ui.card:AddButton(text, kind, function()
			pcall(function()
				Remotes.Get("TutorialAction"):InvokeServer(name)
			end)
		end)
	end
	ui.ack = action("Got it", nil, "Ack")
	ui.skip = action("Skip tutorial", "paper", "Skip")
end

function TutorialController.Start()
	build()
	Remotes.Get("TutorialChanged").OnClientEvent:Connect(function(payload)
		state = payload
		sinceScan = math.huge
		render()
	end)
	RunService.Heartbeat:Connect(updateMarker)
	Binds.Changed:Connect(render)
end

return TutorialController
