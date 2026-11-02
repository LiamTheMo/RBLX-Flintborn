-- Drives WalletController headlessly in the kit Market window (Hud/ListWindow,
-- docs/ui/ListWindows.md): the tabs (Buy, Sell, Offers, Codes), a purchase and
-- two sales through the quantity dialog (stepper, slider and live total; one
-- Sell button per row), the perk respec question and a code. Stock and offers
-- are the real ShopCatalog / OfferCatalog entries; sale quotes come from
-- EconomyRules.
--
--   python3 art/ui/capture/capture.py market_flow
--
-- Pages: 1 Buy, 2 Sell, 3 Offers, 4 Codes, 5 the Buy quantity dialog, 6 the
-- Sell quantity dialog, 7 forced states (hover, pressed, disabled buttons; a
-- hovered tab), 8 phone 844 × 390 (Sell), 9 the phone's Sell quantity dialog,
-- 10 the 667 × 375 phone's Buy quantity dialog.

for key, widths in table.clone(__textWidths or {}) do
	__textWidths["Enum." .. key] = __textWidths["Enum." .. key] or widths
end

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local UserInputService = game:GetService("UserInputService")
workspace:SetAttribute("FlintbornPlaceRole", "Lobby")
local folder = Instance.new("Folder")
folder.Name = "FlintbornRemotes"
folder.Parent = ReplicatedStorage
local player = Players.LocalPlayer
player:SetAttribute("Coins", 2450)
player:SetAttribute("Gems", 300)

local Shared = ReplicatedStorage.Shared
local ItemCatalog = require(Shared.Items.ItemCatalog)
local ShopCatalog = require(Shared.Economy.ShopCatalog)
local OfferCatalog = require(Shared.Economy.OfferCatalog)
local EconomyRules = require(Shared.Economy.EconomyRules)

local function nameOf(id: string): string
	local def = ItemCatalog.Get(id)
	return def and def.name or id
end

local stock = {}
for _, entry in ShopCatalog.Stock do
	table.insert(stock, {
		id = entry.id,
		catalogId = entry.catalogId,
		name = entry.title and ("Title: " .. entry.title) or nameOf(entry.catalogId),
		quantity = entry.quantity,
		price = entry.price,
		category = entry.category,
		note = entry.note,
		owned = entry.title == "Wanderer",
		-- As ShopService: what the 2,450 Coins cover, within the limit (the
		-- backpack is empty).
		maxQuantity = if entry.title == "Wanderer"
			then 0
			else math.min(if entry.title then 1 else EconomyRules.MAX_BUY_QUANTITY, 2450 // entry.price),
	})
end
local sellable = {}
for index, item in { { catalogId = "Flint", quantity = 6 }, { catalogId = "Redberry", quantity = 4 } } do
	local coins, warning = EconomyRules.Quote(item, nil)
	assert(coins, "a merchant buys " .. item.catalogId)
	table.insert(sellable, {
		source = "backpack",
		key = index,
		catalogId = item.catalogId,
		name = nameOf(item.catalogId),
		quantity = item.quantity,
		coins = coins,
		each = (EconomyRules.Quote(item, 1)),
		warning = warning,
	})
end
for _, entry in { { "IronBar", 34 }, { "Hide", 9 }, { "Wood", 32 } } do
	local each, warning = EconomyRules.Quote({ catalogId = entry[1], quantity = 1 }, 1)
	table.insert(sellable, {
		source = "vault",
		key = entry[1],
		catalogId = entry[1],
		name = nameOf(entry[1]),
		quantity = entry[2],
		each = each or 1,
		warning = warning,
	})
end
local offers = {}
for _, offer in OfferCatalog.Offers do
	table.insert(offers, { id = offer.id, name = offer.name, productId = offer.productId, earnable = offer.earnable })
end
-- One offer purchasable, so both button states show.
offers[4].productId = 1234
local view = {
	stock = stock,
	sellable = sellable,
	offers = offers,
	vaultTier = 1,
	vaultPrice = EconomyRules.VaultUpgradePrice(1),
	maxVaultTier = EconomyRules.MAX_VAULT_TIER,
	respecGems = EconomyRules.RESPEC_GEMS,
	maxBuy = EconomyRules.MAX_BUY_QUANTITY,
}

local calls = {}
for name, fn in
	{
		ShopView = function()
			return view
		end,
		ShopBuy = function(...)
			table.insert(calls, { "ShopBuy", ... })
			return true
		end,
		MerchantSell = function(...)
			table.insert(calls, { "MerchantSell", ... })
			return true
		end,
		VaultUpgrade = function()
			table.insert(calls, { "VaultUpgrade" })
			return true
		end,
		PerkRespec = function()
			table.insert(calls, { "PerkRespec" })
			return true
		end,
		RedeemCode = function(code)
			table.insert(calls, { "RedeemCode", code })
			return true
		end,
	}
do
	local remote = Instance.new("RemoteFunction")
	remote.Name = name
	remote.Parent = folder
	remote.InvokeServer = function(_, ...)
		return fn(...)
	end
end

local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local Kit = require(Client.Hud.Kit)
local ListWindow = require(Client.Hud.ListWindow)
local WalletController = require(Client.Controllers.WalletController)
WalletController.Start()
WalletController.Open("Shop")
local gui = player.PlayerGui:FindFirstChild("FlintbornMarket")
local function check(cond, msg)
	print((cond and "  ok " or "  FAIL ") .. msg)
	if not cond then
		__failed = true
	end
end
-- A named part anywhere under `root`, and a press on a kit control's hit.
local function find(root: Instance?, name: string): Instance?
	return root and root:FindFirstChild(name, true)
end
local function press(component: Instance?)
	local hit = component and component:FindFirstChild("Hit")
	assert(hit, "nothing to press")
	-- Past the kit's press debounce (time only passes for real here).
	local start = os.clock()
	while os.clock() - start < 0.16 do
	end
	hit.Activated:Fire()
end
-- The tab named `name` (row buttons share names with tabs: Buy, Sell).
local function tabNamed(name: string): Instance?
	for _, d in gui:GetDescendants() do
		if d.Name == name and d:GetAttribute("KitComponent") == "Tab" then
			return d
		end
	end
	return nil
end
local function dialog(): Instance?
	-- A closed dialog lingers until its close tween ends; the open one is enabled.
	for _, d in player.PlayerGui:GetChildren() do
		if d.Name == "KitDialog" and d.Enabled then
			return d
		end
	end
	return nil
end

check(gui and gui.Enabled, 'the market opens (Open("Shop") still opens it, on Buy)')
check(tabNamed("Buy") ~= nil and tabNamed("Shop") == nil, "the first tab reads Buy, not Shop")
check(tabNamed("Buy"):GetAttribute("KitState") == "selected", "and is the open tab")
check(find(gui, "StoneAxe") ~= nil, "stock is listed")
check(find(find(gui, "TitleWanderer"), "Done") ~= nil, "an owned title shows a tick")
check(find(find(gui, "TitleEmberborn"), "Buy"):GetAttribute("KitState") == "disabled", "too dear to buy: Buy is off")
check(find(gui, "Coins") and find(gui, "Coins"):GetAttribute("KitValue") == 2450, "the header shows the wallet")
local market = WalletController.window
press(find(find(gui, "StoneAxe"), "Buy"))
check(dialog() ~= nil and #calls == 0, "Buy asks how many first")
local question = market.confirm
local function total(): string
	local label = find(dialog(), "Total")
	return label and label.Text or ""
end
check(question.stepper ~= nil and question.slider ~= nil, "the dialog has a stepper and a slider")
check(question.Quantity() == 1 and total() == "150", "it starts at one, total 150")
press(find(dialog(), "Plus"))
press(find(dialog(), "Plus"))
check(question.Quantity() == 3 and question.slider.value == 3, "+ twice: three, the slider follows")
check(total() == "450", "the total follows live (3 × 150)")
question.slider:_change(7)
check(question.Quantity() == 7 and question.stepper.value == 7, "dragging the slider moves the stepper")
check(total() == "1,050", "and the total (7 × 150)")
press(find(dialog(), "All"))
check(question.Quantity() == 16, "Max stops at what the Coins cover (2,450 // 150)")
question.SetQuantity(999)
check(question.Quantity() == 16, "nothing past the maximum")
question.SetQuantity(3)
press(find(dialog(), "Confirm"))
check(
	calls[1] and calls[1][1] == "ShopBuy" and calls[1][2] == "StoneAxe" and calls[1][4] == 3,
	"confirming buys the stock id, three of them"
)
press(tabNamed("Sell"))
check(find(gui, "vaultIronBar") ~= nil, "Sell lists vault materials")
local oneButton = true
for _, row in { find(gui, "vaultIronBar"), find(gui, "backpack1"), find(gui, "vaultWood") } do
	local count = 0
	for _, d in row:GetDescendants() do
		if d:GetAttribute("KitComponent") == "Button" then
			count += 1
			oneButton = oneButton and d.Name == "Sell"
		end
	end
	oneButton = oneButton and count == 1
end
check(oneButton, "every sale row has one Sell button (no Sell 10 / Sell All)")
press(find(find(gui, "vaultIronBar"), "Sell"))
question = market.confirm
check(dialog() ~= nil and question.stepper.max == 34, "Sell asks how many, up to the 34 in the vault")
press(find(dialog(), "All"))
check(question.Quantity() == 34 and total() == "340", "Max: all 34 bars, 340 Coins")
press(find(dialog(), "Confirm"))
local sale = calls[#calls]
check(sale[1] == "MerchantSell" and sale[2] == "vault" and sale[3] == "IronBar" and sale[4] == 34, "sells 34")
press(find(find(gui, "backpack1"), "Sell"))
question = market.confirm
press(find(dialog(), "Plus"))
press(find(dialog(), "Confirm"))
sale = calls[#calls]
check(
	sale[1] == "MerchantSell" and sale[2] == "backpack" and sale[3] == 1 and sale[4] == 2 and sale[6] == "Flint",
	"a backpack sale sends the amount and the slot's item"
)
press(tabNamed("Offers"))
press(find(find(gui, "Respec"), "Respec"))
check(dialog() ~= nil, "a respec asks first")
press(find(dialog(), "Confirm"))
check(calls[#calls][1] == "PerkRespec", "confirming respecs")
press(tabNamed("Codes"))
local box = find(gui, "Box") :: TextBox
box.Text = "WELCOME"
box.FocusLost:Fire(true)
check(calls[#calls][1] == "RedeemCode" and calls[#calls][2] == "WELCOME", "a code is redeemed with Enter")
box.Text = "FLINT"
press(find(gui, "Submit"))
check(calls[#calls][2] == "FLINT", "Redeem submits the typed code")
check(Kit.Modal.Top() ~= nil, "the window is on the modal stack")
Kit.Modal.Back()
check(not gui:GetAttribute("KitState") or gui:GetAttribute("KitState") == "closed", "Escape / B closes it")
print(__failed and "FLOW FAILED" or "FLOW OK")

local W, H = 1672, 941
local BG = { background = "art/reference/ui/lobby/01_hud.png" }
local function place(width: number, height: number, top: number)
	local k, centre = Kit.Scale.WindowFit(width, height, top, ListWindow.SIZE[1], ListWindow.SIZE[2], 1)
	gui.Holder.Fit.Scale = k
	gui.Holder.Position = UDim2.fromOffset(centre.X, centre.Y)
	return k
end
WalletController.Open("Buy")
place(W, H, 58)
gui.Holder.Fit.Scale = 1
gui.Holder.Position = UDim2.fromOffset(W / 2, H / 2 + 20)
for _, name in { "Buy", "Sell", "Offers", "Codes" } do
	press(tabNamed(name))
	__dump(player.PlayerGui, W, H, BG)
end
local function dumpDialog(label: string)
	local d = dialog()
	d.Holder.Fit.Scale = 1
	d.Holder.Position = UDim2.fromOffset(W / 2, H / 2 + 20)
	__dump(player.PlayerGui, W, H, BG)
	press(find(d, "Cancel"))
	check(dialog() == nil, label .. ": Cancel closes it without a request")
end
press(tabNamed("Buy"))
press(find(find(gui, "RedberryPack"), "Buy"))
market.confirm.SetQuantity(4)
dumpDialog("the Buy dialog")
press(tabNamed("Sell"))
press(find(find(gui, "vaultWood"), "Sell"))
market.confirm.SetQuantity(12)
dumpDialog("the Sell dialog")
press(tabNamed("Buy"))
-- Forced states, as verifiers set them.
find(find(gui, "Bandage"), "Buy"):SetAttribute("DebugState", "hover")
find(find(gui, "RedberryPack"), "Buy"):SetAttribute("DebugState", "pressed")
find(find(gui, "SweetberryPack"), "Buy"):SetAttribute("DebugState", "busy")
tabNamed("Offers"):SetAttribute("DebugState", "hover")
__dump(player.PlayerGui, W, H, BG)
for _, part in player.PlayerGui:GetDescendants() do
	if part:GetAttribute("DebugState") then
		part:SetAttribute("DebugState", "")
	end
end
-- Leak check counts: the PlayerGui's instances, and the live connections on
-- every instance still in the game (a destroyed one drops out with its
-- connections, as in Roblox) plus those on the shared Core.Signal objects.
local leakCounts
do
	local SignalMeta = getmetatable(Instance.new("Frame"):GetPropertyChangedSignal("Name"))
	local CoreSignal = require(game:GetService("ReplicatedStorage").Shared.Core.Signal)
	local coreLive = setmetatable({}, { __mode = "k" })
	local connect = CoreSignal.Connect
	CoreSignal.Connect = function(signal, fn)
		local connection = connect(signal, fn)
		coreLive[connection] = true
		return connection
	end
	local ROOTS = {
		"Players",
		"UserInputService",
		"GuiService",
		"RunService",
		"Lighting",
		"ReplicatedStorage",
		"StarterPlayer",
		"SoundService",
		"ContextActionService",
		"SocialService",
		"TweenService",
	}
	function leakCounts(): (number, number)
		local count = 0
		local seen = {}
		local function signals(map)
			for _, value in map or {} do
				if type(value) == "table" and getmetatable(value) == SignalMeta then
					count += #value.handlers
				end
			end
		end
		local function visit(instance)
			if instance == nil or seen[instance] then
				return
			end
			seen[instance] = true
			signals(rawget(instance, "__props"))
			signals(rawget(instance, "__changed"))
			signals(rawget(instance, "__attrChanged"))
			for _, child in rawget(instance, "__children") or {} do
				visit(child)
			end
		end
		visit(game)
		visit(workspace)
		visit(workspace.CurrentCamera)
		for _, name in ROOTS do
			visit(game:GetService(name))
		end
		local player = game:GetService("Players").LocalPlayer
		visit(player)
		for connection in coreLive do
			if connection.Connected then
				count += 1
			end
		end
		return #player.PlayerGui:GetDescendants(), count
	end
end

-- ×20 open / close: no instances and no connections left behind (the Market window).
WalletController.Toggle()
WalletController.Toggle()
local instancesBefore, connectionsBefore = leakCounts()
for _ = 1, 20 do
	WalletController.Toggle()
	WalletController.Toggle()
end
local instancesAfter, connectionsAfter = leakCounts()
check(
	instancesAfter == instancesBefore,
	("open/close ×20 leaves the instances as they were (%d → %d)"):format(instancesBefore, instancesAfter)
)
check(
	connectionsAfter == connectionsBefore,
	("open/close ×20 leaves the connections as they were (%d → %d)"):format(connectionsBefore, connectionsAfter)
)

-- A phone held sideways: touch only, the window fills the height.
workspace.CurrentCamera.ViewportSize = Vector2.new(844, 390)
UserInputService.TouchEnabled = true
UserInputService.KeyboardEnabled = false
UserInputService.MouseEnabled = false
WalletController.Open("Sell")
local k = place(844, 390, 58)
print(("market phone: window scale %.3f"):format(k))
__dump(player.PlayerGui, 844, 390)
-- The quantity dialogs on phones, fitted as in game; their text is at least 9
-- screen px and the stepper's and slider's 44 px touch pads do not overlap.
local function phoneDialog(w: number, h: number, tag: string)
	workspace.CurrentCamera.ViewportSize = Vector2.new(w, h)
	local handle = market.confirm
	handle.screen:Fit(w, h, 58, 1)
	local scale = handle.screen.scale.Scale
	local smallest = math.huge
	for _, item in dialog():GetDescendants() do
		if item:IsA("TextLabel") and item:GetAttribute("KitTextRole") and item.Text ~= "" and item.Visible then
			smallest = math.min(smallest, item.TextSize * scale)
		end
	end
	print(("%s: dialog scale %.3f, smallest text %.1f screen px"):format(tag, scale, smallest))
	check(smallest >= 9 - 0.05, tag .. ": text at least 9 screen px")
	local stepper, slider = handle.stepper.root, handle.slider.root
	local function pad(part): (number, number)
		local top = part.Position.Y.Offset
		local hgt = part.Size.Y.Offset
		local grow = math.max(0, (44 / scale - hgt) / 2)
		return top - grow, top + hgt + grow
	end
	local _, stepperBottom = pad(stepper)
	local sliderTop = pad(slider)
	check(stepperBottom <= sliderTop + 0.5, tag .. ": the stepper's and slider's touch pads do not overlap")
	__dump(player.PlayerGui, w, h)
end
press(find(find(gui, "vaultIronBar"), "Sell"))
market.confirm.SetQuantity(20)
phoneDialog(844, 390, "market phone 844x390 Sell")
press(find(dialog(), "Cancel"))
WalletController.Open("Buy")
place(667, 375, 58)
press(find(find(gui, "SweetberryPack"), "Buy"))
market.confirm.SetQuantity(5)
phoneDialog(667, 375, "market phone 667x375 Buy")
press(find(dialog(), "Cancel"))
print(__failed and "FLOW FAILED" or "FLOW OK")
if __failed then
	error("market flow failed")
end
