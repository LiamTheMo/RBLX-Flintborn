local Shared = game:GetService("ReplicatedStorage").Shared
local SessionStates = require(Shared.Admission.SessionStates)
local TransitRules = require(Shared.Admission.TransitRules)
local SpawnRules = require(Shared.Admission.SpawnRules)
local MatchmakingRules = require(Shared.Admission.MatchmakingRules)
local PartyRules = require(Shared.Admission.PartyRules)
local PlaceConfig = require(Shared.Config.PlaceConfig)
local ProfileSchema = require(Shared.Data.ProfileSchema)

test("only the GDD §31.2 transitions are legal", function()
	local legal = {
		{ "LobbySafe", "TeleportPending" },
		{ "TeleportPending", "StagingLoading" },
		{ "StagingLoading", "WorldMainMenuReady" },
		{ "WorldMainMenuReady", "PlayRequested" },
		{ "PlayRequested", "ActiveRun" },
		{ "PlayRequested", "WorldMainMenuReady" },
		{ "ActiveRun", "ExtractionHolding" },
		{ "ExtractionHolding", "ExtractionProtected" },
		{ "ActiveRun", "Dead" },
		{ "ActiveRun", "MaintenancePreserved" },
		{ "Dead", "LobbySafe" },
	}
	for _, pair in legal do
		expect(SessionStates.CanTransition(pair[1], pair[2]), pair[1] .. " -> " .. pair[2])
	end
	local illegal = {
		{ "LobbySafe", "ActiveRun" },
		{ "StagingLoading", "ActiveRun" },
		{ "WorldMainMenuReady", "ActiveRun" },
		{ "Dead", "ActiveRun" },
		{ "ExtractionProtected", "ActiveRun" },
		{ "ActiveRun", "LobbySafe" },
	}
	for _, pair in illegal do
		expect(not SessionStates.CanTransition(pair[1], pair[2]), "illegal " .. pair[1] .. " -> " .. pair[2])
	end
end)

test("only ActiveRun and ExtractionHolding carry inventory risk", function()
	local risky = { ActiveRun = true, ExtractionHolding = true }
	for _, state in
		{
			"LobbySafe",
			"TeleportPending",
			"StagingLoading",
			"WorldMainMenuReady",
			"PlayRequested",
			"ActiveRun",
			"ExtractionHolding",
			"ExtractionProtected",
			"MaintenancePreserved",
			"Dead",
		}
	do
		expect(SessionStates.IsState(state), state .. " is a state")
		expectEq(SessionStates.IsAtRisk(state), risky[state] == true, state .. " risk")
	end
	expect(not SessionStates.IsAtRisk(nil), "no state is not at risk")
	expect(SessionStates.ShowsWorldMenu("PlayRequested"), "menu stays up while spawning")
	expect(not SessionStates.ShowsWorldMenu("ActiveRun"), "menu hidden in the run")
end)

test("deploy reserves every unvaulted item and consumes it exactly once", function()
	local profile = ProfileSchema.Default(0)
	profile.lobbyBackpack.slots = { { catalogId = "StoneSpear" }, { catalogId = "FlintArrow", quantity = 40 } }
	TransitRules.Reserve(profile, "res-1", 10)
	expectEq(#profile.lobbyBackpack.slots, 0, "backpack emptied into transit")
	expectEq(#profile.transit.items, 2, "both items reserved")
	expect(not pcall(TransitRules.Reserve, profile, "res-2", 11), "a second reservation is refused")

	expect(not pcall(TransitRules.Consume, profile, "res-other"), "a mismatched reservation is refused")
	local items = TransitRules.Consume(profile, "res-1")
	expectEq(#items, 2, "items enter the run")
	expectEq(profile.transit, nil, "reservation cleared")
	expect(not pcall(TransitRules.Consume, profile, "res-1"), "cannot consume twice")
end)

test("extracted materials never leave the lobby: a deploy leaves them behind", function()
	local profile = ProfileSchema.Default(0)
	profile.lobbyBackpack.slots = {
		{ catalogId = "Wood", quantity = 40 },
		{ instanceId = "spear-1", catalogId = "StoneSpear" },
		{ catalogId = "AncientEmber", quantity = 2 },
		{ catalogId = "FlintArrow", quantity = 20 },
		{ catalogId = "IronOre", quantity = 5 },
		{ catalogId = "IronBar", quantity = 3 },
	}
	TransitRules.Reserve(profile, "res-m", 10)
	expectEq(#profile.transit.items, 2, "only the spear and arrows are reserved")
	for _, item in profile.transit.items do
		expect(
			item.catalogId == "StoneSpear" or item.catalogId == "FlintArrow",
			"no material in transit: " .. item.catalogId
		)
	end
	expectEq(#profile.lobbyBackpack.slots, 4, "every material stays in the backpack")
	for _, item in profile.lobbyBackpack.slots do
		expect(not TransitRules.Deployable(item), "only materials stayed: " .. item.catalogId)
	end
	expect(
		TransitRules.Deployable({ instanceId = "x", catalogId = "Wood" }),
		"a unique record is never a material stack"
	)
	TransitRules.Rollback(profile)
	expectEq(#profile.lobbyBackpack.slots, 6, "a rollback returns the reserved items beside the materials")
end)

test("any failure before Play rolls every item back", function()
	local profile = ProfileSchema.Default(0)
	profile.lobbyBackpack.slots = { { catalogId = "WoodenBow" } }
	TransitRules.Reserve(profile, "res-1", 10)
	expectEq(TransitRules.Rollback(profile), 1, "one item returned")
	expectEq(#profile.lobbyBackpack.slots, 1, "back in the lobby backpack")
	expectEq(profile.lobbyBackpack.slots[1].catalogId, "WoodenBow", "same item")
	expectEq(TransitRules.Rollback(profile), 0, "rollback with nothing reserved is a no-op")
end)

test("spawns are never chosen within the minimum distance of a living player", function()
	local candidates = {}
	for i = 0, 9 do
		table.insert(candidates, Vector3.new(i * 100, 0, 0))
	end
	local players = { Vector3.new(0, 0, 0), Vector3.new(500, 0, 0) }
	local rng = Random.new(7)
	for _ = 1, 50 do
		local position, isFallback = SpawnRules.Choose(candidates, players, rng)
		expect(not isFallback, "a valid candidate exists")
		for _, other in players do
			expect((position - other).Magnitude >= SpawnRules.MIN_PLAYER_DISTANCE, "far enough from players")
		end
	end
end)

test("when nothing is far enough the farthest candidate is used", function()
	local candidates = { Vector3.new(0, 0, 0), Vector3.new(60, 0, 0), Vector3.new(120, 0, 0) }
	local players = { Vector3.new(0, 0, 0) }
	local position, isFallback = SpawnRules.Choose(candidates, players, Random.new(1))
	expect(isFallback, "fallback reported")
	expectEq(position.X, 120, "farthest candidate")
	expectEq(SpawnRules.Choose({}, players, Random.new(1)), nil, "no candidates means no spawn")
end)

test("matchmaking keeps parties together within capacity and exclusions", function()
	local now = 1000
	local worlds = {
		{ privateServerId = "a", accessCode = "A", players = 28, updatedAt = now },
		{ privateServerId = "b", accessCode = "B", players = 20, updatedAt = now },
		{ privateServerId = "c", accessCode = "C", players = 25, updatedAt = now, excludedUserIds = { ["7"] = true } },
		{ privateServerId = "d", accessCode = "D", players = 1, updatedAt = now - 500 },
	}
	local pick = MatchmakingRules.Pick(worlds, { 7, 8, 9 }, now)
	expectEq(pick.privateServerId, "b", "only b fits a party of three without exclusions")
	pick = MatchmakingRules.Pick(worlds, { 1 }, now)
	expectEq(pick.privateServerId, "a", "the fullest world with room")
	expectEq(MatchmakingRules.Pick(worlds, table.create(12, 5), now), nil, "no world fits twelve: reserve a new one")
	expect(not MatchmakingRules.IsJoinable(worlds[4], { 1 }, now), "stale worlds are ignored")
end)

test("parties invite, accept, cap at eight and hand over leadership", function()
	local state = PartyRules.NewState()
	expect(PartyRules.Invite(state, 1, 2, "p1"), "leader invites")
	expectEq(PartyRules.PartyOf(state, 1).leader, 1, "inviter leads")
	expect(not PartyRules.Accept(state, 3, "p1"), "uninvited player cannot join")
	expect(PartyRules.Accept(state, 2, "p1"), "invitee accepts")
	expectEq(#PartyRules.PartyOf(state, 1).members, 2, "two members")
	local ok, reason = PartyRules.Invite(state, 2, 3, "p2")
	expect(not ok and reason == "NotLeader", "members cannot invite")

	for userId = 3, 8 do
		PartyRules.Invite(state, 1, userId, "x")
		PartyRules.Accept(state, userId, "p1")
	end
	expectEq(#PartyRules.PartyOf(state, 1).members, 8, "full party of eight")
	ok, reason = PartyRules.Invite(state, 1, 9, "x")
	expect(not ok and reason == "PartyFull", "ninth invite refused")

	PartyRules.Leave(state, 1)
	expectEq(PartyRules.PartyOf(state, 2).leader, 2, "leadership passes on")
	expectEq(PartyRules.PartyOf(state, 1), nil, "leaver has no party")
	for userId = 2, 8 do
		PartyRules.Leave(state, userId)
	end
	expectEq(next(state.parties), nil, "empty party removed")
end)

test("place role comes from generated IDs, then the Studio attribute", function()
	local ids = { lobby = 100, world = 200 }
	expectEq(PlaceConfig.Resolve(ids, 100, nil, false), "Lobby", "lobby place")
	expectEq(PlaceConfig.Resolve(ids, 200, nil, false), "World", "world place")
	expectEq(PlaceConfig.Resolve(ids, 300, nil, false), "Unknown", "unknown live place")
	expectEq(PlaceConfig.Resolve(nil, 0, "Lobby", true), "Lobby", "Studio attribute")
	expectEq(PlaceConfig.Resolve(nil, 0, nil, true), "World", "Studio default")
	expectEq(PlaceConfig.Resolve(nil, 0, "Bogus", false), "Unknown", "bad attribute ignored")
end)
