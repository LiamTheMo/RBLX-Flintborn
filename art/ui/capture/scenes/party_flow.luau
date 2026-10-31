-- Drives the Party window through PartyController headlessly with real events:
-- the server's party views arrive through the PartyChanged remote, presses go
-- through the buttons, and the PartyAction remote is mocked (it records each
-- call and broadcasts the next view, as PartyService does). A handler can park
-- to stand for a slow server, so the pending states are visible. Prints one
-- line per check and captures three moments.
--
--   python3 art/ui/capture/capture.py party_flow

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
workspace:SetAttribute("FlintbornPlaceRole", "Lobby")
local NOW = 1_700_000_000
workspace.GetServerTimeNow = function()
	return NOW
end

local folder = Instance.new("Folder")
folder.Name = "FlintbornRemotes"
folder.Parent = ReplicatedStorage
local partyChanged = Instance.new("RemoteEvent")
partyChanged.Name = "PartyChanged"
partyChanged.Parent = folder
local function broadcast(view)
	partyChanged.OnClientEvent:Fire(view)
end

local calls = {}
-- What the next PartyAction answers: a function(action, argument) -> ok, reason.
local server = nil
-- A parked request (the server has not answered yet).
local parked = nil
local function park()
	parked = coroutine.running()
	coroutine.yield()
end
local function resume()
	local thread = parked
	parked = nil
	coroutine.resume(thread)
end

local handlers = {
	DeployPreview = function()
		return {}
	end,
	PartyAction = function(action, argument)
		table.insert(calls, { action, argument })
		if server then
			return server(action, argument)
		end
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

local player = Players.LocalPlayer
player:SetAttribute("Level", 12)
local others = {}
for _, entry in { { 2, "ForestRanger", 15 }, { 3, "SunnyVale", 8 }, { 4, "Emberwick", 21 } } do
	local other = Instance.new("Player")
	other.Name = entry[2]
	other.DisplayName = entry[2]
	other.UserId = entry[1]
	other:SetAttribute("Level", entry[3])
	other.Parent = Players
	others[entry[1]] = other
end

local Controllers = game:GetService("StarterPlayer").StarterPlayerScripts.Client.Controllers
local LobbyController = require(Controllers.LobbyController)
local PartyController = require(Controllers.PartyController)
local PartyWindow = require(game:GetService("StarterPlayer").StarterPlayerScripts.Client.Hud.Screens.PartyWindow)

local failures = 0
local function check(cond, msg)
	print((cond and "  ok " or "  FAIL ") .. msg)
	if not cond then
		failures += 1
	end
end

local function view(party, extra)
	local v = { party = party, invites = {}, maxSize = 8 }
	for key, value in extra or {} do
		v[key] = value
	end
	return v
end

local function rowNames(window)
	local names = {}
	for _, component in window:Rows("invites") do
		if component.props and component.props.name and component.action then
			table.insert(names, component.props.name)
		end
	end
	return table.concat(names, ",")
end

local function inviteRow(window, name)
	for _, component in window:Rows("invites") do
		if component.props and component.props.name == name then
			return component
		end
	end
	return nil
end

local function detail(window, label)
	return window.detailRows[label].value.Text
end

local function dump()
	__dump(player.PlayerGui, 1672, 941, { background = "art/reference/ui/lobby/01_hud.png" })
end

local function place(window)
	window.screen.holder.Position = UDim2.fromOffset(
		PartyWindow.ORIGIN[1] + PartyWindow.SIZE[1] / 2,
		PartyWindow.ORIGIN[2] + PartyWindow.SIZE[2] / 2
	)
	window.screen.scale.Scale = 1
end

LobbyController.Start()
PartyController.Start()
check(not PartyController.IsOpen(), "closed until asked")
PartyController.Open("invite")
local window = PartyController.Window()
check(PartyController.IsOpen() and window.screen.gui.Enabled, "Open shows the window")
check(window.screen.gui.Name == "FlintbornParty" and window.screen.gui.DisplayOrder == 20, "window gui and layer")
check(window.partyHeader.count.Text == "1/8", "solo reads 1/8")
check(detail(window, "Created") == "—", "no party yet: Created reads —")
check(rowNames(window) == "Emberwick,ForestRanger,SunnyVale", "everyone else is invitable, sorted")
check(inviteRow(window, "ForestRanger").props.level == 15, "levels come from the Level attribute")
check(window.readyButton == nil and window.tally == nil, "no Ready toggle or tally (D24)")
local gui = window.screen.gui
check(gui:FindFirstChild("ReadiedStatus", true) == nil, "no Readied Status card")
local details = gui:FindFirstChild("PartyDetails", true)
check(details ~= nil and details.Size.Y.Offset == 448, "Party Details takes the right column")

-- Invite: the button waits for the server, then reads Invited from the view.
server = function(action, argument)
	park()
	broadcast(view({
		id = "p1",
		leader = 1,
		createdAt = NOW,
		members = { { userId = 1, name = "LiamTheMo" } },
		invited = { argument },
	}))
	return true
end
window.selectables["invites:player:2"].Activated:Fire()
check(calls[#calls][1] == "invite" and calls[#calls][2] == 2, "Invite sends PartyAction invite with the user id")
check(
	inviteRow(window, "ForestRanger").action.root:GetAttribute("KitState") == "busy",
	"the Invite button is busy while the server answers"
)
resume()
local forest = inviteRow(window, "ForestRanger").action
check(forest.text == "Invited" and forest.root:GetAttribute("KitState") == "disabled", "then Invited, disabled")
check(forest.root:GetAttribute("KitRole") == "button.secondary", "Invited is the paper button")
check(detail(window, "Created") == "Just now", "Created from createdAt")
place(window)
dump()

-- Search filters by name as typed.
window.search:SetText("sun")
window.props.onSearch("sun")
check(rowNames(window) == "SunnyVale", "search filters the list")
window.search:SetText("")
window.props.onSearch("")

-- A refused request shows a toast and leaves the state as the server has it.
server = function()
	return false, "PartyFull"
end
window.selectables["invites:player:3"].Activated:Fire()
check(inviteRow(window, "SunnyVale").action.text == "Invite", "a refusal leaves the row as it was")
local toasts = player.PlayerGui:FindFirstChild("KitToasts")
check(toasts ~= nil and #toasts:GetDescendants() > 0, "and explains it in a toast")

-- ForestRanger accepts: two members, Leave shows.
server = nil
broadcast(view({
	id = "p1",
	leader = 1,
	createdAt = NOW,
	members = { { userId = 1, name = "LiamTheMo" }, { userId = 2, name = "ForestRanger" } },
	invited = {},
}))
check(window.partyHeader.count.Text == "2/8" and detail(window, "Members") == "2 / 8", "counts follow the view")
check(window.leaveButton.root.Visible, "Leave Party shows in a party of two")
check(rowNames(window) == "Emberwick,SunnyVale", "members leave the invite list")
local leaderRow = window:Rows("members")[1]
check(
	leaderRow.row.badge == nil and leaderRow.row.content:FindFirstChild("Crown") ~= nil,
	"the leader has a crown, no tag"
)
check(window:Rows("members")[2].row.badge == nil, "members carry no Ready tag")

-- A player leaving the server drops out of the list.
others[3].Parent = nil
Players.PlayerRemoving:Fire(others[3])
check(rowNames(window) == "Emberwick", "a player who left the server is gone")

-- An invitation from another party arrives; accepting joins it as a member.
broadcast(view({
	id = "p1",
	leader = 1,
	createdAt = NOW,
	members = { { userId = 1, name = "LiamTheMo" }, { userId = 2, name = "ForestRanger" } },
	invited = {},
}, { invites = { { partyId = "p9", from = "Emberwick", fromUserId = 4 } } }))
check(window.selectables["invites:accept:p9"] ~= nil, "the invitation shows Accept")
check(window.selectables["invites:decline:p9"] ~= nil, "and a decline button")
place(window)
dump()
server = function(action, argument)
	broadcast(view({
		id = argument,
		leader = 4,
		createdAt = NOW - 300,
		members = { { userId = 4, name = "Emberwick" }, { userId = 1, name = "LiamTheMo" } },
		invited = {},
	}))
	return true
end
window.selectables["invites:accept:p9"].Activated:Fire()
check(calls[#calls][1] == "accept" and calls[#calls][2] == "p9", "Accept sends PartyAction accept with the party id")
check(detail(window, "Party Leader") == "Emberwick", "now in Emberwick's party")
check(window.window and window.data.members[1].userId == 4, "the leader is listed first")
check(window.inviteNote.root.Text == "Only the party leader can invite players.", "a member cannot invite")
check(window.search.root:GetAttribute("KitState") == "disabled", "and the search is greyed")
check(detail(window, "Created") == "5 min ago", "Created is relative to the server clock")

-- Leave asks first, then goes to the server.
server = function()
	broadcast(view(nil))
	return true
end
window.leaveButton.control:Activate()
local dialog = player.PlayerGui:FindFirstChild("KitDialog")
check(dialog ~= nil and dialog.Enabled, "Leave asks for confirmation")
local confirm = nil
for _, object in dialog:GetDescendants() do
	if object:GetAttribute("KitRole") == "button.primary" then
		confirm = object
	end
end
confirm.Hit.Activated:Fire()
check(calls[#calls][1] == "leave", "confirming sends PartyAction leave")
check(window.partyHeader.count.Text == "1/8" and not window.leaveButton.root.Visible, "solo again, no Leave")
place(window)
dump()

-- Rows update in place: redrawing the same data keeps every row.
local membersBefore, invitesBefore = window:Rows("members"), window:Rows("invites")
window:SetData(window.data)
local membersAfter, invitesAfter = window:Rows("members"), window:Rows("invites")
check(
	membersAfter[1] == membersBefore[1] and membersAfter[#membersAfter] == membersBefore[#membersBefore],
	"an unchanged member row is kept, not rebuilt"
)
check(invitesAfter[1] == invitesBefore[1], "an unchanged invite row is kept")

-- Close, Toggle and the leak check.
window.closeX.control:Activate()
check(not PartyController.IsOpen(), "the ✕ closes the window")
PartyController.Toggle()
check(PartyController.IsOpen(), "Toggle opens it")
PartyController.Toggle()
check(not PartyController.IsOpen(), "and closes it")
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

local instances, connections = leakCounts()
for _ = 1, 20 do
	PartyController.Open()
	PartyController.Toggle()
end
local instancesAfter, connectionsAfter = leakCounts()
check(instancesAfter == instances, ("open/close ×20 leaves %d descendants (%d)"):format(instances, instancesAfter))
check(
	connectionsAfter == connections,
	("open/close ×20 leaves %d connections (%d)"):format(connections, connectionsAfter)
)
print(("party_flow: %d failed"):format(failures))
