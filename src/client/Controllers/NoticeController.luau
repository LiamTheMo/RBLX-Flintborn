-- One-off important notices from the server (GDD §34.1): e.g. "Server crashed —
-- your items were recovered". Shown on a kit notice card (Hud/NoticeCard) in the
-- lobby and the world menu until dismissed (the ✕, or a press anywhere on the
-- card), with words, not colour alone. While it shows, the kit's toast column
-- keeps below it (Kit.Toast.Avoid), so toasts never cover its title.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local Kit = require(script.Parent.Parent.Hud.Kit)
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
	-- Upper middle, under the kit's toast column (up to three toasts); scaled
	-- with the HUD.
	local holder = Theme.Make("Frame", {
		Name = "Holder",
		AnchorPoint = Vector2.new(0.5, 0),
		BackgroundTransparency = 1,
		Position = UDim2.fromScale(0.5, 0.38),
		Size = UDim2.fromOffset(NoticeController.WIDTH, 0),
	}, gui)
	Theme.FitHud(gui, Theme.Make("UIScale", { Name = "Fit" }, holder))
	card = NoticeCard.new(holder, {
		name = "Card",
		width = NoticeController.WIDTH,
		title = "",
		icon = "exclamation",
		onPress = function()
			NoticeController.Hide()
		end,
	})
end

function NoticeController.Show(text: string, title: string?)
	card:Show(text, title)
	Kit.Toast.Avoid(card.frame)
end

function NoticeController.Hide()
	card:Hide()
	Kit.Toast.Avoid(nil)
end

function NoticeController.Start()
	build()
	Remotes.Get("Notice").OnClientEvent:Connect(function(notice)
		NoticeController.Show(notice.text, notice.title)
	end)
end

return NoticeController
