-- QA: the Party window (fitted by its own screen:Watch), opened as PartyController
-- does (w:Open(section) - no gamepad flag). Console: the HUD party title was
-- selected when A was pressed. Page 1: party of 3 + invite; page 2: 8 members
-- with 20-char names, friends with long names; then B.
local Players = game:GetService("Players")
local GuiService = game:GetService("GuiService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Hud = game:GetService("StarterPlayer").StarterPlayerScripts.Client.Hud
local PartyModel = require(ReplicatedStorage.Shared.UI.PartyModel)
local PartyWindow = require(Hud.Screens.PartyWindow)

local NOW = 1_700_000_000
local function data(long)
	local members = {
		{ userId = 1, name = "LiamTheMo", ready = true },
		{ userId = 2, name = "ForestRanger", ready = false },
		{ userId = 3, name = "SunnyVale", ready = true },
	}
	local friends = {
		{ userId = 4, name = "Emberwick", userName = "Emberwick" },
		{ userId = 5, name = "MossyStone", userName = "MossyStone" },
	}
	local levels = { [1] = 12, [2] = 15, [3] = 8, [4] = 21, [5] = 3, [6] = 9 }
	local from = "RiverFox"
	if long then
		members = {}
		for i = 1, 8 do
			table.insert(members, { userId = i, name = if i % 2 == 0 then "WWWWWWWWWWWWWWWWWWWW" else "MightyWarriorQueen9" .. i, ready = i % 2 == 1 })
			levels[i] = 100
		end
		friends = {
			{ userId = 20, name = "WWWWWWWWWWWWWWWWWWWW", userName = "WWWWWWWWWWWWWWWWWWWW" },
			{ userId = 21, name = "Explorer_Of_Isles_21", userName = "explorer_of_isles_21" },
		}
		levels[20], levels[21] = 100, 100
		from = "WWWWWWWWWWWWWWWWWWWW"
	end
	local view = {
		party = { id = "p1", leader = 1, createdAt = NOW - 12 * 60, members = members, invited = { 4 } },
		invites = { { partyId = "p9", from = from, fromUserId = 6 } },
		ready = true,
		maxSize = 8,
	}
	return PartyModel.WindowData(view, { userId = 1, name = members[1].name }, friends, { now = NOW, levels = levels })
end

local window = PartyWindow.new({})
if QA.gamepad then
	local tile = Instance.new("TextButton")
	tile.Name = "HudPartyTitle"
	tile.Parent = Players.LocalPlayer.PlayerGui
	GuiService.SelectedObject = tile
end
window:SetData(data(false))
window:Open(nil)
QA.report(Players.LocalPlayer.PlayerGui, { scale = window.screen.scale.Scale })
__dump(Players.LocalPlayer.PlayerGui, QA.W, QA.H)
window:SetData(data(true))
QA.report(Players.LocalPlayer.PlayerGui, { scale = window.screen.scale.Scale })
__dump(Players.LocalPlayer.PlayerGui, QA.W, QA.H)
print("QA back:", QA.back(), "open after B:", window.screen:IsOpen())
