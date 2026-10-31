-- The kit notice cards: a server notice through the real NoticeController (its
-- remote fired with sample text), a trade invite and the safe-camp note built the
-- way TradeController and MapController build them, and the run's toasts
-- (Kit.Toast) at the top centre, over the lobby backdrop.
--
--   python3 art/ui/capture/capture.py notices

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local W, H = 1672, 941
workspace.CurrentCamera.ViewportSize = Vector2.new(W, H)
local folder = Instance.new("Folder")
folder.Name = "FlintbornRemotes"
folder.Parent = ReplicatedStorage
local notice = Instance.new("RemoteEvent")
notice.Name = "Notice"
notice.Parent = folder

local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local Kit = require(Client.Hud.Kit)
local NoticeCard = require(Client.Hud.NoticeCard)
local NoticeController = require(Client.Controllers.NoticeController)
local player = Players.LocalPlayer
local gui = player.PlayerGui

local function check(cond, msg)
	print((cond and "  ok " or "  FAIL ") .. msg)
	if not cond then
		__failed = true
	end
end

NoticeController.Start()
notice.OnClientEvent:Fire({
	title = "Items recovered",
	text = "The server restarted. Everything you carried was recovered to your vault.",
})
local card = gui:FindFirstChild("Card", true)
check(card and card.Visible, "the server notice shows")

-- A trade invite (TradeController) and the safe-camp note (MapController).
local side = Instance.new("ScreenGui")
side.Name = "Samples"
side.Parent = gui
local invite = NoticeCard.new(side, { name = "TradeInvite", width = 420, title = "Trade invite" })
invite.frame.Position = UDim2.fromOffset(80, 420)
invite:AddButton("Accept", nil, function() end)
invite:AddButton("Decline", "paper", function() end)
invite:Show("River wants to trade with you.")
local safe = NoticeCard.new(side, { name = "Safe", width = 360, title = "Safe camp" })
safe.frame.Position = UDim2.fromOffset(1220, 440)
safe:SetTone("haveEnough")
safe:Show("Elder's Camp: no damage here.")
check(safe.text.Text == "Elder's Camp: no damage here.", "the note's text reads back as given")

Kit.Toast.Show({ kind = "item", title = "Item received", text = "Iron Pickaxe", icon = "backpack", duration = 4 })
Kit.Toast.Show({ kind = "info", title = "Backpack full", text = "Flint stayed on the ground.", duration = 4 })

__dump(gui, W, H, { background = "art/reference/ui/lobby/01_hud.png" })

-- Dismissing: a press anywhere on the server notice hides it.
card:FindFirstChild("Press").Activated:Fire()
check(not card.Visible, "pressing the notice dismisses it")
print(__failed and "SCENE FAILED" or "SCENE OK")
if __failed then
	error("notices failed")
end
