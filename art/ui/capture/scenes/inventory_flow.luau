-- Drives the lobby VaultController and its Inventory window headlessly through
-- real presses: open on the Backpack tab, select, store, an overflow that asks
-- first, search, category, switch to the Vault tab, take a material in the
-- picked amount, take an item, STORE ALL, the vault-full upgrade link, the
-- extraction receipt and close. Remotes are mocked. The last page is the
-- window after the flow (Vault tab).
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
workspace:SetAttribute("FlintbornPlaceRole", "Lobby")
local folder = Instance.new("Folder")
folder.Name = "FlintbornRemotes"
folder.Parent = ReplicatedStorage
local calls = {}
local snapshots = 0
local view = {
	backpack = {
		{ catalogId = "StoneAxe", name = "Stone Axe", rarity = "Common" },
		{ catalogId = "Wood", name = "Wood", quantity = 900, rarity = "Common" },
		{ catalogId = "Fiber", name = "Plant Fiber", quantity = 10, rarity = "Common" },
	},
	items = { { catalogId = "IronSword", name = "Iron Sword", rarity = "Uncommon" } },
	materials = { { catalogId = "Stone", name = "Stone", quantity = 84 } },
	itemCapacity = 25,
	backpackCapacity = 50,
}
local handlers = {
	VaultSnapshot = function()
		snapshots += 1
		return view
	end,
	VaultDeposit = function(index, confirmId, loss)
		table.insert(calls, { "VaultDeposit", index, confirmId, loss })
		local item = view.backpack[index]
		if item and item.catalogId == "Wood" and confirmId == nil then
			return false, "VaultWouldOverflow", 40
		end
		table.remove(view.backpack, index)
		return true
	end,
	VaultWithdrawItem = function(index)
		table.insert(calls, { "VaultWithdrawItem", index })
		return false, "BackpackFull"
	end,
	VaultWithdrawMaterial = function(id, amount)
		table.insert(calls, { "VaultWithdrawMaterial", id, amount })
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
local receipt = Instance.new("RemoteEvent")
receipt.Name = "ExtractionReceipt"
receipt.Parent = folder

local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local VaultController = require(Client.Controllers.VaultController)
local player = Players.LocalPlayer
local function check(cond, msg)
	print((cond and "  ok " or "  FAIL ") .. msg)
	if not cond then
		__failed = true
	end
end
local changed = 0
VaultController.Changed:Connect(function()
	changed += 1
end)
VaultController.Start()
check(not VaultController.IsOpen(), "starts closed")
VaultController.Open("Backpack")
local gui = player.PlayerGui:FindFirstChild("FlintbornInventory")
local window = VaultController.window
check(gui and gui.Enabled and VaultController.IsOpen(), 'Open("Backpack") opens the window')
check(snapshots == 1 and changed == 1, "opening fetches one snapshot and fires Changed")
check(window:SlotFor("b1") ~= nil and window:SlotFor("be50") ~= nil, "fifty backpack slots, filled and empty")
check(window.selectedId == "b1" and window.detailName.root.Text == "Stone Axe", "the first item is chosen on open")

local function press(component)
	component.control.hit.Activated:Fire()
end

-- STORE the axe.
press(window:ActionButton("store"))
check(calls[1] and calls[1][1] == "VaultDeposit" and calls[1][2] == 1, "STORE deposits the chosen slot")
check(not window.busy and window:ActionButton("store") ~= nil, "the action is live again after the reply")
-- Wood overflows: asks first, then deposits with the confirmation.
press(window:SlotFor("b1"))
check(window.detailName.root.Text == "Wood", "pressing a slot shows it in the card")
window:ActionButton("store").control:Activate()
local dialogGui = player.PlayerGui:FindFirstChild("KitDialog")
check(dialogGui ~= nil and dialogGui.Enabled, "an overflow asks first")
local before = #calls
local confirm = nil
for _, d in dialogGui:GetDescendants() do
	if d.Name == "Confirm" and d:GetAttribute("KitComponent") == "Button" then
		confirm = d
	end
end
confirm.Hit.Activated:Fire()
local last = calls[#calls]
check(#calls == before + 1 and last[3] == "Wood" and last[4] == 40, "deposit anyway names the stack and loss")

-- Search and categories filter the grid.
window:SetQuery("fib")
check(window:SlotFor("b1") ~= nil and window:SlotFor("be50") == nil, "search keeps the match and hides empties")
window:SetQuery("")
window.categories.tabs[2].control.hit.Activated:Fire() -- Tools
check(window.category == "Tools" and window:SlotFor("b1") == nil, "the Tools category hides plant fiber")
window.categories.tabs[1].control.hit.Activated:Fire() -- All
check(window.category == "All", "All shows everything again")

-- Vault tab: take 30 stone with the stepper.
press(window.tabs.Vault)
check(window.tabId == "Vault", "the Vault tab opens")
check(window:SlotFor("i1") ~= nil and window:SlotFor("mStone") ~= nil, "vault items and materials shown")
check(
	window.tabs.Vault.label.Text == "Vault"
		and window.tabs.Vault.countBadge ~= nil
		and window.tabs.Vault.countBadge.label.Text == "1/25",
	"the tab carries the vault's capacity on its count plaque"
)
press(window:SlotFor("mStone"))
check(window.amount ~= nil, "a material shows the amount stepper")
window.amount.plus.control.hit.Activated:Fire()
check(window.amount.value == 11, "+ raises the amount")
window.amount.all.control.hit.Activated:Fire()
press(window:ActionButton("take"))
last = calls[#calls]
check(last[1] == "VaultWithdrawMaterial" and last[2] == "Stone" and last[3] == 84, "All takes the whole stack")
-- Taking an item the server refuses shows the reason.
-- (Slots are pooled across tabs: Activate skips the press debounce the
-- earlier press on this slot started.)
window:SlotFor("i1").control:Activate()
window:ActionButton("take").control:Activate()
last = calls[#calls]
check(last[1] == "VaultWithdrawItem" and last[2] == 1, "TAKE withdraws the chosen vault item")

-- Back to the backpack: STORE ALL.
press(window.tabs.Backpack)
window.toolbar.storeAll.control:Activate()
check(#view.backpack == 0, "STORE ALL empties the backpack")
check(window:SlotFor("be1") ~= nil, "the empty backpack shows its slots")

-- A full vault offers more space.
for i = 2, 25 do
	view.items[i] = { catalogId = "StoneAxe", name = "Stone Axe" }
end
press(window.tabs.Vault)
VaultController.Open("Vault")
check(window.toolbar.upgrade ~= nil, "a full vault links to vault upgrades")

-- The receipt toast.
receipt.OnClientEvent:Fire({
	portal = "the Old Gate",
	multiplier = 1,
	vaulted = { Stone = 20 },
	toBackpack = {},
	deleted = {},
})
local toasts = player.PlayerGui:FindFirstChild("KitToasts")
check(toasts ~= nil and #toasts:GetDescendants() > 0, "the extraction receipt shows as a toast")

local busyBefore = window.busy
check(busyBefore == false, "nothing is left pending")
print(__failed and "FLOW FAILED" or "FLOW OK")
__dump(player.PlayerGui, 1672, 941, { background = "art/reference/ui/lobby/01_hud.png" })
window.window.close.control.hit.Activated:Fire()
check(not VaultController.IsOpen(), "the close button closes the window")
VaultController.Toggle()
check(VaultController.IsOpen(), "Toggle opens it again")
VaultController.Toggle()
check(not VaultController.IsOpen(), "and closes it")
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

-- ×20 open / close: no instances and no connections left behind (the Inventory window).
VaultController.Toggle()
VaultController.Toggle()
local instancesBefore, connectionsBefore = leakCounts()
for _ = 1, 20 do
	VaultController.Toggle()
	VaultController.Toggle()
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

print(__failed and "FLOW FAILED" or "FLOW OK")
if __failed then
	error("inventory flow failed")
end
