-- Server half of Shared.Building.StructureCatalog: what only the server uses. Everything in
-- ReplicatedStorage is downloaded to every player, so the shared module keeps
-- only what clients need; this one clones it and adds the rest, and server code
-- requires this module.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local SharedStructureCatalog = require(ReplicatedStorage.Shared.Building.StructureCatalog)

local StructureCatalog = table.clone(SharedStructureCatalog)

StructureCatalog.CHEST_SLOTS = 20
StructureCatalog.TRAP_DAMAGE = 15
StructureCatalog.TRAP_COOLDOWN = 2

-- Crops planted in a planter (GDD Q41): what one planting costs and yields.
StructureCatalog.Crops = {
	Redberry = { seed = { Redberry = 1 }, yield = { catalogId = "Redberry", quantity = 4 }, seconds = 180 },
	Sweetberry = { seed = { Sweetberry = 1 }, yield = { catalogId = "Sweetberry", quantity = 4 }, seconds = 180 },
	Herbs = { seed = { Herbs = 2 }, yield = { catalogId = "Herbs", quantity = 6 }, seconds = 300 },
	Sapling = { seed = { Wood = 5 }, yield = { catalogId = "Wood", quantity = 25 }, seconds = 600 },
	-- Fiber grows in planters too (GDD §53); Sunberry and Glimmerberry stay wild-only.
	Fiber = { seed = { Fiber = 3 }, yield = { catalogId = "Fiber", quantity = 12 }, seconds = 240 },
}

StructureCatalog.CROP_ORDER = { "Redberry", "Sweetberry", "Herbs", "Sapling", "Fiber" }

return StructureCatalog
