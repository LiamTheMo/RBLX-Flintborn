-- Ancient Supply Caches (GDD §7.4). Opening one takes 60 continuous seconds of
-- interaction; letting go, walking off or being hit restarts the channel. The
-- loot is rolled once on the server and spills out as physical, contested drops.
-- The plain hitbox part keeps the prompt and the interaction; PropModels draws a
-- wood chest over it whose lid swings open (its lock and gem go out) when the cache is looted. World place only.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local EventRules = require(script.Parent.Parent.Rules.Events.EventRules)
local ModelBuilder = require(script.Parent.Parent.Rules.Visuals.ModelBuilder)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local PropModels = require(script.Parent.Parent.Rules.Visuals.PropModels)
local Rarity = require(ReplicatedStorage.Shared.Items.Rarity)
local Recipe = require(script.Parent.Parent.Rules.Visuals.Recipe)
local Channel = require(script.Parent.Parent.Infrastructure.Channel)
local CombatService = require(script.Parent.CombatService)
local DropService = require(script.Parent.DropService)
local InteractionService = require(script.Parent.InteractionService)
local InventoryService = require(script.Parent.InventoryService)
local ModifierService = require(script.Parent.ModifierService)
local ProgressionService = require(script.Parent.ProgressionService)

local CacheService = {}

CacheService.CHANNEL_SECONDS = 60
CacheService.REACH = 10

local rng = Random.new()

-- Swings the chest's lid open about its hinge and hides the lit parts.
local function openChest(dressing: { BasePart })
	local hinge = CFrame.new(PropModels.CHEST_HINGE[1], PropModels.CHEST_HINGE[2], PropModels.CHEST_HINGE[3])
	local swing = hinge * CFrame.Angles(math.rad(PropModels.CHEST_OPEN_DEGREES), 0, 0) * hinge:Inverse()
	local dark = {}
	for _, piece in dressing do
		if string.sub(piece.Name, 1, #PropModels.LID_PREFIX) == PropModels.LID_PREFIX then
			local weld = piece:FindFirstChildOfClass("Weld")
			if weld then
				weld.C0 = swing * weld.C0
			end
		end
		if PropModels.CHEST_GLOW[piece.Name] then
			table.insert(dark, piece)
		end
	end
	ModelBuilder.SetVisible(dark, false)
end

-- Spawns a cache for `entry` (an EventCatalog cache) at `position`. `onOpened()`
-- runs once after the loot has spilled. Returns the cache part.
function CacheService.Spawn(entry, position: Vector3, parent: Instance, onOpened)
	local part = Instance.new("Part")
	part.Name = entry.name
	part.Anchored = true
	part.Size = Vector3.new(4, 3, 3)
	-- The invisible hitbox; the chest is drawn over it, its lock and gem in the rarity colour.
	part.Transparency = 1
	part.CFrame = CFrame.new(position + Vector3.new(0, 1.5, 0))
	part.Parent = parent
	local accent = Recipe.Rgb(Rarity.Colors[entry.rarity] or Color3.fromRGB(140, 110, 70))
	local dressing = ModelBuilder.Decorate(part, PropModels.Chest(accent))
	local prompt = Instance.new("ProximityPrompt")
	prompt.ActionText = "Open (60 s, don't get hit)"
	prompt.ObjectText = ("%s · %s"):format(entry.name, entry.rarity)
	prompt.MaxActivationDistance = CacheService.REACH - 2
	prompt.RequiresLineOfSight = false
	prompt.Parent = part
	local site = {}
	Channel.Attach(prompt, CacheService.CHANNEL_SECONDS, function(player)
		return InteractionService.CanInteract(player, part, CacheService.REACH)
	end, function(player)
		if not EventRules.Claim(site) then
			return
		end
		prompt:Destroy()
		openChest(dressing)
		ProgressionService.GrantXp(player, "Cache", entry.name)
		DropService.Scatter(EventRules.RollLoot(entry.loot, rng, ModifierService.Sum(player, "Luck")), position, rng)
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
