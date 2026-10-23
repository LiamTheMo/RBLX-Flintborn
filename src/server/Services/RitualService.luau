-- Ritual bosses (GDD §7.2, Q45). Placing the rare offering at a ritual altar
-- consumes it once on the server and starts a 10 s summoning that anyone can
-- interrupt: if the summoner is hit, downed or walks away, the offering spills on
-- the ground as contested loot. A completed summon is a world interaction, not
-- player magic, and is announced like any event. World place only.

local CollectionService = game:GetService("CollectionService")
local HttpService = game:GetService("HttpService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local BossCatalog = require(ReplicatedStorage.Shared.Bosses.BossCatalog)
local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local AnnouncementService = require(script.Parent.AnnouncementService)
local BossService = require(script.Parent.BossService)
local CacheService = require(script.Parent.CacheService)
local CombatService = require(script.Parent.CombatService)
local DropService = require(script.Parent.DropService)
local InventoryService = require(script.Parent.InventoryService)

local RitualService = {}

RitualService.SITE_TAG = "RitualSite"
RitualService.STAY_RADIUS = 15
RitualService.PLACEHOLDER_SITES = 2
RitualService.DEFAULT_MAP_RADIUS = 1000

local sites = {}
local summoning = {}

local function offeringText(): string
	local parts = {}
	for catalogId, quantity in BossCatalog.Ritual.offering do
		local def = ItemCatalog.Get(catalogId)
		table.insert(parts, ("%d %s"):format(quantity, def and def.name or catalogId))
	end
	table.sort(parts)
	return table.concat(parts, ", ")
end

local function spill(site)
	for catalogId, quantity in BossCatalog.Ritual.offering do
		DropService.Spawn({ catalogId = catalogId, quantity = quantity }, site.position)
	end
end

local function summon(site)
	local def = BossCatalog.Get(BossCatalog.Ritual.boss)
	local announcementId = HttpService:GenerateGUID(false)
	site.boss = BossService.Spawn(BossCatalog.Ritual.boss, site.position + Vector3.new(0, 0, 12), {
		source = BossCatalog.Sources.Ritual,
		onEnded = function()
			site.boss = nil
			site.prompt.Enabled = true
			AnnouncementService.End(announcementId)
		end,
	})
	AnnouncementService.Announce({
		id = announcementId,
		name = def.name .. " (ritual)",
		rarity = "Legendary",
		category = "Boss",
		kind = "Boss",
		position = site.position,
		radius = 60,
		endsAt = workspace:GetServerTimeNow() + 3600,
	})
end

local function begin(player: Player, site)
	if site.boss or site.summoner then
		InventoryService.Notify(player, "This altar is already in use.")
		return
	end
	if not CacheService.CanInteract(player, site.part, 12) then
		return
	end
	-- Consumed once, here, on the server.
	if not InventoryService.RemoveAll(player, BossCatalog.Ritual.offering) then
		InventoryService.Notify(player, "The ritual needs " .. offeringText() .. ".")
		return
	end
	site.summoner = player
	site.prompt.Enabled = false
	site.part.Color = Color3.fromRGB(255, 110, 40)
	summoning[player] = site
	InventoryService.Notify(player, "Summoning… stay close and don't get hit.")
	local seconds = BossCatalog.Ritual.summonSeconds
	local deadline = os.clock() + seconds
	task.spawn(function()
		while os.clock() < deadline do
			task.wait(0.25)
			if site.summoner ~= player then
				return
			end
			if not CacheService.CanInteract(player, site.part, RitualService.STAY_RADIUS) then
				RitualService.Interrupt(player)
				return
			end
		end
		summoning[player] = nil
		site.summoner = nil
		site.part.Color = Color3.fromRGB(80, 60, 90)
		summon(site)
	end)
end

-- A third party broke the ritual: the offering spills as contested loot.
function RitualService.Interrupt(player: Player)
	local site = summoning[player]
	if site == nil then
		return
	end
	summoning[player] = nil
	site.summoner = nil
	site.prompt.Enabled = true
	site.part.Color = Color3.fromRGB(80, 60, 90)
	spill(site)
	InventoryService.Notify(player, "The ritual was broken and the offering scattered.")
end

local function register(position: Vector3, name: string)
	local part = Instance.new("Part")
	part.Name = name
	part.Anchored = true
	part.Size = Vector3.new(6, 3, 6)
	part.Material = Enum.Material.Slate
	part.Color = Color3.fromRGB(80, 60, 90)
	part.CFrame = CFrame.new(position + Vector3.new(0, 1.5, 0))
	CollectionService:AddTag(part, "GeneratedStructure")
	part.Parent = workspace
	local prompt = Instance.new("ProximityPrompt")
	prompt.ActionText = "Offer " .. offeringText()
	prompt.ObjectText = "Ritual altar"
	prompt.HoldDuration = 2
	prompt.MaxActivationDistance = 10
	prompt.RequiresLineOfSight = false
	prompt.Parent = part
	local site = { part = part, prompt = prompt, position = position }
	prompt.Triggered:Connect(function(player)
		begin(player, site)
	end)
	table.insert(sites, site)
end

function RitualService.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	local tagged = CollectionService:GetTagged(RitualService.SITE_TAG)
	for _, part in tagged do
		if part:IsA("BasePart") then
			register(part.Position, part.Name)
		end
	end
	if #tagged == 0 then
		-- Placeholder altars in the inner ring until the island arrives (v0.15).
		local radius = (workspace:GetAttribute("FlintbornMapRadius") or RitualService.DEFAULT_MAP_RADIUS) * 0.45
		for index = 1, RitualService.PLACEHOLDER_SITES do
			local angle = (index / RitualService.PLACEHOLDER_SITES) * math.pi * 2 + 0.6
			local hit = workspace:Raycast(
				Vector3.new(math.cos(angle) * radius, 1000, math.sin(angle) * radius),
				Vector3.new(0, -2000, 0)
			)
			if hit then
				register(hit.Position, "Ritual Altar " .. index)
			end
		end
	end
	CombatService.Hurt:Connect(RitualService.Interrupt)
end

return RitualService
