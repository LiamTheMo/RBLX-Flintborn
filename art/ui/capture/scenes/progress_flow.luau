-- Drives ProgressionController headlessly in the kit Progress window
-- (Hud/ListWindow, docs/ui/ListWindows.md): the tabs with their level and
-- mastery bars, a perk purchase through its confirm dialog and the rebirth
-- question, confirmed only by holding the button (the hold's timing needs
-- real time: checked in game).
--
--   python3 art/ui/capture/capture.py progress_flow
--
-- Pages: 1 Overview, 2 Perks, 3 Rebirth, 4 Titles, 5 the rebirth dialog,
-- 6 forced states, 7 phone 844 × 390.

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
local calls = {}
local view = {
	level = 30,
	xp = 820,
	xpToNext = 1500,
	premium = false,
	boosterUntil = 0,
	masteries = {
		{ track = "Mining", level = 4, xp = 120, nextXp = 400, nextReward = "Prospector" },
		{ track = "Woodcutting", level = 2, xp = 40, nextXp = 200 },
		{ track = "Crafting", level = 10, xp = 0 },
	},
	titles = { "Wanderer", "Prospector" },
	rebirth = {
		count = 1,
		tokens = 3,
		levelNeeded = 30,
		legendariesNeeded = 1,
		legendaries = 1,
		ownedPerks = { Scholar = 2, Tidewalker = 2 },
	},
}
for name, fn in
	{
		ProgressionSnapshot = function()
			return view
		end,
		RebirthPreview = function()
			return {
				reset = { "Level 30 → 1", "Mastery levels" },
				kept = { "Vault", "Titles", "Coins and Gems" },
				gained = { "3 perk tokens" },
			}
		end,
		Rebirth = function()
			table.insert(calls, { "Rebirth" })
			return true
		end,
		BuyPerk = function(perkId)
			table.insert(calls, { "BuyPerk", perkId })
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
for _, name in { "ProgressionChanged", "XpGained" } do
	local remote = Instance.new("RemoteEvent")
	remote.Name = name
	remote.Parent = folder
end
local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local Kit = require(Client.Hud.Kit)
local ListWindow = require(Client.Hud.ListWindow)
local ProgressionController = require(Client.Controllers.ProgressionController)
ProgressionController.Start()
folder.ProgressionChanged.OnClientEvent:Fire(view)
folder.XpGained.OnClientEvent:Fire({ amount = 40, reason = "Gathered" })
ProgressionController.Toggle()
local gui = player.PlayerGui:FindFirstChild("FlintbornProgress")
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

check(gui and gui.Enabled, "the progress window opens")
check(find(gui, "Mining") ~= nil, "masteries are listed")
check(find(find(gui, "Mining"), "Bar"):GetAttribute("KitValue") == 0.3, "a mastery bar shows its real fraction")
check(find(find(gui, "Crafting"), "Done") ~= nil, "a finished mastery shows a tick")
check(find(find(gui, "Mining"), "Done") == nil, "a mastery in progress shows its bar, no ring")
check(find(player.PlayerGui, "Popup") ~= nil, "an XP pop-up shows")
press(find(gui, "Perks"))
press(find(find(gui, "Scholar"), "Buy"))
check(dialog() ~= nil and #calls == 0, "Buy asks first")
press(find(dialog(), "Confirm"))
check(calls[#calls] and calls[#calls][2] == "Scholar", "confirming buys the perk's next rank")
check(find(find(gui, "Tidewalker"), "Done") ~= nil, "a maxed perk shows a tick")
press(find(gui, "Rebirth"))
press(find(gui, "Review"))
local d = dialog()
check(d ~= nil, "rebirth asks first")
press(find(d, "Confirm"))
check(#calls == 1, "a tap does not rebirth: the button must be held")
-- Time does not pass in a capture, so the hold itself is checked in game.
check(find(find(d, "Confirm"), "Hold") ~= nil, "the confirm button carries the hold bar")
press(find(d, "Cancel"))
check(dialog() == nil and #calls == 1, "Cancel closes the question without a rebirth")
print(__failed and "FLOW FAILED" or "FLOW OK")

local W, H = 1672, 941
local BG = { background = "art/reference/ui/lobby/01_hud.png" }
local function centre(target: Instance)
	target.Holder.Fit.Scale = 1
	target.Holder.Position = UDim2.fromOffset(W / 2, H / 2 + 20)
end
if not gui.Enabled then
	ProgressionController.Toggle()
end
centre(gui)
for _, name in { "Overview", "Perks", "Rebirth", "Titles" } do
	press(find(gui, name))
	__dump(player.PlayerGui, W, H, BG)
end
press(find(gui, "Rebirth"))
press(find(gui, "Review"))
d = dialog()
centre(d)
__dump(player.PlayerGui, W, H, BG)
press(find(d, "Cancel"))
press(find(gui, "Perks"))
find(find(gui, "Scholar"), "Buy"):SetAttribute("DebugState", "hover")
find(gui, "Rebirth"):SetAttribute("DebugState", "hover")
find(find(gui, "Tidewalker"), "Done"):SetAttribute("DebugState", "disabled")
__dump(player.PlayerGui, W, H, BG)
for _, part in player.PlayerGui:GetDescendants() do
	if part:GetAttribute("DebugState") then
		part:SetAttribute("DebugState", "")
	end
end
workspace.CurrentCamera.ViewportSize = Vector2.new(844, 390)
UserInputService.TouchEnabled = true
UserInputService.KeyboardEnabled = false
UserInputService.MouseEnabled = false
press(find(gui, "Overview"))
local k, c = Kit.Scale.WindowFit(844, 390, 58, ListWindow.SIZE[1], ListWindow.SIZE[2], 1)
gui.Holder.Fit.Scale = k
gui.Holder.Position = UDim2.fromOffset(c.X, c.Y)
__dump(player.PlayerGui, 844, 390)
if __failed then
	error("progress flow failed")
end
