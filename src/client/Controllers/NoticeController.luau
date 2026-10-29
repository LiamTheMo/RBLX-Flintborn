-- One-off important notices from the server (GDD §34.1): e.g. "Server crashed —
-- your items were recovered". Shown on a parchment notice card (Hud/NoticeCard)
-- in the lobby and the world menu until dismissed, with words, not colour alone.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local NoticeCard = require(script.Parent.Parent.Hud.NoticeCard)
local Theme = require(script.Parent.Parent.Ui.Theme)

local NoticeController = {}

local player = Players.LocalPlayer
local card = nil

local function build()
	local gui = Theme.Make(
		"ScreenGui",
		{ Name = "Notice", ResetOnSpawn = false, DisplayOrder = 30 },
		player:WaitForChild("PlayerGui")
	)
	card = NoticeCard.new(gui, {
		name = "Card",
		width = 480,
		title = "",
		onPress = function()
			card:Hide()
		end,
	})
	card.frame.AnchorPoint = Vector2.new(0.5, 0)
	card.frame.Position = UDim2.new(0.5, 0, 0, 90)
end

function NoticeController.Start()
	build()
	Remotes.Get("Notice").OnClientEvent:Connect(function(notice)
		card:Show(notice.text .. "\n\nTap to dismiss.", notice.title)
	end)
end

return NoticeController
