-- Wallet, shops, merchant, offers and codes (GDD §10, §25.4.1, §36) in the
-- parchment Market window (Hud/ListWindow). The lobby shows Coins and Gems at
-- all times; the Market navigation button opens the window with tabs: Shop,
-- Sell, Offers (vault upgrades, perk respec and Robux offers, each with its
-- earnable equivalent next to it) and Codes. Quests live in the Journal.
-- Lobby place only.

local ContextActionService = game:GetService("ContextActionService")
local GuiService = game:GetService("GuiService")
local HttpService = game:GetService("HttpService")
local MarketplaceService = game:GetService("MarketplaceService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local HudMode = require(script.Parent.Parent.Hud.HudMode)
local ListWindow = require(script.Parent.Parent.Hud.ListWindow)
local Reasons = require(script.Parent.Parent.Ui.Reasons)

local WalletController = {}

WalletController.SELL_STEP = 10
WalletController.TABS = {
	{ id = "Shop", label = "Shop", glyph = "pm_glyph_bag" },
	{ id = "Sell", label = "Sell", glyph = "pm_glyph_weight" },
	{ id = "Offers", label = "Offers", glyph = "pm_glyph_diamond" },
	{ id = "Codes", label = "Codes", glyph = "pm_glyph_tent" },
}

local player = Players.LocalPlayer
local window = nil
local wallet = nil
local tab = "Shop"
-- Bumped by every render; a render that yielded and is no longer the latest drops.
local renderToken = 0

local CLOSE_ACTION = "FlintbornMarketClose"
local GOLD = Color3.fromRGB(255, 214, 150)

local function invoke(name: string, ...)
	local ok, success, reason = pcall(Remotes.Get(name).InvokeServer, Remotes.Get(name), ...)
	if not ok then
		return false, "Request failed"
	end
	return success, if success then reason else Reasons.Text(reason)
end

local function nonce(): string
	return HttpService:GenerateGUID(false)
end

local render

-- Runs a request from a button, then shows its outcome and redraws.
local function act(success: string, name: string, ...)
	local ok, result = invoke(name, ...)
	window:SetStatus(if ok then success else ("Not done: " .. tostring(result)))
	render()
end

local function updateWallet()
	local coins, gems = player:GetAttribute("Coins") or 0, player:GetAttribute("Gems") or 0
	if wallet then
		wallet.Text = ("🪙 %d   💎 %d"):format(coins, gems)
	end
	if window then
		window:SetCorner({
			{ icon = "pm_icon_coin", text = tostring(coins) },
			{ icon = "pm_icon_gem", text = tostring(gems) },
		})
	end
end

local function drawShop(view)
	local coins = player:GetAttribute("Coins") or 0
	window:Line("Starter supplies. Purchases go to your lobby backpack.")
	-- Grouped by category, in stock order.
	local categories, byCategory = {}, {}
	for _, entry in view.stock do
		local category = entry.category or "Other"
		if byCategory[category] == nil then
			byCategory[category] = {}
			table.insert(categories, category)
		end
		table.insert(byCategory[category], entry)
	end
	for _, category in categories do
		window:Section(category)
		for _, entry in byCategory[category] do
			window:Row({
				key = entry.id,
				title = entry.name .. (if entry.quantity then (" ×" .. entry.quantity) else ""),
				detail = entry.note,
				icon = entry.catalogId,
				glyph = "pm_glyph_bag",
				value = tostring(entry.price),
				valueIcon = "pm_icon_coin",
				done = entry.owned,
				buttons = if entry.owned
					then nil
					else {
						{
							label = "BUY",
							key = "Buy",
							enabled = coins >= entry.price,
							onPress = function()
								act("Bought " .. entry.name .. ".", "ShopBuy", entry.id, nonce())
							end,
						},
					},
			})
		end
	end
end

local function drawSell(view)
	window:Line(
		"Merchants pay fixed prices; crafted gear is worth 40% of its materials. Withdraw gear from the vault to sell it."
	)
	local heading = nil
	for _, entry in view.sellable do
		if entry.source ~= heading then
			heading = entry.source
			window:Section(if heading == "vault" then "From your vault" else "From your lobby backpack")
		end
		local buttons, detail, value
		if entry.source == "vault" then
			-- The next SELL_STEP, and the whole stack (never for a Forge reagent,
			-- which warns).
			local step = math.min(WalletController.SELL_STEP, entry.quantity)
			buttons = {
				{
					label = ("SELL %d"):format(step),
					key = "Step",
					onPress = function()
						act("Sold.", "MerchantSell", "vault", entry.key, step, nonce())
					end,
				},
			}
			if entry.quantity > step and not entry.warning then
				table.insert(buttons, {
					label = "SELL ALL",
					key = "All",
					kind = "paper",
					onPress = function()
						act("Sold.", "MerchantSell", "vault", entry.key, entry.quantity, nonce())
					end,
				})
			end
			detail = ("%d in your vault"):format(entry.quantity)
			value = ("%d each"):format(entry.each)
		else
			buttons = {
				{
					label = "SELL",
					key = "Sell",
					onPress = function()
						act("Sold.", "MerchantSell", entry.source, entry.key, nil, nonce())
					end,
				},
			}
			value = tostring(entry.coins)
		end
		if entry.warning then
			detail = (if detail then detail .. ". " else "") .. entry.warning
		end
		window:Row({
			key = entry.source .. tostring(entry.key),
			title = entry.name
				.. (if entry.source == "backpack" and entry.quantity then (" ×" .. entry.quantity) else ""),
			detail = detail,
			icon = entry.catalogId,
			glyph = "pm_glyph_weight",
			value = value,
			valueIcon = "pm_icon_coin",
			buttons = buttons,
		})
	end
	if heading == nil then
		window:Line("Nothing to sell yet.", "ink")
	end
end

local function drawOffers(view)
	local gems = player:GetAttribute("Gems") or 0
	window:Section("Vault")
	local maxed = view.vaultTier >= view.maxVaultTier
	window:Row({
		key = "Vault",
		title = ("Vault tier %d / %d"):format(view.vaultTier, view.maxVaultTier),
		detail = if maxed then "Your vault is as large as it gets." else "Each tier adds 25 item slots.",
		glyph = "pm_glyph_bag",
		value = if maxed then nil else tostring(view.vaultPrice),
		valueIcon = "pm_icon_gem",
		done = maxed,
		buttons = if maxed
			then nil
			else {
				{
					label = "UPGRADE",
					key = "Upgrade",
					enabled = gems >= view.vaultPrice,
					onPress = function()
						act("Vault upgraded.", "VaultUpgrade", nonce())
					end,
				},
			},
	})
	window:Row({
		key = "Respec",
		title = "Respec rebirth perks",
		detail = "Refunds every perk token you have spent.",
		glyph = "pm_glyph_person",
		value = tostring(view.respecGems),
		valueIcon = "pm_icon_gem",
		buttons = {
			{
				label = "RESPEC",
				key = "Respec",
				enabled = gems >= view.respecGems,
				onPress = function()
					window:Confirm(
						("Refund every rebirth perk for %d Gems?\n\nYour perks are reset and their tokens returned to spend again."):format(
							view.respecGems
						),
						"RESPEC",
						0,
						function()
							act("Perk tokens refunded.", "PerkRespec", nonce())
						end
					)
				end,
			},
		},
	})
	window:Section("Robux offers")
	window:Line("Every offer has a route you can earn in play instead.")
	for _, offer in view.offers do
		local available = offer.productId ~= 0
		window:Row({
			key = offer.id,
			title = offer.name,
			detail = "Earn it instead: " .. offer.earnable,
			glyph = "pm_glyph_diamond",
			buttons = {
				{
					label = if available then "BUY" else "SOON",
					key = "Buy",
					enabled = available,
					onPress = function()
						MarketplaceService:PromptProductPurchase(player, offer.productId)
					end,
				},
			},
		})
	end
end

local function drawCodes()
	window:Line("Codes come from Flintborn's group and social posts. Each one works once per player.")
	local box
	box = window:Input("Redeem a code", "Type a code…", function(code)
		box.Text = ""
		local ok, reason = invoke("RedeemCode", code)
		window:SetStatus(if ok then "Code redeemed!" else ("Code: " .. tostring(reason)))
	end)
end

function render()
	renderToken += 1
	local token = renderToken
	local shown = tab
	window:SetTab(shown)
	-- Fetch first, then clear and rebuild without yielding, so overlapping renders
	-- (a tab switch during a purchase) can't interleave and duplicate rows.
	local view = if shown == "Codes" then nil else invoke("ShopView")
	if token ~= renderToken then
		return
	end
	window:Begin()
	if shown == "Codes" then
		drawCodes()
	elseif type(view) ~= "table" then
		window:Line("Your data is still loading.", "ink")
	elseif shown == "Shop" then
		drawShop(view)
	elseif shown == "Sell" then
		drawSell(view)
	else
		drawOffers(view)
	end
	window:Finish()
end

local function close()
	ContextActionService:UnbindAction(CLOSE_ACTION)
	window:Close()
end

local function open()
	window:SetStatus("")
	window:Open(GuiService.SelectedObject ~= nil or UserInputService.GamepadEnabled)
	ContextActionService:BindAction(CLOSE_ACTION, function(_, state)
		if state == Enum.UserInputState.Begin then
			if window:IsConfirming() then
				window:HideConfirm()
			else
				close()
			end
		end
		return Enum.ContextActionResult.Sink
	end, false, Enum.KeyCode.ButtonB)
	render()
end

local function build()
	local playerGui = player:WaitForChild("PlayerGui")
	window = ListWindow.new(playerGui, {
		name = "FlintbornMarket",
		title = "MARKET",
		tabs = WalletController.TABS,
		onTab = function(id)
			tab = id
			window:SetStatus("")
			render()
		end,
		onClose = close,
	})
	window.screen:Watch()
	-- Outside the new lobby HUD (which has its own currency bar), a small wallet
	-- label stays on screen.
	if not HudMode.ReplacesLobby() then
		local gui = Instance.new("ScreenGui")
		gui.Name = "Wallet"
		gui.ResetOnSpawn = false
		gui.DisplayOrder = 2
		local label = Instance.new("TextLabel")
		label.AnchorPoint = Vector2.new(1, 0)
		label.Position = UDim2.new(1, -12, 0, 12)
		label.Size = UDim2.fromOffset(200, 28)
		label.BackgroundColor3 = Color3.fromRGB(28, 24, 20)
		label.BackgroundTransparency = 0.15
		label.TextColor3 = GOLD
		label.Font = Enum.Font.GothamBold
		label.TextSize = 15
		label.Parent = gui
		local corner = Instance.new("UICorner")
		corner.CornerRadius = UDim.new(0, 8)
		corner.Parent = label
		gui.Parent = playerGui
		wallet = label
	end
end

-- Opens or closes the window (keys, and the on-screen navigation bar).
function WalletController.Toggle()
	if window.screen:IsOpen() then
		close()
	else
		open()
	end
end

-- Opens the window on one tab ("Shop", "Sell", "Offers" or "Codes"), as the
-- lobby HUD's Shop tile does; pressing it again on that tab closes it.
function WalletController.Open(name: string)
	if window.screen:IsOpen() and tab == name then
		close()
		return
	end
	for _, candidate in WalletController.TABS do
		if candidate.id == name then
			tab = name
		end
	end
	if window.screen:IsOpen() then
		window:SetStatus("")
		render()
	else
		open()
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
end

return WalletController
