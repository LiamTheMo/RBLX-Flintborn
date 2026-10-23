-- Downed and revive (GDD §5.3, §21.2, Q68, Q136, Q159). Lethal damage to a tribe
-- member downs them instead: 20 downed HP behind their armor, a 60 s bleed-out that
-- pauses while someone revives, a slow crawl and no healing. Anyone can revive with
-- a 10 s hold; one reviver at a time; hurting the reviver does not stop it. Solo
-- players skip all of this and die at once. World place only.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local ArmorRules = require(ReplicatedStorage.Shared.Combat.ArmorRules)
local DownedRules = require(ReplicatedStorage.Shared.Combat.DownedRules)
local GameConstants = require(ReplicatedStorage.Shared.GameConstants)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local SurvivalRules = require(ReplicatedStorage.Shared.Survival.SurvivalRules)
local InventoryService = require(script.Parent.InventoryService)
local SurvivalService = require(script.Parent.SurvivalService)
local TribeService = require(script.Parent.TribeService)
local WorldAdmissionService = require(script.Parent.WorldAdmissionService)

local DownedService = {}

DownedService.RANGE_ALLOWANCE = 2

local downed = {}

local function humanoidOf(player: Player): Humanoid?
	return player.Character and player.Character:FindFirstChildOfClass("Humanoid") or nil
end

local function rootOf(player: Player)
	return player.Character and player.Character:FindFirstChild("HumanoidRootPart")
end

local function armorFactor(player: Player): number
	return ArmorRules.Factor(InventoryService.ArmorPieces(player))
end

function DownedService.IsDowned(player: Player): boolean
	return downed[player] ~= nil
end

local function publish(player: Player, entry)
	local reviver = entry.rules.reviverId and Players:GetPlayerByUserId(entry.rules.reviverId)
	player:SetAttribute("DownedRemaining", math.ceil(entry.rules.remaining))
	player:SetAttribute("DownedHealth", math.ceil(entry.rules.downedHealth))
	player:SetAttribute("DownedReviver", reviver and reviver.DisplayName or nil)
	player:SetAttribute("DownedReviveProgress", math.floor(entry.rules.reviveProgress * 10) / 10)
end

local function clear(player: Player)
	local entry = downed[player]
	if entry == nil then
		return
	end
	downed[player] = nil
	entry.prompt:Destroy()
	if player.Parent then
		player:SetAttribute("Downed", nil)
		player:SetAttribute("DownedRemaining", nil)
		player:SetAttribute("DownedHealth", nil)
		player:SetAttribute("DownedReviver", nil)
		player:SetAttribute("DownedReviveProgress", nil)
	end
end

local function finish(player: Player)
	local humanoid = humanoidOf(player)
	clear(player)
	if humanoid then
		humanoid.Health = 0
	end
end

local function revive(player: Player)
	local humanoid = humanoidOf(player)
	clear(player)
	if humanoid and humanoid.Health > 0 then
		local health = DownedRules.RevivedHealth(humanoid.MaxHealth, armorFactor(player))
		SurvivalService.SetHealth(player, health)
		humanoid.JumpHeight = 7.2
	end
end

local function canRevive(reviver: Player, target: Player): boolean
	local humanoid = humanoidOf(reviver)
	return reviver ~= target
		and humanoid ~= nil
		and humanoid.Health > 0
		and not DownedService.IsDowned(reviver)
		and WorldAdmissionService.IsAtRisk(reviver)
end

-- Called by combat when damage would take a player to 0 HP. Returns true when the
-- player went down instead of dying (tribe members only).
function DownedService.TryDown(player: Player): boolean
	if downed[player] or not TribeService.InTribe(player) or not WorldAdmissionService.IsAtRisk(player) then
		return false
	end
	local humanoid = humanoidOf(player)
	local root = rootOf(player)
	if humanoid == nil or root == nil then
		return false
	end
	local rules = SurvivalService.Get(player)
	if rules then
		SurvivalRules.OnDowned(rules)
	end
	SurvivalService.SetHealth(player, 1)
	humanoid.WalkSpeed = DownedRules.CRAWL_SPEED
	humanoid.JumpHeight = 0

	local prompt = Instance.new("ProximityPrompt")
	prompt.ActionText = "Revive"
	prompt.ObjectText = player.DisplayName
	prompt.HoldDuration = GameConstants.REVIVE_SECONDS
	prompt.MaxActivationDistance = DownedRules.REVIVE_RANGE
	prompt.RequiresLineOfSight = false
	prompt.Parent = root
	local entry = { rules = DownedRules.New(), prompt = prompt }
	downed[player] = entry
	prompt.PromptButtonHoldBegan:Connect(function(reviver)
		if downed[player] ~= entry or not canRevive(reviver, player) then
			return
		end
		if not DownedRules.StartRevive(entry.rules, reviver.UserId) then
			InventoryService.Notify(reviver, "Someone else is already reviving them.")
		end
	end)
	prompt.PromptButtonHoldEnded:Connect(function(reviver)
		if downed[player] == entry then
			DownedRules.StopRevive(entry.rules, reviver.UserId)
		end
	end)
	player:SetAttribute("Downed", true)
	publish(player, entry)
	return true
end

-- Damage to a downed player goes to the downed pool, still behind armor.
-- Returns true when it finished them.
function DownedService.DamageDowned(player: Player, rawDamage: number): boolean
	local entry = downed[player]
	if entry == nil then
		return false
	end
	if DownedRules.Damage(entry.rules, armorFactor(player), rawDamage) then
		finish(player)
		return true
	end
	publish(player, entry)
	return false
end

local function step(dt: number)
	for player, entry in downed do
		local reviverId = entry.rules.reviverId
		if reviverId then
			local reviver = Players:GetPlayerByUserId(reviverId)
			local reviverRoot = reviver and rootOf(reviver)
			local root = rootOf(player)
			local inRange = reviverRoot ~= nil
				and root ~= nil
				and (reviverRoot.Position - root.Position).Magnitude
					<= DownedRules.REVIVE_RANGE + DownedService.RANGE_ALLOWANCE
			if not inRange or not canRevive(reviver, player) then
				DownedRules.StopRevive(entry.rules, reviverId)
			end
		end
		local outcome = DownedRules.Step(entry.rules, dt)
		if outcome == "Revived" then
			revive(player)
		elseif outcome == "BledOut" then
			finish(player)
		else
			publish(player, entry)
		end
	end
end

function DownedService.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	WorldAdmissionService.RunEnded:Connect(clear)
	Players.PlayerRemoving:Connect(clear)
	RunService.Heartbeat:Connect(step)
end

return DownedService
