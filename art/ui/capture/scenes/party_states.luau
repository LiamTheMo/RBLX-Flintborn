-- The Party window's states (docs/ui/PartyScreen.md → States; D5, D24), each
-- page over the lobby mockup at 1672 × 941. States are forced through the
-- DebugState attribute, as verifiers do; data comes through PartyModel.
--
--   1 leader of three: Invite hover / pressed, an invite on its way (busy),
--     Invited, the leader's crown (no tags), Leave Party, CloseX hover, CLOSE
--     pressed
--   2 a full party (8/8): the 8th row scrolls (D5), Invite disabled, gamepad
--     focus on CLOSE
--   3 a member (not the leader): an incoming invitation (Accept / ✕), the
--     search greyed, "Only the party leader can invite players."
--   4 alone with nobody else in the lobby, Created "—"
--   5 a search with no match, the search box focused, Invite Friends shown
--
--   python3 art/ui/capture/capture.py party_states

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Hud = game:GetService("StarterPlayer").StarterPlayerScripts.Client.Hud
-- Members' replicated level and progress (PlayerRow levelBar reads them).
for userId, level in { [1] = { 12, 0.6 }, [2] = { 15, 0.35 }, [3] = { 8, 0.8 }, [4] = { 21, 0.15 }, [5] = { 3, 0.5 } } do
	local member = game:GetService("Players"):GetPlayerByUserId(userId)
	member:SetAttribute("Level", level[1])
	member:SetAttribute("LevelProgress", level[2])
end
local PartyModel = require(ReplicatedStorage.Shared.UI.PartyModel)
local PartyWindow = require(Hud.Screens.PartyWindow)

local W, H = 1672, 941
local NOW = 1_700_000_000
local ME = { userId = 1, name = "LiamTheMo" }
local LEVELS = { [1] = 12, [2] = 15, [3] = 8, [4] = 21, [5] = 3, [6] = 9, [7] = 30, [8] = 17, [9] = 5, [10] = 11 }
for userId = 6, 10 do
	local member = Players:GetPlayerByUserId(userId)
	member:SetAttribute("Level", LEVELS[userId])
	member:SetAttribute("LevelProgress", (userId % 4 + 1) / 5)
end
local NAMES = {
	"LiamTheMo",
	"ForestRanger",
	"SunnyVale",
	"Emberwick",
	"MossyStone",
	"RiverFox",
	"Thornback",
	"Ashfall",
	"PineNeedle",
	"Kestrel",
}

local function candidate(id)
	return { userId = id, name = NAMES[id], userName = NAMES[id] }
end

local function member(id)
	return { userId = id, name = NAMES[id] }
end

-- Builds the window for `view`, lets `after(window)` force states, dumps a page.
local function page(view, candidates, opts, after)
	opts = opts or {}
	opts.now = opts.now or NOW
	opts.levels = LEVELS
	local window = PartyWindow.new({})
	window:SetData(PartyModel.WindowData(view, ME, candidates, opts))
	window:Open()
	window.screen.holder.Position = UDim2.fromOffset(
		PartyWindow.ORIGIN[1] + PartyWindow.SIZE[1] / 2,
		PartyWindow.ORIGIN[2] + PartyWindow.SIZE[2] / 2
	)
	window.screen.scale.Scale = 1
	if after then
		after(window)
	end
	__dump(Players.LocalPlayer.PlayerGui, W, H, { background = "art/reference/ui/lobby/01_hud.png" })
	window:Destroy()
end

local function force(component, state)
	component.root:SetAttribute("DebugState", state)
end

local function inviteButton(window, userId)
	for key, hit in window.selectables do
		if key == "invites:player:" .. userId then
			return hit.Parent
		end
	end
	return nil
end

-- 1. Leader of three ---------------------------------------------------------------------
page({
	party = {
		id = "p1",
		leader = 1,
		createdAt = NOW - 5 * 60 - 10,
		members = { member(1), member(4), member(5) },
		invited = { 3 },
	},
	invites = {},
	maxSize = 8,
}, { candidate(2), candidate(3), candidate(6), candidate(7) }, {
	pendingInvites = { [6] = true },
}, function(window)
	force({ root = inviteButton(window, 2) }, "hover")
	force({ root = inviteButton(window, 7) }, "pressed")
	force(window.closeX, "hover")
	force(window.closeButton, "pressed")
end)

-- 2. Full party ----------------------------------------------------------------------------
local full = {}
for id = 1, 8 do
	table.insert(full, member(id))
end
page({
	party = { id = "p1", leader = 1, createdAt = NOW - 2 * 3600 - 5, members = full, invited = {} },
	invites = {},
	maxSize = 8,
}, { candidate(9), candidate(10) }, {}, function(window)
	force(window.closeButton, "focused")
end)

-- 3. A member, with an invitation from another party ------------------------------------
page({
	party = {
		id = "p2",
		leader = 2,
		createdAt = NOW - 40,
		members = { member(2), member(1) },
		invited = {},
	},
	invites = { { partyId = "p3", from = "Emberwick", fromUserId = 4 } },
	maxSize = 8,
}, {}, {})

-- 4. Alone, nobody else here ---------------------------------------------------------------
page({ party = nil, invites = {}, maxSize = 8 }, {}, {})

-- 5. Search with no match, Invite Friends --------------------------------------------------
page(
	{ party = nil, invites = {}, maxSize = 8 },
	{ candidate(2), candidate(3) },
	{ query = "zz", friends = true },
	function(window)
		window.search:SetText("zz")
		force(window.search, "focused")
		force(window.friends, "hover")
	end
)
