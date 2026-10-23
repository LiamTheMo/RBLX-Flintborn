-- The first-session tutorial (GDD §25.5, §36.5, Q59). Steps complete only from
-- server-observed gameplay (Play, gathering, crafting, healing, events,
-- extraction, vaulting) or a short acknowledgement for explanation steps. Rewards
-- are paid once, never after a skip, and never include Permanent gear. Nothing
-- here bypasses a risk rule: the tutorial runs inside the normal game.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local EconomyRules = require(ReplicatedStorage.Shared.Economy.EconomyRules)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local TutorialSteps = require(ReplicatedStorage.Shared.Tutorial.TutorialSteps)
local CurrencyService = require(script.Parent.CurrencyService)
local HealingService = require(script.Parent.HealingService)
local ProfileService = require(script.Parent.ProfileService)
local ProgressionService = require(script.Parent.ProgressionService)
local VaultService = require(script.Parent.VaultService)
local WorldAdmissionService = require(script.Parent.WorldAdmissionService)

local TutorialService = {}

local function publish(player: Player)
	local profile = ProfileService.GetProfile(player)
	if profile == nil or not player.Parent then
		return
	end
	local state = profile.tutorial
	local step = TutorialSteps.Steps[state.step]
	Remotes.Get("TutorialChanged"):FireClient(player, {
		index = state.step,
		total = #TutorialSteps.Steps,
		id = step and step.id,
		title = step and step.title,
		hint = step and step.hint,
		ack = step ~= nil and step.trigger == "Ack",
		skipped = state.skipped,
		done = state.completedAt ~= nil,
	})
end

local function pay(player: Player, step)
	local reward = step.reward
	if reward.coins then
		CurrencyService.Run(player, "tutorial:", step.id, "TutorialReward", function(profile)
			if not TutorialSteps.ClaimReward(profile.tutorial, step) then
				return false, "AlreadyPaid"
			end
			EconomyRules.Grant(profile, reward.coins, reward.gems)
			return true, nil
		end)
	elseif reward.xp then
		local claimed = false
		ProfileService.Mutate(player, function(profile)
			claimed = TutorialSteps.ClaimReward(profile.tutorial, step)
		end)
		if claimed then
			ProgressionService.GrantXp(player, reward.xp, "Tutorial: " .. step.title)
		end
	end
end

-- Feeds one observed trigger into the player's tutorial.
function TutorialService.Observe(player: Player, trigger: string)
	local completed = nil
	ProfileService.Mutate(player, function(profile)
		completed = TutorialSteps.Advance(profile.tutorial, trigger, os.time())
	end)
	if completed then
		if completed.reward then
			pay(player, completed)
		end
		publish(player)
	end
end

function TutorialService.Start()
	ProfileService.ProfileLoaded:Connect(function(player)
		publish(player)
	end)
	WorldAdmissionService.RunStarted:Connect(function(player)
		TutorialService.Observe(player, "RunStarted")
	end)
	WorldAdmissionService.RunEnded:Connect(function(player, reason)
		if reason == "Extracted" then
			TutorialService.Observe(player, "Extract")
		end
	end)
	ProgressionService.Acted:Connect(function(player, action)
		local trigger = TutorialSteps.ACTION_TRIGGERS[action]
		if trigger then
			TutorialService.Observe(player, trigger)
		end
	end)
	HealingService.Used:Connect(function(player)
		TutorialService.Observe(player, "Heal")
	end)
	VaultService.Deposited:Connect(function(player)
		TutorialService.Observe(player, "Vault")
	end)
	Remotes.Get("TutorialAction").OnServerInvoke = function(player, action)
		if action == "Ack" then
			TutorialService.Observe(player, "Ack")
		elseif action == "Skip" then
			ProfileService.Mutate(player, function(profile)
				TutorialSteps.Skip(profile.tutorial)
			end)
		elseif action == "Replay" then
			ProfileService.Mutate(player, function(profile)
				TutorialSteps.Replay(profile.tutorial)
			end)
		else
			return false
		end
		publish(player)
		return true
	end
end

return TutorialService
