-- Timed consumable boosts (GDD §51, Q162). One boost per kind, and a running boost
-- never weakens (owner decision 2026-10-28): it stays exactly as it is until it
-- runs out, unless a stronger boost of its kind takes over with its own timer.
-- Boosts never stack with themselves.
-- Each kind feeds one modifier stat as an additive bonus, so an XP boost adds to
-- Premium and the paid booster rather than multiplying them, and Luck raises
-- rare-drop chances only (EventRules.RollLoot). Boosts count down only during a
-- run and pause between runs (GDD §53): a successful extraction saves each
-- running boost's remaining time (Pause) and the next deploy resumes it (Resume);
-- dying or leaving the world without extracting ends them. Times are in the
-- caller's clock (the server uses workspace:GetServerTimeNow(), which clients can
-- count down against); saved boosts hold only remaining seconds.

local Consumables = require(script.Parent.Parent.Items.Consumables)
local BoostRules = {}

-- Display order on the HUD.
BoostRules.ORDER = { "XP", "Luck" }
export type Boost = { kind: string, amount: number, seconds: number }
export type Entry = { amount: number, endsAt: number }
export type Paused = { kind: string, amount: number, remaining: number }

-- The longest boost any consumable grants: a saved boost never has more left.
BoostRules.MAX_SECONDS = 0
for _, item in Consumables.Catalog do
	if item.boost then
		BoostRules.MAX_SECONDS = math.max(BoostRules.MAX_SECONDS, item.boost.seconds)
	end
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

return BoostRules
