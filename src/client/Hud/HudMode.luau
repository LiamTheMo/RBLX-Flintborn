-- One switch for "the kit HUD is in charge" (GDD §11, §25.4). The world HUD
-- (HudController) builds only in the world place and only when the layout
-- loads; controllers ask it before showing a kit display the HUD would
-- duplicate (the extraction and event lists, the level bar). There is no older
-- UI behind it: when the layout is missing HudController logs the error and the
-- run has no HUD.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local PlaceConfig = require(ReplicatedStorage.Shared.Config.PlaceConfig)
local Signal = require(ReplicatedStorage.Shared.Core.Signal)
local Layout = require(script.Parent.Layout)

local HudMode = {}

-- Fires (visible) when the new HUD shows or hides (it shows only during a run).
HudMode.VisibilityChanged = Signal.new()

local visible = false
local lobbyFailed = false

function HudMode.WorldHud(): boolean
	return PlaceConfig.IsWorld() and Layout.Get() ~= nil
end

-- The lobby's counterpart: true in the lobby place unless the lobby HUD failed
-- to build (LobbyHudController logs why). Then the kit's own ⚙ button, Coins and
-- Gems pills and level bar, which the lobby HUD otherwise replaces, show
-- instead (SettingsController, WalletController, ProgressionController).
function HudMode.ReplacesLobby(): boolean
	return PlaceConfig.IsLobby() and not lobbyFailed
end

-- LobbyHudController calls this when the lobby HUD fails to build, so the
-- controllers that start after it show their own kit pieces instead.
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
