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
local lobbyFailed = false

function HudMode.ReplacesLegacy(): boolean
	return PlaceConfig.IsWorld() and Layout.Get() ~= nil
end

-- The lobby's counterpart: true in the lobby place unless the lobby HUD failed to
-- build. Then LobbyHudController draws the profile, currency, party, navigation
-- and Play entry, and the older lobby panel, wallet label, navigation bar, XP bar
-- and settings button stay hidden. HudLayout's lobby section is not consulted:
-- the lobby HUD brings its own layout, and when it cannot build (for example a
-- missing layout) it calls SetLobbyFailed and LobbyController builds the fallback
-- panel, so the lobby is never left without Deploy.
function HudMode.ReplacesLobby(): boolean
	return PlaceConfig.IsLobby() and not lobbyFailed
end

-- LobbyHudController calls this when the lobby HUD fails to build, so the
-- controllers that start after it show their own lobby visuals instead.
function HudMode.SetLobbyFailed()
	lobbyFailed = true
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
