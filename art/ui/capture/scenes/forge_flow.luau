-- Drives ForgeController and its RecipeWindow headlessly through real events:
-- choose a recipe, raise the quantity, forge a batch (one nonce, the count sent,
-- a receipt toast, a fresh snapshot), a refusal (its reason in a toast), a
-- transport failure retried with the same nonce, a locked recipe that cannot be
-- sent, and a Permanent conversion that asks first (pick the vault item, hold
-- CONVERT) and sends exactly that item with a count of 1. Gamepad: the chosen
-- row is the default selection and leads right to FORGE. Ends with the window
-- and its toasts.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
workspace:SetAttribute("FlintbornPlaceRole", "Lobby")

local W, H = 1672, 941

local function input(id, name, owned, needed)
	return { catalogId = id, name = name, owned = owned, needed = needed }
end

local snapshots = 0
local view = {
	maxBatch = 10,
	categories = { "Tools", "Weapons", "Armor", "Supplies", "Permanent" },
	recipes = {
		{
			id = "ForgeIronAxe",
			kind = "Special",
			category = "Tools",
			name = "Iron Axe",
			output = "IronAxe",
			quantity = 1,
			unlocked = true,
			requirement = "",
			maxCount = 2,
			inputs = { input("IronBar", "Iron Bar", 40, 16), input("Wood", "Wood", 30, 10) },
		},
		{
			id = "ForgeIronLegs",
			kind = "Special",
			category = "Armor",
			name = "Iron Legs/Boots",
			output = "IronLegs",
			quantity = 1,
			unlocked = false,
			requirement = "Unlock: extract 1 time(s), extract Iron Ore",
			maxCount = 1,
			inputs = { input("Hide", "Hide", 8, 8), input("IronBar", "Iron Bar", 40, 30) },
		},
		{
			id = "PermanentIronSword",
			kind = "Permanent",
			category = "Permanent",
			name = "Permanent Iron Sword",
			output = "IronSword",
			quantity = 1,
			unlocked = true,
			requirement = "",
			maxCount = 1,
			inputs = { input("AncientEmber", "Ancient Ember", 3, 2), input("IronBar", "Iron Bar", 90, 60) },
			sources = {
				{ instanceId = "sword-1", name = "Iron Sword", qualityRoll = 0.02 },
				{ instanceId = "sword-2", name = "Iron Sword", qualityRoll = -0.01 },
			},
		},
	},
}

local calls = {}
local replies = {}
local folder = Instance.new("Folder")
folder.Name = "FlintbornRemotes"
folder.Parent = ReplicatedStorage
for name, fn in
	{
		ForgeSnapshot = function()
			snapshots += 1
			return view
		end,
		ForgeCraft = function(...)
			table.insert(calls, { ... })
			local reply = table.remove(replies, 1)
			if reply == "drop" then
				error("transport failure")
			end
			return table.unpack(reply or { true, {} })
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
local ForgeController = require(Client.Controllers.ForgeController)
local RecipeWindow = require(Client.Hud.Screens.RecipeWindow)
local player = Players.LocalPlayer
ForgeController.Start()

local function check(cond, msg)
	print((cond and "  ok " or "  FAIL ") .. msg)
	if not cond then
		__failed = true
	end
end

-- Every text shown in the toast column.
local function toasts(): string
	local gui = player.PlayerGui:FindFirstChild("KitToasts")
	local out = {}
	for _, d in (gui and gui:GetDescendants()) or {} do
		if d:IsA("TextLabel") then
			table.insert(out, d.Text)
		end
	end
	return table.concat(out, " | ")
end

ForgeController.Toggle()
local window = ForgeController.window
check(window:IsOpen() and window.screen.gui.Enabled, "the Forge tile opens the window")
check(snapshots == 1, "opening fetches one snapshot")
check(window:Selected().id == "ForgeIronAxe", "the first recipe is chosen")
check(window.screen.defaultSelection == window.rows.ForgeIronAxe.control.hit, "gamepad starts on the chosen row")
check(window.rows.ForgeIronAxe.control.hit.NextSelectionRight == window.button.control.hit, "right goes to FORGE")
check(window.button.control.hit.NextSelectionLeft == window.rows.ForgeIronAxe.control.hit, "left comes back")

-- Quantity: bounded by maxCount.
window.stepper.plus.control:Activate()
window.stepper.plus.control:Activate()
check(window:Count() == 2, "+ stops at the snapshot's maxCount")
check(
	string.find(window.cards[1].root:FindFirstChild("Count", true).Text, "40 / 32", 1, true) ~= nil,
	"REQUIRES shows the cost of 2"
)

-- Forge 2: one request with the count and a nonce, a receipt, a fresh snapshot.
replies = { { true, { count = 2, output = { catalogId = "IronAxe" } } } }
window.button.control:Activate()
check(#calls == 1, "FORGE sends one request")
local first = calls[1]
check(
	first[1] == "ForgeIronAxe" and first[2] == nil and type(first[3]) == "string" and first[4] == 2,
	"recipe, no source, nonce, count 2"
)
check(string.find(toasts(), "Iron Axe ×2", 1, true) ~= nil, "the receipt names what was forged")
check(snapshots == 2, "the snapshot refreshes after a forge")
check(window.button.root:GetAttribute("KitState") ~= "busy", "FORGE is ready again")

-- A refusal: its reason, nothing else changes.
replies = { { false, "MissingMaterials" } }
window.button.control:Activate()
check(#calls == 2, "a second request")
check(calls[2][3] ~= first[3], "a new request has a new nonce")
check(string.find(toasts(), "enough materials", 1, true) ~= nil, "the refusal says why")

-- A dropped request is retried once with the same nonce.
replies = { "drop", { true, { count = 1 } } }
window.stepper.minus.control:Activate()
window.button.control:Activate()
check(#calls == 4 and calls[3][3] == calls[4][3], "a transport failure retries with the same nonce")
check(calls[4][4] == 1, "the stepper's count is sent")

-- A locked recipe can be chosen but not sent.
window.rows.ForgeIronLegs.control.hit.Activated:Fire()
check(window:Selected().id == "ForgeIronLegs", "a locked recipe is chosen to show its unlock")
window.button.control:Activate()
check(#calls == 4, "a locked recipe cannot be forged")

-- A Permanent conversion asks first, naming the vault item.
window.rows.PermanentIronSword.control.hit.Activated:Fire()
check(not window.stepper.root.Visible, "no quantity for a conversion")
window.button.control:Activate()
check(#calls == 4 and window.confirm ~= nil, "CONVERT opens the confirmation")
local dialog = window.confirm.dialog
local body = dialog.body
check(string.find(body:FindFirstChild("Text", true).Text, "+2.0%", 1, true) ~= nil, "it names the first item's quality")
window.confirm.Close()
check(#calls == 4, "cancel sends nothing")
window.button.control:Activate()
dialog = window.confirm.dialog
local second = dialog.body:FindFirstChild("sword-2", true)
second:FindFirstChild("Hit", true).Activated:Fire()
check(
	string.find(dialog.body:FindFirstChild("Text", true).Text, "-1.0%", 1, true) ~= nil,
	"picking the other item renames it"
)
-- The capture cannot hold a button for 1.5 s: finish the hold directly.
replies = { { true, { count = 1, output = { catalogId = "IronSword", permanent = true } } } }
dialog:_confirm()
check(#calls == 5, "a held CONVERT sends the conversion")
check(calls[5][1] == "PermanentIronSword" and calls[5][2] == "sword-2" and calls[5][4] == 1, "the chosen item, count 1")
check(string.find(toasts(), "Permanent", 1, true) ~= nil, "the receipt says it is Permanent")

-- Escape / B (Kit.Modal) and the tile close it again.
ForgeController.Toggle()
check(not window:IsOpen(), "the tile closes it")
ForgeController.Toggle()
window.rows.ForgeIronAxe.control.hit.Activated:Fire()

print(__failed and "FLOW FAILED" or "FLOW OK")
window.screen.holder.Position = UDim2.fromOffset(285 + 1102 / 2, 132 + RecipeWindow.SIZE[2] / 2)
window.screen.scale.Scale = 1
__dump(player.PlayerGui, W, H, { background = "art/reference/ui/lobby/01_hud.png" })
if __failed then
	error("forge flow failed")
end
