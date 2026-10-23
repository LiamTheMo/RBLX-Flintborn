-- Ancient Supply Caches (GDD §7.4). Opening one takes 60 continuous seconds of
-- interaction; letting go, walking off or being hit restarts the channel. The
-- loot is rolled once on the server and spills out as physical, contested drops.
-- World place only.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local EventRules = require(ReplicatedStorage.Shared.Events.EventRules)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Rarity = require(ReplicatedStorage.Shared.Items.Rarity)
local Channel = require(script.Parent.Parent.Infrastructure.Channel)
local CombatService = require(script.Parent.CombatService)
local DownedService = require(script.Parent.DownedService)
local DropService = require(script.Parent.DropService)
local InventoryService = require(script.Parent.InventoryService)
local WorldAdmissionService = require(script.Parent.WorldAdmissionService)

local CacheService = {}

CacheService.CHANNEL_SECONDS = 60
CacheService.REACH = 10

local rng = Random.new()

-- True for a living, at-risk, non-downed player within `reach` of `part`.
function CacheService.CanInteract(player: Player, part: BasePart, reach: number): boolean
	local character = player.Character
	local root = character and character:FindFirstChild("HumanoidRootPart")
	local humanoid = character and character:FindFirstChildOfClass("Humanoid")
	return root ~= nil
		and humanoid ~= nil
		and humanoid.Health > 0
		and WorldAdmissionService.IsAtRisk(player)
		and not DownedService.IsDowned(player)
		and (root.Position - part.Position).Magnitude <= reach
end

-- Spawns a cache for `entry` (an EventCatalog cache) at `position`. `onOpened()`
-- runs once after the loot has spilled. Returns the cache part.
function CacheService.Spawn(entry, position: Vector3, parent: Instance, onOpened)
	local part = Instance.new("Part")
	part.Name = entry.name
	part.Anchored = true
	part.Size = Vector3.new(4, 3, 3)
	part.Material = Enum.Material.Wood
	part.Color = Rarity.Colors[entry.rarity] or Color3.fromRGB(140, 110, 70)
	part.CFrame = CFrame.new(position + Vector3.new(0, 1.5, 0))
	part.Parent = parent
	local prompt = Instance.new("ProximityPrompt")
	prompt.ActionText = "Open (60 s, don't get hit)"
	prompt.ObjectText = ("%s · %s"):format(entry.name, entry.rarity)
	prompt.MaxActivationDistance = CacheService.REACH - 2
	prompt.RequiresLineOfSight = false
	prompt.Parent = part
	local site = {}
	Channel.Attach(prompt, CacheService.CHANNEL_SECONDS, function(player)
		return CacheService.CanInteract(player, part, CacheService.REACH)
	end, function()
		if not EventRules.Claim(site) then
			return
		end
		prompt:Destroy()
		part.Transparency = 0.6
		for _, item in EventRules.RollLoot(entry.loot, rng) do
			DropService.Spawn(item, position + Vector3.new(rng:NextNumber(-3, 3), 0, rng:NextNumber(-3, 3)))
		end
		onOpened()
	end, function(player)
		InventoryService.Notify(player, "Interrupted: the cache channel starts over.")
	end)
	return part
end

function CacheService.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	-- Taking damage from anything breaks every channel the victim was holding.
	CombatService.Hurt:Connect(Channel.Interrupt)
end

return CacheService
