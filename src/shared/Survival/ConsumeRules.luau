-- Eating and drinking from the hand (GDD §59). A consumable is held like a tool
-- (its hotbar slot is equipped) and the attack input uses it: the character eats
-- or drinks for the item's use time. Food and boosts are used when that ends;
-- medicine heals as the drink starts and its animation is the cooldown (Q64).
-- Pure rules shared by HealingService (the authority), ConsumeController (the
-- animation and progress bar on every client) and CombatController (the attack
-- input and the touch button's icon).
--
-- Use time: medicine takes its own animation time (0.5/1/1.5 s, Q64, Q135), food
-- and boosts GameConstants.CONSUME_SECONDS. One use runs at a time per player.
-- A use still to be applied is interrupted (nothing used) when the player stops
-- holding that item (puts it away, picks another slot, the stack leaves the slot),
-- goes down, dies or leaves the run. Moving is allowed at full speed; menus do
-- not interrupt.

local Consumables = require(script.Parent.Parent.Items.Consumables)
local GameConstants = require(script.Parent.Parent.GameConstants)

local ConsumeRules = {}

-- The running use, as player attributes the server sets and every client reads:
-- the catalog id, and the server times it started and ends.
ConsumeRules.ITEM_ATTRIBUTE = "ConsumeItem"
ConsumeRules.START_ATTRIBUTE = "ConsumeStart"
ConsumeRules.END_ATTRIBUTE = "ConsumeEnd"

-- Kinds applied when the use starts rather than when it ends: medicine heals at
-- once and its animation is the only cooldown, "not a pre-heal channel" (GDD
-- §4.5, §5.4, Q64). Remove Medicine here to heal at the end of the drink instead.
ConsumeRules.APPLY_AT_START = { [Consumables.Medicine] = true }

-- How the arm moves: food is eaten in nibbles, medicine and draughts are drunk.
ConsumeRules.Eat = "Eat"
ConsumeRules.Drink = "Drink"

-- The pose, in degrees about the right shoulder (R6): RAISE swings the arm
-- forward and up (0 hangs, 90 points ahead), ACROSS turns it in toward the face.
-- Together they bring the held item to the mouth: with the R6 joints and the
-- held-item grip, the pouch or flask body ends about 0.2–0.4 studs in front of the
-- face (checked numerically; tune here after looking in game).
ConsumeRules.POSE = {
	Eat = { raise = 130, across = 70, nibble = 7, nibbleHz = 4 },
	Drink = { raise = 125, raiseEnd = 140, across = 65 },
}
-- The arm rises over RAISE_SECONDS and lowers over LOWER_SECONDS (each at most
-- this share of a short use), and after an interruption lowers over LOWER_SECONDS.
ConsumeRules.RAISE_SECONDS = 0.2
ConsumeRules.LOWER_SECONDS = 0.15
ConsumeRules.RAISE_SHARE = 0.3
ConsumeRules.LOWER_SHARE = 0.25

-- The touch attack button's icon while a consumable is held, by kind.
ConsumeRules.ICONS = {
	[Consumables.Food] = "drumstick",
	[Consumables.Medicine] = "heart",
	[Consumables.Boost] = "lightning",
}

-- Seconds the use of `item` (a Consumables entry) takes.
function ConsumeRules.Duration(item): number
	if item.kind == Consumables.Medicine then
		return item.animationSeconds
	end
	return GameConstants.CONSUME_SECONDS[item.kind] or GameConstants.CONSUME_SECONDS.Food
end

-- True when `item` is applied as its use starts (medicine), false when it ends.
function ConsumeRules.AppliesAtStart(item): boolean
	return item ~= nil and ConsumeRules.APPLY_AT_START[item.kind] == true
end

-- "Eat" for food, "Drink" for medicine and draughts.
function ConsumeRules.Style(item): string
	return if item and item.kind == Consumables.Food then ConsumeRules.Eat else ConsumeRules.Drink
end

-- A new use of `item` started at `now`: {requestId, catalogId, item, startedAt, endsAt}.
function ConsumeRules.Begin(requestId: string, catalogId: string, item, now: number)
	return {
		requestId = requestId,
		catalogId = catalogId,
		item = item,
		startedAt = now,
		endsAt = now + ConsumeRules.Duration(item),
	}
end

-- True once the use's animation has run its full time.
function ConsumeRules.Done(use, now: number): boolean
	return now >= use.endsAt
end

-- Why a running use of `catalogId` must stop, or nil to carry on. `view` is what
-- the server sees now: {present, alive, downed, held = the held catalog id}.
function ConsumeRules.Interruption(view, catalogId: string): string?
	if not view.present or not view.alive then
		return "NotInRun"
	elseif view.downed then
		return "Downed"
	elseif view.held ~= catalogId then
		return "Interrupted"
	end
	return nil
end

-- How far through the use `now` is, 0..1.
function ConsumeRules.Progress(startedAt: number, endsAt: number, now: number): number
	local span = endsAt - startedAt
	if span <= 0 then
		return 1
	end
	return math.clamp((now - startedAt) / span, 0, 1)
end

-- The arm's pose `elapsed` seconds into a `duration`-second use in `style`:
-- (blend 0..1 over whatever the arm was doing, raise degrees, across degrees).
-- The blend eases in at the start and out at the end, so the arm rests at both.
function ConsumeRules.Pose(style: string, elapsed: number, duration: number): (number, number, number)
	local pose = ConsumeRules.POSE[style] or ConsumeRules.POSE.Drink
	local raiseTime = math.min(ConsumeRules.RAISE_SECONDS, duration * ConsumeRules.RAISE_SHARE)
	local lowerTime = math.min(ConsumeRules.LOWER_SECONDS, duration * ConsumeRules.LOWER_SHARE)
	local blend = 1
	if elapsed <= 0 or elapsed >= duration then
		blend = 0
	elseif elapsed < raiseTime then
		blend = elapsed / raiseTime
	elseif elapsed > duration - lowerTime then
		blend = (duration - elapsed) / lowerTime
	end
	-- Smoothstep, so the arm starts and stops gently.
	blend = blend * blend * (3 - 2 * blend)
	local raise = pose.raise
	if pose.raiseEnd then
		raise += (pose.raiseEnd - pose.raise) * math.clamp(elapsed / math.max(duration, 1e-6), 0, 1)
	end
	if pose.nibble then
		raise += pose.nibble * math.sin(2 * math.pi * pose.nibbleHz * math.max(elapsed - raiseTime, 0))
	end
	return blend, raise, pose.across
end

-- The blend after an interruption: from `from` down to 0 over LOWER_SECONDS.
function ConsumeRules.Release(from: number, since: number): number
	return math.clamp(from * (1 - since / ConsumeRules.LOWER_SECONDS), 0, 1)
end

-- The touch attack button's icon while `item` is held.
function ConsumeRules.AttackIcon(item): string
	return ConsumeRules.ICONS[item and item.kind] or ConsumeRules.ICONS[Consumables.Food]
end

-- The progress bar's words: "Eating Cooked Meat", "Drinking Healing Potion".
function ConsumeRules.BarText(item): string
	local verb = if ConsumeRules.Style(item) == ConsumeRules.Eat then "Eating" else "Drinking"
	return verb .. " " .. (item and item.name or "")
end

-- The one-time hint when a consumable is first held, for the input in use
-- ("mouse", "touch" or "gamepad").
function ConsumeRules.HoldHint(item, input: string): string
	local verb = if ConsumeRules.Style(item) == ConsumeRules.Eat then "eat" else "drink"
	if input == "touch" then
		return ("Tap the attack button to %s it. Tap its slot again to put it away."):format(verb)
	elseif input == "gamepad" then
		return ("Press RT to %s it. Pick its slot again to put it away."):format(verb)
	end
	return ("Click to %s it. Press its hotbar key again to put it away."):format(verb)
end

return ConsumeRules
