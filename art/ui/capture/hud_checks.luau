-- Layout checks shared by the HUD capture scenes (bundled after the game's
-- modules): the HUD grid (ARCHITECTURE D30, HudLayout.json "grid") in both
-- HUDs. Every corner piece stands the margin M from both its edges; every
-- column's pieces share one outer edge and, where the spec says so, one width,
-- with the gap G between stacked pieces; a column's edge is M from the
-- screen's side while the whole column lies in the corner bands (the top 30 %
-- or the bottom 25 % of the screen's height), else M or the device safe inset,
-- whichever is larger, for the whole column; the pieces the lobby and the run
-- share (the menu tiles, Settings, the level/XP bar and hotbar, the
-- right-hand column's edge, top and width) sit in the same place in both; no
-- region overlaps another, leaves the screen, or meets Roblox's own controls
-- (the stand-ins __robloxChrome draws: the top-bar buttons and, on touch, the
-- jump button and the thumbstick) or a notch. Rectangles are screen px {x1,
-- y1, x2, y2} (__rect); the kit's plates are drawn outset by their sprites'
-- transparent margins (KitModel.EDGES), so a region's rect is its art's
-- visible edge. Every check prints "ok" or "FAIL"; a scene ends with
-- __hudChecksDone(name), which fails the scene when any check failed.

local hudFails = 0

-- The grid as the spec states it (HudLayout.json holds the game's copy; the
-- checks keep their own so a change to either shows).
local M = 24
local G = 12
local COLUMN = 315
local TOP_BAND = 0.30
local BOTTOM_BAND = 0.25
-- Roblox's top-bar buttons: 44 px tall (HudModel.TOP_BUTTON).
local TOP_BUTTON = 44

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

local function near(a: number, b: number, tolerance: number?): boolean
	return math.abs(a - b) <= (tolerance or 1)
end

-- Places the world HUD (HudController.Mount) as HudController's applyTop does
-- for a screen W × H at HUD scale k under the chrome's top bar (with its
-- modelled safe area, chrome.insets). Returns what PlaceTop returns. The HUD
-- keeps a way to place itself again (`__replace`), as the live controller
-- does when a column piece shows, hides or grows (its region watcher).
function __placeWorldHud(hud, W: number, H: number, k: number, chrome, touch: boolean?)
	local HudController = require(Client().Controllers.HudController)
	local function place()
		return HudController.PlaceTop(
			HudController.TopRegions(hud),
			HudController.TopBar(chrome.bar, W, k, game:GetService("GuiService").TopbarInset, 0),
			__hudScreen(W, H, k, touch, chrome.insets)
		)
	end
	hud.__replace = place
	return place()
end

-- The world ⚙ on `root` as SettingsController places it (its own HUD-scaled,
-- full-screen gui in game). Returns the Kit IconButton.
function __worldGear(root, W: number, H: number, k: number, chrome, touch: boolean?)
	local SettingsController = require(Client().Controllers.SettingsController)
	local Kit = require(Client().Hud.Kit)
	local size = SettingsController.GearSize()
	return Kit.IconButton.new(root, {
		name = "Settings",
		variant = "settings",
		size = { size[1], size[2] },
		position = SettingsController.GearPosition(__hudScreen(W, H, k, touch, chrome.insets)),
		anchorPoint = Vector2.new(0, 1),
	})
end

-- Places the lobby HUD (Hud/Screens/LobbyHud) as LobbyHudController does for
-- a screen W × H at HUD scale k under the chrome's top bar.
function __placeLobbyHud(hud, W: number, H: number, k: number, chrome, touch: boolean?)
	local HudModel = require(game:GetService("ReplicatedStorage").Shared.UI.HudModel)
	hud:SetScreen(__hudScreen(W, H, k, touch, chrome.insets))
	hud:SetTopInset(math.max(chrome.bar, 52) / k, HudModel.TopRow(chrome.bar) / k, false)
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

-- The union of rectangles.
local function union(list)
	local u = { math.huge, math.huge, -math.huge, -math.huge }
	for _, r in list do
		u = { math.min(u[1], r[1]), math.min(u[2], r[2]), math.max(u[3], r[3]), math.max(u[4], r[4]) }
	end
	return u
end

-- The gap (screen px) the edge rule asks between a column spanning `span`
-- (the union of its pieces) and its `side` edge.
local function ruleGap(span, side: string, H: number, k: number, insets): number
	if inCornerBand(span, H) then
		return M * k
	end
	return math.max(M * k, if side == "left" then insets.left else insets.right)
end

-- A column: `pieces` ({name, rect, stacked?, width?}) on the `side` edge,
-- the stacked ones one under another from `top` (screen px; nil: not checked).
-- Checks they share one edge, the edge the rule gives for the whole column,
-- the widths named, and the gap G between stacked neighbours. Returns the
-- column's edge gap.
local function checkColumn(scene: string, title: string, pieces, side: string, top: number?, ctx)
	local k, W, H = ctx.k, ctx.W, ctx.H
	local insets = ctx.chrome.insets or __NO_INSETS
	local rects = {}
	for _, piece in pieces do
		table.insert(rects, piece[2])
	end
	local span = union(rects)
	local want = ruleGap(span, side, H, k, insets)
	local bad = {}
	for _, piece in pieces do
		local r = piece[2]
		local gap = if side == "left" then r[1] else W - r[3]
		if not near(gap, want) then
			table.insert(bad, ("%s %d px from the %s edge"):format(piece[1], math.round(gap), side))
		end
		if piece.width and not near(r[3] - r[1], piece.width * k) then
			table.insert(bad, ("%s %d px wide (want %d)"):format(piece[1], math.round(r[3] - r[1]), piece.width * k))
		end
	end
	local stacked = {}
	for _, piece in pieces do
		if piece.stacked then
			table.insert(stacked, piece)
		end
	end
	if top and stacked[1] and not near(stacked[1][2][2], top) then
		table.insert(bad, ("%s starts at y %d (want %d)"):format(stacked[1][1], stacked[1][2][2], math.round(top)))
	end
	for index = 2, #stacked do
		local above, below = stacked[index - 1], stacked[index]
		local gap = below[2][2] - above[2][4]
		if not near(gap, G * k) then
			table.insert(bad, ("%s → %s gap %.1f px (want G = %.1f)"):format(above[1], below[1], gap, G * k))
		end
	end
	local names = {}
	for _, piece in pieces do
		table.insert(names, piece[1])
	end
	__hudCheck(
		scene,
		#bad == 0,
		if #bad == 0
			then ("%s column (%s): one %s edge %d px in (%s: %s), widths as specified, G = %.1f px between stacked pieces"):format(
				title,
				table.concat(names, ", "),
				side,
				math.round(want),
				__fmtRect(span),
				if inCornerBand(span, H)
					then "in a corner band, M"
					elseif want > M * k + 0.5 then "reaches the middle band, the safe inset"
					else "reaches the middle band, M (no larger inset)",
				G * k
			)
			else title .. " column: " .. table.concat(bad, "; ")
	)
	return want
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

-- Settings in the grid's bottom-left corner (D30; HudModel.GearCorner): M
-- from the screen's left and bottom edges (±1 px), on touch screens too
-- unless the thumbstick ring reaches the corner, where it stands above the
-- ring (its foot 12 px over it, at the edge rule's gap). Always left of the
-- hotbar (`bottomLeft`) with its pad clear of the tiles' (`tiles`) and the
-- ring.
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
	local corner = stick == nil or __apart(pad, stick, 12)
	if corner then
		__hudCheck(
			scene,
			near(gear[1], M * k) and near(H - gear[4], M * k),
			("Settings sits in the corner: %.1f px from the left and %.1f from the bottom, M = %.1f (%s)%s"):format(
				gear[1],
				H - gear[4],
				M * k,
				__fmtRect(gear),
				if stick
					then (", its pad (%s) 12 px or more clear of the thumbstick ring"):format(__fmtRect(pad))
					else ""
			)
		)
		return
	end
	__hudCheck(
		scene,
		gear[4] + 12 <= stick[2] + 0.5 and __apart(pad, stick),
		("touch (the ring reaches the corner): Settings' foot (y %d) stands 12 px or more above the thumbstick ring (y %d), its pad (%s) clear of it"):format(
			gear[4],
			stick[2],
			__fmtRect(pad)
		)
	)
	local want = ruleGap(gear, "left", H, k, chrome.insets or __NO_INSETS)
	__hudCheck(
		scene,
		near(gear[1], want),
		("Settings %.1f px from the left edge (the edge rule: %.1f)"):format(gear[1], want)
	)
end

-- The level/XP bar and hotbar: the bottom group M above the screen's bottom
-- edge and centred, the XP bar centred over the hotbar. `bottom` is the
-- group's rect, `bar` the XP bar's, `slots` the hotbar slots'.
local function checkBottom(scene: string, bottom, bar, slots, ctx)
	local W, H, k = ctx.W, ctx.H, ctx.k
	local hotbar = union(slots)
	__hudCheck(
		scene,
		near(H - hotbar[4], M * k)
			and near((hotbar[1] + hotbar[3]) / 2, W / 2)
			and near((bar[1] + bar[3]) / 2, (hotbar[1] + hotbar[3]) / 2),
		("the hotbar %.1f px above the bottom edge (M = %.1f) and centred (x %d..%d); the XP bar centred over it (x %d..%d)"):format(
			H - hotbar[4],
			M * k,
			hotbar[1],
			hotbar[3],
			bar[1],
			bar[3]
		)
	)
	return hotbar
end

-- The pieces the two HUDs share, from a world HUD (HudController.Mount) or a
-- lobby HUD: {tiles, tile1, tile2, tileLast, settings, bottom, bar, slot1,
-- slotLast, rightTop (the right-hand column's first piece), rightSecond}.
local function sharedWorld(hud, rect, gear)
	local tiles = hud.tiles
	return {
		tiles = rect(hud.tileRegion),
		tile1 = rect(tiles[1].root),
		tile2 = rect(tiles[2].root),
		tileLast = rect(tiles[#tiles].root),
		settings = if gear then rect(gear) else nil,
		bottom = rect(hud.bottom.root),
		bar = rect(hud.bottom.xpBar.root),
		slot1 = rect(hud.bottom.slots[1].root),
		slotLast = rect(hud.bottom.slots[#hud.bottom.slots].root),
		rightTop = rect(hud.vitals.root),
		rightSecond = rect(hud.objective.root),
	}
end

local function sharedLobby(hud, rect)
	local tiles = hud.tiles
	return {
		tiles = rect(hud.tileRegion),
		tile1 = rect(tiles[1].root),
		tile2 = rect(tiles[2].root),
		tileLast = rect(tiles[#tiles].root),
		settings = rect(hud.settingsRegion),
		bottom = rect(hud.bottom),
		bar = rect(hud.bar.root),
		slot1 = rect(hud.slots[1].root),
		slotLast = rect(hud.slots[#hud.slots].root),
		rightTop = rect(hud.topRight),
		rightSecond = rect(hud.partyRegion),
	}
end

-- Builds the lobby HUD at the world page's screen (a hidden gui, not drawn)
-- and checks the shared pieces sit in the same place in both (±1 px): the
-- tile grid (origin, tile size, pitch), Settings, the bottom group, the XP
-- bar and hotbar, and the right-hand column's first piece (top, right edge,
-- width) and second piece (right edge, width; its top follows the first
-- piece's height).
local function compareWithLobby(scene: string, world, ctx)
	local LobbyHud = require(Client().Hud.Screens.LobbyHud)
	local Kit = require(Client().Hud.Kit)
	local W, H, k = ctx.W, ctx.H, ctx.k
	local gui, root = __screen(W, H)
	local lobby = LobbyHud.new(root, {})
	Kit.Scale.Hud(gui, root)
	__placeLobbyHud(lobby, W, H, k, ctx.chrome, ctx.chrome.stick ~= nil)
	local rect = function(object)
		return __rect(object, root, W, H, k)
	end
	local other = sharedLobby(lobby, rect)
	local bad = {}
	local function same(name: string, a, b, parts)
		if a == nil or b == nil then
			return
		end
		for _, i in parts do
			if not near(a[i], b[i]) then
				table.insert(bad, ("%s: world %s, lobby %s"):format(name, __fmtRect(a), __fmtRect(b)))
				return
			end
		end
	end
	local all = { 1, 2, 3, 4 }
	same("menu tiles", world.tiles, other.tiles, all)
	same("first tile", world.tile1, other.tile1, all)
	same("second tile (pitch)", world.tile2, other.tile2, all)
	same("last tile", world.tileLast, other.tileLast, all)
	same("Settings", world.settings, other.settings, all)
	same("bottom group", world.bottom, other.bottom, all)
	same("XP bar", world.bar, other.bar, all)
	same("first hotbar slot", world.slot1, other.slot1, all)
	same("last hotbar slot", world.slotLast, other.slotLast, all)
	same("right-hand column's top piece (top, right edge, width)", world.rightTop, other.rightTop, { 1, 2, 3 })
	same("right-hand column's second piece (right edge, width)", world.rightSecond, other.rightSecond, { 1, 3 })
	__hudCheck(
		scene,
		#bad == 0,
		if #bad == 0
			then ("the lobby at this screen puts the shared pieces in the same place: tiles %s, Settings %s, hotbar %s..%s, right column %s / %s"):format(
				__fmtRect(world.tiles),
				__fmtRect(world.settings or other.settings),
				__fmtRect(world.slot1),
				__fmtRect(world.slotLast),
				__fmtRect(world.rightTop),
				__fmtRect(world.rightSecond)
			)
			else "shared pieces differ: " .. table.concat(bad, "; ")
	)
	lobby:Destroy()
	gui:Destroy()
end

-- The world HUD (HudController.Mount) as placed by HudController.PlaceTop.
-- ctx: {scene, hud, root, W, H, k, chrome, gear (GuiObject, the Settings
-- button), attack (GuiObject?), lobby (false: skip the comparison)}.
function __checkWorldHud(ctx)
	local scene, hud, root, W, H, k, chrome = ctx.scene, ctx.hud, ctx.root, ctx.W, ctx.H, ctx.k, ctx.chrome
	if hud.__replace then
		-- Shown, hidden or resized pieces restack, as the live watcher does.
		hud.__replace()
	end
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

	-- 2 The right-hand column: the vitals M from the top and the right (the
	-- corner piece), the status plaques, objective and world event under them
	-- with G between, one right edge, the panels one width.
	local right = {}
	local vitals = add("vitals", rect(hud.vitals.root))
	table.insert(right, { "vitals", vitals, stacked = true, width = COLUMN })
	if hud.vitals.status.Visible then
		-- The plaques fit their text, right-aligned on the column's edge.
		table.insert(right, { "status", add("status", rect(hud.vitals.status)), stacked = true })
	end
	local objective = add("objective", rect(hud.objective.root))
	table.insert(right, { "objective", objective, stacked = true, width = COLUMN })
	local eventRight = hud.event.root.AnchorPoint.X == 1
	local event = if hud.event.root.Visible then add("world event", rect(hud.event.root)) else nil
	if event and eventRight then
		table.insert(right, { "world event", event, stacked = true, width = COLUMN })
	end
	local rightGap = checkColumn(scene, "right-hand", right, "right", M * k, ctx)
	__hudCheck(
		scene,
		near(vitals[2], M * k) and (rightGap > M * k + 0.5 or near(W - vitals[3], M * k)),
		("the vitals (the top-right corner piece) %.1f px from the top and %.1f from the right (M = %.1f%s)"):format(
			vitals[2],
			W - vitals[3],
			M * k,
			if rightGap > M * k + 0.5
				then "; the column reaches the middle band, so the right edge is the safe inset"
				else ""
		)
	)

	-- 3 The left-hand column: the tribe frames (desktop), the menu tiles and
	-- (phones) the world event, one left edge; the stacked ones from G under
	-- Roblox's buttons, G apart; the desktop tiles centred on the screen's
	-- height.
	local left = {}
	local tiles = add("menu tiles", rect(hud.tileRegion))
	local tilesCfg = require(Client().Hud.Layout).ForScreen(require(Client().Hud.Layout).Get().tiles)
	local tilesCentred = type(tilesCfg.centreY) == "number"
	local party = hud.party.root
	local strip = hud.party.cfg.strip
	if party.Visible and not strip then
		table.insert(left, { "tribe frames", add("tribe frames", rect(party)), stacked = true })
	end
	table.insert(left, { "menu tiles", tiles, stacked = not tilesCentred })
	if event and not eventRight then
		table.insert(left, { "world event", event, stacked = true, width = COLUMN })
	end
	checkColumn(scene, "left-hand", left, "left", buttons[4] + G * k, ctx)
	if tilesCentred then
		__hudCheck(
			scene,
			near((tiles[2] + tiles[4]) / 2, tilesCfg.centreY * H),
			("the menu tiles are centred at %.3f of the screen's height (%s)"):format(
				tilesCfg.centreY,
				__fmtRect(tiles)
			)
		)
	end
	if strip and party.Visible then
		local r = add("tribe strip", rect(party))
		__hudCheck(
			scene,
			near((r[1] + r[3]) / 2, (compass[1] + compass[3]) / 2) and r[2] >= waypoints[4] - 0.5,
			("phones: the tribe strip hangs under the compass's waypoints, centred on the compass (%s)"):format(
				__fmtRect(r)
			)
		)
	end

	-- 4 The level, XP bar and hotbar, with the inked level and XP text beside
	-- the bar.
	local bottom = rect(hud.bottom.root)
	local slots = {}
	for _, slot in hud.bottom.slots do
		table.insert(slots, rect(slot.root))
	end
	local hotbar = checkBottom(scene, bottom, rect(hud.bottom.xpBar.root), slots, ctx)
	local level, xp = inkWidth(hud.bottom.levelText.root), inkWidth(hud.bottom.xpText.root)
	local cfgBottom = require(Client().Hud.Layout).Get().bottom
	local levelRight = cfgBottom.level[1] + cfgBottom.level[3]
	local xpLeft = cfgBottom.xpText[1]
	bottom = {
		math.min(hotbar[1], bottom[1] + (levelRight - level) * k),
		bottom[2] - 4 * k,
		math.max(hotbar[3], bottom[1] + (xpLeft + xp) * k),
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

	-- 6 The lobby at the same screen puts the shared pieces in the same place.
	if ctx.lobby ~= false then
		compareWithLobby(scene, sharedWorld(hud, rect, ctx.gear), ctx)
	end
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
	local pills = add("coins and gems", rect(hud.topRight))
	local party = add("party panel", rect(hud.partyRegion))
	local tiles = add("menu tiles", rect(hud.tileRegion))
	local slots = {}
	for _, slot in hud.slots do
		table.insert(slots, rect(slot.root))
	end
	local hotbar = checkBottom(scene, rect(hud.bottom), rect(hud.bar.root), slots, ctx)
	-- The level and XP text beside the bar, as inked.
	local b = require(Client().Hud.Layout).Get().bottom
	local group = rect(hud.bottom)
	local level, xp = inkWidth(hud.barLevel.root), inkWidth(hud.barText.root)
	add("XP bar and hotbar", {
		math.min(hotbar[1], group[1] + (b.level[1] + b.level[3] - level) * k),
		group[2] - 4 * k,
		math.max(hotbar[3], group[1] + (b.xpText[1] + xp) * k),
		group[4],
	})
	if hud.noticeRegion.Visible then
		add("update notice", rect(hud.noticeRegion))
		local notice = rect(hud.noticeRegion)
		__hudCheck(
			scene,
			near((notice[1] + notice[3]) / 2, W / 2) and near(group[2] - notice[4], G * k),
			("the update notice is centred (%s), G above the XP bar"):format(__fmtRect(notice))
		)
	end
	local gear = add("settings", rect(hud.settingsRegion))

	-- The right-hand column: Coins and Gems in the top-right corner (M from
	-- the top and the right while the column fits the corner band), the Party
	-- panel G under them, one right edge and one width.
	local rightGap = checkColumn(scene, "right-hand", {
		{ "coins and gems", pills, stacked = true, width = COLUMN },
		{ "party panel", party, stacked = true, width = COLUMN },
	}, "right", M * k, ctx)
	__hudCheck(
		scene,
		near(pills[2], M * k) and (rightGap > M * k + 0.5 or near(W - pills[3], M * k)),
		("Coins and Gems (the top-right corner piece) %.1f px from the top and %.1f from the right (M = %.1f%s)"):format(
			pills[2],
			W - pills[3],
			M * k,
			if rightGap > M * k + 0.5
				then "; the column reaches the middle band, so the right edge is the safe inset"
				else ""
		)
	)
	-- The tiles: the run's grid at the left edge.
	local Layout = require(Client().Hud.Layout)
	local tilesCfg = Layout.ForScreen(Layout.Get().tiles)
	local centred = type(tilesCfg.centreY) == "number"
	checkColumn(
		scene,
		"left-hand",
		{ { "menu tiles", tiles, stacked = not centred } },
		"left",
		chrome.buttons[4] + G * k,
		ctx
	)
	if centred then
		__hudCheck(
			scene,
			near((tiles[2] + tiles[4]) / 2, tilesCfg.centreY * H),
			("the menu tiles are centred at %.3f of the screen's height (%s)"):format(
				tilesCfg.centreY,
				__fmtRect(tiles)
			)
		)
	end
	checkGear(scene, gear, tiles, hotbar[1], ctx)
	noOverlaps(scene, named, chrome, W, H)
end

-- The run's boost list (BoostHudController) beside the world ⚙ (D30): it
-- starts G right of the ⚙'s art, or of its touch pad where that reaches
-- further, and its foot stands M above the screen's bottom edge, level with
-- the ⚙'s and the hotbar's. `gearAt` is SettingsController.GearPosition's
-- UDim2 at HUD scale k; the list draws at `listScale`. `check(ok, message)`
-- reports.
function __checkBoosts(scene: string, list, gearAt, k: number, listScale: number, W: number, H: number, check)
	local spec = require(Client().Hud.Layout).Gear()
	local w = spec.size[1] * k
	local gearRight = gearAt.X.Offset * k + w + math.max(0, spec.pad - w) / 2
	local left = list.Position.X.Offset * listScale
	local foot = H + list.Position.Y.Offset * listScale
	check(
		near(left, gearRight + G * k) and near(H - foot, M * k),
		("%s: the boosts start G (%.1f px) right of the world settings button (x %.1f; it ends at x %.1f) and stand M (%.1f px) above the bottom edge (%.1f)"):format(
			scene,
			G * k,
			left,
			gearRight,
			M * k,
			H - foot
		)
	)
end
