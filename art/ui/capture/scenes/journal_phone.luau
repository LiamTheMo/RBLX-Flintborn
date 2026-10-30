-- The Quest Journal on a phone held sideways (844 × 390, touch only, the top bar
-- 58 px down): the real window fit (Kit.Scale.Window, as screen:Watch does)
-- fills the room under the top bar, side tabs included (the screen is 50 px
-- wider each side for them). Pages: the book tab, the map tab.
--
--   python3 art/ui/capture/capture.py journal_phone

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")
local Hud = game:GetService("StarterPlayer").StarterPlayerScripts.Client.Hud
local JournalModel = require(ReplicatedStorage.Shared.UI.JournalModel)
local JournalWindow = require(Hud.Screens.JournalWindow)
local QuestCatalog = require(ReplicatedStorage.Shared.Economy.QuestCatalog)

local W, H = 844, 390
local NOW = 20000 * 86400 - 3 * 3600
workspace.CurrentCamera.ViewportSize = Vector2.new(W, H)
UserInputService.TouchEnabled = true
UserInputService.KeyboardEnabled = false
UserInputService.MouseEnabled = false

local quests = {}
for index, quest in QuestCatalog.Quests do
	table.insert(quests, {
		id = quest.id,
		name = quest.name,
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
window:Select("DailyCraft")
local screen = window.screen
screen:Open()
-- The capture env has no AbsoluteSize: fit the way Scale.Window does in game.
screen:Fit(W, H, 58, 1)
local k = screen.scale.Scale
print(
	("journal_phone: window scale %.3f -> %d x %d screen px (frame %d px wide)"):format(
		k,
		JournalWindow.SIZE[1] * k,
		JournalWindow.SIZE[2] * k,
		JournalWindow.FRAME[1] * k
	)
)
-- The smallest text on the page in screen px (row subtitles, 15 design px).
print(("journal_phone: 15 px text draws at %.1f screen px"):format(15 * k))
__dump(Players.LocalPlayer.PlayerGui, W, H)
window:SelectTab("map")
__dump(Players.LocalPlayer.PlayerGui, W, H)
window:Destroy()
