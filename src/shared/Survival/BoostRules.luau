-- Timed consumable boosts (GDD §51, Q162). One boost per kind: a new one replaces
-- the running one and restarts its timer, so boosts never stack with themselves.
-- Each kind feeds one modifier stat as an additive bonus, so an XP boost adds to
-- Premium and the paid booster rather than multiplying them, and Luck raises
-- rare-drop chances only (EventRules.RollLoot). Boosts are run state: the server
-- clears them when a run ends. Times are in the caller's clock (the server uses
-- workspace:GetServerTimeNow(), which clients can count down against).

local GameConstants = require(script.Parent.Parent.GameConstants)
local Consumables = require(script.Parent.Parent.Items.Consumables)

local BoostRules = {}

-- Boost kind -> the ModifierRules stat it raises.
BoostRules.STATS = { XP = "Xp", Luck = "Luck" }
-- Display order on the HUD.
BoostRules.ORDER = { "XP", "Luck" }
BoostRules.LABELS = { XP = "XP", Luck = "rare-drop chance" }

export type Boost = { kind: string, amount: number, seconds: number }
export type Entry = { amount: number, endsAt: number }

function BoostRules.New(): { [string]: Entry }
	return {}
end

function BoostRules.IsValid(boost: any): boolean
	return type(boost) == "table"
		and BoostRules.STATS[boost.kind] ~= nil
		and type(boost.amount) == "number"
		and boost.amount > 0
		and type(boost.seconds) == "number"
		and boost.seconds > 0
end

-- The running boost of `kind`, or nil once it has run out.
function BoostRules.Active(boosts, kind: string, now: number): Entry?
	local entry = boosts and boosts[kind]
	if entry == nil or entry.endsAt <= now then
		return nil
	end
	return entry
end

-- Starts `boost`, replacing any boost of the same kind. Returns the new entry and
-- the one it replaced while that was still running.
function BoostRules.Apply(boosts, boost: Boost, now: number): (Entry, Entry?)
	local replaced = BoostRules.Active(boosts, boost.kind, now)
	local entry = { amount = boost.amount, endsAt = now + boost.seconds }
	boosts[boost.kind] = entry
	return entry, replaced
end

-- Drops boosts that have run out.
function BoostRules.Prune(boosts, now: number)
	for kind in boosts do
		if BoostRules.Active(boosts, kind, now) == nil then
			boosts[kind] = nil
		end
	end
end

function BoostRules.Amount(boosts, kind: string, now: number): number
	local entry = BoostRules.Active(boosts, kind, now)
	return if entry then entry.amount else 0
end

-- Running boosts as {stat, op, value} modifiers for ModifierService.Sources.
function BoostRules.Modifiers(boosts, now: number)
	local list = {}
	for _, kind in BoostRules.ORDER do
		local entry = BoostRules.Active(boosts, kind, now)
		if entry then
			table.insert(list, { stat = BoostRules.STATS[kind], op = "Additive", value = entry.amount })
		end
	end
	return list
end

-- Player attributes that replicate a boost to its owner's HUD.
function BoostRules.Attributes(kind: string): (string, string)
	return "Boost" .. kind, "Boost" .. kind .. "Until"
end

-- "9:41" for 581 seconds; partial seconds round up so 0:00 never shows early.
function BoostRules.FormatTime(seconds: number): string
	local whole = math.max(0, math.ceil(seconds - 1e-9))
	return ("%d:%02d"):format(whole // 60, whole % 60)
end

function BoostRules.Percent(amount: number): string
	return ("+%d%%"):format(math.round(amount * 100))
end

-- "+25% XP for 10:00".
function BoostRules.Describe(boost: Boost): string
	return ("%s %s for %s"):format(
		BoostRules.Percent(boost.amount),
		BoostRules.LABELS[boost.kind] or boost.kind,
		BoostRules.FormatTime(boost.seconds)
	)
end

-- The toast after using a consumable, e.g. "Sunberry: +5% food, +10% XP
-- for 3:00". `replaced` (from Apply) adds what the new boost took the place of.
function BoostRules.UseText(item, replaced: Entry?): string
	local parts = {}
	if (item.hunger or 0) > 0 then
		table.insert(parts, BoostRules.Percent(item.hunger) .. " food")
	end
	if (item.heal or 0) > 0 then
		table.insert(
			parts,
			if item.kind == Consumables.Medicine
				then ("heals %d"):format(item.heal)
				else ("heals %d over %d s"):format(item.heal, GameConstants.FOOD_HEAL_SECONDS)
		)
	end
	if item.boost then
		table.insert(parts, BoostRules.Describe(item.boost))
	end
	local text = item.name .. ": " .. (if #parts > 0 then table.concat(parts, ", ") else "used")
	if replaced and item.boost then
		text ..= (" (replaces your %s %s boost)"):format(
			BoostRules.Percent(replaced.amount),
			BoostRules.LABELS[item.boost.kind] or item.boost.kind
		)
	end
	return text
end

return BoostRules
