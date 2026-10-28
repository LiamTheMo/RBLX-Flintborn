-- The parchment notice cards: a server notice, a trade invite with its buttons,
-- a run toast and an extraction receipt, as they stack at the top centre.
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local player = Players.LocalPlayer
local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local NoticeCard = require(Client.Hud.NoticeCard)
local Theme = require(Client.Ui.Theme)
local stack = Theme.TopStack()
stack.Position = UDim2.new(0.5, 0, 0, 20)
local invite = NoticeCard.new(stack, { name = "TradeInvite", width = 420, layoutOrder = 9, title = "Trade invite" })
invite:AddButton("ACCEPT", nil, function() end)
invite:AddButton("DECLINE", "paper", function() end)
invite:Show("River wants to trade with you.")
local toast = NoticeCard.new(stack, { name = "Toast", width = 420, layoutOrder = 10 })
toast:Show("Backpack full: Flint stayed on the ground.")
local receipt = NoticeCard.new(stack, { name = "Receipt", width = 480, layoutOrder = 8, title = "Extraction receipt" })
receipt:Show(
	"Extracted at North Portal — Center bonus ×2 materials\nBanked to vault: Iron Bar ×12, Wood ×40\nLobby backpack: Iron Sword ×1\n\nTap to dismiss."
)
-- The server notice has its own gui in game; drawn here beside the stack.
local gui = stack.Parent
local notice = NoticeCard.new(gui, { name = "Card", width = 480, title = "" })
notice.frame.AnchorPoint = Vector2.new(0.5, 0)
notice.frame.Position = UDim2.new(0.5, 0, 0, 560)
notice:Show("The server restarted. Everything you carried was recovered to your vault.\n\nTap to dismiss.", "Items recovered")
__dump(gui, 1280, 820)
