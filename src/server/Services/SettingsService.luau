-- Saved player choices (GDD §23.2, §25, §46): the camera zoom preference, the
-- Settings screen's choices (SettingsRules: UI scale, accessibility, volumes,
-- camera sensitivity and inversion, damage numbers, names, graphics quality) and
-- keyboard rebinds. The server validates and stores them and hands them back as
-- player attributes on join.

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local CameraRules = require(ReplicatedStorage.Shared.World.CameraRules)
local Keybinds = require(ReplicatedStorage.Shared.Settings.Keybinds)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local SettingsRules = require(script.Parent.Parent.Rules.Settings.SettingsRules)
local Cooldown = require(script.Parent.Parent.Infrastructure.Cooldown)
local ProfileService = require(script.Parent.ProfileService)

local SettingsService = {}

SettingsService.SAVE_INTERVAL = 5

local function applyAttributes(player: Player, choices)
	player:SetAttribute("CameraZoom", CameraRules.Clamp(choices.camera.zoom))
	local values = SettingsRules.Resolve(choices)
	for _, setting in SettingsRules.Settings do
		player:SetAttribute(setting.attribute, values[setting.key])
	end
	-- Attributes cannot hold tables, so the overrides travel as JSON.
	player:SetAttribute("Keybinds", HttpService:JSONEncode(Keybinds.Sanitize(choices.keybinds)))
end

-- Camera zoom saves are throttled; extra ones are dropped silently.
local zoomSaves = Cooldown.new(function()
	return SettingsService.SAVE_INTERVAL
end)

function SettingsService.Start()
	ProfileService.ProfileLoaded:Connect(function(player, profile)
		applyAttributes(player, profile.choices)
	end)
	Remotes.Listen("SaveSettings", function(player, settings)
		if type(settings) ~= "table" then
			return
		end
		ProfileService.Mutate(player, function(profile)
			SettingsRules.Apply(profile.choices, settings)
			applyAttributes(player, profile.choices)
		end)
	end)
	Remotes.Listen("SaveKeybinds", function(player, overrides)
		local clean = Keybinds.Sanitize(overrides)
		ProfileService.Mutate(player, function(profile)
			profile.choices.keybinds = clean
		end)
		player:SetAttribute("Keybinds", HttpService:JSONEncode(clean))
	end)
	Remotes.Listen("SaveCamera", function(player, zoom)
		-- The type is checked first, so a malformed request never starts the cooldown.
		if type(zoom) ~= "number" or not zoomSaves:Try(player) then
			return
		end
		local clamped = CameraRules.Clamp(zoom)
		ProfileService.Mutate(player, function(profile)
			profile.choices.camera.zoom = clamped
		end)
		player:SetAttribute("CameraZoom", clamped)
	end)
	Players.PlayerRemoving:Connect(function(player)
		zoomSaves:Forget(player)
	end)
end

return SettingsService
