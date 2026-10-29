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
local SettingsRules = require(ReplicatedStorage.Shared.Settings.SettingsRules)
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

local lastSave = {}

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
