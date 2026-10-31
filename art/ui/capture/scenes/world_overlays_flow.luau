-- Drives the world overlays through real presses and remote events and checks
-- what reaches the (mocked) server: the tutorial's Got it, Take and Store in the
-- loot and chest windows, the tribe's Invite and Kick, the build palette's
-- piece tabs, tier arrows and Rotate, Escape / B closing the window, the
-- server notice's ✕, and a 20× open / close leak check. Captures the end state
-- (the build palette after picking a Floor one tier up).
--
--   python3 art/ui/capture/capture.py world_overlays_flow

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local W, H = 1672, 941
workspace.CurrentCamera.ViewportSize = Vector2.new(W, H)
workspace:SetAttribute("FlintbornPlaceRole", "World")

local folder = Instance.new("Folder")
folder.Name = "FlintbornRemotes"
folder.Parent = ReplicatedStorage
local events = {}
for _, name in { "Notice", "TutorialChanged", "CorpseOpened", "DeathSummary", "ChestOpened", "TribeChanged" } do
	local remote = Instance.new("RemoteEvent")
	remote.Name = name
	remote.Parent = folder
	events[name] = remote
end
local calls = {}
local answers = { CorpseTake = { false, "OutOfRange" } }
for _, name in { "TutorialAction", "CorpseTake", "ChestTake", "ChestPut", "TribeAction", "Build", "BuildInfo" } do
	local remote = Instance.new("RemoteFunction")
	remote.Name = name
	remote.Parent = folder
	remote.InvokeServer = function(_, ...)
		table.insert(calls, { name, ... })
		if name == "BuildInfo" then
			return { auras = {} }
		end
		return table.unpack(answers[name] or { true, "Done" })
	end
end
local function last()
	return calls[#calls] or {}
end

local player = Players.LocalPlayer
player:SetAttribute("SessionState", "ActiveRun")
player.GetMouse = function()
	return { X = 0, Y = 0 }
end
local mira = Instance.new("Player")
mira.Name = "Mira"
mira.DisplayName = "Mira"
mira.UserId = 2
mira.Parent = Players

local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local Controllers = Client.Controllers
local Kit = require(Client.Hud.Kit)
local InventoryController = require(Controllers.InventoryController)
InventoryController.Snapshot.slots = {
	{ area = "backpack", index = 4, catalogId = "Wood", quantity = 24 },
}
local started = {}
for _, name in
	{
		"NoticeController",
		"TutorialController",
		"LootController",
		"StorageController",
		"TribeController",
		"BuildController",
	}
do
	started[name] = require(Controllers[name])
	started[name].Start()
end
local gui = player.PlayerGui
local function find(name, from)
	return (from or gui):FindFirstChild(name, true)
end
-- Presses a kit control. Controls ignore a second press within their debounce
-- (0.15 s of real time), so a repeat press waits that out first.
local pressed = {}
local function press(root)
	local hit = root:FindFirstChild("Hit")
	if pressed[hit] then
		local t = os.clock()
		while os.clock() - t < 0.2 do
		end
	end
	pressed[hit] = true
	hit.Activated:Fire()
end
local function check(cond, msg)
	print((cond and "  ok " or "  FAIL ") .. msg)
	if not cond then
		__failed = true
	end
end

-- Tutorial: Got it asks the server to acknowledge the step.
events.TutorialChanged.OnClientEvent:Fire({
	id = "Food",
	index = 2,
	total = 11,
	title = "Food",
	hint = "Eat.",
	ack = true,
})
press(find("Got it", find("Tutorial")))
check(last()[1] == "TutorialAction" and last()[2] == "Ack", "Got it sends Ack")
events.TutorialChanged.OnClientEvent:Fire({
	id = "Food",
	index = 2,
	total = 11,
	title = "Food",
	hint = "Eat.",
	done = true,
})
check(not find("Tutorial").Visible, "a finished tutorial hides its card")

-- Loot: Take asks for that entry; a refusal shows why.
events.CorpseOpened.OnClientEvent:Fire("body1", {
	{ index = 1, name = "Stone Axe", catalogId = "StoneAxe", key = "item-stoneaxe-8", rarity = "Common" },
	{ index = 2, name = "Iron Ore", catalogId = "IronOre", key = "stack:IronOre", rarity = "Uncommon", quantity = 6 },
})
local loot = find("FlintbornLoot")
press(find("Take", find("Item2", loot)))
check(
	last()[1] == "CorpseTake" and last()[2] == "body1" and last()[3] == 2 and last()[4] == "stack:IronOre",
	"Take asks for that item of that body, by its key"
)
check(string.find(find("Status", loot).Text, "OutOfRange") ~= nil, "a refused take says why")
Kit.Modal.Back()
check(not loot.Enabled, "Escape / B closes the loot window")

-- Storage: Store sends the carried slot; Take the chest entry.
events.ChestOpened.OnClientEvent:Fire(
	"chest1",
	{ { index = 3, name = "Wood", catalogId = "Wood", key = "stack:Wood", rarity = "Common", quantity = 40 } }
)
local chest = find("FlintbornStorage")
press(find("Store", chest))
check(
	last()[1] == "ChestPut" and last()[2] == "chest1" and last()[3] == "backpack" and last()[4] == 4,
	"Store sends the slot"
)
press(find("Take", chest))
check(last()[1] == "ChestTake" and last()[3] == 3, "Take asks for the chest entry")
chest:FindFirstChild("Close", true):FindFirstChild("Hit").Activated:Fire()
check(not chest.Enabled, "the ✕ closes the chest window")

-- Tribe: Invite and Kick go to the server with the player's id.
started.TribeController.Toggle()
events.TribeChanged.OnClientEvent:Fire({
	tribe = {
		leader = player.UserId,
		members = { { userId = player.UserId, name = player.Name }, { userId = 7, name = "Ash" } },
		allies = {},
	},
	invites = {},
	others = {},
})
local tribe = find("FlintbornTribe")
-- A player row's action button is its "Action".
press(find("Action", find("Mira", tribe)))
check(last()[1] == "TribeAction" and last()[2] == "invite" and last()[3] == 2, "Invite asks for that player")
press(find("Action", find("Ash", tribe)))
check(last()[2] == "kick" and last()[3] == 7, "Kick asks for that member")
check(find("Status", tribe).Text == "Done", "the server's answer shows")
started.TribeController.Toggle()

-- Leak check: open and close the loot window 20 times.
local function count()
	return #gui:GetDescendants()
end
events.CorpseOpened.OnClientEvent:Fire(
	"body2",
	{ { index = 1, name = "Stone", catalogId = "Stone", key = "stack:Stone", rarity = "Common", quantity = 3 } }
)
Kit.Modal.Back()
local before = count()
for _ = 1, 20 do
	events.CorpseOpened.OnClientEvent:Fire(
		"body2",
		{ { index = 1, name = "Stone", catalogId = "Stone", key = "stack:Stone", rarity = "Common", quantity = 3 } }
	)
	Kit.Modal.Back()
end
check(count() == before, ("20 opens leave the PlayerGui as it was (%d -> %d)"):format(before, count()))

-- Notice: the ✕ dismisses.
events.Notice.OnClientEvent:Fire({ title = "Items recovered", text = "Recovered to your vault." })
local card = find("Card", find("Notice"))
press(find("Close", card))
check(not card.Visible, "the notice's ✕ dismisses it")

-- Build: a tab picks the piece, the arrows step the tier, Rotate turns it.
started.BuildController.Toggle()
local palette = find("Palette")
press(find("Floor", palette))
check(find("Floor", palette):GetAttribute("KitState") == "selected", "a piece tab selects")
press(find("TierUp", palette))
local tier = find("Tier", palette).Text
check(string.find(tier, "2/") ~= nil, "the arrow steps the tier (" .. tier .. ")")
press(find("Rotate", palette))
check(true, "Rotate presses without error")
press(find("Chest", palette))
check(not find("TierUp", palette).Visible, "one-tier pieces hide the arrows")
press(find("Floor", palette))
check(string.find(find("Tier", palette).Text, "2/") ~= nil, "the chosen tier survives picking a chest")

print(__failed and "FLOW FAILED" or "FLOW OK")
__dump(gui, W, H, { background = "art/reference/lobby_map.png" })
if __failed then
	error("world overlays flow failed")
end
