-- Server-authoritative player session states (GDD §31.2). Being inside the play-world
-- place is not the same as being at risk: only ActiveRun and ExtractionHolding carry
-- inventory risk, and every loss rule must ask IsAtRisk rather than infer it.

local SessionStates = {}

SessionStates.LobbySafe = "LobbySafe"
SessionStates.TeleportPending = "TeleportPending"
SessionStates.StagingLoading = "StagingLoading"
SessionStates.WorldMainMenuReady = "WorldMainMenuReady"
SessionStates.PlayRequested = "PlayRequested"
SessionStates.ActiveRun = "ActiveRun"
SessionStates.ExtractionHolding = "ExtractionHolding"
SessionStates.ExtractionProtected = "ExtractionProtected"
SessionStates.MaintenancePreserved = "MaintenancePreserved"
SessionStates.Dead = "Dead"

-- Legal transitions from each state (GDD §31.2 "Exit/next transition").
local TRANSITIONS = {
	LobbySafe = { TeleportPending = true },
	TeleportPending = { StagingLoading = true, LobbySafe = true },
	StagingLoading = { WorldMainMenuReady = true, LobbySafe = true },
	WorldMainMenuReady = { PlayRequested = true, LobbySafe = true },
	PlayRequested = { ActiveRun = true, WorldMainMenuReady = true },
	ActiveRun = { ExtractionHolding = true, Dead = true, MaintenancePreserved = true },
	ExtractionHolding = { ActiveRun = true, ExtractionProtected = true, Dead = true, MaintenancePreserved = true },
	ExtractionProtected = { LobbySafe = true },
	MaintenancePreserved = { StagingLoading = true, LobbySafe = true },
	Dead = { LobbySafe = true },
}

local AT_RISK = { ActiveRun = true, ExtractionHolding = true }

function SessionStates.IsState(value: any): boolean
	return type(value) == "string" and TRANSITIONS[value] ~= nil
end

function SessionStates.CanTransition(from: string, to: string): boolean
	local allowed = TRANSITIONS[from]
	return allowed ~= nil and allowed[to] == true
end

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
