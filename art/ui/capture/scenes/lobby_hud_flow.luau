-- Drives the lobby HUD through LobbyHudController headlessly with real events:
-- progression, currency, party and preview updates arrive through their
-- signals and remotes; tiles, pills, the gear, the Party panel and an
-- invite answer are pressed through their buttons' Activated events. Remotes are
-- mocked as vault_flow does. Ends with a capture of the whole PlayerGui.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
workspace:SetAttribute("FlintbornPlaceRole", "Lobby")

local folder = Instance.new("Folder")
folder.Name = "FlintbornRemotes"
folder.Parent = ReplicatedStorage
local calls = {}
local preview = {
	{ catalogId = "StoneAxe", quantity = 1, permanent = true },
	{ catalogId = "StoneSpear", quantity = 1 },
	{ catalogId = "Wood", quantity = 40 },
}
local handlers = {
	DeployPreview = function()
		return preview
	end,
	PartyAction = function(action, argument)
		table.insert(calls, { "PartyAction", action, argument })
		if action == "leave" then
			return false, "NotInParty"
		end
		return true
	end,
	Deploy = function()
		return true
	end,
}
for name, fn in handlers do
	local remote = Instance.new("RemoteFunction")
	remote.Name = name
	remote.Parent = folder
	remote.InvokeServer = function(_, ...)
		return fn(...)
	end
end
local partyChanged = Instance.new("RemoteEvent")
partyChanged.Name = "PartyChanged"
partyChanged.Parent = folder

local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local Controllers = Client.Controllers
local LobbyController = require(Controllers.LobbyController)
local LobbyHudController = require(Controllers.LobbyHudController)
local ProgressionController = require(Controllers.ProgressionController)
local WalletController = require(Controllers.WalletController)
local SettingsController = require(Controllers.SettingsController)
local ForgeController = require(Controllers.ForgeController)
local TradeController = require(Controllers.TradeController)
local JournalController = require(Controllers.JournalController)
local VaultController = require(Controllers.VaultController)

local function check(cond, msg)
	print((cond and "  ok " or "  FAIL ") .. msg)
	if not cond then
		__failed = true
	end
end

-- Record what the HUD opens instead of building every window.
local opened = {}
local function spy(controller, name, label)
	if type(controller[name]) == "function" then
		controller[name] = function(...)
			table.insert(opened, { label, ... })
		end
	end
end
spy(WalletController, "Open", "Wallet.Open")
spy(SettingsController, "Toggle", "Settings.Toggle")
spy(ForgeController, "Toggle", "Forge.Toggle")
spy(TradeController, "Toggle", "Trade.Toggle")
spy(JournalController, "Open", "Journal.Open")
spy(JournalController, "Toggle", "Journal.Toggle")
spy(VaultController, "Open", "Vault.Open")
spy(VaultController, "Toggle", "Vault.Toggle")
spy(ProgressionController, "Toggle", "Progress.Toggle")
spy(require(Controllers.PartyController), "Open", "PartyController.Open")
spy(require(Controllers.PlayController), "Open", "PlayController.Open")
local VaultChanged = VaultController.Changed
local function last()
	return opened[#opened] and opened[#opened][1]
end

local player = Players.LocalPlayer
LobbyController.Start()
LobbyHudController.Start()
local gui = player.PlayerGui:FindFirstChild("FlintbornLobbyHud")
local hud = LobbyHudController.Hud()
check(gui ~= nil and hud ~= nil, "the HUD builds in the lobby")
check(gui and gui.DisplayOrder == 1 and gui.IgnoreGuiInset == true and gui.ResetOnSpawn == false, "gui setup")

-- Data arrives through change signals, never polled.
check(hud.barLevel.root.Text == "", "level is blank while progression loads")
check(hud.parts.card == nil and gui:FindFirstChild("PlayerCard", true) == nil, "no player card")
ProgressionController.Changed:Fire({ level = 12, xp = 450, xpToNext = 750 })
check(hud.barLevel.root.Text == "LV. 12", "level from ProgressionChanged")
check(hud.barText.root.Text == "450/750 XP", "XP text from ProgressionChanged")
check(math.abs(hud.bar.fraction - 0.6) < 1e-6, "the bar at 0.6")
player:SetAttribute("Coins", 2450)
player:SetAttribute("Gems", 125)
check(hud.coins.label.Text == "2,450" and hud.gems.label.Text == "125", "currency from attributes")
check(hud.slots[1].item and hud.slots[1].item.itemId == "StoneAxe", "hotbar slot 1 from the deploy preview")
check(hud.slots[2].item and hud.slots[2].item.itemId == "StoneSpear", "hotbar slot 2 from the deploy preview")
check(hud.slots[3].item == nil, "materials stay out of the hotbar")
preview = { { catalogId = "StonePickaxe", quantity = 1 } }
LobbyController.FetchPreview()
check(hud.slots[1].item and hud.slots[1].item.itemId == "StonePickaxe", "a new preview redraws the hotbar")
check(hud.slots[2].item == nil, "and empties the rest")

-- Party view from the server.
check(hud.countText.root.Text == "1/8", "solo party 1/8")
check(#hud.parts.members == 1 and #hud.parts.empty == 7, "one member row and seven empty rows")
check(hud.invite and hud.invite.control.flags.enabled ~= false, "solo can invite")
hud.invite.control:Activate()
check(
	last() == "PartyController.Open" and opened[#opened][2] == "invite",
	"the add-player button opens its invite list"
)
local fire = partyChanged.OnClientEvent.Fire
-- Members' levels and XP come from their replicated attributes.
local ranger = Players:GetPlayerByUserId(2)
ranger:SetAttribute("Level", 15)
ranger:SetAttribute("LevelProgress", 0.25)
fire(partyChanged.OnClientEvent, {
	party = {
		id = "p1",
		leader = 2,
		members = {
			{ userId = 2, name = "ForestRanger", ready = true },
			{ userId = 1, name = "LiamTheMo", ready = false },
		},
		invited = {},
	},
	invites = { { partyId = "p9", from = "RiverFox" } },
	ready = false,
	maxSize = 8,
})
check(hud.countText.root.Text == "2/8", "party count from PartyChanged")
check(#hud.parts.members == 2 and #hud.parts.empty == 6, "two members, six free")
check(hud.parts.members[1]:GetAttribute("LobbyReady") == true, "leader's ready flag")
check(hud.parts.members[2]:GetAttribute("LobbyReady") == false, "your not-ready flag")
local function rowFor(root)
	for _, row in hud.rows do
		if row.root == root then
			return row
		end
	end
	return nil
end
local rangerRow = rowFor(hud.parts.members[1])
check(
	rangerRow.levelLabel.Text == "LV. 15" and math.abs(rangerRow.levelBar.fraction - 0.25) < 1e-6,
	"a member row shows the member's level and XP"
)
ranger:SetAttribute("LevelProgress", 0.5)
ranger:SetAttribute("Level", 16)
check(
	rangerRow.levelLabel.Text == "LV. 16" and math.abs(rangerRow.levelBar.fraction - 0.5) < 1e-6,
	"a member's level and XP follow their attribute changes"
)
check(hud.invite.control.flags.enabled == false, "a non-leader's add button is disabled")
check(#hud.parts.answers == 2, "the incoming invite offers accept and decline")

-- Presses go to the owning controllers.
local function press(component)
	component.control:Activate()
end
press(hud.tiles.Shop)
check(last() == "Wallet.Open" and opened[#opened][2] == "Shop", "Shop tile opens the Shop tab")
press(hud.tiles.Forge)
check(last() == "Forge.Toggle", "Forge tile toggles the Forge")
press(hud.tiles.Trade)
check(last() == "Trade.Toggle", "Trade tile toggles Trade")
press(hud.tiles.Quests)
check(last() == "Journal.Open", "Quests tile opens the Journal")
press(hud.tiles.Inventory)
check(last() == "Vault.Open" and opened[#opened][2] == "Backpack", "Inventory tile opens the Backpack tab")
press(hud.tiles.Play)
check(last() == "PlayController.Open", "Play tile opens the Play window")
press(hud.coins)
check(last() == "Wallet.Open", "Coins open the Shop")
press(hud.settings)
check(last() == "Settings.Toggle", "the gear toggles Settings")
hud.titleControl:Activate()
check(last() == "PartyController.Open" and opened[#opened][2] == nil, "the Party title opens the Party window")
local before = #opened
press(hud.invite)
check(#opened == before, "a non-leader's disabled add-player button does nothing")
press(hud.slots[1])
check(last() == "Vault.Open", "a hotbar slot opens the Inventory")
preview = { { catalogId = "StoneSpear", quantity = 1 } }
VaultChanged:Fire({})
check(hud.slots[1].item and hud.slots[1].item.itemId == "StoneSpear", "VaultController.Changed refreshes the hotbar")

-- Answering an invite runs the party action.
local accept
for _, part in hud.rows do
	if part.root.Name == "Accept" then
		accept = part
	end
end
press(accept)
local action = calls[#calls]
check(action and action[2] == "accept" and action[3] == "p9", "accept sends PartyAction accept")

-- Status (a refused party action) and the update notice.
LobbyController.PartyAction("leave")
local toasts = player.PlayerGui:FindFirstChild("KitToasts")
check(toasts ~= nil and #toasts:GetDescendants() > 0, "a status message shows as a toast")
player:SetAttribute("MaintenanceNotice", true)
check(hud.noticeRegion.Visible == true, "the update notice shows while it applies")
player:SetAttribute("MaintenanceNotice", nil)
check(hud.noticeRegion.Visible == false, "and hides after")

-- Redrawing the party list does not leak instances.
local count = #gui:GetDescendants()
for _ = 1, 20 do
	fire(partyChanged.OnClientEvent, LobbyController.PartyView())
end
check(#gui:GetDescendants() == count, "20 party redraws leave the instance count unchanged")

-- Gamepad order through the tile grid.
local tile1 = hud.tiles[1].control.hit
check(tile1.NextSelectionRight == hud.tiles[2].control.hit, "Inventory -> Play")
check(tile1.NextSelectionDown == hud.tiles[3].control.hit, "Inventory v Quests")
check(hud.tiles[5].control.hit.NextSelectionDown == hud.slots[1].control.hit, "Forge v hotbar")
check(hud:DefaultSelection() == tile1, "default selection is the Inventory tile")

assert(not __failed, "lobby_hud_flow: a check failed")
__dump(player.PlayerGui, 1672, 941)
