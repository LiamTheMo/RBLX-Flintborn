-- Pure account-economy rules over a profile (GDD §10, Q90–99, Q116–125). Coins come
-- from quests and merchant sales, never from extracting; neither currency ever
-- drops. Every change runs inside a once-only profile operation in the services.

local EconomyRules = {}

EconomyRules.BOOSTER_SECONDS = 1800

return EconomyRules
