-- QA: the Quest Journal fitted by screen:Watch (as JournalController does) and
-- opened with screen:Open(UserInputService.GamepadEnabled). Page 1 the book tab
-- (first quest name lengthened by ~30 %), page 2 the map tab; then B.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")
local Hud = game:GetService("StarterPlayer").StarterPlayerScripts.Client.Hud
local JournalModel = require(ReplicatedStorage.Shared.UI.JournalModel)
local JournalWindow = require(Hud.Screens.JournalWindow)
local QuestCatalog = require(ReplicatedStorage.Shared.Economy.QuestCatalog)

local NOW = 20000 * 86400 - 3 * 3600
local quests = {}
for index, quest in QuestCatalog.Quests do
	table.insert(quests, {
		id = quest.id,
		name = if index == 1 then quest.name .. " in the Ancient Grove" else quest.name,
		tier = quest.tier,
		coins = quest.coins,
		gems = quest.gems,
		booster = quest.booster,
		count = if index == 3 then quest.count else math.floor(quest.count / 3),
		needed = quest.count,
		claimed = false,
		repeats = quest.repeats,
		action = quest.action,
	})
end
local window = JournalWindow.new(nil, {})
window:SetPage("quests", JournalModel.QuestPage(quests, NOW))
window:SetPartyAvailable(true)
window:Select(quests[1].id)
local screen = window.screen
screen:Watch()
screen:Open(UserInputService.GamepadEnabled)
QA.report(Players.LocalPlayer.PlayerGui, { scale = screen.scale.Scale })
__dump(Players.LocalPlayer.PlayerGui, QA.W, QA.H)
window:SelectTab("map")
QA.report(Players.LocalPlayer.PlayerGui, { scale = screen.scale.Scale })
__dump(Players.LocalPlayer.PlayerGui, QA.W, QA.H)
print("QA back:", QA.back(), "open after B:", screen:IsOpen())
