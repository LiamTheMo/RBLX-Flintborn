-- Adjustable third-person camera (GDD §36.5, Q58). Mouse wheel, pinch and the
-- right stick zoom between fixed bounds; the last zoom is saved to the profile and
-- restored on the next spawn.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local CameraRules = require(ReplicatedStorage.Shared.World.CameraRules)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)

local CameraController = {}

CameraController.REPORT_SECONDS = 6

local player = Players.LocalPlayer
local lastReported = nil

-- Restores a saved zoom by briefly pinning both bounds to it.
local function restore()
	local zoom = CameraRules.Clamp(player:GetAttribute("CameraZoom"))
	player.CameraMinZoomDistance = zoom
	player.CameraMaxZoomDistance = zoom
	task.wait(0.2)
	player.CameraMinZoomDistance = CameraRules.MIN_ZOOM
	player.CameraMaxZoomDistance = CameraRules.MAX_ZOOM
	lastReported = zoom
end

local function currentZoom(): number?
	local head = player.Character and player.Character:FindFirstChild("Head")
	local camera = workspace.CurrentCamera
	if head == nil or camera == nil then
		return nil
	end
	return (camera.CFrame.Position - head.Position).Magnitude
end

function CameraController.Start()
	player.CameraMode = Enum.CameraMode.Classic
	player.CameraMinZoomDistance = CameraRules.MIN_ZOOM
	player.CameraMaxZoomDistance = CameraRules.MAX_ZOOM
	player.CharacterAdded:Connect(function()
		task.wait(0.5)
		restore()
	end)
	if player.Character then
		task.spawn(restore)
	end
	task.spawn(function()
		while true do
			task.wait(CameraController.REPORT_SECONDS)
			local zoom = currentZoom()
			if zoom and (lastReported == nil or math.abs(zoom - lastReported) >= 2) then
				lastReported = zoom
				Remotes.Get("SaveCamera"):FireServer(zoom)
			end
		end
	end)
end

return CameraController
