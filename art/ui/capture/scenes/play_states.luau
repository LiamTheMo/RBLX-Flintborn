-- Every state of the Play window, forced through DebugState and the window's
-- setters, at the mockup's place over the lobby HUD mockup:
--
--   1 PLAY hover            2 PLAY pressed          3 PLAY busy (deploying)
--   4 PLAY disabled while the teleport runs, with the game-update notice
--   5 empty loadout         6 preview not read yet, a full party (8, scrolls)
--   7 member: READY         8 member: NOT READY     9 close button hover
--
-- It also prints the gamepad order (default selection and neighbours).

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local PlayModel = require(ReplicatedStorage.Shared.UI.PlayModel)
local PlayWindow = require(Client.Hud.Screens.PlayWindow)

local W, H = 1672, 941
local SAMPLE = {
	{ catalogId = "StoneAxe" },
	{ catalogId = "StoneSpear" },
	{ catalogId = "BasicMedicine", quantity = 3 },
}
local NAMES =
	{ "LiamTheMo", "ForestRanger", "StoneSeeker", "RiverFox", "AshWalker", "MossBeard", "FlintSpark", "TideRunner" }

-- A party of `n` (the first `readyCount` ready) led by `leader`, ordered as
-- PlayController orders it (PlayModel.Members: leader first), with levels.
local function members(n, readyCount, leader)
	local list = {}
	for i = 1, n do
		table.insert(list, { userId = i, name = NAMES[i], ready = i <= readyCount })
	end
	local view = { party = { leader = leader, members = list } }
	if n == 1 then
		view = { party = nil, ready = readyCount > 0 }
	end
	local rows = PlayModel.Members(view, { userId = 1, name = NAMES[1] })
	for _, row in rows do
		row.level = if row.userId == 1 then 12 else 8 + row.userId
	end
	return rows
end

local function page(opts)
	local window = PlayWindow.new({})
	local preview = if opts.preview == "none" then nil else (opts.preview or SAMPLE)
	local details = PlayModel.WorldRows()
	table.insert(details, PlayModel.CarryingRow(preview))
	window:SetDetails(details)
	window:SetParty(opts.party or members(1, 0, 1), opts.party ~= nil)
	window:SetLoadout(PlayModel.LoadoutHotbar(preview))
	window:SetMode(opts.mode or "solo", opts.ready)
	window:SetStatus(opts.status)
	if opts.setup then
		opts.setup(window)
	end
	window:Open()
	window.screen.holder.Position = UDim2.fromOffset(309 + PlayWindow.SIZE[1] / 2, 127 + PlayWindow.SIZE[2] / 2)
	window.screen.scale.Scale = 1
	if opts.check then
		opts.check(window)
	end
	__dump(Players.LocalPlayer.PlayerGui, W, H, { background = "art/reference/ui/lobby/01_hud.png" })
	window:Destroy()
end

local function force(state)
	return function(window)
		window.play.root:SetAttribute("DebugState", state)
	end
end

page({ setup = force("hover") })
page({ setup = force("pressed") })
page({
	setup = function(window)
		window:SetBusy(true)
	end,
	status = "Deploying…",
})
page({
	setup = function(window)
		window:SetEnabled(false)
	end,
	status = "Game update: your items were saved and return on your next Play.",
})
page({ preview = {} })
page({ preview = "none", party = members(8, 5, 1), mode = "leader" })
page({ party = members(3, 1, 2), mode = "member", ready = false, status = PlayModel.MEMBER_CAPTION })
page({ party = members(3, 2, 2), mode = "member", ready = true, status = PlayModel.MEMBER_READY_CAPTION })
page({
	setup = function(window)
		window.close.root:SetAttribute("DebugState", "hover")
	end,
	check = function(window)
		local function name(object)
			return if object then object.Parent.Name else "none"
		end
		local hit = window.play.control.hit
		print("gamepad: default " .. name(window.screen.defaultSelection))
		print("gamepad: PLAY up -> " .. name(hit.NextSelectionUp))
		print("gamepad: close down -> " .. name(window.close.control.hit.NextSelectionDown))
	end,
})
