-- Sprint (hold) input on keyboard, gamepad and touch (GDD §5.1,
-- Q27). Sends intent only; the server owns stamina and movement speed (including
-- the 30% slow in water). Nobody swims (GDD §55): this client owns its
-- character's humanoid state, so it turns Swimming off on every character. World
-- only.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local SessionStates = require(ReplicatedStorage.Shared.Admission.SessionStates)
local Binds = require(script.Parent.Parent.Ui.Binds)

local MovementController = {}

local player = Players.LocalPlayer
local sprintHeld = false

local function send()
	Remotes.Get("SetMovement"):FireServer(sprintHeld)
end

local function onSprint(_, inputState)
	if inputState == Enum.UserInputState.Begin then
		sprintHeld = true
		send()
	elseif inputState == Enum.UserInputState.End or inputState == Enum.UserInputState.Cancel then
		sprintHeld = false
		send()
	end
	-- Sunk at high priority: Roblox's Shift Lock toggle also listens to LeftShift
	-- (at medium priority), so sprinting no longer flips Shift Lock.
	return Enum.ContextActionResult.Sink
end

local function bind()
	Binds.Bind(
		"Sprint",
		onSprint,
		{ priority = Enum.ContextActionPriority.High.Value, touchButton = true, title = "Sprint" }
	)
end

local function unbind()
	Binds.Unbind("Sprint")
	sprintHeld = false
end

local function refresh()
	if SessionStates.IsAtRisk(player:GetAttribute("SessionState")) then
		bind()
	else
		unbind()
	end
end

-- Knee-deep water is walked through, never swum.
local function noSwimming(character: Model)
	local humanoid = character:WaitForChild("Humanoid", 10)
	if humanoid and humanoid:IsA("Humanoid") then
		humanoid:SetStateEnabled(Enum.HumanoidStateType.Swimming, false)
	end
end

function MovementController.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	player.CharacterAdded:Connect(noSwimming)
	if player.Character then
		task.spawn(noSwimming, player.Character)
	end
	player:GetAttributeChangedSignal("SessionState"):Connect(refresh)
	refresh()
end

return MovementController
