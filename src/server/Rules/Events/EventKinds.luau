-- The event kinds the world event director knows how to build (GDD §7) and the
-- director category each one belongs to. EventDirectorService keeps one builder per
-- entry of Built and checks the two lists match when it loads, so a catalog kind
-- nobody builds fails a headless spec instead of silently spawning an empty,
-- announced event in the world.

local EventKinds = {}

EventKinds.Built = { "Node", "Cache", "Meteor", "Npc", "Structure", "Boss" }

-- Each EventCatalog category and the kind its entries must have.
EventKinds.OfCategory = {
	Vegetation = "Node",
	Ore = "Node",
	Npc = "Npc",
	Cache = "Cache",
	Meteor = "Meteor",
	Structure = "Structure",
	Boss = "Boss",
}

function EventKinds.IsBuilt(kind: any): boolean
	return table.find(EventKinds.Built, kind) ~= nil
end

return EventKinds
