-- Siege items (GDD §6.3, §51; docs/design/ITEM_CATALOG.md §5). Optional raid
-- accelerators, never a requirement: ordinary weapons and tools still break every
-- tier. The Fire Bomb is thrown on a slow, visible arc and bursts in a small
-- radius; fire burns Wood ×3, Stone ×1 and every metal ×0.25 of the base burst.
-- The burst also scorches players (under the same PvP, tribe and safe-zone rules
-- as any hit, never the thrower) and creatures for a modest amount. A Breaching
-- Charge is set on an enemy wall or door the player is looking at and near, burns
-- an 8 s fuse and then deals one heavy flat blow to that piece only: enough to
-- break any Wood or Stone wall or door, and a large share of a metal one. Neither
-- works inside a safe zone; a charge also cannot be set in a no-build aura
-- (portals, the Guardian arena). Totems never protect against raids. All numbers
-- are starting placeholders.

local ItemCatalog = require(script.Parent.Parent.Items.ItemCatalog)
local SiegeRules = {}

SiegeRules.FUSE_SECONDS = 8
-- Player-facing text for every refusal reason.
SiegeRules.MESSAGES = {
	NotInRun = "You can't use that right now.",
	BadRequest = "Can't use that.",
	NotHeld = "Equip the item on your hotbar first.",
	NoItem = "You have none left.",
	TooSoon = "Wait a moment.",
	SafeZone = "Nothing can be raided inside a safe zone.",
	NoRaidZone = "Charges can't be set here.",
	NoTarget = "Aim at an enemy wall or door within reach.",
	NotBreachable = "Charges only go on walls and doors.",
	OwnStructure = "That's your own structure.",
	TooFar = "Get closer.",
	ChargeSet = ("Breaching Charge set: %d s fuse."):format(SiegeRules.FUSE_SECONDS),
	BombReady = "Fire Bomb ready: attack to throw it.",
	ChargeReady = "Aim at an enemy wall or door within reach, then attack to set the charge.",
}

-- "Thrown" or "Placed" for a siege item, otherwise nil.
function SiegeRules.Kind(catalogId: any): string?
	local item = ItemCatalog.Get(catalogId)
	return item and item.siege and item.siege.kind or nil
end

function SiegeRules.Message(reason: string?): string
	return reason and SiegeRules.MESSAGES[reason] or ("Can't do that (" .. tostring(reason) .. ").")
end

return SiegeRules
