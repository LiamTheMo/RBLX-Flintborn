-- One modifier pipeline for every XP, yield and luck calculation (GDD §33.3, §51,
-- Q78, Q150–153, Q162). Collects mastery buffs, rebirth perks, Roblox Premium (+25%
-- XP, checked on the server), the earnable XP booster (+50%) and the timed boosts
-- from berries and draughts as {stat, op, value}; callers combine them with
-- ModifierRules. Every XP bonus is additive, so a potion adds to Premium and the
-- booster (Q162). Consumable boosts count down only during a run (GDD §53): a
-- successful extraction (or a maintenance kick, which preserves the run's items)
-- saves each one's remaining time in the profile and the next deploy resumes it;
-- dying or leaving the world without extracting ends them and clears what was
-- saved.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local BoostRules = require(ReplicatedStorage.Shared.Survival.BoostRules)
local GameConstants = require(ReplicatedStorage.Shared.GameConstants)
local MasteryCatalog = require(ReplicatedStorage.Shared.Progression.MasteryCatalog)
local ModifierRules = require(ReplicatedStorage.Shared.Progression.ModifierRules)
local PerkCatalog = require(ReplicatedStorage.Shared.Progression.PerkCatalog)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local ProfileService = require(script.Parent.ProfileService)
local WorldAdmissionService = require(script.Parent.WorldAdmissionService)

local ModifierService = {}

ModifierService.BOOSTER_XP = 0.5

-- Player -> BoostRules state for the current run.
local boosts = {}

local function now(): number
	return workspace:GetServerTimeNow()
end

local publishBoosts

-- Ends `entry` after `seconds` unless it is no longer the boost of its kind (Sources
-- may have pruned it already; a stronger one that took over keeps its own timer).
local function expireLater(player: Player, state, kind: string, entry, seconds: number)
	task.delay(math.max(0, seconds), function()
		local current = state[kind]
		if boosts[player] == state and (current == nil or current == entry) and player.Parent then
			state[kind] = nil
			publishBoosts(player)
		end
	end)
end

-- Replicates each boost kind to its owner's HUD as an amount and an end time.
function publishBoosts(player: Player)
	local state = boosts[player]
	for _, kind in BoostRules.ORDER do
		local amountName, untilName = BoostRules.Attributes(kind)
		local entry = state and BoostRules.Active(state, kind, now())
		player:SetAttribute(amountName, if entry then entry.amount else nil)
		player:SetAttribute(untilName, if entry then entry.endsAt else nil)
	end
end

-- True when `boost` would take effect for `player` now (BoostRules.Takes).
function ModifierService.BoostTakes(player: Player, boost): boolean
	local state = boosts[player]
	return BoostRules.IsValid(boost) and (state == nil or BoostRules.Takes(state, boost, now()))
end

-- Starts a timed boost ({kind, amount, seconds}) unless a boost of its kind at
-- least as strong is running, which then stays exactly as it is. Returns the
-- entry in force and whether this boost started, or nil for a bad boost.
function ModifierService.ApplyBoost(player: Player, boost)
	if not BoostRules.IsValid(boost) then
		return nil, false
	end
	local state = boosts[player]
	if state == nil then
		state = BoostRules.New()
		boosts[player] = state
	end
	local entry, started = BoostRules.Apply(state, boost, now())
	if not started then
		return entry, false
	end
	publishBoosts(player)
	expireLater(player, state, boost.kind, entry, boost.seconds)
	return entry, true
end

-- Ends every boost in memory (the run ended, or a new one started).
function ModifierService.ClearBoosts(player: Player)
	boosts[player] = nil
	if player.Parent then
		publishBoosts(player)
	end
end

-- Starts a run's boosts: the ones its last extraction saved, with the time they
-- had left (GDD §53). The saved copy stays in the profile until the run ends, so
-- a crashed run loses nothing.
function ModifierService.ResumeBoosts(player: Player)
	local profile = ProfileService.GetProfile(player)
	local state = BoostRules.Resume(profile and profile.boosters.paused, now())
	boosts[player] = state
	for kind, entry in state do
		expireLater(player, state, kind, entry, entry.endsAt - now())
	end
	publishBoosts(player)
end

-- Ends the run's boosts. An extraction or a maintenance kick saves what is left of
-- each; any other ending (death, leaving) saves nothing and clears what an earlier
-- extraction saved.
function ModifierService.EndBoosts(player: Player, reason: string?)
	local state = boosts[player]
	local keep = reason == "Extracted" or reason == "Maintenance"
	local paused = if keep and state then BoostRules.Pause(state, now()) else {}
	ProfileService.Mutate(player, function(profile)
		profile.boosters.paused = paused
	end)
	ModifierService.ClearBoosts(player)
end

function ModifierService.IsPremium(player: Player): boolean
	return player.MembershipType == Enum.MembershipType.Premium
end

-- Every active modifier for `player`.
function ModifierService.Sources(player: Player)
	local sources = {}
	local state = boosts[player]
	if state then
		BoostRules.Prune(state, now())
		for _, modifier in BoostRules.Modifiers(state, now()) do
			table.insert(sources, modifier)
		end
	end
	local profile = ProfileService.GetProfile(player)
	if profile == nil then
		return sources
	end
	for name, entry in profile.progression.masteryTracks do
		for _, buff in MasteryCatalog.Buffs(name, entry.level or 0) do
			table.insert(sources, buff)
		end
	end
	for _, modifier in PerkCatalog.Modifiers(profile.rebirth.ownedPerks) do
		table.insert(sources, modifier)
	end
	if ModifierService.IsPremium(player) then
		table.insert(sources, { stat = "Xp", op = "Additive", value = GameConstants.PREMIUM_XP_BONUS })
	end
	if (profile.boosters.xpUntil or 0) > os.time() then
		table.insert(sources, { stat = "Xp", op = "Additive", value = ModifierService.BOOSTER_XP })
	end
	return sources
end

-- Modifiers for one or more stats, ready for ModifierRules.Final/RollYield.
function ModifierService.Get(player: Player, ...: string)
	local sources = ModifierService.Sources(player)
	local list = {}
	for _, stat in { ... } do
		for _, modifier in ModifierRules.Collect(sources, stat) do
			table.insert(list, modifier)
		end
	end
	return list
end

-- The summed additive value of one stat (0 when none).
function ModifierService.Sum(player: Player, stat: string): number
	local total = 0
	for _, modifier in ModifierService.Get(player, stat) do
		total += modifier.value
	end
	return total
end

function ModifierService.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	WorldAdmissionService.RunStarted:Connect(ModifierService.ResumeBoosts)
	WorldAdmissionService.RunEnded:Connect(ModifierService.EndBoosts)
	Players.PlayerRemoving:Connect(function(player)
		-- Deferred: a departure or shutdown ending (BeforeRelease) reads them first.
		task.defer(function()
			boosts[player] = nil
		end)
	end)
end

return ModifierService
