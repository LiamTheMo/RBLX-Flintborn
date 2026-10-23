-- Saved player choices (GDD §23.2 choices): the camera zoom preference. Clients
-- report their zoom at most every few seconds; the server clamps and stores it
-- and hands it back on the next join as the CameraZoom attribute.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local CameraRules = require(ReplicatedStorage.Shared.World.CameraRules)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local ProfileService = require(script.Parent.ProfileService)

local SettingsService = {}

SettingsService.SAVE_INTERVAL = 5

local lastSave = {}

function SettingsService.Start()
	ProfileService.ProfileLoaded:Connect(function(player, profile)
		player:SetAttribute("CameraZoom", CameraRules.Clamp(profile.choices.camera.zoom))
	end)
	Remotes.Get("SaveCamera").OnServerEvent:Connect(function(player, zoom)
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
