-- On-screen navigation (GDD §11, §25.4). Every panel that has a keyboard key also
-- gets a large button, so touch and controller players reach the whole game
-- without precise pointing or memorised keys. The lobby lists the vault, Forge,
-- market, trading and progress; the world lists backpack, crafting, building,
-- tribe, map and progress.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local HudMode = require(script.Parent.Parent.Hud.HudMode)
local Binds = require(script.Parent.Parent.Ui.Binds)
local Theme = require(script.Parent.Parent.Ui.Theme)

local NavController = {}

local player = Players.LocalPlayer
local make = Theme.Make

local function entries()
	local controllers = script.Parent
	if PlaceConfig.IsLobby() then
		return {
			-- Lobby panels have no keys of their own (GDD §46); the Backpack key also
			-- opens the vault panel (VaultController, GDD §52).
			{ "🔒 Vault", "Backpack", require(controllers.VaultController).Toggle },
			{ "🔥 Forge", nil, require(controllers.ForgeController).Toggle },
			{ "🪙 Market", nil, require(controllers.WalletController).Toggle },
			{ "🤝 Trade", nil, require(controllers.TradeController).Toggle },
			{ "▲ Progress", "Progression", require(controllers.ProgressionController).Toggle },
		}
	end
	return {
		{ "🎒 Backpack", "Backpack", require(controllers.InventoryController).ToggleBackpack },
		{ "🔨 Craft", "Craft", require(controllers.CraftingController).Toggle },
		{ "🧱 Build", "Build", require(controllers.BuildController).Toggle },
		{ "⚑ Tribe", "Tribe", require(controllers.TribeController).Toggle },
		{ "🗺 Map", "Map", require(controllers.MapController).Toggle },
		{ "▲ Progress", "Progression", require(controllers.ProgressionController).Toggle },
	}
end

function NavController.Start()
	if not PlaceConfig.IsLobby() and not PlaceConfig.IsWorld() then
		return
	end
	-- The lobby HUD (LobbyHudController) and the world HUD (HudController) draw
	-- these buttons as the Kit's menu tiles. This plain bar is only the fallback
	-- for a place where those HUDs cannot build, so it must not depend on the Kit.
	if HudMode.ReplacesLobby() or HudMode.ReplacesLegacy() then
		return
	end
	local gui = make("ScreenGui", { Name = "Navigation", ResetOnSpawn = false }, player:WaitForChild("PlayerGui"))
	local bar = make("Frame", {
		AnchorPoint = Vector2.new(1, 0.5),
		Position = UDim2.new(1, -8, 0.5, 0),
		Size = UDim2.fromOffset(140, 0),
		AutomaticSize = Enum.AutomaticSize.Y,
		BackgroundTransparency = 1,
		Active = true,
	}, gui)
	make("UIListLayout", { Padding = UDim.new(0, 4), HorizontalAlignment = Enum.HorizontalAlignment.Right }, bar)
	local labelled = {}
	for _, entry in entries() do
		local button = make("TextButton", {
			Text = entry[1],
			Size = UDim2.fromOffset(140, Theme.TOUCH_TARGET - 6),
			BackgroundColor3 = Theme.Colors.Panel,
			BackgroundTransparency = 0.2,
			TextColor3 = Theme.Colors.Text,
			TextXAlignment = Enum.TextXAlignment.Left,
			Font = Theme.Fonts.Bold,
			TextSize = Theme.TextSize.Small,
		}, bar)
		make("UICorner", { CornerRadius = UDim.new(0, 6) }, button)
		make("UIPadding", { PaddingLeft = UDim.new(0, 8) }, button)
		local toggle = entry[3]
		button.Activated:Connect(function()
			toggle()
		end)
		table.insert(labelled, { button = button, text = entry[1], action = entry[2] })
	end
	-- Each button names its keyboard key, which follows the player's rebinds.
	local function relabel()
		for _, item in labelled do
			item.button.Text = if item.action
				then ("%s (%s)"):format(item.text, Binds.Label(item.action))
				else item.text
		end
	end
	relabel()
	Binds.Changed:Connect(relabel)
	-- In the world the bar shows only during a run, like the HUD.
	if PlaceConfig.IsWorld() then
		local function refresh()
			bar.Visible = player:GetAttribute("SessionState") == "ActiveRun"
		end
		player:GetAttributeChangedSignal("SessionState"):Connect(refresh)
		refresh()
	end
end

return NavController
