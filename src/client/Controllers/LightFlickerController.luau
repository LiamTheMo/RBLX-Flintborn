-- Flickers fire and torch PointLights tagged "FlickerLight" (the lobby map's VFX
-- sockets, placed by scripts/roblox_lobby_map.py with a BaseBrightness
-- attribute). Runs on each client, so nothing replicates. Only lights near the
-- camera animate, and every light holds steady with Reduced Motion.

local CollectionService = game:GetService("CollectionService")
local RunService = game:GetService("RunService")

local Theme = require(script.Parent.Parent.Ui.Theme)

local LightFlickerController = {}

LightFlickerController.TAG = "FlickerLight"
LightFlickerController.RADIUS = 160
LightFlickerController.STEP = 1 / 20

-- light -> { base, position, seed }
local lights = {}

-- Brightness multiplier at time t: a slow sway plus a quick crackle, kept within
-- 0.75–1.1 of the base so a torch never looks like it is going out.
function LightFlickerController.Factor(t: number, seed: number): number
	local sway = math.noise(t * 1.3, seed)
	local crackle = math.noise(t * 7.1, seed + 17.3)
	return math.clamp(0.93 + sway * 0.14 + crackle * 0.1, 0.75, 1.1)
end

local function positionOf(light: Instance): Vector3?
	local parent = light.Parent
	if parent and parent:IsA("Attachment") then
		return parent.WorldPosition
	elseif parent and parent:IsA("BasePart") then
		return parent.Position
	end
	return nil
end

local function track(light: Instance)
	if not light:IsA("Light") then
		return
	end
	local base = light:GetAttribute("BaseBrightness")
	lights[light] = {
		base = if type(base) == "number" then base else light.Brightness,
		position = positionOf(light),
		seed = math.random() * 100,
	}
end

local function untrack(light: Instance)
	lights[light] = nil
end

function LightFlickerController.Start()
	for _, light in CollectionService:GetTagged(LightFlickerController.TAG) do
		track(light)
	end
	CollectionService:GetInstanceAddedSignal(LightFlickerController.TAG):Connect(track)
	CollectionService:GetInstanceRemovedSignal(LightFlickerController.TAG):Connect(untrack)

	local elapsed = 0
	local wasSteady = false
	RunService.Heartbeat:Connect(function(dt)
		elapsed += dt
		if elapsed < LightFlickerController.STEP or next(lights) == nil then
			return
		end
		elapsed = 0
		local steady = Theme.ReducedMotion()
		if steady then
			if not wasSteady then
				for light, info in lights do
					light.Brightness = info.base
				end
			end
			wasSteady = true
			return
		end
		wasSteady = false
		local camera = workspace.CurrentCamera
		local origin = camera and camera.CFrame.Position
		local now = os.clock()
		for light, info in lights do
			info.position = info.position or positionOf(light)
			local position = info.position
			if origin == nil or position == nil or (position - origin).Magnitude <= LightFlickerController.RADIUS then
				light.Brightness = info.base * LightFlickerController.Factor(now, info.seed)
			end
		end
	end)
end

return LightFlickerController
