-- Public event announcements (GDD §7.1, Q43). Every event that actually spawns is
-- announced to the whole server with its name, rarity, area and end time, plus a
-- thin sky beacon that never hides projectiles or extraction signals (§36.5).
-- Players arriving later receive everything still running. World place only.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Rarity = require(ReplicatedStorage.Shared.Items.Rarity)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)

local AnnouncementService = {}

local active = {}

-- view = {id, name, rarity, category, kind, position, radius, endsAt}
function AnnouncementService.Announce(view)
	local beacon = Instance.new("Part")
	beacon.Name = "EventBeacon"
	beacon.Anchored = true
	beacon.CanCollide = false
	beacon.CanQuery = false
	beacon.CanTouch = false
	beacon.CastShadow = false
	beacon.Material = Enum.Material.Neon
	beacon.Color = Rarity.Colors[view.rarity] or Color3.new(1, 1, 1)
	beacon.Transparency = 0.6
	beacon.Size = Vector3.new(0.8, 300, 0.8)
	beacon.CFrame = CFrame.new(view.position + Vector3.new(0, 150, 0))
	beacon.Parent = workspace
	active[view.id] = { view = view, beacon = beacon }
	Remotes.Get("EventAnnounced"):FireAllClients(view)
end

function AnnouncementService.End(eventId: string)
	local entry = active[eventId]
	if entry == nil then
		return
	end
	active[eventId] = nil
	entry.beacon:Destroy()
	Remotes.Get("EventEnded"):FireAllClients(eventId)
end

function AnnouncementService.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	Players.PlayerAdded:Connect(function(player)
		for _, entry in active do
			Remotes.Get("EventAnnounced"):FireClient(player, entry.view, true)
		end
	end)
end

return AnnouncementService
