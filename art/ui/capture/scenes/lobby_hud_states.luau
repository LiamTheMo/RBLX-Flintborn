-- Every interactive part of the lobby HUD forced into one state per page through
-- the DebugState attribute (as verifiers do): 1 hover, 2 pressed, 3 disabled,
-- 4 focused (gamepad selection), 5 selected. The pills, gear, tiles,
-- Party title, member and empty rows, the add-player button, the invite answers
-- and the hotbar slots.
local Hud = game:GetService("StarterPlayer").StarterPlayerScripts.Client.Hud
-- Members' replicated level and progress (PlayerRow levelBar reads them).
for userId, level in { [1] = { 12, 0.6 }, [2] = { 15, 0.35 }, [3] = { 8, 0.8 }, [4] = { 21, 0.15 }, [5] = { 3, 0.5 } } do
	local member = game:GetService("Players"):GetPlayerByUserId(userId)
	member:SetAttribute("Level", level[1])
	member:SetAttribute("LevelProgress", level[2])
end
local Shared = game:GetService("ReplicatedStorage").Shared
local LobbyHud = require(Hud.Screens.LobbyHud)
local LobbyHudModel = require(Shared.UI.LobbyHudModel)

local W, H = 1672, 941
local ME = { userId = 1, name = "LiamTheMo" }

for _, state in { "hover", "pressed", "disabled", "focused", "selected" } do
	local _, root = __screen(W, H)
	local hud = LobbyHud.new(root, {})
	hud:SetTopInset(58)
	hud:SetProgress({ level = 12, xp = 450, xpToNext = 750 }, true)
	hud:SetCurrency(2450, 125, true)
	hud:SetParty(LobbyHudModel.Party({
		party = { id = "p1", leader = 1, members = { { userId = 1, name = "LiamTheMo" } } },
		invites = { { partyId = "p9", from = "RiverFox" } },
		maxSize = 8,
	}, ME))
	hud:SetHotbar(LobbyHudModel.Hotbar({ { catalogId = "StoneAxe", quantity = 1 } }))
	local parts = hud.parts
	local roots = { parts.coins, parts.gems, parts.settings, parts.partyTitle, parts.invite }
	for _, tile in ipairs(hud.tiles) do
		table.insert(roots, tile.root)
	end
	for _, slot in hud.slots do
		table.insert(roots, slot.root)
	end
	for _, list in { parts.members, parts.empty, parts.answers } do
		for _, item in list do
			table.insert(roots, item)
		end
	end
	for _, item in roots do
		item:SetAttribute("DebugState", state)
		assert(item:GetAttribute("KitState") == state, ("%s did not draw %s"):format(item.Name, state))
	end
	print(("lobby_hud_states: %d parts drawn %s"):format(#roots, state))
	__dump(root, W, H)
end
