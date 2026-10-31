-- Drives TradeController headlessly in the kit Trade window (Hud/ListWindow,
-- docs/ui/ListWindows.md): inviting a player, an invite toast answered through
-- its dialog, then a running trade's two offer panels, adding a backpack item
-- and vault materials, gems, the lock and the confirm question.
--
--   python3 art/ui/capture/capture.py trade_flow
--
-- Pages: 1 invite list, 2 the invite toast, 3 a running trade (top), 4 the
-- same scrolled to your items, 5 both locked with the confirm dialog, 6 forced
-- states, 7 phone 844 × 390.

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
for index, entry in { { "ForestRanger", 15 }, { "SunnyVale", 8 } } do
	local other = Instance.new("Player")
	other.Name = entry[1]
	other.DisplayName = entry[1]
	other.UserId = index + 1
	other:SetAttribute("Level", entry[2])
	other.Parent = Players
end
local calls = {}
local vault = {
	backpack = {
		{ key = "b1", catalogId = "Redberry", name = "Redberry", quantity = 3, tradeable = true },
		{ key = "b2", catalogId = "StoneSpear", name = "★ Stone Spear", tradeable = true, permanent = true },
	},
	materials = {
		{ catalogId = "Amethyst", name = "Amethyst", quantity = 24 },
		{ catalogId = "IronBar", name = "Iron Bar", quantity = 40 },
	},
	items = {},
}
for name, fn in
	{
		VaultSnapshot = function()
			return vault
		end,
		TradeRequest = function(userId)
			table.insert(calls, { "TradeRequest", userId })
			return true
		end,
		TradeOffer = function(_, keys, gems, materials)
			table.insert(calls, { "TradeOffer", keys, gems, materials })
			return true
		end,
		TradeLock = function()
			table.insert(calls, { "TradeLock" })
			return true
		end,
		TradeConfirm = function()
			table.insert(calls, { "TradeConfirm" })
			return true
		end,
		TradeCancel = function()
			return true
		end,
		TradeRespond = function(id, accept)
			table.insert(calls, { "TradeRespond", id, accept })
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
local changed = Instance.new("RemoteEvent")
changed.Name = "TradeChanged"
changed.Parent = folder
local Shared = ReplicatedStorage.Shared
local TradeRules = require(Shared.Economy.TradeRules)
-- Every listed slot and Amethyst trade in this scene.
TradeRules.IsTradeableSlot = function(item)
	return item.tradeable == true
end
TradeRules.IsTradeableMaterial = function(catalogId)
	return catalogId == "Amethyst"
end
local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local Kit = require(Client.Hud.Kit)
local ListWindow = require(Client.Hud.ListWindow)
local TradeController = require(Client.Controllers.TradeController)
TradeController.Start()
TradeController.Toggle()
local gui = player.PlayerGui:FindFirstChild("FlintbornTrade")
local function check(cond, msg)
	print((cond and "  ok " or "  FAIL ") .. msg)
	if not cond then
		__failed = true
	end
end
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
local function dialog(): Instance?
	for _, d in player.PlayerGui:GetChildren() do
		if d.Name == "KitDialog" and d.Enabled then
			return d
		end
	end
	return nil
end

local W, H = 1672, 941
local BG = { background = "art/reference/ui/lobby/01_hud.png" }
local function place(width: number, height: number, top: number, target: Instance?)
	local k, centre = Kit.Scale.WindowFit(width, height, top, ListWindow.SIZE[1], ListWindow.SIZE[2], 1)
	local holder = (target or gui).Holder
	holder.Fit.Scale = k
	holder.Position = UDim2.fromOffset(centre.X, centre.Y)
	return k
end
local function centre(target: Instance)
	target.Holder.Fit.Scale = 1
	target.Holder.Position = UDim2.fromOffset(W / 2, H / 2 + 20)
end

check(gui and gui.Enabled, "the trade window opens")
centre(gui)
check(find(gui, "Player2") ~= nil and find(gui, "Player3") ~= nil, "lobby players are listed")
press(find(find(gui, "Player2"), "Invite"))
check(calls[1] and calls[1][2] == 2, "Invite asks that player")
__dump(player.PlayerGui, W, H, BG)

-- An invite arrives: a toast, its View opens Accept / Decline.
changed.OnClientEvent:Fire({ kind = "Invite", id = "t0", from = "SunnyVale" })
local toasts = player.PlayerGui:FindFirstChild("KitToasts")
check(toasts ~= nil and find(toasts, "Action1") ~= nil, "an invite shows a toast with View")
__dump(player.PlayerGui, W, H, BG)
press(find(toasts, "Action1"))
check(dialog() ~= nil, "View asks Accept or Decline")
press(find(dialog(), "Confirm"))
check(calls[#calls][1] == "TradeRespond" and calls[#calls][3] == true, "Accept answers the invite")

local session = {
	kind = "Session",
	id = "t1",
	partner = "ForestRanger",
	mine = { items = { { key = "b1", name = "Redberry", quantity = 3 } }, gems = 0 },
	theirs = {
		items = {
			{ key = "mat:Amethyst", name = "Amethyst", quantity = 10 },
			{ key = "x9", name = "Stone Axe" },
		},
		gems = 15,
	},
	locked = { mine = false, theirs = true },
	confirmed = { mine = false, theirs = false },
}
changed.OnClientEvent:Fire(session)
check(find(gui, "Pair") ~= nil, "both offers show")
check(find(find(gui, "Right"), "State"):GetAttribute("KitVariant") == "ready", "their lock shows")
check(find(find(gui, "Slotb1"), "Toggle"):FindFirstChild("Label", true).Text == "Remove", "an offered item can be removed")
press(find(find(gui, "Slotb2"), "Toggle"))
local offer = calls[#calls]
check(offer[1] == "TradeOffer" and table.find(offer[2], "b2") ~= nil, "Add puts the item in the offer")
press(find(find(gui, "MaterialAmethyst"), "Ten"))
offer = calls[#calls]
check(offer[4].Amethyst == 10, "+10 offers ten of a vault material")
check(find(gui, "MaterialIronBar") == nil, "untradeable materials are not offered")
local box = find(gui, "Box") :: TextBox
box.Text = "25"
box.FocusLost:Fire(false)
check(calls[#calls][3] == 25, "the gems box offers gems")
press(find(find(gui, "Buttons"), "Lock"))
check(calls[#calls][1] == "TradeLock", "Lock Offer locks")
centre(gui)
__dump(player.PlayerGui, W, H, BG)
-- The Kit.Scroll root and its ScrollingFrame are both named List.
local list = find(find(gui, "List"), "List") :: ScrollingFrame
list.CanvasPosition = Vector2.new(0, 420)
__dump(player.PlayerGui, W, H, BG)
list.CanvasPosition = Vector2.new(0, 0)

-- Both locked, the countdown over: Confirm asks with both offers spelled out.
session.mine = {
	items = {
		{ key = "b1", name = "Redberry", quantity = 3 },
		{ key = "b2", name = "★ Stone Spear" },
		{ key = "mat:Amethyst", name = "Amethyst", quantity = 10 },
	},
	gems = 25,
}
session.locked = { mine = true, theirs = true }
session.confirmAt = workspace:GetServerTimeNow() - 1
changed.OnClientEvent:Fire(session)
press(find(find(gui, "Buttons"), "Confirm"))
check(dialog() ~= nil, "Confirm asks first")
centre(dialog())
__dump(player.PlayerGui, W, H, BG)
press(find(dialog(), "Confirm"))
check(calls[#calls][1] == "TradeConfirm", "confirming confirms the trade")

-- Forced states.
find(find(gui, "Buttons"), "Cancel"):SetAttribute("DebugState", "hover")
find(find(gui, "Slotb1"), "Toggle"):SetAttribute("DebugState", "pressed")
find(find(gui, "Left"), "Item1"):SetAttribute("DebugState", "selected")
__dump(player.PlayerGui, W, H, BG)
for _, part in player.PlayerGui:GetDescendants() do
	if part:GetAttribute("DebugState") then
		part:SetAttribute("DebugState", "")
	end
end
changed.OnClientEvent:Fire({ kind = "Closed", reason = "Cancelled" })
check(find(gui, "Pair") == nil and find(gui, "Player2") ~= nil, "a closed trade goes back to the invite list")
print(__failed and "FLOW FAILED" or "FLOW OK")

workspace.CurrentCamera.ViewportSize = Vector2.new(844, 390)
UserInputService.TouchEnabled = true
UserInputService.KeyboardEnabled = false
UserInputService.MouseEnabled = false
changed.OnClientEvent:Fire(session)
local k = place(844, 390, 58)
print(("trade phone: window scale %.3f"):format(k))
__dump(player.PlayerGui, 844, 390)
if __failed then
	error("trade flow failed")
end
