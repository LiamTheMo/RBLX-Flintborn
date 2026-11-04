-- Drives WalletController headlessly in the kit Market window (Hud/ListWindow,
-- docs/ui/ListWindows.md): the tabs (Buy, Sell, Offers, Codes), a purchase
-- through the quantity dialog (stepper, slider and live total), sales from the
-- Sell rows' own quantity (slider and stepper in the row, the total live by the
-- one Sell button, no dialog; a Forge reagent asks first), touch on a slider
-- inside the scrolling list, the perk respec question and a code. Stock and
-- offers are the real ShopCatalog / OfferCatalog entries; sale quotes come from
-- EconomyRules.
--
--   python3 art/ui/capture/capture.py market_flow
--
-- Pages: 1 Buy, 2 Sell (one row set to part of its stack), 3 Offers, 4 Codes,
-- 5 the Buy quantity dialog, 6 the Forge reagent's question on Sell, 7 forced
-- states (hover, pressed, busy buttons; a hovered tab), 8 phone 844 × 390
-- (Sell), 9 phone 667 × 375 (Sell), 10 the same scrolled to the vault, 11 the
-- 667 × 375 phone's Buy quantity dialog. The phone Sell pages print their
-- smallest text and check that no two touch pads overlap.

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
local Rules = game:GetService("ServerScriptService").Server.Rules
local ItemCatalog = require(Shared.Items.ItemCatalog)
local ShopCatalog = require(Shared.Economy.ShopCatalog)
local OfferCatalog = require(Rules.Economy.OfferCatalog)
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
-- What ShopView sends for the Sell tab: backpack slots (two stacks and a
-- unique Stone Axe), then vault materials (an Ancient Ember, which a Forge
-- recipe needs, carries the server's warning). Rebuilt for the pages after the
-- flow's sales took from it.
local sellable = {}
local function stockSellable()
	table.clear(sellable)
	for index, item in
		{
			{ catalogId = "Flint", quantity = 6 },
			{ catalogId = "Redberry", quantity = 4 },
			{ catalogId = "StoneAxe", instanceId = "axe-1" },
		}
	do
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
	for _, entry in { { "AncientEmber", 7 }, { "Hide", 9 }, { "IronBar", 34 }, { "Wood", 32 } } do
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
end
stockSellable()
assert(sellable[4].warning ~= nil, "a Forge reagent carries the server's warning")
-- As the server: a sale takes from the stack (a backpack slot sold out is
-- removed and the later slots move up a key).
local function takeSold(source, key, quantity)
	for index, entry in sellable do
		if entry.source == source and entry.key == key then
			local left = (entry.quantity or 1) - quantity
			if left > 0 then
				entry.quantity = left
			else
				table.remove(sellable, index)
				if source == "backpack" then
					for _, later in sellable do
						if later.source == "backpack" and later.key > key then
							later.key -= 1
						end
					end
				end
			end
			return
		end
	end
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
local duringSale = nil
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
			-- While the request is out, the flow may press again (a double press).
			if duringSale then
				local again = duringSale
				duringSale = nil
				again()
			end
			local source, key, quantity = ...
			takeSold(source, key, quantity)
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
for _, key in { "vaultIronBar", "backpack1", "backpack3", "vaultWood" } do
	local count = 0
	for _, d in find(gui, key):GetDescendants() do
		if d:GetAttribute("KitComponent") == "Button" then
			count += 1
			oneButton = oneButton and d.Name == "Sell"
		end
	end
	oneButton = oneButton and count == 1
end
check(oneButton, "every sale row has one Sell button (no Sell 10 / Sell All)")
-- Each row's own quantity: market.quantities holds the rows' handles.
local rows = market.quantities
local function totalOf(key: string): string
	local label = find(find(gui, key), "Total")
	return label and label.Text or ""
end
local flint = rows.backpack1
check(flint and flint.slider ~= nil and flint.stepper ~= nil, "a stack carries its own slider and stepper")
check(
	flint.Quantity() == 6 and flint.slider.value == 6 and flint.stepper.value == 6,
	"it starts at the whole stack (6), as one press sold before"
)
check(totalOf("backpack1") == "18", "the total by Sell reads 18 (6 × 3)")
check(
	rows.backpack3.slider == nil and find(find(gui, "backpack3"), "Quantity") == nil,
	"a unique item (one) has no control"
)
check(totalOf("backpack3") == tostring(sellable[3].each), "just its price by Sell")
local before = #calls
press(find(find(gui, "backpack1"), "Minus"))
check(flint.Quantity() == 5 and flint.slider.value == 5, "−: five, the slider follows")
check(totalOf("backpack1") == "15", "the total follows live (5 × 3)")
flint.slider:_change(2)
check(flint.stepper.value == 2 and flint.Quantity() == 2, "dragging the slider moves the stepper")
check(totalOf("backpack1") == "6", "and the total (2 × 3)")
check(dialog() == nil and #calls == before, "choosing asks nothing and sends nothing")
-- Pressed again while the sale is out (the same button, then another row's):
-- nothing more is sent.
local flintSell = find(find(gui, "backpack1"), "Sell")
local busyDuring = nil
duringSale = function()
	busyDuring = flintSell:GetAttribute("KitState")
	press(flintSell)
	press(find(find(gui, "vaultHide"), "Sell"))
end
press(flintSell)
check(dialog() == nil, "Sell opens no dialog")
check(#calls == before + 1, "one press sends one sale, even pressed again meanwhile")
check(busyDuring == "busy", "the Sell button is busy while the sale is out")
local sale = calls[#calls]
check(
	sale[1] == "MerchantSell" and sale[2] == "backpack" and sale[3] == 1 and sale[4] == 2 and sale[6] == "Flint",
	"Sell sends the chosen two, with the slot's item"
)
flint = rows.backpack1
check(
	flint ~= nil and flint.Quantity() == 4 and totalOf("backpack1") == "12",
	"the list refreshes: the row resets to the 4 left (12)"
)
check(market.status.root.Text == "Sold Flint ×2.", "the status says what was sold")
rows.vaultWood.SetQuantity(12)
press(find(find(gui, "vaultIronBar"), "Sell"))
sale = calls[#calls]
check(
	sale[1] == "MerchantSell" and sale[2] == "vault" and sale[3] == "IronBar" and sale[4] == 34,
	"Sell at the default sells the whole stack (34 bars)"
)
check(find(gui, "vaultIronBar") == nil, "a sold-out row leaves the list")
check(rows.vaultWood.Quantity() == 12 and totalOf("vaultWood") == "24", "another row keeps its choice (12, 24)")
-- A Forge reagent (the server's warning) still asks first.
for _ = 1, 4 do
	press(find(find(gui, "vaultAncientEmber"), "Minus"))
end
before = #calls
press(find(find(gui, "vaultAncientEmber"), "Sell"))
check(dialog() ~= nil and #calls == before, "a Forge reagent asks before selling")
local asked = find(find(dialog(), "Body"), "Text")
check(
	asked ~= nil and asked.Text:find("Forge") ~= nil and asked.Text:find("×3") ~= nil,
	"the question names the warning and the three"
)
press(find(dialog(), "Confirm"))
sale = calls[#calls]
check(
	#calls == before + 1 and sale[2] == "vault" and sale[3] == "AncientEmber" and sale[4] == 3,
	"confirming sells the three chosen"
)
-- Touch on a slider inside the scrolling list (track placed by hand: the
-- harness measures nothing).
local wood = rows.vaultWood
local list = market.list
local slider = wood.slider
slider.track.AbsolutePosition = Vector2.new(100, 300)
slider.track.AbsoluteSize = Vector2.new(slider.trackW, 14)
local function touch(x: number, y: number)
	return { UserInputType = Enum.UserInputType.Touch, KeyCode = Enum.KeyCode.Unknown, Position = Vector3.new(x, y, 0) }
end
local finger = touch(200, 307)
slider.hit.InputBegan:Fire(finger)
finger.Position = Vector3.new(203, 345, 0)
UserInputService.InputChanged:Fire(finger, true)
check(
	wood.Quantity() == 12 and list.ScrollingEnabled,
	"a swipe up or down over a slider scrolls the list, the amount stays"
)
UserInputService.InputEnded:Fire(finger, true)
check(wood.Quantity() == 12, "and lifting the finger leaves it too")
list.CanvasPosition = Vector2.new(0, 40)
finger = touch(200, 307)
slider.hit.InputBegan:Fire(finger)
-- The list starts to follow the finger before the drag shows its direction.
list.CanvasPosition = Vector2.new(0, 46)
finger.Position = Vector3.new(250, 309, 0)
UserInputService.InputChanged:Fire(finger, true)
check(
	not list.ScrollingEnabled and list.CanvasPosition.Y == 40,
	"a sideways drag takes the slider: the list stops, back where it was"
)
local dragged = wood.Quantity()
check(
	dragged ~= 12 and wood.stepper.value == dragged and totalOf("vaultWood") == tostring(dragged * 2),
	("the amount follows the finger (%d), the stepper and total too"):format(dragged)
)
UserInputService.InputEnded:Fire(finger, true)
check(list.ScrollingEnabled, "lifting the finger lets the list scroll again")
finger = touch(100 + slider.trackW, 307)
slider.hit.InputBegan:Fire(finger)
UserInputService.InputEnded:Fire(finger, true)
check(wood.Quantity() == 32, "a tap sets the amount where it lands (the end: all 32)")
list.CanvasPosition = Vector2.new(0, 0)
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
-- The pages start from the full stock again (the flow's sales took from it).
stockSellable()
for _, name in { "Buy", "Sell", "Offers", "Codes" } do
	press(tabNamed(name))
	if name == "Sell" then
		-- One row set to part of its stack; the others at their whole stack.
		market.quantities.backpack1.SetQuantity(2)
	end
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
market.quantities.vaultAncientEmber.SetQuantity(3)
local sales = #calls
press(find(find(gui, "vaultAncientEmber"), "Sell"))
dumpDialog("the Forge reagent's question")
check(#calls == sales, "the Forge reagent's question: nothing sold on Cancel")
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

-- ×20 open / close: no instances and no connections left behind (the Market
-- window, on Buy and on Sell with its sliders and steppers).
for _, name in { "Buy", "Sell" } do
	press(tabNamed(name))
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
		("%s: open/close ×20 leaves the instances as they were (%d → %d)"):format(
			name,
			instancesBefore,
			instancesAfter
		)
	)
	check(
		connectionsAfter == connectionsBefore,
		("%s: open/close ×20 leaves the connections as they were (%d → %d)"):format(
			name,
			connectionsBefore,
			connectionsAfter
		)
	)
end

-- A phone held sideways: touch only, the window fills the height.
workspace.CurrentCamera.ViewportSize = Vector2.new(844, 390)
UserInputService.TouchEnabled = true
UserInputService.KeyboardEnabled = false
UserInputService.MouseEnabled = false
stockSellable()
-- The leak loop left the window open on Sell: close it, then open it drawn
-- for the phone.
if market:IsOpen() then
	WalletController.Toggle()
end
WalletController.Open("Sell")
market.quantities.backpack1.SetQuantity(2)
-- The Sell list on a phone at window scale `k`: no text under 9 screen px or
-- cut short, and no two controls' touch pads (44 screen px: Interact's growth,
-- the stepper's − and + and the slider's band) overlap, in a row or across rows.
local function phoneSell(k: number, tag: string)
	local smallest, cut, which = math.huge, nil, nil
	for _, item in market.list:GetDescendants() do
		local role = item:IsA("TextLabel") and item:GetAttribute("KitTextRole")
		if role and item.Text ~= "" and item.Visible then
			local size = item.TextSize
			if not item.TextWrapped then
				-- Measured at the unboosted size (Width boosts it again).
				local need = Kit.Text.Width(item.Text, role, size / Kit.Core.TextBoost(role, size))
				local room = item.Size.X.Offset
				if need > room + 0.5 then
					if item.TextScaled then
						size *= room / need
					else
						cut = cut or item.Text
					end
				end
			end
			if size * k < smallest then
				smallest, which = size * k, item.Name .. " '" .. item.Text .. "'"
			end
		end
	end
	print(("%s: window scale %.3f, smallest text %.1f screen px (%s)"):format(tag, k, smallest, tostring(which)))
	check(smallest >= 9 - 0.05, tag .. ": text at least 9 screen px")
	check(cut == nil, tag .. ": no text cut short" .. (if cut then (" (" .. cut .. ")") else ""))
	local need = 44 / k
	local rows = {}
	for _, child in market.list:GetChildren() do
		if child:IsA("GuiObject") then
			table.insert(rows, child)
		end
	end
	table.sort(rows, function(a, b)
		return a.LayoutOrder < b.LayoutOrder
	end)
	local pads, y = {}, 2
	for _, row in rows do
		local visual = row:FindFirstChild("Visual")
		local content = visual and visual:FindFirstChild("Content")
		for _, part in if row:GetAttribute("KitComponent") == "Panel" and content then content:GetChildren() else {} do
			local kind = part:GetAttribute("KitComponent")
			if kind == "Button" or kind == "Stepper" or kind == "Slider" then
				local px, py = part.Position.X.Offset, y + part.Position.Y.Offset
				local pw, ph = part.Size.X.Offset, part.Size.Y.Offset
				-- The slider's band reaches half a knob (31 px) past the track's ends.
				local sx = if kind == "Slider" then 15.5 else math.max(0, (need - math.min(pw, ph)) / 2)
				local sy = math.max(0, (need - (if kind == "Slider" then ph else math.min(pw, ph))) / 2)
				table.insert(
					pads,
					{
						name = row.Name .. "/" .. part.Name,
						l = px - sx,
						t = py - sy,
						r = px + pw + sx,
						b = py + ph + sy,
					}
				)
			end
		end
		y += row.Size.Y.Offset + 8
	end
	local clash = nil
	for i = 1, #pads do
		for j = i + 1, #pads do
			local a, b = pads[i], pads[j]
			if a.l < b.r - 0.5 and b.l < a.r - 0.5 and a.t < b.b - 0.5 and b.t < a.b - 0.5 then
				clash = clash or (a.name .. " / " .. b.name)
			end
		end
	end
	check(#pads >= 15, ("%s: %d controls measured"):format(tag, #pads))
	check(clash == nil, tag .. ": no two touch pads overlap" .. (if clash then (" (" .. clash .. ")") else ""))
end
local k = place(844, 390, 58)
phoneSell(k, "market phone 844x390 Sell")
__dump(player.PlayerGui, 844, 390)
workspace.CurrentCamera.ViewportSize = Vector2.new(667, 375)
-- Drawn again on the smaller screen (its phone text floor is larger).
WalletController.Toggle()
WalletController.Toggle()
market.quantities.backpack1.SetQuantity(2)
k = place(667, 375, 58)
phoneSell(k, "market phone 667x375 Sell")
__dump(player.PlayerGui, 667, 375)
-- Scrolled down to the vault's rows.
market.scroll:ScrollToRow(find(gui, "vaultHide"))
__dump(player.PlayerGui, 667, 375)
market.list.CanvasPosition = Vector2.new(0, 0)
-- The quantity dialog on phones, fitted as in game; its text is at least 9
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
