-- Applies the Settings screen's preferences that change the game around the
-- player (GDD §25): sound volumes, camera sensitivity and inversion, other
-- players' name tags and graphics quality. Each follows its player attribute
-- (SettingsService sets them from the profile), so a change applies the moment
-- it is saved. All of it is local to this client.
--
-- Sounds play through two SoundGroups: "Music" (sounds tagged "Music") and
-- "Effects" (every other sound without a group of its own).

local CollectionService = game:GetService("CollectionService")
local Lighting = game:GetService("Lighting")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local SoundService = game:GetService("SoundService")
local UserInputService = game:GetService("UserInputService")

local SettingsRules = require(ReplicatedStorage.Shared.Settings.SettingsRules)

local PreferencesController = {}

PreferencesController.MUSIC_TAG = "Music"

local player = Players.LocalPlayer
local groups = {}
-- Lighting's own shadow setting, restored when quality goes back up.
local shadowsDefault = Lighting.GlobalShadows

local function value(key: string)
	local setting = SettingsRules.Get(key)
	local clean = SettingsRules.Clean(setting, player:GetAttribute(setting.attribute))
	return if clean == nil then setting.default else clean
end

local function group(name: string): SoundGroup
	if groups[name] == nil then
		local soundGroup = SoundService:FindFirstChild(name)
		if soundGroup == nil or not soundGroup:IsA("SoundGroup") then
			soundGroup = Instance.new("SoundGroup")
			soundGroup.Name = name
			soundGroup.Parent = SoundService
		end
		groups[name] = soundGroup
	end
	return groups[name]
end

local function applyVolumes()
	group("Music").Volume = SettingsRules.Volume(value("musicVolume"))
	group("Effects").Volume = SettingsRules.Volume(value("effectsVolume"))
end

local function route(sound: Instance)
	if sound:IsA("Sound") and sound.SoundGroup == nil then
		sound.SoundGroup = if CollectionService:HasTag(sound, PreferencesController.MUSIC_TAG)
			then group("Music")
			else group("Effects")
	end
end

local function routeSounds()
	for _, root in { workspace, SoundService, player:WaitForChild("PlayerGui") } do
		for _, descendant in root:GetDescendants() do
			route(descendant)
		end
		root.DescendantAdded:Connect(route)
	end
	CollectionService:GetInstanceAddedSignal(PreferencesController.MUSIC_TAG):Connect(function(sound)
		if sound:IsA("Sound") then
			sound.SoundGroup = group("Music")
		end
	end)
end

-- Set once the camera input is wrapped: sensitivity then scales mouse, touch and
-- gamepad look alike; until then (or without the module) it scales the mouse only.
local hooked = false

local function applySensitivity()
	pcall(function()
		UserInputService.MouseDeltaSensitivity = if hooked
			then 1
			else SettingsRules.MouseSensitivity(value("cameraSensitivity"))
	end)
end

-- Camera sensitivity and inversion: Roblox's camera reads look input (mouse,
-- touch and gamepad) through the PlayerModule's CameraInput.getRotation; wrapping
-- it scales the turn and flips its vertical part while the setting is on. Without
-- that module (a forked or missing camera) inversion does nothing and sensitivity
-- falls back to the mouse.
local function hookCamera()
	task.spawn(function()
		local scripts = player:WaitForChild("PlayerScripts", 30)
		local module = scripts and scripts:WaitForChild("PlayerModule", 30)
		local cameraModule = module and module:WaitForChild("CameraModule", 30)
		local inputModule = cameraModule and cameraModule:WaitForChild("CameraInput", 30)
		if inputModule == nil then
			return
		end
		local ok, CameraInput = pcall(require, inputModule)
		if not ok or type(CameraInput) ~= "table" or type(CameraInput.getRotation) ~= "function" then
			warn("[Preferences] camera input not found; Invert Camera is unavailable")
			return
		end
		local getRotation = CameraInput.getRotation
		CameraInput.getRotation = function(...)
			local rotation = getRotation(...)
			if typeof(rotation) ~= "Vector2" then
				return rotation
			end
			local k = SettingsRules.MouseSensitivity(value("cameraSensitivity"))
			local flip = if player:GetAttribute("InvertCamera") == true then -1 else 1
			return Vector2.new(rotation.X * k, rotation.Y * k * flip)
		end
		hooked = true
		applySensitivity()
	end)
end

-- Other players' name tags, shown or hidden. Hiding remembers the tag's own
-- setting so showing again restores it.
local shownAs = setmetatable({}, { __mode = "k" })
local nameWatch = {}

local function applyName(character: Model?)
	local humanoid = character and character:FindFirstChildOfClass("Humanoid")
	if humanoid == nil then
		return
	end
	if value("showNames") then
		if shownAs[humanoid] then
			humanoid.DisplayDistanceType = shownAs[humanoid]
			shownAs[humanoid] = nil
		end
	elseif humanoid.DisplayDistanceType ~= Enum.HumanoidDisplayDistanceType.None then
		shownAs[humanoid] = humanoid.DisplayDistanceType
		humanoid.DisplayDistanceType = Enum.HumanoidDisplayDistanceType.None
	end
end

local function watchPlayer(other: Player)
	if other == player then
		return
	end
	nameWatch[other] = other.CharacterAdded:Connect(function(character)
		character:WaitForChild("Humanoid", 10)
		applyName(character)
	end)
	applyName(other.Character)
end

local function applyNames()
	for _, other in Players:GetPlayers() do
		if other ~= player then
			applyName(other.Character)
		end
	end
end

-- Graphics quality: shadows on or off, and decorative particle rates scaled.
local function scaleParticles(emitter: Instance)
	if not emitter:IsA("ParticleEmitter") then
		return
	end
	local base = emitter:GetAttribute("BaseRate")
	if base == nil then
		base = emitter.Rate
		emitter:SetAttribute("BaseRate", base)
	end
	local quality = SettingsRules.Graphics[value("graphicsQuality")] or SettingsRules.Graphics.High
	emitter.Rate = base * quality.particles
end

local function applyGraphics()
	local quality = SettingsRules.Graphics[value("graphicsQuality")] or SettingsRules.Graphics.High
	Lighting.GlobalShadows = shadowsDefault and quality.shadows
	for _, descendant in workspace:GetDescendants() do
		scaleParticles(descendant)
	end
end

function PreferencesController.Start()
	applyVolumes()
	routeSounds()
	applySensitivity()
	hookCamera()
	for _, other in Players:GetPlayers() do
		watchPlayer(other)
	end
	Players.PlayerAdded:Connect(watchPlayer)
	Players.PlayerRemoving:Connect(function(other)
		if nameWatch[other] then
			nameWatch[other]:Disconnect()
			nameWatch[other] = nil
		end
	end)
	applyGraphics()
	workspace.DescendantAdded:Connect(scaleParticles)
	local handlers = {
		MusicVolume = applyVolumes,
		EffectsVolume = applyVolumes,
		CameraSensitivity = applySensitivity,
		ShowNames = applyNames,
		GraphicsQuality = applyGraphics,
	}
	player.AttributeChanged:Connect(function(name: string)
		local handler = handlers[name]
		if handler then
			handler()
		end
	end)
end

return PreferencesController
