-- Layout checks shared by the HUD capture scenes (bundled after the game's
-- modules): where the owner's HUD layout (ARCHITECTURE D28, D29) puts each
-- region, that every region keeps the edge rule (D29: the corner margin, 24
-- design px, from the screen's edge while it lies wholly in the top 30 % or
-- the bottom 25 % of the screen; at least the device safe inset wherever it
-- reaches the middle band, where a notch can be), and that no region overlaps
-- another, leaves the screen, or meets Roblox's own controls (the stand-ins
-- __robloxChrome draws: the top-bar buttons and, on touch, the jump button and
-- the thumbstick) or a notch. Rectangles are screen px {x1, y1, x2, y2}
-- (__rect). Every check prints "ok" or "FAIL"; a scene ends with
-- __hudChecksDone(name), which fails the scene when any check failed.

local hudFails = 0

-- The edge rule's numbers as the spec states them (HudModel.EDGE holds the
-- game's copy; the checks keep their own so a change to either shows).
local EDGE_MARGIN = 24
local TOP_BAND = 0.30
local BOTTOM_BAND = 0.25

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

local function Client()
	return game:GetService("StarterPlayer").StarterPlayerScripts.Client
end

-- Places the world HUD (HudController.Mount) as HudController's applyTop does
-- for a screen W × H at HUD scale k under the chrome's top bar (with its
-- modelled safe area, chrome.insets). Returns what PlaceTop returns.
function __placeWorldHud(hud, W: number, H: number, k: number, chrome, touch: boolean?)
	local HudController = require(Client().Controllers.HudController)
	return HudController.PlaceTop(
		HudController.TopRegions(hud),
		HudController.TopBar(chrome.bar, W, k, game:GetService("GuiService").TopbarInset, 0),
		__hudScreen(W, H, k, touch, chrome.insets)
	)
end

-- The world ⚙ on `root` as SettingsController places it (its own HUD-scaled,
-- full-screen gui in game). Returns the Kit IconButton.
function __worldGear(root, W: number, H: number, k: number, chrome, touch: boolean?)
	local SettingsController = require(Client().Controllers.SettingsController)
	local Kit = require(Client().Hud.Kit)
	local g = SettingsController.GEAR
	return Kit.IconButton.new(root, {
		name = "Settings",
		variant = "settings",
		size = { g.w, g.h },
		position = SettingsController.GearPosition(__hudScreen(W, H, k, touch, chrome.insets)),
		anchorPoint = Vector2.new(0, 1),
	})
end

-- Places the lobby HUD (Hud/Screens/LobbyHud) as LobbyHudController does for
-- a screen W × H at HUD scale k under the chrome's top bar. Returns the tiles'
-- lift.
function __placeLobbyHud(hud, W: number, H: number, k: number, chrome, touch: boolean?)
	local HudModel = require(game:GetService("ReplicatedStorage").Shared.UI.HudModel)
	hud:SetTopInset(math.max(chrome.bar, 52) / k, HudModel.TopRow(chrome.bar) / k, false)
	return hud:SetScreen(__hudScreen(W, H, k, touch, chrome.insets))
end

-- A label's inked width in design px at its drawn size.
local function inkWidth(label): number
	if label == nil or label.Text == "" then
		return 0
	end
	local Kit = require(Client().Hud.Kit)
	local role = label:GetAttribute("KitTextRole") or "hudSmall"
	local base = label.TextSize / Kit.Core.TextBoost(role, label.TextSize)
	return math.min(Kit.Text.Width(label.Text, role, base), label.Size.X.Offset)
end

local function onScreen(r, W: number, H: number): boolean
	return r[1] >= -0.5 and r[2] >= -0.5 and r[3] <= W + 0.5 and r[4] <= H + 0.5
end

local function inCornerBand(r, H: number): boolean
	return r[4] <= TOP_BAND * H + 0.5 or r[2] >= (1 - BOTTOM_BAND) * H - 0.5
end

-- The gap (screen px) the edge rule asks between `r` and its `side` edge.
local function ruleGap(r, side: string, H: number, k: number, insets): number
	if inCornerBand(r, H) then
		return EDGE_MARGIN * k
	end
	return math.max(EDGE_MARGIN * k, if side == "left" then insets.left else insets.right)
end

-- Checks that region `r` keeps the edge rule's gap from its `side` edge.
local function atEdge(scene: string, name: string, r, side: string, ctx)
	local insets = ctx.chrome.insets or __NO_INSETS
	local want = ruleGap(r, side, ctx.H, ctx.k, insets)
	local gap = if side == "left" then r[1] else ctx.W - r[3]
	__hudCheck(
		scene,
		math.abs(gap - want) <= 1,
		("%s: %d px from the %s edge (%s; %s: %d)"):format(
			name,
			math.round(gap),
			side,
			__fmtRect(r),
			if inCornerBand(r, ctx.H)
				then "corner band, the margin"
				elseif want > EDGE_MARGIN * ctx.k + 0.5 then "middle band, the safe inset"
				else "middle band, the margin (no larger safe inset)",
			math.round(want)
		)
	)
end

-- Every pair of `named` ({name, rect}) keeps apart, every one is on screen
-- and none meets Roblox's top-bar buttons (on touch the jump button and the
-- thumbstick ring) or a notch (on either side); every one reaching the middle
-- band keeps inside the device safe insets.
local function noOverlaps(scene: string, named, chrome, W: number, H: number)
	local bad = {}
	local insets = chrome.insets or __NO_INSETS
	local zones = {
		{ "Roblox's buttons", chrome.buttons },
		{ "the jump button", chrome.jump },
		{ "the thumbstick", chrome.stick },
	}
	if chrome.notch then
		local n = chrome.notch
		table.insert(zones, { "the notch (left)", n })
		table.insert(zones, { "the notch (right)", { W - n[3], n[2], W - n[1], n[4] } })
	end
	local middle = 0
	for i = 1, #named do
		local a = named[i]
		if not onScreen(a[2], W, H) then
			table.insert(bad, a[1] .. " off screen (" .. __fmtRect(a[2]) .. ")")
		end
		if not inCornerBand(a[2], H) then
			middle += 1
			if a[2][1] < insets.left - 0.5 or a[2][3] > W - insets.right + 0.5 then
				table.insert(bad, a[1] .. " reaches the middle band outside the safe area (" .. __fmtRect(a[2]) .. ")")
			end
		end
		for j = i + 1, #named do
			local b = named[j]
			if not __apart(a[2], b[2]) then
				table.insert(bad, a[1] .. " meets " .. b[1])
			end
		end
		for _, zone in zones do
			if zone[2] and not __apart(a[2], zone[2]) then
				table.insert(bad, a[1] .. " meets " .. zone[1])
			end
		end
	end
	__hudCheck(
		scene,
		#bad == 0,
		if #bad == 0
			then ("%d regions: none overlaps another, leaves the screen or meets Roblox's controls or a notch; the %d reaching the middle band keep inside the safe insets (left %d, right %d)"):format(
				#named,
				middle,
				insets.left,
				insets.right
			)
			else table.concat(bad, "; ")
	)
end

-- Settings in the bottom-left corner (D29; HudModel.GearCorner): without
-- touch the corner margin from the left and bottom edges; on touch left of the
-- thumbstick ring, centred on its height, its pad clear of the ring, or (no
-- room beside it) above the ring at the edge rule's gap. Always left of the
-- hotbar (`bottomLeft`) with its pad clear of the tiles' (`tiles`).
local function checkGear(scene: string, gear, tiles, bottomLeft: number, ctx)
	local W, H, k, chrome = ctx.W, ctx.H, ctx.k, ctx.chrome
	local pad = __pad(gear)
	__hudCheck(
		scene,
		gear[3] < bottomLeft and __apart(pad, __pad(tiles)),
		("Settings (%s) sits left of the hotbar (x %d), its touch pad clear of the tiles'"):format(
			__fmtRect(gear),
			bottomLeft
		)
	)
	local stick = chrome.stick
	if not stick then
		__hudCheck(
			scene,
			math.abs(gear[1] - EDGE_MARGIN * k) <= 1 and math.abs(H - gear[4] - EDGE_MARGIN * k) <= 1,
			("Settings sits in the bottom-left corner, %d px from the left and the bottom (%s)"):format(
				EDGE_MARGIN * k,
				__fmtRect(gear)
			)
		)
		return
	end
	local ringMid = (stick[2] + stick[4]) / 2
	if pad[3] <= stick[1] then
		__hudCheck(
			scene,
			pad[3] + 12 <= stick[1] + 0.5
				and math.abs((gear[2] + gear[4]) / 2 - ringMid) <= 1
				and inCornerBand(gear, H)
				and gear[1] >= EDGE_MARGIN * k - 0.5
				and pad[1] >= -0.5,
			("touch: Settings (%s) sits in the corner left of the thumbstick ring (x %d), centred on its height (y %d), its pad (x %d..%d) 12 px or more clear of it"):format(
				__fmtRect(gear),
				stick[1],
				ringMid,
				pad[1],
				pad[3]
			)
		)
	else
		__hudCheck(
			scene,
			gear[4] + 12 <= stick[2] + 0.5 and __apart(pad, stick) and pad[3] <= 0.1 * W,
			("touch (no room beside the ring): Settings' foot (y %d) stands 12 px or more above the thumbstick ring (y %d), its pad (%s) clear of it, in the screen's outer tenth"):format(
				gear[4],
				stick[2],
				__fmtRect(pad)
			)
		)
		atEdge(scene, "Settings", gear, "left", ctx)
	end
end

-- The world HUD (HudController.Mount) as placed by HudController.PlaceTop.
-- ctx: {scene, hud, root, W, H, k, chrome, gear (GuiObject, the Settings
-- button), attack (GuiObject?), phone (boolean)}.
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

	-- 2 The vitals in the top-right corner, level with the buttons' top, at
	-- the edge (D29).
	local vitals = add("vitals", rect(hud.vitals.root))
	__hudCheck(
		scene,
		math.abs(vitals[2] - buttons[2]) <= 2,
		("the vitals start level with the buttons' top (%s)"):format(__fmtRect(vitals))
	)
	atEdge(scene, "the vitals", vitals, "right", ctx)
	local foot = vitals[4]
	if hud.vitals.status.Visible then
		local status = add("status", rect(hud.vitals.status))
		__hudCheck(scene, status[2] >= vitals[4], "the status plaques sit under the vitals")
		atEdge(scene, "the status plaques", status, "right", ctx)
		foot = status[4]
	end

	-- 3 The objective right under the vitals and status, the event under it.
	local objective = add("objective", rect(hud.objective.root))
	__hudCheck(
		scene,
		objective[2] >= foot and objective[2] - vitals[4] <= 70 * k,
		("the objective sits right under the vitals (%s; vitals end at y %d)"):format(__fmtRect(objective), vitals[4])
	)
	atEdge(scene, "the objective", objective, "right", ctx)
	local tiles = add("menu tiles", rect(hud.tileRegion))
	if hud.event.root.Visible then
		local event = add("world event", rect(hud.event.root))
		if hud.event.root.AnchorPoint.X == 1 then
			__hudCheck(
				scene,
				event[2] >= objective[4] and event[2] - objective[4] <= 20 * k,
				("the world event sits under the objective (%s)"):format(__fmtRect(event))
			)
			atEdge(scene, "the world event", event, "right", ctx)
		else
			__hudCheck(
				scene,
				event[2] >= tiles[4],
				("phones: the world event sits under the menu tiles (%s)"):format(__fmtRect(event))
			)
			atEdge(scene, "the world event", event, "left", ctx)
		end
	end

	-- 4 The menu tiles at the left edge, below Roblox's buttons.
	__hudCheck(
		scene,
		tiles[2] >= buttons[4],
		("the menu tiles sit below Roblox's buttons (%s)"):format(__fmtRect(tiles))
	)
	atEdge(scene, "the menu tiles", tiles, "left", ctx)
	if hud.party.root.Visible then
		local party = add("tribe frames", rect(hud.party.root))
		if hud.party.root.AnchorPoint.X == 0 and hud.party.root.Position.X.Scale == 0 then
			atEdge(scene, "the tribe frames", party, "left", ctx)
		end
	end

	-- The level, XP bar and hotbar, with the inked level and XP text beside
	-- the bar.
	local bottom = rect(hud.bottom.root)
	local level, xp = inkWidth(hud.bottom.levelText.root), inkWidth(hud.bottom.xpText.root)
	local cfgBottom = require(Client().Hud.Layout).Get().bottom
	local levelRight = cfgBottom.level[1] + cfgBottom.level[3]
	local xpLeft = cfgBottom.xpText[1]
	bottom = {
		math.min(bottom[1], bottom[1] + (levelRight - level) * k),
		bottom[2] - 4 * k,
		math.max(bottom[3], bottom[1] + (xpLeft + xp) * k),
		bottom[4],
	}
	add("XP bar and hotbar", bottom)

	-- 5 Settings in the bottom-left corner.
	if ctx.gear then
		local gear = add("settings", rect(ctx.gear))
		checkGear(scene, gear, tiles, bottom[1], ctx)
	end
	if ctx.attack then
		add("attack button", rect(ctx.attack))
	end
	noOverlaps(scene, named, chrome, W, H)
end

-- The lobby HUD (Hud/Screens/LobbyHud) after SetTopInset and SetScreen
-- (__placeLobbyHud). ctx: {scene, hud, root, W, H, k, chrome, phone}.
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
	local insets = chrome.insets or __NO_INSETS
	local pills = add("coins and gems", rect(hud.topRight))
	local party = add("party panel", rect(hud.partyRegion))
	local tiles = add("menu tiles", rect(hud.tileRegion))
	local bottom = rect(hud.bottom)
	bottom = { bottom[1] - 40 * k, bottom[2] - 4 * k, bottom[3] + 36 * k, bottom[4] }
	add("XP bar and hotbar", bottom)
	if hud.noticeRegion.Visible then
		add("update notice", rect(hud.noticeRegion))
	end
	local gear = add("settings", rect(hud.settingsRegion))

	-- Coins and Gems in the top-right corner, level with Roblox's buttons'
	-- top; the Party panel right under them; both at the edge (D29).
	__hudCheck(
		scene,
		math.abs(pills[2] - chrome.buttons[2]) <= 2,
		("Coins and Gems sit level with Roblox's buttons' top (%s; buttons y %d)"):format(
			__fmtRect(pills),
			chrome.buttons[2]
		)
	)
	atEdge(scene, "Coins and Gems", pills, "right", ctx)
	__hudCheck(
		scene,
		party[2] >= pills[4] and math.abs(party[2] - pills[4] - 16 * k) <= 1,
		("the Party panel sits right under them (%s)"):format(__fmtRect(party))
	)
	atEdge(scene, "the Party panel", party, "right", ctx)
	-- The tiles keep their place (68 px in from the safe area's left edge).
	__hudCheck(
		scene,
		math.abs(tiles[1] - (insets.left + 68 * k)) <= 1,
		("the menu tiles keep their place inside the safe area (%s)"):format(__fmtRect(tiles))
	)
	checkGear(scene, gear, tiles, bottom[1], ctx)
	noOverlaps(scene, named, chrome, W, H)
end
