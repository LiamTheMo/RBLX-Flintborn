-- Extraction (GDD §9, Q17–24, Q118–119, Q158). Each world activates a subset of the
-- fixed portal sites (always including the Center). Any at-risk player can start a
-- shared 120 s countdown that everyone can see; players may roam, fight and heal,
-- and only living, non-downed players inside the zone at zero extract (strangers
-- included; the activator's fate is irrelevant). Portable runes run 30 s anywhere
-- except inside structures and never grant the Center bonus. World place only.

local CollectionService = game:GetService("CollectionService")
local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local ExtractionRules = require(ReplicatedStorage.Shared.Extraction.ExtractionRules)
local GameConstants = require(ReplicatedStorage.Shared.GameConstants)
local InventoryRules = require(ReplicatedStorage.Shared.Inventory.InventoryRules)
local ItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local ProfileSchema = require(ReplicatedStorage.Shared.Data.ProfileSchema)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local DownedService = require(script.Parent.DownedService)
local InventoryService = require(script.Parent.InventoryService)
local ProfileService = require(script.Parent.ProfileService)
local TravelService = require(script.Parent.TravelService)
local WorldAdmissionService = require(script.Parent.WorldAdmissionService)

local ExtractionService = {}

ExtractionService.SITE_TAG = "PortalSite"
ExtractionService.STRUCTURE_TAGS = { "Workbench", "Structure" }
ExtractionService.ACTIVE_FIXED_SITES = 2
ExtractionService.DEFAULT_ZONE_RADIUS = { Fixed = 12, Center = 8, Portable = 10 }
ExtractionService.COOLDOWN_SECONDS = 60
ExtractionService.ANIMATION_SECONDS = 3
ExtractionService.DEFAULT_MAP_RADIUS = 1000
ExtractionService.ALERT_RADIUS = 400
ExtractionService.ALERT_SOUND = "rbxasset://sounds/electronicpingshort.wav"

local sites = {}
local activeEvents = {}
local rng = Random.new()

local function now(): number
	return workspace:GetServerTimeNow()
end

local function rootOf(player: Player)
	return player.Character and player.Character:FindFirstChild("HumanoidRootPart")
end

local function aliveHumanoid(player: Player): Humanoid?
	local humanoid = player.Character and player.Character:FindFirstChildOfClass("Humanoid")
	return humanoid and humanoid.Health > 0 and humanoid or nil
end

local function eventView(event)
	return {
		id = event.id,
		name = event.name,
		kind = event.kind,
		position = event.center,
		radius = event.radius,
		endsAt = event.endsAt,
	}
end

local function beacon(position: Vector3, radius: number)
	local model = Instance.new("Model")
	model.Name = "ExtractionBeacon"
	local column = Instance.new("Part")
	column.Anchored = true
	column.CanCollide = false
	column.CanQuery = false
	column.Material = Enum.Material.Neon
	column.Color = Color3.fromRGB(120, 220, 255)
	column.Transparency = 0.35
	column.Size = Vector3.new(2, 400, 2)
	column.CFrame = CFrame.new(position + Vector3.new(0, 200, 0))
	column.Parent = model
	local zone = Instance.new("Part")
	zone.Anchored = true
	zone.CanCollide = false
	zone.CanQuery = false
	zone.Shape = Enum.PartType.Cylinder
	zone.Material = Enum.Material.ForceField
	zone.Color = Color3.fromRGB(120, 220, 255)
	zone.Size = Vector3.new(0.4, radius * 2, radius * 2)
	zone.CFrame = CFrame.new(position) * CFrame.Angles(0, 0, math.rad(90))
	zone.Parent = model
	local light = Instance.new("PointLight")
	light.Brightness = 4
	light.Range = 60
	light.Color = column.Color
	light.Parent = column
	model.Parent = workspace
	-- Large-radius audio cue so rivals can contest the exit (Q20).
	local alert = Instance.new("Sound")
	alert.SoundId = ExtractionService.ALERT_SOUND
	alert.Volume = 2
	alert.RollOffMode = Enum.RollOffMode.Linear
	alert.RollOffMaxDistance = ExtractionService.ALERT_RADIUS
	alert.Parent = zone
	alert:Play()
	return model
end

-- Settles one qualified player: their items move into their profile exactly once,
-- then they become protected and travel to the lobby.
local function extractPlayer(player: Player, event)
	-- Settlement and the protected transition happen without yielding in between, so
	-- the run cannot end (and drop its items) after the items were already banked.
	if not WorldAdmissionService.IsAtRisk(player) then
		return
	end
	local items = ProfileSchema.DeepCopy(InventoryService.Items(player))
	-- Operation IDs are per profile, so the event ID alone is unique for this player.
	local receiptId = "extract:" .. event.id
	local ok, err = ProfileService.RunOperation(player, receiptId, "Extraction", function(profile)
		local receipt = ExtractionRules.Settle(profile, items, event.kind, receiptId, os.time())
		receipt.portal = event.name
		return receipt
	end)
	if not ok then
		warn(("[ExtractionService] Settlement failed for %s: %s"):format(player.Name, tostring(err)))
		InventoryService.Notify(player, "Extraction failed to save. You are still in the run.")
		return
	end
	WorldAdmissionService.Extract(player)
	local root = rootOf(player)
	if root then
		root.Anchored = true
	end
	ProfileService.SaveNow(player)
	task.delay(ExtractionService.ANIMATION_SECONDS, function()
		if player.Parent then
			TravelService.ToLobby({ player })
		end
	end)
end

local function resolve(event)
	activeEvents[event.id] = nil
	if event.visual then
		event.visual:Destroy()
	end
	Remotes.Get("ExtractionEnded"):FireAllClients(event.id)
	for _, player in Players:GetPlayers() do
		local root = rootOf(player)
		local candidate = {
			alive = aliveHumanoid(player) ~= nil,
			downed = DownedService.IsDowned(player),
			atRisk = WorldAdmissionService.IsAtRisk(player),
			inZone = root ~= nil and ExtractionRules.InZone(root.Position, event.center, event.radius),
		}
		if ExtractionRules.Qualifies(candidate) then
			task.spawn(extractPlayer, player, event)
		end
	end
	if event.site then
		event.site.coolingUntil = now() + ExtractionService.COOLDOWN_SECONDS
		event.site.event = nil
	end
end

local function startEvent(kind: string, center: Vector3, radius: number, name: string, site)
	local duration = if kind == ExtractionRules.Kinds.Portable
		then ExtractionRules.PORTABLE_SECONDS
		else ExtractionRules.FIXED_SECONDS
	local event = {
		id = HttpService:GenerateGUID(false),
		kind = kind,
		center = center,
		radius = radius,
		name = name,
		site = site,
		endsAt = now() + duration,
	}
	event.visual = beacon(center, radius)
	activeEvents[event.id] = event
	if site then
		site.event = event
	end
	-- Announced to everyone: the large-radius cue lets rivals contest it (Q20).
	Remotes.Get("ExtractionEvent"):FireAllClients(eventView(event))
	task.delay(duration, resolve, event)
	return event
end

local function canStart(player: Player): boolean
	return WorldAdmissionService.IsAtRisk(player)
		and aliveHumanoid(player) ~= nil
		and not DownedService.IsDowned(player)
end

local function registerSite(position: Vector3, kind: string, radius: number, name: string)
	local portal = Instance.new("Part")
	portal.Name = name
	portal.Anchored = true
	portal.CanCollide = false
	portal.Shape = Enum.PartType.Cylinder
	portal.Material = Enum.Material.Neon
	portal.Color = if kind == ExtractionRules.Kinds.Center
		then Color3.fromRGB(255, 170, 60)
		else Color3.fromRGB(120, 220, 255)
	portal.Size = Vector3.new(0.6, 6, 6)
	portal.CFrame = CFrame.new(position + Vector3.new(0, 0.3, 0)) * CFrame.Angles(0, 0, math.rad(90))
	portal:SetAttribute("PortalKind", kind)
	portal.Parent = workspace
	local prompt = Instance.new("ProximityPrompt")
	prompt.ActionText = "Start extraction"
	prompt.ObjectText = name .. (kind == ExtractionRules.Kinds.Center and " (2× materials)" or "")
	prompt.HoldDuration = 1
	prompt.MaxActivationDistance = 10
	prompt.RequiresLineOfSight = false
	prompt.Parent = portal
	local site = { name = name, kind = kind, center = position, radius = radius, part = portal }
	prompt.Triggered:Connect(function(player)
		if not canStart(player) then
			return
		end
		if site.event then
			InventoryService.Notify(player, "This extraction is already counting down.")
		elseif site.coolingUntil and now() < site.coolingUntil then
			InventoryService.Notify(player, "This portal is recharging.")
		else
			startEvent(kind, position, radius, name, site)
		end
	end)
	table.insert(sites, site)
end

local function groundAt(x: number, z: number): Vector3?
	local hit = workspace:Raycast(Vector3.new(x, 1000, z), Vector3.new(0, -2000, 0))
	return hit and hit.Position or nil
end

-- Uses map sites tagged PortalSite (attributes Kind, ZoneRadius); otherwise lays out
-- placeholder sites until the real map arrives (v0.15).
local function setupSites()
	local candidates = {}
	local center = nil
	for _, part in CollectionService:GetTagged(ExtractionService.SITE_TAG) do
		if part:IsA("BasePart") then
			local kind = part:GetAttribute("Kind") or ExtractionRules.Kinds.Fixed
			local entry = {
				position = part.Position,
				kind = kind,
				radius = part:GetAttribute("ZoneRadius") or ExtractionService.DEFAULT_ZONE_RADIUS[kind] or 12,
				name = part.Name,
			}
			if kind == ExtractionRules.Kinds.Center then
				center = entry
			else
				table.insert(candidates, entry)
			end
		end
	end
	if center == nil and #candidates == 0 then
		local radius = (workspace:GetAttribute("FlintbornMapRadius") or ExtractionService.DEFAULT_MAP_RADIUS) * 0.6
		local origin = groundAt(0, 0)
		if origin then
			center = { position = origin, kind = "Center", radius = 8, name = "Center Crater Portal" }
		end
		for index = 1, 6 do
			local angle = (index / 6) * math.pi * 2
			local position = groundAt(math.cos(angle) * radius, math.sin(angle) * radius)
			if position then
				table.insert(
					candidates,
					{ position = position, kind = "Fixed", radius = 12, name = "Portal " .. index }
				)
			end
		end
	end
	if center then
		registerSite(center.position, center.kind, center.radius, center.name)
	end
	-- A different random subset of the fixed candidates is active in each world (Q22).
	for _ = 1, math.min(ExtractionService.ACTIVE_FIXED_SITES, #candidates) do
		local entry = table.remove(candidates, rng:NextInteger(1, #candidates))
		registerSite(entry.position, entry.kind, entry.radius, entry.name)
	end
end

local function insideStructure(position: Vector3): boolean
	for _, part in workspace:GetPartBoundsInRadius(position, 6) do
		for _, tag in ExtractionService.STRUCTURE_TAGS do
			if CollectionService:HasTag(part, tag) or (part.Parent and CollectionService:HasTag(part.Parent, tag)) then
				return true
			end
		end
	end
	return false
end

local function placeRune(player: Player, hotbarIndex: any)
	if type(hotbarIndex) ~= "number" or not canStart(player) then
		return false, "NotInRun"
	end
	local inventory = InventoryService.Get(player)
	local entry = inventory and InventoryRules.At(inventory, "hotbar", hotbarIndex)
	local def = entry and ItemCatalog.Get(entry.catalogId)
	if def == nil or def.placeable ~= "ExtractionRune" then
		return false, "NotARune"
	end
	local root = rootOf(player)
	local ground = root and workspace:Raycast(root.Position, Vector3.new(0, -12, 0))
	if ground == nil then
		return false, "NoGround"
	end
	if insideStructure(ground.Position) then
		return false, "InsideStructure"
	end
	for _, event in activeEvents do
		-- Overlapping zones would let one rune piggyback on another's countdown.
		if
			(event.center - ground.Position).Magnitude
			< event.radius + ExtractionService.DEFAULT_ZONE_RADIUS.Portable
		then
			return false, "TooCloseToExtraction"
		end
	end
	if not InventoryService.RemoveAll(player, { [entry.catalogId] = 1 }) then
		return false, "NotCarried"
	end
	startEvent(
		ExtractionRules.Kinds.Portable,
		ground.Position,
		ExtractionService.DEFAULT_ZONE_RADIUS.Portable,
		player.DisplayName .. "'s rune",
		nil
	)
	return true, nil
end

-- No-build auras (GDD §3.1): every active fixed portal plus every running rune.
function ExtractionService.Auras()
	local radius = GameConstants.PORTAL_NO_BUILD_METERS * GameConstants.STUDS_PER_METER
	local auras = {}
	for _, site in sites do
		table.insert(auras, { center = site.center, radius = radius })
	end
	for _, event in activeEvents do
		if event.site == nil then
			table.insert(auras, { center = event.center, radius = radius })
		end
	end
	return auras
end

function ExtractionService.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	setupSites()
	Remotes.Get("PlaceRune").OnServerInvoke = placeRune
	-- Late joiners still see countdowns already running.
	WorldAdmissionService.RunStarted:Connect(function(player)
		for _, event in activeEvents do
			Remotes.Get("ExtractionEvent"):FireClient(player, eventView(event))
		end
	end)
end

return ExtractionService
