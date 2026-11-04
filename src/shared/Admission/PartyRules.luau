-- Lobby parties (GDD Q161c): players group in the lobby and deploy into the same
-- world together. Pure state transitions over a parties table, so the server and
-- specs share one definition. Every function returns (ok, reason?).

local GameConstants = require(script.Parent.Parent.GameConstants)

local PartyRules = {}

PartyRules.MAX_SIZE = GameConstants.MAX_TRIBE_SIZE

export type Party = {
	id: string,
	leader: number,
	members: { number },
	invites: { [number]: boolean },
	createdAt: number?,
}
export type State = { parties: { [string]: Party }, memberOf: { [number]: string } }

return PartyRules
