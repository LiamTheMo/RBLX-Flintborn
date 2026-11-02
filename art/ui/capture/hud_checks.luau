-- Layout checks shared by the HUD capture scenes (bundled after the game's
-- modules): where the owner's HUD layout (ARCHITECTURE D28) puts each region,
-- and that no region overlaps another, leaves the screen, or meets Roblox's
-- own controls (the stand-ins __robloxChrome draws: the top-bar buttons and,
-- on touch, the jump button and the thumbstick). Rectangles are screen px
-- {x1, y1, x2, y2} (__rect). Every check prints "ok" or "FAIL"; a scene ends
-- with __hudChecksDone(name), which fails the scene when any check failed.

local hudFails = 0

function __hudCheck(scene: string, ok: boolean, message: string): boolean
	print(("  %s %s: %s"):format(if ok then "ok" else "FAIL", scene, message))
	if not ok then
		hudFails += 1
	end
	return ok
end

function __hudChecksDone(scene: string)
	if hudFails > 0 then
		error(("%s: %d layout check(s) failed"):format(scene, hudFails))
	end
end

function __fmtRect(r): string
	return ("x %d..%d, y %d..%d"):format(math.floor(r[1]), math.ceil(r[3]), math.floor(r[2]), math.ceil(r[4]))
end

-- A label's inked width in design px at its drawn size.
local function inkWidth(label): number
	if label == nil or label.Text == "" then
		return 0
	end
	local Kit = require(game:GetService("StarterPlayer").StarterPlayerScripts.Client.Hud.Kit)
	local role = label:GetAttribute("KitTextRole") or "hudSmall"
	local base = label.TextSize / Kit.Core.TextBoost(role, label.TextSize)
	return math.min(Kit.Text.Width(label.Text, role, base), label.Size.X.Offset)
end

local function onScreen(r, W: number, H: number): boolean
	return r[1] >= -0.5 and r[2] >= -0.5 and r[3] <= W + 0.5 and r[4] <= H + 0.5
end

-- Every pair of `named` ({name, rect}) keeps apart, every one is on screen and
-- none meets Roblox's top-bar buttons (or, on touch, the jump button and the
-- thumbstick ring).
local function noOverlaps(scene: string, named, chrome, W: number, H: number)
	local bad = {}
	for i = 1, #named do
		local a = named[i]
		if not onScreen(a[2], W, H) then
			table.insert(bad, a[1] .. " off screen (" .. __fmtRect(a[2]) .. ")")
		end
		for j = i + 1, #named do
			local b = named[j]
			if not __apart(a[2], b[2]) then
				table.insert(bad, a[1] .. " meets " .. b[1])
			end
		end
		for _, zone in
			{
				{ "Roblox's buttons", chrome.buttons },
				{ "the jump button", chrome.jump },
				{ "the thumbstick", chrome.stick },
			}
		do
			if zone[2] and not __apart(a[2], zone[2]) then
				table.insert(bad, a[1] .. " meets " .. zone[1])
			end
		end
	end
	__hudCheck(
		scene,
		#bad == 0,
		if #bad == 0
			then ("%d regions: none overlaps another, leaves the screen or meets Roblox's controls"):format(#named)
			else table.concat(bad, "; ")
	)
end

-- The world HUD (HudController.Mount) as placed by HudController.PlaceTop.
-- ctx: {scene, hud, root, W, H, k, chrome, layout, gear (GuiObject, the
-- Settings button), attack (GuiObject?), phone (boolean)}.
function __checkWorldHud(ctx)
	local scene, hud, root, W, H, k, chrome = ctx.scene, ctx.hud, ctx.root, ctx.W, ctx.H, ctx.k, ctx.chrome
	local function rect(object)
		return __rect(object, root, W, H, k)
	end
	local buttons = chrome.buttons
	local named = {}
	local function add(name: string, r)
		table.insert(named, { name, r })
		return r
	end

	-- 1 The compass in the top bar's row, level with Roblox's buttons and
	-- clear of them, its waypoints just below it.
	local compass = add("compass", rect(hud.compass.root))
	local centre = (compass[2] + compass[4]) / 2
	local buttonsCentre = (buttons[2] + buttons[4]) / 2
	__hudCheck(
		scene,
		compass[2] < buttons[4] and compass[4] > buttons[2] and math.abs(centre - buttonsCentre) <= 10,
		("the compass sits in the top bar's row (%s; Roblox's buttons y %d..%d)"):format(
			__fmtRect(compass),
			buttons[2],
			buttons[4]
		)
	)
	__hudCheck(
		scene,
		__apart(compass, buttons, 8),
		("the compass keeps 8 px or more from Roblox's buttons (they end at x %d)"):format(buttons[3])
	)
	local cfg = hud.compass.cfg
	local waypoints = {
		compass[1],
		compass[2] + cfg.waypoints.y * k,
		compass[3],
		compass[2] + (cfg.waypoints.y + cfg.waypoints.size) * k,
	}
	__hudCheck(
		scene,
		waypoints[2] >= compass[4] and waypoints[2] - compass[4] <= 8 * k,
		("its waypoints sit just under it (y %d..%d)"):format(waypoints[2], waypoints[4])
	)
	add("waypoints", waypoints)

	-- 2 The vitals in the top-right corner, level with the buttons' top.
	local vitals = add("vitals", rect(hud.vitals.root))
	__hudCheck(
		scene,
		math.abs(vitals[2] - buttons[2]) <= 2 and math.abs(vitals[3] - (W - 53 * k)) <= 1,
		("the vitals start in the top-right corner, level with the buttons' top (%s)"):format(__fmtRect(vitals))
	)
	local foot = vitals[4]
	if hud.vitals.status.Visible then
		local status = add("status", rect(hud.vitals.status))
		__hudCheck(scene, status[2] >= vitals[4], "the status plaques sit under the vitals")
		foot = status[4]
	end

	-- 3 The objective right under the vitals and status, the event under it.
	local objective = add("objective", rect(hud.objective.root))
	local underVitals = objective[2] >= foot and objective[2] - vitals[4] <= 70 * k
	__hudCheck(
		scene,
		underVitals and math.abs(objective[3] - vitals[3]) <= 1,
		("the objective sits right under the vitals (%s; vitals end at y %d)"):format(__fmtRect(objective), vitals[4])
	)
	local event = nil
	if hud.event.root.Visible then
		event = add("world event", rect(hud.event.root))
		if hud.event.root.AnchorPoint.X == 1 then
			__hudCheck(
				scene,
				event[2] >= objective[4] and event[2] - objective[4] <= 20 * k and math.abs(event[3] - vitals[3]) <= 1,
				("the world event sits under the objective (%s)"):format(__fmtRect(event))
			)
		else
			__hudCheck(
				scene,
				event[2] >= rect(ctx.hud.tileRegion)[4],
				("phones: the world event sits under the menu tiles (%s)"):format(__fmtRect(event))
			)
		end
	end

	-- 4 The menu tiles at the left edge, below Roblox's buttons.
	local tiles = add("menu tiles", rect(hud.tileRegion))
	local left = (if ctx.phone then 16 else 39) * k
	__hudCheck(
		scene,
		math.abs(tiles[1] - left) <= 1 and tiles[2] >= buttons[4],
		("the menu tiles sit at the left edge (x %d), below Roblox's buttons (%s)"):format(left, __fmtRect(tiles))
	)
	if hud.party.root.Visible then
		add("tribe frames", rect(hud.party.root))
	end

	-- The level, XP bar and hotbar, with the inked level and XP text beside
	-- the bar.
	local bottom = rect(hud.bottom.root)
	local level, xp = inkWidth(hud.bottom.levelText.root), inkWidth(hud.bottom.xpText.root)
	local cfgBottom = require(game:GetService("StarterPlayer").StarterPlayerScripts.Client.Hud.Layout).Get().bottom
	local levelRight = cfgBottom.level[1] + cfgBottom.level[3]
	local xpLeft = cfgBottom.xpText[1]
	bottom = {
		math.min(bottom[1], bottom[1] + (levelRight - level) * k),
		bottom[2] - 4 * k,
		math.max(bottom[3], bottom[1] + (xpLeft + xp) * k),
		bottom[4],
	}
	add("XP bar and hotbar", bottom)

	-- 5 Settings at the bottom left: in the tiles' column, clear of the hotbar;
	-- on touch above the thumbstick ring, its pad clear of the tiles'.
	if ctx.gear then
		local gear = add("settings", rect(ctx.gear))
		__hudCheck(
			scene,
			math.abs(gear[1] - tiles[1]) <= 1 and gear[2] > H / 2 and gear[3] < bottom[1],
			("Settings sits at the bottom left in the tiles' column (%s), left of the hotbar (x %d)"):format(
				__fmtRect(gear),
				bottom[1]
			)
		)
		local pad = __pad(gear)
		__hudCheck(scene, __apart(pad, __pad(tiles)), "its touch pad keeps clear of the tiles'")
		if chrome.stick then
			local zone = chrome.zone
			__hudCheck(
				scene,
				__apart(pad, chrome.stick) and pad[3] <= 0.1 * W,
				("touch: its pad (%s) clears the thumbstick ring (y %d) and keeps to the screen's outer tenth (x < %d; the thumbstick zone reaches x %d)"):format(
					__fmtRect(pad),
					chrome.stick[2],
					0.1 * W,
					zone[3]
				)
			)
		end
	end
	if ctx.attack then
		add("attack button", rect(ctx.attack))
	end
	noOverlaps(scene, named, chrome, W, H)
end

-- The lobby HUD (Hud/Screens/LobbyHud) after SetTopInset and SetScreen.
-- ctx: {scene, hud, root, W, H, k, chrome, phone (boolean)}.
function __checkLobbyHud(ctx)
	local scene, hud, root, W, H, k, chrome = ctx.scene, ctx.hud, ctx.root, ctx.W, ctx.H, ctx.k, ctx.chrome
	local function rect(object)
		return __rect(object, root, W, H, k)
	end
	local named = {}
	local function add(name: string, r)
		table.insert(named, { name, r })
		return r
	end
	local pills = add("coins and gems", rect(hud.topRight))
	add("party panel", rect(hud.partyRegion))
	local tiles = add("menu tiles", rect(hud.tileRegion))
	local bottom = rect(hud.bottom)
	bottom = { bottom[1] - 40 * k, bottom[2] - 4 * k, bottom[3] + 36 * k, bottom[4] }
	add("XP bar and hotbar", bottom)
	if hud.noticeRegion.Visible then
		add("update notice", rect(hud.noticeRegion))
	end
	local gear = add("settings", rect(hud.settingsRegion))
	__hudCheck(
		scene,
		math.abs(pills[3] - (W - 53 * k)) <= 1 and pills[4] < H / 4,
		("Coins and Gems keep the top right on their own (%s)"):format(__fmtRect(pills))
	)
	local left = (if ctx.phone then 16 else 39) * k
	__hudCheck(
		scene,
		math.abs(gear[1] - left) <= 1 and gear[2] >= tiles[4] and gear[2] > H / 2 and gear[3] < bottom[1],
		("Settings (%s) sits at the bottom left edge (x %d), below the tiles (y %d) and left of the hotbar (x %d), not beside the pills"):format(
			__fmtRect(gear),
			left,
			tiles[4],
			bottom[1]
		)
	)
	local pad = __pad(gear)
	__hudCheck(
		scene,
		__apart(pad, __pad(tiles)),
		("its touch pad keeps clear of the tiles' (tiles end at y %d)"):format(tiles[4])
	)
	if chrome.stick then
		local zone = chrome.zone
		__hudCheck(
			scene,
			__apart(pad, chrome.stick) and pad[3] <= 0.1 * W,
			("touch: its pad (%s) clears the thumbstick ring (y %d) and keeps to the screen's outer tenth (x < %d; the thumbstick zone reaches x %d)"):format(
				__fmtRect(pad),
				chrome.stick[2],
				0.1 * W,
				zone[3]
			)
		)
	end
	noOverlaps(scene, named, chrome, W, H)
end
