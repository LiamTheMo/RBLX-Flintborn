-- Sprint (hold) and crouch (toggle) input on keyboard, gamepad and touch (GDD §5.1,
-- Q27). Sends intent only; the server owns stamina and movement speed. World only.

local ContextActionService = game:GetService("ContextActionService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local SessionStates = require(ReplicatedStorage.Shared.Admission.SessionStates)

local MovementController = {}

local player = Players.LocalPlayer
local sprintHeld = false
local crouching = false

local function send()
	Remotes.Get("SetMovement"):FireServer(sprintHeld, crouching)
end

local function onSprint(_, inputState)
	if inputState == Enum.UserInputState.Begin then
		sprintHeld = true
		send()
	elseif inputState == Enum.UserInputState.End or inputState == Enum.UserInputState.Cancel then
		sprintHeld = false
		send()
	end
	return Enum.ContextActionResult.Pass
end

local function onCrouch(_, inputState)
	if inputState == Enum.UserInputState.Begin then
		crouching = not crouching
		send()
	end
	return Enum.ContextActionResult.Sink
end

local function bind()
	ContextActionService:BindAction("FlintbornSprint", onSprint, true, Enum.KeyCode.LeftShift, Enum.KeyCode.ButtonL3)
	ContextActionService:SetTitle("FlintbornSprint", "Sprint")
	ContextActionService:BindAction("FlintbornCrouch", onCrouch, true, Enum.KeyCode.C, Enum.KeyCode.ButtonR3)
	ContextActionService:SetTitle("FlintbornCrouch", "Crouch")
end

local function unbind()
	ContextActionService:UnbindAction("FlintbornSprint")
	ContextActionService:UnbindAction("FlintbornCrouch")
	sprintHeld, crouching = false, false
end

local function refresh()
	if SessionStates.IsAtRisk(player:GetAttribute("SessionState")) then
		bind()
	else
		unbind()
	end
end

function MovementController.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	player:GetAttributeChangedSignal("SessionState"):Connect(refresh)
	refresh()
end

return MovementController
