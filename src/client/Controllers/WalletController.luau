-- Wallet, shops, merchant, offers and codes (GDD §10, §25.4.1, §36) in the
-- kit Market window (Hud/ListWindow, docs/ui/ListWindows.md). The lobby shows
-- Coins and Gems at all times (the window's header too); the Market tile opens
-- the window on a category tab: Buy (the shop's stock), Sell, Offers (vault
-- upgrades, perk respec and Robux offers, each with its earnable equivalent next
-- to it) and Codes. Every Buy row has one Buy button; it opens a quantity
-- dialog (a stepper and a slider kept in step, the total live) clamped to what
-- the player can afford and carry (the server's maxQuantity). Every Sell row
-- carries its own slider and stepper (1 to what it holds, the whole stack by
-- default) with the total live beside its one Sell button, which sells that
-- amount at once (a Forge reagent asks first). The server checks every amount
-- again. Spending Gems or tokens asks first in a confirm dialog. Quests live in
-- the Journal. Lobby place only.

local GuiService = game:GetService("GuiService")
local HttpService = game:GetService("HttpService")
local MarketplaceService = game:GetService("MarketplaceService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local HudModel = require(ReplicatedStorage.Shared.UI.HudModel)
local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Remotes = require(ReplicatedStorage.Shared.Net.Remotes)
local HudMode = require(script.Parent.Parent.Hud.HudMode)
local Kit = require(script.Parent.Parent.Hud.Kit)
local ListWindow = require(script.Parent.Parent.Hud.ListWindow)
local Reasons = require(script.Parent.Parent.Ui.Reasons)

local WalletController = {}

WalletController.TABS = {
	{ id = "Buy", label = "Buy", icon = "market" },
	{ id = "Sell", label = "Sell", icon = "coin" },
	{ id = "Offers", label = "Offers", icon = "gem" },
	{ id = "Codes", label = "Codes", icon = "gift" },
}

local player = Players.LocalPlayer
local window = nil
local wallet = nil
local tab = "Buy"
-- Bumped by every render; a render that yielded and is no longer the latest drops.
local renderToken = 0

-- Remotes.Invoke with a refusal's reason as player-facing text.
local function invoke(name: string, ...)
	local success, reason = Remotes.Invoke(name, ...)
	return success, if success then reason else Reasons.Text(reason)
end

local function nonce(): string
	return HttpService:GenerateGUID(false)
end

local render

-- Runs a request from a button, then shows its outcome and redraws.
local function act(success: string, name: string, ...)
	local ok, result = invoke(name, ...)
	window:SetStatus(if ok then success else ("Not done: " .. tostring(result)), if ok then "good" else "warn")
	render()
end

local function updateWallet()
	local coins, gems = player:GetAttribute("Coins") or 0, player:GetAttribute("Gems") or 0
	if wallet then
		wallet.coins:SetValue(coins)
		wallet.gems:SetValue(gems)
	end
	if window then
		window:SetCurrencies(coins, gems)
	end
end

-- Asks how many packs of shop entry `entry` (at most `max`) and buys them.
local function buyDialog(entry, max: number)
	local pack = entry.quantity or 1
	window:Quantity({
		title = "Buy " .. entry.name .. "?",
		itemId = entry.catalogId,
		glyph = "market",
		name = entry.name .. (if pack > 1 then (" ×" .. pack) else ""),
		detail = ("%s Coins each%s. Goes to your lobby backpack."):format(
			HudModel.Thousands(entry.price),
			if pack > 1 then " pack" else ""
		),
		max = max,
		each = entry.price,
		currency = "coins",
		confirmLabel = "Buy",
		onConfirm = function(quantity)
			local what = if pack > 1 or quantity > 1 then (" ×" .. pack * quantity) else ""
			act(("Bought %s%s."):format(entry.name, what), "ShopBuy", entry.id, nonce(), quantity)
		end,
	})
end

-- How many each Sell row is set to sell, by row key, while the Sell tab stays
-- open: {catalogId, quantity}. A redraw keeps a row's choice (within what is
-- left); a sale resets its own row to everything left.
local chosen = {}
-- A sale in flight: further Sell presses wait for it.
local selling = false

local function sellKey(entry): string
	return entry.source .. tostring(entry.key)
end

-- Sells `quantity` of sellable `entry` at once, then shows the outcome and
-- redraws from the server's view. `button` shows busy meanwhile.
local function sell(entry, quantity: number, button)
	if selling then
		return
	end
	selling = true
	if button then
		button:SetBusy(true)
	end
	-- A backpack sale names the slot's item, so a slot that changed meanwhile
	-- sells nothing (the server checks).
	local ok, result = invoke(
		"MerchantSell",
		entry.source,
		entry.key,
		quantity,
		nonce(),
		if entry.source == "backpack" then entry.catalogId else nil
	)
	selling = false
	chosen[sellKey(entry)] = nil
	window:SetStatus(
		if ok then ("Sold %s ×%d."):format(entry.name, quantity) else ("Not done: " .. tostring(result)),
		if ok then "good" else "warn"
	)
	render()
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
			-- The most one purchase can buy: the server's figure (Coins, backpack
			-- room, its limit), never more than the Coins shown now cover.
			local afford = math.floor(coins / entry.price)
			local max = math.min(entry.maxQuantity or afford, afford, view.maxBuy or afford)
			local detail = entry.note
			if not entry.owned and afford >= 1 and max < 1 then
				detail = (if detail then detail .. " " else "") .. "No room in your lobby backpack."
			end
			window:Row({
				key = entry.id,
				title = entry.name .. (if (entry.quantity or 1) > 1 then (" ×" .. entry.quantity) else ""),
				detail = detail,
				icon = entry.catalogId,
				glyph = if entry.catalogId then nil elseif category == "Titles" then "crown" else "market",
				value = if entry.owned then nil else HudModel.Thousands(entry.price),
				valueIcon = "coin",
				done = entry.owned,
				buttons = if entry.owned
					then nil
					else {
						{
							label = "Buy",
							key = "Buy",
							enabled = max >= 1,
							onPress = function()
								if entry.catalogId then
									buyDialog(entry, max)
									return
								end
								-- A title is bought once: a plain question.
								window:Confirm(
									("Buy %s for %s Coins?"):format(entry.name, HudModel.Thousands(entry.price)),
									"Buy",
									0,
									function()
										act("Bought " .. entry.name .. ".", "ShopBuy", entry.id, nonce(), 1)
									end,
									{ title = "Buy " .. entry.name .. "?" }
								)
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
		-- Each row picks its own amount (a slider and a stepper, from 1 to the
		-- whole stack; whole by default, as one press sold before) and shows the
		-- total by its one Sell button, which sells that amount at once.
		local key = sellKey(entry)
		local owned = entry.quantity or 1
		local each = entry.each or entry.coins or 0
		local kept = chosen[key]
		local value = if kept and kept.catalogId == entry.catalogId then math.min(kept.quantity, owned) else owned
		local detail = if owned > 1
			then ("%s Coins each · %d %s"):format(
				HudModel.Thousands(each),
				owned,
				if entry.source == "vault" then "in your vault" else "in your backpack"
			)
			else nil
		if entry.warning then
			detail = (if detail then detail .. ". " else "") .. entry.warning
		end
		window:QuantityRow({
			key = key,
			title = entry.name,
			detail = detail,
			icon = entry.catalogId,
			glyph = "coin",
			max = owned,
			value = value,
			each = each,
			currency = "coins",
			onChange = function(quantity)
				chosen[key] = { catalogId = entry.catalogId, quantity = quantity }
			end,
			action = {
				label = "Sell",
				key = "Sell",
				onPress = function(quantity, button)
					if selling then
						return
					end
					if entry.warning == nil then
						sell(entry, quantity, button)
						return
					end
					-- Something a Forge recipe needs (the server's warning): ask first.
					window:Confirm(
						("Sell %s ×%d for %s Coins? %s"):format(
							entry.name,
							quantity,
							HudModel.Thousands(each * quantity),
							entry.warning
						),
						"Sell",
						0,
						function()
							sell(entry, quantity, button)
						end,
						{ title = "Sell " .. entry.name .. "?" }
					)
				end,
			},
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
		glyph = "chest",
		value = if maxed then nil else tostring(view.vaultPrice),
		valueIcon = "gem",
		done = maxed,
		buttons = if maxed
			then nil
			else {
				{
					label = "Upgrade",
					key = "Upgrade",
					enabled = gems >= view.vaultPrice,
					onPress = function()
						window:Confirm(
							("Upgrade your vault to tier %d for %d Gems? It adds 25 item slots."):format(
								view.vaultTier + 1,
								view.vaultPrice
							),
							"Upgrade",
							0,
							function()
								act("Vault upgraded.", "VaultUpgrade", nonce())
							end,
							{ title = "Upgrade the vault?" }
						)
					end,
				},
			},
	})
	window:Row({
		key = "Respec",
		title = "Respec rebirth perks",
		detail = "Refunds every perk token you have spent.",
		glyph = "star",
		value = tostring(view.respecGems),
		valueIcon = "gem",
		buttons = {
			{
				label = "Respec",
				key = "Respec",
				enabled = gems >= view.respecGems,
				onPress = function()
					window:Confirm(
						("Refund every rebirth perk for %d Gems? Your perks are reset and their tokens returned to spend again."):format(
							view.respecGems
						),
						"Respec",
						0,
						function()
							act("Perk tokens refunded.", "PerkRespec", nonce())
						end,
						{ title = "Respec your perks?" }
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
			glyph = "gem",
			buttons = {
				{
					label = if available then "Buy" else "Soon",
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
		window:SetStatus(if ok then "Code redeemed!" else ("Code: " .. tostring(reason)), if ok then "good" else "warn")
	end, false, "Redeem")
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
	elseif shown == "Buy" then
		drawShop(view)
	elseif shown == "Sell" then
		drawSell(view)
	else
		drawOffers(view)
	end
	window:Finish()
end

-- Escape and gamepad B close the question first, then the window (Kit.Modal).
local function close()
	window:Close()
end

local function open()
	table.clear(chosen)
	window:SetStatus("")
	window:Open(GuiService.SelectedObject ~= nil or UserInputService.GamepadEnabled)
	render()
end

local function build()
	local playerGui = player:WaitForChild("PlayerGui")
	window = ListWindow.new(playerGui, {
		name = "FlintbornMarket",
		title = "Market",
		icon = "market",
		tabs = WalletController.TABS,
		onTab = function(id)
			tab = id
			table.clear(chosen)
			window:SetStatus("")
			render()
		end,
		onClose = close,
	})
	-- For flows and verifiers (the Market window and its open question).
	WalletController.window = window
	-- Outside the new lobby HUD (which has its own currency pills), the kit's
	-- Coins and Gems pills stay on screen at the top right.
	if not HudMode.ReplacesLobby() then
		local gui = Kit.Core.Make("ScreenGui", {
			Name = "Wallet",
			DisplayOrder = 2,
			IgnoreGuiInset = true,
			ResetOnSpawn = false,
			ZIndexBehavior = Enum.ZIndexBehavior.Sibling,
		}, playerGui)
		local bar = Kit.Core.Make("Frame", {
			Name = "Pills",
			AnchorPoint = Vector2.new(1, 0),
			BackgroundTransparency = 1,
			Position = UDim2.new(1, -12, 0, Kit.Scale.TopInset(gui) + 8),
			Size = UDim2.fromOffset(276, 46),
		}, gui)
		Kit.Core.Make("UIScale", { Scale = 0.8 }, bar)
		wallet = {
			coins = Kit.CurrencyPill.new(bar, { name = "Coins", rect = { 0, 0, 140, 46 }, currency = "coins" }),
			gems = Kit.CurrencyPill.new(bar, { name = "Gems", rect = { 148, 0, 128, 46 }, currency = "gems" }),
		}
	end
end

-- Opens or closes the window (keys, and the HUD's menu tiles).
function WalletController.Toggle()
	if window.screen:IsOpen() then
		close()
	else
		open()
	end
end

-- Opens the window on one tab ("Buy", "Sell", "Offers" or "Codes"; "Shop", the
-- lobby HUD tile's id, opens Buy), as the lobby HUD's Market tile does; pressing
-- it again on that tab closes it.
function WalletController.Open(name: string)
	if name == "Shop" then
		name = "Buy"
	end
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
		table.clear(chosen)
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
