-- Pure progression rules over a profile (GDD §33, §37, Q52–54, Q69–89, Q150–153).
-- General XP and mastery XP apply to the profile the moment they are earned and are
-- never taken back by death (Q70). Each run tracks the XP it earned so a Center
-- extraction can add an equal bonus once (Q69); portable runes never do (Q158).
-- Rebirth resets the general level only (Q82).

local LevelCurve = require(script.Parent.LevelCurve)
local MasteryCatalog = require(script.Parent.MasteryCatalog)
local PerkCatalog = require(script.Parent.PerkCatalog)

local ProgressionRules = {}

ProgressionRules.REBIRTH_LEVEL = LevelCurve.MAX_LEVEL
ProgressionRules.REBIRTH_COST_GROWTH = 1.5

local function track(profile, name: string)
	local tracks = profile.progression.masteryTracks
	tracks[name] = tracks[name] or { level = 0, counters = {} }
	return tracks[name]
end

-- Starts counting a new run's XP for the Center bonus.
function ProgressionRules.StartRun(profile, runId: string)
	profile.progression.currentRun = { runId = runId, general = 0, mastery = {}, settled = false }
end

local function runFor(profile)
	local run = profile.progression.currentRun
	return if run and not run.settled then run else nil
end

-- Adds general XP. Returns levels gained.
function ProgressionRules.GrantXp(profile, amount: number): number
	if amount <= 0 then
		return 0
	end
	local progression = profile.progression
	local level, xp, gained = LevelCurve.Add(progression.level, progression.xp, amount)
	progression.level, progression.xp = level, xp
	local run = runFor(profile)
	if run then
		run.general += amount
	end
	return gained
end

-- Applies newly reached mastery levels' titles exactly once.
local function applyMilestones(profile, name: string, level: number)
	local progression = profile.progression
	for reached = 1, level do
		local key = name .. ":" .. reached
		if not progression.appliedMilestones[key] then
			progression.appliedMilestones[key] = true
			local title = MasteryCatalog.MILESTONES[name] and MasteryCatalog.MILESTONES[name][reached]
			if title then
				progression.titles[title] = true
			end
		end
	end
end

local function addMasteryXp(profile, name: string, amount: number): number
	local entry = track(profile, name)
	local before = entry.level
	entry.counters.xp = (entry.counters.xp or 0) + amount
	entry.level = math.min(MasteryCatalog.MAX_LEVEL, MasteryCatalog.LevelFor(entry.counters.xp))
	applyMilestones(profile, name, entry.level)
	return entry.level - before
end

-- A verified action on a mastery track: one action is one mastery XP. Returns
-- levels gained.
function ProgressionRules.GrantMastery(profile, name: string, actions: number): number
	if actions <= 0 or table.find(MasteryCatalog.TRACKS, name) == nil then
		return 0
	end
	local entry = track(profile, name)
	entry.counters.actions = (entry.counters.actions or 0) + actions
	local run = runFor(profile)
	if run then
		run.mastery[name] = (run.mastery[name] or 0) + actions
	end
	return addMasteryXp(profile, name, actions)
end

-- Fills a receipt's XP fields and, for the Center only, adds a bonus equal to the
-- run's XP (general and mastery, never action counts). The run is then settled so
-- a later receipt cannot bonus it again.
function ProgressionRules.SettleRun(profile, receipt, kind: string)
	local run = runFor(profile)
	local general = run and run.general or 0
	local mastery = run and table.clone(run.mastery) or {}
	local masteryTotal = 0
	for _, amount in mastery do
		masteryTotal += amount
	end
	receipt.runGeneralXPEarned = general
	receipt.runMasteryXPEarned = masteryTotal
	receipt.centerBonusGeneralXP = 0
	receipt.centerBonusMasteryXP = 0
	if run then
		run.settled = true
	end
	if kind ~= "Center" or run == nil then
		return
	end
	local progression = profile.progression
	progression.level, progression.xp = LevelCurve.Add(progression.level, progression.xp, general)
	for name, amount in mastery do
		addMasteryXp(profile, name, amount)
	end
	receipt.centerBonusGeneralXP = general
	receipt.centerBonusMasteryXP = masteryTotal
end

-- Legendary extractions the next rebirth needs: 1, 2, 3, 4, 6, … (×1.5 each).
function ProgressionRules.RequiredLegendaries(rebirths: number): number
	return math.ceil(ProgressionRules.REBIRTH_COST_GROWTH ^ rebirths - 1e-9)
end

-- Tokens for the nth rebirth: 3, +1 every third rebirth.
function ProgressionRules.TokensFor(nth: number): number
	return 3 + nth // 3
end

function ProgressionRules.CanRebirth(profile)
	local rebirth = profile.rebirth
	if profile.progression.level < ProgressionRules.REBIRTH_LEVEL then
		return false, "LevelTooLow"
	end
	if (rebirth.legendariesSinceRebirth or 0) < ProgressionRules.RequiredLegendaries(rebirth.count) then
		return false, "ChallengeIncomplete"
	end
	return true, nil
end

-- What a rebirth would do, in plain words for the confirmation screen.
function ProgressionRules.Preview(profile)
	return {
		reset = { ("General level %d → 1 (and XP toward the next level)"):format(profile.progression.level) },
		kept = {
			"Vault and lobby backpack",
			"Permanent items",
			"All mastery levels, titles and cosmetics",
			"Owned perks",
			"Coins and Gems",
		},
		gained = { ("%d rebirth tokens"):format(ProgressionRules.TokensFor(profile.rebirth.count + 1)) },
	}
end

-- Commits a rebirth (the caller runs it as a once-only operation).
function ProgressionRules.Rebirth(profile)
	local ok, reason = ProgressionRules.CanRebirth(profile)
	if not ok then
		return false, reason
	end
	local rebirth = profile.rebirth
	rebirth.count += 1
	rebirth.tokens += ProgressionRules.TokensFor(rebirth.count)
	rebirth.legendariesSinceRebirth = 0
	profile.progression.level = 1
	profile.progression.xp = 0
	return true, nil
end

function ProgressionRules.PerkCost(perkId: string, rank: number): number?
	local perk = PerkCatalog.Get(perkId)
	return perk and perk.costs[rank + 1] or nil
end

function ProgressionRules.BuyPerk(profile, perkId: any)
	local perk = PerkCatalog.Get(perkId)
	if perk == nil then
		return false, "UnknownPerk"
	end
	local owned = profile.rebirth.ownedPerks
	local rank = owned[perkId] or 0
	local cost = perk.costs[rank + 1]
	if cost == nil then
		return false, "MaxRank"
	end
	if profile.rebirth.tokens < cost then
		return false, "NotEnoughTokens"
	end
	profile.rebirth.tokens -= cost
	owned[perkId] = rank + 1
	return true, nil
end

return ProgressionRules
