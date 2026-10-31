-- QA: the Play window fitted by the real Kit.Scale.Window (screen:Watch, as
-- PlayController does) and opened the way PlayController opens it (window:Open()).
--   page 1: solo sample          page 2: a party of 8 with 20-char names, long loadout
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local PlayModel = require(ReplicatedStorage.Shared.UI.PlayModel)
local PlayWindow = require(Client.Hud.Screens.PlayWindow)

local function page(long)
	local preview = {
		{ catalogId = "StoneAxe" },
		{ catalogId = "StoneSpear" },
		{ catalogId = "BasicMedicine", quantity = if long then 99 else 3 },
	}
	local window = PlayWindow.new({})
	local details = PlayModel.WorldRows()
	table.insert(details, PlayModel.CarryingRow(preview))
	window:SetDetails(details)
	if long then
		local list = {}
		for i = 1, 8 do
			table.insert(list, { userId = i, name = if i % 2 == 0 then "WWWWWWWWWWWWWWWWWWWW" else "MightyWarriorQueen9" .. i, ready = i % 3 ~= 0 })
		end
		local rows = PlayModel.Members({ party = { leader = 1, members = list } }, { userId = 1, name = list[1].name })
		for _, row in rows do
			row.level = 100
		end
		window:SetParty(rows, true)
		window:SetMode("party", true)
	else
		window:SetParty({ { userId = 1, name = "LiamTheMo", level = 12, leader = true } }, false)
		window:SetMode("solo")
	end
	window:SetLoadout(PlayModel.LoadoutHotbar(preview))
	window.screen:Watch()
	window:Open()
	QA.report(Players.LocalPlayer.PlayerGui, {
		scale = window.screen.scale.Scale,
		default = window.screen.defaultSelection and window.screen.defaultSelection.Name or nil,
	})
	__dump(Players.LocalPlayer.PlayerGui, QA.W, QA.H)
	window.screen.gui:Destroy()
end

page(false)
page(true)
