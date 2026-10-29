-- Drives ProgressionController headlessly: the Progress window's tabs, a perk
-- purchase and the rebirth question (armed only after its delay).
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
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
		{ track = "Gathering", level = 4, xp = 120, nextXp = 400, nextReward = "Forager" },
		{ track = "Combat", level = 2, xp = 40, nextXp = 200 },
		{ track = "Crafting", level = 10, xp = 0 },
	},
	titles = { "Scout", "Forager" },
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
			return { reset = { "Level 30 → 1" }, kept = { "Vault", "Titles" }, gained = { "3 perk tokens" } }
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
local ProgressionController = require(Client.Controllers.ProgressionController)
ProgressionController.Start()
folder.ProgressionChanged.OnClientEvent:Fire(view)
ProgressionController.Toggle()
local gui = player.PlayerGui:FindFirstChild("FlintbornProgress")
local function check(cond, msg)
	print((cond and "  ok " or "  FAIL ") .. msg)
	if not cond then
		__failed = true
	end
end
check(gui and gui.Enabled, "the progress window opens")
local window = gui.Window
local list = window.List
check(list:FindFirstChild("Gathering") ~= nil, "masteries are listed")
check(list.Crafting:FindFirstChild("Done") ~= nil, "a finished mastery shows a tick")
window.Perks.Press.Activated:Fire()
list.Scholar.Buy.Press.Activated:Fire()
check(calls[#calls] and calls[#calls][2] == "Scholar", "BUY buys the perk's next rank")
check(list.Tidewalker:FindFirstChild("Done") ~= nil, "a maxed perk shows a tick")
window.Rebirth.Press.Activated:Fire()
list:FindFirstChild("Review", true).Press.Activated:Fire()
check(window.Confirm.Visible, "rebirth asks first")
window.Confirm.Yes.Press.Activated:Fire()
check(#calls == 1, "the rebirth button is not armed before its delay")
window.Confirm.No.Press.Activated:Fire()
check(not window.Confirm.Visible, "cancel closes the question")
print(__failed and "FLOW FAILED" or "FLOW OK")
gui.Window.UIScale.Scale = 1.3
gui.Window.Position = UDim2.fromOffset(836, 470)
for _, name in { "Overview", "Perks", "Rebirth" } do
	window[name].Press.Activated:Fire()
	__dump(gui, 1672, 941)
end
if __failed then
	error("progress flow failed")
end
