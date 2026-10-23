-- Robux offers (GDD §1.2, §36.2, Q97, Q99, Q123). Every paid benefit is convenience
-- or speed with an earnable in-game route, shown next to the price. Robux never
-- buys PvP damage, armor or health. Product IDs are set when the developer
-- products exist on the experience (0 = not purchasable yet).

local OfferCatalog = {}

OfferCatalog.Offers = {
	{
		id = "VaultTier",
		name = "Vault upgrade (+25 slots)",
		productId = 0,
		grant = { vaultTier = 1 },
		earnable = "500 Gems in the lobby wallet (Gems come from quests, milestones and rare encounters)",
	},
	{
		id = "XpBooster",
		name = "XP booster (+50% for 30 minutes)",
		productId = 0,
		grant = { boosterSeconds = 1800 },
		earnable = 'The "Extract 3 times" daily quest grants the same booster',
	},
	{
		id = "PerkRespec",
		name = "Rebirth perk respec",
		productId = 0,
		grant = { respec = true },
		earnable = "250 Gems, or a redemption code",
	},
	{
		id = "GemPack",
		name = "100 Gems",
		productId = 0,
		grant = { gems = 100 },
		earnable = "About one hour of quests and rare encounters",
	},
}

-- Grant keys that would sell power and are never allowed (Q99).
OfferCatalog.FORBIDDEN_GRANTS = { "damage", "armor", "health" }

OfferCatalog.ById = {}
OfferCatalog.ByProduct = {}
for _, offer in OfferCatalog.Offers do
	OfferCatalog.ById[offer.id] = offer
	if offer.productId ~= 0 then
		OfferCatalog.ByProduct[offer.productId] = offer
	end
end

return OfferCatalog
