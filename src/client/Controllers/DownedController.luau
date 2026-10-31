-- Downed overlay (GDD §5.3, §25.4): the bleed-out timer (marked paused while a
-- revive runs), downed health, who is reviving and their progress. Crawling uses
-- normal movement at the server's crawl speed. A kit notice card in the shared
-- top-centre column: the bar shows the bleed-out time left, or the revive's
-- progress while someone revives you. World place only.

local GameConstants = require(game:GetService("ReplicatedStorage").Shared.GameConstants)
local PlaceConfig = require(game:GetService("ReplicatedStorage").Shared.Config.PlaceConfig)
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")

local NoticeCard = require(script.Parent.Parent.Hud.NoticeCard)
local Theme = require(script.Parent.Parent.Ui.Theme)

local DownedController = {}

local player = Players.LocalPlayer
local ui = {}

local function build()
	-- Lives in the shared top-centre column so it never covers the other banners.
	ui.card = NoticeCard.new(Theme.TopStack(), {
		name = "Downed",
		width = 480,
		layoutOrder = Theme.TopOrder.Downed,
		title = "Downed",
		icon = "heart",
	})
	ui.card:SetTone("short")
end

local function update()
	local isDowned = player:GetAttribute("Downed") == true
	if not isDowned then
		ui.card:Hide()
		return
	end
	local remaining = player:GetAttribute("DownedRemaining") or 0
	local health = player:GetAttribute("DownedHealth") or 0
	local reviver = player:GetAttribute("DownedReviver")
	local progress = player:GetAttribute("DownedReviveProgress") or 0
	local lines = {}
	if reviver then
		table.insert(lines, ("Bleed-out PAUSED at %d s"):format(remaining))
		table.insert(lines, ("%s is reviving you: %.1f / %d s"):format(reviver, progress, GameConstants.REVIVE_SECONDS))
		ui.card:SetBar(progress / GameConstants.REVIVE_SECONDS, "green", "Revive")
	else
		table.insert(lines, ("Bleeding out in %d s — anyone can revive you"):format(remaining))
		ui.card:SetBar(remaining / GameConstants.BLEED_OUT_SECONDS, "red", "Bleed-out")
	end
	table.insert(lines, "You can crawl slowly but cannot heal.")
	ui.card:Show(table.concat(lines, "\n"), ("Downed — %d HP left"):format(health))
end

function DownedController.Start()
	if not PlaceConfig.IsWorld() then
		return
	end
	build()
	RunService.RenderStepped:Connect(update)
end

return DownedController
