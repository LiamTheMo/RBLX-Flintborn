-- Extraction qualification and settlement (GDD §9, §10.3, §53, Q17–24, Q119,
-- Q126–129, Q151–154, Q158). Presence counts only at the deadline. Only the fixed
-- Center portal doubles material quantities; portable runes never do. Materials
-- may be carried into a run (GDD §53), and what was carried in never multiplies:
-- Play tags each material stack it takes from the lobby as carried
-- (InventoryRules.MarkCarried), the tag stays on the units through every drop,
-- body, chest, merge and craft (a carried ore smelts into a carried bar), and per
-- material only the extracted units not tagged carried are multiplied. Units
-- handed to another player stay carried for them too. Every material, special
-- ones included, banks into the vault: its material capacity (1,000 per type)
-- decides what is deleted, and the receipt lists it. Everything else lands in the durable 50-slot lobby backpack,
-- where only a full backpack deletes. Unique gear is never multiplied.

local GameConstants = require(script.Parent.Parent.GameConstants)
local Geometry = require(script.Parent.Parent.Core.Geometry)
local ExtractionRules = {}

ExtractionRules.FIXED_SECONDS = GameConstants.FIXED_EXTRACTION_SECONDS
ExtractionRules.PORTABLE_SECONDS = GameConstants.PORTABLE_EXTRACTION_SECONDS

ExtractionRules.Kinds = { Fixed = "Fixed", Center = "Center", Portable = "Portable" }

function ExtractionRules.InZone(playerPosition, center, radius: number): boolean
	return Geometry.FlatDistance(playerPosition, center) <= radius
		and math.abs(playerPosition.Y - center.Y) <= radius + 10
end

return ExtractionRules
