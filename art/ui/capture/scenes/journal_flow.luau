-- Drives JournalController headlessly: open, claim a finished quest, check what
-- reaches the server and that the list refreshes.
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local folder = Instance.new("Folder")
folder.Name = "FlintbornRemotes"
folder.Parent = ReplicatedStorage
local claimed = {}
local quests = {
	{
		id = "DailyExtract",
		name = "Extract once",
		tier = "Easy",
		action = "Extract",
		coins = 250,
		count = 1,
		needed = 1,
		claimed = false,
		repeats = "Daily",
	},
	{
		id = "DailyGather",
		name = "Gather 100 times",
		tier = "Easy",
		action = "Harvest",
		coins = 250,
		count = 10,
		needed = 100,
		claimed = false,
		repeats = "Daily",
	},
}
for _, name in { "QuestView", "QuestClaim" } do
	local remote = Instance.new("RemoteFunction")
	remote.Name = name
	remote.Parent = folder
	remote.InvokeServer = function(_, id)
		if name == "QuestView" then
			return quests
		end
		table.insert(claimed, id)
		for _, q in quests do
			if q.id == id then
				q.claimed = true
			end
		end
		return true
	end
end
local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local JournalController = require(Client.Controllers.JournalController)
local player = Players.LocalPlayer
JournalController.Start()
JournalController.Toggle()
local gui = player.PlayerGui:FindFirstChild("FlintbornJournal")
local function check(cond, msg)
	print((cond and "  ok " or "  FAIL ") .. msg)
	if not cond then
		__failed = true
	end
end
check(gui and gui.Enabled, "journal opens")
local window = gui.Window
check(window.Quests:FindFirstChild("DailyExtract") ~= nil, "quests listed")
window.Quests.DailyGather.Press.Activated:Fire()
window.Claim.Press.Activated:Fire()
check(#claimed == 0, "an unfinished quest cannot be claimed")
window.Quests.DailyExtract.Press.Activated:Fire()
window.Claim.Press.Activated:Fire()
check(#claimed == 1 and claimed[1] == "DailyExtract", "claim sends the quest id")
check(window.Claim:FindFirstChild("Text").Text == "CLAIMED", "card shows CLAIMED after refresh")
window.Daily.Press.Activated:Fire()
check(window.Quests:FindFirstChild("DailyExtract") ~= nil, "daily tab lists daily quests")
window.Once.Press.Activated:Fire()
check(window.Quests:FindFirstChild("DailyExtract") == nil, "main tab hides daily quests")
window.Close.Activated:Fire()
check(not gui.Enabled, "close hides the journal")
print(__failed and "FLOW FAILED" or "FLOW OK")
__dump(gui, 1672, 941)
if __failed then
	error("journal flow failed")
end
