-- Drives SpriteLoader's paced image queue headlessly (the capture runtime's
-- clock never runs, so ticks are called by hand): images on screen go first, a
-- few per tick; a hidden screen's art follows only when nothing on screen
-- waits; an image on screen that has not loaded is asked for again.
__FlintbornCapture = false
local Players = game:GetService("Players")
local Client = game:GetService("StarterPlayer").StarterPlayerScripts.Client
local SpriteLoader = require(Client.Hud.SpriteLoader)
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
local function make(parent, count)
	local list = {}
	for index = 1, count do
		local label = Instance.new("ImageLabel")
		label.Parent = parent
		SpriteLoader.Assign(label, "rbxassetid://" .. (1000 + index))
		table.insert(list, label)
	end
	return list
end
local onScreen = make(shownGui, 10)
local hidden = make(hiddenGui, 5)
local function given(list)
	local count = 0
	for _, label in list do
		if label.Image ~= "" then
			count += 1
		end
	end
	return count
end
check(given(onScreen) <= 1 and given(hidden) == 0, "images start empty (the pump's first tick may give one)")
SpriteLoader._tick()
-- The pump's first tick may already have run; count against the per-tick cap.
local first = given(onScreen)
check(first >= SpriteLoader.PER_TICK and first <= SpriteLoader.PER_TICK * 2, "a few on-screen images per tick")
check(given(hidden) == 0, "hidden art waits while on-screen images do")
SpriteLoader._tick()
SpriteLoader._tick()
check(given(onScreen) == 10, "every on-screen image is given out")
local before = given(hidden)
SpriteLoader._tick()
check(given(hidden) > before and given(hidden) <= before + SpriteLoader.IDLE_PER_TICK, "then hidden art, slowly")
-- A shown image that has not loaded is asked for again once its wait is over.
local label = onScreen[1]
label.IsLoaded = false
local entry = SpriteLoader._labels[label]
entry.due = 0
SpriteLoader._tick(true)
check(entry.tries == 1 and label.Image == entry.id, "a stuck image is asked for again")
check(entry.due > os.clock(), "and waits before asking again")
-- A loaded one is left alone.
local other = onScreen[2]
SpriteLoader._labels[other].due = 0
other.IsLoaded = true
SpriteLoader._tick(true)
check(SpriteLoader._labels[other].tries == 0, "a loaded image is not asked for again")
-- Something else setting the image first wins.
local mine = Instance.new("ImageLabel")
mine.Parent = shownGui
SpriteLoader.Assign(mine, "rbxassetid://7")
mine.Image = "rbxassetid://8"
SpriteLoader._tick()
check(mine.Image == "rbxassetid://8", "an image set elsewhere is kept")
print(__failed and "FLOW FAILED" or "FLOW OK")
-- The capture tool expects a picture; this one only proves the queue.
__dump(shownGui, 64, 64)
if __failed then
	error("sprite loader flow failed")
end
