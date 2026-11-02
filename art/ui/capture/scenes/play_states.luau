-- Every state of the Play window, forced through DebugState and the window's
-- setters, at the mockup's place over the lobby HUD mockup:
--
--   1 PLAY hover            2 PLAY pressed          3 PLAY busy (deploying)
--   4 PLAY disabled while the teleport runs, with the game-update notice
--   5 empty loadout         6 preview not read yet, a full party (8 tiles,
--                             one with a 20-character name)
--   7 member: PLAY disabled with the leader caption   8 close button hover
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
local NAMES = {
	"LiamTheMo",
	"ForestRanger",
	"StoneSeeker",
	"RiverFox",
	"AshWalker",
	"MossBeard",
	"FlintSparkTheBrave20",
	"TideRunner",
}

-- The party section shows every member at once: no scrolling list, no
-- clipping frame, every tile inside the column, square headshots.
local function checkParty(window, rows)
	local section = window.party
	local scrolls, clips = 0, 0
	for _, object in window.screen.gui:GetDescendants() do
		if object:IsA("ScrollingFrame") then
			scrolls += 1
		end
	end
	local object = section
	while object and object ~= window.screen.gui do
		if object:IsA("GuiObject") and object.ClipsDescendants then
			clips += 1
		end
		object = object.Parent
	end
	local tiles, inside, square = 0, true, true
	local columnW = section.Size.X.Offset
	for _, tile in section:GetChildren() do
		if tile:IsA("Frame") and tile.Name:match("^Member") then
			tiles += 1
			local x, w = tile.Position.X.Offset, tile.Size.X.Offset
			local y, h = tile.Position.Y.Offset, tile.Size.Y.Offset
			inside = inside and x >= 0 and x + w <= columnW and y >= 0 and y + h <= section.Size.Y.Offset
			for _, child in tile:GetDescendants() do
				if child:IsA("GuiObject") and child.ClipsDescendants then
					clips += 1
				end
			end
			local portrait = tile:FindFirstChild("Portrait")
			square = square and portrait ~= nil and portrait.Size.X.Offset == portrait.Size.Y.Offset
		end
	end
	local function report(ok, text)
		print(("  %s %s"):format(if ok then "ok" else "FAIL", text))
		assert(ok, text)
	end
	report(scrolls == 0, "the window has no scrolling list")
	report(clips == 0, "no clipping frame holds or cuts the party tiles")
	report(tiles == #rows, ("every member has a tile (%d of %d)"):format(tiles, #rows))
	report(inside, "every tile lies inside the party column")
	report(square, "every headshot is square")
end

-- A party of `n` led by `leader`, ordered as PlayController orders it
-- (PlayModel.Members: leader first), with levels.
local function members(n, leader)
	local list = {}
	for i = 1, n do
		table.insert(list, { userId = i, name = NAMES[i] })
	end
	local view = { party = { leader = leader, members = list } }
	if n == 1 then
		view = { party = nil }
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
	window:SetParty(opts.party or members(1, 1))
	window:SetLoadout(PlayModel.LoadoutHotbar(preview))
	window:SetMode(opts.mode or "solo")
	window:SetStatus(opts.status)
	if opts.setup then
		opts.setup(window)
	end
	window:Open()
	window.screen.holder.Position = UDim2.fromOffset(243 + PlayWindow.SIZE[1] / 2, 150 + PlayWindow.SIZE[2] / 2)
	window.screen.scale.Scale = 1
	if opts.check then
		opts.check(window)
	end
	checkParty(window, opts.party or members(1, 1))
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
page({ preview = "none", party = members(8, 1), mode = "leader" })
page({ party = members(3, 2), mode = "member", status = PlayModel.MEMBER_CAPTION })
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
