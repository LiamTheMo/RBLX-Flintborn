-- Overhead health bars (docs/ui/HudScreen.md "Overhead health bars"): the pure
-- rules behind the small bar over a hurt player's head that every player sees.
-- Which look a character's bar has, how full it is, when it shows, lingers and
-- hides, and its sizes. The client module (src/client/Hud/OverheadHealth.luau)
-- draws it; specs check these rules.
--
-- Modes:
--   "hurt"   alive and below full health: the red health fill
--   "downed" downed (the player's Downed attribute): the downed pool
--            (DownedHealth of GameConstants.DOWNED_HEALTH) in the orange fill,
--            with a "Downed" line over it
--   "full"   alive at full health: no bar (one that was showing lingers, then fades)
--   "off"    no bar at all, at once: dead, your own character (SHOW_OWN), or the
--            Show Health Bars setting off

local GameConstants = require(script.Parent.Parent.GameConstants)
local HudModel = require(script.Parent.HudModel)

local OverheadHealthModel = {}

-- Your own bar is the HUD's health row already, so it stays hidden.
OverheadHealthModel.SHOW_OWN = false
-- Seconds a bar stays at full after healing before it fades out.
OverheadHealthModel.LINGER_SECONDS = 1.2
-- Studs from the camera beyond which a bar is not drawn (BillboardGui.MaxDistance).
OverheadHealthModel.MAX_DISTANCE = 100
-- The bar in design px (Kit.Bar, health fill on the track; just the bar, kept
-- small so it takes little of the screen: owner, 2026-11-03) and the "Downed"
-- line over it; LIFT is clear space under the bar (px, so it holds at any range).
-- 12 px tall is the thinnest that stays 9 px on a phone (MIN_SCALE).
OverheadHealthModel.BAR = { 72, 12 }
OverheadHealthModel.LABEL_H = 18
OverheadHealthModel.LABEL_SIZE = 15
OverheadHealthModel.LABEL_GAP = 1
OverheadHealthModel.LIFT = 14
OverheadHealthModel.DOWNED_TEXT = "Downed"
-- The bar's foot sits this many studs over the top of the head (above the name tag).
OverheadHealthModel.STUDS_ABOVE_HEAD = 1.5
-- Design px to screen px: the HUD's scale, kept between these so the bar stays
-- readable on phones (HUD scale about 0.4) and never grows huge on big screens.
OverheadHealthModel.MIN_SCALE = 0.75
OverheadHealthModel.MAX_SCALE = 1.15
-- Kit.Bar fills for each look.
OverheadHealthModel.FILLS = { hurt = "health", downed = "food" }

export type Mode = "hurt" | "downed" | "full" | "off"

export type State = {
	health: number?,
	maxHealth: number?,
	downed: boolean?,
	isLocal: boolean?,
	-- The Show Health Bars setting (nil reads as on, its default).
	enabled: boolean?,
}

-- The look a character's bar has now.
function OverheadHealthModel.Mode(state: State): Mode
	if state.enabled == false then
		return "off"
	end
	if state.isLocal and not OverheadHealthModel.SHOW_OWN then
		return "off"
	end
	local health = state.health
	if type(health) ~= "number" or health ~= health or health <= 0 then
		return "off"
	end
	if state.downed then
		return "downed"
	end
	-- The same whole number the HUD's health row shows (rounded up), so a bar
	-- never shows for a player whose own HUD reads full.
	local maxHealth = if type(state.maxHealth) == "number" and state.maxHealth > 0 then state.maxHealth else 100
	local _, shown = HudModel.Health(health, maxHealth)
	return if shown < math.ceil(maxHealth) then "hurt" else "full"
end

-- How full the bar is in `mode`: the health fraction, the downed pool's share of
-- GameConstants.DOWNED_HEALTH (full while unknown), or 1 at full health.
function OverheadHealthModel.Fraction(mode: Mode, health: number?, maxHealth: number?, downedHealth: number?): number
	if mode == "downed" then
		if type(downedHealth) ~= "number" then
			return 1
		end
		return HudModel.Clamp01(downedHealth / GameConstants.DOWNED_HEALTH)
	elseif mode == "hurt" then
		return (HudModel.Health(health, maxHealth))
	elseif mode == "full" then
		return 1
	end
	return 0
end

-- What a bar does when its mode becomes `mode` while it is `shown` (drawn now,
-- lingering or fading included):
--   "show"   draw it now (cancelling a linger or a fade)
--   "linger" healed to full: keep it LINGER_SECONDS, then fade it out
--   "hide"   remove it at once
--   "none"   nothing to do (it is hidden and stays hidden)
function OverheadHealthModel.Plan(mode: Mode, shown: boolean): "show" | "linger" | "hide" | "none"
	if mode == "hurt" or mode == "downed" then
		return "show"
	elseif mode == "full" then
		return if shown then "linger" else "none"
	end
	return if shown then "hide" else "none"
end

-- Design px to screen px for a HUD scale.
function OverheadHealthModel.Scale(hudScale: number?): number
	local k = if type(hudScale) == "number" and hudScale == hudScale then hudScale else 1
	return math.clamp(k, OverheadHealthModel.MIN_SCALE, OverheadHealthModel.MAX_SCALE)
end

-- The billboard's design size {w, h}: the "Downed" line, the bar, the lift.
function OverheadHealthModel.Size(): { number }
	local m = OverheadHealthModel
	return { m.BAR[1], m.LABEL_H + m.LABEL_GAP + m.BAR[2] + m.LIFT }
end

-- The bar's rect {x, y, w, h} and the "Downed" line's in the billboard's design px.
function OverheadHealthModel.Rects(): ({ number }, { number })
	local m = OverheadHealthModel
	local barY = m.LABEL_H + m.LABEL_GAP
	return { 0, barY, m.BAR[1], m.BAR[2] }, { 0, 0, m.BAR[1], m.LABEL_H }
end

-- Studs from the head's centre to the billboard's foot.
function OverheadHealthModel.StudsOffset(headHeight: number?): number
	local h = if type(headHeight) == "number" and headHeight > 0 then headHeight else 1.2
	return h / 2 + OverheadHealthModel.STUDS_ABOVE_HEAD
end

return OverheadHealthModel
