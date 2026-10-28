-- Player-facing text for server refusal codes that need explaining. Codes not
-- listed here are shown as they are.

local Reasons = {}

local TEXT = {
	RecoveringItems = "your items from a crashed server are still being recovered — try again in a minute",
	TradeSettling = "a recent trade is still being saved — try again shortly",
	PartnerVaultFull = "their vault has no room for that many",
	BadQuantity = "that amount isn't allowed",
	BoostActive = "a boost at least as strong is already running",
}

function Reasons.Text(code: any): string
	return TEXT[code] or tostring(code)
end

return Reasons
