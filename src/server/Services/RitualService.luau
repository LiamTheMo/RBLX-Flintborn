-- Ritual bosses (GDD §7.2, Q45). Placing the rare offering at a ritual altar
-- consumes it once on the server and starts a 10 s summoning that anyone can
-- interrupt: if the summoner is hit, downed or walks away, the offering spills on
-- the ground as contested loot. A completed summon is a world interaction, not
-- player magic, and is announced like any event. Each altar performs the ritual
-- of its map zone (BossCatalog.RitualFor): the Shattered Keep's summons the
-- Minotaur (GDD §54). The altar slab keeps the prompt; PropModels draws standing
-- stones, a bowl and runes on it, lit purple at rest and orange while a summoning
-- runs. World place only.

local CollectionService = game:GetService("CollectionService")
local HttpService = game:GetService("HttpService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local BiomeCatalog = require(ReplicatedStorage.Shared.World.BiomeCatalog)
local BossCatalog = require(ReplicatedStorage.Shared.Bosses.BossCatalog)
local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local ModelBuilder = require(ReplicatedStorage.Shared.Visuals.ModelBuilder)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local PoiCatalog = require(ReplicatedStorage.Shared.World.PoiCatalog)
local PropModels = require(ReplicatedStorage.Shared.Visuals.PropModels)
local WorldState = require(ReplicatedStorage.Shared.World.WorldState)
local AnnouncementService = require(script.Parent.AnnouncementService)
local BossService = require(script.Parent.BossService)
local CombatService = require(script.Parent.CombatService)
local DropService = require(script.Parent.DropService)
local InteractionService = require(script.Parent.InteractionService)
local InventoryService = require(script.Parent.InventoryService)

local RitualService = {}

RitualService.SITE_TAG = "RitualSite"
RitualService.STAY_RADIUS = 15
RitualService.PLACEHOLDER_SITES = 2
RitualService.DEFAULT_MAP_RADIUS = 1000
-- The altar's colours: the slab and the runes at rest, and everything while summoning.
RitualService.IDLE_COLOR = Color3.fromRGB(80, 60, 90)
RitualService.GLOW_COLOR = Color3.fromRGB(150, 90, 200)
RitualService.SUMMON_COLOR = Color3.fromRGB(255, 110, 40)

local sites = {}
local summoning = {}

local function offeringText(ritual): string
	local parts = {}
	for catalogId, quantity in ritual.offering do
		table.insert(parts, ("%d %s"):format(quantity, ItemCatalog.NameOf(catalogId)))
	end
	table.sort(parts)
	return table.concat(parts, ", ")
end

-- The offering spills exactly as it was placed.
local function spill(site)
	for _, stack in site.offering or {} do
		DropService.Spawn(stack, site.position)
	end
	site.offering = nil
end

local function summon(site)
	local def = BossCatalog.Get(site.ritual.boss)
	local announcementId = HttpService:GenerateGUID(false)
	site.boss = BossService.Spawn(site.ritual.boss, site.position + Vector3.new(0, 0, 12), {
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

-- Lights the altar for a summoning (or back to rest).
local function setSummoning(site, lit: boolean)
	site.part.Color = if lit then RitualService.SUMMON_COLOR else RitualService.IDLE_COLOR
	for _, piece in site.glow do
		piece.Color = if lit then RitualService.SUMMON_COLOR else RitualService.GLOW_COLOR
	end
end

local function begin(player: Player, site)
	if site.boss or site.summoner then
		InventoryService.Notify(player, "This altar is already in use.")
		return
	end
	if not InteractionService.CanInteract(player, site.part, 12) then
		return
	end
	-- Consumed once, here, on the server.
	local offering = InventoryService.TakeAll(player, site.ritual.offering)
	if offering == nil then
		InventoryService.Notify(player, "The ritual needs " .. offeringText(site.ritual) .. ".")
		return
	end
	site.offering = offering
	site.summoner = player
	site.prompt.Enabled = false
	setSummoning(site, true)
	summoning[player] = site
	InventoryService.Notify(player, "Summoning… stay close and don't get hit.")
	local seconds = site.ritual.summonSeconds
	local deadline = os.clock() + seconds
	task.spawn(function()
		while os.clock() < deadline do
			task.wait(0.25)
			if site.summoner ~= player then
				return
			end
			if not InteractionService.CanInteract(player, site.part, RitualService.STAY_RADIUS) then
				RitualService.Interrupt(player)
				return
			end
		end
		summoning[player] = nil
		site.summoner = nil
		site.offering = nil
		setSummoning(site, false)
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
	setSummoning(site, false)
	spill(site)
	InventoryService.Notify(player, "The ritual was broken and the offering scattered.")
end

-- The map zone an altar stands in: its PoiCatalog entry's, else the map's zone at
-- that spot (BiomeCatalog.ZoneAt), when the map provides one.
local function zoneOf(position: Vector3, name: string): string?
	for _, entry in PoiCatalog.RitualSites or {} do
		if entry.name == name and type(entry.zone) == "string" then
			return entry.zone
		end
	end
	if type(BiomeCatalog.ZoneAt) == "function" then
		local ok, zoneId = pcall(BiomeCatalog.ZoneAt, position.X, position.Z)
		if ok and type(zoneId) == "string" then
			return zoneId
		end
	end
	return nil
end

local function register(position: Vector3, name: string)
	local ritual = BossCatalog.RitualFor(zoneOf(position, name))
	local part = Instance.new("Part")
	part.Name = name
	part.Anchored = true
	part.Size = Vector3.new(6, 3, 6)
	part.Material = Enum.Material.Slate
	part.Color = RitualService.IDLE_COLOR
	part.CFrame = CFrame.new(position + Vector3.new(0, 1.5, 0))
	-- Generated ruins are never claimable (Q39); BuildingService marked the map's tagged
	-- parts at Start, before this altar existed.
	part:SetAttribute("Generated", true)
	CollectionService:AddTag(part, "GeneratedStructure")
	part.Parent = workspace
	local glow = {}
	for _, piece in ModelBuilder.Decorate(part, PropModels.Altar, { anchored = true }) do
		if piece.Name == PropModels.ALTAR_GLOW then
			piece.Color = RitualService.GLOW_COLOR
			table.insert(glow, piece)
		end
	end
	local prompt = Instance.new("ProximityPrompt")
	prompt.ActionText = "Offer " .. offeringText(ritual)
	prompt.ObjectText = BossCatalog.Get(ritual.boss).name .. " altar"
	prompt.HoldDuration = 2
	prompt.MaxActivationDistance = 10
	prompt.RequiresLineOfSight = false
	prompt.Parent = part
	local site = { part = part, prompt = prompt, position = position, ritual = ritual, glow = glow }
	prompt.Triggered:Connect(function(player)
		begin(player, site)
	end)
	table.insert(sites, site)
end

function RitualService.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	-- Altars are the map's tagged parts, so they wait for the map.
	task.spawn(function()
		WorldState.WaitUntilReady()
		local tagged = CollectionService:GetTagged(RitualService.SITE_TAG)
		for _, part in tagged do
			if part:IsA("BasePart") then
				-- The marker's base is the ground; the altar stands on it.
				register(part.Position - Vector3.new(0, part.Size.Y / 2, 0), part.Name)
			end
		end
		if #tagged == 0 then
			-- Placeholder altars in the inner ring until the island arrives (v0.15).
			local radius = WorldState.MapRadius(RitualService.DEFAULT_MAP_RADIUS) * 0.45
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
	end)
	CombatService.Hurt:Connect(RitualService.Interrupt)
end

return RitualService
