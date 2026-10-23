-- Wallet, shops, merchant, quests and offers (GDD §10, §25.4.1, §36). The lobby
-- shows Coins and Gems at all times; M (or ButtonL2) opens the market panel with
-- tabs: Shop, Sell, Quests and Vault & offers. Every Robux offer shows its earnable
-- equivalent next to it. Lobby place only.

local ContextActionService = game:GetService("ContextActionService")
local HttpService = game:GetService("HttpService")
local MarketplaceService = game:GetService("MarketplaceService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)

local WalletController = {}

WalletController.SELL_STEP = 10

local player = Players.LocalPlayer
local ui = {}
local tab = "Shop"

local TEXT = Color3.fromRGB(235, 226, 212)
local GOLD = Color3.fromRGB(255, 214, 150)
local WARN = Color3.fromRGB(255, 170, 120)

local function make(className: string, props, parent)
	local instance = Instance.new(className)
	for key, value in props do
		instance[key] = value
	end
	instance.Parent = parent
	return instance
end

local function invoke(name: string, ...)
	local ok, success, reason = pcall(Remotes.Get(name).InvokeServer, Remotes.Get(name), ...)
	if not ok then
		return false, "Request failed"
	end
	return success, reason
end

local function nonce(): string
	return HttpService:GenerateGUID(false)
end

local function line(text: string, color: Color3?, order: number)
	return make("TextLabel", {
		Text = text,
		Size = UDim2.new(1, -8, 0, 0),
		AutomaticSize = Enum.AutomaticSize.Y,
		BackgroundTransparency = 1,
		TextXAlignment = Enum.TextXAlignment.Left,
		TextWrapped = true,
		TextColor3 = color or TEXT,
		Font = Enum.Font.GothamMedium,
		TextSize = 13,
		LayoutOrder = order,
	}, ui.list)
end

local render

local function button(text: string, enabled: boolean, order: number, onClick)
	local b = make("TextButton", {
		Text = text,
		Size = UDim2.new(1, -8, 0, 28),
		BackgroundColor3 = if enabled then Color3.fromRGB(110, 70, 30) else Color3.fromRGB(50, 44, 38),
		TextColor3 = if enabled then Color3.fromRGB(255, 240, 220) else Color3.fromRGB(140, 130, 120),
		AutoButtonColor = enabled,
		TextXAlignment = Enum.TextXAlignment.Left,
		TextTruncate = Enum.TextTruncate.AtEnd,
		Font = Enum.Font.GothamBold,
		TextSize = 13,
		LayoutOrder = order,
	}, ui.list)
	make("UICorner", { CornerRadius = UDim.new(0, 6) }, b)
	make("UIPadding", { PaddingLeft = UDim.new(0, 8) }, b)
	if enabled then
		b.Activated:Connect(function()
			onClick()
			render()
		end)
	end
end

local function report(ok, result, success: string)
	ui.status.Text = if ok then success else ("Not done: " .. tostring(result))
end

local function updateWallet()
	ui.wallet.Text = ("🪙 %d   💎 %d"):format(player:GetAttribute("Coins") or 0, player:GetAttribute("Gems") or 0)
end

function render()
	for _, child in ui.list:GetChildren() do
		if not child:IsA("UIListLayout") then
			child:Destroy()
		end
	end
	for name, b in ui.tabs do
		b.BackgroundColor3 = if name == tab then Color3.fromRGB(110, 70, 30) else Color3.fromRGB(46, 38, 30)
	end
	local order = 0
	local function nextOrder()
		order += 1
		return order
	end
	local coins = player:GetAttribute("Coins") or 0
	if tab == "Quests" then
		local quests = invoke("QuestView")
		if type(quests) ~= "table" then
			line("Your data is still loading.", TEXT, nextOrder())
			return
		end
		for _, quest in quests do
			local reward = ("%d Coins%s%s"):format(
				quest.coins,
				quest.gems and (" + " .. quest.gems .. " Gems") or "",
				quest.booster and " + XP booster" or ""
			)
			local text = ("[%s] %s — %d/%d · %s%s"):format(
				quest.tier,
				quest.name,
				quest.count,
				quest.needed,
				reward,
				quest.repeats == "Daily" and " (daily)" or ""
			)
			if quest.claimed then
				line("✓ " .. text, Color3.fromRGB(150, 200, 150), nextOrder())
			else
				button(text, quest.count >= quest.needed, nextOrder(), function()
					report(invoke("QuestClaim", quest.id), "Quest reward claimed.")
				end)
			end
		end
		return
	end
	local view = invoke("ShopView")
	if type(view) ~= "table" then
		line("Your data is still loading.", TEXT, nextOrder())
		return
	end
	if tab == "Shop" then
		line("Purchases go to your lobby backpack.", TEXT, nextOrder())
		for _, entry in view.stock do
			local text = ("%s%s — %d Coins"):format(
				entry.name,
				entry.quantity and (" ×" .. entry.quantity) or "",
				entry.price
			)
			if entry.owned then
				line("✓ " .. text, Color3.fromRGB(150, 200, 150), nextOrder())
			else
				button(text, coins >= entry.price, nextOrder(), function()
					report(invoke("ShopBuy", entry.id, nonce()), "Bought " .. entry.name .. ".")
				end)
			end
		end
	elseif tab == "Sell" then
		line("Merchants pay fixed prices. Vault materials sell 10 at a time.", TEXT, nextOrder())
		for _, entry in view.sellable do
			local quantity = if entry.source == "vault"
				then math.min(WalletController.SELL_STEP, entry.quantity)
				else nil
			local coinsFor = entry.coins or (entry.each * quantity)
			local text = ("Sell %s%s for %d Coins"):format(
				entry.name,
				quantity and (" ×" .. quantity) or (entry.quantity and (" ×" .. entry.quantity) or ""),
				coinsFor
			)
			button(text, true, nextOrder(), function()
				report(invoke("MerchantSell", entry.source, entry.key, quantity, nonce()), "Sold.")
			end)
			if entry.warning then
				line("⚠ " .. entry.warning, WARN, nextOrder())
			end
		end
	else
		line(("Vault tier %d / %d (+25 item slots each)"):format(view.vaultTier, view.maxVaultTier), GOLD, nextOrder())
		local gems = player:GetAttribute("Gems") or 0
		button(
			("Upgrade the vault for %d Gems"):format(view.vaultPrice),
			view.vaultTier < view.maxVaultTier and gems >= view.vaultPrice,
			nextOrder(),
			function()
				report(invoke("VaultUpgrade", nonce()), "Vault upgraded.")
			end
		)
		button(
			("Respec rebirth perks for %d Gems"):format(view.respecGems),
			gems >= view.respecGems,
			nextOrder(),
			function()
				report(invoke("PerkRespec", nonce()), "Perk tokens refunded.")
			end
		)
		line("Robux offers — each has an earnable route:", GOLD, nextOrder())
		for _, offer in view.offers do
			local available = offer.productId ~= 0
			button(offer.name .. (if available then "" else " (coming soon)"), available, nextOrder(), function()
				MarketplaceService:PromptProductPurchase(player, offer.productId)
			end)
			line("   Earn it instead: " .. offer.earnable, TEXT, nextOrder())
		end
	end
end

local function build()
	local gui = make("ScreenGui", { Name = "Wallet", ResetOnSpawn = false }, player:WaitForChild("PlayerGui"))
	ui.wallet = make("TextLabel", {
		AnchorPoint = Vector2.new(1, 0),
		Position = UDim2.new(1, -12, 0, 12),
		Size = UDim2.fromOffset(200, 28),
		BackgroundColor3 = Color3.fromRGB(28, 24, 20),
		BackgroundTransparency = 0.15,
		TextColor3 = GOLD,
		Font = Enum.Font.GothamBold,
		TextSize = 15,
	}, gui)
	make("UICorner", { CornerRadius = UDim.new(0, 8) }, ui.wallet)
	ui.panel = make("Frame", {
		AnchorPoint = Vector2.new(0.5, 0.5),
		Position = UDim2.fromScale(0.45, 0.5),
		Size = UDim2.new(0.45, 0, 0.75, 0),
		BackgroundColor3 = Color3.fromRGB(24, 20, 17),
		Visible = false,
	}, gui)
	make("UICorner", { CornerRadius = UDim.new(0, 8) }, ui.panel)
	make("UISizeConstraint", { MaxSize = Vector2.new(560, 620), MinSize = Vector2.new(320, 320) }, ui.panel)
	local close = make("TextButton", {
		Text = "✕",
		AnchorPoint = Vector2.new(1, 0),
		Position = UDim2.new(1, -6, 0, 6),
		Size = UDim2.fromOffset(28, 24),
		BackgroundColor3 = Color3.fromRGB(70, 56, 40),
		TextColor3 = Color3.fromRGB(245, 236, 222),
		Font = Enum.Font.GothamBold,
		TextSize = 14,
	}, ui.panel)
	close.Activated:Connect(function()
		ui.panel.Visible = false
	end)
	ui.tabs = {}
	for index, name in { "Shop", "Sell", "Quests", "Vault & offers" } do
		local b = make("TextButton", {
			Text = name,
			Position = UDim2.fromOffset(8 + (index - 1) * 108, 6),
			Size = UDim2.fromOffset(104, 24),
			TextColor3 = Color3.fromRGB(245, 236, 222),
			Font = Enum.Font.GothamBold,
			TextSize = 12,
		}, ui.panel)
		make("UICorner", { CornerRadius = UDim.new(0, 6) }, b)
		b.Activated:Connect(function()
			tab = name
			ui.status.Text = ""
			render()
		end)
		ui.tabs[name] = b
	end
	ui.list = make("ScrollingFrame", {
		Position = UDim2.fromOffset(10, 38),
		Size = UDim2.new(1, -20, 1, -70),
		BackgroundTransparency = 1,
		AutomaticCanvasSize = Enum.AutomaticSize.Y,
		CanvasSize = UDim2.new(),
		ScrollBarThickness = 6,
	}, ui.panel)
	make("UIListLayout", { Padding = UDim.new(0, 4), SortOrder = Enum.SortOrder.LayoutOrder }, ui.list)
	ui.status = make("TextLabel", {
		Text = "",
		AnchorPoint = Vector2.new(0, 1),
		Position = UDim2.new(0, 10, 1, -6),
		Size = UDim2.new(1, -20, 0, 22),
		BackgroundTransparency = 1,
		TextXAlignment = Enum.TextXAlignment.Left,
		TextColor3 = TEXT,
		Font = Enum.Font.Gotham,
		TextSize = 13,
	}, ui.panel)
	-- Codes (Q89): typed into a box under the panel.
	local codeBox = make("TextBox", {
		PlaceholderText = "Redeem a code",
		Text = "",
		AnchorPoint = Vector2.new(1, 0),
		Position = UDim2.new(1, -12, 0, 44),
		Size = UDim2.fromOffset(200, 26),
		BackgroundColor3 = Color3.fromRGB(40, 34, 28),
		TextColor3 = TEXT,
		Font = Enum.Font.Gotham,
		TextSize = 13,
		ClearTextOnFocus = false,
	}, gui)
	make("UICorner", { CornerRadius = UDim.new(0, 6) }, codeBox)
	codeBox.FocusLost:Connect(function(enterPressed)
		if enterPressed and codeBox.Text ~= "" then
			local ok, reason = invoke("RedeemCode", codeBox.Text)
			codeBox.Text = ""
			codeBox.PlaceholderText = if ok then "Code redeemed!" else ("Code: " .. tostring(reason))
		end
	end)
end

-- Opens or closes this panel (keys, and the on-screen navigation bar).
function WalletController.Toggle()
	ui.panel.Visible = not ui.panel.Visible
	if ui.panel.Visible then
		ui.status.Text = ""
		render()
	end
end

function WalletController.Start()
	if not PlaceConfig.IsLobby() then
		return
	end
	build()
	updateWallet()
	player:GetAttributeChangedSignal("Coins"):Connect(updateWallet)
	player:GetAttributeChangedSignal("Gems"):Connect(updateWallet)
	ContextActionService:BindAction("FlintbornMarket", function(_, state)
		if state == Enum.UserInputState.Begin then
			WalletController.Toggle()
		end
		return Enum.ContextActionResult.Pass
	end, false, Enum.KeyCode.M, Enum.KeyCode.ButtonL2)
end

return WalletController
