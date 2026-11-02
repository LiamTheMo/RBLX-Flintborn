-- The Play window on a phone held sideways (844 × 390, touch only, the top bar
-- 58 px down), fitted by Kit.Scale.Window as in game (it fills the screen for
-- readability, ARCHITECTURE §1.1), with the mockup's sample data. Page 2: a
-- tall phone at 2000 × 924 (the owner's test device), also touch only. Pages
-- 3 and 4: parties of 3 and 8 at 844 × 390 (every member shows at once).
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")
local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local PlayModel = require(ReplicatedStorage.Shared.UI.PlayModel)
local PlayWindow = require(Client.Hud.Screens.PlayWindow)

local W, H = 844, 390
workspace.CurrentCamera.ViewportSize = Vector2.new(W, H)
UserInputService.TouchEnabled = true
UserInputService.KeyboardEnabled = false
-- The last input was a touch (Kit.Input: no keyboard hotkey badges).
UserInputService.GetLastInputType = function()
	return Enum.UserInputType.Touch
end

local preview = {
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
local function party(n: number)
	local rows = {}
	for i = 1, n do
		table.insert(rows, { userId = i, name = NAMES[i], level = 7 + i, leader = i == 1 })
	end
	return rows
end

local function report(ok: boolean, text: string)
	print(("  %s %s"):format(if ok then "ok" else "FAIL", text))
	assert(ok, text)
end

-- Every member in one row of tiles inside the column, square headshots, no
-- scrolling list and no clipping frame; names at the phone text floor or more.
local function checkParty(window, rows)
	local scrolls = 0
	for _, object in window.screen.gui:GetDescendants() do
		if object:IsA("ScrollingFrame") then
			scrolls += 1
		end
	end
	local section = window.party
	local tiles, inside, square, clips, smallest = 0, true, true, 0, math.huge
	for _, tile in section:GetChildren() do
		if tile:IsA("Frame") and tile.Name:match("^Member") then
			tiles += 1
			local x, w = tile.Position.X.Offset, tile.Size.X.Offset
			inside = inside and x >= 0 and x + w <= section.Size.X.Offset
			for _, child in tile:GetDescendants() do
				if child:IsA("GuiObject") and child.ClipsDescendants then
					clips += 1
				end
				if child:IsA("TextLabel") and child.Text ~= "" then
					smallest = math.min(smallest, child.TextSize)
				end
			end
			local portrait = tile:FindFirstChild("Portrait")
			square = square and portrait ~= nil and portrait.Size.X.Offset == portrait.Size.Y.Offset
		end
	end
	local k = window.screen.scale.Scale
	report(scrolls == 0, "the window has no scrolling list")
	report(clips == 0, "no clipping frame cuts the party tiles")
	report(tiles == #rows, ("every member has a tile (%d of %d)"):format(tiles, #rows))
	report(inside, "every tile lies inside the party column")
	report(square, "every headshot is square")
	report(smallest * k >= 8.95, ("party text at %.1f screen px or more (9 px floor)"):format(smallest * k))
end

local function page(w: number, h: number, rows)
	workspace.CurrentCamera.ViewportSize = Vector2.new(w, h)
	local window = PlayWindow.new({})
	local details = PlayModel.WorldRows()
	table.insert(details, PlayModel.CarryingRow(preview))
	window:SetDetails(details)
	rows = rows or { { userId = 1, name = "LiamTheMo", level = 12, leader = true } }
	window:SetParty(rows)
	window:SetLoadout(PlayModel.LoadoutHotbar(preview))
	window:SetMode("solo")
	window.screen:Watch()
	window:Open()
	print(("play_phone %d × %d: window scale %.3f, %d member(s)"):format(w, h, window.screen.scale.Scale, #rows))
	checkParty(window, rows)
	__dump(Players.LocalPlayer.PlayerGui, w, h)
	window:Destroy()
end

page(W, H)
page(2000, 924)
page(W, H, party(3))
page(W, H, party(8))
