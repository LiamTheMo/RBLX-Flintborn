-- Ancient Supply Caches (GDD §7.4). Opening one takes 60 continuous seconds of
-- interaction; letting go, walking off or being hit restarts the channel. The
-- loot is rolled once on the server and spills out as physical, contested drops.
-- The plain hitbox part keeps the prompt and the interaction; PropModels draws a
-- wood chest over it whose lid swings open (its lock and gem go out) when the cache is looted. World place only.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local EventRules = require(ReplicatedStorage.Shared.Events.EventRules)
local ModelBuilder = require(ReplicatedStorage.Shared.Visuals.ModelBuilder)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local PropModels = require(ReplicatedStorage.Shared.Visuals.PropModels)
local Rarity = require(ReplicatedStorage.Shared.Items.Rarity)
local Recipe = require(ReplicatedStorage.Shared.Visuals.Recipe)
local Channel = require(script.Parent.Parent.Infrastructure.Channel)
local AntiExploitService = require(script.Parent.AntiExploitService)
local CombatService = require(script.Parent.CombatService)
local DownedService = require(script.Parent.DownedService)
local DropService = require(script.Parent.DropService)
local InventoryService = require(script.Parent.InventoryService)
local ModifierService = require(script.Parent.ModifierService)
local ProgressionService = require(script.Parent.ProgressionService)
local WorldAdmissionService = require(script.Parent.WorldAdmissionService)

local CacheService = {}

CacheService.CHANNEL_SECONDS = 60
CacheService.REACH = 10
-- Extra slack for the last server-validated position, which lags a sample behind.
CacheService.VALIDATED_SLACK = 8

local rng = Random.new()

-- True for a living, at-risk, non-downed player within `reach` of `part`, both
-- where their character is and where the server last validated it (a teleport
-- cannot hold a channel).
function CacheService.CanInteract(player: Player, part: BasePart, reach: number): boolean
	local character = player.Character
	local root = character and character:FindFirstChild("HumanoidRootPart")
	local humanoid = character and character:FindFirstChildOfClass("Humanoid")
	if root == nil or humanoid == nil or humanoid.Health <= 0 then
		return false
	end
	if not WorldAdmissionService.IsAtRisk(player) or DownedService.IsDowned(player) then
		return false
	end
	if part.Parent == nil or (root.Position - part.Position).Magnitude > reach then
		return false
	end
	local validated = AntiExploitService.ValidatedPosition(player)
	return validated == nil or (validated - part.Position).Magnitude <= reach + CacheService.VALIDATED_SLACK
end

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
		return CacheService.CanInteract(player, part, CacheService.REACH)
	end, function(player)
		if not EventRules.Claim(site) then
			return
		end
		prompt:Destroy()
		openChest(dressing)
		ProgressionService.GrantXp(player, "Cache", entry.name)
		for _, item in EventRules.RollLoot(entry.loot, rng, ModifierService.Sum(player, "Luck")) do
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
