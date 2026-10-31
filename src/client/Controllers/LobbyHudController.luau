-- The lobby's always-on HUD (GDD §11, §25; docs/ui/LobbyScreen.md, ARCHITECTURE
-- §4.1): the player card, Coins, Gems and Settings, the menu tiles, the Party
-- panel, the XP bar and the hotbar that shows the deploy loadout, drawn by
-- Hud/Screens/LobbyHud from the shared Kit. There is no Enter button or server
-- choice here: the Play tile opens the Play window, which deploys.
-- Lobby place only (HudMode.ReplacesLobby); the older lobby visuals stay hidden.
-- If the HUD fails to build, the lobby falls back to those older visuals.
--
-- Everything acts through the existing controllers: the tiles open the
-- Inventory (VaultController), Play (PlayController), Quests (JournalController),
-- Shop (WalletController), Forge and Trade; the card opens Progress, the pills the
-- Shop, the gear Settings, the Party panel the Party window (PartyController).

local GuiService = game:GetService("GuiService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local LobbyHudModel = require(ReplicatedStorage.Shared.UI.LobbyHudModel)
local ForgeController = require(script.Parent.ForgeController)
local JournalController = require(script.Parent.JournalController)
local LobbyController = require(script.Parent.LobbyController)
local PartyController = require(script.Parent.PartyController)
local PlayController = require(script.Parent.PlayController)
local ProgressionController = require(script.Parent.ProgressionController)
local SettingsController = require(script.Parent.SettingsController)
local TradeController = require(script.Parent.TradeController)
local VaultController = require(script.Parent.VaultController)
local WalletController = require(script.Parent.WalletController)
local Hud = script.Parent.Parent.Hud
local HudMode = require(Hud.HudMode)
local Kit = require(Hud.Kit)
local LobbyHud = require(Hud.Screens.LobbyHud)

local LobbyHudController = {}

-- How long a status message toast stays.
LobbyHudController.STATUS_SECONDS = 6

local player = Players.LocalPlayer
local gui, root, hud
-- Everything start() connected, so a failed start leaves nothing bound to a
-- destroyed HUD.
local connections = {}
local stops = {}

local function keep(connection)
	table.insert(connections, connection)
	return connection
end

-- The lobby backpack lives in the Inventory window beside the vault.
local function openInventory()
	VaultController.Open("Backpack", Kit.Input.IsGamepad())
end

local TILE_ACTIONS = {
	Inventory = openInventory,
	Play = function()
		PlayController.Open()
	end,
	Quests = function()
		JournalController.Open()
	end,
	Shop = function()
		WalletController.Open("Shop")
	end,
	Forge = function()
		ForgeController.Toggle()
	end,
	Trade = function()
		TradeController.Toggle()
	end,
}

local function openParty(section: string?)
	PartyController.Open(section)
end

local function refreshParty()
	hud:SetParty(
		LobbyHudModel.Party(
			LobbyController.PartyView(),
			{ userId = player.UserId, name = player.DisplayName },
			PartyController.AnswerBusy()
		)
	)
end

local function refreshHotbar()
	hud:SetHotbar(LobbyHudModel.Hotbar(LobbyController.Preview()))
end

local function refreshCurrency(instant: boolean?)
	hud:SetCurrency(player:GetAttribute("Coins"), player:GetAttribute("Gems"), instant)
end

-- The game-update notice plaque while it applies; its status line is not
-- toasted again.
local function refreshNotice()
	hud:SetNotice(if player:GetAttribute("MaintenanceNotice") then LobbyController.MAINTENANCE_TEXT else nil)
end

local function showStatus()
	local text = LobbyController.Status()
	if text == "" or text == LobbyController.MAINTENANCE_TEXT then
		return
	end
	-- A party request PartyController sent reports its own refusal (once).
	if PartyController.Reporting() then
		return
	end
	Kit.Toast.Show({ kind = "info", title = "Lobby", text = text, duration = LobbyHudController.STATUS_SECONDS })
end

local function build()
	gui = Instance.new("ScreenGui")
	gui.Name = "FlintbornLobbyHud"
	gui.ResetOnSpawn = false
	gui.DisplayOrder = Kit.Tokens.Order("hud")
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	-- The layout uses the mockup's full-screen coordinates and keeps clear of the
	-- top bar itself (LobbyHud:SetTopInset); device cut-outs stay excluded.
	gui.IgnoreGuiInset = true
	pcall(function()
		gui.ScreenInsets = Enum.ScreenInsets.DeviceSafeInsets
	end)
	root = Instance.new("Frame")
	root.Name = "Root"
	root.BackgroundTransparency = 1
	root.Size = UDim2.fromScale(1, 1)
	root.Parent = gui
	hud = LobbyHud.new(root, {
		onProfile = function()
			ProgressionController.Toggle()
		end,
		onCurrency = function()
			WalletController.Open("Shop")
		end,
		onSettings = function()
			SettingsController.Toggle()
		end,
		onTile = function(id: string)
			local action = TILE_ACTIONS[id]
			if action then
				action()
			end
		end,
		onParty = openParty,
		onAnswer = function(partyId: string, accept: boolean)
			PartyController.Answer(partyId, accept)
		end,
		onSlot = openInventory,
	})
	ProgressionController.MountPopups(hud.popups)
	gui.Parent = player:WaitForChild("PlayerGui")
end

-- Root scale (HudModel.HudScale, × 0.9 on short touch screens) and the top bar's
-- reach in design px.
local function watchScale()
	table.insert(stops, Kit.Scale.Hud(gui, root))
	local scale = root:FindFirstChildWhichIsA("UIScale") :: UIScale
	local function inset()
		hud:SetTopInset(Kit.Scale.WindowTop(gui) / math.max(scale.Scale, 0.01))
	end
	keep(scale:GetPropertyChangedSignal("Scale"):Connect(inset))
	keep(gui:GetPropertyChangedSignal("AbsoluteSize"):Connect(inset))
	pcall(function()
		keep(GuiService:GetPropertyChangedSignal("TopbarInset"):Connect(inset))
	end)
	inset()
end

local function start()
	build()
	watchScale()
	-- A gamepad picked up with nothing selected lands on the first menu tile.
	Kit.Input.SetHudDefault(hud:DefaultSelection())

	hud:SetProfile(player.DisplayName, player.UserId)
	hud:SetProgress(ProgressionController.View(), true)
	keep(ProgressionController.Changed:Connect(function(view)
		hud:SetProgress(view, Kit.Motion.Reduced())
	end))
	refreshCurrency(true)
	keep(player:GetAttributeChangedSignal("Coins"):Connect(refreshCurrency))
	keep(player:GetAttributeChangedSignal("Gems"):Connect(refreshCurrency))
	refreshNotice()
	keep(player:GetAttributeChangedSignal("MaintenanceNotice"):Connect(refreshNotice))

	refreshParty()
	refreshHotbar()
	-- Invite answers go through PartyController, which watches the party view.
	PartyController.Start()
	-- An invite answer starting or ending (busy buttons).
	keep(PartyController.Changed:Connect(refreshParty))
	keep(LobbyController.Changed:Connect(function(what)
		if what == "party" then
			refreshParty()
		elseif what == "preview" then
			refreshHotbar()
		elseif what == "status" then
			showStatus()
		end
	end))
	-- A backpack or vault change re-reads the deploy preview (and so the hotbar).
	keep(VaultController.Changed:Connect(function()
		LobbyController.RefreshPreview()
	end))
end

-- Undoes a partial start: every connection, the scale watcher and the HUD.
local function teardown()
	for _, connection in connections do
		connection:Disconnect()
	end
	table.clear(connections)
	for _, stop in stops do
		stop()
	end
	table.clear(stops)
	Kit.Input.SetHudDefault(nil)
	if hud then
		pcall(hud.Destroy, hud)
		hud = nil
	end
	if gui then
		gui:Destroy()
		gui = nil
	end
end

-- The HUD screen object (scenes and verifiers), or nil before Start.
function LobbyHudController.Hud()
	return hud
end

function LobbyHudController.Start()
	if not HudMode.ReplacesLobby() then
		return
	end
	local ok, err = pcall(start)
	if not ok then
		-- Never leave the lobby without Deploy: hand it back to the older visuals.
		warn("[LobbyHud] failed to build, using the older lobby screen: " .. tostring(err))
		teardown()
		HudMode.SetLobbyFailed()
		LobbyController.BuildFallback()
	end
end

return LobbyHudController
