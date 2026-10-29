-- The Journal at the design size with sample quests (the first selected, under
-- way), then the Daily tab with a finished quest selected.
local Hud = game:GetService("StarterPlayer").StarterPlayerScripts.Client.Hud
local JournalPanel = require(Hud.JournalPanel)

local gui, root = __screen()
local noop = function() end
local panel = JournalPanel.new(root, { onClose = noop, onClaim = noop })
panel.screen.gui.Enabled = true
panel.screen:Fit(1672, 941, 0, 1)
-- Pinned to the sheet's own scale and place so the capture overlays the reference.
panel.screen.scale.Scale = 1
panel.screen.window.Position = UDim2.fromOffset(20 + 816, 18 + 386)

local function quest(id, name, tier, action, count, needed, repeats, extra)
	local q = {
		id = id,
		name = name,
		tier = tier,
		action = action,
		coins = ({ Easy = 250, Normal = 1000, Hard = 3000 })[tier],
		count = count,
		needed = needed,
		claimed = false,
		repeats = repeats,
	}
	for k, v in extra or {} do
		q[k] = v
	end
	return q
end
panel:SetQuests({
	quest("DailyGather", "Gather 100 times", "Easy", "Harvest", 60, 100, "Daily"),
	quest("DailyExtract", "Extract once", "Easy", "Extract", 1, 1, "Daily"),
	quest("DailyCraft", "Craft 15 items", "Easy", "Craft", 3, 15, "Daily"),
	quest("DailyHunter", "Defeat 10 creatures", "Normal", "Enemy", 0, 10, "Daily"),
	quest("DailyCaches", "Open 2 caches", "Normal", "Cache", 2, 2, "Daily", { gems = 25, claimed = true }),
	quest("DailyExtractions", "Extract 3 times", "Normal", "Extract", 1, 3, "Daily", { booster = true }),
	quest("DailyBoss", "Defeat a boss", "Hard", "Boss", 0, 1, "Daily", { gems = 25 }),
	quest("FirstGuardian", "Defeat the Guardian", "Hard", "Guardian", 0, 1, "Once", { gems = 50 }),
})
__dump(panel.screen.gui, 1672, 941)
panel:SelectTab("Daily")
panel:Select("DailyExtract")
__dump(panel.screen.gui, 1672, 941)
panel:SelectTab("Once")
__dump(panel.screen.gui, 1672, 941)
