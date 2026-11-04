-- Server half of Shared.Survival.BoostRules: what only the server uses. Everything in
-- ReplicatedStorage is downloaded to every player, so the shared module keeps
-- only what clients need; this one clones it and adds the rest, and server code
-- requires this module.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Consumables = require(ReplicatedStorage.Shared.Items.Consumables)
local GameConstants = require(ReplicatedStorage.Shared.GameConstants)
local Validation = require(script.Parent.Parent.Data.Validation)
local SharedBoostRules = require(ReplicatedStorage.Shared.Survival.BoostRules)

type Boost = SharedBoostRules.Boost
type Entry = SharedBoostRules.Entry
type Paused = SharedBoostRules.Paused

local BoostRules = table.clone(SharedBoostRules)

-- Boost kind -> the ModifierRules stat it raises.
BoostRules.STATS = { XP = "Xp", Luck = "Luck" }
BoostRules.LABELS = { XP = "XP", Luck = "rare-drop chance" }

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

-- True when `boost` would take effect now: nothing of its kind is running, or it
-- is stronger than what is. An equal or weaker one would change nothing.
function BoostRules.Takes(boosts, boost: Boost, now: number): boolean
	local running = BoostRules.Active(boosts, boost.kind, now)
	return running == nil or boost.amount > running.amount
end

-- Starts `boost` when it Takes; otherwise the running boost stays as it is.
-- Returns the entry in force and whether `boost` started.
function BoostRules.Apply(boosts, boost: Boost, now: number): (Entry, boolean)
	if not BoostRules.Takes(boosts, boost, now) then
		return boosts[boost.kind], false
	end
	local entry = { amount = boost.amount, endsAt = now + boost.seconds }
	boosts[boost.kind] = entry
	return entry, true
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

-- The running boosts with their remaining seconds, to save between runs.
function BoostRules.Pause(boosts, now: number): { Paused }
	local saved = {}
	for _, kind in BoostRules.ORDER do
		local entry = BoostRules.Active(boosts, kind, now)
		if entry then
			table.insert(saved, { kind = kind, amount = entry.amount, remaining = entry.endsAt - now })
		end
	end
	return BoostRules.Sanitize(saved)
end

-- A saved boost list as loaded: only known kinds with a positive finite amount and
-- a finite remaining time in (0, MAX_SECONDS], and one per kind (the stronger
-- one, as Apply would keep). Anything else is dropped.
function BoostRules.Sanitize(saved: any): { Paused }
	local best = {}
	if type(saved) == "table" then
		for _, entry in saved do
			if
				type(entry) == "table"
				and BoostRules.STATS[entry.kind] ~= nil
				and Validation.IsFinite(entry.amount)
				and entry.amount > 0
				and Validation.IsFinite(entry.remaining)
				and entry.remaining > 0
				and entry.remaining <= BoostRules.MAX_SECONDS
			then
				local kept = best[entry.kind]
				if kept == nil or entry.amount > kept.amount then
					best[entry.kind] = { kind = entry.kind, amount = entry.amount, remaining = entry.remaining }
				end
			end
		end
	end
	local list = {}
	for _, kind in BoostRules.ORDER do
		if best[kind] then
			table.insert(list, best[kind])
		end
	end
	return list
end

-- Boost state that resumes saved boosts at `now` with their remaining time.
function BoostRules.Resume(saved, now: number): { [string]: Entry }
	local boosts = BoostRules.New()
	for _, entry in BoostRules.Sanitize(saved) do
		BoostRules.Apply(boosts, { kind = entry.kind, amount = entry.amount, seconds = entry.remaining }, now)
	end
	return boosts
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
-- for 3:00". `kept` is the running boost that stayed because this item's was not
-- stronger (from Apply); the toast then says so instead of naming the boost.
function BoostRules.UseText(item, kept: Entry?): string
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
	if item.boost and kept then
		table.insert(
			parts,
			("your %s %s boost keeps running"):format(
				BoostRules.Percent(kept.amount),
				BoostRules.LABELS[item.boost.kind] or item.boost.kind
			)
		)
	elseif item.boost then
		table.insert(parts, BoostRules.Describe(item.boost))
	end
	return item.name .. ": " .. (if #parts > 0 then table.concat(parts, ", ") else "used")
end

return BoostRules
