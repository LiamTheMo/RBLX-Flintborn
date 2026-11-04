-- Server-authoritative player session states (GDD §31.2). Being inside the play-world
-- place is not the same as being at risk: only ActiveRun and ExtractionHolding carry
-- inventory risk, and every loss rule must ask IsAtRisk rather than infer it.

local SessionStates = {}

SessionStates.TeleportPending = "TeleportPending"
SessionStates.StagingLoading = "StagingLoading"
SessionStates.WorldMainMenuReady = "WorldMainMenuReady"
SessionStates.PlayRequested = "PlayRequested"
SessionStates.ActiveRun = "ActiveRun"
local AT_RISK = { ActiveRun = true, ExtractionHolding = true }

-- True only while carried items can be lost (death or ordinary departure).
function SessionStates.IsAtRisk(state: string?): boolean
	return state ~= nil and AT_RISK[state] == true
end

-- States in which the protected world main menu is shown.
function SessionStates.ShowsWorldMenu(state: string?): boolean
	return state == SessionStates.StagingLoading
		or state == SessionStates.WorldMainMenuReady
		or state == SessionStates.PlayRequested
end

return SessionStates
