-- Saved player choices (GDD §23.2, §25): the camera zoom preference, UI scale and
-- accessibility options (colour-blind palette, reduced motion, subtitles). The
-- server validates and stores them and hands them back as attributes on join.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local CameraRules = require(ReplicatedStorage.Shared.World.CameraRules)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local ProfileService = require(script.Parent.ProfileService)

local SettingsService = {}

SettingsService.SAVE_INTERVAL = 5
SettingsService.UI_SCALE = { min = 0.8, max = 1.4 }

local function applyAttributes(player: Player, choices)
	player:SetAttribute("CameraZoom", CameraRules.Clamp(choices.camera.zoom))
	player:SetAttribute("UiScale", choices.uiScale or 1)
	player:SetAttribute("ColourBlind", choices.colourBlindMode == true)
	player:SetAttribute("ReducedMotion", choices.reducedMotion == true)
	player:SetAttribute("Subtitles", choices.subtitles ~= false)
end

local lastSave = {}

function SettingsService.Start()
	ProfileService.ProfileLoaded:Connect(function(player, profile)
		applyAttributes(player, profile.choices)
	end)
	Remotes.Listen("SaveSettings", function(player, settings)
		if type(settings) ~= "table" then
			return
		end
		local scale = tonumber(settings.uiScale)
		ProfileService.Mutate(player, function(profile)
			local choices = profile.choices
			if scale and scale == scale then
				choices.uiScale =
					math.clamp(math.round(scale * 10) / 10, SettingsService.UI_SCALE.min, SettingsService.UI_SCALE.max)
			end
			for _, key in { "colourBlindMode", "reducedMotion", "subtitles" } do
				if type(settings[key]) == "boolean" then
					choices[key] = settings[key]
				end
			end
			applyAttributes(player, choices)
		end)
	end)
	Remotes.Listen("SaveCamera", function(player, zoom)
		local now = os.clock()
		if type(zoom) ~= "number" or (lastSave[player] and now - lastSave[player] < SettingsService.SAVE_INTERVAL) then
			return
		end
		lastSave[player] = now
		local clamped = CameraRules.Clamp(zoom)
		ProfileService.Mutate(player, function(profile)
			profile.choices.camera.zoom = clamped
		end)
		player:SetAttribute("CameraZoom", clamped)
	end)
	Players.PlayerRemoving:Connect(function(player)
		lastSave[player] = nil
	end)
end

return SettingsService
