-- The lobby Inventory window on phones held sideways (touch only, the top bar
-- 58 px down), built by the real VaultController over mocked remotes and fitted
-- as in game. Pages:
--   1 844 x 390, the Backpack tab under All: everything owned (backpack, then
--     the vault's items and materials)
--   2 844 x 390, the Vault tab with a material chosen (the amount stepper)
--   3 667 x 375, the Backpack tab under Consumables
-- Checks: every slot is square, every category label fits whole (no "..."), and
-- prints the smallest text drawn.
local UserInputService = game:GetService("UserInputService")
local TextService = game:GetService("TextService")
workspace.CurrentCamera.ViewportSize = Vector2.new(844, 390)
UserInputService.TouchEnabled = true
UserInputService.KeyboardEnabled = false
UserInputService.MouseEnabled = false
UserInputService.GetLastInputType = function()
	return Enum.UserInputType.Touch
end

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
workspace:SetAttribute("FlintbornPlaceRole", "Lobby")
local folder = Instance.new("Folder")
folder.Name = "FlintbornRemotes"
folder.Parent = ReplicatedStorage
local view = {
	backpack = {
		{ catalogId = "StoneAxe", name = "Stone Axe" },
		{ catalogId = "Redberry", name = "Redberry", quantity = 14 },
		{ catalogId = "BasicMedicine", name = "Basic Medicine", quantity = 2 },
		{ catalogId = "FlintArrow", name = "Flint Arrow", quantity = 20 },
	},
	items = {
		{ catalogId = "IronSword", name = "Iron Sword", qualityRoll = 0.03 },
		{ catalogId = "StonePickaxe", name = "Stone Pickaxe", permanent = true },
		{ catalogId = "HideChest", name = "Hide Chest" },
	},
	materials = {
		{ catalogId = "Stone", name = "Stone", quantity = 84 },
		{ catalogId = "Wood", name = "Wood", quantity = 412 },
		{ catalogId = "Fiber", name = "Plant Fiber", quantity = 37 },
	},
	itemCapacity = 25,
	backpackCapacity = 50,
}
for _, name in { "VaultSnapshot", "VaultDeposit", "VaultWithdrawItem", "VaultWithdrawMaterial" } do
	local remote = Instance.new("RemoteFunction")
	remote.Name = name
	remote.Parent = folder
	remote.InvokeServer = function()
		if name == "VaultSnapshot" then
			return view
		end
		return true
	end
end
local receipt = Instance.new("RemoteEvent")
receipt.Name = "ExtractionReceipt"
receipt.Parent = folder

local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local ItemInfo = require(ReplicatedStorage.Shared.Items.ItemInfo)
local VaultController = require(Client.Controllers.VaultController)
local player = Players.LocalPlayer
local function check(cond, msg)
	print((cond and "  ok " or "  FAIL ") .. msg)
	if not cond then
		__failed = true
	end
end
local function shown(item: Instance): boolean
	local node: Instance? = item
	while node and node:IsA("GuiObject") do
		if not node.Visible then
			return false
		end
		node = node.Parent
	end
	return true
end

VaultController.Start()
local window = VaultController.window

-- Fits the window to a phone screen and checks it there.
local function phone(w: number, h: number, tag: string)
	workspace.CurrentCamera.ViewportSize = Vector2.new(w, h)
	window.screen:Fit(w, h, 58, 1)
	local scale = window.screen.scale.Scale
	local smallest, slots, square = math.huge, 0, true
	for _, item in window.screen.gui:GetDescendants() do
		if not shown(item) then
			continue
		end
		if item:IsA("TextLabel") and item:GetAttribute("KitTextRole") and item.Text ~= "" then
			smallest = math.min(smallest, item.TextSize * scale)
		end
		if item:GetAttribute("KitComponent") == "Slot" and item:IsA("GuiObject") then
			slots += 1
			if item.Size.X.Offset ~= item.Size.Y.Offset then
				square = false
				print(("  slot %s is %d x %d"):format(item.Name, item.Size.X.Offset, item.Size.Y.Offset))
			end
		end
	end
	print(("%s: window scale %.3f, smallest text %.1f screen px, %d slots"):format(tag, scale, smallest, slots))
	check(slots > 0 and square, tag .. ": every slot is square (equal width and height)")
	-- A category label shrinks to fit, never below 9 screen px: at that floor
	-- the whole word must fit its box.
	local fits = true
	for _, id in ItemInfo.CATEGORIES do
		local tab = window.screen.gui:FindFirstChild("Category" .. id, true)
		local label = tab and tab:FindFirstChild("Label", true)
		if label == nil then
			fits = false
			print("  no label for " .. id)
			continue
		end
		local floor = 9 / scale
		local need = TextService:GetTextSize(label.Text, floor, Enum.Font.Merriweather, Vector2.new(1e4, 1e4)).X * 1.02
		if need > label.Size.X.Offset then
			fits = false
			print(("  %s needs %.0f design px at the floor, box %d"):format(label.Text, need, label.Size.X.Offset))
		end
	end
	check(fits, tag .. ": every category label fits whole")
end

-- 1: everything owned, under All.
VaultController.Open("Backpack")
phone(844, 390, "inventory_phone 844x390 Backpack")
check(
	window:SlotFor("b1") ~= nil and window:SlotFor("i1") ~= nil and window:SlotFor("mWood") ~= nil,
	"the Backpack tab shows the backpack, vault items and vault materials"
)
__dump(player.PlayerGui, 844, 390)

-- 2: the Vault tab, a material chosen.
window.tabs.Vault.control.hit.Activated:Fire()
window:SlotFor("mWood").control:Activate()
phone(844, 390, "inventory_phone 844x390 Vault")
check(window.amount ~= nil, "a vault material shows the amount stepper")
__dump(player.PlayerGui, 844, 390)

-- 3: a smaller phone, Consumables.
window.tabs.Backpack.control.hit.Activated:Fire()
window:SetCategory("Consumables")
phone(667, 375, "inventory_phone 667x375 Consumables")
check(
	window:SlotFor("b2") ~= nil and window:SlotFor("b3") ~= nil and window:SlotFor("b1") == nil,
	"Consumables shows the berries and medicine, not the axe"
)
__dump(player.PlayerGui, 667, 375)
print(__failed and "FLOW FAILED" or "FLOW OK")
if __failed then
	error("inventory_phone failed")
end
