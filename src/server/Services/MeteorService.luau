-- Meteor crashes (GDD §7.2): a crater of chunks that each take a 30 s channel to
-- break loose, so harvesting the whole meteor is long and contestable. Each chunk
-- pays out once as physical drops. World place only.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local EventRules = require(ReplicatedStorage.Shared.Events.EventRules)
local Channel = require(script.Parent.Parent.Infrastructure.Channel)
local CacheService = require(script.Parent.CacheService)
local DropService = require(script.Parent.DropService)
local InventoryService = require(script.Parent.InventoryService)
local ModifierService = require(script.Parent.ModifierService)
local ProgressionService = require(script.Parent.ProgressionService)

local MeteorService = {}

MeteorService.CHUNK_SECONDS = 30
MeteorService.REACH = 10

local rng = Random.new()

-- Spawns a meteor for `entry` at `position`. `onDepleted()` runs once every
-- chunk has been harvested.
function MeteorService.Spawn(entry, position: Vector3, parent: Instance, onDepleted)
	local core = Instance.new("Part")
	core.Name = entry.name
	core.Shape = Enum.PartType.Ball
	core.Anchored = true
	core.Size = Vector3.new(14, 14, 14)
	core.Material = Enum.Material.Basalt
	core.Color = Color3.fromRGB(60, 44, 40)
	core.CFrame = CFrame.new(position + Vector3.new(0, 4, 0))
	core.Parent = parent
	local glow = Instance.new("PointLight")
	glow.Color = Color3.fromRGB(255, 120, 40)
	glow.Range = 30
	glow.Brightness = 3
	glow.Parent = core
	local remaining = entry.chunks
	for index = 1, entry.chunks do
		local angle = (index / entry.chunks) * math.pi * 2
		local chunk = Instance.new("Part")
		chunk.Name = "MeteorChunk"
		chunk.Anchored = true
		chunk.Size = Vector3.new(3, 3, 3)
		chunk.Material = Enum.Material.CrackedLava
		chunk.Color = Color3.fromRGB(255, 110, 40)
		chunk.CFrame = CFrame.new(position + Vector3.new(math.cos(angle) * 9, 1.5, math.sin(angle) * 9))
		chunk.Parent = parent
		local prompt = Instance.new("ProximityPrompt")
		prompt.ActionText = "Break loose (30 s)"
		prompt.ObjectText = entry.name
		prompt.MaxActivationDistance = MeteorService.REACH - 2
		prompt.RequiresLineOfSight = false
		prompt.Parent = chunk
		local site = {}
		Channel.Attach(prompt, MeteorService.CHUNK_SECONDS, function(player)
			return CacheService.CanInteract(player, chunk, MeteorService.REACH)
		end, function(player)
			if not EventRules.Claim(site) then
				return
			end
			local at = chunk.Position
			chunk:Destroy()
			ProgressionService.GrantXp(player, ProgressionService.XP.MeteorChunk, entry.name)
			for _, item in EventRules.RollLoot(entry.loot, rng, ModifierService.Sum(player, "Luck")) do
				DropService.Spawn(item, at)
			end
			remaining -= 1
			if remaining == 0 then
				onDepleted()
			end
		end, function(player)
			InventoryService.Notify(player, "Interrupted: the chunk starts over.")
		end)
	end
	return core
end

return MeteorService
