-- Server half of Shared.Admission.SessionStates: what only the server uses. Everything in
-- ReplicatedStorage is downloaded to every player, so the shared module keeps
-- only what clients need; this one clones it and adds the rest, and server code
-- requires this module.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local SharedSessionStates = require(ReplicatedStorage.Shared.Admission.SessionStates)

local SessionStates = table.clone(SharedSessionStates)

SessionStates.LobbySafe = "LobbySafe"
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

function SessionStates.IsState(value: any): boolean
	return type(value) == "string" and TRANSITIONS[value] ~= nil
end

function SessionStates.CanTransition(from: string, to: string): boolean
	local allowed = TRANSITIONS[from]
	return allowed ~= nil and allowed[to] == true
end

return SessionStates
