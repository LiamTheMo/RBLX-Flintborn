-- One switch for "the new in-world HUD is in charge" (GDD §11, §25.4). Older
-- controllers ask it before showing the visuals the HUD replaces (survival bars,
-- hotbar strip, XP bar, compass text, extraction and event lists). It is true only
-- in the world place and only when the layout loads, so a place published without
-- the HUD's JSON keeps the old visuals instead of showing nothing.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Signal = require(ReplicatedStorage.Shared.Core.Signal)
local Layout = require(script.Parent.Layout)

local HudMode = {}

-- Fires (visible) when the new HUD shows or hides (it shows only during a run).
HudMode.VisibilityChanged = Signal.new()

local visible = false

function HudMode.ReplacesLegacy(): boolean
	return PlaceConfig.IsWorld() and Layout.Get() ~= nil
end

-- True while the new HUD is on screen. Outside a run (world menu, protected,
-- dead) it is hidden, and controllers show their own minimal displays instead.
function HudMode.IsVisible(): boolean
	return visible
end

-- HudController reports its visibility here.
function HudMode.SetVisible(value: boolean)
	if value ~= visible then
		visible = value
		HudMode.VisibilityChanged:Fire(value)
	end
end

return HudMode
