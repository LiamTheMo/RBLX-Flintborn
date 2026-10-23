-- The Guardian of the Center Crater (GDD §3, §8). Every 15–20 minutes after the
-- previous encounter ends, a Horn of War sounds 3 minutes ahead. Phase I: the
-- Guardian is shielded until its energy pillars fall. Phase II: the gauntlet.
-- Phase III: at 25% HP it releases one Legendary on the ground, once per
-- encounter, and whoever carries it is highlighted. Player structures near the
-- arena are destroyed so they cannot cheese it. Everything stays contested.
-- World place only.

local CollectionService = game:GetService("CollectionService")
local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local BossCatalog = require(ReplicatedStorage.Shared.Bosses.BossCatalog)
local BossRules = require(ReplicatedStorage.Shared.Bosses.BossRules)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local BossService = require(script.Parent.BossService)
local BuildingService = require(script.Parent.BuildingService)
local DropService = require(script.Parent.DropService)
local InventoryService = require(script.Parent.InventoryService)
local NpcService = require(script.Parent.NpcService)

local GuardianService = {}

GuardianService.ARENA_TAG = "GuardianArena"
GuardianService.ARENA_RADIUS = 80
GuardianService.PILLAR_RING = 30
GuardianService.HORN_SOUND = "rbxasset://sounds/electronicpingshort.wav"
-- Studio compresses the schedule so the encounter can be tried quickly.
GuardianService.STUDIO_FIRST_HORN = 30
GuardianService.STUDIO_HORN_LEAD = 30

local released = {}
local state = { encounter = nil, horn = nil }
local rng = Random.new()

local function now(): number
	return workspace:GetServerTimeNow()
end

local function arenaCenter(): Vector3?
	local tagged = CollectionService:GetTagged(GuardianService.ARENA_TAG)[1]
	if tagged and tagged:IsA("BasePart") then
		return tagged.Position
	end
	local hit = workspace:Raycast(Vector3.new(0, 1000, 0), Vector3.new(0, -2000, 0))
	return hit and hit.Position or nil
end

local function alert(payload)
	Remotes.Get("BossAlert"):FireAllClients(payload)
end

local function hornSound(center: Vector3)
	local holder = Instance.new("Part")
	holder.Anchored = true
	holder.CanCollide = false
	holder.CanQuery = false
	holder.Transparency = 1
	holder.CFrame = CFrame.new(center + Vector3.new(0, 20, 0))
	holder.Parent = workspace
	local sound = Instance.new("Sound")
	sound.SoundId = GuardianService.HORN_SOUND
	sound.Volume = 3
	sound.PlaybackSpeed = 0.5
	sound.RollOffMode = Enum.RollOffMode.Linear
	sound.RollOffMaxDistance = 2000
	sound.Parent = holder
	sound:Play()
	task.delay(5, function()
		holder:Destroy()
	end)
end

local function spawnPillars(encounter, center: Vector3)
	local spec = encounter.boss.def.pillars
	for index = 1, spec.count do
		local angle = (index / spec.count) * math.pi * 2
		local body = Instance.new("Part")
		body.Name = "Energy Pillar"
		body.Anchored = true
		body.Size = Vector3.new(4, 16, 4)
		body.Material = Enum.Material.Neon
		body.Color = Color3.fromRGB(120, 200, 255)
		body.CFrame = CFrame.new(
			center
				+ Vector3.new(
					math.cos(angle) * GuardianService.PILLAR_RING,
					8,
					math.sin(angle) * GuardianService.PILLAR_RING
				)
		)
		body.Parent = encounter.folder
		local health = spec.health * encounter.boss.multiplier
		encounter.pillars[index] = NpcService.Register({
			body = body,
			name = "Energy Pillar",
			health = health,
			maxHealth = health,
			onKilled = function()
				encounter.pillarsLeft -= 1
				encounter.boss.npc.body:SetAttribute("PillarsLeft", encounter.pillarsLeft)
				if encounter.pillarsLeft <= 0 and state.encounter == encounter then
					-- Phase II: the shield drops (pillar shielding is boss-only, §8.1).
					BossService.SetShielded(encounter.boss, false)
					BossService.SetPhase(encounter.boss, "Gauntlet")
					alert({ kind = "Phase", phase = "Gauntlet" })
				end
			end,
		})
	end
	encounter.pillarsLeft = spec.count
	encounter.boss.npc.body:SetAttribute("PillarsLeft", spec.count)
end

local function releaseLegendary(encounter)
	if not BossRules.ReleaseLegendary(released, encounter.boss.id) then
		return
	end
	local body = encounter.boss.npc.body
	local at = body.Position - Vector3.new(0, body.Size.Y / 2, 0) + Vector3.new(0, 0, body.Size.Z)
	DropService.Spawn({
		instanceId = HttpService:GenerateGUID(false),
		catalogId = encounter.boss.def.legendary,
		qualityRoll = 0,
		location = "WorldDropped",
	}, at)
	BossService.SetPhase(encounter.boss, "Final")
	alert({ kind = "Legendary", position = at })
end

local schedule

local function endEncounter(encounter)
	if state.encounter ~= encounter then
		return
	end
	state.encounter = nil
	for _, pillar in encounter.pillars do
		NpcService.Despawn(pillar)
	end
	encounter.folder:Destroy()
	alert({ kind = "Ended" })
	schedule(now())
end

local function spawnGuardian()
	local center = arenaCenter()
	if center == nil then
		warn("[GuardianService] No ground at the Center Crater; trying again later")
		schedule(now())
		return
	end
	BuildingService.ClearWithin(center, GuardianService.ARENA_RADIUS)
	local folder = Instance.new("Folder")
	folder.Name = "GuardianArena"
	folder.Parent = workspace
	local encounter = { folder = folder, center = center, pillars = {} }
	state.encounter = encounter
	encounter.boss = BossService.Spawn("Guardian", center, {
		source = BossCatalog.Sources.Guardian,
		shielded = true,
		onDamaged = function(boss, before, after)
			if BossRules.CrossesLegendary(before, after, boss.npc.maxHealth) then
				releaseLegendary(encounter)
			end
		end,
		onEnded = function()
			endEncounter(encounter)
		end,
	})
	BossService.SetPhase(encounter.boss, "Pillars")
	spawnPillars(encounter, center)
	alert({ kind = "Spawned", position = center })
end

-- Arms the next horn and spawn, counted from when the last encounter ended.
function schedule(endedAt: number)
	local plan = BossRules.GuardianSchedule(endedAt, rng)
	local override = workspace:GetAttribute("FlintbornGuardianSeconds")
	if override or RunService:IsStudio() then
		local delay = override or GuardianService.STUDIO_FIRST_HORN + GuardianService.STUDIO_HORN_LEAD
		plan = { hornAt = endedAt + delay - GuardianService.STUDIO_HORN_LEAD, spawnAt = endedAt + delay }
	end
	state.horn = plan
	task.delay(math.max(0, plan.hornAt - now()), function()
		if state.horn ~= plan then
			return
		end
		local center = arenaCenter()
		if center then
			hornSound(center)
		end
		alert({ kind = "Horn", spawnAt = plan.spawnAt, position = center })
		task.delay(math.max(0, plan.spawnAt - now()), function()
			if state.horn == plan then
				state.horn = nil
				spawnGuardian()
			end
		end)
	end)
end

-- Burden of wealth (§25.4): anyone carrying the Guardian's Legendary glows.
local function highlightCarriers()
	local legendary = BossCatalog.Bosses.Guardian.legendary
	for _, player in Players:GetPlayers() do
		local character = player.Character
		if character then
			local carrying = false
			for _, item in InventoryService.Items(player) do
				if item.catalogId == legendary then
					carrying = true
					break
				end
			end
			local highlight = character:FindFirstChild("LegendaryCarrier")
			if carrying and highlight == nil then
				highlight = Instance.new("Highlight")
				highlight.Name = "LegendaryCarrier"
				highlight.FillColor = Color3.fromRGB(240, 170, 40)
				highlight.OutlineColor = Color3.fromRGB(255, 230, 150)
				highlight.FillTransparency = 0.6
				highlight.Parent = character
			elseif not carrying and highlight then
				highlight:Destroy()
			end
		end
	end
end

function GuardianService.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	schedule(now())
	-- A countdown already running is shown to late arrivals too.
	Players.PlayerAdded:Connect(function(player)
		if state.horn and now() >= state.horn.hornAt then
			Remotes.Get("BossAlert"):FireClient(player, { kind = "Horn", spawnAt = state.horn.spawnAt })
		end
	end)
	task.spawn(function()
		while true do
			task.wait(2)
			highlightCarriers()
			local encounter = state.encounter
			if encounter then
				-- Structures built near the arena during the fight are destroyed too.
				BuildingService.ClearWithin(encounter.center, GuardianService.ARENA_RADIUS)
			end
		end
	end)
end

return GuardianService
