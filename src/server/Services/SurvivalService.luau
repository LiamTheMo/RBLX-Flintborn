-- Health, stamina and food for players in an active run (GDD §4.3, §5.4). One
-- Heartbeat loop steps every meter on the server; clients only send sprint and
-- crouch intent. Meters are run state and reset on each spawn. World place only.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local GameConstants = require(ReplicatedStorage.Shared.GameConstants)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local SurvivalRules = require(ReplicatedStorage.Shared.Survival.SurvivalRules)
local ModifierService = require(script.Parent.ModifierService)
local WorldAdmissionService = require(script.Parent.WorldAdmissionService)

local SurvivalService = {}

SurvivalService.PUBLISH_INTERVAL = 0.1

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
	player:SetAttribute("Crouching", rules.crouching)
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
	humanoid.MaxHealth = GameConstants.BASE_MAX_HEALTH
	humanoid.Health = GameConstants.BASE_MAX_HEALTH
	local entry = {
		rules = SurvivalRules.NewState(),
		humanoid = humanoid,
		lastHealth = humanoid.Health,
		sprinting = false,
		lastPublish = 0,
		-- Snapshotted per run from masteries and perks (v0.13).
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
			local moving = humanoid.MoveDirection.Magnitude > 0.1
			entry.sprinting = SurvivalRules.IsSprinting(rules, moving)
			SurvivalRules.StepStamina(rules, dt, moving)
			SurvivalRules.StepFood(rules, dt)
			local healed = SurvivalRules.StepFoodHeals(rules, time, dt)
			if healed > 0 then
				SurvivalService.SetHealth(player, humanoid.Health + healed)
			end
			local speed = SurvivalRules.MoveSpeed(rules, moving)
			if entry.swimBonus > 0 and humanoid:GetState() == Enum.HumanoidStateType.Swimming then
				-- The Tidewalker perk: faster movement in water.
				speed *= 1 + entry.swimBonus
			end
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
	Remotes.Get("SetMovement").OnServerEvent:Connect(function(player, sprintHeld, crouching)
		local entry = entries[player]
		if entry == nil or type(sprintHeld) ~= "boolean" or type(crouching) ~= "boolean" then
			return
		end
		entry.rules.sprintIntent = sprintHeld
		entry.rules.crouching = crouching
	end)
	RunService.Heartbeat:Connect(step)
end

return SurvivalService
