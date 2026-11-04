-- Lobby trading (GDD §10.2, Q13, Q50, Q56, Q98, Q125, Q130, Q164). Two players in
-- the same lobby trade designated items and Gems — never Coins. Raw materials trade
-- only when flagged rare or Exclusive, and only out of the vault (a backpack
-- stack is deposited first, GDD §53); they land in the receiver's vault, so an
-- offer needs room there and a trade never deletes. Gem trades need level 10 on
-- both sides, are capped per UTC day for sending and receiving, and pay a 5%
-- fee. Settlement writes the trade into both profiles as pending; Reconcile later
-- finalises it (the counterpart saved it too) or rolls one side back (the
-- counterpart never saved it, or rolled back), and waits while the counterpart
-- may still save.
-- Until then the profile is "settling": nothing a rollback could not claw back
-- (sales, Forge crafts, Gem spending, a Deploy) may consume what it received.

local ItemCatalog = require(script.Parent.Parent.Items.ItemCatalog)
local TradeRules = {}

-- Offer key of a vault material: "mat:<catalogId>".
TradeRules.MATERIAL_PREFIX = "mat:"

local TRADEABLE_FAMILIES = { Tool = true, Weapon = true, Armor = true, Placeable = true }

-- Designated items only (Q130): gear, tools, placeables (runes), Permanent items,
-- and materials or consumables flagged tradeable (rare materials and berries, GDD
-- §51) or Exclusive (Q56).
function TradeRules.IsTradeable(item): boolean
	local def = ItemCatalog.Get(item.catalogId)
	if def == nil then
		return false
	end
	if item.permanent then
		return true
	end
	if def.family == ItemCatalog.Families.Material or def.family == ItemCatalog.Families.Consumable then
		return def.tradeable == true or def.rarity == "Exclusive"
	end
	return TRADEABLE_FAMILIES[def.family] == true
end

-- A lobby backpack slot that may be offered: never a material, which trades only
-- from the vault (Q164; still so under GDD §53).
function TradeRules.IsTradeableSlot(item): boolean
	return not ItemCatalog.IsMaterial(item.catalogId) and TradeRules.IsTradeable(item)
end

-- A vault material that may be offered: flagged rare or Exclusive (Q56).
function TradeRules.IsTradeableMaterial(catalogId: any): boolean
	return type(catalogId) == "string"
		and ItemCatalog.IsMaterial(catalogId)
		and TradeRules.IsTradeable({ catalogId = catalogId })
end

-- The catalog ID a vault material offer key names, or nil for a backpack key.
function TradeRules.MaterialOf(key: string): string?
	local prefix = TradeRules.MATERIAL_PREFIX
	return if key:sub(1, #prefix) == prefix then key:sub(#prefix + 1) else nil
end

return TradeRules
