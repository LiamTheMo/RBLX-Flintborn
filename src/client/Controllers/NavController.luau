-- On-screen navigation (GDD §11, §25.4). Every panel that has a keyboard key also
-- gets a large button, so touch and controller players reach the whole game
-- without precise pointing or memorised keys. The lobby lists the vault, Forge,
-- market, trading and progress; the world lists backpack, crafting, building,
-- tribe, map and progress.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Theme = require(script.Parent.Parent.Ui.Theme)

local NavController = {}

local player = Players.LocalPlayer
local make = Theme.Make

local function entries()
	local controllers = script.Parent
	if PlaceConfig.IsLobby() then
		return {
			{ "🔒 Vault (G)", require(controllers.VaultController).Toggle },
			{ "🔥 Forge (F)", require(controllers.ForgeController).Toggle },
			{ "🪙 Market (M)", require(controllers.WalletController).Toggle },
			{ "🤝 Trade (Y)", require(controllers.TradeController).Toggle },
			{ "▲ Progress (P)", require(controllers.ProgressionController).Toggle },
		}
	end
	return {
		{ "🎒 Backpack (B)", require(controllers.InventoryController).ToggleBackpack },
		{ "🔨 Craft (V)", require(controllers.CraftingController).Toggle },
		{ "🧱 Build (X)", require(controllers.BuildController).Toggle },
		{ "⚑ Tribe (T)", require(controllers.TribeController).Toggle },
		{ "🗺 Map (N)", require(controllers.MapController).Toggle },
		{ "▲ Progress (P)", require(controllers.ProgressionController).Toggle },
	}
end

function NavController.Start()
	if not PlaceConfig.IsLobby() and not PlaceConfig.IsWorld() then
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
		local toggle = entry[2]
		button.Activated:Connect(function()
			toggle()
		end)
	end
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
