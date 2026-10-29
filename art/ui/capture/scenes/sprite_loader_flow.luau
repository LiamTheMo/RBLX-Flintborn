-- Drives SpriteLoader's HUD image queue headlessly (the capture runtime's clock
-- never runs, so ticks are called by hand): one image is fetched at a time,
-- images on screen first; a hidden screen's art follows; a failed fetch waits
-- and is asked again under the other spelling, and its labels get the image
-- anyway after a few failures; labels are held strongly and let go on Destroy.
__FlintbornCapture = false
__preloadStatus = {}
local Players = game:GetService("Players")
local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local SpriteLoader = require(Client.Hud.SpriteLoader)
SpriteLoader.PREFETCH_HIDDEN = true
local player = Players.LocalPlayer
local function check(cond, msg)
	print((cond and "  ok " or "  FAIL ") .. msg)
	if not cond then
		__failed = true
	end
end
local function gui(name, enabled)
	local screen = Instance.new("ScreenGui")
	screen.Name = name
	screen.Enabled = enabled
	screen.Parent = player.PlayerGui
	return screen
end
local shownGui, hiddenGui = gui("Shown", true), gui("Hidden", false)
local function make(parent, count, base)
	local list = {}
	for index = 1, count do
		local label = Instance.new("ImageLabel")
		label.Parent = parent
		SpriteLoader.Assign(label, "rbxassetid://" .. (base + index))
		table.insert(list, label)
	end
	return list
end
local hidden = make(hiddenGui, 3, 2000)
local onScreen = make(shownGui, 5, 1000)
local function given(list)
	local count = 0
	for _, label in list do
		if label.Image ~= "" then
			count += 1
		end
	end
	return count
end
-- The pump's first tick ran inside the first Assign (a hidden label then).
local start = given(onScreen) + given(hidden)
check(start <= 1, "images start empty")
SpriteLoader._tick()
check(given(onScreen) == 1 and given(hidden) <= 1, "one image is fetched per tick, on-screen first")
for _ = 1, 4 do
	SpriteLoader._tick()
end
check(given(onScreen) == 5, "every on-screen image is fetched and handed out")
for _ = 1, 3 do
	SpriteLoader._tick()
end
check(given(hidden) == 3, "then the hidden screen's art")
-- A second label of a loaded image gets it at once.
local again = Instance.new("ImageLabel")
again.Parent = shownGui
SpriteLoader.Assign(again, "rbxassetid://1001")
check(again.Image == "rbxassetid://1001", "a loaded image is given at once")
-- A failed fetch: the label waits, the image is asked again under its URL later.
__preloadStatus["rbxassetid://3001"] = "AssetFetchStatus.Failure"
local stuck = Instance.new("ImageLabel")
stuck.Parent = shownGui
SpriteLoader.Assign(stuck, "rbxassetid://3001")
SpriteLoader._tick()
local image = SpriteLoader._images["rbxassetid://3001"]
check(image.state == "failed" and image.tries == 1 and stuck.Image == "", "a failed fetch leaves the label waiting")
check(image.content == "http://www.roblox.com/asset/?id=3001", "and is asked again under the asset URL")
SpriteLoader._tick()
check(image.tries == 1, "not before its wait is over")
-- After SHOW_AFTER failures the label is given the image anyway.
__preloadStatus["http://www.roblox.com/asset/?id=3001"] = "AssetFetchStatus.Failure"
for _ = 2, SpriteLoader.SHOW_AFTER do
	image.retryAt = 0
	SpriteLoader._tick()
end
check(image.tries == SpriteLoader.SHOW_AFTER and stuck.Image ~= "", "after a few failures the label tries on its own")
-- An image set elsewhere first wins.
local mine = Instance.new("ImageLabel")
mine.Parent = shownGui
SpriteLoader.Assign(mine, "rbxassetid://7")
mine.Image = "rbxassetid://8"
SpriteLoader._tick()
check(mine.Image == "rbxassetid://8", "an image set elsewhere is kept")
-- Held strongly (a weak table lost live labels in game) and let go on Destroy.
check(getmetatable(SpriteLoader._labels) == nil, "labels are held strongly")
local gone = Instance.new("ImageLabel")
gone.Parent = shownGui
SpriteLoader.Assign(gone, "rbxassetid://9")
gone:Destroy()
check(SpriteLoader._labels[gone] == nil, "a destroyed label is let go")
local counts, _, lines = SpriteLoader.Summary(5)
check(counts.labels >= 8 and #lines <= 5, "the diagnostics summary counts labels and caps its lines")
print(__failed and "FLOW FAILED" or "FLOW OK")
-- The capture tool expects a picture; this one only proves the queue.
__dump(shownGui, 64, 64)
if __failed then
	error("sprite loader flow failed")
end
