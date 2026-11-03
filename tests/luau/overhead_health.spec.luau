-- Overhead health bars (docs/ui/HudScreen.md "Overhead health bars"): which
-- characters show one, how full it is, and when it lingers, fades and hides.

local Shared = game:GetService("ReplicatedStorage").Shared
local GameConstants = require(Shared.GameConstants)
local OverheadHealthModel = require(Shared.UI.OverheadHealthModel)

local function mode(state)
	return OverheadHealthModel.Mode(state)
end

test("a bar shows only while another player is below full health", function()
	expectEq(mode({ health = 100, maxHealth = 100 }), "full", "full health: no bar")
	expectEq(mode({ health = 72, maxHealth = 100 }), "hurt", "hurt")
	expectEq(mode({ health = 1, maxHealth = 100 }), "hurt", "nearly dead is still hurt")
	expectEq(mode({ health = 99.4, maxHealth = 100 }), "full", "reads 100/100 on their HUD: no bar")
	expectEq(mode({ health = 98.9, maxHealth = 100 }), "hurt", "reads 99/100: a bar")
	expectEq(mode({ health = 150, maxHealth = 150 }), "full", "a raised max at full")
	expectEq(mode({ health = 100, maxHealth = 150 }), "hurt", "below a raised max")
	expectEq(mode({ health = 50, maxHealth = 0 }), "hurt", "a missing max falls back to 100")
end)

test("dead, own and switched-off characters have no bar", function()
	expectEq(mode({ health = 0, maxHealth = 100 }), "off", "dead")
	expectEq(mode({ health = -3, maxHealth = 100 }), "off", "below zero")
	expectEq(mode({ health = 0 / 0, maxHealth = 100 }), "off", "NaN")
	expectEq(mode({ health = nil, maxHealth = 100 }), "off", "no humanoid")
	expectEq(OverheadHealthModel.SHOW_OWN, false, "your own bar is hidden by default")
	expectEq(mode({ health = 40, maxHealth = 100, isLocal = true }), "off", "your own character")
	expectEq(mode({ health = 40, maxHealth = 100, enabled = false }), "off", "Show Health Bars off")
	expectEq(mode({ health = 40, maxHealth = 100, enabled = nil }), "hurt", "the setting defaults to on")
end)

test("a downed player shows the downed pool", function()
	expectEq(mode({ health = 1, maxHealth = 100, downed = true }), "downed", "downed at 1 HP")
	expectEq(mode({ health = 0, maxHealth = 100, downed = true }), "off", "finished off: no bar")
	expectEq(mode({ health = 1, maxHealth = 100, downed = true, enabled = false }), "off", "setting off wins")
	local pool = GameConstants.DOWNED_HEALTH
	expectNear(OverheadHealthModel.Fraction("downed", 1, 100, pool / 2), 0.5, 1e-9, "half the pool")
	expectEq(OverheadHealthModel.Fraction("downed", 1, 100, nil), 1, "pool not replicated yet: full")
	expectEq(OverheadHealthModel.Fraction("downed", 1, 100, pool * 3), 1, "clamped")
	expectEq(OverheadHealthModel.FILLS.downed ~= OverheadHealthModel.FILLS.hurt, true, "downed reads apart")
end)

test("the bar's fraction", function()
	expectNear(OverheadHealthModel.Fraction("hurt", 25, 100), 0.25, 1e-9, "hurt")
	expectNear(OverheadHealthModel.Fraction("hurt", 60, 120), 0.5, 1e-9, "a raised max")
	expectEq(OverheadHealthModel.Fraction("full", 100, 100), 1, "full while it lingers")
	expectEq(OverheadHealthModel.Fraction("off", 50, 100), 0, "off")
end)

test("show, linger after healing, hide at once", function()
	local plan = OverheadHealthModel.Plan
	expectEq(plan("hurt", false), "show", "first hit shows it")
	expectEq(plan("hurt", true), "show", "a shown bar updates (and cancels a fade)")
	expectEq(plan("downed", true), "show", "downed shows")
	expectEq(plan("full", true), "linger", "healed to full: lingers, then fades")
	expectEq(plan("full", false), "none", "full and hidden stays hidden")
	expectEq(plan("off", true), "hide", "death or the setting hides at once")
	expectEq(plan("off", false), "none", "nothing to hide")
	expectEq(OverheadHealthModel.LINGER_SECONDS > 0, true, "a moment at full before the fade")
	expectEq(OverheadHealthModel.LINGER_SECONDS <= 3, true, "but only a moment")
end)

test("size, scale and placement", function()
	expectEq(OverheadHealthModel.Scale(1), 1, "desktop HUD scale")
	expectEq(OverheadHealthModel.Scale(0.42), OverheadHealthModel.MIN_SCALE, "phones keep a readable bar")
	expectEq(OverheadHealthModel.Scale(3), OverheadHealthModel.MAX_SCALE, "never huge")
	expectEq(OverheadHealthModel.Scale(nil), 1, "no scale yet")
	local size = OverheadHealthModel.Size()
	local bar, label = OverheadHealthModel.Rects()
	expectEq(bar[3], size[1], "the bar spans the billboard")
	expectEq(bar[2] >= label[2] + label[4], true, "the Downed line sits over the bar")
	expectEq(size[2] - (bar[2] + bar[4]), OverheadHealthModel.LIFT, "the lift under the bar")
	-- The bar and the Downed line stay at least 9 screen px high on a phone.
	expectEq(bar[4] * OverheadHealthModel.MIN_SCALE >= 9, true, "bar tall enough on phones")
	expectEq(
		OverheadHealthModel.LABEL_SIZE * OverheadHealthModel.MIN_SCALE >= 9,
		true,
		"the Downed line at the 9 px floor"
	)
	expectNear(OverheadHealthModel.StudsOffset(1.2), 0.6 + OverheadHealthModel.STUDS_ABOVE_HEAD, 1e-9, "head top")
	expectNear(OverheadHealthModel.StudsOffset(nil), 0.6 + OverheadHealthModel.STUDS_ABOVE_HEAD, 1e-9, "default head")
	expectEq(OverheadHealthModel.MAX_DISTANCE >= 80 and OverheadHealthModel.MAX_DISTANCE <= 120, true, "draw range")
end)
