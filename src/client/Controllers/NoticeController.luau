-- One-off important notices from the server (GDD §34.1): e.g. "Server crashed —
-- your items were recovered". Shown on a kit notice card (Hud/NoticeCard) in the
-- lobby and the world menu until dismissed (the ✕, or a press anywhere on the
-- card), with words, not colour alone.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local NoticeCard = require(script.Parent.Parent.Hud.NoticeCard)
local Theme = require(script.Parent.Parent.Ui.Theme)

local NoticeController = {}

NoticeController.WIDTH = 520

local player = Players.LocalPlayer
local card = nil

local function build()
	local gui = Theme.Make("ScreenGui", {
		Name = "Notice",
		ResetOnSpawn = false,
		DisplayOrder = 30,
		ZIndexBehavior = Enum.ZIndexBehavior.Sibling,
	}, player:WaitForChild("PlayerGui"))
	-- Top centre, clear of the top bar; scaled with the HUD.
	local holder = Theme.Make("Frame", {
		Name = "Holder",
		AnchorPoint = Vector2.new(0.5, 0),
		BackgroundTransparency = 1,
		Position = UDim2.new(0.5, 0, 0, 90),
		Size = UDim2.fromOffset(NoticeController.WIDTH, 0),
	}, gui)
	Theme.FitHud(gui, Theme.Make("UIScale", { Name = "Fit" }, holder))
	card = NoticeCard.new(holder, {
		name = "Card",
		width = NoticeController.WIDTH,
		title = "",
		icon = "exclamation",
		onPress = function()
			card:Hide()
		end,
	})
end

function NoticeController.Start()
	build()
	Remotes.Get("Notice").OnClientEvent:Connect(function(notice)
		card:Show(notice.text, notice.title)
	end)
end

return NoticeController
