-- Server half of Shared.Items.ItemCatalog: what only the server uses. Everything in
-- ReplicatedStorage is downloaded to every player, so the shared module keeps
-- only what clients need; this one clones it and adds the rest, and server code
-- requires this module.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local SharedItemCatalog = require(ReplicatedStorage.Shared.Items.ItemCatalog)

local ItemCatalog = table.clone(SharedItemCatalog)

-- The item's rarity; an unknown id is Common.
function ItemCatalog.RarityOf(catalogId: any): string
	local def = ItemCatalog.Get(catalogId)
	return def and def.rarity or "Common"
end

function ItemCatalog.IsStackable(catalogId: string): boolean
	return ItemCatalog.StackCap(catalogId) ~= nil
end

return ItemCatalog
