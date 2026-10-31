-- Health, stamina and food for players in an active run (GDD §4.3, §5.4). One
-- Heartbeat loop steps every meter on the server; clients only send sprint
-- intent. Whether a player is moving (and so whether a sprint drains
-- stamina) comes from server-observed root travel, never the client-replicated
-- MoveDirection, and travel at sprint pace drains stamina even without a sprint
-- request. Walking through water is 30% slower (GDD §55): the server checks for
-- water at each player's feet a few times a second and folds it into the walk
-- speed it sets. Nobody swims: the Swimming state is off for every character.
-- Meters are run state and reset on each spawn. World place only.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local GameConstants = require(ReplicatedStorage.Shared.GameConstants)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local SurvivalRules = require(ReplicatedStorage.Shared.Survival.SurvivalRules)
local WorldState = require(ReplicatedStorage.Shared.World.WorldState)
local ModifierService = require(script.Parent.ModifierService)
local WorldAdmissionService = require(script.Parent.WorldAdmissionService)

local SurvivalService = {}

SurvivalService.PUBLISH_INTERVAL = 0.1
-- Root travel is sampled over this window; faster than MOVING_SPEED counts as moving.
SurvivalService.MOVE_SAMPLE_SECONDS = 0.2
SurvivalService.MOVING_SPEED = 2
-- How often each player's feet are checked for water.
SurvivalService.WATER_CHECK_SECONDS = 0.2

local entries = {}

local function now(): number
	return workspace:GetServerTimeNow()
end

function SurvivalService.Get(player: Player)
	local entry = entries[player]
	return entry and entry.rules or nil
end

function SurvivalService.Humanoid(player: Player): Humanoid?
	local entry = entries[player]
	return entry and entry.humanoid or nil
end

-- Sets health without it counting as damage (healing paths use this).
function SurvivalService.SetHealth(player: Player, health: number)
	local entry = entries[player]
	if entry == nil or entry.humanoid.Health <= 0 then
		return
	end
	local clamped = math.clamp(health, 0, entry.humanoid.MaxHealth)
	entry.lastHealth = clamped
	entry.humanoid.Health = clamped
end

local function publish(player: Player, entry)
	local rules = entry.rules
	player:SetAttribute("Stamina", math.round(rules.stamina * 100) / 100)
	player:SetAttribute("Food", math.round(rules.food * 1000) / 1000)
	player:SetAttribute("Sprinting", entry.sprinting)
	player:SetAttribute("MedicineLockUntil", rules.medicineLockUntil)
	player:SetAttribute("FoodHealing", math.round(SurvivalRules.PendingFoodHealing(rules)))
end

local function startRun(player: Player, character: Model)
	local humanoid = character:FindFirstChildOfClass("Humanoid")
	if humanoid == nil then
		return
	end
	-- Flintborn has no passive regeneration: remove Roblox's default Health script.
	local regen = character:FindFirstChild("Health")
	if regen and regen:IsA("Script") then
		regen:Destroy()
	end
	-- No swimming (GDD §55); the client turns it off too (it owns the character's state).
	humanoid:SetStateEnabled(Enum.HumanoidStateType.Swimming, false)
	humanoid.MaxHealth = GameConstants.BASE_MAX_HEALTH
	humanoid.Health = GameConstants.BASE_MAX_HEALTH
	local entry = {
		rules = SurvivalRules.NewState(),
		humanoid = humanoid,
		lastHealth = humanoid.Health,
		sprinting = false,
		moving = false,
		speed = 0,
		pace = SurvivalRules.NewPace(),
		observedSprint = false,
		lastPublish = 0,
		inWater = false,
		waterCheckedAt = 0,
		-- Snapshotted per run from masteries and perks (v0.13): Tidewalker's bonus
		-- speed in water.
		swimBonus = ModifierService.Sum(player, "SwimSpeed"),
	}
	entry.rules.staminaDrainScale = 1 / (1 + ModifierService.Sum(player, "SprintEfficiency"))
	entries[player] = entry
	humanoid.HealthChanged:Connect(function(health)
		if entries[player] ~= entry then
			return
		end
		if health < entry.lastHealth then
			-- Any damage halves pending food healing (Q65).
			SurvivalRules.OnDamaged(entry.rules)
		end
		entry.lastHealth = health
	end)
	publish(player, entry)
end

-- Moving, from horizontal root travel the server saw over the last window. Each
-- sample also feeds the pace check that catches sprinting without a sprint
-- request; it is judged against the walk speed the server currently allows.
local function observeMoving(player: Player, entry, time: number, walkPace: number): boolean
	local root = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
	if root == nil then
		entry.moving = false
		entry.observedSprint = false
		return false
	end
	local sample = entry.moveSample
	if sample == nil or sample.root ~= root then
		entry.moveSample = { root = root, position = root.Position, at = time }
		entry.pace = SurvivalRules.NewPace()
		return entry.moving
	end
	local elapsed = time - sample.at
	if elapsed >= SurvivalService.MOVE_SAMPLE_SECONDS then
		local offset = root.Position - sample.position
		local distance = Vector3.new(offset.X, 0, offset.Z).Magnitude
		entry.speed = distance / elapsed
		entry.moving = entry.speed > SurvivalService.MOVING_SPEED
		entry.observedSprint =
			SurvivalRules.ObservePace(entry.pace, distance, elapsed, entry.humanoid.WalkSpeed, walkPace)
		sample.position, sample.at = root.Position, time
	end
	return entry.moving
end

local function step(dt: number)
	local time = now()
	for player, entry in entries do
		local ok, err = pcall(function()
			local humanoid = entry.humanoid
			-- Downed players crawl at a fixed speed and cannot heal (Q159f).
			if humanoid.Health <= 0 or player:GetAttribute("Downed") then
				return
			end
			local rules = entry.rules
			if time - entry.waterCheckedAt >= SurvivalService.WATER_CHECK_SECONDS then
				entry.waterCheckedAt = time
				local root = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
				entry.inWater = root ~= nil and WorldState.FeetInWater(root.Position)
			end
			local walkPace = SurvivalRules.WalkPace(entry.inWater, entry.swimBonus)
			local moving = observeMoving(player, entry, time, walkPace)
			entry.sprinting = SurvivalRules.IsSprinting(rules, moving)
			SurvivalRules.StepStamina(rules, dt, moving, entry.observedSprint)
			SurvivalRules.StepFood(rules, dt)
			local healed = SurvivalRules.StepFoodHeals(rules, time, dt)
			if healed > 0 then
				SurvivalService.SetHealth(player, humanoid.Health + healed)
			end
			local speed = SurvivalRules.MoveSpeed(rules, moving, entry.inWater, entry.swimBonus)
			if humanoid.WalkSpeed ~= speed then
				humanoid.WalkSpeed = speed
			end
			if time - entry.lastPublish >= SurvivalService.PUBLISH_INTERVAL then
				entry.lastPublish = time
				publish(player, entry)
			end
		end)
		if not ok then
			warn(("[SurvivalService] Step failed for %s: %s"):format(player.Name, tostring(err)))
		end
	end
end

function SurvivalService.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	WorldAdmissionService.RunStarted:Connect(startRun)
	WorldAdmissionService.RunEnded:Connect(function(player)
		entries[player] = nil
	end)
	Players.PlayerRemoving:Connect(function(player)
		entries[player] = nil
	end)
	Remotes.Listen("SetMovement", function(player, sprintHeld)
		local entry = entries[player]
		if entry == nil or type(sprintHeld) ~= "boolean" then
			return
		end
		entry.rules.sprintIntent = sprintHeld
	end)
	RunService.Heartbeat:Connect(step)
end

return SurvivalService
