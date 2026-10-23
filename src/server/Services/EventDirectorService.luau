-- The world event director (GDD §7, Q42–48, Q111–112, Q140–143). About every five
-- minutes each category rolls on its own; whatever triggers is placed at a random
-- valid spot in its biome, kept apart from other event footprints and inside the
-- server's budget, announced to everyone, and cleaned up when claimed or expired.
-- Rare nodes pay out once and never regrow; generated ruins are never claimable.
-- The Guardian keeps its own schedule (v0.12). World place only.

local CollectionService = game:GetService("CollectionService")
local HttpService = game:GetService("HttpService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local EventCatalog = require(ReplicatedStorage.Shared.Events.EventCatalog)
local EventRules = require(ReplicatedStorage.Shared.Events.EventRules)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Rarity = require(ReplicatedStorage.Shared.Items.Rarity)
local AnnouncementService = require(script.Parent.AnnouncementService)
local BossService = require(script.Parent.BossService)
local CacheService = require(script.Parent.CacheService)
local DropService = require(script.Parent.DropService)
local InventoryService = require(script.Parent.InventoryService)
local MeteorService = require(script.Parent.MeteorService)
local ModifierService = require(script.Parent.ModifierService)
local NpcService = require(script.Parent.NpcService)
local ProgressionService = require(script.Parent.ProgressionService)

local EventDirectorService = {}

EventDirectorService.DEFAULT_MAP_RADIUS = 1000
EventDirectorService.PLACEMENT_ATTEMPTS = 10
-- Studio ticks faster so events can be tried without waiting five minutes.
EventDirectorService.STUDIO_TICK_SECONDS = 45
EventDirectorService.NODE_HARVEST_SECONDS = 3
EventDirectorService.GENERATED_TAG = "GeneratedStructure"

-- Spawn counts by category and rarity, for analytics in v0.17 (§7.5).
EventDirectorService.Stats = {}

local events = {}
local folder = nil
local rng = Random.new()

local function now(): number
	return workspace:GetServerTimeNow()
end

local function activeFootprints()
	local list = {}
	for _, event in events do
		table.insert(list, { position = event.position, radius = event.entry.footprint })
	end
	return list
end

local function groundAt(x: number, z: number): Vector3?
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	params.FilterDescendantsInstances = { folder }
	local hit = workspace:Raycast(Vector3.new(x, 1000, z), Vector3.new(0, -2000, 0), params)
	if hit and hit.Material ~= Enum.Material.Water and hit.Position.Y > -50 then
		return hit.Position
	end
	return nil
end

-- A random spot in the entry's biome that keeps clear of other footprints.
local function place(entry): Vector3?
	local mapRadius = workspace:GetAttribute("FlintbornMapRadius") or EventDirectorService.DEFAULT_MAP_RADIUS
	local footprints = activeFootprints()
	for _ = 1, EventDirectorService.PLACEMENT_ATTEMPTS do
		local angle = rng:NextNumber(0, math.pi * 2)
		local distance = EventRules.BiomeDistance(entry.biome, rng) * mapRadius
		local position = groundAt(math.cos(angle) * distance, math.sin(angle) * distance)
		if position and EventRules.Separated(position, entry.footprint, footprints) then
			return position
		end
	end
	return nil
end

local function finish(event)
	if events[event.id] ~= event then
		return
	end
	events[event.id] = nil
	for npc in event.npcs do
		NpcService.Despawn(npc)
	end
	if event.boss then
		-- Event and structure bosses leave with their event (Q46).
		BossService.Despawn(event.boss, "EventEnded")
	end
	event.model:Destroy()
	AnnouncementService.End(event.id)
end

local function spill(loot, position: Vector3, luck: number?)
	for _, item in EventRules.RollLoot(loot, rng, luck) do
		DropService.Spawn(item, position + Vector3.new(rng:NextNumber(-3, 3), 0, rng:NextNumber(-3, 3)))
	end
end

-- A one-time rare node: harvested once, never regrows (Q112).
local function spawnNode(event, loot, position: Vector3, tool: string?, onClaimed)
	local isOre = tool == "Pickaxe"
	local part = Instance.new("Part")
	part.Name = event.entry.name
	part.Anchored = true
	part.Shape = if isOre then Enum.PartType.Block else Enum.PartType.Ball
	part.Size = if isOre then Vector3.new(6, 5, 6) else Vector3.new(4, 4, 4)
	part.Material = if isOre then Enum.Material.Slate else Enum.Material.Grass
	part.Color = Rarity.Colors[event.entry.rarity] or Color3.new(1, 1, 1)
	part.CFrame = CFrame.new(position + Vector3.new(0, part.Size.Y / 2, 0))
	part.Parent = event.model
	local prompt = Instance.new("ProximityPrompt")
	prompt.ActionText = if isOre then "Mine" else "Harvest"
	prompt.ObjectText = ("%s · %s"):format(event.entry.name, event.entry.rarity)
	prompt.HoldDuration = EventDirectorService.NODE_HARVEST_SECONDS
	prompt.MaxActivationDistance = 8
	prompt.RequiresLineOfSight = false
	prompt.Parent = part
	local site = {}
	prompt.Triggered:Connect(function(player)
		if not CacheService.CanInteract(player, part, 10) then
			return
		end
		local equipped = InventoryService.EquippedTool(player)
		if tool and (equipped == nil or equipped.kind ~= tool) then
			InventoryService.Notify(player, "You need a " .. string.lower(tool) .. " for that.")
			return
		end
		if EventRules.Claim(site) then
			part:Destroy()
			spill(loot, position, ModifierService.Sum(player, "Luck"))
			ProgressionService.GrantXp(player, "RareNode", event.entry.name)
			onClaimed()
		end
	end)
end

local function spawnGroup(event, group, center: Vector3)
	for _, member in group do
		for _ = 1, member.count do
			local offset = Vector3.new(rng:NextNumber(-8, 8), 0, rng:NextNumber(-8, 8))
			local position = groundAt(center.X + offset.X, center.Z + offset.Z) or center
			local npc = NpcService.Spawn(member.enemy, position, member.elite, event.id)
			event.npcs[npc] = true
		end
	end
end

-- Generated raidable structures (Q47): never claimable by players.
local function spawnStructure(event, position: Vector3)
	local entry = event.entry
	local style = entry.style
	local material = if style == "Ruin" then Enum.Material.Cobblestone else Enum.Material.WoodPlanks
	local radius, segments = 16, 10
	for index = 1, segments do
		-- Leave a doorway gap so the inside is reachable without breaking walls.
		if index ~= 1 and (style ~= "Ruin" or index % 3 ~= 0) then
			local angle = (index / segments) * math.pi * 2
			local wall = Instance.new("Part")
			wall.Name = "GeneratedWall"
			wall.Anchored = true
			wall.Material = material
			wall.Color = if style == "Ruin" then Color3.fromRGB(120, 116, 108) else Color3.fromRGB(110, 80, 50)
			wall.Size = Vector3.new(10, if style == "Ruin" then rng:NextNumber(3, 7) else 9, 1.5)
			local at = position + Vector3.new(math.cos(angle) * radius, wall.Size.Y / 2, math.sin(angle) * radius)
			wall.CFrame = CFrame.lookAt(at, Vector3.new(position.X, at.Y, position.Z))
			wall:SetAttribute("Generated", true)
			CollectionService:AddTag(wall, EventDirectorService.GENERATED_TAG)
			wall.Parent = event.model
		end
	end
	if entry.cache then
		CacheService.Spawn(EventCatalog.Get(entry.cache), position, event.model, function() end)
	end
	if entry.loot then
		spawnNode(event, entry.loot, position, nil, function() end)
	end
	if entry.defenders then
		spawnGroup(event, entry.defenders, position)
	end
	if entry.boss then
		event.boss = BossService.Spawn(entry.boss, position + Vector3.new(0, 0, 6), {
			source = "Structure",
			structureGone = function()
				return events[event.id] ~= event
			end,
		})
	end
end

local function start(entry): boolean
	local large = 0
	for _, event in events do
		if event.entry.footprint >= EventRules.LARGE_FOOTPRINT then
			large += 1
		end
	end
	local npcCount = EventRules.NpcCount(entry.group) + EventRules.NpcCount(entry.defenders)
	if not EventRules.WithinBudget(entry, large, NpcService.Count(), npcCount) then
		return false
	end
	local position = place(entry)
	if position == nil then
		return false
	end
	local model = Instance.new("Model")
	model.Name = entry.name
	model.Parent = folder
	local event = {
		id = HttpService:GenerateGUID(false),
		entry = entry,
		position = position,
		model = model,
		npcs = {},
		endsAt = now() + entry.lifetime,
	}
	events[event.id] = event
	local function done()
		finish(event)
	end
	local kind = entry.kind
	if kind == EventCatalog.Kinds.Node then
		spawnNode(event, entry.loot, position, entry.tool, done)
	elseif kind == EventCatalog.Kinds.Cache then
		CacheService.Spawn(entry, position, model, done)
	elseif kind == EventCatalog.Kinds.Meteor then
		MeteorService.Spawn(entry, position, model, done)
	elseif kind == EventCatalog.Kinds.Npc then
		spawnGroup(event, entry.group, position)
	elseif kind == EventCatalog.Kinds.Structure then
		spawnStructure(event, position)
	elseif kind == EventCatalog.Kinds.Boss then
		event.boss = BossService.Spawn(entry.boss, position, {
			source = "Event",
			expired = function()
				return events[event.id] ~= event
			end,
			onEnded = function(_, reason)
				if reason == "Defeated" then
					event.boss = nil
					done()
				end
			end,
		})
	end
	AnnouncementService.Announce({
		id = event.id,
		name = entry.name,
		rarity = entry.rarity,
		category = entry.category,
		kind = kind,
		position = position,
		radius = entry.footprint,
		endsAt = event.endsAt,
	})
	task.delay(entry.lifetime, done)
	local key = entry.category .. ":" .. entry.rarity
	EventDirectorService.Stats[key] = (EventDirectorService.Stats[key] or 0) + 1
	return true
end

-- One director tick: every category rolls independently (Q141).
function EventDirectorService.Tick()
	for _, entry in EventRules.RollTick(EventCatalog.Entries, EventCatalog.Categories, rng) do
		if not start(entry) then
			warn(("[EventDirector] Skipped %s: no valid place or over budget"):format(entry.name))
		end
	end
end

function EventDirectorService.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	folder = Instance.new("Folder")
	folder.Name = "WorldEvents"
	folder.Parent = workspace
	-- An NPC event ends once its whole group is dead.
	NpcService.Died:Connect(function(npc)
		local event = npc.eventId and events[npc.eventId]
		if event then
			event.npcs[npc] = nil
			if event.entry.kind == EventCatalog.Kinds.Npc and next(event.npcs) == nil then
				finish(event)
			end
		end
	end)
	task.spawn(function()
		while true do
			local seconds = workspace:GetAttribute("FlintbornEventSeconds")
				or (if RunService:IsStudio() then EventDirectorService.STUDIO_TICK_SECONDS else EventRules.TICK_SECONDS)
			task.wait(seconds)
			EventDirectorService.Tick()
		end
	end)
end

return EventDirectorService
