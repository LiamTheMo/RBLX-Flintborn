-- One modifier pipeline for every XP and yield calculation (GDD §33.3, Q78,
-- Q150–153, Q162). Collects mastery buffs, rebirth perks, Roblox Premium (+25% XP,
-- checked on the server) and the earnable XP booster (+50%) as {stat, op, value};
-- callers combine them with ModifierRules.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local GameConstants = require(ReplicatedStorage.Shared.GameConstants)
local MasteryCatalog = require(ReplicatedStorage.Shared.Progression.MasteryCatalog)
local ModifierRules = require(ReplicatedStorage.Shared.Progression.ModifierRules)
local PerkCatalog = require(ReplicatedStorage.Shared.Progression.PerkCatalog)
local ProfileService = require(script.Parent.ProfileService)

local ModifierService = {}

ModifierService.BOOSTER_XP = 0.5

function ModifierService.IsPremium(player: Player): boolean
	return player.MembershipType == Enum.MembershipType.Premium
end

-- Every active modifier for `player`.
function ModifierService.Sources(player: Player)
	local sources = {}
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

return ModifierService
